# %% Variable Extraction and Creation
# Script: 02_create_analysis_variables.py
# Purpose: Extract voice type, create AOI categories, create trial-level aggregations

import pandas as pd
import numpy as np
import re
import os

# Set working directory
if not os.path.exists("scripts"):
    os.chdir("..")

# Load cleaned data
print("Loading cleaned data...")
fixation_data = pd.read_csv("data/processed/fixation_cleaned.csv")
interest_area_data = pd.read_csv("data/processed/interest_area_cleaned.csv")
saccade_data = pd.read_csv("data/processed/saccade_cleaned.csv")

# %% Extract voice type from voice_id or other variables
def extract_voice_type(df):
    """
    Extract voice type from dataframe.
    This is a placeholder - adjust based on actual data structure.
    """
    if "voice_type" in df.columns:
        return df
    
    if "voice_id" in df.columns:
        df['voice_type'] = np.nan  # Placeholder - will be filled based on actual data
    
    return df

# %% Create AOI categories from interest area labels
def create_aoi_categories(label):
    """Create AOI category from label."""
    if pd.isna(label) or label == "" or label == ".":
        return "other"
    
    # Check if label starts with s_ (subject) or o_ (object)
    if isinstance(label, str) and label.startswith("s_"):
        return "subject"
    elif isinstance(label, str) and label.startswith("o_"):
        return "object"
    else:
        return "other"

# %% Process Fixation Data
print("Processing fixation data...")

fixation_data = fixation_data.copy()
fixation_data['aoi_type'] = fixation_data['CURRENT_FIX_INTEREST_AREA_LABEL'].apply(create_aoi_categories)
fixation_data['trial_id'] = fixation_data['participant_id'].astype(str) + "_" + fixation_data['TRIAL_INDEX'].astype(str)
fixation_data['time_from_trial_start'] = fixation_data['CURRENT_FIX_START'] - fixation_data['TRIAL_START_TIME']

# Calculate time windows per trial
def assign_time_window_group(df_group):
    """Calculate time window for a trial group."""
    trial_duration = df_group['CURRENT_FIX_END'].max() - df_group['CURRENT_FIX_START'].min()
    if trial_duration == 0:
        df_group['time_window'] = "early"
    else:
        time_from_start = df_group['time_from_trial_start']
        df_group['time_window'] = pd.cut(
            time_from_start,
            bins=[-np.inf, trial_duration / 3, 2 * trial_duration / 3, np.inf],
            labels=['early', 'middle', 'late']
        )
    df_group['trial_duration'] = trial_duration
    return df_group

fixation_data = fixation_data.groupby('trial_id', group_keys=False).apply(assign_time_window_group).reset_index(drop=True)

# %% Process Interest Area Data
print("Processing interest area data...")

interest_area_data = interest_area_data.copy()
interest_area_data['aoi_type'] = interest_area_data['IA_LABEL'].apply(create_aoi_categories)
interest_area_data['trial_id'] = interest_area_data['participant_id'].astype(str) + "_" + interest_area_data['TRIAL_INDEX'].astype(str)

# Ensure numeric columns are numeric
numeric_cols_ia = ['IA_DWELL_TIME', 'IA_FIXATION_COUNT', 'IA_FIRST_FIXATION_TIME']
for col in numeric_cols_ia:
    if col in interest_area_data.columns:
        interest_area_data[col] = pd.to_numeric(interest_area_data[col], errors='coerce')

# %% Process Saccade Data
print("Processing saccade data...")

saccade_data = saccade_data.copy()
saccade_data['aoi_type_start'] = saccade_data['CURRENT_SAC_START_INTEREST_AREA_LABEL'].apply(create_aoi_categories)
saccade_data['aoi_type_end'] = saccade_data['CURRENT_SAC_END_INTEREST_AREA_LABEL'].apply(create_aoi_categories)

# Create saccade transition type
def create_saccade_transition(row):
    """Create saccade transition type from start and end AOI types."""
    start = row['aoi_type_start']
    end = row['aoi_type_end']
    
    if start == "subject" and end == "object":
        return "subject_to_object"
    elif start == "object" and end == "subject":
        return "object_to_subject"
    elif start == "subject" and end == "subject":
        return "subject_to_subject"
    elif start == "object" and end == "object":
        return "object_to_object"
    else:
        return "other"

saccade_data['saccade_transition'] = saccade_data.apply(create_saccade_transition, axis=1)
saccade_data['trial_id'] = saccade_data['participant_id'].astype(str) + "_" + saccade_data['TRIAL_INDEX'].astype(str)
saccade_data['time_from_trial_start'] = saccade_data['CURRENT_SAC_START_TIME'] - saccade_data['TRIAL_START_TIME']

# %% Create Trial-Level Aggregations for Fixation Data
print("Creating trial-level aggregations for fixation data...")

group_cols = ['participant_id', 'trial_id', 'TRIAL_INDEX', 'aoi_type', 'sentence', 'voice_id', 'image_id', 'stim_id']
group_cols = [col for col in group_cols if col in fixation_data.columns]

trial_fixation_summary = fixation_data.groupby(group_cols).agg({
    'CURRENT_FIX_DURATION': ['sum', 'mean', 'median', 'count'],
    'CURRENT_FIX_START': 'min',
    'CURRENT_FIX_END': 'max'
}).reset_index()

trial_fixation_summary.columns = [
    col[0] if col[1] == '' else f"{col[0]}_{col[1]}" 
    for col in trial_fixation_summary.columns
]

