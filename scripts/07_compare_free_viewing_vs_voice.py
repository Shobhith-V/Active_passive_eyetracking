# %% Compare Free Viewing vs Voice Conditions
# Script: 07_compare_free_viewing_vs_voice.py
# Purpose: Compare free viewing (baseline) data with voice conditions

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats

# Set working directory
if not os.path.exists("scripts"):
    os.chdir("..")

# Create output directories
os.makedirs("results/comparisons", exist_ok=True)
os.makedirs("plots/comparisons", exist_ok=True)

print("Comparing Free Viewing (Baseline) vs Voice Conditions...")

# Load data
print("Loading data...")
merged_fixation_data = pd.read_csv("data/processed/merged_fixation_data_with_flags.csv")
merged_trial_data = pd.read_csv("data/processed/merged_trial_data_with_flags.csv")
merged_saccade_data = pd.read_csv("data/processed/merged_saccade_data_with_flags.csv")

# Filter clean data
fixation_clean = merged_fixation_data[~merged_fixation_data['exclude_fixation']].copy()
trial_clean = merged_trial_data[~merged_trial_data['exclude_trial']].copy()
saccade_clean = merged_saccade_data[~merged_saccade_data['exclude_saccade']].copy()

# Create condition variable: Free Viewing vs Voice
print("Creating condition labels...")

def create_condition(row):
    """Create condition label: Free Viewing (baseline) or Voice."""
    if pd.isna(row.get('voice_id')) or row.get('voice_id') == "" or row.get('voice_id') == "UNDEFINEDnull":
        return "Free Viewing"
    else:
        return "Voice"

# Apply to all datasets
fixation_clean['condition'] = fixation_clean.apply(create_condition, axis=1)
trial_clean['condition'] = trial_clean.apply(create_condition, axis=1)
saccade_clean['condition'] = saccade_clean.apply(create_condition, axis=1)

# Get unique voice_id values for voice condition
voice_ids = fixation_clean[fixation_clean['condition'] == 'Voice']['voice_id'].dropna().unique()
print(f"\nFound {len(voice_ids)} unique voice IDs in voice condition")
print(f"Free viewing trials: {len(trial_clean[trial_clean['condition'] == 'Free Viewing'])}")
print(f"Voice trials: {len(trial_clean[trial_clean['condition'] == 'Voice'])}")

# 1. FIXATION DURATION COMPARISON
print("\n" + "="*80)
print("1. FIXATION DURATION COMPARISON")
print("="*80)

fixation_comparison = fixation_clean.groupby(['condition', 'aoi_type'])['CURRENT_FIX_DURATION'].agg([
    'count', 'mean', 'median', 'std', 
    lambda x: np.percentile(x, 25), 
    lambda x: np.percentile(x, 75)
]).round(2)

fixation_comparison.columns = ['n', 'mean', 'median', 'std', 'q25', 'q75']
fixation_comparison = fixation_comparison.reset_index()

print("\nFixation Duration by Condition and AOI Type:")
print(fixation_comparison.to_string(index=False))

# Save comparison
fixation_comparison.to_csv("results/comparisons/fixation_duration_comparison.csv", index=False)

# Statistical tests
print("\nStatistical Tests (Free Viewing vs Voice):")

comparison_results = []

