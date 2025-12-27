# %% Load libraries
require(itsadug)
library(mgcv)
rm(list = ls())

# %% Load the dataset
time_to_first_view <- read.csv("data/time_to_first_view.csv")
print(colnames(time_to_first_view))

# %% Check for any missing values in each column
key_columns <- c("time_to_first_view_power_transformed", "voice_type", "base_image")
sapply(time_to_first_view[key_columns], function(x) any(is.na(x)))

# %% Correct the structure of the dataset
factor_cols <- c("voice_type", "user_name", "base_image", "pos_code", "voice_s_o", "subject_object", "Gender", "education", "bilingualism", "english_proficiency")
time_to_first_view[factor_cols] <- lapply(time_to_first_view[factor_cols], as.factor)

# %%
time_to_first_view$Age <- as.integer(as.character(time_to_first_view$Age))
time_to_first_view$voice_type <- relevel(time_to_first_view$voice_type, ref = "Ref")
time_to_first_view$subject_object <- relevel(time_to_first_view$subject_object, ref = "O")
time_to_first_view$education <- relevel(time_to_first_view$education, ref = "LP")
time_to_first_view$bilingualism <- relevel(time_to_first_view$bilingualism, ref = "No")
time_to_first_view$english_proficiency <- relevel(time_to_first_view$english_proficiency, ref = "LOW")
time_to_first_view$Age <- as.numeric(as.character(time_to_first_view$Age))

# %% === Create folders if they don't exist ===
dir.create("time_to_first_view_gam_models", showWarnings = FALSE)
dir.create("time_to_first_view_gam_plots", showWarnings = FALSE)


# Load formulas from the csv file
formula_reference <- read.csv("time_to_first_view_formulas.csv", stringsAsFactors = FALSE)
formulas <- lapply(formula_reference$Formula, as.formula)
# %%
# Family
ocat_family <- ocat(R = 3)

# Initialize
model_metrics <- data.frame()
summary_file <- file("time_to_first_view_gam_models/all_model_summaries.txt", open = "wt")

for (i in seq_along(formulas)) {
    model_path <- paste0("time_to_first_view_gam_models/model_", i, ".rds")

    if (file.exists(model_path)) {
        cat("⏭️ Skipping model", i, "(already exists)\n")
        next
    }

    cat("🔄 Fitting Model", i, "...\n")
    model <- bam(formulas[[i]], data = time_to_first_view)

    # Save model
    saveRDS(model, model_path)

    # Append summary
    cat("\n\n============ MODEL", i, "============\n", file = summary_file, append = TRUE)
    capture.output(summary(model), file = summary_file, append = TRUE)

    # Diagnostics
    png(paste0("time_to_first_view_gam_plots/diag_model_", i, ".png"), width = 1000, height = 800)
    par(mfrow = c(2, 2))
    gam.check(model)
    dev.off()

    # Smooth plots if available
    if (length(model$smooth) > 0) {
        png(paste0("time_to_first_view_gam_plots/smooths_model_", i, ".png"), width = 1000, height = 800)
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
write.csv(model_metrics, "time_to_first_view_model_comparison.csv", row.names = FALSE)

# Print best model
best_model_index <- which.min(model_metrics$AIC)
cat("\n✅ Best model is", model_metrics$Model[best_model_index], "with AIC =", model_metrics$AIC[best_model_index], "\n")
