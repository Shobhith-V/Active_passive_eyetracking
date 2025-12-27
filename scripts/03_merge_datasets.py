# %% Data Merging
# Script: 03_merge_datasets.py
# Purpose: Merge fixation, interest_area, and saccade data by participant and trial

import pandas as pd
import numpy as np
import os

# Set working directory
if not os.path.exists("scripts"):
    os.chdir("..")

# Load processed data
print("Loading processed data...")
fixation_data = pd.read_csv("data/processed/fixation_with_variables.csv")
interest_area_data = pd.read_csv("data/processed/interest_area_with_variables.csv")
saccade_data = pd.read_csv("data/processed/saccade_with_variables.csv")

trial_fixation_summary = pd.read_csv("data/processed/trial_fixation_summary.csv")
trial_summary = pd.read_csv("data/processed/trial_summary.csv")
trial_saccade_summary = pd.read_csv("data/processed/trial_saccade_summary.csv")

# %% Create common trial identifiers
# Ensure all datasets have consistent trial identifiers
fixation_data['merge_key'] = (
    fixation_data['participant_id'].astype(str) + "|" + 
    fixation_data['TRIAL_INDEX'].astype(str) + "|" + 
    fixation_data['sentence'].astype(str)
)

interest_area_data['merge_key'] = (
    interest_area_data['participant_id'].astype(str) + "|" + 
    interest_area_data['TRIAL_INDEX'].astype(str) + "|" + 
    interest_area_data['sentence'].astype(str)
)

saccade_data['merge_key'] = (
    saccade_data['participant_id'].astype(str) + "|" + 
    saccade_data['TRIAL_INDEX'].astype(str) + "|" + 
    saccade_data['sentence'].astype(str)
)

trial_summary['merge_key'] = (
    trial_summary['participant_id'].astype(str) + "|" + 
    trial_summary['TRIAL_INDEX'].astype(str) + "|" + 
    trial_summary['sentence'].astype(str)
)

# %% Merge trial-level summaries
print("Merging trial-level summaries...")

# Start with trial summary as base
merged_trial_data = trial_summary.copy()

# Merge saccade summary
saccade_cols = ['participant_id', 'TRIAL_INDEX', 'sentence', 'n_saccades', 
                'mean_saccade_amplitude', 'mean_saccade_duration', 
                'mean_saccade_velocity', 'mean_peak_velocity']
saccade_cols = [col for col in saccade_cols if col in trial_saccade_summary.columns]

merged_trial_data = merged_trial_data.merge(
    trial_saccade_summary[saccade_cols],
    on=['participant_id', 'TRIAL_INDEX', 'sentence'],
    how='left'
)

# Add AOI-specific fixation summaries (pivot wider)
pivot_cols = ['participant_id', 'TRIAL_INDEX', 'sentence', 'aoi_type', 
              'total_fixation_duration', 'n_fixations', 'mean_fixation_duration', 
              'time_to_first_fixation']
pivot_cols = [col for col in pivot_cols if col in trial_fixation_summary.columns]

trial_fixation_pivot = trial_fixation_summary[pivot_cols].copy()

# Pivot the data
value_cols = ['total_fixation_duration', 'n_fixations', 'mean_fixation_duration', 'time_to_first_fixation']
value_cols = [col for col in value_cols if col in trial_fixation_pivot.columns]

if 'aoi_type' in trial_fixation_pivot.columns and len(value_cols) > 0:
    trial_fixation_wide = trial_fixation_pivot.pivot_table(
        index=['participant_id', 'TRIAL_INDEX', 'sentence'],
        columns='aoi_type',
        values=value_cols,
        aggfunc='first'
    )
    
    # Flatten column names
    trial_fixation_wide.columns = ['_'.join([str(col[0]), str(col[1])]) if col[1] else str(col[0])
                                   for col in trial_fixation_wide.columns]
    trial_fixation_wide = trial_fixation_wide.reset_index()
    
    merged_trial_data = merged_trial_data.merge(
        trial_fixation_wide,
        on=['participant_id', 'TRIAL_INDEX', 'sentence'],
        how='left'
    )

# %% Create hierarchical merged dataset at fixation level
print("Creating hierarchical merged dataset...")