for aoi in fixation_clean['aoi_type'].dropna().unique():
    free_viewing = fixation_clean[
        (fixation_clean['condition'] == 'Free Viewing') & 
        (fixation_clean['aoi_type'] == aoi)
    ]['CURRENT_FIX_DURATION'].dropna()
    
    voice = fixation_clean[
        (fixation_clean['condition'] == 'Voice') & 
        (fixation_clean['aoi_type'] == aoi)
    ]['CURRENT_FIX_DURATION'].dropna()
    
    if len(free_viewing) > 0 and len(voice) > 0:
        # Mann-Whitney U test (non-parametric)
        statistic, p_value = stats.mannwhitneyu(free_viewing, voice, alternative='two-sided')
        
        # Effect size (Cohen's d)
        pooled_std = np.sqrt((free_viewing.std()**2 + voice.std()**2) / 2)
        cohens_d = (voice.mean() - free_viewing.mean()) / pooled_std if pooled_std > 0 else 0
        
        comparison_results.append({
            'aoi_type': aoi,
            'free_viewing_mean': free_viewing.mean(),
            'voice_mean': voice.mean(),
            'difference': voice.mean() - free_viewing.mean(),
            'percent_change': ((voice.mean() - free_viewing.mean()) / free_viewing.mean() * 100) if free_viewing.mean() > 0 else 0,
            'mannwhitney_u': statistic,
            'p_value': p_value,
            'cohens_d': cohens_d,
            'n_free_viewing': len(free_viewing),
            'n_voice': len(voice)
        })
        
        print(f"\nAOI: {aoi}")
        print(f"  Free Viewing: M={free_viewing.mean():.2f}, SD={free_viewing.std():.2f}, n={len(free_viewing)}")
        print(f"  Voice: M={voice.mean():.2f}, SD={voice.std():.2f}, n={len(voice)}")
        print(f"  Difference: {voice.mean() - free_viewing.mean():.2f} ms ({((voice.mean() - free_viewing.mean()) / free_viewing.mean() * 100):.1f}%)")
        print(f"  Mann-Whitney U: {statistic:.2f}, p={p_value:.4f}")
        print(f"  Cohen's d: {cohens_d:.3f}")
        if p_value < 0.001:
            print(f"  Significance: *** p < 0.001")
        elif p_value < 0.01:
            print(f"  Significance: ** p < 0.01")
        elif p_value < 0.05:
            print(f"  Significance: * p < 0.05")
        else:
            print(f"  Significance: ns (p >= 0.05)")

statistical_comparison = pd.DataFrame(comparison_results)
statistical_comparison.to_csv("results/comparisons/fixation_statistical_comparison.csv", index=False)

# 2. DWELL TIME COMPARISON (if available)
print("\n" + "="*80)
print("2. DWELL TIME COMPARISON")
print("="*80)

# Load interest area data if available
try:
    merged_interest_area_data = pd.read_csv("data/processed/merged_interest_area_data.csv")
    interest_area_clean = merged_interest_area_data[
        merged_interest_area_data['IA_DWELL_TIME'].notna() & 
        (merged_interest_area_data['IA_DWELL_TIME'] > 0)
    ].copy()
    
    interest_area_clean['condition'] = interest_area_clean.apply(create_condition, axis=1)
    
    dwell_time_comparison = interest_area_clean.groupby(['condition', 'aoi_type'])['IA_DWELL_TIME'].agg([
        'count', 'mean', 'median', 'std'
    ]).round(2)
    
    dwell_time_comparison.columns = ['n', 'mean', 'median', 'std']
    dwell_time_comparison = dwell_time_comparison.reset_index()
    
    print("\nDwell Time by Condition and AOI Type:")
    print(dwell_time_comparison.to_string(index=False))
    
    dwell_time_comparison.to_csv("results/comparisons/dwell_time_comparison.csv", index=False)
    
    # Statistical tests for dwell time
    dwell_time_results = []
    for aoi in interest_area_clean['aoi_type'].dropna().unique():
        free_viewing = interest_area_clean[
            (interest_area_clean['condition'] == 'Free Viewing') & 
            (interest_area_clean['aoi_type'] == aoi)
        ]['IA_DWELL_TIME'].dropna()
        
        voice = interest_area_clean[
            (interest_area_clean['condition'] == 'Voice') & 
            (interest_area_clean['aoi_type'] == aoi)
        ]['IA_DWELL_TIME'].dropna()
        
        if len(free_viewing) > 0 and len(voice) > 0:
            statistic, p_value = stats.mannwhitneyu(free_viewing, voice, alternative='two-sided')
            pooled_std = np.sqrt((free_viewing.std()**2 + voice.std()**2) / 2)
            cohens_d = (voice.mean() - free_viewing.mean()) / pooled_std if pooled_std > 0 else 0
            
            dwell_time_results.append({
                'aoi_type': aoi,
                'free_viewing_mean': free_viewing.mean(),
                'voice_mean': voice.mean(),
                'difference': voice.mean() - free_viewing.mean(),
                'percent_change': ((voice.mean() - free_viewing.mean()) / free_viewing.mean() * 100) if free_viewing.mean() > 0 else 0,
                'p_value': p_value,
                'cohens_d': cohens_d,
                'n_free_viewing': len(free_viewing),
                'n_voice': len(voice)
            })
    
    dwell_time_stats = pd.DataFrame(dwell_time_results)
    dwell_time_stats.to_csv("results/comparisons/dwell_time_statistical_comparison.csv", index=False)
    
