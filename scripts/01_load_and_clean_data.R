# %% Data Loading and Initial Cleaning
# Script: 01_load_and_clean_data.R
# Purpose: Load all Excel files from three report types, extract participant IDs,
#          select relevant variables, and perform initial cleaning

# Load required libraries
library(readxl)
library(dplyr)
library(tidyr)
library(stringr)

# Clear workspace
rm(list = ls())

# Set working directory to project root
if (!dir.exists("scripts")) {
  setwd("..")
}

# Create output directories
dir.create("data/processed", showWarnings = FALSE, recursive = TRUE)

# %% Define file paths
fixation_dir <- "reports/fixation"
interest_area_dir <- "reports/interest_area"
saccade_dir <- "reports/saccade_reports"

# %% Function to extract participant ID from filename
extract_participant_id <- function(filename) {
  # Pattern: edf##_YYYY_MM_DD_HH_MM.xls or P##_YYYY_MM_DD_HH_MM.xls
  pattern <- "(edf\\d+|P\\d+)_\\d{4}_\\d{2}_\\d{2}_\\d{2}_\\d{2}\\.xls"
  match <- str_extract(filename, pattern)
  if (!is.na(match)) {
    # Extract the participant ID part (edf## or P##)
    participant_id <- str_extract(match, "(edf\\d+|P\\d+)")
    return(participant_id)
  }
  return(NA)
}

# %% Load Fixation Reports
cat("Loading fixation reports...\n")
fixation_files <- list.files(fixation_dir, pattern = "\\.xls$", full.names = TRUE)
cat(sprintf("Found %d fixation files\n", length(fixation_files)))

fixation_data_list <- list()

for (i in seq_along(fixation_files)) {
  file_path <- fixation_files[i]
  filename <- basename(file_path)
  participant_id <- extract_participant_id(filename)
  
  if (is.na(participant_id)) {
    cat(sprintf("Warning: Could not extract participant ID from %s\n", filename))
    next
  }
  
  tryCatch({
    # Read Excel file
    df <- read_excel(file_path, col_types = "text")
    
    # Add participant ID and filename
    df$participant_id <- participant_id
    df$data_file <- filename
    
    # Select relevant variables from fixation reports
    relevant_vars <- c(
      # Participant and trial identifiers
      "participant_id", "data_file", "TRIAL_INDEX", "TRIAL_LABEL", "TRIAL_START_TIME",
      # Fixation metrics
      "CURRENT_FIX_DURATION", "CURRENT_FIX_INDEX", "CURRENT_FIX_START", "CURRENT_FIX_END",
      "CURRENT_FIX_X", "CURRENT_FIX_Y",
      # Interest area information
      "CURRENT_FIX_INTEREST_AREA_LABEL", "CURRENT_FIX_INTEREST_AREA_ID",
      "CURRENT_FIX_INTEREST_AREA_INDEX", "CURRENT_FIX_INTEREST_AREA_DWELL_TIME",
      "CURRENT_FIX_INTEREST_AREA_FIX_COUNT",
      # Trial-level information
      "TRIAL_FIXATION_TOTAL", "sentence", "voice_id", "image_id", "stim_id",
      "image", "stimulus_file", "session_var", "exp_id", "language", "audio"
    )
    
    # Select only variables that exist in the dataframe
    vars_to_select <- intersect(relevant_vars, names(df))
    df_selected <- df %>% select(all_of(vars_to_select))
    
    # Convert numeric columns
    numeric_cols <- c("CURRENT_FIX_DURATION", "CURRENT_FIX_INDEX", "CURRENT_FIX_START",
                     "CURRENT_FIX_END", "CURRENT_FIX_X", "CURRENT_FIX_Y",
                     "TRIAL_INDEX", "TRIAL_START_TIME", "TRIAL_FIXATION_TOTAL",
                     "CURRENT_FIX_INTEREST_AREA_ID", "CURRENT_FIX_INTEREST_AREA_INDEX",
                     "CURRENT_FIX_INTEREST_AREA_DWELL_TIME", "CURRENT_FIX_INTEREST_AREA_FIX_COUNT")
    
    for (col in numeric_cols) {
      if (col %in% names(df_selected)) {
        df_selected[[col]] <- as.numeric(df_selected[[col]])
      }
    }
    
    fixation_data_list[[i]] <- df_selected
    
    if (i %% 10 == 0) {
      cat(sprintf("Processed %d/%d fixation files\n", i, length(fixation_files)))
    }
  }, error = function(e) {
    cat(sprintf("Error reading %s: %s\n", filename, e$message))
  })
}

