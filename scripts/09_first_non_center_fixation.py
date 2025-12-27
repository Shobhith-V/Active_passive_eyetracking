# %% First Non-Center Fixation Analysis
# Script: 09_first_non_center_fixation.py
# Purpose: Find first fixation away from center and analyze which AOI is seen first

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
os.makedirs("results/first_non_center_fixation", exist_ok=True)
os.makedirs("plots/first_non_center_fixation", exist_ok=True)

print("Analyzing First Non-Center Fixation (Voice Condition)...")

# Load data
print("Loading data...")
merged_fixation_data = pd.read_csv("data/processed/merged_fixation_data_with_flags.csv")

# Filter clean data
fixation_clean = merged_fixation_data[~merged_fixation_data['exclude_fixation']].copy()

# Filter for Voice condition only (has voice_id)
voice_data = fixation_clean[
    fixation_clean['voice_id'].notna() & 
    (fixation_clean['voice_id'] != "") & 
    (fixation_clean['voice_id'] != "UNDEFINEDnull")
].copy()

print(f"\nTotal fixations in Voice condition: {len(voice_data)}")
print(f"Unique trials in Voice condition: {voice_data.groupby(['participant_id', 'TRIAL_INDEX']).ngroups}")

# Calculate screen center from all data
x_center = fixation_clean['CURRENT_FIX_X'].median()
y_center = fixation_clean['CURRENT_FIX_Y'].median()
print(f"\nEstimated screen center: X={x_center:.0f}, Y={y_center:.0f}")

# Define center threshold (e.g., within 100 pixels of center)
# We'll test different thresholds
thresholds = [50, 75, 100, 125, 150]

print("\n" + "="*80)
print("TESTING DIFFERENT CENTER THRESHOLDS")
print("="*80)

threshold_results = []

for threshold in thresholds:
    # Calculate distance from center for each fixation
    voice_data['distance_from_center'] = np.sqrt(
        (voice_data['CURRENT_FIX_X'] - x_center)**2 + 
        (voice_data['CURRENT_FIX_Y'] - y_center)**2
    )
    
    # Identify center fixations (within threshold)
    voice_data['is_center'] = voice_data['distance_from_center'] <= threshold
    
    # For each trial, find first non-center fixation
    grouping_cols = ['participant_id', 'TRIAL_INDEX']
    if 'image_id' in voice_data.columns:
        grouping_cols.append('image_id')
    
    first_non_center = []
    
    for name, group in voice_data.groupby(grouping_cols):
        # Sort by fixation start time
        group_sorted = group.sort_values('CURRENT_FIX_START')
        
        # Find first non-center fixation
        non_center_fixations = group_sorted[~group_sorted['is_center']]
        
        if len(non_center_fixations) > 0:
            first_non_center_fix = non_center_fixations.iloc[0]
            first_non_center.append({
                'participant_id': first_non_center_fix['participant_id'],
                'TRIAL_INDEX': first_non_center_fix['TRIAL_INDEX'],
                'image_id': first_non_center_fix.get('image_id', 'unknown'),
                'aoi_type': first_non_center_fix.get('aoi_type', 'unknown'),
                'CURRENT_FIX_X': first_non_center_fix['CURRENT_FIX_X'],
                'CURRENT_FIX_Y': first_non_center_fix['CURRENT_FIX_Y'],
                'distance_from_center': first_non_center_fix['distance_from_center'],
                'CURRENT_FIX_START': first_non_center_fix['CURRENT_FIX_START'],
                'CURRENT_FIX_DURATION': first_non_center_fix['CURRENT_FIX_DURATION'],
                'threshold': threshold
            })
    
    first_non_center_df = pd.DataFrame(first_non_center)
    
    if len(first_non_center_df) > 0:
        # Count AOI types
        aoi_counts = first_non_center_df['aoi_type'].value_counts()
        aoi_pct = first_non_center_df['aoi_type'].value_counts(normalize=True) * 100
        
        threshold_results.append({
            'threshold': threshold,
            'n_trials': len(first_non_center_df),
            'subject_count': aoi_counts.get('subject', 0),
            'subject_pct': aoi_pct.get('subject', 0),
            'object_count': aoi_counts.get('object', 0),
            'object_pct': aoi_pct.get('object', 0),
            'other_count': aoi_counts.get('other', 0),
            'other_pct': aoi_pct.get('other', 0),
            'mean_distance': first_non_center_df['distance_from_center'].mean()
        })
        
        print(f"\nThreshold: {threshold} pixels")
        print(f"  Trials with non-center fixations: {len(first_non_center_df)}")
        print(f"  Mean distance from center: {first_non_center_df['distance_from_center'].mean():.1f} pixels")
        print(f"  AOI distribution:")
        for aoi in ['subject', 'object', 'other']:
            count = aoi_counts.get(aoi, 0)
            pct = aoi_pct.get(aoi, 0)
            print(f"    {aoi}: {count} ({pct:.1f}%)")

