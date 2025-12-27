# %% Data Quality Checks
# Script: 04_data_quality.py
# Purpose: Identify outliers, check missing data, validate consistency

import pandas as pd
import numpy as np
import os

# Set working directory
if not os.path.exists("scripts"):
    os.chdir("..")

# Create output directory for quality reports
os.makedirs("results/data_quality", exist_ok=True)

# Load merged data
print("Loading merged data...")
merged_fixation_data = pd.read_csv("data/processed/merged_fixation_data.csv")
merged_interest_area_data = pd.read_csv("data/processed/merged_interest_area_data.csv")
merged_saccade_data = pd.read_csv("data/processed/merged_saccade_data.csv")
merged_trial_data = pd.read_csv("data/processed/merged_trial_data.csv")

# %% Check for missing critical variables
print("Checking for missing critical variables...")

def check_missing(df, df_name):
    """Check for missing data in a dataframe."""
    print(f"\n=== Missing Data Check: {df_name} ===")
    
    # Count missing values (NA, empty strings, or ".")
    missing_counts = {}
    for col in df.columns:
        missing_count = df[col].isna().sum() + (df[col] == "").sum() + (df[col] == ".").sum()
        missing_counts[col] = missing_count
    
    missing_summary = pd.DataFrame({
        'variable': list(missing_counts.keys()),
        'missing_count': list(missing_counts.values())
    })
    
    missing_summary['missing_pct'] = (100 * missing_summary['missing_count'] / len(df)).round(2)
    
    critical_vars = ["participant_id", "TRIAL_INDEX", "sentence", "voice_id",
                     "CURRENT_FIX_DURATION", "IA_DWELL_TIME", "CURRENT_SAC_AMPLITUDE"]
    missing_summary['critical'] = missing_summary['variable'].isin(critical_vars)
    
    missing_summary = missing_summary.sort_values('missing_count', ascending=False)
    
    # Print critical variables with missing data
    critical_missing = missing_summary[(missing_summary['critical']) & (missing_summary['missing_count'] > 0)]
    
    if len(critical_missing) > 0:
        print("Critical variables with missing data:")
        print(critical_missing.to_string(index=False))
    else:
        print("No missing data in critical variables")
    
    return missing_summary

fixation_missing = check_missing(merged_fixation_data, "Fixation Data")
interest_area_missing = check_missing(merged_interest_area_data, "Interest Area Data")
saccade_missing = check_missing(merged_saccade_data, "Saccade Data")
trial_missing = check_missing(merged_trial_data, "Trial Data")

# Save missing data reports
fixation_missing.to_csv("results/data_quality/fixation_missing_data.csv", index=False)
interest_area_missing.to_csv("results/data_quality/interest_area_missing_data.csv", index=False)
saccade_missing.to_csv("results/data_quality/saccade_missing_data.csv", index=False)
trial_missing.to_csv("results/data_quality/trial_missing_data.csv", index=False)

# %% Identify outliers in fixation duration
print("\nIdentifying outliers in fixation duration...")

# Calculate IQR bounds once (not per row)
fixation_filtered = merged_fixation_data[merged_fixation_data['CURRENT_FIX_DURATION'].notna()].copy()

