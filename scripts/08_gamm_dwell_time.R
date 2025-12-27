# %% GAMM Model: Total Dwell Time
# Script: 08_gamm_dwell_time.R
# Purpose: Model total dwell time per AOI per trial

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
dir.create("models/dwell_time_models", showWarnings = FALSE, recursive = TRUE)
dir.create("results/model_summaries", showWarnings = FALSE, recursive = TRUE)

# Load data
cat("Loading data...\n")
interest_area_data <- read.csv("data/processed/merged_interest_area_data.csv", stringsAsFactors = FALSE)

# Prepare data
dwell_data <- interest_area_data %>%
  filter(
    !is.na(IA_DWELL_TIME) &
    !is.na(IA_LABEL) &
    IA_LABEL != "" &
    !is.na(aoi_type) &
    aoi_type != "other"
  )

# Add voice_type if missing
if (!"voice_type" %in% names(dwell_data)) {
  dwell_data$voice_type <- ifelse(is.na(dwell_data$voice_id) | 
                                    dwell_data$voice_id == "UNDEFINEDnull",
                                    "unknown", dwell_data$voice_id)
}

# Convert to factors
dwell_data$voice_type <- as.factor(dwell_data$voice_type)
dwell_data$aoi_type <- as.factor(dwell_data$aoi_type)
dwell_data$participant_id <- as.factor(dwell_data$participant_id)
dwell_data$trial_id <- as.factor(dwell_data$trial_id)

# Set reference levels
dwell_data$voice_type <- relevel(dwell_data$voice_type, ref = levels(dwell_data$voice_type)[1])
dwell_data$aoi_type <- relevel(dwell_data$aoi_type, ref = "subject")

# Log transform dwell time
dwell_data$log_dwell_time <- log(dwell_data$IA_DWELL_TIME + 1)

cat(sprintf("Data prepared: %d dwell time records\n", nrow(dwell_data)))

# %% Model 1: Basic model
cat("\nFitting Model 1: Basic model...\n")

model1 <- bam(
  log_dwell_time ~ 
    voice_type + 
    aoi_type + 
    voice_type:aoi_type +
    s(participant_id, bs = "re") +
    s(trial_id, bs = "re"),
  data = dwell_data,
  method = "fREML"
)

saveRDS(model1, "models/dwell_time_models/model1_basic.rds")
summary1 <- summary(model1)
capture.output(summary1, file = "results/model_summaries/dwell_time_model1_summary.txt")

# %% Model 2: With additional predictors
cat("\nFitting Model 2: With additional predictors...\n")

model2 <- bam(
  log_dwell_time ~ 
    voice_type + 
    aoi_type + 
    voice_type:aoi_type +
    s(IA_AREA, k = 5) +
    s(participant_id, bs = "re") +
    s(trial_id, bs = "re"),
  data = dwell_data %>% filter(!is.na(IA_AREA)),
  method = "fREML"
)

saveRDS(model2, "models/dwell_time_models/model2_with_area.rds")
summary2 <- summary(model2)
capture.output(summary2, file = "results/model_summaries/dwell_time_model2_summary.txt")

# %% Model comparison
model_comparison <- data.frame(
  Model = c("Model 1: Basic", "Model 2: With Area"),
  AIC = c(AIC(model1), AIC(model2)),
  BIC = c(BIC(model1), BIC(model2)),
  Deviance_Explained = c(summary1$dev.expl * 100, summary2$dev.expl * 100),
  R_sq = c(summary1$r.sq, summary2$r.sq)
)

write.csv(model_comparison, "results/model_summaries/dwell_time_model_comparison.csv", row.names = FALSE)

cat("\n=== Dwell Time Modeling Complete ===\n")

