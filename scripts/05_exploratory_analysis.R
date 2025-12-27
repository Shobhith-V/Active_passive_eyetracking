# %% Exploratory Data Analysis
# Script: 05_exploratory_analysis.R
# Purpose: Summary statistics and initial data exploration

# Load required libraries
library(dplyr)
library(tidyr)
library(ggplot2)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Create output directories
dir.create("plots/exploratory", showWarnings = FALSE, recursive = TRUE)
dir.create("results/exploratory", showWarnings = FALSE, recursive = TRUE)

# Load data with exclusion flags
cat("Loading data...\n")
merged_fixation_data <- read.csv("data/processed/merged_fixation_data_with_flags.csv", stringsAsFactors = FALSE)
merged_interest_area_data <- read.csv("data/processed/merged_interest_area_data.csv", stringsAsFactors = FALSE)
merged_saccade_data <- read.csv("data/processed/merged_saccade_data_with_flags.csv", stringsAsFactors = FALSE)
merged_trial_data <- read.csv("data/processed/merged_trial_data_with_flags.csv", stringsAsFactors = FALSE)

# Filter out excluded data
fixation_clean <- merged_fixation_data %>% filter(!exclude_fixation)
saccade_clean <- merged_saccade_data %>% filter(!exclude_saccade)
trial_clean <- merged_trial_data %>% filter(!exclude_trial)

# %% Summary Statistics by Voice Type
cat("Calculating summary statistics by voice type...\n")

# Note: voice_type may need to be extracted from voice_id or other variables
# For now, we'll use voice_id as a proxy if voice_type doesn't exist
if (!"voice_type" %in% names(trial_clean)) {
  # Create a placeholder - this should be adjusted based on actual data
  trial_clean$voice_type <- "unknown"
  fixation_clean$voice_type <- "unknown"
  saccade_clean$voice_type <- "unknown"
}

# Fixation duration summary by voice type and AOI
fixation_summary <- fixation_clean %>%
  group_by(voice_type, aoi_type) %>%
  summarise(
    n = n(),
    mean_duration = mean(CURRENT_FIX_DURATION, na.rm = TRUE),
    median_duration = median(CURRENT_FIX_DURATION, na.rm = TRUE),
    sd_duration = sd(CURRENT_FIX_DURATION, na.rm = TRUE),
    min_duration = min(CURRENT_FIX_DURATION, na.rm = TRUE),
    max_duration = max(CURRENT_FIX_DURATION, na.rm = TRUE),
    .groups = "drop"
  )

write.csv(fixation_summary, "results/exploratory/fixation_summary_by_voice_aoi.csv", row.names = FALSE)

# Dwell time summary by voice type and AOI
dwell_time_summary <- merged_interest_area_data %>%
  filter(IA_LABEL != "" & !is.na(IA_LABEL)) %>%
  group_by(voice_id, aoi_type) %>%
  summarise(
    n = n(),
    mean_dwell_time = mean(IA_DWELL_TIME, na.rm = TRUE),
    median_dwell_time = median(IA_DWELL_TIME, na.rm = TRUE),
    sd_dwell_time = sd(IA_DWELL_TIME, na.rm = TRUE),
    .groups = "drop"
  )

write.csv(dwell_time_summary, "results/exploratory/dwell_time_summary_by_voice_aoi.csv", row.names = FALSE)

# Saccade summary by voice type
saccade_summary <- saccade_clean %>%
  group_by(voice_type) %>%
  summarise(
    n = n(),
    mean_amplitude = mean(CURRENT_SAC_AMPLITUDE, na.rm = TRUE),
    mean_duration = mean(CURRENT_SAC_DURATION, na.rm = TRUE),
    mean_velocity = mean(CURRENT_SAC_AVG_VELOCITY, na.rm = TRUE),
    .groups = "drop"
  )

write.csv(saccade_summary, "results/exploratory/saccade_summary_by_voice.csv", row.names = FALSE)

# %% Distribution plots for key dependent variables
cat("Creating distribution plots...\n")

# Fixation duration distribution
p1 <- ggplot(fixation_clean, aes(x = CURRENT_FIX_DURATION)) +
  geom_histogram(bins = 50, fill = "skyblue", color = "black", alpha = 0.6) +
  labs(title = "Distribution of Fixation Duration",
       x = "Fixation Duration (ms)",
       y = "Frequency") +
  theme_minimal()

ggsave("plots/exploratory/fixation_duration_distribution.png", p1, width = 8, height = 5)

# Fixation duration by voice type and AOI
p2 <- ggplot(fixation_clean %>% filter(!is.na(aoi_type)), 
             aes(x = voice_type, y = CURRENT_FIX_DURATION, fill = aoi_type)) +
  geom_boxplot(position = position_dodge(width = 0.8)) +
  labs(title = "Fixation Duration by Voice Type and AOI",
       x = "Voice Type",
       y = "Fixation Duration (ms)",
       fill = "AOI Type") +
  theme_minimal()

ggsave("plots/exploratory/fixation_duration_by_voice_aoi.png", p2, width = 10, height = 6)

# Dwell time distribution
p3 <- ggplot(merged_interest_area_data %>% filter(!is.na(IA_DWELL_TIME)), 
             aes(x = IA_DWELL_TIME)) +
  geom_histogram(bins = 50, fill = "lightgreen", color = "black", alpha = 0.6) +
  labs(title = "Distribution of Dwell Time",
       x = "Dwell Time (ms)",
       y = "Frequency") +
  theme_minimal()

ggsave("plots/exploratory/dwell_time_distribution.png", p3, width = 8, height = 5)

# Saccade amplitude distribution
p4 <- ggplot(saccade_clean, aes(x = CURRENT_SAC_AMPLITUDE)) +
  geom_histogram(bins = 50, fill = "salmon", color = "black", alpha = 0.6) +
  labs(title = "Distribution of Saccade Amplitude",
       x = "Saccade Amplitude (degrees)",
       y = "Frequency") +
  theme_minimal()

ggsave("plots/exploratory/saccade_amplitude_distribution.png", p4, width = 8, height = 5)

# %% AOI-specific summaries
cat("Creating AOI-specific summaries...\n")

aoi_summary <- fixation_clean %>%
  filter(!is.na(aoi_type)) %>%
  group_by(voice_type, aoi_type) %>%
  summarise(
    total_fixations = n(),
    total_duration = sum(CURRENT_FIX_DURATION, na.rm = TRUE),
    mean_duration = mean(CURRENT_FIX_DURATION, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  group_by(voice_type) %>%
  mutate(
    pct_fixations = 100 * total_fixations / sum(total_fixations),
    pct_duration = 100 * total_duration / sum(total_duration)
  )

write.csv(aoi_summary, "results/exploratory/aoi_summary.csv", row.names = FALSE)

# %% Participant-level variability
cat("Calculating participant-level variability...\n")

participant_variability <- fixation_clean %>%
  group_by(participant_id, voice_type, aoi_type) %>%
  summarise(
    mean_fixation_duration = mean(CURRENT_FIX_DURATION, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  group_by(voice_type, aoi_type) %>%
  summarise(
    n_participants = n(),
    mean_across_participants = mean(mean_fixation_duration, na.rm = TRUE),
    sd_across_participants = sd(mean_fixation_duration, na.rm = TRUE),
    .groups = "drop"
  )

write.csv(participant_variability, "results/exploratory/participant_variability.csv", row.names = FALSE)

# %% Print summary
cat("\n=== Exploratory Analysis Summary ===\n")
cat("Summary statistics saved to results/exploratory/\n")
cat("Plots saved to plots/exploratory/\n")
cat("\nExploratory analysis complete!\n")

