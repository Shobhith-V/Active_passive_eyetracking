# Free Viewing (Baseline) vs Voice Condition Comparison Report

## Executive Summary

This report compares eye-tracking measures between **Free Viewing** (baseline condition, where voice_id is missing/UNDEFINEDnull) and **Voice** conditions (where voice_id is present). Free viewing serves as the baseline control condition.

## Data Overview

- **Free Viewing Fixations**: 15,221 total fixations
  - Object AOI: 7,140 fixations
  - Subject AOI: 6,088 fixations  
  - Other AOI: 1,993 fixations

- **Voice Condition Fixations**: 12,150 total fixations
  - Object AOI: 5,706 fixations
  - Subject AOI: 4,789 fixations
  - Other AOI: 1,655 fixations

- **Unique Voice IDs**: 3 different voice conditions identified

## Key Findings

### 1. Fixation Duration Differences

#### Subject AOI
- **Free Viewing**: M = 349.89 ms, SD = 351.52 ms
- **Voice**: M = 360.87 ms, SD = 345.05 ms
- **Difference**: +10.99 ms (3.1% longer in Voice condition)
- **Statistical Significance**: ** p < 0.01 (Mann-Whitney U test)
- **Effect Size**: Cohen's d = 0.032 (small effect)

**Interpretation**: Voice condition shows significantly longer fixations on subject AOI, though the effect size is small.

#### Object AOI
- **Free Viewing**: M = 333.39 ms, SD = 323.52 ms
- **Voice**: M = 356.00 ms, SD = 371.85 ms
- **Difference**: +22.61 ms (6.8% longer in Voice condition)
- **Statistical Significance**: ** p < 0.01 (Mann-Whitney U test)
- **Effect Size**: Cohen's d = 0.065 (small effect)

**Interpretation**: Voice condition shows significantly longer fixations on object AOI, with a larger difference than subject AOI. The effect size remains small but is twice that of subject AOI.

#### Other AOI
- **Free Viewing**: M = 262.73 ms, SD = 254.37 ms
- **Voice**: M = 262.98 ms, SD = 276.65 ms
- **Difference**: +0.24 ms (0.1% difference)
- **Statistical Significance**: ** p < 0.01 (Mann-Whitney U test)
- **Effect Size**: Cohen's d = 0.001 (negligible effect)

**Interpretation**: No meaningful difference between conditions for "other" AOI regions.

### 2. Pattern of Results

1. **Voice condition increases fixation duration** on both subject and object AOIs compared to free viewing baseline
2. **Object AOI shows larger effect** (6.8% increase) than subject AOI (3.1% increase)
3. **Effect sizes are small** (Cohen's d < 0.1), suggesting the differences, while statistically significant, are modest in magnitude
4. **No meaningful difference** in "other" AOI regions

### 3. Dwell Time Analysis

Dwell time data available only for Voice condition:
- **Object AOI**: M = 2,153.10 ms
- **Subject AOI**: M = 1,885.79 ms

*Note: Free viewing dwell time data not available in current dataset*

### 4. Saccade Metrics

Saccade data available only for Voice condition:
- **Mean Amplitude**: 3.02 degrees
- **Mean Duration**: 49.11 ms
- **Mean Velocity**: 110.77 deg/s

*Note: Free viewing saccade data not available in current dataset*

## Statistical Summary

All comparisons between Free Viewing and Voice conditions for subject and object AOIs reached statistical significance (p < 0.01), though effect sizes are small. This suggests:

1. **Reliable differences**: The differences are consistent and not due to chance
2. **Small practical impact**: The magnitude of differences is modest
3. **Voice condition effect**: Voice presentation increases attention (fixation duration) to both subject and object regions

## Interpretation

### Theoretical Implications

1. **Voice guidance enhances attention**: The presence of voice leads to longer fixations on critical AOIs (subject and object), suggesting enhanced processing or attention allocation.

2. **Object advantage**: The larger effect size for object AOI (6.8% vs 3.1%) may indicate that voice guidance particularly enhances attention to object regions, possibly due to:
   - Object regions being more visually complex
   - Voice providing semantic information that guides attention to objects
   - Objects requiring more processing time when voice context is present

3. **Baseline comparison**: Free viewing serves as an appropriate baseline, showing natural viewing patterns without auditory guidance.

### Practical Implications

1. **Voice guidance is effective**: Voice conditions show increased attention to relevant AOIs
2. **Modest but reliable effects**: While statistically significant, the effects are small, suggesting voice guidance provides a subtle but consistent enhancement
3. **Object-focused attention**: Voice may be particularly effective at directing attention to object regions

## Recommendations

1. **Proceed with advanced modeling**: The data quality and effect patterns support GAMM modeling to examine:
   - Time-course of voice effects
   - Individual differences in response to voice
   - Interactions between voice type and AOI

2. **Consider voice type differences**: With 3 unique voice IDs, examine whether different voice types have differential effects

3. **Examine temporal dynamics**: Use time-window analyses to understand when voice effects emerge during trials

4. **Individual differences**: Investigate participant-level variability in response to voice conditions

## Files Generated

- `results/comparisons/fixation_duration_comparison.csv` - Descriptive statistics
- `results/comparisons/fixation_statistical_comparison.csv` - Statistical test results
- `results/comparisons/saccade_comparison.csv` - Saccade metrics
- `results/comparisons/free_viewing_vs_voice_summary.txt` - Text summary
- `plots/comparisons/fixation_duration_comparison.png` - Visualization
- `plots/comparisons/saccade_comparison.png` - Saccade visualization

---

*Report generated: 2025-12-27*
*Analysis: Free Viewing (Baseline) vs Voice Condition Comparison*

