# Eye-Tracking Analysis Report

## Overview

This report summarizes the analysis pipeline completed so far for the English/Punjabi active-passive eye-tracking study.
The central goals were to test language and sentence-type effects, use free viewing as a same-picture baseline, evaluate cognitive-load markers, and examine whether the results support an agent-first processing principle.

## Data Preparation Completed

Raw EyeLink report exports were standardized into participant-level and trial-level datasets using `process_eye_tracking_reports.py`.
The analysis preparation script `analysis/prepare_analysis_data.py` then recovered stimulus metadata, matched every sentence/audio trial to same-participant same-picture free-viewing baselines, and created baseline-adjusted outcomes.

Primary analysis dataset:

```text
analysis/derived/sentence_audio_baseline_adjusted.csv
```

Interest-area dataset:

```text
analysis/derived/interest_area_agent_first_dataset.csv
```

All 900 sentence/audio trials had participant-specific same-image free-viewing baselines.

## Experimental Balance

| language   | sentence_type         | agent_first_alignment   | agent_overt   |   rows |
|:-----------|:----------------------|:------------------------|:--------------|-------:|
| English    | active                | agent_first             | agent_overt   |    150 |
| English    | passive               | non_agent_first         | agent_overt   |    150 |
| English    | passive_dropped_agent | non_agent_first         | agent_dropped |    150 |
| Punjabi    | active                | agent_first             | agent_overt   |    150 |
| Punjabi    | passive               | non_agent_first         | agent_overt   |    150 |
| Punjabi    | passive_dropped_agent | non_agent_first         | agent_dropped |    150 |

## AOI Role Coding

AOI role was inferred from `ia_label` using the rule requested:

```text
s_... = agent/subject
o_... = object
everything else = bg
```

| language   | sentence_type         | aoi_role   |   rows |
|:-----------|:----------------------|:-----------|-------:|
| English    | active                | agent      |    150 |
| English    | active                | object     |    150 |
| English    | passive               | agent      |    150 |
| English    | passive               | object     |    150 |
| English    | passive_dropped_agent | agent      |    150 |
| English    | passive_dropped_agent | object     |    150 |
| Punjabi    | active                | agent      |    150 |
| Punjabi    | active                | object     |    150 |
| Punjabi    | passive               | agent      |    150 |
| Punjabi    | passive               | object     |    150 |
| Punjabi    | passive_dropped_agent | agent      |    150 |
| Punjabi    | passive_dropped_agent | object     |    150 |

## Free-Viewing Baseline Strategy

For each sentence/audio trial and each outcome, the analysis computed:

```text
delta_outcome = sentence_audio_outcome - free_viewing_outcome_for_same_participant_and_image
```

This controls for image-level visual salience and participant-specific image-viewing tendencies before testing linguistic effects.

## Exploratory Screening Results

The exploratory stage used descriptive summaries and non-parametric tests. These tests do not replace the GAMMs because they do not model crossed participant/image effects, but they identify promising patterns.

### Strongest Trial-Level Exploratory Effects

