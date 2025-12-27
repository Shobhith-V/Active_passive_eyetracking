# %% Common Imports. Some unused
library(itsadug) # Tools for interpreting GAMM models and visualization (especially time series in psycholing.)
library(lme4) # Fitting linear and generalized linear mixed-effects models
library(sjPlot) # Plotting regression models and diagnostics (e.g., fixed effects, random effects)
library(ggeffects) # Easily extract and plot marginal effects (predicted values) from regression models
library(performance) # Diagnostic tools for regression models (e.g., check_model, check_overdispersion)
library(patchwork) # Combine multiple ggplot2 plots into a single layout
library(lmerTest) # Adds p-values to lme4 mixed models using Satterthwaite’s method
library(dplyr) # Data manipulation: filter, select, mutate, summarize, etc.
library(ggplot2) # Data visualization using the grammar of graphics
library(MASS) # Functions and datasets for statistical methods (e.g., stepAIC, negative binomial)
library(tidyr) # Data tidying: pivot_longer, pivot_wider, separate, unite, etc.
library(glmmTMB)
library(knitr)
library(kableExtra)
library(glmmTMB)

rm(list = ls())
# %%# Load the dataset
fixation_data <- read.csv("data\\output\\final-combined-pre-post-reaction-time-filtered-1-5.csv")
colnames(fixation_data)
fixation_data["main_experiment_name"] <- fixation_data["experiment_name.1"]

# %%
all_cols <- c(
    "trial_number", "index", "file", "posx", "posy", "correct_key",
    "correct_key_number", "circle_dia", "resp_key", "rt", "ID",
    "participant", "session", "Gender", "edf_filename_df", "date_df",
    "experiment_name", "date_part", "experiment_name.1", "age", "gender",
    "edf_filename_part", "dominant_eye", "dominant_hand", "mean_rt",
    "std_rt", "lower_bound", "upper_bound"
)

# Columns to convert to factors (categorical only)
factor_cols <- c(
    "file", "correct_key", "resp_key", "ID", "participant",
    "session", "Gender", "gender", "experiment_name", "experiment_name.1",
    "edf_filename_df", "edf_filename_part", "dominant_eye", "dominant_hand", "main_experiment_name"
)

# Convert categorical columns to factor
fixation_data[factor_cols] <- lapply(fixation_data[factor_cols], as.factor)

# Relevel selected categorical variables for interpretation clarity
fixation_data$session <- relevel(fixation_data$session, ref = "POST")
fixation_data$Gender <- relevel(fixation_data$Gender, ref = "Female")
fixation_data$gender <- relevel(fixation_data$gender, ref = "Female")
# fixation_data$experiment_name <- relevel(fixation_data$experiment_name, ref = "Grounded")
fixation_data$experiment_name.1 <- relevel(fixation_data$experiment_name.1, ref = "Grounded")
fixation_data$dominant_eye <- relevel(fixation_data$dominant_eye, ref = "Right")
fixation_data$dominant_hand <- relevel(fixation_data$dominant_hand, ref = "Right")

# %%
numeric_vars <- c("posx", "posy")

# Save mean and sd for later use (e.g., prediction)
scaling_params <- fixation_data %>%
    dplyr::select(all_of(numeric_vars)) %>%
    summarise(across(everything(), list(mean = mean, sd = sd)))
# Standardize predictors
fixation_data_scaled <- fixation_data
fixation_data_scaled[numeric_vars] <- scale(fixation_data[numeric_vars])
# %%
model_simple <- glmmTMB(
    rt ~ main_experiment_name + session + correct_key +
        posx + posy + age + gender + dominant_hand + dominant_eye +
        (1 | participant) + (1 | file),
    data = fixation_data_scaled,
    family = Gamma(link = "log"),
    dispformula = ~1
)
summary(model_simple)

# %%
model_interaction <- glmmTMB(
    rt ~ main_experiment_name * session + correct_key +
        posx + posy + age + gender +
        dominant_hand + dominant_eye +
        (1 | participant) + (1 | file),
    data = fixation_data_scaled,
    family = Gamma(link = "log"),
    dispformula = ~1
)
summary(model_interaction)
# %%
anova(model_simple, model_interaction, test = "Chisq")