# Merge fixation data with trial-level information
trial_summary_cols = ['participant_id', 'TRIAL_INDEX', 'sentence', 
                      'total_trial_duration', 'trial_duration']
trial_summary_cols = [col for col in trial_summary_cols if col in trial_summary.columns]

merged_fixation_data = fixation_data.merge(
    trial_summary[trial_summary_cols],
    on=['participant_id', 'TRIAL_INDEX', 'sentence'],
    how='left'
)

saccade_summary_cols = ['participant_id', 'TRIAL_INDEX', 'sentence', 
                        'n_saccades', 'mean_saccade_amplitude']
saccade_summary_cols = [col for col in saccade_summary_cols if col in trial_saccade_summary.columns]

merged_fixation_data = merged_fixation_data.merge(
    trial_saccade_summary[saccade_summary_cols],
    on=['participant_id', 'TRIAL_INDEX', 'sentence'],
    how='left'
)

# %% Create hierarchical merged dataset at interest area level
merged_interest_area_data = interest_area_data.merge(
    trial_summary[trial_summary_cols],
    on=['participant_id', 'TRIAL_INDEX', 'sentence'],
    how='left'
)

merged_interest_area_data = merged_interest_area_data.merge(
    trial_saccade_summary[['participant_id', 'TRIAL_INDEX', 'sentence', 'n_saccades']],
    on=['participant_id', 'TRIAL_INDEX', 'sentence'],
    how='left'
)

# %% Create hierarchical merged dataset at saccade level
merged_saccade_data = saccade_data.merge(
    trial_summary[trial_summary_cols],
    on=['participant_id', 'TRIAL_INDEX', 'sentence'],
    how='left'
)

# Calculate total fixations for subject/object AOIs
subject_object_fixations = trial_fixation_summary[
    trial_fixation_summary['aoi_type'].isin(['subject', 'object'])
].groupby(['participant_id', 'TRIAL_INDEX', 'sentence'])['n_fixations'].sum().reset_index()
subject_object_fixations.columns = ['participant_id', 'TRIAL_INDEX', 'sentence', 
                                     'total_fixations_subject_object']

merged_saccade_data = merged_saccade_data.merge(
    subject_object_fixations,
    on=['participant_id', 'TRIAL_INDEX', 'sentence'],
    how='left'
)

# %% Validate merge integrity
print("Validating merge integrity...")

# Check for missing matches
fixation_missing = merged_fixation_data['total_trial_duration'].isna().sum()
interest_area_missing = merged_interest_area_data['total_trial_duration'].isna().sum()
saccade_missing = merged_saccade_data['total_trial_duration'].isna().sum()

print(f"Fixation records without trial match: {fixation_missing}")
print(f"Interest area records without trial match: {interest_area_missing}")
print(f"Saccade records without trial match: {saccade_missing}")

# Check for duplicate merge keys
duplicate_trials = merged_trial_data.groupby(['participant_id', 'TRIAL_INDEX', 'sentence']).size().reset_index(name='n')
duplicate_trials = duplicate_trials[duplicate_trials['n'] > 1]

if len(duplicate_trials) > 0:
    print(f"Warning: {len(duplicate_trials)} duplicate trial entries found")
else:
    print("No duplicate trial entries found")

# %% Save merged datasets
print("Saving merged datasets...")

merged_trial_data.to_csv("data/processed/merged_trial_data.csv", index=False)
merged_fixation_data.to_csv("data/processed/merged_fixation_data.csv", index=False)
merged_interest_area_data.to_csv("data/processed/merged_interest_area_data.csv", index=False)
merged_saccade_data.to_csv("data/processed/merged_saccade_data.csv", index=False)

# Also save a comprehensive merged dataset
print("Creating comprehensive merged dataset...")

comprehensive_data = merged_trial_data.copy()
comprehensive_data['data_level'] = "trial"

comprehensive_data.to_csv("data/processed/merged_data.csv", index=False)

print("\n=== Merge Summary ===")
print(f"Merged trial records: {len(merged_trial_data)}")
print(f"Merged fixation records: {len(merged_fixation_data)}")
print(f"Merged interest area records: {len(merged_interest_area_data)}")
print(f"Merged saccade records: {len(merged_saccade_data)}")
print("\nData merging complete!")

