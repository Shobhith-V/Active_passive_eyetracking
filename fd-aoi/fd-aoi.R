# %% Model fitting and inference
library(lme4) # Linear and GLMMs
library(glmmTMB) # Flexible GLMMs, incl. zero-inflation
library(lmerTest) # p-values for lmer models
library(MASS) # Stepwise model selection, distributions

# Visualization and effects
library(ggplot2) # Plotting
library(ggeffects) # Marginal effects plots
library(sjPlot) # Visualizing model summaries
library(patchwork) # Combine ggplots

# Diagnostics
library(performance) # Model checks

# Data handling
library(dplyr) # Data manipulation
library(tidyr) # Data tidying

# GAM/GAMM utilities
library(itsadug) # Tools for interpreting GAMMs

# Reporting
library(knitr) # Report tables
library(kableExtra) # Table formatting for reports
library("xtable")

rm(list = ls())
# %%
fixation_data <- read.csv("fd-aoi/df_merged_total_fixation_duration_near_objects_aoi.csv")
# %%
# --- Define thresholds and classify distance into proximity labels ---
threshold <- 230
margin <- 30

fixation_data$near_far_between <- with(fixation_data, case_when(
    distance_from_camera < (threshold - margin) ~ "NEAR",
    distance_from_camera > (threshold + margin) ~ "FAR",
    TRUE ~ "AROUND_THRESHOLD"
))

# Set factor levels for ordered proximity categories
fixation_data$near_far_between <- factor(
    fixation_data$near_far_between,
    levels = c("NEAR", "AROUND_THRESHOLD", "FAR")
)

factor_cols <- c(
    "participant", "file", "gender", "expName", "session",
    "object_shape", "object_size", "object_color",
    "near_far", "real_near_far_label",
    "correct"
)

# Convert selected columns to factors
fixation_data[factor_cols] <- lapply(fixation_data[factor_cols], as.factor)
# Releveling in-place for clarity
fixation_data$correct <- relevel(fixation_data$correct, ref = "False")
fixation_data$expName <- relevel(fixation_data$expName, ref = "Grounded")
fixation_data$session <- relevel(fixation_data$session, ref = "TEST")
fixation_data$gender <- relevel(fixation_data$gender, ref = "Female")
fixation_data$object_shape <- relevel(fixation_data$object_shape, ref = "cube")
fixation_data$object_size <- relevel(fixation_data$object_size, ref = "size 6")
fixation_data$object_color <- relevel(fixation_data$object_color, ref = "blue")
fixation_data$real_near_far_label <- relevel(fixation_data$real_near_far_label, ref = "NEAR")
fixation_data$bounding_box_area <- with(
    fixation_data,
    (bounding_box_x_max - bounding_box_x_min) *
        (bounding_box_y_max - bounding_box_y_min)
)

# --- Standardize numeric predictors and save scaling parameters ---
numeric_vars <- c(
    "age", "bounding_box_area"
)

# Save means and SDs of numeric variables
scaling_params <- fixation_data %>%
    dplyr::select(all_of(numeric_vars)) %>%
    summarise(across(everything(), list(mean = mean, sd = sd)))

# Create scaled copy of dataset
fixation_data_scaled <- fixation_data
fixation_data_scaled[numeric_vars] <- scale(fixation_data[numeric_vars])
# %%
# --- Convert object size to ordered factor ---
fixation_data_scaled$object_size <- factor(
    fixation_data_scaled$object_size,
    levels = c("size 6", "size 8", "size 10")
)

# --- Rename and recode key columns for consistency and analysis ---
fixation_data_scaled <- fixation_data_scaled %>%
    rename(
        experiment            = expName,
        session_type          = session,
        is_response_correct   = correct,
        proximity_label       = near_far_between,
        participant_id        = participant,
        file_id               = file
    )


# Create labeled version of response accuracy
fixation_data_scaled <- fixation_data_scaled %>%
    mutate(is_response_correct_label = ifelse(is_response_correct == "True", "Correct", "Incorrect"))

