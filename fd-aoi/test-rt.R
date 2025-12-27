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
rt <- read.csv("main-experiment\\far_near_grounded_ungrounded_combined.csv")
# %%
colnames(rt)
# %%
# --- Packages ---
library(dplyr)
library(glmmTMB)

# %% Work on a copy without outliers
nrow(rt)
dat <- rt[rt$outlier == "False", ]
nrow(dat)

# %%
# Compute bounding box area (pixels)
dat$bounding_box_area <- with(
    dat,
    (bounding_box_x_max - bounding_box_x_min) *
        (bounding_box_y_max - bounding_box_y_min)
)

# --- Define thresholds and classify distance into proximity labels ---
threshold <- 230
margin <- 30

dat$near_far_between <- with(dat, case_when(
    distance_from_camera < (threshold - margin) ~ "NEAR",
    distance_from_camera > (threshold + margin) ~ "FAR",
    TRUE ~ "AROUND_THRESHOLD"
))

# Set factor levels for ordered proximity categories
dat$near_far_between <- factor(
    dat$near_far_between,
    levels = c("NEAR", "AROUND_THRESHOLD", "FAR")
)

# Convert selected columns to factors (use names that exist in `rt`)
factor_cols <- c(
    "participant", "stim_id", "gender", "expName", "session",
    "object_shape", "object_size", "near_far_between", "object_color",
    "real_near_far_label", "correct"
)

dat[factor_cols] <- lapply(dat[factor_cols], \(x) as.factor(x))

dat$correct <- stats::relevel(factor(dat$correct), ref = "False")
dat$expName <- stats::relevel(factor(dat$expName), ref = "UnGrounded")
dat$session <- stats::relevel(factor(dat$session), ref = "TRAIN")
dat$gender <- stats::relevel(factor(dat$gender), ref = "Female")
dat$object_shape <- stats::relevel(factor(dat$object_shape), ref = "cube")
dat$object_color <- stats::relevel(factor(dat$object_color), ref = "blue")
dat$object_size <- factor(dat$object_size, levels = c("size 6", "size 8", "size 10"))
dat$real_near_far_label <- stats::relevel(factor(dat$real_near_far_label), ref = "NEAR")
dat$proximity_label <- factor(dat$near_far_between)

# %%
# --- Standardize numeric predictors ---
numeric_vars <- c("age", "bounding_box_area")

scaling_params <- dat |>
    dplyr::select(all_of(numeric_vars)) |>
    summarise(across(everything(), list(
        mean = ~ mean(.x, na.rm = TRUE),
        sd = ~ sd(.x, na.rm = TRUE)
    )))

dat_scaled <- dat
if (length(numeric_vars) > 0) {
    dat_scaled[numeric_vars] <- lapply(dat_scaled[numeric_vars], scale)
}

# --- Rename to analysis-friendly names (matching your prior script) ---
dat_scaled <- dat_scaled |>
    rename(
        experiment          = expName,
        session_type        = session,
        is_response_correct = correct,
        participant_id      = participant,
        file_id             = file_name
    )


# %% ========== Model ==========
m1 <- glmmTMB(
    rt ~ experiment + session_type + is_response_correct +
        bounding_box_area + proximity_label +
        object_size + object_shape + object_color +
        age + gender +
        (1 | participant_id) + (1 | file_id),
    data = dat_scaled,
    family = Gamma(link = "log"),
    dispformula = ~1
)

summary(m1)

# %%
m2 <- glmmTMB(
    rt ~ experiment * session_type + is_response_correct +
        bounding_box_area + proximity_label +
        object_size + object_shape + object_color +
        age + gender +
        (1 | participant_id) + (1 | file_id),
    data = dat_scaled,
    family = Gamma(link = "log"),
    dispformula = ~1
)
summary(m2)
# %%
anova(m1, m2, test = "Chisq")

# %% Dharma test
library(DHARMa)
model <- m2
model_string <- "rt-glmmTMB-Gamma-log-m2"
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