# Combine all fixation data
fixation_data <- bind_rows(fixation_data_list)
cat(sprintf("Total fixation records: %d\n", nrow(fixation_data)))

# Save cleaned fixation data
write.csv(fixation_data, "data/processed/fixation_cleaned.csv", row.names = FALSE)
cat("Saved fixation data to data/processed/fixation_cleaned.csv\n")

# %% Load Interest Area Reports
cat("\nLoading interest area reports...\n")
interest_area_files <- list.files(interest_area_dir, pattern = "\\.xls$", full.names = TRUE)
cat(sprintf("Found %d interest area files\n", length(interest_area_files)))

interest_area_data_list <- list()

for (i in seq_along(interest_area_files)) {
  file_path <- interest_area_files[i]
  filename <- basename(file_path)
  participant_id <- extract_participant_id(filename)
  
  if (is.na(participant_id)) {
    cat(sprintf("Warning: Could not extract participant ID from %s\n", filename))
    next
  }
  
  tryCatch({
    df <- read_excel(file_path, col_types = "text")
    
    df$participant_id <- participant_id
    df$data_file <- filename
    
    # Select relevant variables from interest area reports
    relevant_vars <- c(
      # Participant and trial identifiers
      "participant_id", "data_file", "TRIAL_INDEX", "TRIAL_LABEL", "TRIAL_START_TIME",
      # Interest area metrics
      "IA_LABEL", "IA_DWELL_TIME", "IA_FIXATION_COUNT", "IA_FIRST_FIXATION_TIME",
      "IA_FIRST_FIXATION_DURATION", "IA_FIRST_FIXATION_INDEX",
      "IA_AREA", "IA_LEFT", "IA_RIGHT", "IA_TOP", "IA_BOTTOM",
      # Trial-level information
      "TRIAL_DWELL_TIME", "TRIAL_FIXATION_COUNT", "TRIAL_IA_COUNT",
      "sentence", "voice_id", "image_id", "stim_id", "image", "stimulus_file",
      "session_var", "exp_id", "language", "audio"
    )
    
    vars_to_select <- intersect(relevant_vars, names(df))
    df_selected <- df %>% select(all_of(vars_to_select))
    
    # Convert numeric columns
    numeric_cols <- c("TRIAL_INDEX", "TRIAL_START_TIME", "IA_DWELL_TIME", "IA_FIXATION_COUNT",
                     "IA_FIRST_FIXATION_TIME", "IA_FIRST_FIXATION_DURATION",
                     "IA_FIRST_FIXATION_INDEX", "IA_AREA", "IA_LEFT", "IA_RIGHT",
                     "IA_TOP", "IA_BOTTOM", "TRIAL_DWELL_TIME", "TRIAL_FIXATION_COUNT",
                     "TRIAL_IA_COUNT")
    
    for (col in numeric_cols) {
      if (col %in% names(df_selected)) {
        df_selected[[col]] <- as.numeric(df_selected[[col]])
      }
    }
    
    interest_area_data_list[[i]] <- df_selected
    
    if (i %% 10 == 0) {
      cat(sprintf("Processed %d/%d interest area files\n", i, length(interest_area_files)))
    }
  }, error = function(e) {
    cat(sprintf("Error reading %s: %s\n", filename, e$message))
  })
}

# Combine all interest area data
interest_area_data <- bind_rows(interest_area_data_list)
cat(sprintf("Total interest area records: %d\n", nrow(interest_area_data)))

# Save cleaned interest area data
write.csv(interest_area_data, "data/processed/interest_area_cleaned.csv", row.names = FALSE)
cat("Saved interest area data to data/processed/interest_area_cleaned.csv\n")

# %% Load Saccade Reports
cat("\nLoading saccade reports...\n")
saccade_files <- list.files(saccade_dir, pattern = "\\.xls$", full.names = TRUE)
cat(sprintf("Found %d saccade files\n", length(saccade_files)))

saccade_data_list <- list()

