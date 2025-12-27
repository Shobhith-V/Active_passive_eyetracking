# %% Report Generation
# Script: 14_generate_report.R
# Purpose: Generate summary tables and reports

# Load required libraries
library(dplyr)
library(knitr)
library(kableExtra)

# Clear workspace
rm(list = ls())

# Set working directory
if (!dir.exists("scripts")) {
  setwd("..")
}

# Create output directories
dir.create("results/tables", showWarnings = FALSE, recursive = TRUE)
dir.create("results/reports", showWarnings = FALSE, recursive = TRUE)

# %% Load all model comparison results
cat("Loading model comparison results...\n")

model_comparisons <- list()

comparison_files <- list.files("results/model_summaries", 
                               pattern = "*_model_comparison.csv", 
                               full.names = TRUE)

for (file in comparison_files) {
  analysis_type <- gsub("_model_comparison.csv", "", basename(file))
  model_comparisons[[analysis_type]] <- read.csv(file, stringsAsFactors = FALSE)
}

# %% Create comprehensive model comparison table
cat("Creating comprehensive model comparison table...\n")

if (length(model_comparisons) > 0) {
  all_comparisons <- do.call(rbind, lapply(names(model_comparisons), function(name) {
    df <- model_comparisons[[name]]
    df$analysis_type <- name
    return(df)
  }))
  
  write.csv(all_comparisons, "results/tables/all_models_comparison.csv", row.names = FALSE)
  
  # Create formatted table
  comparison_table <- all_comparisons %>%
    select(analysis_type, Model, AIC, BIC, Deviance_Explained, R_sq) %>%
    arrange(analysis_type, AIC)
  
  write.csv(comparison_table, "results/tables/formatted_model_comparison.csv", row.names = FALSE)
}

# %% Create key findings summary
cat("Creating key findings summary...\n")

key_findings <- data.frame(
  finding = character(),
  description = character(),
  evidence = character(),
  stringsAsFactors = FALSE
)

# Load effect sizes if available
if (file.exists("results/effect_sizes/voice_type_effect_sizes.csv")) {
  effect_sizes <- read.csv("results/effect_sizes/voice_type_effect_sizes.csv", stringsAsFactors = FALSE)
  
  # Extract significant findings
  significant_effects <- effect_sizes %>%
    filter(p_value < 0.05)
  
  if (nrow(significant_effects) > 0) {
    for (i in 1:nrow(significant_effects)) {
      key_findings <- rbind(key_findings, data.frame(
        finding = paste("Significant effect in", significant_effects$model[i]),
        description = paste("Voice type effect on", significant_effects$predictor[i]),
        evidence = paste("Estimate =", round(significant_effects$estimate[i], 3),
                        ", p =", round(significant_effects$p_value[i], 4)),
        stringsAsFactors = FALSE
      ))
    }
  }
}

# Load EMM results if available
if (file.exists("results/effect_sizes/estimated_marginal_means.csv")) {
  emm_results <- read.csv("results/effect_sizes/estimated_marginal_means.csv", stringsAsFactors = FALSE)
  
  # Add findings about differences between conditions
  if (nrow(emm_results) > 0 && "voice_type" %in% names(emm_results)) {
    voice_comparisons <- emm_results %>%
      group_by(model, aoi_type) %>%
      summarise(
        n_conditions = n_distinct(voice_type),
        mean_diff = ifelse(n_conditions == 2, 
                          diff(range(emmean, na.rm = TRUE)), 
                          NA),
        .groups = "drop"
      ) %>%
      filter(!is.na(mean_diff))
    
    if (nrow(voice_comparisons) > 0) {
      for (i in 1:nrow(voice_comparisons)) {
        key_findings <- rbind(key_findings, data.frame(
          finding = paste("Voice type difference in", voice_comparisons$model[i]),
          description = paste("Difference in", voice_comparisons$aoi_type[i], "AOI"),
          evidence = paste("Mean difference =", round(voice_comparisons$mean_diff[i], 3)),
          stringsAsFactors = FALSE
        ))
      }
    }
  }
}

# Save key findings
if (nrow(key_findings) > 0) {
  write.csv(key_findings, "results/reports/key_findings_summary.csv", row.names = FALSE)
} else {
  # Create empty template
  write.csv(key_findings, "results/reports/key_findings_summary.csv", row.names = FALSE)
}

# %% Create summary statistics table
cat("Creating summary statistics table...\n")

# Load data quality report
if (file.exists("results/data_quality/data_quality_report.csv")) {
  quality_report <- read.csv("results/data_quality/data_quality_report.csv", stringsAsFactors = FALSE)
  write.csv(quality_report, "results/tables/data_quality_summary.csv", row.names = FALSE)
}

# %% Export results to Excel (if writexl is available)
cat("Exporting results to CSV files...\n")

# Create a summary of all available results
results_summary <- data.frame(
  result_type = c(
    "Model Comparisons",
    "Effect Sizes",
    "Estimated Marginal Means",
    "Model Diagnostics",
    "Data Quality",
    "Key Findings"
  ),
  file_path = c(
    "results/tables/all_models_comparison.csv",
    "results/effect_sizes/voice_type_effect_sizes.csv",
    "results/effect_sizes/estimated_marginal_means.csv",
    "results/model_summaries/model_diagnostic_summary.csv",
    "results/data_quality/data_quality_report.csv",
    "results/reports/key_findings_summary.csv"
  ),
  available = file.exists(c(
    "results/tables/all_models_comparison.csv",
    "results/effect_sizes/voice_type_effect_sizes.csv",
    "results/effect_sizes/estimated_marginal_means.csv",
    "results/model_summaries/model_diagnostic_summary.csv",
    "results/data_quality/data_quality_report.csv",
    "results/reports/key_findings_summary.csv"
  )),
  stringsAsFactors = FALSE
)

write.csv(results_summary, "results/reports/results_index.csv", row.names = FALSE)

# %% Print summary
cat("\n=== Report Generation Complete ===\n")
cat("Summary tables saved to results/tables/\n")
cat("Reports saved to results/reports/\n")
cat("\nAvailable results:\n")
print(results_summary)

cat("\nAll analysis complete! Check results/ directory for outputs.\n")



