# Runnable GAMM analyses for sentence type, language, cognitive load, and agent-first hypotheses.
# Run from project root after:
#   python analysis/prepare_analysis_data.py
#   python analysis/run_exploratory_analysis.py

suppressPackageStartupMessages(library(mgcv))

out_dir <- "analysis/results/gamm"
plot_dir <- file.path(out_dir, "plots")
dir.create(out_dir, recursive = TRUE, showWarnings = FALSE)
dir.create(plot_dir, recursive = TRUE, showWarnings = FALSE)

trial_data <- read.csv("analysis/derived/sentence_audio_baseline_adjusted.csv")
ia_data <- read.csv("analysis/derived/interest_area_agent_first_dataset.csv")

trial_data$participant_id <- factor(trial_data$participant_id)
trial_data$image_id <- factor(trial_data$image_id)
trial_data$language <- relevel(factor(trial_data$language), ref = "English")
trial_data$sentence_type <- relevel(factor(trial_data$sentence_type), ref = "active")
trial_data$agent_first_alignment <- relevel(factor(trial_data$agent_first_alignment), ref = "agent_first")
trial_data$agent_overt <- relevel(factor(trial_data$agent_overt), ref = "agent_overt")
trial_data$trial_number <- suppressWarnings(as.numeric(trial_data$trial_id))
trial_data$language_sentence_type <- interaction(trial_data$language, trial_data$sentence_type, drop = TRUE)

ia_sentence <- subset(ia_data, session_type == "sentence_audio")
ia_sentence$participant_id <- factor(ia_sentence$participant_id)
ia_sentence$image_id <- factor(ia_sentence$image_id)
ia_sentence$ia_label <- factor(ia_sentence$ia_label)
ia_sentence$language <- relevel(factor(ia_sentence$language), ref = "English")
ia_sentence$sentence_type <- relevel(factor(ia_sentence$sentence_type), ref = "active")
ia_sentence$aoi_role <- relevel(factor(ia_sentence$aoi_role), ref = "agent")

trial_outcomes <- c(
  "delta_fixation_mean_fixation_duration",
  "delta_fixation_total_fixation_duration",
  "delta_fixation_fixation_count",
  "delta_interest_area_total_interest_area_dwell_time",
  "delta_interest_area_interest_area_dwell_time_normalized",
  "delta_saccade_saccade_rate",
  "delta_saccade_mean_saccade_amplitude",
  "delta_saccade_mean_saccade_velocity",
  "delta_saccade_mean_saccade_duration",
  "cognitive_load_index"
)

ia_outcomes <- c(
  "time_to_first_fixation",
  "dwell_time_normalized_by_trial_length",
  "dwell_time",
  "entry_count"
)

safe_name <- function(x) gsub("[^A-Za-z0-9_]+", "_", x)

write_model_outputs <- function(model, model_name, model_family, outcome) {
  summary_path <- file.path(out_dir, paste0(model_name, "_summary.txt"))
  capture.output({
    cat("Model:", model_name, "\n")
    cat("Family:", model_family, "\n")
    cat("Outcome:", outcome, "\n\n")
    print(summary(model))
    cat("\nAIC:\n")
    print(AIC(model))
    cat("\nGAM check:\n")
    print(gam.check(model, rep = 0))
    cat("\nConcurvity:\n")
    print(concurvity(model, full = TRUE))
  }, file = summary_path)

  sm <- summary(model)
  parametric <- as.data.frame(sm$p.table)
  parametric$term <- rownames(parametric)
  rownames(parametric) <- NULL
  names(parametric) <- gsub(" ", "_", names(parametric))
  # Standardise across Gaussian (t) and binomial (z) model families
  names(parametric) <- gsub("^z_value$", "t_value", names(parametric))
  names(parametric) <- gsub("Pr\\(>\\|z\\|\\)", "Pr(>|t|)", names(parametric))
  parametric$model <- model_name
  parametric$model_family <- model_family
  parametric$outcome <- outcome

  smooth <- as.data.frame(sm$s.table)
  smooth$term <- if (nrow(smooth) > 0) rownames(smooth) else character(0)
  rownames(smooth) <- NULL
  names(smooth) <- gsub(" ", "_", names(smooth))
  smooth$model <- model_name
  smooth$model_family <- model_family
  smooth$outcome <- outcome

  fit <- data.frame(
    model = model_name,
    model_family = model_family,
    outcome = outcome,
    n = nobs(model),
    aic = AIC(model),
    deviance_explained = sm$dev.expl,
    r_sq = sm$r.sq,
    scale = sm$scale,
    stringsAsFactors = FALSE
  )
  list(parametric = parametric, smooth = smooth, fit = fit)
}