except Exception as e:
    print(f"Could not load interest area data: {e}")

# 3. SACCADE COMPARISON
print("\n" + "="*80)
print("3. SACCADE COMPARISON")
print("="*80)

saccade_comparison = saccade_clean.groupby('condition').agg({
    'CURRENT_SAC_AMPLITUDE': ['count', 'mean', 'median', 'std'],
    'CURRENT_SAC_DURATION': ['mean', 'median', 'std'],
    'CURRENT_SAC_AVG_VELOCITY': ['mean', 'median', 'std']
}).round(2)

saccade_comparison.columns = ['_'.join(col).strip() for col in saccade_comparison.columns.values]
saccade_comparison = saccade_comparison.reset_index()

print("\nSaccade Metrics by Condition:")
print(saccade_comparison.to_string(index=False))

saccade_comparison.to_csv("results/comparisons/saccade_comparison.csv", index=False)

# Statistical tests for saccades
saccade_results = []

for metric in ['CURRENT_SAC_AMPLITUDE', 'CURRENT_SAC_DURATION', 'CURRENT_SAC_AVG_VELOCITY']:
    if metric in saccade_clean.columns:
        free_viewing = saccade_clean[
            saccade_clean['condition'] == 'Free Viewing'
        ][metric].dropna()
        
        voice = saccade_clean[
            saccade_clean['condition'] == 'Voice'
        ][metric].dropna()
        
        if len(free_viewing) > 0 and len(voice) > 0:
            statistic, p_value = stats.mannwhitneyu(free_viewing, voice, alternative='two-sided')
            pooled_std = np.sqrt((free_viewing.std()**2 + voice.std()**2) / 2)
            cohens_d = (voice.mean() - free_viewing.mean()) / pooled_std if pooled_std > 0 else 0
            
            saccade_results.append({
                'metric': metric,
                'free_viewing_mean': free_viewing.mean(),
                'voice_mean': voice.mean(),
                'difference': voice.mean() - free_viewing.mean(),
                'percent_change': ((voice.mean() - free_viewing.mean()) / free_viewing.mean() * 100) if free_viewing.mean() > 0 else 0,
                'p_value': p_value,
                'cohens_d': cohens_d,
                'n_free_viewing': len(free_viewing),
                'n_voice': len(voice)
            })

saccade_stats = pd.DataFrame(saccade_results)
saccade_stats.to_csv("results/comparisons/saccade_statistical_comparison.csv", index=False)

# 4. VISUALIZATIONS
print("\n" + "="*80)
print("4. CREATING VISUALIZATIONS")
print("="*80)

plt.style.use('default')
sns.set_palette("Set2")

# Fixation duration comparison plot
fig, axes = plt.subplots(1, 2, figsize=(14, 6))

# Box plot
fixation_plot_data = fixation_clean[fixation_clean['aoi_type'].notna()].copy()
sns.boxplot(data=fixation_plot_data, x='aoi_type', y='CURRENT_FIX_DURATION', 
            hue='condition', ax=axes[0])
axes[0].set_title('Fixation Duration: Free Viewing vs Voice by AOI Type')
axes[0].set_xlabel('AOI Type')
axes[0].set_ylabel('Fixation Duration (ms)')
axes[0].legend(title='Condition')

# Violin plot
sns.violinplot(data=fixation_plot_data, x='aoi_type', y='CURRENT_FIX_DURATION', 
               hue='condition', ax=axes[1], split=True)
axes[1].set_title('Fixation Duration Distribution: Free Viewing vs Voice')
axes[1].set_xlabel('AOI Type')
axes[1].set_ylabel('Fixation Duration (ms)')
axes[1].legend(title='Condition')

plt.tight_layout()
plt.savefig("plots/comparisons/fixation_duration_comparison.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved: plots/comparisons/fixation_duration_comparison.png")

