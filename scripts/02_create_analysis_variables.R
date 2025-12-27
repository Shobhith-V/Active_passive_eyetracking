# %% Variable Extraction and Creation
# Script: 02_create_analysis_variables.R
# Purpose: Extract voice type, create AOI categories, create trial-level aggregations

# Load required libraries
library(dplyr)
library(tidyr)
library(stringr)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Load cleaned data
cat("Loading cleaned data...\n")
fixation_data <- read.csv("data/processed/fixation_cleaned.csv", stringsAsFactors = FALSE)
interest_area_data <- read.csv("data/processed/interest_area_cleaned.csv", stringsAsFactors = FALSE)
saccade_data <- read.csv("data/processed/saccade_cleaned.csv", stringsAsFactors = FALSE)

# %% Extract voice type from voice_id or other variables
# Based on existing code patterns, voice_type might be in voice_id or need to be extracted
# For now, we'll create a function to extract it from available variables

extract_voice_type <- function(df) {
  # Check if voice_type exists directly
  if ("voice_type" %in% names(df)) {
    return(df)
  }
  
  # Try to extract from voice_id or other variables
  # This is a placeholder - adjust based on actual data structure
  if ("voice_id" %in% names(df)) {
    # If voice_id contains voice type information, extract it
    # Otherwise, we may need to infer from sentence structure or other variables
    df$voice_type <- NA  # Placeholder - will be filled based on actual data
  }
  
  return(df)
}

# %% Create AOI categories from interest area labels
create_aoi_categories <- function(label) {
  if (is.na(label) || label == "" || label == ".") {
    return("other")
  }
  
  # Check if label starts with s_ (subject) or o_ (object)
  if (str_detect(label, "^s_")) {
    return("subject")
  } else if (str_detect(label, "^o_")) {
    return("object")
  } else {
    return("other")
  }
}

# %% Process Fixation Data
cat("Processing fixation data...\n")

fixation_data <- fixation_data %>%
  mutate(
    # Create AOI type from interest area label
    aoi_type = sapply(CURRENT_FIX_INTEREST_AREA_LABEL, create_aoi_categories),
    
    # Create trial identifier
    trial_id = paste(participant_id, TRIAL_INDEX, sep = "_"),
    
    # Calculate time relative to trial start (in ms)
    time_from_trial_start = CURRENT_FIX_START - TRIAL_START_TIME,
    
    # Create time windows (early, middle, late) - will be calculated per trial
    time_window = NA  # Placeholder, will be calculated below
  )

# Calculate time windows per trial
fixation_data <- fixation_data %>%
  group_by(trial_id) %>%
  mutate(
    trial_duration = max(CURRENT_FIX_END, na.rm = TRUE) - min(CURRENT_FIX_START, na.rm = TRUE),
    time_window = case_when(
      time_from_trial_start <= trial_duration / 3 ~ "early",
      time_from_trial_start <= 2 * trial_duration / 3 ~ "middle",
      TRUE ~ "late"
    )
  ) %>%
  ungroup()

# %% Process Interest Area Data
cat("Processing interest area data...\n")

interest_area_data <- interest_area_data %>%
  mutate(
    # Create AOI type from label
    aoi_type = sapply(IA_LABEL, create_aoi_categories),
    
    # Create trial identifier
    trial_id = paste(participant_id, TRIAL_INDEX, sep = "_"),
    
    # Ensure numeric columns are numeric
    IA_DWELL_TIME = as.numeric(IA_DWELL_TIME),
    IA_FIXATION_COUNT = as.numeric(IA_FIXATION_COUNT),
    IA_FIRST_FIXATION_TIME = as.numeric(IA_FIRST_FIXATION_TIME)
  )

# %% Process Saccade Data
cat("Processing saccade data...\n")

saccade_data <- saccade_data %>%
  mutate(
    # Create AOI types for start and end
    aoi_type_start = sapply(CURRENT_SAC_START_INTEREST_AREA_LABEL, create_aoi_categories),
    aoi_type_end = sapply(CURRENT_SAC_END_INTEREST_AREA_LABEL, create_aoi_categories),
    
    # Create saccade transition type
    saccade_transition = case_when(
      aoi_type_start == "subject" & aoi_type_end == "object" ~ "subject_to_object",
      aoi_type_start == "object" & aoi_type_end == "subject" ~ "object_to_subject",
      aoi_type_start == "subject" & aoi_type_end == "subject" ~ "subject_to_subject",
      aoi_type_start == "object" & aoi_type_end == "object" ~ "object_to_object",
      TRUE ~ "other"
    ),
    
    # Create trial identifier
    trial_id = paste(participant_id, TRIAL_INDEX, sep = "_"),
    
    # Calculate time relative to trial start
    time_from_trial_start = CURRENT_SAC_START_TIME - TRIAL_START_TIME
  )

# %% Create Trial-Level Aggregations for Fixation Data
cat("Creating trial-level aggregations for fixation data...\n")

