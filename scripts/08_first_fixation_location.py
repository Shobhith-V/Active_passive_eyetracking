# %% First Fixation Location Analysis
# Script: 08_first_fixation_location.py
# Purpose: Analyze the location of first fixations on images

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Set working directory
if not os.path.exists("scripts"):
    os.chdir("..")

# Create output directories
os.makedirs("results/first_fixation", exist_ok=True)
os.makedirs("plots/first_fixation", exist_ok=True)

print("Analyzing First Fixation Locations on Images...")

# Load data
print("Loading data...")
fixation_data = pd.read_csv("data/processed/fixation_with_variables.csv")
merged_fixation_data = pd.read_csv("data/processed/merged_fixation_data_with_flags.csv")

# Filter clean data (no exclusions for this analysis, or use clean data)
fixation_clean = merged_fixation_data[~merged_fixation_data['exclude_fixation']].copy()

# Check if we have image_id and X/Y coordinates
print(f"\nTotal fixations: {len(fixation_clean)}")
print(f"Columns available: {fixation_clean.columns.tolist()}")

# Ensure we have required columns
required_cols = ['CURRENT_FIX_X', 'CURRENT_FIX_Y', 'CURRENT_FIX_START', 'participant_id', 'TRIAL_INDEX']
if not all(col in fixation_clean.columns for col in required_cols):
    print("Warning: Missing required columns. Checking fixation_data...")
    fixation_clean = fixation_data.copy()
    required_cols = ['CURRENT_FIX_X', 'CURRENT_FIX_Y', 'CURRENT_FIX_START', 'participant_id', 'TRIAL_INDEX']

# Get image_id if available, otherwise use trial identifier
if 'image_id' in fixation_clean.columns:
    grouping_cols = ['participant_id', 'TRIAL_INDEX', 'image_id']
    use_image_id = True
elif 'stim_id' in fixation_clean.columns:
    grouping_cols = ['participant_id', 'TRIAL_INDEX', 'stim_id']
    use_image_id = True
    fixation_clean['image_id'] = fixation_clean['stim_id']
else:
    grouping_cols = ['participant_id', 'TRIAL_INDEX']
    use_image_id = False
    fixation_clean['image_id'] = fixation_clean['participant_id'].astype(str) + '_' + fixation_clean['TRIAL_INDEX'].astype(str)

print(f"\nGrouping by: {grouping_cols}")

# Filter out missing coordinates
fixation_clean = fixation_clean[
    fixation_clean['CURRENT_FIX_X'].notna() & 
    fixation_clean['CURRENT_FIX_Y'].notna() &
    (fixation_clean['CURRENT_FIX_X'] >= 0) &
    (fixation_clean['CURRENT_FIX_Y'] >= 0)
].copy()

print(f"Fixations with valid coordinates: {len(fixation_clean)}")

# Identify first fixation for each trial
print("\nIdentifying first fixations per trial...")

first_fixations = fixation_clean.groupby(grouping_cols).apply(
    lambda x: x.loc[x['CURRENT_FIX_START'].idxmin()]
).reset_index(drop=True)

print(f"Total first fixations identified: {len(first_fixations)}")

# Create condition label (Free Viewing vs Voice)
def create_condition(row):
    """Create condition label."""
    if 'voice_id' in row:
        if pd.isna(row.get('voice_id')) or row.get('voice_id') == "" or row.get('voice_id') == "UNDEFINEDnull":
            return "Free Viewing"
        else:
            return "Voice"
    return "Unknown"

first_fixations['condition'] = first_fixations.apply(create_condition, axis=1)

# 1. SUMMARY STATISTICS BY IMAGE
print("\n" + "="*80)
print("1. FIRST FIXATION LOCATIONS BY IMAGE")
print("="*80)

image_summary = first_fixations.groupby('image_id').agg({
    'CURRENT_FIX_X': ['count', 'mean', 'median', 'std', 'min', 'max'],
    'CURRENT_FIX_Y': ['mean', 'median', 'std', 'min', 'max']
}).round(2)

image_summary.columns = ['_'.join(col).strip() for col in image_summary.columns.values]
image_summary = image_summary.reset_index()
image_summary.columns = ['image_id', 'n_trials', 'x_mean', 'x_median', 'x_std', 'x_min', 'x_max',
                         'y_mean', 'y_median', 'y_std', 'y_min', 'y_max']

print(f"\nFound {len(image_summary)} unique images")
print("\nSummary Statistics by Image:")
print(image_summary.to_string(index=False))

image_summary.to_csv("results/first_fixation/first_fixation_by_image.csv", index=False)

