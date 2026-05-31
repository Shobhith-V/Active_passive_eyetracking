# GAMM model templates for language, sentence type, cognitive load, and agent-first analyses.
# Run after: python analysis/prepare_analysis_data.py

library(mgcv)

trial_data <- read.csv("analysis/derived/sentence_audio_baseline_adjusted.csv")
ia_data <- read.csv("analysis/derived/interest_area_agent_first_dataset.csv")

trial_data$participant_id <- factor(trial_data$participant_id)
trial_data$image_id <- factor(trial_data$image_id)
trial_data$language <- relevel(factor(trial_data$language), ref = "English")
trial_data$sentence_type <- relevel(factor(trial_data$sentence_type), ref = "active")
trial_data$agent_first_alignment <- relevel(factor(trial_data$agent_first_alignment), ref = "agent_first")
trial_data$agent_overt <- relevel(factor(trial_data$agent_overt), ref = "agent_overt")

# Primary sentence-type model: tests English/Punjabi, sentence type, and interaction.
m_fix_mean <- bam(
  delta_fixation_mean_fixation_duration ~ language * sentence_type +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = trial_data,
  method = "fREML"
)
summary(m_fix_mean)
gam.check(m_fix_mean)
concurvity(m_fix_mean, full = TRUE)

# Primary cognitive-load model.
m_load <- bam(
  cognitive_load_index ~ language * sentence_type +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = trial_data,
  method = "fREML"
)
summary(m_load)
gam.check(m_load)

# Agent-first formulation: active is agent_first, passives are non_agent_first.
m_agent_first <- bam(
  cognitive_load_index ~ language * agent_first_alignment +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = trial_data,
  method = "fREML"
)
summary(m_agent_first)

# Overt-agent formulation: passive vs passive dropped-agent among non-active sentences.
passive_only <- subset(trial_data, sentence_type %in% c("passive", "passive_dropped_agent"))
passive_only$agent_overt <- relevel(factor(passive_only$agent_overt), ref = "agent_overt")
passive_only$language <- relevel(factor(passive_only$language), ref = "English")

m_agent_overt <- bam(
  cognitive_load_index ~ language * agent_overt +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = passive_only,
  method = "fREML"
)
summary(m_agent_overt)

# Outcome-specific cognitive-load indicators.
m_total_fix <- bam(
  delta_fixation_total_fixation_duration ~ language * sentence_type +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = trial_data,
  method = "fREML"
)
summary(m_total_fix)

m_dwell <- bam(
  delta_interest_area_total_interest_area_dwell_time ~ language * sentence_type +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = trial_data,
  method = "fREML"
)
summary(m_dwell)

m_saccade_rate <- bam(
  delta_saccade_saccade_rate ~ language * sentence_type +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = trial_data,
  method = "fREML"
)
summary(m_saccade_rate)

m_saccade_amp <- bam(
  delta_saccade_mean_saccade_amplitude ~ language * sentence_type +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = trial_data,
  method = "fREML"
)
summary(m_saccade_amp)

# Optional nonlinear trial-order control, if trial_id is numeric enough to be meaningful.
trial_data$trial_number <- suppressWarnings(as.numeric(trial_data$trial_id))
m_load_trial_order <- bam(
  cognitive_load_index ~ language * sentence_type +
    s(trial_number, by = interaction(language, sentence_type), k = 8) +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = trial_data,
  method = "fREML"
)
summary(m_load_trial_order)

# Interest-area model. Strongest after analysis/aoi_role_lookup_template.csv is filled.
if ("aoi_role" %in% names(ia_data) && any(!is.na(ia_data$aoi_role))) {
  ia_sentence <- subset(ia_data, session_type == "sentence_audio")
  ia_sentence$participant_id <- factor(ia_sentence$participant_id)
  ia_sentence$image_id <- factor(ia_sentence$image_id)
  ia_sentence$ia_label <- factor(ia_sentence$ia_label)
  ia_sentence$language <- relevel(factor(ia_sentence$language), ref = "English")
  ia_sentence$sentence_type <- relevel(factor(ia_sentence$sentence_type), ref = "active")
  ia_sentence$aoi_role <- factor(ia_sentence$aoi_role)

  m_ia_dwell <- bam(
    dwell_time_normalized_by_trial_length ~ language * sentence_type * aoi_role +
      s(participant_id, bs = "re") +
      s(image_id, bs = "re") +
      s(ia_label, bs = "re"),
    data = ia_sentence,
    method = "fREML"
  )
  summary(m_ia_dwell)

  m_ia_tff <- bam(
    time_to_first_fixation ~ language * sentence_type * aoi_role +
      s(participant_id, bs = "re") +
      s(image_id, bs = "re") +
      s(ia_label, bs = "re"),
    data = ia_sentence,
    method = "fREML"
  )
  summary(m_ia_tff)
}