trial_fixation_summary <- fixation_data %>%
  group_by(participant_id, trial_id, TRIAL_INDEX, aoi_type, sentence, voice_id, image_id, stim_id) %>%
  summarise(
    total_fixation_duration = sum(CURRENT_FIX_DURATION, na.rm = TRUE),
    n_fixations = n(),
    mean_fixation_duration = mean(CURRENT_FIX_DURATION, na.rm = TRUE),
    median_fixation_duration = median(CURRENT_FIX_DURATION, na.rm = TRUE),
    first_fixation_time = min(CURRENT_FIX_START, na.rm = TRUE),
    last_fixation_time = max(CURRENT_FIX_END, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  # Calculate time to first fixation on this AOI type
  group_by(participant_id, trial_id) %>%
  mutate(
    time_to_first_fixation = first_fixation_time - min(first_fixation_time, na.rm = TRUE)
  ) %>%
  ungroup()

# Overall trial summary (across all AOIs)
trial_summary <- fixation_data %>%
  group_by(participant_id, trial_id, TRIAL_INDEX, sentence, voice_id, image_id, stim_id) %>%
  summarise(
    total_trial_fixations = n(),
    total_trial_duration = sum(CURRENT_FIX_DURATION, na.rm = TRUE),
    mean_fixation_duration = mean(CURRENT_FIX_DURATION, na.rm = TRUE),
    trial_start_time = min(CURRENT_FIX_START, na.rm = TRUE),
    trial_end_time = max(CURRENT_FIX_END, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(
    trial_duration = trial_end_time - trial_start_time
  )

# %% Create Trial-Level Aggregations for Saccade Data
cat("Creating trial-level aggregations for saccade data...\n")

trial_saccade_summary <- saccade_data %>%
  group_by(participant_id, trial_id, TRIAL_INDEX, sentence, voice_id, image_id, stim_id) %>%
  summarise(
    n_saccades = n(),
    mean_saccade_amplitude = mean(CURRENT_SAC_AMPLITUDE, na.rm = TRUE),
    mean_saccade_duration = mean(CURRENT_SAC_DURATION, na.rm = TRUE),
    mean_saccade_velocity = mean(CURRENT_SAC_AVG_VELOCITY, na.rm = TRUE),
    mean_peak_velocity = mean(CURRENT_SAC_PEAK_VELOCITY, na.rm = TRUE),
    .groups = "drop"
  )

# Saccade transition summary
saccade_transition_summary <- saccade_data %>%
  filter(!is.na(saccade_transition), saccade_transition != "other") %>%
  group_by(participant_id, trial_id, TRIAL_INDEX, saccade_transition, sentence, voice_id) %>%
  summarise(
    n_transitions = n(),
    mean_amplitude = mean(CURRENT_SAC_AMPLITUDE, na.rm = TRUE),
    mean_duration = mean(CURRENT_SAC_DURATION, na.rm = TRUE),
    .groups = "drop"
  )

# %% Extract sentence-level variables
# This function extracts information from the sentence column if needed
extract_sentence_info <- function(sentence_col) {
  # Placeholder - adjust based on actual sentence structure
  # For now, return the sentence as-is
  return(sentence_col)
}

# Add sentence info to all datasets
fixation_data$sentence_clean <- extract_sentence_info(fixation_data$sentence)
interest_area_data$sentence_clean <- extract_sentence_info(interest_area_data$sentence)
saccade_data$sentence_clean <- extract_sentence_info(saccade_data$sentence)

# %% Save processed data with new variables
cat("Saving processed data...\n")

write.csv(fixation_data, "data/processed/fixation_with_variables.csv", row.names = FALSE)
write.csv(interest_area_data, "data/processed/interest_area_with_variables.csv", row.names = FALSE)
write.csv(saccade_data, "data/processed/saccade_with_variables.csv", row.names = FALSE)

# Save trial-level summaries
write.csv(trial_fixation_summary, "data/processed/trial_fixation_summary.csv", row.names = FALSE)
write.csv(trial_summary, "data/processed/trial_summary.csv", row.names = FALSE)
write.csv(trial_saccade_summary, "data/processed/trial_saccade_summary.csv", row.names = FALSE)
write.csv(saccade_transition_summary, "data/processed/saccade_transition_summary.csv", row.names = FALSE)

cat("\n=== Variable Creation Summary ===\n")
cat(sprintf("Fixation records with variables: %d\n", nrow(fixation_data)))
cat(sprintf("Interest area records with variables: %d\n", nrow(interest_area_data)))
cat(sprintf("Saccade records with variables: %d\n", nrow(saccade_data)))
cat(sprintf("Trial fixation summaries: %d\n", nrow(trial_fixation_summary)))
cat(sprintf("Trial summaries: %d\n", nrow(trial_summary)))
cat(sprintf("Trial saccade summaries: %d\n", nrow(trial_saccade_summary)))
cat("\nVariable creation complete!\n")

