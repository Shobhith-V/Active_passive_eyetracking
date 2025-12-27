# %% Data Quality Checks
# Script: 04_data_quality.R
# Purpose: Identify outliers, check missing data, validate consistency

# Load required libraries
library(dplyr)
library(ggplot2)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Create output directory for quality reports
dir.create("results/data_quality", showWarnings = FALSE, recursive = TRUE)

# Load merged data
cat("Loading merged data...\n")
merged_fixation_data <- read.csv("data/processed/merged_fixation_data.csv", stringsAsFactors = FALSE)
merged_interest_area_data <- read.csv("data/processed/merged_interest_area_data.csv", stringsAsFactors = FALSE)
merged_saccade_data <- read.csv("data/processed/merged_saccade_data.csv", stringsAsFactors = FALSE)
merged_trial_data <- read.csv("data/processed/merged_trial_data.csv", stringsAsFactors = FALSE)

# %% Check for missing critical variables
cat("Checking for missing critical variables...\n")

check_missing <- function(df, df_name) {
  cat(sprintf("\n=== Missing Data Check: %s ===\n", df_name))
  
  missing_summary <- df %>%
    summarise(across(everything(), ~ sum(is.na(.x) | .x == "" | .x == "."))) %>%
    pivot_longer(everything(), names_to = "variable", values_to = "missing_count") %>%
    mutate(
      missing_pct = round(100 * missing_count / nrow(df), 2),
      critical = variable %in% c("participant_id", "TRIAL_INDEX", "sentence", "voice_id",
                                 "CURRENT_FIX_DURATION", "IA_DWELL_TIME", "CURRENT_SAC_AMPLITUDE")
    ) %>%
    arrange(desc(missing_count))
  
  # Print critical variables with missing data
  critical_missing <- missing_summary %>%
    filter(critical & missing_count > 0)
  
  if (nrow(critical_missing) > 0) {
    cat("Critical variables with missing data:\n")
    print(critical_missing)
  } else {
    cat("No missing data in critical variables\n")
  }
  
  return(missing_summary)
}

fixation_missing <- check_missing(merged_fixation_data, "Fixation Data")
interest_area_missing <- check_missing(merged_interest_area_data, "Interest Area Data")
saccade_missing <- check_missing(merged_saccade_data, "Saccade Data")
trial_missing <- check_missing(merged_trial_data, "Trial Data")

# Save missing data reports
write.csv(fixation_missing, "results/data_quality/fixation_missing_data.csv", row.names = FALSE)
write.csv(interest_area_missing, "results/data_quality/interest_area_missing_data.csv", row.names = FALSE)
write.csv(saccade_missing, "results/data_quality/saccade_missing_data.csv", row.names = FALSE)
write.csv(trial_missing, "results/data_quality/trial_missing_data.csv", row.names = FALSE)

# %% Identify outliers in fixation duration
cat("\nIdentifying outliers in fixation duration...\n")

fixation_outliers <- merged_fixation_data %>%
  filter(!is.na(CURRENT_FIX_DURATION)) %>%
  mutate(
    # Standard outlier detection using IQR
    q1 = quantile(CURRENT_FIX_DURATION, 0.25, na.rm = TRUE),
    q3 = quantile(CURRENT_FIX_DURATION, 0.75, na.rm = TRUE),
    iqr = q3 - q1,
    lower_bound = q1 - 3 * iqr,  # Using 3*IQR for more conservative detection
    upper_bound = q3 + 3 * iqr,
    is_outlier = CURRENT_FIX_DURATION < lower_bound | CURRENT_FIX_DURATION > upper_bound
  ) %>%
  filter(is_outlier)

cat(sprintf("Fixation duration outliers: %d (%.2f%%)\n",
            nrow(fixation_outliers),
            100 * nrow(fixation_outliers) / nrow(merged_fixation_data)))

# Check for impossible values (negative durations, extremely long durations)
impossible_fixations <- merged_fixation_data %>%
  filter(
    CURRENT_FIX_DURATION < 0 | CURRENT_FIX_DURATION > 5000 |  # > 5 seconds is likely an error
    CURRENT_FIX_X < 0 | CURRENT_FIX_X > 2000 |  # Assuming reasonable screen bounds
    CURRENT_FIX_Y < 0 | CURRENT_FIX_Y > 2000
  )

cat(sprintf("Impossible fixation values: %d\n", nrow(impossible_fixations)))

# %% Identify outliers in saccade metrics
cat("\nIdentifying outliers in saccade metrics...\n")

saccade_outliers <- merged_saccade_data %>%
  filter(!is.na(CURRENT_SAC_AMPLITUDE)) %>%
  mutate(
    q1 = quantile(CURRENT_SAC_AMPLITUDE, 0.25, na.rm = TRUE),
    q3 = quantile(CURRENT_SAC_AMPLITUDE, 0.75, na.rm = TRUE),
    iqr = q3 - q1,
    lower_bound = q1 - 3 * iqr,
    upper_bound = q3 + 3 * iqr,
    is_outlier = CURRENT_SAC_AMPLITUDE < lower_bound | CURRENT_SAC_AMPLITUDE > upper_bound
  ) %>%
  filter(is_outlier)

