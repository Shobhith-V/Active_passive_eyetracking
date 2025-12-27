# %% Active/Passive Voice and First Fixation Correlation Analysis
# Script: 11_active_passive_first_fixation_correlation.py
# Purpose: Analyze correlation between voice type (active/passive) and first fixation AOI

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from scipy import stats
from scipy.stats import chi2_contingency, fisher_exact

# Set working directory
if not os.path.exists("scripts"):
    os.chdir("..")

# Create output directories
os.makedirs("results/active_passive_correlation", exist_ok=True)
os.makedirs("plots/active_passive_correlation", exist_ok=True)

print("Analyzing Active/Passive Voice and First Fixation Correlation...")

# Load first non-center fixation data
print("Loading data...")
first_non_center = pd.read_csv("results/first_non_center_fixation/first_non_center_fixations.csv")

# Recategorize "other" as "subject" if not already done
if 'aoi_type' in first_non_center.columns:
    first_non_center['aoi_type'] = first_non_center['aoi_type'].replace('other', 'subject')

print(f"\nTotal first non-center fixations: {len(first_non_center)}")
print(f"Unique voice_id values: {first_non_center['voice_id'].unique()}")

# Map voice_id to active/passive
# Based on common naming: ACT = Active, PNA/PWA might be Passive
# We'll need to infer or check - let's check the patterns first
print("\n" + "="*80)
print("VOICE ID VALUES AND DISTRIBUTION")
print("="*80)

voice_counts = first_non_center['voice_id'].value_counts()
print("\nVoice ID distribution:")
print(voice_counts)

# Create voice type mapping (ACT = Active, others = Passive, or check patterns)
# Let's assume ACT is Active and PNA/PWA are Passive variants
# If we need to check more, we can analyze sentence structure

# Create active/passive categorization
def categorize_voice_type(voice_id):
    """Categorize voice_id as Active or Passive."""
    voice_id_str = str(voice_id).upper()
    if 'ACT' in voice_id_str or 'ACTIVE' in voice_id_str:
        return 'Active'
    elif 'PNA' in voice_id_str or 'PWA' in voice_id_str or 'PASSIVE' in voice_id_str:
        return 'Passive'
    else:
        return 'Unknown'

first_non_center['voice_type_category'] = first_non_center['voice_id'].apply(categorize_voice_type)

print("\nVoice Type Category distribution:")
print(first_non_center['voice_type_category'].value_counts())

# Filter to only Active and Passive
analysis_data = first_non_center[first_non_center['voice_type_category'].isin(['Active', 'Passive'])].copy()

print(f"\nData for analysis (Active + Passive): {len(analysis_data)} trials")

# 1. CROSS-TABULATION ANALYSIS
print("\n" + "="*80)
print("1. CROSS-TABULATION: VOICE TYPE vs FIRST FIXATION AOI")
print("="*80)

# Create contingency table
contingency_table = pd.crosstab(analysis_data['voice_type_category'], analysis_data['aoi_type'])
print("\nContingency Table (Counts):")
print(contingency_table)
print("\nRow totals:")
print(contingency_table.sum(axis=1))

# Percentage by row
contingency_table_pct = pd.crosstab(analysis_data['voice_type_category'], analysis_data['aoi_type'], 
                                   normalize='index') * 100
print("\nContingency Table (Row Percentages):")
print(contingency_table_pct.round(1))

contingency_table.to_csv("results/active_passive_correlation/contingency_table_counts.csv")
contingency_table_pct.to_csv("results/active_passive_correlation/contingency_table_percentages.csv")

# 2. STATISTICAL TESTS
print("\n" + "="*80)
print("2. STATISTICAL TESTS")
print("="*80)

# Chi-square test of independence
chi2, p_value, dof, expected = chi2_contingency(contingency_table)

print("\nChi-square Test of Independence:")
print(f"  Chi-square statistic: {chi2:.4f}")
print(f"  Degrees of freedom: {dof}")
print(f"  p-value: {p_value:.4f}")
print(f"  Expected frequencies:")
print(pd.DataFrame(expected, index=contingency_table.index, columns=contingency_table.columns).round(2))

