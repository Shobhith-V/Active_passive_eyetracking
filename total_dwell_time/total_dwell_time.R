# %% Load libraries
require(itsadug)
library(mgcv)
rm(list = ls())

# %% Load the dataset
total_dwell_time <- read.csv("data/total_dwell_time.csv")
print(colnames(total_dwell_time))

# %% Check for any missing values in each column
key_columns <- c("total_dwell_time_power_tranformed", "voice_type", "base_image")
sapply(total_dwell_time[key_columns], function(x) any(is.na(x)))

# %% Correct the structure of the dataset
factor_cols <- c("voice_type", "user_name", "base_image", "pos_code", "voice_s_o", "subject_object", "Gender", "education", "bilingualism", "english_proficiency")
total_dwell_time[factor_cols] <- lapply(total_dwell_time[factor_cols], as.factor)

# %%
total_dwell_time$Age <- as.integer(as.character(total_dwell_time$Age))
total_dwell_time$voice_type <- relevel(total_dwell_time$voice_type, ref = "Ref")
total_dwell_time$subject_object <- relevel(total_dwell_time$subject_object, ref = "O")
total_dwell_time$education <- relevel(total_dwell_time$education, ref = "LP")
total_dwell_time$bilingualism <- relevel(total_dwell_time$bilingualism, ref = "No")
total_dwell_time$english_proficiency <- relevel(total_dwell_time$english_proficiency, ref = "LOW")
total_dwell_time$Age <- as.numeric(as.character(total_dwell_time$Age))

# %% === Create folders if they don't exist ===
dir.create("total_dwell_time_gam_models", showWarnings = FALSE)
dir.create("total_dwell_time_gam_plots", showWarnings = FALSE)


# Load formulas from the csv file
formula_reference <- read.csv("total_dwell_time_model_formulas.csv", stringsAsFactors = FALSE)
formulas <- lapply(formula_reference$Formula, as.formula)
# %%
# Family
ocat_family <- ocat(R = 3)

# Initialize
model_metrics <- data.frame()
summary_file <- file("total_dwell_time_gam_models/all_model_summaries.txt", open = "wt")

for (i in seq_along(formulas)) {
    model_path <- paste0("total_dwell_time_gam_models/model_", i, ".rds")

    if (file.exists(model_path)) {
        cat("⏭️ Skipping model", i, "(already exists)\n")
        next
    }

    cat("🔄 Fitting Model", i, "...\n")
    model <- bam(formulas[[i]], data = total_dwell_time)

    # Save model
    saveRDS(model, model_path)

    # Append summary
    cat("\n\n============ MODEL", i, "============\n", file = summary_file, append = TRUE)
    capture.output(summary(model), file = summary_file, append = TRUE)

    # Diagnostics
    png(paste0("total_dwell_time_gam_plots/diag_model_", i, ".png"), width = 1000, height = 800)
    par(mfrow = c(2, 2))
    gam.check(model)
    dev.off()

    # Smooth plots if available
    if (length(model$smooth) > 0) {
        png(paste0("total_dwell_time_gam_plots/smooths_model_", i, ".png"), width = 1000, height = 800)
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
write.csv(model_metrics, "total_dwell_time_model_comparison.csv", row.names = FALSE)

# Print best model
best_model_index <- which.min(model_metrics$AIC)
cat("\n✅ Best model is", model_metrics$Model[best_model_index], "with AIC =", model_metrics$AIC[best_model_index], "\n")