if len(fixation_filtered) > 0:
    q1 = fixation_filtered['CURRENT_FIX_DURATION'].quantile(0.25)
    q3 = fixation_filtered['CURRENT_FIX_DURATION'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 3 * iqr  # Using 3*IQR for more conservative detection
    upper_bound = q3 + 3 * iqr
    
    fixation_filtered['is_outlier'] = (
        (fixation_filtered['CURRENT_FIX_DURATION'] < lower_bound) | 
        (fixation_filtered['CURRENT_FIX_DURATION'] > upper_bound)
    )
    fixation_outliers = fixation_filtered[fixation_filtered['is_outlier']].copy()
else:
    fixation_outliers = fixation_filtered.copy()

outlier_pct = (100 * len(fixation_outliers) / len(merged_fixation_data)) if len(merged_fixation_data) > 0 else 0
print(f"Fixation duration outliers: {len(fixation_outliers)} ({outlier_pct:.2f}%)")

# Check for impossible values (negative durations, extremely long durations)
impossible_fixations = merged_fixation_data[
    (merged_fixation_data['CURRENT_FIX_DURATION'] < 0) | 
    (merged_fixation_data['CURRENT_FIX_DURATION'] > 5000) |  # > 5 seconds is likely an error
    (merged_fixation_data['CURRENT_FIX_X'] < 0) | 
    (merged_fixation_data['CURRENT_FIX_X'] > 2000) |  # Assuming reasonable screen bounds
    (merged_fixation_data['CURRENT_FIX_Y'] < 0) | 
    (merged_fixation_data['CURRENT_FIX_Y'] > 2000)
].copy()

print(f"Impossible fixation values: {len(impossible_fixations)}")

# %% Identify outliers in saccade metrics
print("\nIdentifying outliers in saccade metrics...")

# Calculate IQR bounds once (not per row)
saccade_filtered = merged_saccade_data[merged_saccade_data['CURRENT_SAC_AMPLITUDE'].notna()].copy()

if len(saccade_filtered) > 0:
    q1 = saccade_filtered['CURRENT_SAC_AMPLITUDE'].quantile(0.25)
    q3 = saccade_filtered['CURRENT_SAC_AMPLITUDE'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 3 * iqr
    upper_bound = q3 + 3 * iqr
    
    saccade_filtered['is_outlier'] = (
        (saccade_filtered['CURRENT_SAC_AMPLITUDE'] < lower_bound) | 
        (saccade_filtered['CURRENT_SAC_AMPLITUDE'] > upper_bound)
    )
    saccade_outliers = saccade_filtered[saccade_filtered['is_outlier']].copy()
else:
    saccade_outliers = saccade_filtered.copy()

outlier_pct_sac = (100 * len(saccade_outliers) / len(merged_saccade_data)) if len(merged_saccade_data) > 0 else 0
print(f"Saccade amplitude outliers: {len(saccade_outliers)} ({outlier_pct_sac:.2f}%)")

# Check for impossible saccade values
impossible_saccades = merged_saccade_data[
    (merged_saccade_data['CURRENT_SAC_AMPLITUDE'] < 0) | 
    (merged_saccade_data['CURRENT_SAC_AMPLITUDE'] > 2000) |  # > 20 degrees is extreme
    (merged_saccade_data['CURRENT_SAC_DURATION'] < 0) | 
    (merged_saccade_data['CURRENT_SAC_DURATION'] > 500) |
    (merged_saccade_data['CURRENT_SAC_AVG_VELOCITY'] < 0) | 
    (merged_saccade_data['CURRENT_SAC_AVG_VELOCITY'] > 1000)
].copy()

print(f"Impossible saccade values: {len(impossible_saccades)}")

# %% Validate voice type encoding consistency
print("\nValidating voice type encoding...")

# Check if voice_id is consistent across datasets for same trials
voice_consistency = merged_trial_data.groupby(['participant_id', 'TRIAL_INDEX', 'sentence'])['voice_id'].nunique().reset_index()
voice_consistency.columns = ['participant_id', 'TRIAL_INDEX', 'sentence', 'unique_voice_ids']
voice_consistency = voice_consistency[voice_consistency['unique_voice_ids'] > 1]

if len(voice_consistency) > 0:
    print(f"Warning: {len(voice_consistency)} trials have inconsistent voice_id values")
else:
    print("Voice ID encoding is consistent")

# Check for missing voice_id
missing_voice = merged_trial_data[
    merged_trial_data['voice_id'].isna() | 
    (merged_trial_data['voice_id'] == "") | 
    (merged_trial_data['voice_id'] == "UNDEFINEDnull")
].copy()

print(f"Trials with missing/invalid voice_id: {len(missing_voice)}")

# %% Create data quality report
print("\nCreating data quality report...")

quality_report = pd.DataFrame({
    'check': [
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
    ],
    'count': [
        len(merged_fixation_data),
        len(fixation_outliers),
        len(impossible_fixations),
        len(merged_interest_area_data),
        len(merged_saccade_data),
        len(saccade_outliers),
        len(impossible_saccades),
        len(voice_consistency),
        len(missing_voice),
        merged_trial_data['participant_id'].nunique(),
        len(merged_trial_data)
    ],
    'percentage': [
        100,
        round(100 * len(fixation_outliers) / len(merged_fixation_data), 2) if len(merged_fixation_data) > 0 else 0,
        round(100 * len(impossible_fixations) / len(merged_fixation_data), 2) if len(merged_fixation_data) > 0 else 0,
        100,
        100,
        round(100 * len(saccade_outliers) / len(merged_saccade_data), 2) if len(merged_saccade_data) > 0 else 0,
        round(100 * len(impossible_saccades) / len(merged_saccade_data), 2) if len(merged_saccade_data) > 0 else 0,
        round(100 * len(voice_consistency) / len(merged_trial_data), 2) if len(merged_trial_data) > 0 else 0,
        round(100 * len(missing_voice) / len(merged_trial_data), 2) if len(merged_trial_data) > 0 else 0,
        100,
        100
    ]
})

quality_report.to_csv("results/data_quality/data_quality_report.csv", index=False)

# Save outlier records for review
if 'is_outlier' in fixation_outliers.columns:
    fixation_outliers.drop('is_outlier', axis=1).to_csv("results/data_quality/fixation_outliers.csv", index=False)
else:
    fixation_outliers.to_csv("results/data_quality/fixation_outliers.csv", index=False)

if 'is_outlier' in saccade_outliers.columns:
    saccade_outliers.drop('is_outlier', axis=1).to_csv("results/data_quality/saccade_outliers.csv", index=False)
else:
    saccade_outliers.to_csv("results/data_quality/saccade_outliers.csv", index=False)

impossible_fixations.to_csv("results/data_quality/impossible_fixations.csv", index=False)
impossible_saccades.to_csv("results/data_quality/impossible_saccades.csv", index=False)

# %% Create exclusion flags
print("\nCreating exclusion flags...")

# Add exclusion flags to datasets
merged_fixation_data['exclude_fixation'] = (
    (merged_fixation_data['CURRENT_FIX_DURATION'] < 0) | 
    (merged_fixation_data['CURRENT_FIX_DURATION'] > 5000) |
    (merged_fixation_data['CURRENT_FIX_X'] < 0) | 
    (merged_fixation_data['CURRENT_FIX_X'] > 2000) |
    (merged_fixation_data['CURRENT_FIX_Y'] < 0) | 
    (merged_fixation_data['CURRENT_FIX_Y'] > 2000)
)

merged_saccade_data['exclude_saccade'] = (
    (merged_saccade_data['CURRENT_SAC_AMPLITUDE'] < 0) | 
    (merged_saccade_data['CURRENT_SAC_AMPLITUDE'] > 2000) |
    (merged_saccade_data['CURRENT_SAC_DURATION'] < 0) | 
    (merged_saccade_data['CURRENT_SAC_DURATION'] > 500) |
    (merged_saccade_data['CURRENT_SAC_AVG_VELOCITY'] < 0) | 
    (merged_saccade_data['CURRENT_SAC_AVG_VELOCITY'] > 1000)
)

merged_trial_data['exclude_trial'] = (
    merged_trial_data['voice_id'].isna() | 
    (merged_trial_data['voice_id'] == "") | 
    (merged_trial_data['voice_id'] == "UNDEFINEDnull")
)

# Save datasets with exclusion flags
merged_fixation_data.to_csv("data/processed/merged_fixation_data_with_flags.csv", index=False)
merged_saccade_data.to_csv("data/processed/merged_saccade_data_with_flags.csv", index=False)
merged_trial_data.to_csv("data/processed/merged_trial_data_with_flags.csv", index=False)

# %% Print summary
print("\n=== Data Quality Summary ===")
print(quality_report.to_string(index=False))
print("\nData quality checks complete!")
print("Reports saved to results/data_quality/")