# %% Model Training
model_simple <- m1 <- glmmTMB(
    total_fixation_duration ~ experiment + session_type + is_response_correct +
        bounding_box_area + object_size + proximity_label + object_color + object_shape + age + gender +
        (1 | participant_id) + (1 | file_id),
    data = fixation_data_scaled,
    family = Gamma(link = "log"),
    dispformula = ~1
)
summary(m1)
# %%
vif_result <- check_collinearity(m1)
print(vif_result)
# %%
model_simpler <- m2 <- glmmTMB(
    total_fixation_duration ~ experiment + session_type + is_response_correct +
        bounding_box_area + object_size + proximity_label +
        (1 | participant_id) + (1 | file_id),
    data = fixation_data_scaled,
    family = Gamma(link = "log"),
    dispformula = ~1
)
summary(m2)
# %%
model_interaction <- m3 <- glmmTMB(
    total_fixation_duration ~ bounding_box_area +
        object_size * proximity_label +
        is_response_correct * experiment +
        experiment * session_type +
        (1 | participant_id) + (1 | file_id),
    family = Gamma(link = "log"),
    data = fixation_data_scaled,
    dispformula = ~1
)
summary(m3)
# %%
library(emmeans)
# On response scale (μ), not log scale
emm_obj_prox <- emmeans(m3, ~ proximity_label * object_size, type = "response")
# View the estimated means
summary(emm_obj_prox)
# %%
plot(emm_obj_prox)
emm_df <- as.data.frame(emm_obj_prox)
library(ggplot2)

# Optional: relabel for readability
emm_df$proximity_label <- recode(emm_df$proximity_label,
    "NEAR" = "Near",
    "AROUND_THRESHOLD" = "Around Threshold",
    "FAR" = "Far"
)

# Create the plot
p <- ggplot(emm_df, aes(x = proximity_label, y = response, color = object_size)) +
    geom_point(size = 3, position = position_dodge(0.3)) +
    geom_line(aes(group = object_size), position = position_dodge(0.3), linewidth = 1) +
    geom_errorbar(aes(ymin = asymp.LCL, ymax = asymp.UCL),
        width = 0.1, position = position_dodge(0.3)
    ) +
    labs(
        x = "Proximity",
        y = "Estimated Fixation Duration (s)",
        color = "Object Size"
    ) +
    theme_minimal(base_size = 14, base_family = "Times New Roman") +
    theme(
        plot.title = element_blank(), # No title
        legend.position = "right"
    )

# Save as SVG (8x5 inches)
ggsave("emm-plot-proximity-label-response.svg", plot = p, width = 8, height = 5, units = "in")

# %%
# %%
library(emmeans)
library(ggplot2)

# Compute estimated marginal means with experiment included
emm_obj_prox_exp <- emmeans(
    m3,
    ~ proximity_label * object_size * experiment,
    type = "response"
)

# Convert to data frame
emm_df_exp <- as.data.frame(emm_obj_prox_exp)

# Optional: relabel for readability
emm_df_exp$proximity_label <- recode(emm_df_exp$proximity_label,
    "NEAR" = "Near",
    "AROUND_THRESHOLD" = "Around Threshold",
    "FAR" = "Far"
)

emm_df_exp$experiment <- recode(emm_df_exp$experiment,
    "Grounded" = "Grounded",
    "Ungrounded" = "Ungrounded"
)

# Plot separately by experiment (Grounded/Ungrounded)
p_split <- ggplot(emm_df_exp, aes(x = proximity_label, y = response, color = object_size)) +
    geom_point(size = 3, position = position_dodge(0.3)) +
    geom_line(aes(group = object_size), position = position_dodge(0.3), linewidth = 1) +
    geom_errorbar(aes(ymin = asymp.LCL, ymax = asymp.UCL),
        width = 0.1, position = position_dodge(0.3)
    ) +
    labs(
        x = "Proximity",
        y = "Estimated Fixation Duration (s)",
        color = "Object Size"
    ) +
    facet_wrap(~experiment) + # <-- Split by Grounded/Ungrounded
    theme_minimal(base_size = 14, base_family = "Times New Roman") +
    theme(
        plot.title = element_blank(),
        legend.position = "right"
    )

# Save as SVG
ggsave("emm-plot-proximity-split-by-experiment.svg", plot = p_split, width = 8, height = 5, units = "in")

# %% Estimated marginal means for the is_response_correct × experiment interaction
emm_correct_exp <- emmeans(model_interaction, ~ is_response_correct * experiment, type = "response")
# View results
summary(emm_correct_exp)

# %% Estimated marginal means for the is_response_correct × experiment interaction
emm_session_exp <- emmeans(model_interaction, ~ session_type * experiment, type = "response")

# View results
summary(emm_session_exp)

# %%
# Load necessary libraries
library(ggplot2)
library(emmeans)

# Get emmeans
emm_correct_exp <- emmeans(model_interaction, ~ is_response_correct * experiment, type = "response")
emm_df_correct <- as.data.frame(emm_correct_exp)

