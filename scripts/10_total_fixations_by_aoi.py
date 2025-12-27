# %% Total Fixations by AOI Analysis
# Script: 10_total_fixations_by_aoi.py
# Purpose: Analyze total number of fixations by AOI type for Voice condition

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set working directory
if not os.path.exists("scripts"):
    os.chdir("..")

# Create output directories
os.makedirs("results/total_fixations", exist_ok=True)
os.makedirs("plots/total_fixations", exist_ok=True)

print("Analyzing Total Fixations by AOI (Voice Condition)...")

# Load data
print("Loading data...")
merged_fixation_data = pd.read_csv("data/processed/merged_fixation_data_with_flags.csv")

# Filter clean data for Voice condition only
fixation_clean = merged_fixation_data[~merged_fixation_data['exclude_fixation']].copy()

voice_data = fixation_clean[
    fixation_clean['voice_id'].notna() & 
    (fixation_clean['voice_id'] != "") & 
    (fixation_clean['voice_id'] != "UNDEFINEDnull")
].copy()

# Recategorize "other" as "subject"
voice_data['aoi_type'] = voice_data['aoi_type'].replace('other', 'subject')

print(f"\nTotal fixations in Voice condition: {len(voice_data)}")
print(f"Unique trials: {voice_data.groupby(['participant_id', 'TRIAL_INDEX']).ngroups}")

# 1. TOTAL FIXATIONS BY AOI TYPE
print("\n" + "="*80)
print("1. TOTAL FIXATIONS BY AOI TYPE")
print("="*80)

aoi_totals = voice_data['aoi_type'].value_counts()
aoi_totals_pct = voice_data['aoi_type'].value_counts(normalize=True) * 100

print("\nTotal Fixations by AOI Type:")
for aoi in ['subject', 'object']:
    count = aoi_totals.get(aoi, 0)
    pct = aoi_totals_pct.get(aoi, 0)
    print(f"  {aoi}: {count:,} fixations ({pct:.1f}%)")

print(f"\nTotal fixations: {len(voice_data):,}")

total_summary = pd.DataFrame({
    'aoi_type': aoi_totals.index,
    'total_fixations': aoi_totals.values,
    'percentage': aoi_totals_pct.values
})
total_summary.to_csv("results/total_fixations/total_fixations_by_aoi.csv", index=False)

# 2. TOTAL FIXATIONS BY VOICE ID
print("\n" + "="*80)
print("2. TOTAL FIXATIONS BY VOICE ID AND AOI")
print("="*80)

voice_aoi_totals = pd.crosstab(voice_data['voice_id'], voice_data['aoi_type'])
voice_aoi_totals_pct = pd.crosstab(voice_data['voice_id'], voice_data['aoi_type'], normalize='index') * 100

print("\nTotal Fixations by Voice ID and AOI (counts):")
print(voice_aoi_totals.to_string())

print("\nTotal Fixations by Voice ID and AOI (%):")
print(voice_aoi_totals_pct.round(1).to_string())

voice_aoi_totals.to_csv("results/total_fixations/total_fixations_by_voice_aoi_counts.csv")
voice_aoi_totals_pct.to_csv("results/total_fixations/total_fixations_by_voice_aoi_pct.csv")

# Add row totals
voice_aoi_totals['TOTAL'] = voice_aoi_totals.sum(axis=1)
print("\nTotal Fixations by Voice ID (with totals):")
print(voice_aoi_totals.to_string())

# 3. TOTAL FIXATIONS BY IMAGE
print("\n" + "="*80)
print("3. TOTAL FIXATIONS BY IMAGE AND AOI")
print("="*80)

if 'image_id' in voice_data.columns:
    image_aoi_totals = pd.crosstab(voice_data['image_id'], voice_data['aoi_type'])
    image_aoi_totals_pct = pd.crosstab(voice_data['image_id'], voice_data['aoi_type'], normalize='index') * 100
    
    image_aoi_totals['TOTAL'] = image_aoi_totals.sum(axis=1)
    
    print("\nTotal Fixations by Image and AOI (sample - first 10 images):")
    print(image_aoi_totals.head(10).to_string())
    
    print("\n...")
    print(f"\nTotal fixations across all images: {image_aoi_totals['TOTAL'].sum():,}")
    
    image_aoi_totals.to_csv("results/total_fixations/total_fixations_by_image_aoi_counts.csv")
    image_aoi_totals_pct.to_csv("results/total_fixations/total_fixations_by_image_aoi_pct.csv")

# 4. TRIAL-LEVEL SUMMARY
print("\n" + "="*80)
print("4. AVERAGE FIXATIONS PER TRIAL BY AOI")
print("="*80)

trial_aoi_summary = voice_data.groupby(['participant_id', 'TRIAL_INDEX', 'aoi_type']).size().reset_index(name='fixation_count')
trial_summary = trial_aoi_summary.groupby('aoi_type')['fixation_count'].agg(['mean', 'median', 'std', 'count']).round(2)

print("\nAverage Fixations per Trial by AOI:")
print(trial_summary.to_string())

trial_summary.to_csv("results/total_fixations/average_fixations_per_trial_by_aoi.csv")

# 5. VISUALIZATIONS
print("\n" + "="*80)
print("5. CREATING VISUALIZATIONS")
print("="*80)

plt.style.use('default')
sns.set_palette("Set2")