if p_value < 0.001:
    print(f"\n  Result: *** p < 0.001 (Strong evidence of association)")
elif p_value < 0.01:
    print(f"\n  Result: ** p < 0.01 (Evidence of association)")
elif p_value < 0.05:
    print(f"\n  Result: * p < 0.05 (Evidence of association)")
else:
    print(f"\n  Result: ns (p >= 0.05, no significant association)")

# Effect size: Cramér's V
n = contingency_table.sum().sum()
min_dim = min(contingency_table.shape) - 1
cramers_v = np.sqrt(chi2 / (n * min_dim))

print(f"\nEffect Size (Cramér's V): {cramers_v:.4f}")
if cramers_v < 0.1:
    print("  Interpretation: Negligible effect")
elif cramers_v < 0.3:
    print("  Interpretation: Small effect")
elif cramers_v < 0.5:
    print("  Interpretation: Medium effect")
else:
    print("  Interpretation: Large effect")

# Fisher's exact test (for 2x2 tables)
if contingency_table.shape == (2, 2):
    oddsratio, p_value_fisher = fisher_exact(contingency_table)
    print(f"\nFisher's Exact Test:")
    print(f"  Odds ratio: {oddsratio:.4f}")
    print(f"  p-value: {p_value_fisher:.4f}")
    
    if oddsratio > 1:
        print(f"  Interpretation: {oddsratio:.2f}x more likely for Active voice to fixate first AOI")
    else:
        print(f"  Interpretation: {1/oddsratio:.2f}x more likely for Passive voice to fixate first AOI")

# 3. DETAILED BREAKDOWN BY VOICE ID
print("\n" + "="*80)
print("3. DETAILED BREAKDOWN BY SPECIFIC VOICE ID")
print("="*80)

# Compare ACT vs Passive (PNA + PWA combined, or separately)
voice_aoi_detailed = pd.crosstab(first_non_center['voice_id'], first_non_center['aoi_type'])
voice_aoi_detailed_pct = pd.crosstab(first_non_center['voice_id'], first_non_center['aoi_type'], 
                                     normalize='index') * 100

print("\nFirst Fixation AOI by Voice ID (counts):")
print(voice_aoi_detailed)

print("\nFirst Fixation AOI by Voice ID (%):")
print(voice_aoi_detailed_pct.round(1))

# Compare ACT (Active) vs combined Passive
if 'ACT' in first_non_center['voice_id'].values:
    active_data = first_non_center[first_non_center['voice_id'] == 'ACT']
    passive_data = first_non_center[first_non_center['voice_id'].isin(['PNA', 'PWA'])]
    
    print(f"\nACT (Active) voice:")
    print(f"  Total trials: {len(active_data)}")
    active_aoi = active_data['aoi_type'].value_counts(normalize=True) * 100
    for aoi in ['subject', 'object']:
        pct = active_aoi.get(aoi, 0)
        print(f"  {aoi}: {pct:.1f}%")
    
    print(f"\nPNA/PWA (Passive) voices combined:")
    print(f"  Total trials: {len(passive_data)}")
    passive_aoi = passive_data['aoi_type'].value_counts(normalize=True) * 100
    for aoi in ['subject', 'object']:
        pct = passive_aoi.get(aoi, 0)
        print(f"  {aoi}: {pct:.1f}%")

# 4. VISUALIZATIONS
print("\n" + "="*80)
print("4. CREATING VISUALIZATIONS")
print("="*80)

plt.style.use('default')
sns.set_palette("Set2")

# 4.1 Stacked bar chart
fig, axes = plt.subplots(1, 2, figsize=(14, 5))

# Counts
contingency_table.plot(kind='bar', stacked=False, ax=axes[0], 
                       color=['skyblue', 'lightcoral'])