# Relabel (optional)
emm_df_correct$is_response_correct <- recode(emm_df_correct$is_response_correct,
    "True" = "Correct", "False" = "Incorrect"
)
emm_df_correct$experiment <- recode(emm_df_correct$experiment,
    "Grounded" = "Grounded", "Ungrounded" = "Ungrounded"
)

# Plot
p_correct <- ggplot(emm_df_correct, aes(x = experiment, y = response, color = is_response_correct)) +
    geom_point(size = 3, position = position_dodge(0.3)) +
    geom_line(aes(group = is_response_correct), position = position_dodge(0.3), linewidth = 1) +
    geom_errorbar(aes(ymin = asymp.LCL, ymax = asymp.UCL),
        width = 0.1, position = position_dodge(0.3)
    ) +
    labs(
        x = "Experimental Condition",
        y = "Estimated Fixation Duration (s)",
        color = "Response Accuracy"
    ) +
    theme_minimal(base_size = 14, base_family = "Times New Roman") +
    theme(
        plot.title = element_blank(),
        legend.position = "right"
    )

# Save
ggsave("emm-plot-correctness-experiment.svg", plot = p_correct, width = 8, height = 5, units = "in")




# %%
# Get emmeans
emm_session_exp <- emmeans(model_interaction, ~ session_type * experiment, type = "response")
emm_df_session <- as.data.frame(emm_session_exp)

# Relabel (optional)
emm_df_session$session_type <- recode(emm_df_session$session_type,
    "TEST" = "Test", "TRAIN" = "Train"
)
emm_df_session$experiment <- recode(emm_df_session$experiment,
    "Grounded" = "Grounded", "Ungrounded" = "Ungrounded"
)

# Plot
p_session <- ggplot(emm_df_session, aes(x = experiment, y = response, color = session_type)) +
    geom_point(size = 3, position = position_dodge(0.3)) +
    geom_line(aes(group = session_type), position = position_dodge(0.3), linewidth = 1) +
    geom_errorbar(aes(ymin = asymp.LCL, ymax = asymp.UCL),
        width = 0.1, position = position_dodge(0.3)
    ) +
    labs(
        x = "Experimental Condition",
        y = "Estimated Fixation Duration (s)",
        color = "Session Type"
    ) +
    theme_minimal(base_size = 14, base_family = "Times New Roman") +
    theme(
        plot.title = element_blank(),
        legend.position = "right"
    )

# Save
ggsave("emm-plot-sessiontype-experiment.svg", plot = p_session, width = 8, height = 5, units = "in")
# %%
library(ggplot2)

# Create the plot
p <- ggplot(fixation_data, aes(x = total_fixation_duration)) +
    geom_histogram(aes(y = ..density..), bins = 50, fill = "skyblue", color = "black", alpha = 0.6) +
    geom_density(color = "darkblue", size = 1.2) +
    labs(
        title = "Distribution of Total Fixation Duration",
        x = "Total Fixation Duration (ms)",
        y = "Density"
    ) +
    theme_minimal(base_family = "Times New Roman") +
    theme(
        plot.title = element_text(size = 14, face = "bold"),
        axis.title = element_text(size = 12),
        axis.text = element_text(size = 10)
    )

# Save to SVG
ggsave(
    filename = "distribution_total_fixation_duration.svg",
    plot = p,
    width = 8,
    height = 5,
    dpi = 300,
    device = "svg"
)

# %% Dharma test
library(DHARMa)
model <- m3
model_string <- "m3"
# Simulate residuals
sim_res <- simulateResiduals(fittedModel = model)
# Save main residual diagnostics plot
svg(paste0(model_string, "-DHARMa-residual-diagnostics.svg"), width = 8, height = 6)
plot(sim_res)
dev.off()

# Save testDispersion plot
svg(paste0(model_string, "-DHARMa-dispersion-test.svg"), width = 8, height = 6)
testDispersion(sim_res, plot = TRUE)
dev.off()

# Save testZeroInflation plot
svg(paste0(model_string, "-DHARMa-zero-inflation-test.svg"), width = 8, height = 6)
testZeroInflation(sim_res, plot = TRUE)
dev.off()

# PPC
library(performance)
ppc <- check_predictions(model, iterations = 50, type = "density")
ggsave(paste0(model_string, "-ppc-auto.svg"),
    plot = plot(ppc),
    width = 8, height = 4, dpi = 300
)


# %%
theme_set(theme_minimal(base_family = "Times New Roman"))

