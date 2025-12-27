# %% Visualizations
# Script: 06_visualizations.R
# Purpose: Create comprehensive visualizations of gaze patterns

# Load required libraries
library(dplyr)
library(ggplot2)
library(tidyr)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Create output directory
dir.create("plots/exploratory", showWarnings = FALSE, recursive = TRUE)

# Load data
cat("Loading data...\n")
merged_fixation_data <- read.csv("data/processed/merged_fixation_data_with_flags.csv", stringsAsFactors = FALSE)
merged_interest_area_data <- read.csv("data/processed/merged_interest_area_data.csv", stringsAsFactors = FALSE)
merged_saccade_data <- read.csv("data/processed/merged_saccade_data_with_flags.csv", stringsAsFactors = FALSE)
merged_trial_data <- read.csv("data/processed/merged_trial_data_with_flags.csv", stringsAsFactors = FALSE)

# Filter excluded data
fixation_clean <- merged_fixation_data %>% filter(!exclude_fixation)
saccade_clean <- merged_saccade_data %>% filter(!exclude_saccade)

# Add voice_type if missing
if (!"voice_type" %in% names(fixation_clean)) {
  fixation_clean$voice_type <- "unknown"
  saccade_clean$voice_type <- "unknown"
}

# %% Boxplots: Fixation duration by voice type and AOI
cat("Creating boxplots...\n")

p_boxplot <- ggplot(fixation_clean %>% filter(!is.na(aoi_type) & aoi_type != "other"),
                    aes(x = voice_type, y = CURRENT_FIX_DURATION, fill = aoi_type)) +
  geom_boxplot(position = position_dodge(width = 0.8), outlier.alpha = 0.3) +
  labs(title = "Fixation Duration by Voice Type and AOI",
       x = "Voice Type",
       y = "Fixation Duration (ms)",
       fill = "AOI Type") +
  theme_minimal(base_size = 12) +
  theme(legend.position = "right")

ggsave("plots/exploratory/boxplot_fixation_duration_voice_aoi.png", p_boxplot, width = 10, height = 6, dpi = 300)

# %% Heatmaps: Gaze patterns by voice type
cat("Creating heatmaps...\n")

# Create aggregated fixation positions
fixation_positions <- fixation_clean %>%
  filter(!is.na(CURRENT_FIX_X) & !is.na(CURRENT_FIX_Y)) %>%
  mutate(
    x_bin = cut(CURRENT_FIX_X, breaks = 20, labels = FALSE),
    y_bin = cut(CURRENT_FIX_Y, breaks = 20, labels = FALSE)
  ) %>%
  group_by(voice_type, x_bin, y_bin) %>%
  summarise(
    fixation_count = n(),
    .groups = "drop"
  )

p_heatmap <- ggplot(fixation_positions, aes(x = x_bin, y = y_bin, fill = fixation_count)) +
  geom_tile() +
  facet_wrap(~ voice_type) +
  scale_fill_gradient(low = "white", high = "darkblue") +
  labs(title = "Gaze Pattern Heatmaps by Voice Type",
       x = "X Position (binned)",
       y = "Y Position (binned)",
       fill = "Fixation\nCount") +
  theme_minimal()

ggsave("plots/exploratory/heatmap_gaze_patterns_voice.png", p_heatmap, width = 12, height = 8, dpi = 300)

# %% Time series: Fixation patterns over trial duration
cat("Creating time series plots...\n")

# Create time bins
fixation_time_series <- fixation_clean %>%
  filter(!is.na(time_from_trial_start) & !is.na(aoi_type)) %>%
  mutate(
    time_bin = cut(time_from_trial_start, breaks = 20, labels = FALSE)
  ) %>%
  group_by(voice_type, aoi_type, time_bin) %>%
  summarise(
    mean_fixation_duration = mean(CURRENT_FIX_DURATION, na.rm = TRUE),
    fixation_count = n(),
    .groups = "drop"
  )

p_timeseries <- ggplot(fixation_time_series %>% filter(aoi_type %in% c("subject", "object")),
                       aes(x = time_bin, y = mean_fixation_duration, color = aoi_type)) +
  geom_line(size = 1) +
  facet_wrap(~ voice_type) +
  labs(title = "Fixation Duration Over Trial Time by Voice Type",
       x = "Time Bin",
       y = "Mean Fixation Duration (ms)",
       color = "AOI Type") +
  theme_minimal()

ggsave("plots/exploratory/timeseries_fixation_duration.png", p_timeseries, width = 12, height = 6, dpi = 300)

# %% Saccade direction/amplitude distributions
cat("Creating saccade visualizations...\n")

p_saccade_amplitude <- ggplot(saccade_clean, aes(x = voice_type, y = CURRENT_SAC_AMPLITUDE, fill = voice_type)) +
  geom_violin(alpha = 0.6) +
  geom_boxplot(width = 0.2, fill = "white", alpha = 0.8) +
  labs(title = "Saccade Amplitude Distribution by Voice Type",
       x = "Voice Type",
       y = "Saccade Amplitude (degrees)") +
  theme_minimal() +
  theme(legend.position = "none")

ggsave("plots/exploratory/saccade_amplitude_by_voice.png", p_saccade_amplitude, width = 8, height = 6, dpi = 300)

# Saccade direction distribution
if ("CURRENT_SAC_DIRECTION" %in% names(saccade_clean)) {
  p_saccade_direction <- ggplot(saccade_clean %>% filter(!is.na(CURRENT_SAC_DIRECTION)),
                                aes(x = CURRENT_SAC_DIRECTION, fill = voice_type)) +
    geom_bar(position = "dodge") +
    labs(title = "Saccade Direction Distribution by Voice Type",
         x = "Saccade Direction",
         y = "Count",
         fill = "Voice Type") +
    theme_minimal()
  
  ggsave("plots/exploratory/saccade_direction_by_voice.png", p_saccade_direction, width = 10, height = 6, dpi = 300)
}

# %% AOI transition patterns
cat("Creating transition pattern visualizations...\n")

if ("saccade_transition" %in% names(saccade_clean)) {
  transition_summary <- saccade_clean %>%
    filter(!is.na(saccade_transition) & saccade_transition != "other") %>%
    group_by(voice_type, saccade_transition) %>%
    summarise(
      count = n(),
      mean_amplitude = mean(CURRENT_SAC_AMPLITUDE, na.rm = TRUE),
      .groups = "drop"
    )
  
  p_transitions <- ggplot(transition_summary, aes(x = saccade_transition, y = count, fill = voice_type)) +
    geom_bar(stat = "identity", position = "dodge") +
    labs(title = "Saccade Transition Patterns by Voice Type",
         x = "Transition Type",
         y = "Count",
         fill = "Voice Type") +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
  
  ggsave("plots/exploratory/saccade_transitions_by_voice.png", p_transitions, width = 10, height = 6, dpi = 300)
}

cat("\nVisualizations complete! Plots saved to plots/exploratory/\n")