threshold_summary = pd.DataFrame(threshold_results)
print("\n" + "="*80)
print("THRESHOLD COMPARISON SUMMARY")
print("="*80)
print(threshold_summary.to_string(index=False))

# Select optimal threshold (e.g., 100 pixels - reasonable distance from center)
selected_threshold = 100
print(f"\nUsing threshold: {selected_threshold} pixels for main analysis")

# Recalculate with selected threshold
voice_data['distance_from_center'] = np.sqrt(
    (voice_data['CURRENT_FIX_X'] - x_center)**2 + 
    (voice_data['CURRENT_FIX_Y'] - y_center)**2
)
voice_data['is_center'] = voice_data['distance_from_center'] <= selected_threshold

# Find first non-center fixation for each trial
print("\n" + "="*80)
print("MAIN ANALYSIS: FIRST NON-CENTER FIXATION (Voice Condition)")
print("="*80)

grouping_cols = ['participant_id', 'TRIAL_INDEX']
if 'image_id' in voice_data.columns:
    grouping_cols.append('image_id')

first_non_center_list = []

for name, group in voice_data.groupby(grouping_cols):
    group_sorted = group.sort_values('CURRENT_FIX_START')
    non_center_fixations = group_sorted[~group_sorted['is_center']]
    
    if len(non_center_fixations) > 0:
        first_fix = non_center_fixations.iloc[0]
        first_non_center_list.append({
            'participant_id': first_fix['participant_id'],
            'TRIAL_INDEX': first_fix['TRIAL_INDEX'],
            'image_id': first_fix.get('image_id', 'unknown'),
            'voice_id': first_fix.get('voice_id', 'unknown'),
            'aoi_type': first_fix.get('aoi_type', 'unknown'),
            'CURRENT_FIX_X': first_fix['CURRENT_FIX_X'],
            'CURRENT_FIX_Y': first_fix['CURRENT_FIX_Y'],
            'distance_from_center': first_fix['distance_from_center'],
            'CURRENT_FIX_START': first_fix['CURRENT_FIX_START'],
            'CURRENT_FIX_DURATION': first_fix['CURRENT_FIX_DURATION'],
            'CURRENT_FIX_INTEREST_AREA_LABEL': first_fix.get('CURRENT_FIX_INTEREST_AREA_LABEL', ''),
        })

first_non_center_df = pd.DataFrame(first_non_center_list)

# Recategorize "other" as "subject"
first_non_center_df['aoi_type'] = first_non_center_df['aoi_type'].replace('other', 'subject')

print(f"\nTotal trials analyzed: {len(first_non_center_df)}")
print(f"Trials with valid AOI: {first_non_center_df['aoi_type'].notna().sum()}")
print("Note: 'other' AOI has been recategorized as 'subject'")

# 1. AOI DISTRIBUTION
print("\n" + "="*80)
print("1. AOI DISTRIBUTION (First Non-Center Fixation)")
print("="*80)

aoi_counts = first_non_center_df['aoi_type'].value_counts()
aoi_pct = first_non_center_df['aoi_type'].value_counts(normalize=True) * 100

print("\nWhich AOI is seen first (after ignoring center fixations):")
print("Note: 'other' AOI has been recategorized as 'subject'")
for aoi in ['subject', 'object']:
    count = aoi_counts.get(aoi, 0)
    pct = aoi_pct.get(aoi, 0)
    print(f"  {aoi}: {count} fixations ({pct:.1f}%)")

print(f"\nTotal first non-center fixations: {len(first_non_center_df)}")
print(f"Total subject (including recategorized 'other'): {aoi_counts.get('subject', 0)}")
print(f"Total object: {aoi_counts.get('object', 0)}")

aoi_summary = pd.DataFrame({
    'aoi_type': aoi_counts.index,
    'count': aoi_counts.values,
    'percentage': aoi_pct.values
})
aoi_summary.to_csv("results/first_non_center_fixation/aoi_distribution.csv", index=False)

# 2. BY VOICE ID
print("\n" + "="*80)
print("2. AOI DISTRIBUTION BY VOICE ID")
print("="*80)

if 'voice_id' in first_non_center_df.columns:
    voice_aoi = pd.crosstab(first_non_center_df['voice_id'], first_non_center_df['aoi_type'], 
                            normalize='index') * 100
    voice_aoi_counts = pd.crosstab(first_non_center_df['voice_id'], first_non_center_df['aoi_type'])
    
    print("\nAOI Distribution by Voice ID (%):")
    print(voice_aoi.round(1).to_string())
    
    print("\nAOI Distribution by Voice ID (counts):")
    print(voice_aoi_counts.to_string())
    
    voice_aoi.to_csv("results/first_non_center_fixation/aoi_by_voice_id_pct.csv")
    voice_aoi_counts.to_csv("results/first_non_center_fixation/aoi_by_voice_id_counts.csv")