| outcome                                | outcome_label                             | group         | levels                                 |   statistic |   p_value | language   | sentence_type   |
|:---------------------------------------|:------------------------------------------|:--------------|:---------------------------------------|------------:|----------:|:-----------|:----------------|
| delta_fixation_fixation_count          | Baseline-adjusted fixation count          | sentence_type | active, passive, passive_dropped_agent |    15.5887  |  0.000412 | English    | nan             |
| delta_fixation_total_fixation_duration | Baseline-adjusted total fixation duration | language      | English, Punjabi                       |     8.78377 |  0.003    | nan        | passive         |
| delta_saccade_mean_saccade_duration    | Baseline-adjusted saccade duration        | sentence_type | active, passive, passive_dropped_agent |    10.473   |  0.005    | English    | nan             |
| delta_fixation_mean_fixation_duration  | Baseline-adjusted mean fixation duration  | language      | English, Punjabi                       |     6.92541 |  0.008    | nan        | passive         |
| cognitive_load_index                   | Composite cognitive-load index            | language      | English, Punjabi                       |     6.79294 |  0.009    | nan        | passive         |
| delta_fixation_fixation_count          | Baseline-adjusted fixation count          | language      | English, Punjabi                       |     6.76376 |  0.009    | nan        | passive         |
| delta_saccade_saccade_rate             | Baseline-adjusted saccade rate            | sentence_type | active, passive, passive_dropped_agent |     9.0794  |  0.011    | English    | nan             |
| delta_fixation_mean_fixation_duration  | Baseline-adjusted mean fixation duration  | sentence_type | active, passive, passive_dropped_agent |     8.38357 |  0.015    | English    | nan             |
| delta_saccade_mean_saccade_duration    | Baseline-adjusted saccade duration        | sentence_type | active, passive, passive_dropped_agent |     7.53012 |  0.023    | Punjabi    | nan             |
| delta_saccade_mean_saccade_velocity    | Baseline-adjusted saccade velocity        | language      | English, Punjabi                       |     4.69691 |  0.03     | nan        | passive         |
| cognitive_load_index                   | Composite cognitive-load index            | sentence_type | active, passive, passive_dropped_agent |     6.87865 |  0.032    | Punjabi    | nan             |
| delta_saccade_mean_saccade_duration    | Baseline-adjusted saccade duration        | language      | English, Punjabi                       |     4.28994 |  0.038    | nan        | active          |
| delta_saccade_saccade_rate             | Baseline-adjusted saccade rate            | language      | English, Punjabi                       |     4.28315 |  0.038    | nan        | passive         |
| delta_saccade_mean_saccade_duration    | Baseline-adjusted saccade duration        | language      | English, Punjabi                       |     3.51535 |  0.061    | nan        | passive         |
| delta_saccade_mean_saccade_velocity    | Baseline-adjusted saccade velocity        | language      | English, Punjabi                       |     3.34994 |  0.067    | nan        | active          |

### Strongest Interest-Area Exploratory Effects

| outcome                               | outcome_label                         | group         | levels                                 |   statistic |   p_value | language   | aoi_role   | sentence_type         |
|:--------------------------------------|:--------------------------------------|:--------------|:---------------------------------------|------------:|----------:|:-----------|:-----------|:----------------------|
| dwell_time                            | Dwell time                            | aoi_role      | agent, object                          |    14.6666  |  0.000128 | English    | nan        | passive_dropped_agent |
| dwell_time                            | Dwell time                            | aoi_role      | agent, object                          |    13.7103  |  0.000213 | English    | nan        | passive               |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | aoi_role      | agent, object                          |    13.4931  |  0.000239 | English    | nan        | passive_dropped_agent |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | aoi_role      | agent, object                          |    13.3091  |  0.000264 | English    | nan        | passive               |
| dwell_time                            | Dwell time                            | aoi_role      | agent, object                          |    12.8458  |  0.000338 | Punjabi    | nan        | passive_dropped_agent |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | aoi_role      | agent, object                          |    12.3825  |  0.000433 | Punjabi    | nan        | passive_dropped_agent |
| time_to_first_fixation                | Time to first fixation                | aoi_role      | agent, object                          |     8.01894 |  0.005    | English    | nan        | passive_dropped_agent |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | aoi_role      | agent, object                          |     6.09714 |  0.014    | English    | nan        | active                |
| dwell_time                            | Dwell time                            | aoi_role      | agent, object                          |     5.86924 |  0.015    | English    | nan        | active                |
| dwell_time                            | Dwell time                            | language      | English, Punjabi                       |     4.20238 |  0.04     | nan        | object     | passive               |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | sentence_type | active, passive, passive_dropped_agent |     5.92529 |  0.052    | Punjabi    | agent      | nan                   |
| entry_count                           | Entry count                           | language      | English, Punjabi                       |     3.63412 |  0.057    | nan        | agent      | passive               |
| dwell_time                            | Dwell time                            | sentence_type | active, passive, passive_dropped_agent |     5.39977 |  0.067    | Punjabi    | agent      | nan                   |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | language      | English, Punjabi                       |     3.24154 |  0.072    | nan        | agent      | passive               |
| entry_count                           | Entry count                           | language      | English, Punjabi                       |     3.22142 |  0.073    | nan        | object     | passive               |

### Exploratory Interpretation

Exploratory screening suggested that sentence-type effects were clearest in English for fixation count, mean fixation duration, saccade rate, and saccade duration. Interest-area screening also showed strong agent/object differences in dwell-time measures, especially in English passive and passive dropped-agent conditions. These findings motivated the confirmatory GAMM stage below.

## GAMM Models

GAMMs were run with `mgcv::bam` in R using participant and image/item random-effect smooths.

Core trial-level model:

```r
outcome ~ language * sentence_type +
  s(participant_id, bs = 're') +
  s(image_id, bs = 're')
```