prediction_grid_trial <- function(data) {
  expand.grid(
    language = levels(data$language),
    sentence_type = levels(data$sentence_type),
    participant_id = levels(data$participant_id)[1],
    image_id = levels(data$image_id)[1],
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
}

plot_trial_predictions <- function(model, model_name, outcome, data) {
  grid <- prediction_grid_trial(data)
  grid$language <- factor(grid$language, levels = levels(data$language))
  grid$sentence_type <- factor(grid$sentence_type, levels = levels(data$sentence_type))
  grid$participant_id <- factor(grid$participant_id, levels = levels(data$participant_id))
  grid$image_id <- factor(grid$image_id, levels = levels(data$image_id))
  pred <- predict(model, newdata = grid, type = "response", se.fit = TRUE, exclude = c("s(participant_id)", "s(image_id)"))
  grid$fit <- pred$fit
  grid$se <- pred$se.fit
  grid$lower <- grid$fit - 1.96 * grid$se
  grid$upper <- grid$fit + 1.96 * grid$se
  write.csv(grid, file.path(out_dir, paste0(model_name, "_predictions.csv")), row.names = FALSE)

  png(file.path(plot_dir, paste0(model_name, "_predicted_means.png")), width = 1200, height = 800, res = 150)
  y_range <- range(c(grid$lower, grid$upper), na.rm = TRUE)
  x <- seq_along(levels(data$sentence_type))
  plot(x, rep(NA, length(x)), ylim = y_range, xaxt = "n", xlab = "Sentence type", ylab = outcome, main = model_name)
  axis(1, at = x, labels = levels(data$sentence_type), las = 2)
  colors <- c("English" = "#1f77b4", "Punjabi" = "#d62728")
  offsets <- c("English" = -0.08, "Punjabi" = 0.08)
  for (lang in levels(data$language)) {
    sub <- grid[grid$language == lang, ]
    sub <- sub[match(levels(data$sentence_type), sub$sentence_type), ]
    xx <- x + offsets[lang]
    points(xx, sub$fit, type = "b", pch = 19, col = colors[lang])
    arrows(xx, sub$lower, xx, sub$upper, angle = 90, code = 3, length = 0.04, col = colors[lang])
  }
  legend("topright", legend = levels(data$language), col = colors[levels(data$language)], pch = 19, lty = 1, bty = "n")
  dev.off()
}

prediction_grid_ia <- function(data) {
  expand.grid(
    language = levels(data$language),
    sentence_type = levels(data$sentence_type),
    aoi_role = levels(data$aoi_role),
    participant_id = levels(data$participant_id)[1],
    image_id = levels(data$image_id)[1],
    ia_label = levels(data$ia_label)[1],
    KEEP.OUT.ATTRS = FALSE,
    stringsAsFactors = FALSE
  )
}

plot_ia_predictions <- function(model, model_name, outcome, data) {
  grid <- prediction_grid_ia(data)
  grid$language <- factor(grid$language, levels = levels(data$language))
  grid$sentence_type <- factor(grid$sentence_type, levels = levels(data$sentence_type))
  grid$aoi_role <- factor(grid$aoi_role, levels = levels(data$aoi_role))
  grid$participant_id <- factor(grid$participant_id, levels = levels(data$participant_id))
  grid$image_id <- factor(grid$image_id, levels = levels(data$image_id))
  grid$ia_label <- factor(grid$ia_label, levels = levels(data$ia_label))
  pred <- predict(model, newdata = grid, type = "response", se.fit = TRUE, exclude = c("s(participant_id)", "s(image_id)", "s(ia_label)"))
  grid$fit <- pred$fit
  grid$se <- pred$se.fit
  grid$lower <- grid$fit - 1.96 * grid$se
  grid$upper <- grid$fit + 1.96 * grid$se
  write.csv(grid, file.path(out_dir, paste0(model_name, "_predictions.csv")), row.names = FALSE)

  png(file.path(plot_dir, paste0(model_name, "_predicted_means.png")), width = 1400, height = 800, res = 150)
  y_range <- range(c(grid$lower, grid$upper), na.rm = TRUE)
  x <- seq_along(levels(data$sentence_type))
  plot(x, rep(NA, length(x)), ylim = y_range, xaxt = "n", xlab = "Sentence type", ylab = outcome, main = model_name)
  axis(1, at = x, labels = levels(data$sentence_type), las = 2)
  colors <- c("agent" = "#2ca02c", "object" = "#9467bd", "bg" = "#7f7f7f")
  offsets <- seq(-0.12, 0.12, length.out = length(levels(data$aoi_role)))
  names(offsets) <- levels(data$aoi_role)
  for (role in levels(data$aoi_role)) {
    sub <- grid[grid$aoi_role == role & grid$language == "English", ]
    sub <- sub[match(levels(data$sentence_type), sub$sentence_type), ]
    xx <- x + offsets[role]
    points(xx, sub$fit, type = "b", pch = 19, col = colors[role])
    arrows(xx, sub$lower, xx, sub$upper, angle = 90, code = 3, length = 0.04, col = colors[role])
  }
  legend("topright", legend = paste("English", levels(data$aoi_role)), col = colors[levels(data$aoi_role)], pch = 19, lty = 1, bty = "n")
  dev.off()
}

all_parametric <- list()
all_smooth <- list()
all_fit <- list()
counter <- 1

for (outcome in trial_outcomes) {
  model_name <- paste0("trial_sentence_type_", safe_name(outcome))
  formula <- as.formula(paste0(outcome, " ~ language * sentence_type + s(participant_id, bs='re') + s(image_id, bs='re')"))
  model_data <- trial_data[complete.cases(trial_data[, c(outcome, "language", "sentence_type", "participant_id", "image_id")]), ]
  model <- bam(formula, data = model_data, method = "fREML")
  outputs <- write_model_outputs(model, model_name, "trial_language_by_sentence_type", outcome)
  all_parametric[[counter]] <- outputs$parametric
  all_smooth[[counter]] <- outputs$smooth
  all_fit[[counter]] <- outputs$fit
  plot_trial_predictions(model, model_name, outcome, model_data)
  counter <- counter + 1
}

model_name <- "agent_first_cognitive_load_index"
model <- bam(cognitive_load_index ~ language * agent_first_alignment + s(participant_id, bs='re') + s(image_id, bs='re'), data = trial_data, method = "fREML")
outputs <- write_model_outputs(model, model_name, "trial_language_by_agent_first", "cognitive_load_index")
all_parametric[[counter]] <- outputs$parametric
all_smooth[[counter]] <- outputs$smooth
all_fit[[counter]] <- outputs$fit
counter <- counter + 1

passive_only <- subset(trial_data, sentence_type %in% c("passive", "passive_dropped_agent"))
passive_only$agent_overt <- relevel(factor(passive_only$agent_overt), ref = "agent_overt")
passive_only$language <- relevel(factor(passive_only$language), ref = "English")
model_name <- "agent_overt_passive_only_cognitive_load_index"
model <- bam(cognitive_load_index ~ language * agent_overt + s(participant_id, bs='re') + s(image_id, bs='re'), data = passive_only, method = "fREML")
outputs <- write_model_outputs(model, model_name, "passive_only_language_by_agent_overt", "cognitive_load_index")
all_parametric[[counter]] <- outputs$parametric
all_smooth[[counter]] <- outputs$smooth
all_fit[[counter]] <- outputs$fit
counter <- counter + 1

for (outcome in ia_outcomes) {
  model_name <- paste0("ia_role_", safe_name(outcome))
  formula <- as.formula(paste0(outcome, " ~ language * sentence_type * aoi_role + s(participant_id, bs='re') + s(image_id, bs='re') + s(ia_label, bs='re')"))
  model_data <- ia_sentence[complete.cases(ia_sentence[, c(outcome, "language", "sentence_type", "aoi_role", "participant_id", "image_id", "ia_label")]), ]
  model <- bam(formula, data = model_data, method = "fREML")
  outputs <- write_model_outputs(model, model_name, "interest_area_language_by_sentence_type_by_role", outcome)
  all_parametric[[counter]] <- outputs$parametric
  all_smooth[[counter]] <- outputs$smooth
  all_fit[[counter]] <- outputs$fit
  plot_ia_predictions(model, model_name, outcome, model_data)
  counter <- counter + 1
}

# ── Agent-first look: logistic GAMM ────────────────────────────────────────
# Binary outcome: did the first non-centre fixation land on the agent AOI?
# Excludes fixation index 1 (crosshair return).  One row per trial.
first_visit_path <- "analysis/derived/first_aoi_visit_dataset.csv"
if (file.exists(first_visit_path)) {
  first_visit <- read.csv(first_visit_path)
  first_visit <- subset(first_visit, !is.na(agent_first_look) & !is.na(language) & !is.na(sentence_type))
  first_visit$participant_id <- factor(first_visit$participant_id)
  first_visit$image_id       <- factor(first_visit$image_id)
  first_visit$language       <- relevel(factor(first_visit$language), ref = "English")
  first_visit$sentence_type  <- relevel(factor(first_visit$sentence_type), ref = "active")

  model_name <- "agent_first_look_logistic"
  model_fv <- bam(
    agent_first_look ~ language * sentence_type +
      s(participant_id, bs = "re") + s(image_id, bs = "re"),
    data   = first_visit,
    family = binomial,
    method = "fREML"
  )
  outputs_fv <- write_model_outputs(model_fv, model_name, "first_aoi_visit_logistic", "agent_first_look")
  all_parametric[[counter]] <- outputs_fv$parametric
  all_smooth[[counter]]     <- outputs_fv$smooth
  all_fit[[counter]]        <- outputs_fv$fit

  # Predicted probability grid
  grid_fv <- expand.grid(
    language      = levels(first_visit$language),
    sentence_type = levels(first_visit$sentence_type),
    participant_id = levels(first_visit$participant_id)[1],
    image_id       = levels(first_visit$image_id)[1],
    KEEP.OUT.ATTRS = FALSE, stringsAsFactors = FALSE
  )
  grid_fv$language      <- factor(grid_fv$language,      levels = levels(first_visit$language))
  grid_fv$sentence_type <- factor(grid_fv$sentence_type, levels = levels(first_visit$sentence_type))
  grid_fv$participant_id <- factor(grid_fv$participant_id, levels = levels(first_visit$participant_id))
  grid_fv$image_id       <- factor(grid_fv$image_id,       levels = levels(first_visit$image_id))
  pred_fv <- predict(model_fv, newdata = grid_fv, type = "response", se.fit = TRUE,
                     exclude = c("s(participant_id)", "s(image_id)"))
  grid_fv$prob_agent_first <- pred_fv$fit
  grid_fv$se               <- pred_fv$se.fit
  grid_fv$lower            <- pmax(0, grid_fv$prob_agent_first - 1.96 * grid_fv$se)
  grid_fv$upper            <- pmin(1, grid_fv$prob_agent_first + 1.96 * grid_fv$se)
  write.csv(grid_fv, file.path(out_dir, "agent_first_look_predictions.csv"), row.names = FALSE)

  png(file.path(plot_dir, "agent_first_look_predicted_prob.png"), width = 1200, height = 800, res = 150)
  x      <- seq_along(levels(first_visit$sentence_type))
  colors <- c("English" = "#1f77b4", "Punjabi" = "#d62728")
  offsets <- c("English" = -0.08, "Punjabi" = 0.08)
  plot(x, rep(NA, length(x)), ylim = c(0.2, 0.8), xaxt = "n",
       xlab = "Sentence type", ylab = "P(agent first look)",
       main = "Predicted probability of agent-first look (excl. fixation index 1)")
  axis(1, at = x, labels = levels(first_visit$sentence_type), las = 2)
  abline(h = 0.5, lty = 2, col = "gray60")
  for (lang in levels(first_visit$language)) {
    sub <- grid_fv[grid_fv$language == lang, ]
    sub <- sub[match(levels(first_visit$sentence_type), sub$sentence_type), ]
    xx  <- x + offsets[lang]
    points(xx, sub$prob_agent_first, type = "b", pch = 19, col = colors[lang])
    arrows(xx, sub$lower, xx, sub$upper, angle = 90, code = 3, length = 0.04, col = colors[lang])
  }
  legend("topright", legend = levels(first_visit$language),
         col = colors[levels(first_visit$language)], pch = 19, lty = 1, bty = "n")
  dev.off()
  counter <- counter + 1
  cat("Agent-first look logistic GAMM completed.\n")
} else {
  cat("Skipping agent_first_look model: first_aoi_visit_dataset.csv not found.\n")
}

# ── Temporal gaze dynamics: smooth over fixation index ─────────────────────
# Proportion of agent looks as a function of ordinal fixation position,
# modelled per language × sentence_type with participant random effects.
temporal_path <- "analysis/results/temporal/prop_agent_by_fixation_index.csv"
if (file.exists(temporal_path)) {
  temporal <- read.csv(temporal_path)
  temporal <- subset(temporal, !is.na(prop_agent_look) & n_fixations >= 20)
  temporal$language      <- relevel(factor(temporal$language), ref = "English")
  temporal$sentence_type <- relevel(factor(temporal$sentence_type), ref = "active")
  temporal$condition     <- interaction(temporal$language, temporal$sentence_type, drop = TRUE)

  model_name <- "temporal_agent_look_by_condition"
  # Gaussian GAM over aggregate proportion (no participant random effects at
  # aggregate level; participant-level temporal models need individual-trial data)
  model_temp <- gam(
    prop_agent_look ~ s(fixation_index, by = condition, k = 8) + condition,
    data   = temporal,
    method = "REML",
    weights = n_fixations
  )
  summary_path <- file.path(out_dir, paste0(model_name, "_summary.txt"))
  capture.output(print(summary(model_temp)), file = summary_path)

  pred_grid <- expand.grid(
    fixation_index = seq(2, 18, by = 1),
    condition = levels(temporal$condition),
    KEEP.OUT.ATTRS = FALSE, stringsAsFactors = FALSE
  )
  pred_grid$condition <- factor(pred_grid$condition, levels = levels(temporal$condition))
  pred_grid$language      <- sub("\\..*", "", pred_grid$condition)
  pred_grid$sentence_type <- sub(".*\\.", "", pred_grid$condition)
  pred_grid$n_fixations   <- 100
  pred_g <- predict(model_temp, newdata = pred_grid, type = "response", se.fit = TRUE)
  pred_grid$fit   <- pred_g$fit
  pred_grid$lower <- pred_g$fit - 1.96 * pred_g$se.fit
  pred_grid$upper <- pred_g$fit + 1.96 * pred_g$se.fit
  write.csv(pred_grid, file.path(out_dir, "temporal_agent_look_smooth_predictions.csv"), row.names = FALSE)

  png(file.path(plot_dir, "temporal_agent_look_smooth.png"), width = 1400, height = 800, res = 150)
  par(mfrow = c(1, 2))
  colors_t <- c("active" = "#2166ac", "passive" = "#f4a582", "passive_dropped_agent" = "#d6604d")
  for (lang in c("English", "Punjabi")) {
    sub <- pred_grid[pred_grid$language == lang, ]
    plot(NULL, xlim = c(2, 18), ylim = c(0.25, 0.75),
         xlab = "Fixation index (1 excluded)", ylab = "P(agent look)",
         main = paste("Temporal gaze dynamics —", lang))
    abline(h = 0.5, lty = 2, col = "gray60")
    for (stype in c("active", "passive", "passive_dropped_agent")) {
      s <- sub[sub$sentence_type == stype, ]
      if (nrow(s) == 0) next
      polygon(c(s$fixation_index, rev(s$fixation_index)),
              c(s$lower, rev(s$upper)),
              col = adjustcolor(colors_t[stype], alpha.f = 0.2), border = NA)
      lines(s$fixation_index, s$fit, col = colors_t[stype], lwd = 2,
            lty = ifelse(stype == "active", 1, ifelse(stype == "passive", 2, 3)))
    }
    legend("bottomright",
           legend = c("active", "passive", "passive_dropped_agent"),
           col = unname(colors_t), lwd = 2, lty = c(1, 2, 3), bty = "n", cex = 0.85)
  }
  dev.off()
  cat("Temporal gaze dynamics model completed.\n")
} else {
  cat("Skipping temporal model: run python analysis/run_temporal_analysis.py first.\n")
}

safe_rbind <- function(lst) {
  lst <- Filter(Negate(is.null), lst)
  lst <- Filter(function(x) !is.null(x) && nrow(x) > 0, lst)
  if (length(lst) == 0) return(data.frame())
  all_cols <- unique(unlist(lapply(lst, names)))
  lst <- lapply(lst, function(x) {
    missing_cols <- setdiff(all_cols, names(x))
    if (length(missing_cols) > 0) x[missing_cols] <- NA
    x[all_cols]
  })
  do.call(rbind, lst)
}

parametric_results <- safe_rbind(all_parametric)
smooth_results     <- safe_rbind(all_smooth)
fit_results        <- safe_rbind(all_fit)

write.csv(parametric_results, file.path(out_dir, "gamm_parametric_terms.csv"), row.names = FALSE)
write.csv(smooth_results, file.path(out_dir, "gamm_smooth_terms.csv"), row.names = FALSE)
write.csv(fit_results, file.path(out_dir, "gamm_model_fit.csv"), row.names = FALSE)

p_column <- grep("^Pr", names(parametric_results), value = TRUE)[1]
significant_parametric <- parametric_results[parametric_results[[p_column]] < 0.05, ]
if (nrow(significant_parametric) > 0) {
  write.csv(significant_parametric, file.path(out_dir, "gamm_significant_parametric_terms.csv"), row.names = FALSE)
} else {
  write.csv(parametric_results[0, ], file.path(out_dir, "gamm_significant_parametric_terms.csv"), row.names = FALSE)
}

cat("GAMM analyses completed. Outputs written to", out_dir, "\n")