axes[0].set_title('First Fixation AOI by Voice Type (Counts)')
axes[0].set_xlabel('Voice Type')
axes[0].set_ylabel('Number of Trials')
axes[0].legend(title='First Fixation AOI')
axes[0].tick_params(axis='x', rotation=0)
axes[0].grid(axis='y', alpha=0.3)

# Percentages (stacked)
contingency_table_pct.plot(kind='bar', stacked=True, ax=axes[1], 
                           color=['skyblue', 'lightcoral'])
axes[1].set_title('First Fixation AOI by Voice Type (% Stacked)')
axes[1].set_xlabel('Voice Type')
axes[1].set_ylabel('Percentage')
axes[1].legend(title='First Fixation AOI')
axes[1].tick_params(axis='x', rotation=0)
axes[1].grid(axis='y', alpha=0.3)
axes[1].set_ylim(0, 100)

plt.tight_layout()
plt.savefig("plots/active_passive_correlation/first_fixation_by_voice_type.png", 
           dpi=300, bbox_inches='tight')
plt.close()
print("Saved: plots/active_passive_correlation/first_fixation_by_voice_type.png")

# 4.2 Detailed breakdown by specific voice IDs
if len(voice_aoi_detailed) > 1:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    voice_aoi_detailed.plot(kind='bar', ax=axes[0], color=['skyblue', 'lightcoral'])
    axes[0].set_title('First Fixation AOI by Voice ID (Counts)')
    axes[0].set_xlabel('Voice ID')
    axes[0].set_ylabel('Number of Trials')
    axes[0].legend(title='First Fixation AOI')
    axes[0].tick_params(axis='x', rotation=0)
    axes[0].grid(axis='y', alpha=0.3)
    
    voice_aoi_detailed_pct.plot(kind='bar', stacked=True, ax=axes[1], 
                                color=['skyblue', 'lightcoral'])
    axes[1].set_title('First Fixation AOI by Voice ID (% Stacked)')
    axes[1].set_xlabel('Voice ID')
    axes[1].set_ylabel('Percentage')
    axes[1].legend(title='First Fixation AOI')
    axes[1].tick_params(axis='x', rotation=0)
    axes[1].grid(axis='y', alpha=0.3)
    axes[1].set_ylim(0, 100)
    
    plt.tight_layout()
    plt.savefig("plots/active_passive_correlation/first_fixation_by_voice_id_detailed.png", 
               dpi=300, bbox_inches='tight')
    plt.close()
    print("Saved: plots/active_passive_correlation/first_fixation_by_voice_id_detailed.png")

# 5. LOGISTIC REGRESSION (if we have enough data)
print("\n" + "="*80)
print("5. LOGISTIC REGRESSION ANALYSIS")
print("="*80)

# Create binary outcome (1 = object, 0 = subject)
analysis_data['aoi_binary'] = (analysis_data['aoi_type'] == 'object').astype(int)
analysis_data['voice_binary'] = (analysis_data['voice_type_category'] == 'Active').astype(int)

# Simple logistic regression
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report

X = analysis_data[['voice_binary']].values
y = analysis_data['aoi_binary'].values

if len(np.unique(y)) > 1:  # Need variation in outcome
    model = LogisticRegression()
    model.fit(X, y)
    
    # Predictions
    y_pred = model.predict(X)
    proba = model.predict_proba(X)
    
    print(f"\nLogistic Regression Results:")
    print(f"  Coefficient (voice_type): {model.coef_[0][0]:.4f}")
    print(f"  Intercept: {model.intercept_[0]:.4f}")
    print(f"  Odds Ratio: {np.exp(model.coef_[0][0]):.4f}")
    
    if model.coef_[0][0] > 0:
        print(f"  Interpretation: Active voice increases odds of object fixation")
    else:
        print(f"  Interpretation: Active voice decreases odds of object fixation")
    
    # Model accuracy
    accuracy = (y_pred == y).mean()
    print(f"  Model Accuracy: {accuracy:.3f}")