Agent-first model:

```r
cognitive_load_index ~ language * agent_first_alignment +
  s(participant_id, bs = 're') +
  s(image_id, bs = 're')
```

Interest-area model:

```r
outcome ~ language * sentence_type * aoi_role +
  s(participant_id, bs = 're') +
  s(image_id, bs = 're') +
  s(ia_label, bs = 're')
```

### GAMM Model Fit Summary

| model                                                                       | model_family                                    | outcome                                                 |    n |      aic |   deviance_explained |   r_sq |
|:----------------------------------------------------------------------------|:------------------------------------------------|:--------------------------------------------------------|-----:|---------:|---------------------:|-------:|
| trial_sentence_type_delta_fixation_mean_fixation_duration                   | trial_language_by_sentence_type                 | delta_fixation_mean_fixation_duration                   |  900 | 13550.4  |                0.095 |  0.063 |
| trial_sentence_type_delta_fixation_total_fixation_duration                  | trial_language_by_sentence_type                 | delta_fixation_total_fixation_duration                  |  900 | 13358.2  |                0.163 |  0.121 |
| trial_sentence_type_delta_fixation_fixation_count                           | trial_language_by_sentence_type                 | delta_fixation_fixation_count                           |  900 |  5192.46 |                0.16  |  0.123 |
| trial_sentence_type_delta_interest_area_total_interest_area_dwell_time      | trial_language_by_sentence_type                 | delta_interest_area_total_interest_area_dwell_time      |  900 | 14556.8  |                0.088 |  0.057 |
| trial_sentence_type_delta_interest_area_interest_area_dwell_time_normalized | trial_language_by_sentence_type                 | delta_interest_area_interest_area_dwell_time_normalized |  900 |  -746.94 |                0.026 |  0.011 |
| trial_sentence_type_delta_saccade_saccade_rate                              | trial_language_by_sentence_type                 | delta_saccade_saccade_rate                              |  897 |  1659.7  |                0.275 |  0.228 |
| trial_sentence_type_delta_saccade_mean_saccade_amplitude                    | trial_language_by_sentence_type                 | delta_saccade_mean_saccade_amplitude                    |  897 |  3214.75 |                0.082 |  0.051 |
| trial_sentence_type_delta_saccade_mean_saccade_velocity                     | trial_language_by_sentence_type                 | delta_saccade_mean_saccade_velocity                     |  897 |  9979.58 |                0.17  |  0.131 |
| trial_sentence_type_delta_saccade_mean_saccade_duration                     | trial_language_by_sentence_type                 | delta_saccade_mean_saccade_duration                     |  897 | 10672.7  |                0.028 |  0.013 |
| trial_sentence_type_cognitive_load_index                                    | trial_language_by_sentence_type                 | cognitive_load_index                                    |  900 |  1280.47 |                0.107 |  0.073 |
| agent_first_cognitive_load_index                                            | trial_language_by_agent_first                   | cognitive_load_index                                    |  900 |  1281.81 |                0.102 |  0.069 |
| agent_overt_passive_only_cognitive_load_index                               | passive_only_language_by_agent_overt            | cognitive_load_index                                    |  600 |   944.65 |                0.119 |  0.077 |
| ia_role_time_to_first_fixation                                              | interest_area_language_by_sentence_type_by_role | time_to_first_fixation                                  | 1733 | 27773.2  |                0.22  |  0.194 |
| ia_role_dwell_time_normalized_by_trial_length                               | interest_area_language_by_sentence_type_by_role | dwell_time_normalized_by_trial_length                   | 1800 |  -191.28 |                0.31  |  0.281 |
| ia_role_dwell_time                                                          | interest_area_language_by_sentence_type_by_role | dwell_time                                              | 1800 | 30101.3  |                0.321 |  0.29  |
| ia_role_entry_count                                                         | interest_area_language_by_sentence_type_by_role | entry_count                                             | 1800 |  5374.67 |                0.336 |  0.303 |

### Significant GAMM Parametric Terms