trial_fixation_summary = trial_fixation_summary.rename(columns={
    'CURRENT_FIX_DURATION_sum': 'total_fixation_duration',
    'CURRENT_FIX_DURATION_count': 'n_fixations',
    'CURRENT_FIX_DURATION_mean': 'mean_fixation_duration',
    'CURRENT_FIX_DURATION_median': 'median_fixation_duration',
    'CURRENT_FIX_START_min': 'first_fixation_time',
    'CURRENT_FIX_END_max': 'last_fixation_time'
})

# Calculate time to first fixation on this AOI type
def add_time_to_first_fixation(group):
    """Add time_to_first_fixation to group."""
    group['time_to_first_fixation'] = group['first_fixation_time'] - group['first_fixation_time'].min()
    return group

trial_fixation_summary = trial_fixation_summary.groupby(['participant_id', 'trial_id'], group_keys=False).apply(add_time_to_first_fixation).reset_index(drop=True)

# Overall trial summary (across all AOIs)
group_cols_trial = ['participant_id', 'trial_id', 'TRIAL_INDEX', 'sentence', 'voice_id', 'image_id', 'stim_id']
group_cols_trial = [col for col in group_cols_trial if col in fixation_data.columns]

trial_summary = fixation_data.groupby(group_cols_trial).agg({
    'CURRENT_FIX_DURATION': ['sum', 'mean', 'count'],
    'CURRENT_FIX_START': 'min',
    'CURRENT_FIX_END': 'max'
}).reset_index()

trial_summary.columns = [
    col[0] if col[1] == '' else f"{col[0]}_{col[1]}" 
    for col in trial_summary.columns
]

trial_summary = trial_summary.rename(columns={
    'CURRENT_FIX_DURATION_count': 'total_trial_fixations',
    'CURRENT_FIX_DURATION_sum': 'total_trial_duration',
    'CURRENT_FIX_DURATION_mean': 'mean_fixation_duration',
    'CURRENT_FIX_START_min': 'trial_start_time',
    'CURRENT_FIX_END_max': 'trial_end_time'
})

trial_summary['trial_duration'] = trial_summary['trial_end_time'] - trial_summary['trial_start_time']

# %% Create Trial-Level Aggregations for Saccade Data
print("Creating trial-level aggregations for saccade data...")

group_cols_sac = ['participant_id', 'trial_id', 'TRIAL_INDEX', 'sentence', 'voice_id', 'image_id', 'stim_id']
group_cols_sac = [col for col in group_cols_sac if col in saccade_data.columns]

trial_saccade_summary = saccade_data.groupby(group_cols_sac).agg({
    'CURRENT_SAC_AMPLITUDE': 'mean',
    'CURRENT_SAC_DURATION': 'mean',
    'CURRENT_SAC_AVG_VELOCITY': 'mean',
    'CURRENT_SAC_PEAK_VELOCITY': 'mean',
    'CURRENT_SAC_INDEX': 'count'
}).reset_index()

trial_saccade_summary = trial_saccade_summary.rename(columns={
    'CURRENT_SAC_INDEX': 'n_saccades',
    'CURRENT_SAC_AMPLITUDE': 'mean_saccade_amplitude',
    'CURRENT_SAC_DURATION': 'mean_saccade_duration',
    'CURRENT_SAC_AVG_VELOCITY': 'mean_saccade_velocity',
    'CURRENT_SAC_PEAK_VELOCITY': 'mean_peak_velocity'
})

# Saccade transition summary
saccade_transition_summary = saccade_data[
    saccade_data['saccade_transition'].notna() & (saccade_data['saccade_transition'] != "other")
].groupby(['participant_id', 'trial_id', 'TRIAL_INDEX', 'saccade_transition', 'sentence', 'voice_id']).agg({
    'CURRENT_SAC_AMPLITUDE': 'mean',
    'CURRENT_SAC_DURATION': 'mean',
    'CURRENT_SAC_INDEX': 'count'  # Use a different column for count
}).reset_index()

saccade_transition_summary = saccade_transition_summary.rename(columns={
    'CURRENT_SAC_INDEX': 'n_transitions',
    'CURRENT_SAC_AMPLITUDE': 'mean_amplitude',
    'CURRENT_SAC_DURATION': 'mean_duration'
})

# %% Extract sentence-level variables
def extract_sentence_info(sentence_col):
    """Extract sentence info - placeholder function."""
    return sentence_col

# Add sentence info to all datasets
fixation_data['sentence_clean'] = extract_sentence_info(fixation_data['sentence'])
interest_area_data['sentence_clean'] = extract_sentence_info(interest_area_data['sentence'])
saccade_data['sentence_clean'] = extract_sentence_info(saccade_data['sentence'])

# %% Save processed data with new variables
print("Saving processed data...")

fixation_data.to_csv("data/processed/fixation_with_variables.csv", index=False)
interest_area_data.to_csv("data/processed/interest_area_with_variables.csv", index=False)
saccade_data.to_csv("data/processed/saccade_with_variables.csv", index=False)

# Save trial-level summaries
trial_fixation_summary.to_csv("data/processed/trial_fixation_summary.csv", index=False)
trial_summary.to_csv("data/processed/trial_summary.csv", index=False)
trial_saccade_summary.to_csv("data/processed/trial_saccade_summary.csv", index=False)
saccade_transition_summary.to_csv("data/processed/saccade_transition_summary.csv", index=False)

print("\n=== Variable Creation Summary ===")
print(f"Fixation records with variables: {len(fixation_data)}")
print(f"Interest area records with variables: {len(interest_area_data)}")
print(f"Saccade records with variables: {len(saccade_data)}")
print(f"Trial fixation summaries: {len(trial_fixation_summary)}")
print(f"Trial summaries: {len(trial_summary)}")
print(f"Trial saccade summaries: {len(trial_saccade_summary)}")
print("\nVariable creation complete!")