# 2. SUMMARY STATISTICS BY CONDITION
print("\n" + "="*80)
print("2. FIRST FIXATION LOCATIONS BY CONDITION")
print("="*80)

condition_summary = first_fixations.groupby('condition').agg({
    'CURRENT_FIX_X': ['count', 'mean', 'median', 'std'],
    'CURRENT_FIX_Y': ['mean', 'median', 'std']
}).round(2)

condition_summary.columns = ['_'.join(col).strip() for col in condition_summary.columns.values]
condition_summary = condition_summary.reset_index()
condition_summary.columns = ['condition', 'n', 'x_mean', 'x_median', 'x_std', 
                             'y_mean', 'y_median', 'y_std']

print("\nSummary Statistics by Condition:")
print(condition_summary.to_string(index=False))

condition_summary.to_csv("results/first_fixation/first_fixation_by_condition.csv", index=False)

# 3. COMBINED SUMMARY (Image × Condition)
print("\n" + "="*80)
print("3. FIRST FIXATION LOCATIONS BY IMAGE AND CONDITION")
print("="*80)

image_condition_summary = first_fixations.groupby(['image_id', 'condition']).agg({
    'CURRENT_FIX_X': ['count', 'mean', 'median', 'std'],
    'CURRENT_FIX_Y': ['mean', 'median', 'std']
}).round(2)

image_condition_summary.columns = ['_'.join(col).strip() for col in image_condition_summary.columns.values]
image_condition_summary = image_condition_summary.reset_index()
image_condition_summary.columns = ['image_id', 'condition', 'n', 'x_mean', 'x_median', 'x_std',
                                   'y_mean', 'y_median', 'y_std']

print(f"\nFound {len(image_condition_summary)} image-condition combinations")
image_condition_summary.to_csv("results/first_fixation/first_fixation_by_image_condition.csv", index=False)

# Show top images by trial count
top_images = image_summary.nlargest(20, 'n_trials')[['image_id', 'n_trials', 'x_mean', 'y_mean']]
print("\nTop 20 Images by Trial Count:")
print(top_images.to_string(index=False))

# 4. VISUALIZATIONS
print("\n" + "="*80)
print("4. CREATING VISUALIZATIONS")
print("="*80)

plt.style.use('default')
sns.set_palette("husl")

# 4.1 Scatter plot of all first fixations
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Overall scatter plot
axes[0].scatter(first_fixations['CURRENT_FIX_X'], first_fixations['CURRENT_FIX_Y'], 
               alpha=0.3, s=20, c='blue')
axes[0].set_title('First Fixation Locations (All Images)')
axes[0].set_xlabel('X Coordinate (pixels)')
axes[0].set_ylabel('Y Coordinate (pixels)')
axes[0].grid(True, alpha=0.3)

# Scatter plot by condition
for condition in first_fixations['condition'].unique():
    condition_data = first_fixations[first_fixations['condition'] == condition]
    axes[1].scatter(condition_data['CURRENT_FIX_X'], condition_data['CURRENT_FIX_Y'], 
                   alpha=0.4, s=20, label=condition)

axes[1].set_title('First Fixation Locations by Condition')
axes[1].set_xlabel('X Coordinate (pixels)')
axes[1].set_ylabel('Y Coordinate (pixels)')
axes[1].legend()
axes[1].grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig("plots/first_fixation/first_fixation_locations_scatter.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved: plots/first_fixation/first_fixation_locations_scatter.png")

# 4.2 Density heatmaps
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# Overall density
axes[0].hexbin(first_fixations['CURRENT_FIX_X'], first_fixations['CURRENT_FIX_Y'], 
              gridsize=30, cmap='Blues', mincnt=1)
axes[0].set_title('First Fixation Density (All Images)')
axes[0].set_xlabel('X Coordinate (pixels)')
axes[0].set_ylabel('Y Coordinate (pixels)')
plt.colorbar(axes[0].collections[0], ax=axes[0], label='Count')

# Density by condition
for idx, condition in enumerate(first_fixations['condition'].unique()):
    condition_data = first_fixations[first_fixations['condition'] == condition]
    if len(condition_data) > 0:
        axes[1].hexbin(condition_data['CURRENT_FIX_X'], condition_data['CURRENT_FIX_Y'], 
                      gridsize=30, cmap='Reds' if idx == 0 else 'Greens', 
                      mincnt=1, alpha=0.6, label=condition)

axes[1].set_title('First Fixation Density by Condition')
axes[1].set_xlabel('X Coordinate (pixels)')
axes[1].set_ylabel('Y Coordinate (pixels)')
axes[1].legend()
plt.colorbar(axes[1].collections[-1], ax=axes[1], label='Count')