| model_family                                    | outcome                                            | term                                 |    Estimate |   Std._Error |   t_value |   p_value_fmt |
|:------------------------------------------------|:---------------------------------------------------|:-------------------------------------|------------:|-------------:|----------:|--------------:|
| trial_language_by_sentence_type                 | delta_fixation_mean_fixation_duration              | sentence_typepassive                 |  143.763    |   50.9415    |   2.82211 |      0.005    |
| trial_language_by_sentence_type                 | delta_fixation_mean_fixation_duration              | sentence_typepassive_dropped_agent   |  101.001    |   50.9415    |   1.98269 |      0.048    |
| trial_language_by_sentence_type                 | delta_fixation_fixation_count                      | sentence_typepassive                 |   -2.20667  |    0.488593  |  -4.51637 |      7.17e-06 |
| trial_language_by_sentence_type                 | delta_fixation_fixation_count                      | sentence_typepassive_dropped_agent   |   -1.17333  |    0.488593  |  -2.40145 |      0.017    |
| trial_language_by_sentence_type                 | delta_fixation_fixation_count                      | languagePunjabi:sentence_typepassive |    1.76     |    0.690975  |   2.54712 |      0.011    |
| trial_language_by_sentence_type                 | delta_interest_area_total_interest_area_dwell_time | languagePunjabi:sentence_typepassive | -279.481    |  126.086     |  -2.21658 |      0.027    |
| trial_language_by_sentence_type                 | delta_saccade_saccade_rate                         | (Intercept)                          |   -1.00138  |    0.0682748 | -14.6668  |      1.55e-43 |
| trial_language_by_sentence_type                 | delta_saccade_saccade_rate                         | sentence_typepassive                 |   -0.248839 |    0.068328  |  -3.64184 |      0.000287 |
| trial_language_by_sentence_type                 | delta_saccade_saccade_rate                         | languagePunjabi:sentence_typepassive |    0.208091 |    0.0965465 |   2.15535 |      0.031    |
| trial_language_by_sentence_type                 | delta_saccade_mean_saccade_duration                | sentence_typepassive                 |   22.9527   |   10.5858    |   2.16826 |      0.03     |
| interest_area_language_by_sentence_type_by_role | time_to_first_fixation                             | (Intercept)                          | 6205.59     |  102.007     |  60.8349  |      0        |
| interest_area_language_by_sentence_type_by_role | dwell_time_normalized_by_trial_length              | (Intercept)                          |    0.415701 |    0.0365703 |  11.3672  |      6.31e-29 |
| interest_area_language_by_sentence_type_by_role | dwell_time                                         | (Intercept)                          | 1823.43     |  163.88      |  11.1266  |      8.07e-28 |
| interest_area_language_by_sentence_type_by_role | entry_count                                        | (Intercept)                          |    2.51425  |    0.151938  |  16.5479  |      3.56e-57 |
| interest_area_language_by_sentence_type_by_role | entry_count                                        | sentence_typepassive                 |   -0.257725 |    0.12138   |  -2.12329 |      0.034    |

### Key GAMM Results By Hypothesis

#### Sentence-Type Effects

- English passive vs English active for mean fixation duration: estimate = 143.763, p = 0.005 (significant).
- English passive dropped-agent vs English active for mean fixation duration: estimate = 101.001, p = 0.048 (significant).
- English passive vs English active for fixation count: estimate = -2.207, p = 7.17e-06 (significant).
- English passive dropped-agent vs English active for fixation count: estimate = -1.173, p = 0.017 (significant).
- English passive vs English active for saccade rate: estimate = -0.249, p = 2.87e-04 (significant).
- English passive vs English active for saccade duration: estimate = 22.953, p = 0.030 (significant).

Interpretation: relative to English active sentences, English passive sentences showed longer mean fixation durations, lower fixation counts, lower saccade rate, and longer saccade duration. This is consistent with changed processing dynamics under passive syntax, but the decrease in fixation count means the cognitive-load interpretation should be framed as a pattern of longer/deeper fixations rather than globally more fixations.

#### Language Differences

- Punjabi modulation of the passive effect for fixation count: estimate = 1.760, p = 0.011 (significant).
- Punjabi modulation of the passive effect for total IA dwell time: estimate = -279.481, p = 0.027 (significant).
- Punjabi modulation of the passive effect for saccade rate: estimate = 0.208, p = 0.031 (significant).

Interpretation: several passive effects differed between English and Punjabi. The positive Punjabi interaction for fixation count and saccade rate indicates that the English passive reduction in these measures was attenuated in Punjabi. The negative Punjabi interaction for interest-area dwell time suggests a different passive-related dwell-time pattern across languages.

#### Cognitive Load Composite

