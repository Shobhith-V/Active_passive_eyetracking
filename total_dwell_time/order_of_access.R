require(itsadug)
library(mgcv)
rm(list = ls())

# Load the dataset
access_order_data <- read.csv("data/order_of_access.csv")
print(colnames(access_order_data))

# Check for any missing values in each column
key_columns <- c("order_of_access", "voice_type", "base_image")
sapply(access_order_data[key_columns], function(x) any(is.na(x)))

# Correct the structure of the dataset
factor_cols <- c("voice_type", "user_name", "base_image", "voice_s_o", "pos_code", "subject_object", "Gender", "education", "bilingualism", "english_proficiency")
access_order_data[factor_cols] <- lapply(access_order_data[factor_cols], as.factor)
access_order_data$order_of_access <- factor(access_order_data$order_of_access, levels = c("1", "2", "3"))
access_order_data$order_of_access <- as.integer(as.character(access_order_data$order_of_access))
access_order_data$Age <- as.integer(as.character(access_order_data$Age))
access_order_data$voice_type <- relevel(access_order_data$voice_type, ref = "Ref")
access_order_data$subject_object <- relevel(access_order_data$subject_object, ref = "O")
access_order_data$education <- relevel(access_order_data$education, ref = "LP")
access_order_data$bilingualism <- relevel(access_order_data$bilingualism, ref = "No")
access_order_data$english_proficiency <- relevel(access_order_data$english_proficiency, ref = "LOW")
access_order_data$Age <- as.numeric(as.character(access_order_data$Age))

# === Create folders if they don't exist ===
dir.create("order_of_access_gam_models", showWarnings = FALSE)
dir.create("order_of_access_gam_plots", showWarnings = FALSE)


# Load formulas from the csv file
formula_reference <- read.csv("order_of_access_model_formulas.csv", stringsAsFactors = FALSE)
formulas <- lapply(formula_reference$Formula, as.formula)

# Family
ocat_family <- ocat(R = 3)

# Initialize
model_metrics <- data.frame()
summary_file <- file("order_of_access_gam_models/all_model_summaries.txt", open = "wt")

for (i in seq_along(formulas)) {
    model_path <- paste0("order_of_access_gam_models/model_", i, ".rds")

    if (file.exists(model_path)) {
        cat("⏭️ Skipping model", i, "(already exists)\n")
        next
    }

    cat("🔄 Fitting Model", i, "...\n")
    model <- bam(formulas[[i]], data = access_order_data, family = ocat_family, method = "fREML")

    # Save model
    saveRDS(model, model_path)

    # Append summary
    cat("\n\n============ MODEL", i, "============\n", file = summary_file, append = TRUE)
    capture.output(summary(model), file = summary_file, append = TRUE)

    # Diagnostics
    png(paste0("order_of_access_gam_plots/diag_model_", i, ".png"), width = 1000, height = 800)
    par(mfrow = c(2, 2))
    gam.check(model)
    dev.off()

    # Smooth plots if available
    if (length(model$smooth) > 0) {
        png(paste0("order_of_access_gam_plots/smooths_model_", i, ".png"), width = 1000, height = 800)
        plot(model, pages = 1, se = TRUE, shade = TRUE, main = paste("Smooths: Model", i))
        dev.off()
    }

    # Metrics
    model_summary <- summary(model)
    model_metrics <- rbind(model_metrics, data.frame(
        Model = paste0("Model_", i),
        Formula = formula_reference$Formula[i],
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

# Close and save metrics
close(summary_file)
model_metrics <- model_metrics[order(model_metrics$AIC), ]
write.csv(model_metrics, "order_of_access_model_comparison.csv", row.names = FALSE)

# Print best model
best_model_index <- which.min(model_metrics$AIC)
cat("\n✅ Best model is", model_metrics$Model[best_model_index], "with AIC =", model_metrics$AIC[best_model_index], "\n")
