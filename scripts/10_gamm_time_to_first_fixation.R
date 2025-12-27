# %% GAMM Model: Time to First Fixation
# Script: 10_gamm_time_to_first_fixation.R
# Purpose: Model time to first fixation on subject/object AOI

# Load required libraries
library(mgcv)
library(itsadug)
library(dplyr)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Create output directories
dir.create("models/time_to_first_fixation_models", showWarnings = FALSE, recursive = TRUE)
dir.create("results/model_summaries", showWarnings = FALSE, recursive = TRUE)

# Load data
cat("Loading data...\n")
fixation_data <- read.csv("data/processed/merged_fixation_data_with_flags.csv", stringsAsFactors = FALSE)
trial_summary <- read.csv("data/processed/trial_fixation_summary.csv", stringsAsFactors = FALSE)

# Prepare time to first fixation data
ttff_data <- trial_summary %>%
  filter(
    !is.na(time_to_first_fixation) &
    !is.na(aoi_type) &
    aoi_type %in% c("subject", "object")
  )

# Add voice_type if missing
if (!"voice_type" %in% names(ttff_data)) {
  if ("voice_id" %in% names(ttff_data)) {
    ttff_data$voice_type <- ifelse(is.na(ttff_data$voice_id) | 
                                     ttff_data$voice_id == "UNDEFINEDnull",
                                     "unknown", ttff_data$voice_id)
  } else {
    ttff_data$voice_type <- "unknown"
  }
}

# Convert to factors
ttff_data$voice_type <- as.factor(ttff_data$voice_type)
ttff_data$aoi_type <- as.factor(ttff_data$aoi_type)
ttff_data$participant_id <- as.factor(ttff_data$participant_id)
ttff_data$trial_id <- as.factor(ttff_data$trial_id)

# Set reference levels
ttff_data$voice_type <- relevel(ttff_data$voice_type, ref = levels(ttff_data$voice_type)[1])
ttff_data$aoi_type <- relevel(ttff_data$aoi_type, ref = "subject")

# Log transform time to first fixation
ttff_data$log_ttff <- log(ttff_data$time_to_first_fixation + 1)

cat(sprintf("Data prepared: %d time-to-first-fixation records\n", nrow(ttff_data)))

# %% Model 1: Basic model
cat("\nFitting Model 1: Basic model...\n")

model1 <- bam(
  log_ttff ~ 
    voice_type + 
    aoi_type + 
    voice_type:aoi_type +
    s(participant_id, bs = "re") +
    s(trial_id, bs = "re"),
  data = ttff_data,
  method = "fREML"
)

saveRDS(model1, "models/time_to_first_fixation_models/model1_basic.rds")
summary1 <- summary(model1)
capture.output(summary1, file = "results/model_summaries/ttff_model1_summary.txt")

# %% Model 2: With additional predictors
cat("\nFitting Model 2: With trial-level predictors...\n")

# Merge with trial summary for additional predictors
if (file.exists("data/processed/trial_summary.csv")) {
  trial_info <- read.csv("data/processed/trial_summary.csv", stringsAsFactors = FALSE)
  ttff_data <- ttff_data %>%
    left_join(
      trial_info %>%
        select(participant_id, TRIAL_INDEX, sentence, total_trial_fixations),
      by = c("participant_id", "TRIAL_INDEX", "sentence")
    )
  
  model2 <- bam(
    log_ttff ~ 
      voice_type + 
      aoi_type + 
      voice_type:aoi_type +
      s(total_trial_fixations, k = 5) +
      s(participant_id, bs = "re") +
      s(trial_id, bs = "re"),
    data = ttff_data %>% filter(!is.na(total_trial_fixations)),
    method = "fREML"
  )
  
  saveRDS(model2, "models/time_to_first_fixation_models/model2_with_trial_predictors.rds")
  summary2 <- summary(model2)
  capture.output(summary2, file = "results/model_summaries/ttff_model2_summary.txt")
  
  # Model comparison
  model_comparison <- data.frame(
    Model = c("Model 1: Basic", "Model 2: With Trial Predictors"),
    AIC = c(AIC(model1), AIC(model2)),
    BIC = c(BIC(model1), BIC(model2)),
    Deviance_Explained = c(summary1$dev.expl * 100, summary2$dev.expl * 100),
    R_sq = c(summary1$r.sq, summary2$r.sq)
  )
} else {
  model_comparison <- data.frame(
    Model = "Model 1: Basic",
    AIC = AIC(model1),
    BIC = BIC(model1),
    Deviance_Explained = summary1$dev.expl * 100,
    R_sq = summary1$r.sq
  )
}

write.csv(model_comparison, "results/model_summaries/ttff_model_comparison.csv", row.names = FALSE)

cat("\n=== Time to First Fixation Modeling Complete ===\n")



