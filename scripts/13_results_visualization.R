# %% Results Visualization
# Script: 13_results_visualization.R
# Purpose: Create publication-ready plots of model results

# Load required libraries
library(mgcv)
library(emmeans)
library(ggplot2)
library(dplyr)
library(tidyr)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Create output directory
dir.create("plots/results", showWarnings = FALSE, recursive = TRUE)

# %% Load models and effect sizes
cat("Loading models and results...\n")

# Load EMM results
if (file.exists("results/effect_sizes/estimated_marginal_means.csv")) {
  emm_results <- read.csv("results/effect_sizes/estimated_marginal_means.csv", stringsAsFactors = FALSE)
}

# Load effect sizes
if (file.exists("results/effect_sizes/voice_type_effect_sizes.csv")) {
  effect_sizes <- read.csv("results/effect_sizes/voice_type_effect_sizes.csv", stringsAsFactors = FALSE)
}

# %% Plot smooth terms with confidence bands
cat("Creating smooth term plots...\n")

# Load fixation duration model
if (file.exists("models/fixation_duration_models/model3_interaction_smooth.rds")) {
  model <- readRDS("models/fixation_duration_models/model3_interaction_smooth.rds")
  
  # Plot smooth terms
  png("plots/results/fixation_duration_smooth_terms.png", width = 1200, height = 800, res = 300)
  plot(model, pages = 1, se = TRUE, shade = TRUE, 
       main = "Smooth Terms: Fixation Duration Model")
  dev.off()
}

# %% Interaction plots (voice × AOI)
cat("Creating interaction plots...\n")

if (exists("emm_results") && nrow(emm_results) > 0) {
  # Filter for fixation duration model if available
  if (any(grepl("fixation", emm_results$model))) {
    fixation_emm <- emm_results %>%
      filter(grepl("fixation", model)) %>%
      filter(!is.na(voice_type) & !is.na(aoi_type))
    
    if (nrow(fixation_emm) > 0) {
      p_interaction <- ggplot(fixation_emm, 
                             aes(x = voice_type, y = emmean, color = aoi_type)) +
        geom_point(size = 3, position = position_dodge(width = 0.3)) +
        geom_line(aes(group = aoi_type), position = position_dodge(width = 0.3), size = 1) +
        geom_errorbar(aes(ymin = lower.CL, ymax = upper.CL),
                     width = 0.1, position = position_dodge(width = 0.3)) +
        labs(title = "Estimated Marginal Means: Fixation Duration",
             x = "Voice Type",
             y = "Estimated Mean (log scale)",
             color = "AOI Type") +
        theme_minimal(base_size = 12) +
        theme(legend.position = "right")
      
      ggsave("plots/results/fixation_duration_interaction.png", 
             p_interaction, width = 10, height = 6, dpi = 300)
    }
  }
}

# %% Model predictions
cat("Creating prediction plots...\n")

# Create prediction plots for key comparisons
if (file.exists("models/fixation_duration_models/model3_interaction_smooth.rds")) {
  model <- readRDS("models/fixation_duration_models/model3_interaction_smooth.rds")
  
  # Load data for predictions
  fixation_data <- read.csv("data/processed/merged_fixation_data_with_flags.csv", stringsAsFactors = FALSE)
  fixation_clean <- fixation_data %>% filter(!exclude_fixation)
  
  # Create prediction data frame
  pred_data <- expand.grid(
    voice_type = unique(fixation_clean$voice_type),
    aoi_type = c("subject", "object"),
    participant_id = levels(factor(fixation_clean$participant_id))[1],
    trial_id = levels(factor(fixation_clean$trial_id))[1],
    trial_time_norm = seq(0, 1, length.out = 20)
  )
  
  # Make predictions
  pred_data$predicted <- predict(model, newdata = pred_data, type = "response")
  
  # Plot predictions
  p_pred <- ggplot(pred_data, aes(x = trial_time_norm, y = predicted, color = voice_type)) +
    geom_line(size = 1) +
    facet_wrap(~ aoi_type) +
    labs(title = "Model Predictions: Fixation Duration Over Trial Time",
         x = "Normalized Trial Time",
         y = "Predicted Log Fixation Duration",
         color = "Voice Type") +
    theme_minimal()
  
  ggsave("plots/results/fixation_duration_predictions.png", 
         p_pred, width = 12, height = 6, dpi = 300)
}

# %% Effect size plots
cat("Creating effect size plots...\n")

if (exists("effect_sizes") && nrow(effect_sizes) > 0) {
  p_effects <- ggplot(effect_sizes, 
                      aes(x = predictor, y = estimate, ymin = ci_lower, ymax = ci_upper)) +
    geom_pointrange(size = 1) +
    geom_hline(yintercept = 0, linetype = "dashed", color = "red") +
    facet_wrap(~ model, scales = "free_x") +
    labs(title = "Effect Sizes: Voice Type Comparisons",
         x = "Predictor",
         y = "Estimate (95% CI)") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  
  ggsave("plots/results/effect_sizes_plot.png", 
         p_effects, width = 12, height = 8, dpi = 300)
}

# %% Summary figure combining key results
cat("Creating summary figure...\n")

# This would combine multiple plots into one figure
# For now, we'll create individual publication-ready figures

cat("\n=== Results Visualization Complete ===\n")
cat("Plots saved to plots/results/\n")