p1 <- ggplot(fixation_data_scaled, aes(x = proximity_label, y = total_fixation_duration, fill = object_size)) +
    geom_boxplot(position = position_dodge(width = 0.8)) +
    labs(
        x = "Proximity",
        y = "Total Fixation Duration"
    ) +
    theme(
        plot.title = element_blank()
    )

ggsave("plot_objectsize_proximity.svg", plot = p1, width = 8, height = 5, dpi = 300)


# %% Accuracy vs Distance

library(ggplot2)
library(scales)
df <- fixation_data

# 1) Prep: correctness as 0/1
df <- df %>%
    mutate(is_correct = ifelse(correct == "True", 1L, 0L))


bin_width <- 5

binned <- df %>%
    mutate(dist_bin = cut_width(distance_from_camera, width = bin_width, boundary = 0)) %>%
    group_by(dist_bin) %>%
    summarise(
        bin_center = mean(distance_from_camera, na.rm = TRUE),
        pct_correct = mean(is_correct, na.rm = TRUE) * 100,
        n = dplyr::n(),
        .groups = "drop"
    ) %>%
    arrange(bin_center)

# 4) Mean/SD of the *distance* distribution
mu <- mean(df$distance_from_camera, na.rm = TRUE)
sdv <- sd(df$distance_from_camera, na.rm = TRUE)

# Bands for ±1σ, ±2σ, ±3σ (for background shading)
bands <- tibble::tribble(
    ~xmin,          ~xmax,           ~band,
    mu - 1 * sdv,     mu + 1 * sdv,      "±1σ",
    mu - 2 * sdv,     mu + 2 * sdv,      "±2σ",
    mu - 3 * sdv,     mu + 3 * sdv,      "±3σ"
)

# Vertical lines at μ, ±1σ, ±2σ, ±3σ
vlines <- tibble::tibble(
    x = c(mu + (-3:-1) * sdv, mu, mu + (1:3) * sdv),
    lab = c("-3σ", "-2σ", "-1σ", "μ", "+1σ", "+2σ", "+3σ")
)

# Build tick positions + labels
tick_tbl <- tibble::tibble(
    x   = c(mu + (-3:3) * sdv, mu - 0.5 * sdv, mu + 0.5 * sdv, 230),
    tag = c("-3σ", "-2σ", "-1σ", "μ", "+1σ", "+2σ", "+3σ", "-0.5σ", "+0.5σ", "230")
) %>%
    arrange(x) %>%
    distinct(x, .keep_all = TRUE)

# %% Plot with smoothed curve, SD bands, 230 line, and custom x-axis labels
ggplot(binned, aes(x = bin_center, y = pct_correct)) +
    geom_rect(
        data = bands,
        aes(xmin = xmin, xmax = xmax, ymin = -Inf, ymax = Inf, fill = band),
        inherit.aes = FALSE, alpha = 0.06, show.legend = TRUE
    ) +
    geom_point(aes(size = 0.1), alpha = 0.7) +
    geom_smooth(aes(weight = n),
        method = "loess", span = 0.35,
        se = FALSE, linewidth = 1
    ) +
    geom_vline(xintercept = 230, linetype = "dashed", linewidth = 0.7, color = "red") +
    geom_vline(
        data = vlines, aes(xintercept = x, linetype = lab),
        linewidth = 0.5, alpha = 0.7
    ) +
    geom_vline(xintercept = mu - 0.5 * sdv, linetype = "dotdash", linewidth = 0.5, alpha = 0.7) +
    geom_vline(xintercept = mu + 0.5 * sdv, linetype = "dotdash", linewidth = 0.5, alpha = 0.7) +
    scale_linetype_manual(values = c("dashed", "dashed", "dashed", "solid", "dashed", "dashed", "dashed")) +
    scale_size_continuous(name = "Point") +
    scale_fill_discrete(name = "Distance bands") +
    coord_cartesian(ylim = c(45, 105)) +
    # <<< custom x-axis ticks with values >>>
    scale_x_continuous(
        breaks = tick_tbl$x,
        labels = paste0(tick_tbl$tag, "\n", number(tick_tbl$x, accuracy = 0.1))
    ) +
    labs(
        x = "Distance from Camera", y = "Percentage Correct",
        title = "Percentage Correct vs Distance (smoothed) with μ & SD markers"
    ) +
    theme_minimal() +
    theme(axis.text.x = element_text(angle = 45, hjust = 1))
# %%
# Save last plotted ggplot
ggsave("accuracy-distribution.svg", width = 8, height = 6, dpi = 300)