# Saccade comparison plot
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

for idx, metric in enumerate(['CURRENT_SAC_AMPLITUDE', 'CURRENT_SAC_DURATION', 'CURRENT_SAC_AVG_VELOCITY']):
    if metric in saccade_clean.columns:
        sns.boxplot(data=saccade_clean, x='condition', y=metric, ax=axes[idx])
        axes[idx].set_title(f'{metric.replace("CURRENT_SAC_", "").replace("_", " ").title()}')
        axes[idx].set_xlabel('Condition')
        if 'AMPLITUDE' in metric:
            axes[idx].set_ylabel('Amplitude (degrees)')
        elif 'DURATION' in metric:
            axes[idx].set_ylabel('Duration (ms)')
        else:
            axes[idx].set_ylabel('Velocity (deg/s)')

plt.tight_layout()
plt.savefig("plots/comparisons/saccade_comparison.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved: plots/comparisons/saccade_comparison.png")

# 5. SUMMARY REPORT
print("\n" + "="*80)
print("5. GENERATING SUMMARY REPORT")
print("="*80)

summary_lines = []
summary_lines.append("="*80)
summary_lines.append("FREE VIEWING (BASELINE) vs VOICE CONDITION COMPARISON")
summary_lines.append("="*80)
summary_lines.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

summary_lines.append("CONDITION SUMMARY:")
summary_lines.append(f"  Free Viewing (Baseline) trials: {len(trial_clean[trial_clean['condition'] == 'Free Viewing'])}")
summary_lines.append(f"  Voice trials: {len(trial_clean[trial_clean['condition'] == 'Voice'])}")
summary_lines.append(f"  Free Viewing fixations: {len(fixation_clean[fixation_clean['condition'] == 'Free Viewing'])}")
summary_lines.append(f"  Voice fixations: {len(fixation_clean[fixation_clean['condition'] == 'Voice'])}")

summary_lines.append("\n" + "="*80)
summary_lines.append("KEY FINDINGS")
summary_lines.append("="*80 + "\n")

if not statistical_comparison.empty:
    summary_lines.append("Fixation Duration Comparisons:")
    for _, row in statistical_comparison.iterrows():
        direction = "longer" if row['difference'] > 0 else "shorter"
        sig = ""
        if row['p_value'] < 0.001:
            sig = "***"
        elif row['p_value'] < 0.01:
            sig = "**"
        elif row['p_value'] < 0.05:
            sig = "*"
        
        summary_lines.append(
            f"  {row['aoi_type']} AOI: Voice condition shows {abs(row['percent_change']):.1f}% "
            f"{direction} fixations ({row['difference']:.1f} ms) {sig}"
        )
        summary_lines.append(f"    Effect size (Cohen's d): {row['cohens_d']:.3f}")

if not saccade_stats.empty:
    summary_lines.append("\nSaccade Comparisons:")
    for _, row in saccade_stats.iterrows():
        metric_name = row['metric'].replace('CURRENT_SAC_', '').replace('_', ' ').title()
        direction = "higher" if row['difference'] > 0 else "lower"
        sig = ""
        if row['p_value'] < 0.001:
            sig = "***"
        elif row['p_value'] < 0.01:
            sig = "**"
        elif row['p_value'] < 0.05:
            sig = "*"
        
        summary_lines.append(
            f"  {metric_name}: Voice condition shows {abs(row['percent_change']):.1f}% "
            f"{direction} values {sig}"
        )

summary_text = "\n".join(summary_lines)

with open("results/comparisons/free_viewing_vs_voice_summary.txt", 'w', encoding='utf-8') as f:
    f.write(summary_text)

print("\n" + "="*80)
print("COMPARISON ANALYSIS COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  - results/comparisons/fixation_duration_comparison.csv")
print("  - results/comparisons/fixation_statistical_comparison.csv")
print("  - results/comparisons/saccade_comparison.csv")
print("  - results/comparisons/saccade_statistical_comparison.csv")
print("  - results/comparisons/free_viewing_vs_voice_summary.txt")
print("  - plots/comparisons/fixation_duration_comparison.png")
print("  - plots/comparisons/saccade_comparison.png")