for (i in seq_along(saccade_files)) {
  file_path <- saccade_files[i]
  filename <- basename(file_path)
  participant_id <- extract_participant_id(filename)
  
  if (is.na(participant_id)) {
    cat(sprintf("Warning: Could not extract participant ID from %s\n", filename))
    next
  }
  
  tryCatch({
    df <- read_excel(file_path, col_types = "text")
    
    df$participant_id <- participant_id
    df$data_file <- filename
    
    # Select relevant variables from saccade reports
    relevant_vars <- c(
      # Participant and trial identifiers
      "participant_id", "data_file", "TRIAL_INDEX", "TRIAL_LABEL", "TRIAL_START_TIME",
      # Saccade metrics
      "CURRENT_SAC_DURATION", "CURRENT_SAC_AMPLITUDE", "CURRENT_SAC_AVG_VELOCITY",
      "CURRENT_SAC_PEAK_VELOCITY", "CURRENT_SAC_INDEX", "CURRENT_SAC_START_TIME",
      "CURRENT_SAC_END_TIME", "CURRENT_SAC_DIRECTION", "CURRENT_SAC_ANGLE",
      # Start and end positions
      "CURRENT_SAC_START_X", "CURRENT_SAC_START_Y", "CURRENT_SAC_END_X", "CURRENT_SAC_END_Y",
      # Interest area information
      "CURRENT_SAC_START_INTEREST_AREA_LABEL", "CURRENT_SAC_END_INTEREST_AREA_LABEL",
      "CURRENT_SAC_START_INTEREST_AREA_ID", "CURRENT_SAC_END_INTEREST_AREA_ID",
      # Trial-level information
      "sentence", "voice_id", "image_id", "stim_id", "image", "stimulus_file",
      "session_var", "exp_id", "language", "audio"
    )
    
    vars_to_select <- intersect(relevant_vars, names(df))
    df_selected <- df %>% select(all_of(vars_to_select))
    
    # Convert numeric columns
    numeric_cols <- c("TRIAL_INDEX", "TRIAL_START_TIME", "CURRENT_SAC_DURATION",
                     "CURRENT_SAC_AMPLITUDE", "CURRENT_SAC_AVG_VELOCITY", "CURRENT_SAC_PEAK_VELOCITY",
                     "CURRENT_SAC_INDEX", "CURRENT_SAC_START_TIME", "CURRENT_SAC_END_TIME",
                     "CURRENT_SAC_ANGLE", "CURRENT_SAC_START_X", "CURRENT_SAC_START_Y",
                     "CURRENT_SAC_END_X", "CURRENT_SAC_END_Y", "CURRENT_SAC_START_INTEREST_AREA_ID",
                     "CURRENT_SAC_END_INTEREST_AREA_ID")
    
    for (col in numeric_cols) {
      if (col %in% names(df_selected)) {
        df_selected[[col]] <- as.numeric(df_selected[[col]])
      }
    }
    
    saccade_data_list[[i]] <- df_selected
    
    if (i %% 10 == 0) {
      cat(sprintf("Processed %d/%d saccade files\n", i, length(saccade_files)))
    }
  }, error = function(e) {
    cat(sprintf("Error reading %s: %s\n", filename, e$message))
  })
}

# Combine all saccade data
saccade_data <- bind_rows(saccade_data_list)
cat(sprintf("Total saccade records: %d\n", nrow(saccade_data)))

# Save cleaned saccade data
write.csv(saccade_data, "data/processed/saccade_cleaned.csv", row.names = FALSE)
cat("Saved saccade data to data/processed/saccade_cleaned.csv\n")

# %% Create participant metadata summary
participant_metadata <- data.frame(
  participant_id = unique(c(
    unique(fixation_data$participant_id),
    unique(interest_area_data$participant_id),
    unique(saccade_data$participant_id)
  )),
  stringsAsFactors = FALSE
) %>%
  mutate(
    n_fixation_files = sapply(participant_id, function(id) {
      sum(fixation_data$participant_id == id, na.rm = TRUE) > 0
    }),
    n_interest_area_files = sapply(participant_id, function(id) {
      sum(interest_area_data$participant_id == id, na.rm = TRUE) > 0
    }),
    n_saccade_files = sapply(participant_id, function(id) {
      sum(saccade_data$participant_id == id, na.rm = TRUE) > 0
    })
  )

write.csv(participant_metadata, "data/processed/participant_metadata.csv", row.names = FALSE)
cat("\nSaved participant metadata to data/processed/participant_metadata.csv\n")

# %% Summary statistics
cat("\n=== Data Loading Summary ===\n")
cat(sprintf("Participants: %d\n", nrow(participant_metadata)))
cat(sprintf("Fixation records: %d\n", nrow(fixation_data)))
cat(sprintf("Interest area records: %d\n", nrow(interest_area_data)))
cat(sprintf("Saccade records: %d\n", nrow(saccade_data)))
cat("\nData loading complete!\n")



