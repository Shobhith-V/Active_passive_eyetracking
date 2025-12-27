# %% Model Diagnostics
# Script: 11_model_diagnostics.R
# Purpose: Comprehensive model diagnostics and validation

# Load required libraries
library(mgcv)
library(DHARMa)
library(itsadug)
library(dplyr)
library(ggplot2)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Create output directories
dir.create("plots/model_diagnostics", showWarnings = FALSE, recursive = TRUE)
dir.create("results/model_summaries", showWarnings = FALSE, recursive = TRUE)

# %% Load all models
cat("Loading models...\n")

models_to_check <- list()

# Fixation duration models
if (file.exists("models/fixation_duration_models/model3_interaction_smooth.rds")) {
  models_to_check[["fixation_duration"]] <- readRDS("models/fixation_duration_models/model3_interaction_smooth.rds")
}

# Dwell time models
if (file.exists("models/dwell_time_models/model1_basic.rds")) {
  models_to_check[["dwell_time"]] <- readRDS("models/dwell_time_models/model1_basic.rds")
}

# Saccade models
if (file.exists("models/saccade_models/model_amplitude.rds")) {
  models_to_check[["saccade_amplitude"]] <- readRDS("models/saccade_models/model_amplitude.rds")
}

if (file.exists("models/saccade_models/model_duration.rds")) {
  models_to_check[["saccade_duration"]] <- readRDS("models/saccade_models/model_duration.rds")
}

if (file.exists("models/saccade_models/model_velocity.rds")) {
  models_to_check[["saccade_velocity"]] <- readRDS("models/saccade_models/model_velocity.rds")
}

# Time to first fixation models
if (file.exists("models/time_to_first_fixation_models/model1_basic.rds")) {
  models_to_check[["ttff"]] <- readRDS("models/time_to_first_fixation_models/model1_basic.rds")
}

cat(sprintf("Loaded %d models for diagnostics\n", length(models_to_check)))

# %% Run diagnostics for each model
diagnostic_results <- list()

for (model_name in names(models_to_check)) {
  cat(sprintf("\nRunning diagnostics for %s...\n", model_name))
  
  model <- models_to_check[[model_name]]
  
  # GAM check
  png(sprintf("plots/model_diagnostics/%s_gam_check.png", model_name), 
      width = 1200, height = 800)
  par(mfrow = c(2, 2))
  gam_check_result <- gam.check(model)
  dev.off()
  
  # Smooth plots
  if (length(model$smooth) > 0) {
    png(sprintf("plots/model_diagnostics/%s_smooths.png", model_name),
        width = 1200, height = 800)
    plot(model, pages = 1, se = TRUE, shade = TRUE)
    dev.off()
  }
  
  # DHARMa diagnostics (if applicable)
  tryCatch({
    sim_res <- simulateResiduals(fittedModel = model, plot = FALSE)
    
    png(sprintf("plots/model_diagnostics/%s_dharma.png", model_name),
        width = 1200, height = 800)
    plot(sim_res)
    dev.off()
    
    # Test dispersion
    dispersion_test <- testDispersion(sim_res, plot = FALSE)
    
    # Test zero inflation
    zero_inflation_test <- testZeroInflation(sim_res, plot = FALSE)
    
    diagnostic_results[[model_name]] <- data.frame(
      model = model_name,
      dispersion_p = dispersion_test$p.value,
      zero_inflation_p = zero_inflation_test$p.value,
      stringsAsFactors = FALSE
    )
  }, error = function(e) {
    cat(sprintf("DHARMa diagnostics failed for %s: %s\n", model_name, e$message))
  })
  
  # Model summary metrics
  model_summary <- summary(model)
  
  diagnostic_results[[paste0(model_name, "_summary")]] <- data.frame(
    model = model_name,
    AIC = AIC(model),
    BIC = BIC(model),
    deviance_explained = model_summary$dev.expl * 100,
    r_squared = model_summary$r.sq,
    edf = sum(model_summary$edf),
    stringsAsFactors = FALSE
  )
}

# %% Combine diagnostic results
if (length(diagnostic_results) > 0) {
  # Extract summary metrics
  summary_metrics <- do.call(rbind, 
    diagnostic_results[grepl("_summary$", names(diagnostic_results))])
  
  # Extract DHARMa results
  dharma_results <- do.call(rbind,
    diagnostic_results[!grepl("_summary$", names(diagnostic_results))])
  
  write.csv(summary_metrics, "results/model_summaries/model_diagnostic_summary.csv", row.names = FALSE)
  
  if (nrow(dharma_results) > 0) {
    write.csv(dharma_results, "results/model_summaries/model_dharma_results.csv", row.names = FALSE)
  }
}

# %% Autocorrelation checks (for time series models)
cat("\nChecking autocorrelation...\n")

# Check autocorrelation for fixation duration model if it has temporal structure
if ("fixation_duration" %in% names(models_to_check)) {
  model <- models_to_check[["fixation_duration"]]
  
  # Use itsadug for autocorrelation
  tryCatch({
    acf_result <- acf_resid(model)
    
    png("plots/model_diagnostics/fixation_duration_autocorrelation.png",
        width = 1000, height = 600)
    plot(acf_result)
    dev.off()
    
    cat("Autocorrelation check complete for fixation duration model\n")
  }, error = function(e) {
    cat(sprintf("Autocorrelation check failed: %s\n", e$message))
  })
}

# %% Model comparison across all models
cat("\nCreating overall model comparison...\n")

all_model_comparison <- data.frame()

# Load all model comparison files
comparison_files <- list.files("results/model_summaries", 
                               pattern = "*_model_comparison.csv", 
                               full.names = TRUE)

if (length(comparison_files) > 0) {
  for (file in comparison_files) {
    df <- read.csv(file, stringsAsFactors = FALSE)
    df$analysis_type <- gsub("_model_comparison.csv", "", basename(file))
    all_model_comparison <- rbind(all_model_comparison, df)
  }
  
  write.csv(all_model_comparison, 
            "results/model_summaries/all_models_comparison.csv", 
            row.names = FALSE)
}

cat("\n=== Model Diagnostics Complete ===\n")
cat("Diagnostics saved to plots/model_diagnostics/\n")
cat("Summary saved to results/model_summaries/\n")