# 3. BY IMAGE
print("\n" + "="*80)
print("3. AOI DISTRIBUTION BY IMAGE")
print("="*80)

if 'image_id' in first_non_center_df.columns:
    image_aoi = pd.crosstab(first_non_center_df['image_id'], first_non_center_df['aoi_type'], 
                           normalize='index') * 100
    image_aoi_counts = pd.crosstab(first_non_center_df['image_id'], first_non_center_df['aoi_type'])
    
    print("\nAOI Distribution by Image (%):")
    print(image_aoi.round(1).to_string())
    
    image_aoi.to_csv("results/first_non_center_fixation/aoi_by_image_pct.csv")
    image_aoi_counts.to_csv("results/first_non_center_fixation/aoi_by_image_counts.csv")

# 4. LOCATION ANALYSIS
print("\n" + "="*80)
print("4. LOCATION OF FIRST NON-CENTER FIXATION")
print("="*80)

location_summary = first_non_center_df.groupby('aoi_type').agg({
    'CURRENT_FIX_X': ['mean', 'median', 'std'],
    'CURRENT_FIX_Y': ['mean', 'median', 'std'],
    'distance_from_center': ['mean', 'median', 'std']
}).round(2)

location_summary.columns = ['_'.join(col).strip() for col in location_summary.columns.values]
location_summary = location_summary.reset_index()

print("\nLocation Statistics by AOI Type:")
print(location_summary.to_string(index=False))

location_summary.to_csv("results/first_non_center_fixation/location_by_aoi.csv", index=False)

# 5. VISUALIZATIONS
print("\n" + "="*80)
print("5. CREATING VISUALIZATIONS")
print("="*80)

plt.style.use('default')
sns.set_palette("Set2")

# 5.1 AOI Distribution Bar Chart
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Filter to only subject and object
aoi_counts_filtered = aoi_counts[aoi_counts.index.isin(['subject', 'object'])]
aoi_pct_filtered = aoi_pct[aoi_pct.index.isin(['subject', 'object'])]

# Counts
aoi_counts_filtered.plot(kind='bar', ax=axes[0], color=['skyblue', 'lightcoral'])
axes[0].set_title('First Non-Center Fixation: AOI Distribution (Counts)\n(other → subject)')
axes[0].set_xlabel('AOI Type')
axes[0].set_ylabel('Number of Trials')
axes[0].tick_params(axis='x', rotation=0)
axes[0].grid(axis='y', alpha=0.3)

# Percentages
aoi_pct_filtered.plot(kind='bar', ax=axes[1], color=['skyblue', 'lightcoral'])
axes[1].set_title('First Non-Center Fixation: AOI Distribution (%)\n(other → subject)')
axes[1].set_xlabel('AOI Type')
axes[1].set_ylabel('Percentage of Trials')
axes[1].tick_params(axis='x', rotation=0)
axes[1].grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig("plots/first_non_center_fixation/aoi_distribution.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved: plots/first_non_center_fixation/aoi_distribution.png")

# 5.2 Scatter plot by AOI
fig, ax = plt.subplots(figsize=(10, 8))

colors = {'subject': 'red', 'object': 'blue'}
for aoi in ['subject', 'object']:
    aoi_data = first_non_center_df[first_non_center_df['aoi_type'] == aoi]
    if len(aoi_data) > 0:
        ax.scatter(aoi_data['CURRENT_FIX_X'], aoi_data['CURRENT_FIX_Y'], 
                  alpha=0.5, s=30, label=aoi, c=colors.get(aoi, 'black'))

# Mark center
ax.scatter(x_center, y_center, marker='+', s=500, c='black', linewidths=3, label='Screen Center')
ax.axvline(x_center, color='black', linestyle='--', alpha=0.3)
ax.axhline(y_center, color='black', linestyle='--', alpha=0.3)

# Draw threshold circle
circle = plt.Circle((x_center, y_center), selected_threshold, fill=False, 
                   color='red', linestyle='--', linewidth=2, label=f'Center Threshold ({selected_threshold}px)')
ax.add_patch(circle)

ax.set_title('First Non-Center Fixation Locations by AOI Type (Voice Condition)')
ax.set_xlabel('X Coordinate (pixels)')
ax.set_ylabel('Y Coordinate (pixels)')
ax.legend()
ax.grid(True, alpha=0.3)
ax.set_aspect('equal', adjustable='box')

plt.tight_layout()
plt.savefig("plots/first_non_center_fixation/locations_by_aoi.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved: plots/first_non_center_fixation/locations_by_aoi.png")

