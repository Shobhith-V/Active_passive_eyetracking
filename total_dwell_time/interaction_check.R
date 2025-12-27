# === Load Required Packages ===
require(itsadug)
library(mgcv)
library(dplyr)
library(readr)

# === Step 1: Load Original Formulas and Create Interaction Variants ===
original_formulas <- read.csv("order_of_access_model_formulas.csv", stringsAsFactors = FALSE)
original_formulas$Model <- paste0("Model_", original_formulas$Model_Index)

interaction_formulas <- original_formulas
interaction_formulas$Formula <- gsub("subject_object \\+ voice_type", "subject_object * voice_type", interaction_formulas$Formula)
interaction_formulas$Model <- paste0("Model_Interaction_", interaction_formulas$Model_Index)

# Combine both
all_formulas <- rbind(original_formulas, interaction_formulas)
write.csv(all_formulas, "order_of_access_all_model_formulas.csv", row.names = FALSE)
cat("✅ Saved combined formulas with and without interaction to: order_of_access_all_model_formulas.csv\n")

# === Step 2: Load Data ===
access_order_data <- read.csv("data/order_of_access.csv")

# Reformat columns
factor_cols <- c(
    "voice_type", "user_name", "base_image", "voice_s_o", "pos_code", "subject_object",
    "Gender", "education", "bilingualism", "english_proficiency"
)
access_order_data[factor_cols] <- lapply(access_order_data[factor_cols], as.factor)
access_order_data$order_of_access <- factor(access_order_data$order_of_access, levels = c("1", "2", "3"))
access_order_data$order_of_access <- as.integer(as.character(access_order_data$order_of_access))
access_order_data$Age <- as.numeric(as.character(access_order_data$Age))

# Set reference levels
access_order_data$voice_type <- relevel(access_order_data$voice_type, ref = "Ref")
access_order_data$subject_object <- relevel(access_order_data$subject_object, ref = "O")
access_order_data$education <- relevel(access_order_data$education, ref = "LP")
access_order_data$bilingualism <- relevel(access_order_data$bilingualism, ref = "No")
access_order_data$english_proficiency <- relevel(access_order_data$english_proficiency, ref = "LOW")

# === Step 3: Setup Output Folders ===
dir.create("order_of_access_gam_models", showWarnings = FALSE)
dir.create("order_of_access_gam_plots", showWarnings = FALSE)

# === Step 4: Fit All Models ===
formulas <- lapply(all_formulas$Formula, as.formula)
model_names <- all_formulas$Model
ocat_family <- ocat(R = 3)

model_metrics <- data.frame()
summary_file <- file("order_of_access_gam_models/all_model_summaries.txt", open = "wt")

for (i in seq_along(formulas)) {
    model_path <- paste0("order_of_access_gam_models/", model_names[i], ".rds")

    if (file.exists(model_path)) {
        cat("⏭️ Skipping", model_names[i], "(already exists)\n")
        next
    }

    cat("🔄 Fitting", model_names[i], "...\n")
    model <- bam(formulas[[i]], data = access_order_data, family = ocat_family, method = "fREML")

    saveRDS(model, model_path)

    cat("\n\n============", model_names[i], "============\n", file = summary_file, append = TRUE)
    capture.output(summary(model), file = summary_file, append = TRUE)

    png(paste0("order_of_access_gam_plots/diag_", model_names[i], ".png"), width = 1000, height = 800)
    par(mfrow = c(2, 2))
    gam.check(model)
    dev.off()

    if (length(model$smooth) > 0) {
        png(paste0("order_of_access_gam_plots/smooths_", model_names[i], ".png"), width = 1000, height = 800)
        plot(model, pages = 1, se = TRUE, shade = TRUE, main = model_names[i])
        dev.off()
    }

    model_summary <- summary(model)
    model_metrics <- rbind(model_metrics, data.frame(
        Model = model_names[i],
        Formula = as.character(formulas[[i]]),
        Model_File = model_path,
        AIC = AIC(model),
        BIC = BIC(model),
        LogLikelihood = as.numeric(logLik(model)),
        Deviance_Explained_Percent = round(model_summary$dev.expl * 100, 2),
        Adjusted_R2 = if (!is.null(model_summary$r.sq)) round(model_summary$r.sq, 4) else NA,
        EDF = sum(model_summary$edf),
        Num_Params = length(coef(model))
    ))
}

close(summary_file)
model_metrics <- model_metrics[order(model_metrics$AIC), ]
write.csv(model_metrics, "order_of_access_model_comparison_all.csv", row.names = FALSE)

# === Step 5: ANOVA Comparisons Between All Models ===
model_paths <- setNames(model_metrics$Model_File, model_metrics$Model)
model_pairs <- combn(model_metrics$Model, 2, simplify = FALSE)

anova_results <- lapply(model_pairs, function(pair) {
    m1 <- readRDS(model_paths[[pair[1]]])
    m2 <- readRDS(model_paths[[pair[2]]])

    cmp <- try(anova(m1, m2, test = "Chisq"), silent = TRUE)

    if (inherits(cmp, "try-error")) {
        return(NULL)
    }

    data.frame(
        Model1 = pair[1],
        Model2 = pair[2],
        AIC1 = AIC(m1),
        AIC2 = AIC(m2),
        deltaAIC = AIC(m2) - AIC(m1),
        p_value = cmp[2, "Pr(>Chi)"],
        stringsAsFactors = FALSE
    )
})

anova_df <- do.call(rbind, anova_results)
write.csv(anova_df, "order_of_access_model_anova_results_all.csv", row.names = FALSE)

# === Step 6: Print Best Model ===
best_model_index <- which.min(model_metrics$AIC)
cat("\n✅ Best model is", model_metrics$Model[best_model_index], "with AIC =", model_metrics$AIC[best_model_index], "\n")