plt.tight_layout()
plt.savefig("plots/first_fixation/first_fixation_density.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved: plots/first_fixation/first_fixation_density.png")

# 4.3 Distribution of X and Y coordinates
fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# X coordinate distribution
axes[0, 0].hist(first_fixations['CURRENT_FIX_X'], bins=50, color='skyblue', edgecolor='black', alpha=0.7)
axes[0, 0].set_title('Distribution of First Fixation X Coordinates')
axes[0, 0].set_xlabel('X Coordinate (pixels)')
axes[0, 0].set_ylabel('Frequency')
axes[0, 0].axvline(first_fixations['CURRENT_FIX_X'].mean(), color='red', 
                   linestyle='--', label=f'Mean: {first_fixations["CURRENT_FIX_X"].mean():.0f}')
axes[0, 0].legend()

# Y coordinate distribution
axes[0, 1].hist(first_fixations['CURRENT_FIX_Y'], bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
axes[0, 1].set_title('Distribution of First Fixation Y Coordinates')
axes[0, 1].set_xlabel('Y Coordinate (pixels)')
axes[0, 1].set_ylabel('Frequency')
axes[0, 1].axvline(first_fixations['CURRENT_FIX_Y'].mean(), color='red', 
                   linestyle='--', label=f'Mean: {first_fixations["CURRENT_FIX_Y"].mean():.0f}')
axes[0, 1].legend()

# X by condition
for condition in first_fixations['condition'].unique():
    condition_data = first_fixations[first_fixations['condition'] == condition]
    axes[1, 0].hist(condition_data['CURRENT_FIX_X'], bins=30, alpha=0.6, label=condition)
axes[1, 0].set_title('First Fixation X Coordinates by Condition')
axes[1, 0].set_xlabel('X Coordinate (pixels)')
axes[1, 0].set_ylabel('Frequency')
axes[1, 0].legend()

# Y by condition
for condition in first_fixations['condition'].unique():
    condition_data = first_fixations[first_fixations['condition'] == condition]
    axes[1, 1].hist(condition_data['CURRENT_FIX_Y'], bins=30, alpha=0.6, label=condition)
axes[1, 1].set_title('First Fixation Y Coordinates by Condition')
axes[1, 1].set_xlabel('Y Coordinate (pixels)')
axes[1, 1].set_ylabel('Frequency')
axes[1, 1].legend()

plt.tight_layout()
plt.savefig("plots/first_fixation/first_fixation_distributions.png", dpi=300, bbox_inches='tight')
plt.close()
print("Saved: plots/first_fixation/first_fixation_distributions.png")

# 4.4 Box plots by image (top images)
top_image_ids = image_summary.nlargest(12, 'n_trials')['image_id'].tolist()
top_image_data = first_fixations[first_fixations['image_id'].isin(top_image_ids)]

if len(top_image_data) > 0:
    fig, axes = plt.subplots(1, 2, figsize=(18, 6))
    
    # X coordinates by image
    sns.boxplot(data=top_image_data, x='image_id', y='CURRENT_FIX_X', ax=axes[0])
    axes[0].set_title('First Fixation X Coordinates by Image (Top 12 Images)')
    axes[0].set_xlabel('Image ID')
    axes[0].set_ylabel('X Coordinate (pixels)')
    axes[0].tick_params(axis='x', rotation=45)
    
    # Y coordinates by image
    sns.boxplot(data=top_image_data, x='image_id', y='CURRENT_FIX_Y', ax=axes[1])
    axes[1].set_title('First Fixation Y Coordinates by Image (Top 12 Images)')
    axes[1].set_xlabel('Image ID')
    axes[1].set_ylabel('Y Coordinate (pixels)')
    axes[1].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig("plots/first_fixation/first_fixation_by_image_boxplot.png", dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: plots/first_fixation/first_fixation_by_image_boxplot.png")

# 5. CENTER BIAS ANALYSIS
print("\n" + "="*80)
print("5. CENTER BIAS ANALYSIS")
print("="*80)

# Calculate distance from center (assuming standard screen dimensions)
# Estimate screen center (use median as proxy for actual center)
x_center = first_fixations['CURRENT_FIX_X'].median()
y_center = first_fixations['CURRENT_FIX_Y'].median()

print(f"Estimated screen center: X={x_center:.0f}, Y={y_center:.0f}")

first_fixations['distance_from_center'] = np.sqrt(
    (first_fixations['CURRENT_FIX_X'] - x_center)**2 + 
    (first_fixations['CURRENT_FIX_Y'] - y_center)**2
)

center_bias_summary = first_fixations.groupby('condition').agg({
    'distance_from_center': ['mean', 'median', 'std']
}).round(2)

print("\nDistance from Center by Condition:")
print(center_bias_summary)

center_bias_summary.to_csv("results/first_fixation/center_bias_analysis.csv")

# 6. QUADRANT ANALYSIS
print("\n" + "="*80)
print("6. QUADRANT ANALYSIS")
print("="*80)

# Define quadrants based on median center
def assign_quadrant(row):
    x, y = row['CURRENT_FIX_X'], row['CURRENT_FIX_Y']
    if x <= x_center and y <= y_center:
        return "Top-Left"
    elif x > x_center and y <= y_center:
        return "Top-Right"
    elif x <= x_center and y > y_center:
        return "Bottom-Left"
    else:
        return "Bottom-Right"

first_fixations['quadrant'] = first_fixations.apply(assign_quadrant, axis=1)

quadrant_counts = first_fixations.groupby(['condition', 'quadrant']).size().reset_index(name='count')
quadrant_pct = first_fixations.groupby(['condition', 'quadrant']).size() / first_fixations.groupby('condition').size() * 100
quadrant_pct = quadrant_pct.reset_index(name='percentage')
quadrant_summary = quadrant_counts.merge(quadrant_pct, on=['condition', 'quadrant'])
quadrant_summary['percentage'] = quadrant_summary['percentage'].round(2)

print("\nFirst Fixation Quadrant Distribution:")
print(quadrant_summary.to_string(index=False))

quadrant_summary.to_csv("results/first_fixation/quadrant_analysis.csv", index=False)

# 7. GENERATE COMPREHENSIVE REPORT
print("\n" + "="*80)
print("7. GENERATING REPORT")
print("="*80)

report_lines = []
report_lines.append("="*80)
report_lines.append("FIRST FIXATION LOCATION ANALYSIS REPORT")
report_lines.append("="*80)
report_lines.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

report_lines.append("EXECUTIVE SUMMARY:")
report_lines.append(f"  Total first fixations analyzed: {len(first_fixations)}")
report_lines.append(f"  Unique images: {len(image_summary)}")
report_lines.append(f"  Mean X coordinate: {first_fixations['CURRENT_FIX_X'].mean():.0f} pixels")
report_lines.append(f"  Mean Y coordinate: {first_fixations['CURRENT_FIX_Y'].mean():.0f} pixels")
report_lines.append(f"  Estimated screen center: X={x_center:.0f}, Y={y_center:.0f}\n")

report_lines.append("KEY FINDINGS:")
report_lines.append(f"  1. First fixations show variation across images")
report_lines.append(f"  2. Mean distance from center: {first_fixations['distance_from_center'].mean():.0f} pixels")
report_lines.append(f"  3. X coordinate range: {first_fixations['CURRENT_FIX_X'].min():.0f} - {first_fixations['CURRENT_FIX_X'].max():.0f} pixels")
report_lines.append(f"  4. Y coordinate range: {first_fixations['CURRENT_FIX_Y'].min():.0f} - {first_fixations['CURRENT_FIX_Y'].max():.0f} pixels\n")

report_lines.append("CONDITION COMPARISON:")
for _, row in condition_summary.iterrows():
    report_lines.append(f"  {row['condition']}:")
    report_lines.append(f"    X: M={row['x_mean']:.0f}, SD={row['x_std']:.0f}")
    report_lines.append(f"    Y: M={row['y_mean']:.0f}, SD={row['y_std']:.0f}")

report_lines.append("\nQUADRANT DISTRIBUTION:")
for _, row in quadrant_summary.iterrows():
    report_lines.append(f"  {row['condition']} - {row['quadrant']}: {row['percentage']:.1f}% ({row['count']} fixations)")

report_text = "\n".join(report_lines)

with open("results/first_fixation/first_fixation_analysis_report.txt", 'w', encoding='utf-8') as f:
    f.write(report_text)

print("\n" + "="*80)
print("FIRST FIXATION LOCATION ANALYSIS COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  - results/first_fixation/first_fixation_by_image.csv")
print("  - results/first_fixation/first_fixation_by_condition.csv")
print("  - results/first_fixation/first_fixation_by_image_condition.csv")
print("  - results/first_fixation/center_bias_analysis.csv")
print("  - results/first_fixation/quadrant_analysis.csv")
print("  - results/first_fixation/first_fixation_analysis_report.txt")
print("  - plots/first_fixation/first_fixation_locations_scatter.png")
print("  - plots/first_fixation/first_fixation_density.png")
print("  - plots/first_fixation/first_fixation_distributions.png")