# 6. GENERATE COMPREHENSIVE REPORT
print("\n" + "="*80)
print("6. GENERATING REPORT")
print("="*80)

report_lines = []
report_lines.append("="*80)
report_lines.append("ACTIVE/PASSIVE VOICE AND FIRST FIXATION CORRELATION ANALYSIS")
report_lines.append("="*80)
report_lines.append(f"\nGenerated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

report_lines.append("HYPOTHESIS:")
report_lines.append("  Testing whether active vs passive voice influences which AOI")
report_lines.append("  receives the first non-center fixation.\n")

report_lines.append("DATA:")
report_lines.append(f"  Total trials analyzed: {len(analysis_data)}")
report_lines.append(f"  Active voice trials: {len(analysis_data[analysis_data['voice_type_category'] == 'Active'])}")
report_lines.append(f"  Passive voice trials: {len(analysis_data[analysis_data['voice_type_category'] == 'Passive'])}\n")

report_lines.append("CONTINGENCY TABLE:")
report_lines.append(contingency_table.to_string())
report_lines.append("\n")

report_lines.append("ROW PERCENTAGES:")
report_lines.append(contingency_table_pct.round(1).to_string())
report_lines.append("\n")

report_lines.append("STATISTICAL RESULTS:")
report_lines.append(f"  Chi-square test: χ² = {chi2:.4f}, p = {p_value:.4f}")
if p_value < 0.05:
    report_lines.append(f"  Result: SIGNIFICANT association between voice type and first fixation AOI")
else:
    report_lines.append(f"  Result: NO significant association between voice type and first fixation AOI")

report_lines.append(f"  Effect size (Cramér's V): {cramers_v:.4f}")
report_lines.append(f"  Interpretation: {('Small' if cramers_v < 0.3 else 'Medium' if cramers_v < 0.5 else 'Large')} effect size\n")

report_lines.append("KEY FINDINGS:")
if p_value < 0.05:
    # Find which AOI is more common for each voice type
    active_pref = contingency_table_pct.loc['Active'].idxmax()
    passive_pref = contingency_table_pct.loc['Passive'].idxmax()
    active_pct = contingency_table_pct.loc['Active', active_pref]
    passive_pct = contingency_table_pct.loc['Passive', passive_pref]
    
    report_lines.append(f"  1. Active voice: {active_pct:.1f}% first fixate on {active_pref} AOI")
    report_lines.append(f"  2. Passive voice: {passive_pct:.1f}% first fixate on {passive_pref} AOI")
    
    if active_pref != passive_pref:
        report_lines.append(f"  3. Voice type influences first fixation pattern")
else:
    report_lines.append("  1. No significant difference in first fixation patterns between Active and Passive voice")
    report_lines.append("  2. First fixation AOI distribution is similar regardless of voice type")

report_text = "\n".join(report_lines)

with open("results/active_passive_correlation/correlation_analysis_report.txt", 'w', encoding='utf-8') as f:
    f.write(report_text)

print("\n" + "="*80)
print("ANALYSIS COMPLETE!")
print("="*80)
print("\nGenerated files:")
print("  - results/active_passive_correlation/contingency_table_counts.csv")
print("  - results/active_passive_correlation/contingency_table_percentages.csv")
print("  - results/active_passive_correlation/correlation_analysis_report.txt")
print("  - plots/active_passive_correlation/first_fixation_by_voice_type.png")
print("  - plots/active_passive_correlation/first_fixation_by_voice_id_detailed.png")

# Save statistical results
stats_results = pd.DataFrame({
    'test': ['Chi-square', 'Cramér\'s V'],
    'value': [chi2, cramers_v],
    'p_value': [p_value, np.nan],
    'interpretation': [
        f"{'Significant' if p_value < 0.05 else 'Not significant'} (p={p_value:.4f})",
        f"{'Small' if cramers_v < 0.3 else 'Medium' if cramers_v < 0.5 else 'Large'} effect"
    ]
})
stats_results.to_csv("results/active_passive_correlation/statistical_test_results.csv", index=False)

