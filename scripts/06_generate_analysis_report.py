# %% Generate Comprehensive Analysis Report
# Script: 06_generate_analysis_report.py
# Purpose: Analyze results and generate a comprehensive report

import pandas as pd
import numpy as np
import os
from datetime import datetime

# Set working directory
if not os.path.exists("scripts"):
    os.chdir("..")

# Create output directory
os.makedirs("results/reports", exist_ok=True)

print("Generating comprehensive analysis report...")

# Load key result files
print("Loading analysis results...")

# Data quality report
quality_report = pd.read_csv("results/data_quality/data_quality_report.csv")
participant_metadata = pd.read_csv("data/processed/participant_metadata.csv")
fixation_summary = pd.read_csv("results/exploratory/fixation_summary_by_voice_aoi.csv")
aoi_summary = pd.read_csv("results/exploratory/aoi_summary.csv")
participant_variability = pd.read_csv("results/exploratory/participant_variability.csv")
dwell_time_summary = pd.read_csv("results/exploratory/dwell_time_summary_by_voice_aoi.csv")
saccade_summary = pd.read_csv("results/exploratory/saccade_summary_by_voice.csv")

# Load merged trial data for additional statistics
merged_trial_data = pd.read_csv("data/processed/merged_trial_data_with_flags.csv")
merged_fixation_data = pd.read_csv("data/processed/merged_fixation_data_with_flags.csv")
merged_saccade_data = pd.read_csv("data/processed/merged_saccade_data_with_flags.csv")

# Filter clean data
trial_clean = merged_trial_data[~merged_trial_data['exclude_trial']].copy()
fixation_clean = merged_fixation_data[~merged_fixation_data['exclude_fixation']].copy()
saccade_clean = merged_saccade_data[~merged_saccade_data['exclude_saccade']].copy()

# Generate report
report_lines = []

report_lines.append("=" * 80)
report_lines.append("EYE-TRACKING ANALYSIS REPORT")
report_lines.append("=" * 80)
report_lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# 1. EXECUTIVE SUMMARY
report_lines.append("\n" + "=" * 80)
report_lines.append("1. EXECUTIVE SUMMARY")
report_lines.append("=" * 80 + "\n")

total_participants = len(participant_metadata)
total_trials = quality_report[quality_report['check'] == 'Total trials']['count'].values[0]
total_fixations = quality_report[quality_report['check'] == 'Total fixation records']['count'].values[0]
total_saccades = quality_report[quality_report['check'] == 'Total saccade records']['count'].values[0]

report_lines.append(f"This analysis examined eye-tracking data from {total_participants} participants.")
report_lines.append(f"Total trials analyzed: {total_trials:,}")
report_lines.append(f"Total fixations recorded: {total_fixations:,}")
report_lines.append(f"Total saccades recorded: {total_saccades:,}\n")

# Data completeness
participants_all_data = participant_metadata[
    (participant_metadata['has_fixation_data']) &
    (participant_metadata['has_interest_area_data']) &
    (participant_metadata['has_saccade_data'])
].shape[0]

report_lines.append(f"Participants with complete data (fixation, interest area, saccade): {participants_all_data}/{total_participants} ({100*participants_all_data/total_participants:.1f}%)")

# 2. DATA QUALITY ASSESSMENT
report_lines.append("\n" + "=" * 80)
report_lines.append("2. DATA QUALITY ASSESSMENT")
report_lines.append("=" * 80 + "\n")

for _, row in quality_report.iterrows():
    check = row['check']
    count = row['count']
    pct = row['percentage']
    
    if 'outlier' in check.lower() or 'impossible' in check.lower():
        report_lines.append(f"{check}: {count:,} ({pct:.2f}%)")
    elif 'missing' in check.lower():
        report_lines.append(f"{check}: {count:,} ({pct:.2f}%)")
    else:
        report_lines.append(f"{check}: {count:,}")

# Outlier summary
fixation_outliers = quality_report[quality_report['check'] == 'Fixation duration outliers']['count'].values[0]
fixation_outlier_pct = quality_report[quality_report['check'] == 'Fixation duration outliers']['percentage'].values[0]
saccade_outliers = quality_report[quality_report['check'] == 'Saccade amplitude outliers']['count'].values[0]
saccade_outlier_pct = quality_report[quality_report['check'] == 'Saccade amplitude outliers']['percentage'].values[0]

report_lines.append(f"\nOutlier Summary:")
report_lines.append(f"  - Fixation duration outliers: {fixation_outliers:,} ({fixation_outlier_pct:.2f}%)")
report_lines.append(f"  - Saccade amplitude outliers: {saccade_outliers:,} ({saccade_outlier_pct:.2f}%)")

if fixation_outlier_pct < 5 and saccade_outlier_pct < 5:
    report_lines.append("\nData quality assessment: GOOD - Outlier rates are within acceptable limits (<5%)")
else:
    report_lines.append("\nData quality assessment: CAUTION - Some outlier rates exceed 5%")

