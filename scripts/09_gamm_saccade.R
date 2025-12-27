# %% GAMM Models: Saccade Metrics
# Script: 09_gamm_saccade.R
# Purpose: Model saccade amplitude, duration, and velocity

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
dir.create("models/saccade_models", showWarnings = FALSE, recursive = TRUE)
dir.create("results/model_summaries", showWarnings = FALSE, recursive = TRUE)

# Load data
cat("Loading data...\n")
saccade_data <- read.csv("data/processed/merged_saccade_data_with_flags.csv", stringsAsFactors = FALSE)

# Filter excluded data
saccade_clean <- saccade_data %>% filter(!exclude_saccade)

# Add voice_type if missing
if (!"voice_type" %in% names(saccade_clean)) {
  saccade_clean$voice_type <- ifelse(is.na(saccade_clean$voice_id) | 
                                      saccade_clean$voice_id == "UNDEFINEDnull",
                                      "unknown", saccade_clean$voice_id)
}

# Convert to factors
saccade_clean$voice_type <- as.factor(saccade_clean$voice_type)
saccade_clean$participant_id <- as.factor(saccade_clean$participant_id)
saccade_clean$trial_id <- as.factor(saccade_clean$trial_id)

# Set reference levels
saccade_clean$voice_type <- relevel(saccade_clean$voice_type, ref = levels(saccade_clean$voice_type)[1])

# Prepare saccade transition variable
if ("saccade_transition" %in% names(saccade_clean)) {
  saccade_clean$saccade_transition <- as.factor(saccade_clean$saccade_transition)
}

cat(sprintf("Data prepared: %d saccade records\n", nrow(saccade_clean)))

# %% Model 1: Saccade Amplitude
cat("\nFitting Model 1: Saccade Amplitude...\n")

saccade_amplitude <- saccade_clean %>%
  filter(!is.na(CURRENT_SAC_AMPLITUDE) & CURRENT_SAC_AMPLITUDE > 0)

# Log transform amplitude
saccade_amplitude$log_amplitude <- log(saccade_amplitude$CURRENT_SAC_AMPLITUDE + 1)

model_amplitude <- bam(
  log_amplitude ~ 
    voice_type +
    s(participant_id, bs = "re") +
    s(trial_id, bs = "re"),
  data = saccade_amplitude,
  method = "fREML"
)

saveRDS(model_amplitude, "models/saccade_models/model_amplitude.rds")
summary_amplitude <- summary(model_amplitude)
capture.output(summary_amplitude, file = "results/model_summaries/saccade_amplitude_summary.txt")

# %% Model 2: Saccade Duration
cat("\nFitting Model 2: Saccade Duration...\n")

saccade_duration <- saccade_clean %>%
  filter(!is.na(CURRENT_SAC_DURATION) & CURRENT_SAC_DURATION > 0)

saccade_duration$log_duration <- log(saccade_duration$CURRENT_SAC_DURATION + 1)

model_duration <- bam(
  log_duration ~ 
    voice_type +
    s(participant_id, bs = "re") +
    s(trial_id, bs = "re"),
  data = saccade_duration,
  method = "fREML"
)

saveRDS(model_duration, "models/saccade_models/model_duration.rds")
summary_duration <- summary(model_duration)
capture.output(summary_duration, file = "results/model_summaries/saccade_duration_summary.txt")

# %% Model 3: Saccade Average Velocity
cat("\nFitting Model 3: Saccade Average Velocity...\n")

saccade_velocity <- saccade_clean %>%
  filter(!is.na(CURRENT_SAC_AVG_VELOCITY) & CURRENT_SAC_AVG_VELOCITY > 0)

saccade_velocity$log_velocity <- log(saccade_velocity$CURRENT_SAC_AVG_VELOCITY + 1)

model_velocity <- bam(
  log_velocity ~ 
    voice_type +
    s(participant_id, bs = "re") +
    s(trial_id, bs = "re"),
  data = saccade_velocity,
  method = "fREML"
)

saveRDS(model_velocity, "models/saccade_models/model_velocity.rds")
summary_velocity <- summary(model_velocity)
capture.output(summary_velocity, file = "results/model_summaries/saccade_velocity_summary.txt")

# %% Model 4: Saccade transitions (if available)
if ("saccade_transition" %in% names(saccade_clean)) {
  cat("\nFitting Model 4: Saccade Transitions...\n")
  
  saccade_transitions <- saccade_clean %>%
    filter(!is.na(saccade_transition) & 
           saccade_transition != "other" &
           !is.na(CURRENT_SAC_AMPLITUDE))
  
  saccade_transitions$log_amplitude <- log(saccade_transitions$CURRENT_SAC_AMPLITUDE + 1)
  
  model_transitions <- bam(
    log_amplitude ~ 
      voice_type +
      saccade_transition +
      voice_type:saccade_transition +
      s(participant_id, bs = "re") +
      s(trial_id, bs = "re"),
    data = saccade_transitions,
    method = "fREML"
  )
  
  saveRDS(model_transitions, "models/saccade_models/model_transitions.rds")
  summary_transitions <- summary(model_transitions)
  capture.output(summary_transitions, file = "results/model_summaries/saccade_transitions_summary.txt")
}

# %% Model comparison
model_comparison <- data.frame(
  Model = c("Amplitude", "Duration", "Velocity"),
  AIC = c(AIC(model_amplitude), AIC(model_duration), AIC(model_velocity)),
  BIC = c(BIC(model_amplitude), BIC(model_duration), BIC(model_velocity)),
  Deviance_Explained = c(
    summary_amplitude$dev.expl * 100,
    summary_duration$dev.expl * 100,
    summary_velocity$dev.expl * 100
  ),
  R_sq = c(
    summary_amplitude$r.sq,
    summary_duration$r.sq,
    summary_velocity$r.sq
  )
)

write.csv(model_comparison, "results/model_summaries/saccade_model_comparison.csv", row.names = FALSE)

cat("\n=== Saccade Modeling Complete ===\n")



