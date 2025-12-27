# %% Data Merging
# Script: 03_merge_datasets.R
# Purpose: Merge fixation, interest_area, and saccade data by participant and trial

# Load required libraries
library(dplyr)
library(tidyr)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Load processed data
cat("Loading processed data...\n")
fixation_data <- read.csv("data/processed/fixation_with_variables.csv", stringsAsFactors = FALSE)
interest_area_data <- read.csv("data/processed/interest_area_with_variables.csv", stringsAsFactors = FALSE)
saccade_data <- read.csv("data/processed/saccade_with_variables.csv", stringsAsFactors = FALSE)

trial_fixation_summary <- read.csv("data/processed/trial_fixation_summary.csv", stringsAsFactors = FALSE)
trial_summary <- read.csv("data/processed/trial_summary.csv", stringsAsFactors = FALSE)
trial_saccade_summary <- read.csv("data/processed/trial_saccade_summary.csv", stringsAsFactors = FALSE)

# %% Create common trial identifiers
# Ensure all datasets have consistent trial identifiers
fixation_data <- fixation_data %>%
  mutate(
    merge_key = paste(participant_id, TRIAL_INDEX, sentence, sep = "|")
  )

interest_area_data <- interest_area_data %>%
  mutate(
    merge_key = paste(participant_id, TRIAL_INDEX, sentence, sep = "|")
  )

saccade_data <- saccade_data %>%
  mutate(
    merge_key = paste(participant_id, TRIAL_INDEX, sentence, sep = "|")
  )

trial_summary <- trial_summary %>%
  mutate(
    merge_key = paste(participant_id, TRIAL_INDEX, sentence, sep = "|")
  )

# %% Merge trial-level summaries
cat("Merging trial-level summaries...\n")

# Start with trial summary as base
merged_trial_data <- trial_summary %>%
  left_join(
    trial_saccade_summary %>%
      select(participant_id, TRIAL_INDEX, sentence, n_saccades, mean_saccade_amplitude,
             mean_saccade_duration, mean_saccade_velocity, mean_peak_velocity),
    by = c("participant_id", "TRIAL_INDEX", "sentence")
  ) %>%
  # Add AOI-specific fixation summaries (pivot wider)
  left_join(
    trial_fixation_summary %>%
      select(participant_id, TRIAL_INDEX, sentence, aoi_type, total_fixation_duration,
             n_fixations, mean_fixation_duration, time_to_first_fixation) %>%
      pivot_wider(
        names_from = aoi_type,
        values_from = c(total_fixation_duration, n_fixations, mean_fixation_duration, time_to_first_fixation),
        names_sep = "_"
      ),
    by = c("participant_id", "TRIAL_INDEX", "sentence")
  )

# %% Create hierarchical merged dataset at fixation level
cat("Creating hierarchical merged dataset...\n")

# Merge fixation data with trial-level information
merged_fixation_data <- fixation_data %>%
  left_join(
    trial_summary %>%
      select(participant_id, TRIAL_INDEX, sentence, total_trial_duration, trial_duration),
    by = c("participant_id", "TRIAL_INDEX", "sentence")
  ) %>%
  left_join(
    trial_saccade_summary %>%
      select(participant_id, TRIAL_INDEX, sentence, n_saccades, mean_saccade_amplitude),
    by = c("participant_id", "TRIAL_INDEX", "sentence")
  )

# %% Create hierarchical merged dataset at interest area level
merged_interest_area_data <- interest_area_data %>%
  left_join(
    trial_summary %>%
      select(participant_id, TRIAL_INDEX, sentence, total_trial_duration, trial_duration),
    by = c("participant_id", "TRIAL_INDEX", "sentence")
  ) %>%
  left_join(
    trial_saccade_summary %>%
      select(participant_id, TRIAL_INDEX, sentence, n_saccades),
    by = c("participant_id", "TRIAL_INDEX", "sentence")
  )

# %% Create hierarchical merged dataset at saccade level
merged_saccade_data <- saccade_data %>%
  left_join(
    trial_summary %>%
      select(participant_id, TRIAL_INDEX, sentence, total_trial_duration, trial_duration),
    by = c("participant_id", "TRIAL_INDEX", "sentence")
  ) %>%
  left_join(
    trial_fixation_summary %>%
      filter(aoi_type %in% c("subject", "object")) %>%
      group_by(participant_id, TRIAL_INDEX, sentence) %>%
      summarise(
        total_fixations_subject_object = sum(n_fixations, na.rm = TRUE),
        .groups = "drop"
      ),
    by = c("participant_id", "TRIAL_INDEX", "sentence")
  )

# %% Validate merge integrity
cat("Validating merge integrity...\n")

# Check for missing matches
fixation_missing <- merged_fixation_data %>%
  filter(is.na(total_trial_duration)) %>%
  nrow()

interest_area_missing <- merged_interest_area_data %>%
  filter(is.na(total_trial_duration)) %>%
  nrow()

saccade_missing <- merged_saccade_data %>%
  filter(is.na(total_trial_duration)) %>%
  nrow()

cat(sprintf("Fixation records without trial match: %d\n", fixation_missing))
cat(sprintf("Interest area records without trial match: %d\n", interest_area_missing))
cat(sprintf("Saccade records without trial match: %d\n", saccade_missing))

# Check for duplicate merge keys
duplicate_trials <- merged_trial_data %>%
  group_by(participant_id, TRIAL_INDEX, sentence) %>%
  summarise(n = n(), .groups = "drop") %>%
  filter(n > 1)

if (nrow(duplicate_trials) > 0) {
  cat(sprintf("Warning: %d duplicate trial entries found\n", nrow(duplicate_trials)))
} else {
  cat("No duplicate trial entries found\n")
}

# %% Save merged datasets
cat("Saving merged datasets...\n")

write.csv(merged_trial_data, "data/processed/merged_trial_data.csv", row.names = FALSE)
write.csv(merged_fixation_data, "data/processed/merged_fixation_data.csv", row.names = FALSE)
write.csv(merged_interest_area_data, "data/processed/merged_interest_area_data.csv", row.names = FALSE)
write.csv(merged_saccade_data, "data/processed/merged_saccade_data.csv", row.names = FALSE)

# Also save a comprehensive merged dataset (all data in one file)
# This will be large, so we'll create a sample or aggregated version
cat("Creating comprehensive merged dataset...\n")

# Create a comprehensive dataset with key variables from all sources
comprehensive_data <- merged_trial_data %>%
  # Add participant-level identifiers
  mutate(
    data_level = "trial"
  )

# Save comprehensive dataset
write.csv(comprehensive_data, "data/processed/merged_data.csv", row.names = FALSE)

cat("\n=== Merge Summary ===\n")
cat(sprintf("Merged trial records: %d\n", nrow(merged_trial_data)))
cat(sprintf("Merged fixation records: %d\n", nrow(merged_fixation_data)))
cat(sprintf("Merged interest area records: %d\n", nrow(merged_interest_area_data)))
cat(sprintf("Merged saccade records: %d\n", nrow(merged_saccade_data)))
cat("\nData merging complete!\n")

