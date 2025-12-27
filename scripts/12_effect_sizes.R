# %% Effect Size Calculations
# Script: 12_effect_sizes.R
# Purpose: Calculate effect sizes and confidence intervals

# Load required libraries
library(mgcv)
library(emmeans)
library(dplyr)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Create output directories
dir.create("results/effect_sizes", showWarnings = FALSE, recursive = TRUE)

# %% Load models
cat("Loading models...\n")

models <- list()

if (file.exists("models/fixation_duration_models/model3_interaction_smooth.rds")) {
  models[["fixation_duration"]] <- readRDS("models/fixation_duration_models/model3_interaction_smooth.rds")
}

if (file.exists("models/dwell_time_models/model1_basic.rds")) {
  models[["dwell_time"]] <- readRDS("models/dwell_time_models/model1_basic.rds")
}

if (file.exists("models/saccade_models/model_amplitude.rds")) {
  models[["saccade_amplitude"]] <- readRDS("models/saccade_models/model_amplitude.rds")
}

# %% Calculate estimated marginal means
cat("Calculating estimated marginal means...\n")

emm_results <- list()

for (model_name in names(models)) {
  cat(sprintf("Processing %s...\n", model_name))
  
  model <- models[[model_name]]
  
  tryCatch({
    # Extract fixed effects
    fixed_effects <- names(model$coefficients)[!grepl("^s\\(|Intercept", names(model$coefficients))]
    
    if (length(fixed_effects) > 0) {
      # Create emmeans object
      # Adjust formula based on model structure
      if ("voice_type" %in% fixed_effects && "aoi_type" %in% fixed_effects) {
        emm <- emmeans(model, ~ voice_type * aoi_type, type = "response")
        emm_df <- as.data.frame(emm)
        emm_df$model <- model_name
        emm_results[[model_name]] <- emm_df
      } else if ("voice_type" %in% fixed_effects) {
        emm <- emmeans(model, ~ voice_type, type = "response")
        emm_df <- as.data.frame(emm)
        emm_df$model <- model_name
        emm_results[[model_name]] <- emm_df
      }
    }
  }, error = function(e) {
    cat(sprintf("Error calculating EMMs for %s: %s\n", model_name, e$message))
  })
}

# Combine EMM results
if (length(emm_results) > 0) {
  all_emm <- do.call(rbind, emm_results)
  write.csv(all_emm, "results/effect_sizes/estimated_marginal_means.csv", row.names = FALSE)
}

# %% Calculate effect sizes for voice type differences
cat("Calculating effect sizes...\n")

effect_sizes <- list()

for (model_name in names(models)) {
  model <- models[[model_name]]
  model_summary <- summary(model)
  
  # Extract coefficients
  coef_table <- model_summary$p.table
  
  if ("voice_type" %in% rownames(coef_table)) {
    voice_coefs <- coef_table[grepl("voice_type", rownames(coef_table)), , drop = FALSE]
    
    effect_sizes[[model_name]] <- data.frame(
      model = model_name,
      predictor = rownames(voice_coefs),
      estimate = voice_coefs[, "Estimate"],
      se = voice_coefs[, "Std. Error"],
      t_value = voice_coefs[, "t value"],
      p_value = voice_coefs[, "Pr(>|t|)"],
      ci_lower = voice_coefs[, "Estimate"] - 1.96 * voice_coefs[, "Std. Error"],
      ci_upper = voice_coefs[, "Estimate"] + 1.96 * voice_coefs[, "Std. Error"],
      stringsAsFactors = FALSE
    )
  }
}

# Combine effect sizes
if (length(effect_sizes) > 0) {
  all_effect_sizes <- do.call(rbind, effect_sizes)
  write.csv(all_effect_sizes, "results/effect_sizes/voice_type_effect_sizes.csv", row.names = FALSE)
}

# %% Calculate confidence intervals for smooth terms
cat("Calculating confidence intervals for smooth terms...\n")

smooth_ci <- list()

for (model_name in names(models)) {
  model <- models[[model_name]]
  
  if (length(model$smooth) > 0) {
    # Extract smooth term information
    smooth_summary <- summary(model)$s.table
    
    smooth_ci[[model_name]] <- data.frame(
      model = model_name,
      smooth_term = rownames(smooth_summary),
      edf = smooth_summary[, "edf"],
      ref_df = smooth_summary[, "Ref.df"],
      f_value = smooth_summary[, "F"],
      p_value = smooth_summary[, "p-value"],
      stringsAsFactors = FALSE
    )
  }
}

if (length(smooth_ci) > 0) {
  all_smooth_ci <- do.call(rbind, smooth_ci)
  write.csv(all_smooth_ci, "results/effect_sizes/smooth_terms_summary.csv", row.names = FALSE)
}

cat("\n=== Effect Size Calculations Complete ===\n")
cat("Results saved to results/effect_sizes/\n")