# 5.1 Total fixations bar chart
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Counts
aoi_totals.plot(kind='bar', ax=axes[0], color=['skyblue', 'lightcoral'])
axes[0].set_title('Total Fixations by AOI Type\n(Voice Condition, other → subject)')
axes[0].set_xlabel('AOI Type')
axes[0].set_ylabel('Total Number of Fixations')
axes[0].tick_params(axis='x', rotation=0)
axes[0].grid(axis='y', alpha=0.3)
for i, v in enumerate(aoi_totals.values):
    axes[0].text(i, v, f'{v:,}', ha='center', va='bottom')

# Percentages
aoi_totals_pct.plot(kind='bar', ax=axes[1], color=['skyblue', 'lightcoral'])
axes[1].set_title('Fixation Distribution by AOI Type (%)\n(Voice Condition, other → subject)')
axes[1].set_xlabel('AOI Type')
axes[1].set_ylabel('Percentage of Total Fixations')
axes[1].tick_params(axis='x', rotation=0)
axes[1].grid(axis='y', alpha=0.3)
for i, v in enumerate(aoi_totals_pct.values):
    axes[1].text(i, v, f'{v:.1f}%', ha='center', va='bottom')

plt.tight_layout()
plt.savefig("plots/total_fixations/total_fixations_by_aoi.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved: plots/total_fixations/total_fixations_by_aoi.png")

# 5.2 By Voice ID
if len(voice_aoi_totals) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Counts
    voice_aoi_totals[['subject', 'object']].plot(kind='bar', ax=axes[0], 
                                                  color=['skyblue', 'lightcoral'])
    axes[0].set_title('Total Fixations by Voice ID and AOI')
    axes[0].set_xlabel('Voice ID')
    axes[0].set_ylabel('Total Number of Fixations')
    axes[0].legend(title='AOI Type')
    axes[0].tick_params(axis='x', rotation=0)
    axes[0].grid(axis='y', alpha=0.3)
    
    # Percentages
    voice_aoi_totals_pct[['subject', 'object']].plot(kind='bar', ax=axes[1], 
                                                     color=['skyblue', 'lightcoral'], stacked=True)
    axes[1].set_title('Fixation Distribution by Voice ID (% stacked)')
    axes[1].set_xlabel('Voice ID')
    axes[1].set_ylabel('Percentage')
    axes[1].legend(title='AOI Type')
    axes[1].tick_params(axis='x', rotation=0)
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig("plots/total_fixations/total_fixations_by_voice_id.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: plots/total_fixations/total_fixations_by_voice_id.png")

# 6. GENERATE SUMMARY REPORT
print("\n" + "="*80)
print("6. GENERATING SUMMARY REPORT")
print("="*80)

report_lines = []
report_lines.append("="*80)
report_lines.append("TOTAL FIXATIONS BY AOI ANALYSIS (Voice Condition)")
report_lines.append("="*80)
report_lines.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

report_lines.append("NOTE: 'other' AOI has been recategorized as 'subject'\n")

report_lines.append("SUMMARY:")
report_lines.append(f"  Total fixations analyzed: {len(voice_data):,}")
report_lines.append(f"  Total trials: {voice_data.groupby(['participant_id', 'TRIAL_INDEX']).ngroups}\n")

report_lines.append("TOTAL FIXATIONS BY AOI TYPE:")
for aoi in ['subject', 'object']:
    count = aoi_totals.get(aoi, 0)
    pct = aoi_totals_pct.get(aoi, 0)
    report_lines.append(f"  {aoi}: {count:,} fixations ({pct:.1f}%)")

report_lines.append("\nTOTAL FIXATIONS BY VOICE ID:")
for voice_id in voice_aoi_totals.index:
    report_lines.append(f"\n  {voice_id}:")
    total_voice = voice_aoi_totals.loc[voice_id, 'TOTAL'] if 'TOTAL' in voice_aoi_totals.columns else voice_aoi_totals.loc[voice_id].sum()
    report_lines.append(f"    Total fixations: {total_voice:,}")
    for aoi in ['subject', 'object']:
        if aoi in voice_aoi_totals.columns:
            count = voice_aoi_totals.loc[voice_id, aoi]
            pct = voice_aoi_totals_pct.loc[voice_id, aoi]
            report_lines.append(f"    {aoi}: {count:,} ({pct:.1f}%)")

report_lines.append("\nAVERAGE FIXATIONS PER TRIAL:")
for aoi in trial_summary.index:
    mean = trial_summary.loc[aoi, 'mean']
    median = trial_summary.loc[aoi, 'median']
    report_lines.append(f"  {aoi}: M={mean:.2f}, Median={median:.2f}")

report_text = "\n".join(report_lines)

with open("results/total_fixations/total_fixations_report.txt", 'w', encoding='utf-8') as f:
    f.write(report_text)

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  - results/total_fixations/total_fixations_by_aoi.csv")
print("  - results/total_fixations/total_fixations_by_voice_aoi_counts.csv")
print("  - results/total_fixations/total_fixations_by_voice_aoi_pct.csv")
print("  - results/total_fixations/average_fixations_per_trial_by_aoi.csv")
print("  - results/total_fixations/total_fixations_report.txt")
print("  - plots/total_fixations/total_fixations_by_aoi.png")
print("  - plots/total_fixations/total_fixations_by_voice_id.png")