# 3. FIXATION ANALYSIS
report_lines.append("\n" + "=" * 80)
report_lines.append("3. FIXATION ANALYSIS")
report_lines.append("=" * 80 + "\n")

if 'mean_duration' in fixation_summary.columns:
    overall_mean_fix = fixation_clean['CURRENT_FIX_DURATION'].mean()
    overall_median_fix = fixation_clean['CURRENT_FIX_DURATION'].median()
    overall_std_fix = fixation_clean['CURRENT_FIX_DURATION'].std()
    
    report_lines.append(f"Overall Fixation Duration Statistics (ms):")
    report_lines.append(f"  Mean: {overall_mean_fix:.2f}")
    report_lines.append(f"  Median: {overall_median_fix:.2f}")
    report_lines.append(f"  Standard Deviation: {overall_std_fix:.2f}")
    report_lines.append(f"  Range: {fixation_clean['CURRENT_FIX_DURATION'].min():.2f} - {fixation_clean['CURRENT_FIX_DURATION'].max():.2f}\n")
    
    # By AOI type
    if 'aoi_type' in fixation_clean.columns:
        aoi_stats = fixation_clean.groupby('aoi_type')['CURRENT_FIX_DURATION'].agg(['mean', 'median', 'std', 'count']).round(2)
        report_lines.append("Fixation Duration by AOI Type:")
        for aoi, row in aoi_stats.iterrows():
            report_lines.append(f"  {aoi}:")
            report_lines.append(f"    Mean: {row['mean']:.2f} ms, Median: {row['median']:.2f} ms")
            report_lines.append(f"    SD: {row['std']:.2f} ms, Count: {int(row['count']):,}")

# 4. INTEREST AREA (AOI) ANALYSIS
report_lines.append("\n" + "=" * 80)
report_lines.append("4. INTEREST AREA (AOI) ANALYSIS")
report_lines.append("=" * 80 + "\n")

if not aoi_summary.empty:
    report_lines.append("AOI Summary Statistics:")
    report_lines.append(aoi_summary.to_string(index=False))
    
    # Calculate proportions
    if 'total_fixations' in aoi_summary.columns and 'voice_type' in aoi_summary.columns:
        for voice_type in aoi_summary['voice_type'].unique():
            voice_data = aoi_summary[aoi_summary['voice_type'] == voice_type]
            if 'pct_fixations' in voice_data.columns and 'pct_duration' in voice_data.columns:
                report_lines.append(f"\nVoice Type: {voice_type}")
                for _, row in voice_data.iterrows():
                    report_lines.append(f"  {row['aoi_type']}: {row['pct_fixations']:.1f}% of fixations, {row['pct_duration']:.1f}% of duration")

# 5. SACCADE ANALYSIS
report_lines.append("\n" + "=" * 80)
report_lines.append("5. SACCADE ANALYSIS")
report_lines.append("=" * 80 + "\n")

if 'CURRENT_SAC_AMPLITUDE' in saccade_clean.columns:
    overall_mean_amp = saccade_clean['CURRENT_SAC_AMPLITUDE'].mean()
    overall_mean_dur = saccade_clean['CURRENT_SAC_DURATION'].mean()
    overall_mean_vel = saccade_clean['CURRENT_SAC_AVG_VELOCITY'].mean()
    
    report_lines.append(f"Overall Saccade Statistics:")
    report_lines.append(f"  Mean Amplitude: {overall_mean_amp:.2f} degrees")
    report_lines.append(f"  Mean Duration: {overall_mean_dur:.2f} ms")
    report_lines.append(f"  Mean Velocity: {overall_mean_vel:.2f} deg/s\n")
    
    if not saccade_summary.empty and 'mean_amplitude' in saccade_summary.columns:
        report_lines.append("Saccade Statistics by Voice Type:")
        report_lines.append(saccade_summary.to_string(index=False))

# 6. PARTICIPANT VARIABILITY
report_lines.append("\n" + "=" * 80)
report_lines.append("6. PARTICIPANT VARIABILITY")
report_lines.append("=" * 80 + "\n")

if not participant_variability.empty and 'sd_across_participants' in participant_variability.columns:
    report_lines.append("Variability in Fixation Duration Across Participants:")
    report_lines.append(participant_variability.to_string(index=False))
    
    # Calculate coefficient of variation
    if 'mean_across_participants' in participant_variability.columns:
        participant_variability['cv'] = (participant_variability['sd_across_participants'] / 
                                        participant_variability['mean_across_participants'] * 100)
        report_lines.append("\nCoefficient of Variation (CV = SD/Mean * 100):")
        for _, row in participant_variability.iterrows():
            report_lines.append(f"  {row['voice_type']} - {row['aoi_type']}: {row['cv']:.1f}%")

# 7. KEY FINDINGS
report_lines.append("\n" + "=" * 80)
report_lines.append("7. KEY FINDINGS")
report_lines.append("=" * 80 + "\n")

findings = []

# Data quality findings
if fixation_outlier_pct < 5:
    findings.append(f"Data quality is good with only {fixation_outlier_pct:.2f}% fixation outliers")