cat(sprintf("Saccade amplitude outliers: %d (%.2f%%)\n",
            nrow(saccade_outliers),
            100 * nrow(saccade_outliers) / nrow(merged_saccade_data)))

# Check for impossible saccade values
impossible_saccades <- merged_saccade_data %>%
  filter(
    CURRENT_SAC_AMPLITUDE < 0 | CURRENT_SAC_AMPLITUDE > 2000 |  # > 20 degrees is extreme
    CURRENT_SAC_DURATION < 0 | CURRENT_SAC_DURATION > 500 |
    CURRENT_SAC_AVG_VELOCITY < 0 | CURRENT_SAC_AVG_VELOCITY > 1000
  )

cat(sprintf("Impossible saccade values: %d\n", nrow(impossible_saccades)))

# %% Validate voice type encoding consistency
cat("\nValidating voice type encoding...\n")

# Check if voice_id is consistent across datasets for same trials
voice_consistency <- merged_trial_data %>%
  group_by(participant_id, TRIAL_INDEX, sentence) %>%
  summarise(
    unique_voice_ids = n_distinct(voice_id, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  filter(unique_voice_ids > 1)

if (nrow(voice_consistency) > 0) {
  cat(sprintf("Warning: %d trials have inconsistent voice_id values\n", nrow(voice_consistency)))
} else {
  cat("Voice ID encoding is consistent\n")
}

# Check for missing voice_id
missing_voice <- merged_trial_data %>%
  filter(is.na(voice_id) | voice_id == "" | voice_id == "UNDEFINEDnull")

cat(sprintf("Trials with missing/invalid voice_id: %d\n", nrow(missing_voice)))

# %% Create data quality report
cat("\nCreating data quality report...\n")

quality_report <- data.frame(
  check = c(
    "Total fixation records",
    "Fixation duration outliers",
    "Impossible fixation values",
    "Total interest area records",
    "Total saccade records",
    "Saccade amplitude outliers",
    "Impossible saccade values",
    "Trials with inconsistent voice_id",
    "Trials with missing voice_id",
    "Total participants",
    "Total trials"
  ),
  count = c(
    nrow(merged_fixation_data),
    nrow(fixation_outliers),
    nrow(impossible_fixations),
    nrow(merged_interest_area_data),
    nrow(merged_saccade_data),
    nrow(saccade_outliers),
    nrow(impossible_saccades),
    nrow(voice_consistency),
    nrow(missing_voice),
    n_distinct(merged_trial_data$participant_id),
    nrow(merged_trial_data)
  ),
  percentage = c(
    100,
    round(100 * nrow(fixation_outliers) / nrow(merged_fixation_data), 2),
    round(100 * nrow(impossible_fixations) / nrow(merged_fixation_data), 2),
    100,
    100,
    round(100 * nrow(saccade_outliers) / nrow(merged_saccade_data), 2),
    round(100 * nrow(impossible_saccades) / nrow(merged_saccade_data), 2),
    round(100 * nrow(voice_consistency) / nrow(merged_trial_data), 2),
    round(100 * nrow(missing_voice) / nrow(merged_trial_data), 2),
    100,
    100
  )
)

write.csv(quality_report, "results/data_quality/data_quality_report.csv", row.names = FALSE)

# Save outlier records for review
write.csv(fixation_outliers, "results/data_quality/fixation_outliers.csv", row.names = FALSE)
write.csv(saccade_outliers, "results/data_quality/saccade_outliers.csv", row.names = FALSE)
write.csv(impossible_fixations, "results/data_quality/impossible_fixations.csv", row.names = FALSE)
write.csv(impossible_saccades, "results/data_quality/impossible_saccades.csv", row.names = FALSE)

# %% Create exclusion flags
cat("\nCreating exclusion flags...\n")

# Add exclusion flags to datasets
merged_fixation_data <- merged_fixation_data %>%
  mutate(
    exclude_fixation = CURRENT_FIX_DURATION < 0 | CURRENT_FIX_DURATION > 5000 |
                       CURRENT_FIX_X < 0 | CURRENT_FIX_X > 2000 |
                       CURRENT_FIX_Y < 0 | CURRENT_FIX_Y > 2000
  )

merged_saccade_data <- merged_saccade_data %>%
  mutate(
    exclude_saccade = CURRENT_SAC_AMPLITUDE < 0 | CURRENT_SAC_AMPLITUDE > 2000 |
                      CURRENT_SAC_DURATION < 0 | CURRENT_SAC_DURATION > 500 |
                      CURRENT_SAC_AVG_VELOCITY < 0 | CURRENT_SAC_AVG_VELOCITY > 1000
  )

merged_trial_data <- merged_trial_data %>%
  mutate(
    exclude_trial = is.na(voice_id) | voice_id == "" | voice_id == "UNDEFINEDnull"
  )

# Save datasets with exclusion flags
write.csv(merged_fixation_data, "data/processed/merged_fixation_data_with_flags.csv", row.names = FALSE)
write.csv(merged_saccade_data, "data/processed/merged_saccade_data_with_flags.csv", row.names = FALSE)
write.csv(merged_trial_data, "data/processed/merged_trial_data_with_flags.csv", row.names = FALSE)

# %% Print summary
cat("\n=== Data Quality Summary ===\n")
print(quality_report)
cat("\nData quality checks complete!\n")
cat("Reports saved to results/data_quality/\n")