# 5.3 By Voice ID (if available)
if 'voice_id' in first_non_center_df.columns and first_non_center_df['voice_id'].nunique() > 1:
    fig, axes = plt.subplots(1, len(first_non_center_df['voice_id'].unique()), 
                            figsize=(6*first_non_center_df['voice_id'].nunique(), 5))
    
    if first_non_center_df['voice_id'].nunique() == 1:
        axes = [axes]
    
    for idx, voice_id in enumerate(sorted(first_non_center_df['voice_id'].unique())):
        voice_data_subset = first_non_center_df[first_non_center_df['voice_id'] == voice_id]
        aoi_counts_voice = voice_data_subset['aoi_type'].value_counts()
        
        # Filter to only subject and object
        aoi_counts_voice_filtered = aoi_counts_voice[aoi_counts_voice.index.isin(['subject', 'object'])]
        aoi_counts_voice_filtered.plot(kind='bar', ax=axes[idx], color=['skyblue', 'lightcoral'])
        axes[idx].set_title(f'Voice ID: {voice_id}\n(n={len(voice_data_subset)} trials)')
        axes[idx].set_xlabel('AOI Type')
        axes[idx].set_ylabel('Count')
        axes[idx].tick_params(axis='x', rotation=0)
        axes[idx].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("plots/first_non_center_fixation/aoi_by_voice_id.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: plots/first_non_center_fixation/aoi_by_voice_id.png")

# 6. STATISTICAL TEST
print("\n" + "="*80)
print("6. STATISTICAL ANALYSIS")
print("="*80)

# Test if distribution differs from chance (50% each if equal)
from scipy.stats import chi2_contingency

if len(aoi_counts) >= 2:
    # Chi-square test for uniform distribution (50/50 split)
    expected = np.array([len(first_non_center_df) / 2] * 2)  # Equal distribution
    observed = np.array([aoi_counts.get('subject', 0), 
                        aoi_counts.get('object', 0)])
    
    chi2, p_value = stats.chisquare(observed, expected)
    
    print(f"\nChi-square test (equal distribution):")
    print(f"  Chi-square = {chi2:.3f}")
    print(f"  p-value = {p_value:.4f}")
    if p_value < 0.001:
        print(f"  Result: *** p < 0.001 (distribution is NOT uniform)")
    elif p_value < 0.01:
        print(f"  Result: ** p < 0.01 (distribution is NOT uniform)")
    elif p_value < 0.05:
        print(f"  Result: * p < 0.05 (distribution is NOT uniform)")
    else:
        print(f"  Result: ns (p >= 0.05, distribution could be uniform)")

# 7. SAVE DATA
print("\n" + "="*80)
print("7. SAVING RESULTS")
print("="*80)

first_non_center_df.to_csv("results/first_non_center_fixation/first_non_center_fixations.csv", index=False)
print("Saved: results/first_non_center_fixation/first_non_center_fixations.csv")

# Generate summary report
report_lines = []
report_lines.append("="*80)
report_lines.append("FIRST NON-CENTER FIXATION ANALYSIS (Voice Condition)")
report_lines.append("="*80)
report_lines.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

report_lines.append("METHOD:")
report_lines.append(f"  - Center threshold: {selected_threshold} pixels from center (X={x_center:.0f}, Y={y_center:.0f})")
report_lines.append(f"  - Analyzed first fixation that is >{selected_threshold} pixels from center")
report_lines.append(f"  - Total trials analyzed: {len(first_non_center_df)}\n")

report_lines.append("KEY FINDING:")
dominant_aoi = aoi_counts.index[0]
dominant_pct = aoi_pct.iloc[0]
report_lines.append(f"  The first non-center fixation lands on '{dominant_aoi}' AOI in {dominant_pct:.1f}% of trials")
report_lines.append(f"  This is the most common first AOI after ignoring center fixations.\n")

report_lines.append("DETAILED DISTRIBUTION:")
report_lines.append("  Note: 'other' AOI has been recategorized as 'subject'")
for aoi in ['subject', 'object']:
    count = aoi_counts.get(aoi, 0)
    pct = aoi_pct.get(aoi, 0)
    report_lines.append(f"  {aoi}: {count} trials ({pct:.1f}%)")

report_text = "\n".join(report_lines)

with open("results/first_non_center_fixation/analysis_report.txt", 'w', encoding='utf-8') as f:
    f.write(report_text)

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  - results/first_non_center_fixation/first_non_center_fixations.csv")
print("  - results/first_non_center_fixation/aoi_distribution.csv")
print("  - results/first_non_center_fixation/location_by_aoi.csv")
print("  - results/first_non_center_fixation/analysis_report.txt")
print("  - plots/first_non_center_fixation/aoi_distribution.png")
print("  - plots/first_non_center_fixation/locations_by_aoi.png")