else:
    findings.append(f"Data quality needs attention: {fixation_outlier_pct:.2f}% fixation outliers detected")

if saccade_outlier_pct < 5:
    findings.append(f"Saccade data quality is acceptable with {saccade_outlier_pct:.2f}% outliers")
else:
    findings.append(f"Saccade data quality needs review: {saccade_outlier_pct:.2f}% outliers detected")

# Missing voice_id
missing_voice_pct = quality_report[quality_report['check'] == 'Trials with missing voice_id']['percentage'].values[0]
if missing_voice_pct > 50:
    findings.append(f"High rate of missing voice_id: {missing_voice_pct:.1f}% of trials")
    findings.append("  Recommendation: Investigate voice_id encoding in source data")

# Fixation patterns
if 'aoi_type' in fixation_clean.columns:
    aoi_counts = fixation_clean['aoi_type'].value_counts()
    if len(aoi_counts) > 0:
        dominant_aoi = aoi_counts.index[0]
        dominant_pct = 100 * aoi_counts.iloc[0] / len(fixation_clean)
        findings.append(f"Dominant AOI type: {dominant_aoi} ({dominant_pct:.1f}% of fixations)")

for i, finding in enumerate(findings, 1):
    report_lines.append(f"{i}. {finding}")

# 8. RECOMMENDATIONS
report_lines.append("\n" + "=" * 80)
report_lines.append("8. RECOMMENDATIONS")
report_lines.append("=" * 80 + "\n")

recommendations = []

if missing_voice_pct > 30:
    recommendations.append("Investigate and fix voice_id encoding - over 30% of trials are missing this critical variable")

if fixation_outlier_pct > 3:
    recommendations.append("Review fixation duration outliers and consider excluding extreme values (>3 SD from mean)")

if saccade_outlier_pct > 1:
    recommendations.append("Review saccade amplitude outliers for potential data collection issues")

if participants_all_data < total_participants * 0.9:
    recommendations.append("Some participants have incomplete data - consider investigating missing data sources")

recommendations.append("Proceed with statistical modeling (GAMM) to examine voice type effects on eye-tracking measures")
recommendations.append("Consider including participant-level random effects in models to account for individual differences")

if not recommendations:
    recommendations.append("Data quality is sufficient for advanced statistical analysis")

for i, rec in enumerate(recommendations, 1):
    report_lines.append(f"{i}. {rec}")

# 9. DATA SUMMARY TABLE
report_lines.append("\n" + "=" * 80)
report_lines.append("9. DATA SUMMARY TABLE")
report_lines.append("=" * 80 + "\n")

summary_table = pd.DataFrame({
    'Metric': [
        'Total Participants',
        'Participants with Complete Data',
        'Total Trials',
        'Total Fixations',
        'Total Saccades',
        'Fixation Outliers (%)',
        'Saccade Outliers (%)',
        'Trials with Missing Voice ID (%)',
        'Mean Fixation Duration (ms)',
        'Mean Saccade Amplitude (deg)'
    ],
    'Value': [
        total_participants,
        participants_all_data,
        total_trials,
        total_fixations,
        total_saccades,
        f"{fixation_outlier_pct:.2f}%",
        f"{saccade_outlier_pct:.2f}%",
        f"{missing_voice_pct:.1f}%",
        f"{fixation_clean['CURRENT_FIX_DURATION'].mean():.2f}" if 'CURRENT_FIX_DURATION' in fixation_clean.columns else "N/A",
        f"{saccade_clean['CURRENT_SAC_AMPLITUDE'].mean():.2f}" if 'CURRENT_SAC_AMPLITUDE' in saccade_clean.columns else "N/A"
    ]
})

report_lines.append(summary_table.to_string(index=False))

# Write report to file
report_text = "\n".join(report_lines)

report_file = "results/reports/comprehensive_analysis_report.txt"
with open(report_file, 'w', encoding='utf-8') as f:
    f.write(report_text)

print(f"\nReport saved to: {report_file}")

# Also save summary table as CSV
summary_table.to_csv("results/reports/data_summary_table.csv", index=False)
print(f"Summary table saved to: results/reports/data_summary_table.csv")

# Save key findings
key_findings_df = pd.DataFrame({
    'finding_number': range(1, len(findings) + 1),
    'finding': findings
})
key_findings_df.to_csv("results/reports/key_findings.csv", index=False)
print(f"Key findings saved to: results/reports/key_findings.csv")

# Save recommendations
recommendations_df = pd.DataFrame({
    'recommendation_number': range(1, len(recommendations) + 1),
    'recommendation': recommendations
})
recommendations_df.to_csv("results/reports/recommendations.csv", index=False)
print(f"Recommendations saved to: results/reports/recommendations.csv")

print("\n" + "=" * 80)
print("Analysis Report Generation Complete!")
print("=" * 80)
print("\nGenerated files:")
print("  - results/reports/comprehensive_analysis_report.txt")
print("  - results/reports/data_summary_table.csv")
print("  - results/reports/key_findings.csv")
print("  - results/reports/recommendations.csv")

