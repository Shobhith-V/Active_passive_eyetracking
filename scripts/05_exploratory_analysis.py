# %% Exploratory Data Analysis
# Script: 05_exploratory_analysis.py
# Purpose: Summary statistics and initial data exploration

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set working directory
if not os.path.exists("scripts"):
    os.chdir("..")

# Create output directories
os.makedirs("plots/exploratory", exist_ok=True)
os.makedirs("results/exploratory", exist_ok=True)

# Set matplotlib style
plt.style.use('default')
sns.set_palette("husl")

# Load data with exclusion flags
print("Loading data...")
merged_fixation_data = pd.read_csv("data/processed/merged_fixation_data_with_flags.csv")
merged_interest_area_data = pd.read_csv("data/processed/merged_interest_area_data.csv")
merged_saccade_data = pd.read_csv("data/processed/merged_saccade_data_with_flags.csv")
merged_trial_data = pd.read_csv("data/processed/merged_trial_data_with_flags.csv")

# Filter out excluded data
fixation_clean = merged_fixation_data[~merged_fixation_data['exclude_fixation']].copy()
saccade_clean = merged_saccade_data[~merged_saccade_data['exclude_saccade']].copy()
trial_clean = merged_trial_data[~merged_trial_data['exclude_trial']].copy()

# %% Summary Statistics by Voice Type
print("Calculating summary statistics by voice type...")

# Note: voice_type may need to be extracted from voice_id or other variables
# For now, we'll use voice_id as a proxy if voice_type doesn't exist
if "voice_type" not in trial_clean.columns:
    # Create a placeholder - this should be adjusted based on actual data
    trial_clean['voice_type'] = "unknown"
    fixation_clean['voice_type'] = "unknown"
    saccade_clean['voice_type'] = "unknown"

# Fixation duration summary by voice type and AOI
fixation_summary = fixation_clean.groupby(['voice_type', 'aoi_type']).agg({
    'CURRENT_FIX_DURATION': ['count', 'mean', 'median', 'std', 'min', 'max']
}).reset_index()

fixation_summary.columns = ['voice_type', 'aoi_type', 'n', 'mean_duration', 
                            'median_duration', 'sd_duration', 'min_duration', 'max_duration']

fixation_summary.to_csv("results/exploratory/fixation_summary_by_voice_aoi.csv", index=False)

# Dwell time summary by voice type and AOI
dwell_time_summary = merged_interest_area_data[
    (merged_interest_area_data['IA_LABEL'] != "") & 
    merged_interest_area_data['IA_LABEL'].notna()
].groupby(['voice_id', 'aoi_type']).agg({
    'IA_DWELL_TIME': ['count', 'mean', 'median', 'std']
}).reset_index()

dwell_time_summary.columns = ['voice_id', 'aoi_type', 'n', 'mean_dwell_time', 
                              'median_dwell_time', 'sd_dwell_time']

dwell_time_summary.to_csv("results/exploratory/dwell_time_summary_by_voice_aoi.csv", index=False)

# Saccade summary by voice type
saccade_summary = saccade_clean.groupby('voice_type').agg({
    'CURRENT_SAC_AMPLITUDE': ['count', 'mean'],
    'CURRENT_SAC_DURATION': 'mean',
    'CURRENT_SAC_AVG_VELOCITY': 'mean'
}).reset_index()

saccade_summary.columns = ['voice_type', 'n', 'mean_amplitude', 'mean_duration', 'mean_velocity']

saccade_summary.to_csv("results/exploratory/saccade_summary_by_voice.csv", index=False)

# %% Distribution plots for key dependent variables
print("Creating distribution plots...")

# Fixation duration distribution
plt.figure(figsize=(8, 5))
plt.hist(fixation_clean['CURRENT_FIX_DURATION'], bins=50, color='skyblue', edgecolor='black', alpha=0.6)
plt.title("Distribution of Fixation Duration")
plt.xlabel("Fixation Duration (ms)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("plots/exploratory/fixation_duration_distribution.png", dpi=300)
plt.close()

# Fixation duration by voice type and AOI
fixation_clean_aoi = fixation_clean[fixation_clean['aoi_type'].notna()].copy()
if len(fixation_clean_aoi) > 0:
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=fixation_clean_aoi, x='voice_type', y='CURRENT_FIX_DURATION', hue='aoi_type')
    plt.title("Fixation Duration by Voice Type and AOI")
    plt.xlabel("Voice Type")
    plt.ylabel("Fixation Duration (ms)")
    plt.legend(title="AOI Type")
    plt.tight_layout()
    plt.savefig("plots/exploratory/fixation_duration_by_voice_aoi.png", dpi=300)
    plt.close()

# Dwell time distribution
dwell_data = merged_interest_area_data[merged_interest_area_data['IA_DWELL_TIME'].notna()].copy()
if len(dwell_data) > 0:
    plt.figure(figsize=(8, 5))
    plt.hist(dwell_data['IA_DWELL_TIME'], bins=50, color='lightgreen', edgecolor='black', alpha=0.6)
    plt.title("Distribution of Dwell Time")
    plt.xlabel("Dwell Time (ms)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig("plots/exploratory/dwell_time_distribution.png", dpi=300)
    plt.close()

# Saccade amplitude distribution
plt.figure(figsize=(8, 5))
plt.hist(saccade_clean['CURRENT_SAC_AMPLITUDE'], bins=50, color='salmon', edgecolor='black', alpha=0.6)
plt.title("Distribution of Saccade Amplitude")
plt.xlabel("Saccade Amplitude (degrees)")
plt.ylabel("Frequency")
plt.tight_layout()
plt.savefig("plots/exploratory/saccade_amplitude_distribution.png", dpi=300)
plt.close()

# %% AOI-specific summaries
print("Creating AOI-specific summaries...")

aoi_summary = fixation_clean[fixation_clean['aoi_type'].notna()].groupby(['voice_type', 'aoi_type']).agg({
    'CURRENT_FIX_DURATION': ['count', 'sum', 'mean']
}).reset_index()

aoi_summary.columns = ['voice_type', 'aoi_type', 'total_fixations', 'total_duration', 'mean_duration']

# Calculate percentages
aoi_summary = aoi_summary.groupby('voice_type').apply(
    lambda x: x.assign(
        pct_fixations=100 * x['total_fixations'] / x['total_fixations'].sum(),
        pct_duration=100 * x['total_duration'] / x['total_duration'].sum()
    )
).reset_index(drop=True)

aoi_summary.to_csv("results/exploratory/aoi_summary.csv", index=False)

# %% Participant-level variability
print("Calculating participant-level variability...")

participant_variability = fixation_clean.groupby(['participant_id', 'voice_type', 'aoi_type']).agg({
    'CURRENT_FIX_DURATION': 'mean'
}).reset_index()

participant_variability.columns = ['participant_id', 'voice_type', 'aoi_type', 'mean_fixation_duration']

participant_variability = participant_variability.groupby(['voice_type', 'aoi_type']).agg({
    'mean_fixation_duration': ['count', 'mean', 'std']
}).reset_index()

participant_variability.columns = ['voice_type', 'aoi_type', 'n_participants', 
                                   'mean_across_participants', 'sd_across_participants']

participant_variability.to_csv("results/exploratory/participant_variability.csv", index=False)

# %% Print summary
print("\n=== Exploratory Analysis Summary ===")
print("Summary statistics saved to results/exploratory/")
print("Plots saved to plots/exploratory/")
print("\nExploratory analysis complete!")

