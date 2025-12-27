# %% Load libraries
require(itsadug)
library(mgcv)
library(dplyr)

rm(list = ls())

# %% Load the dataset
total_dwell_time <- read.csv("data/total_dwell_time.csv")

# %% Check structure
factor_cols <- c(
    "voice_type", "user_name", "base_image", "pos_code", "voice_s_o",
    "subject_object", "Gender", "education", "bilingualism", "english_proficiency"
)
total_dwell_time[factor_cols] <- lapply(total_dwell_time[factor_cols], as.factor)

total_dwell_time$Age <- as.numeric(as.character(total_dwell_time$Age))
total_dwell_time$voice_type <- relevel(total_dwell_time$voice_type, ref = "Ref")
total_dwell_time$subject_object <- relevel(total_dwell_time$subject_object, ref = "O")
total_dwell_time$education <- relevel(total_dwell_time$education, ref = "LP")
total_dwell_time$bilingualism <- relevel(total_dwell_time$bilingualism, ref = "No")
total_dwell_time$english_proficiency <- relevel(total_dwell_time$english_proficiency, ref = "LOW")

# %% Create folders
dir.create("total_dwell_time_gam_models", showWarnings = FALSE)
dir.create("total_dwell_time_gam_plots", showWarnings = FALSE)

# %% Load formulas and create interaction formulas
original_formulas <- read.csv("total_dwell_time_model_formulas.csv", stringsAsFactors = FALSE)
original_formulas$Model <- paste0("Model_", original_formulas$Model_Index)

interaction_formulas <- original_formulas
interaction_formulas$Formula <- gsub("subject_object \\+ voice_type", "subject_object * voice_type", interaction_formulas$Formula)
interaction_formulas$Model <- paste0("Model_Interaction_", interaction_formulas$Model_Index)

all_formulas <- rbind(original_formulas, interaction_formulas)
write.csv(all_formulas, "total_dwell_time_all_model_formulas.csv", row.names = FALSE)

# %% Fit models
formulas <- lapply(all_formulas$Formula, as.formula)
model_names <- all_formulas$Model

model_metrics <- data.frame()
summary_file <- file("total_dwell_time_gam_models/all_model_summaries.txt", open = "wt")

for (i in seq_along(formulas)) {
    model_path <- paste0("total_dwell_time_gam_models/", model_names[i], ".rds")

    if (file.exists(model_path)) {
        cat("⏭️ Skipping", model_names[i], "(already exists)\n")
        next
    }

    cat("🔄 Fitting", model_names[i], "...\n")
    model <- bam(formulas[[i]], data = total_dwell_time)

    saveRDS(model, model_path)

    cat("\n\n============", model_names[i], "============\n", file = summary_file, append = TRUE)
    capture.output(summary(model), file = summary_file, append = TRUE)

    png(paste0("total_dwell_time_gam_plots/diag_", model_names[i], ".png"), width = 1000, height = 800)
    par(mfrow = c(2, 2))
    gam.check(model)
    dev.off()

    if (length(model$smooth) > 0) {
        png(paste0("total_dwell_time_gam_plots/smooths_", model_names[i], ".png"), width = 1000, height = 800)
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
write.csv(model_metrics, "total_dwell_time_model_comparison_all.csv", row.names = FALSE)

# %% Best model
best_model_index <- which.min(model_metrics$AIC)
cat("\n✅ Best model is", model_metrics$Model[best_model_index], "with AIC =", model_metrics$AIC[best_model_index], "\n")

# %% Pairwise ANOVA: Original vs Interaction Models
originals <- model_metrics[grepl("^Model_\\d+$", model_metrics$Model), ]
interactions <- model_metrics[grepl("^Model_Interaction_\\d+$", model_metrics$Model), ]

originals$Index <- sub("Model_", "", originals$Model)
interactions$Index <- sub("Model_Interaction_", "", interactions$Model)

pairs <- merge(originals, interactions, by = "Index", suffixes = c("_orig", "_inter"))

anova_results <- list()
for (i in 1:nrow(pairs)) {
    m1 <- readRDS(pairs$Model_File_orig[i])
    m2 <- readRDS(pairs$Model_File_inter[i])

    cmp <- try(anova(m1, m2, test = "Chisq"), silent = TRUE)
    if (!inherits(cmp, "try-error")) {
        anova_results[[i]] <- data.frame(
            Model_Original = pairs$Model_orig[i],
            Model_Interaction = pairs$Model_inter[i],
            AIC_Original = AIC(m1),
            AIC_Interaction = AIC(m2),
            deltaAIC = AIC(m2) - AIC(m1),
            p_value = cmp[2, "Pr(>Chi)"]
        )
    }
}

anova_df <- do.call(rbind, anova_results)
write.csv(anova_df, "total_dwell_time_model_interaction_anova.csv", row.names = FALSE)
cat("✅ Interaction ANOVA comparison saved to total_dwell_time_model_interaction_anova.csv\n")


# %%
summary(Model_Interaction_23)