- Passive vs active for composite cognitive-load index: estimate = -0.047, p = 0.399 (not significant).
- Passive dropped-agent vs active for composite cognitive-load index: estimate = -0.022, p = 0.690 (not significant).
- Non-agent-first vs agent-first for composite cognitive-load index: estimate = -0.035, p = 0.474 (not significant).
- Dropped-agent vs overt-agent passive for composite cognitive-load index: estimate = 0.025, p = 0.679 (not significant).

Interpretation: the composite cognitive-load index did not show a significant sentence-type, agent-first, or dropped-agent effect in the GAMMs. Therefore, the current evidence does not support a broad claim that passive sentences uniformly increased cognitive load across all combined gaze indicators. The stronger claim is that passive syntax altered specific gaze dynamics, especially mean fixation duration and saccade behavior.

#### Agent-First Principle

The agent-first hypothesis receives partial, indirect support only. Active sentences, coded as agent-first aligned, differed from passive structures on some gaze measures, especially in English. However, the direct `agent_first_alignment` GAMM on the composite cognitive-load index was not significant, and the interest-area GAMMs did not show robust significant `aoi_role` interactions after accounting for participant, image, and IA-label random effects.

A defensible interpretation is:

```text
The data show evidence that passive sentence structure changes gaze behavior relative to active structure, particularly in English, but the current GAMM results do not provide strong standalone evidence that this is specifically driven by an agent-first processing mechanism. The agent-first account remains plausible, especially given AOI-level exploratory agent/object differences, but should be presented as partially supported and requiring stronger time-course or AOI-role evidence.
```

## Figures And Placeholders

Use these placeholders when preparing the journal manuscript. The corresponding plot files already exist for many of them.

### Figure 1. Study Design And Pipeline

[Placeholder: schematic showing raw reports -> standardized data -> free-viewing baselines -> GAMMs]

### Figure 2. Baseline-Adjusted Mean Fixation Duration

[Placeholder: line/point plot by language and sentence type]

Existing plot:

```text
analysis/results/gamm/plots/trial_sentence_type_delta_fixation_mean_fixation_duration_predicted_means.png
```

### Figure 3. Baseline-Adjusted Fixation Count

[Placeholder: line/point plot by language and sentence type]

Existing plot:

```text
analysis/results/gamm/plots/trial_sentence_type_delta_fixation_fixation_count_predicted_means.png
```

### Figure 4. Saccade Rate And Saccade Duration

[Placeholder: two-panel figure showing saccade rate and saccade duration by language and sentence type]

Existing plots:

```text
analysis/results/gamm/plots/trial_sentence_type_delta_saccade_saccade_rate_predicted_means.png
analysis/results/gamm/plots/trial_sentence_type_delta_saccade_mean_saccade_duration_predicted_means.png
```

### Figure 5. Time To First Fixation By AOI Role

[Placeholder: agent vs object time-to-first-fixation by language and sentence type]

Existing plot:

```text
analysis/results/gamm/plots/ia_role_time_to_first_fixation_predicted_means.png
```

### Figure 6. Dwell Time By AOI Role

[Placeholder: normalized dwell time for agent vs object AOIs by sentence type and language]

Existing plot:

```text
analysis/results/gamm/plots/ia_role_dwell_time_normalized_by_trial_length_predicted_means.png
```

## Journal-Ready Summary

The analysis pipeline successfully standardizes raw EyeLink exports, constructs trial-level and AOI-level datasets, creates same-participant same-picture free-viewing baselines, derives cognitive-load and agent-first variables, and fits GAMMs with crossed participant and image/item random effects.

The strongest GAMM evidence is for sentence-type effects on specific gaze measures in English: passive sentences increased mean fixation duration, reduced fixation count, reduced saccade rate, and increased saccade duration relative to active sentences. Some of these passive effects differed in Punjabi, suggesting language-specific processing patterns. However, the composite cognitive-load index and direct agent-first composite model were not significant, so the paper should avoid claiming a general passive cognitive-load increase without qualification.

Recommended manuscript framing:

```text
Passive syntax modulated gaze dynamics after controlling for same-picture free-viewing baselines. These effects were strongest in English and were expressed in fixation duration and saccadic timing rather than a uniform increase across all cognitive-load markers. The findings are compatible with an agent-first processing account, but the direct evidence for agent-first processing is partial rather than conclusive.
```

## Files Produced

```text
analysis/derived/sentence_audio_baseline_adjusted.csv
analysis/derived/interest_area_agent_first_dataset.csv
analysis/results/exploratory/
analysis/results/gamm/
analysis/analysis_report.md
```