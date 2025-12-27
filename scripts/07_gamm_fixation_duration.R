# %% GAMM Model: Fixation Duration
# Script: 07_gamm_fixation_duration.R
# Purpose: Model fixation duration with voice type, AOI, and interactions

# Load required libraries
library(mgcv)
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
dir.create("models/fixation_duration_models", showWarnings = FALSE, recursive = TRUE)
dir.create("plots/model_diagnostics", showWarnings = FALSE, recursive = TRUE)
dir.create("results/model_summaries", showWarnings = FALSE, recursive = TRUE)

# Load data
cat("Loading data...\n")
fixation_data <- read.csv("data/processed/merged_fixation_data_with_flags.csv", stringsAsFactors = FALSE)

# Filter excluded data
fixation_clean <- fixation_data %>% filter(!exclude_fixation)

# Remove rows with missing critical variables
fixation_clean <- fixation_clean %>%
  filter(
    !is.na(CURRENT_FIX_DURATION) &
    !is.na(participant_id) &
    !is.na(TRIAL_INDEX) &
    !is.na(aoi_type) &
    aoi_type != "other"
  )

# Add voice_type if missing (extract from voice_id or set default)
if (!"voice_type" %in% names(fixation_clean)) {
  # Placeholder - adjust based on actual data structure
  fixation_clean$voice_type <- ifelse(is.na(fixation_clean$voice_id) | 
                                       fixation_clean$voice_id == "UNDEFINEDnull",
                                       "unknown", fixation_clean$voice_id)
}

# Convert to factors
fixation_clean$voice_type <- as.factor(fixation_clean$voice_type)
fixation_clean$aoi_type <- as.factor(fixation_clean$aoi_type)
fixation_clean$participant_id <- as.factor(fixation_clean$participant_id)
fixation_clean$trial_id <- as.factor(fixation_clean$trial_id)

# Set reference levels
fixation_clean$voice_type <- relevel(fixation_clean$voice_type, ref = levels(fixation_clean$voice_type)[1])
fixation_clean$aoi_type <- relevel(fixation_clean$aoi_type, ref = "subject")

# Create trial time variable (normalized 0-1)
fixation_clean <- fixation_clean %>%
  group_by(trial_id) %>%
  mutate(
    trial_time_norm = (time_from_trial_start - min(time_from_trial_start, na.rm = TRUE)) /
                      (max(time_from_trial_start, na.rm = TRUE) - min(time_from_trial_start, na.rm = TRUE))
  ) %>%
  ungroup()

# Log transform fixation duration (common for duration data)
fixation_clean$log_fixation_duration <- log(fixation_clean$CURRENT_FIX_DURATION + 1)

cat(sprintf("Data prepared: %d fixation records\n", nrow(fixation_clean)))
cat(sprintf("Participants: %d\n", n_distinct(fixation_clean$participant_id)))
cat(sprintf("Trials: %d\n", n_distinct(fixation_clean$trial_id)))

# %% Model 1: Basic model with voice type and AOI
cat("\nFitting Model 1: Basic model...\n")

model1 <- bam(
  log_fixation_duration ~ 
    voice_type + 
    aoi_type + 
    voice_type:aoi_type +
    s(participant_id, bs = "re") +
    s(trial_id, bs = "re"),
  data = fixation_clean,
  method = "fREML"
)

saveRDS(model1, "models/fixation_duration_models/model1_basic.rds")
cat("Model 1 saved\n")

# Model summary
summary1 <- summary(model1)
capture.output(summary1, file = "results/model_summaries/fixation_duration_model1_summary.txt")

# %% Model 2: Add temporal smooth
cat("\nFitting Model 2: With temporal smooth...\n")

model2 <- bam(
  log_fixation_duration ~ 
    voice_type + 
    aoi_type + 
    voice_type:aoi_type +
    s(trial_time_norm, by = voice_type, k = 5) +
    s(participant_id, bs = "re") +
    s(trial_id, bs = "re"),
  data = fixation_clean,
  method = "fREML"
)

saveRDS(model2, "models/fixation_duration_models/model2_temporal.rds")
cat("Model 2 saved\n")

summary2 <- summary(model2)
capture.output(summary2, file = "results/model_summaries/fixation_duration_model2_summary.txt")

# %% Model 3: Add interaction smooth
cat("\nFitting Model 3: With interaction smooth...\n")

model3 <- bam(
  log_fixation_duration ~ 
    voice_type + 
    aoi_type + 
    voice_type:aoi_type +
    s(trial_time_norm, by = interaction(voice_type, aoi_type), k = 5) +
    s(participant_id, bs = "re") +
    s(trial_id, bs = "re"),
  data = fixation_clean,
  method = "fREML"
)

saveRDS(model3, "models/fixation_duration_models/model3_interaction_smooth.rds")
cat("Model 3 saved\n")

summary3 <- summary(model3)
capture.output(summary3, file = "results/model_summaries/fixation_duration_model3_summary.txt")

# %% Model comparison
cat("\nComparing models...\n")

model_comparison <- data.frame(
  Model = c("Model 1: Basic", "Model 2: Temporal", "Model 3: Interaction Smooth"),
  AIC = c(AIC(model1), AIC(model2), AIC(model3)),
  BIC = c(BIC(model1), BIC(model2), BIC(model3)),
  LogLik = c(logLik(model1), logLik(model2), logLik(model3)),
  Deviance_Explained = c(summary1$dev.expl * 100, 
                         summary2$dev.expl * 100, 
                         summary3$dev.expl * 100),
  R_sq = c(summary1$r.sq, summary2$r.sq, summary3$r.sq)
)

write.csv(model_comparison, "results/model_summaries/fixation_duration_model_comparison.csv", row.names = FALSE)

# %% Model diagnostics
cat("\nCreating model diagnostics...\n")

# Diagnostics for best model (Model 3)
png("plots/model_diagnostics/fixation_duration_model3_diagnostics.png", width = 1200, height = 800)
par(mfrow = c(2, 2))
gam.check(model3)
dev.off()

# Smooth plots
if (length(model3$smooth) > 0) {
  png("plots/model_diagnostics/fixation_duration_model3_smooths.png", width = 1200, height = 800)
  plot(model3, pages = 1, se = TRUE, shade = TRUE)
  dev.off()
}

# %% Extract key comparisons
cat("\nExtracting key comparisons...\n")

# Create comparison data frame
comparisons <- data.frame(
  comparison = c(
    "Active vs Passive (Overall)",
    "Subject AOI: Active vs Passive",
    "Object AOI: Active vs Passive"
  ),
  estimate = NA,
  se = NA,
  p_value = NA
)

# Extract coefficients for main effects
coef_summary <- summary(model3)$p.table
if ("voice_type" %in% rownames(coef_summary)) {
  # This is a simplified extraction - adjust based on actual model structure
  comparisons$estimate[1] <- coef_summary["voice_type", "Estimate"]
  comparisons$se[1] <- coef_summary["voice_type", "Std. Error"]
  comparisons$p_value[1] <- coef_summary["voice_type", "Pr(>|t|)"]
}

write.csv(comparisons, "results/model_summaries/fixation_duration_comparisons.csv", row.names = FALSE)

cat("\n=== Fixation Duration Modeling Complete ===\n")
cat("Models saved to models/fixation_duration_models/\n")
cat("Diagnostics saved to plots/model_diagnostics/\n")
cat("Summaries saved to results/model_summaries/\n")

