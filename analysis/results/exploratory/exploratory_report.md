# Exploratory Analysis Report

## Scope

This report gives initial descriptive and non-parametric checks before the planned GAMM analyses.
The inferential journal models should still use the GAMM templates with participant and image random effects.

## Trial-Level Sentence/Language Counts

| language   | sentence_type         |   rows |
|:-----------|:----------------------|-------:|
| English    | active                |    150 |
| English    | passive               |    150 |
| English    | passive_dropped_agent |    150 |
| Punjabi    | active                |    150 |
| Punjabi    | passive               |    150 |
| Punjabi    | passive_dropped_agent |    150 |

## AOI Role Counts

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

## Omnibus Trial-Level Checks

| outcome                                | outcome_label                             | test           | group         | levels                                 |   statistic |     p_value | language   | sentence_type         |
|:---------------------------------------|:------------------------------------------|:---------------|:--------------|:---------------------------------------|------------:|------------:|:-----------|:----------------------|
| delta_fixation_fixation_count          | Baseline-adjusted fixation count          | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |   14.1334   | 0.000853048 | English    | nan                   |
| delta_saccade_mean_saccade_duration    | Baseline-adjusted saccade duration        | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |   10.4775   | 0.00530677  | English    | nan                   |
| delta_fixation_mean_fixation_duration  | Baseline-adjusted mean fixation duration  | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    9.17159  | 0.0101956   | English    | nan                   |
| delta_saccade_saccade_rate             | Baseline-adjusted saccade rate            | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    9.0794   | 0.0106766   | English    | nan                   |
| delta_fixation_mean_fixation_duration  | Baseline-adjusted mean fixation duration  | Kruskal-Wallis | language      | English, Punjabi                       |    5.98167  | 0.0144553   | nan        | passive               |
| delta_fixation_fixation_count          | Baseline-adjusted fixation count          | Kruskal-Wallis | language      | English, Punjabi                       |    5.87985  | 0.0153151   | nan        | passive               |
| delta_saccade_mean_saccade_duration    | Baseline-adjusted saccade duration        | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    7.52596  | 0.0232145   | Punjabi    | nan                   |
| delta_fixation_total_fixation_duration | Baseline-adjusted total fixation duration | Kruskal-Wallis | language      | English, Punjabi                       |    4.86832  | 0.0273541   | nan        | passive               |
| delta_saccade_mean_saccade_velocity    | Baseline-adjusted saccade velocity        | Kruskal-Wallis | language      | English, Punjabi                       |    4.69691  | 0.0302168   | nan        | passive               |
| cognitive_load_index                   | Composite cognitive-load index            | Kruskal-Wallis | language      | English, Punjabi                       |    4.34526  | 0.0371121   | nan        | passive               |
| delta_saccade_mean_saccade_duration    | Baseline-adjusted saccade duration        | Kruskal-Wallis | language      | English, Punjabi                       |    4.29546  | 0.0382143   | nan        | active                |
| delta_saccade_saccade_rate             | Baseline-adjusted saccade rate            | Kruskal-Wallis | language      | English, Punjabi                       |    4.28315  | 0.038492    | nan        | passive               |
| delta_saccade_mean_saccade_duration    | Baseline-adjusted saccade duration        | Kruskal-Wallis | language      | English, Punjabi                       |    3.51535  | 0.0608027   | nan        | passive               |
| delta_saccade_mean_saccade_velocity    | Baseline-adjusted saccade velocity        | Kruskal-Wallis | language      | English, Punjabi                       |    3.34994  | 0.0672073   | nan        | active                |
| delta_saccade_mean_saccade_velocity    | Baseline-adjusted saccade velocity        | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    5.08979  | 0.0784814   | Punjabi    | nan                   |
| cognitive_load_index                   | Composite cognitive-load index            | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    4.84925  | 0.0885111   | Punjabi    | nan                   |
| delta_fixation_total_fixation_duration | Baseline-adjusted total fixation duration | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    3.40256  | 0.18245     | Punjabi    | nan                   |
| delta_saccade_mean_saccade_velocity    | Baseline-adjusted saccade velocity        | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    3.09118  | 0.213186    | English    | nan                   |
| cognitive_load_index                   | Composite cognitive-load index            | Kruskal-Wallis | language      | English, Punjabi                       |    1.5457   | 0.213771    | nan        | active                |
| delta_fixation_total_fixation_duration | Baseline-adjusted total fixation duration | Kruskal-Wallis | language      | English, Punjabi                       |    1.46569  | 0.226026    | nan        | active                |
| delta_fixation_total_fixation_duration | Baseline-adjusted total fixation duration | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    2.79242  | 0.247534    | English    | nan                   |
| delta_fixation_total_fixation_duration | Baseline-adjusted total fixation duration | Kruskal-Wallis | language      | English, Punjabi                       |    1.271    | 0.259578    | nan        | passive_dropped_agent |
| delta_saccade_mean_saccade_duration    | Baseline-adjusted saccade duration        | Kruskal-Wallis | language      | English, Punjabi                       |    1.03867  | 0.308132    | nan        | passive_dropped_agent |
| delta_saccade_mean_saccade_amplitude   | Baseline-adjusted saccade amplitude       | Kruskal-Wallis | language      | English, Punjabi                       |    0.985349 | 0.320882    | nan        | passive               |
| delta_saccade_mean_saccade_amplitude   | Baseline-adjusted saccade amplitude       | Kruskal-Wallis | language      | English, Punjabi                       |    0.883165 | 0.347336    | nan        | active                |
| delta_saccade_mean_saccade_amplitude   | Baseline-adjusted saccade amplitude       | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    2.10995  | 0.348201    | Punjabi    | nan                   |
| cognitive_load_index                   | Composite cognitive-load index            | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    1.68741  | 0.430115    | English    | nan                   |
| delta_saccade_saccade_rate             | Baseline-adjusted saccade rate            | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    1.34108  | 0.511433    | Punjabi    | nan                   |
| delta_fixation_fixation_count          | Baseline-adjusted fixation count          | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    1.20194  | 0.54828     | Punjabi    | nan                   |
| delta_fixation_fixation_count          | Baseline-adjusted fixation count          | Kruskal-Wallis | language      | English, Punjabi                       |    0.34847  | 0.55498     | nan        | active                |

## Omnibus Interest-Area Checks

| outcome                               | outcome_label                         | test           | group         | levels                                 |   statistic |     p_value | language   | aoi_role   | sentence_type         |
|:--------------------------------------|:--------------------------------------|:---------------|:--------------|:---------------------------------------|------------:|------------:|:-----------|:-----------|:----------------------|
| dwell_time                            | Dwell time                            | Kruskal-Wallis | aoi_role      | agent, object                          |   14.6666   | 0.000128301 | English    | nan        | passive_dropped_agent |
| dwell_time                            | Dwell time                            | Kruskal-Wallis | aoi_role      | agent, object                          |   13.7103   | 0.000213286 | English    | nan        | passive               |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | Kruskal-Wallis | aoi_role      | agent, object                          |   13.4931   | 0.000239446 | English    | nan        | passive_dropped_agent |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | Kruskal-Wallis | aoi_role      | agent, object                          |   13.3091   | 0.000264119 | English    | nan        | passive               |
| dwell_time                            | Dwell time                            | Kruskal-Wallis | aoi_role      | agent, object                          |   12.8458   | 0.000338241 | Punjabi    | nan        | passive_dropped_agent |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | Kruskal-Wallis | aoi_role      | agent, object                          |   12.3825   | 0.000433384 | Punjabi    | nan        | passive_dropped_agent |
| time_to_first_fixation                | Time to first fixation                | Kruskal-Wallis | aoi_role      | agent, object                          |    8.01894  | 0.00462906  | English    | nan        | passive_dropped_agent |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | Kruskal-Wallis | aoi_role      | agent, object                          |    6.09714  | 0.0135401   | English    | nan        | active                |
| dwell_time                            | Dwell time                            | Kruskal-Wallis | aoi_role      | agent, object                          |    5.86924  | 0.0154077   | English    | nan        | active                |
| dwell_time                            | Dwell time                            | Kruskal-Wallis | language      | English, Punjabi                       |    4.20238  | 0.0403672   | nan        | object     | passive               |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    5.92529  | 0.051682    | Punjabi    | agent      | nan                   |
| entry_count                           | Entry count                           | Kruskal-Wallis | language      | English, Punjabi                       |    3.63412  | 0.0566064   | nan        | agent      | passive               |
| dwell_time                            | Dwell time                            | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    5.39977  | 0.0672133   | Punjabi    | agent      | nan                   |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | Kruskal-Wallis | language      | English, Punjabi                       |    3.24154  | 0.071793    | nan        | agent      | passive               |
| entry_count                           | Entry count                           | Kruskal-Wallis | language      | English, Punjabi                       |    3.22142  | 0.0726804   | nan        | object     | passive               |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | Kruskal-Wallis | language      | English, Punjabi                       |    2.99002  | 0.0837793   | nan        | object     | passive               |
| time_to_first_fixation                | Time to first fixation                | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    4.37968  | 0.111935    | English    | agent      | nan                   |
| dwell_time                            | Dwell time                            | Kruskal-Wallis | language      | English, Punjabi                       |    2.48627  | 0.114844    | nan        | agent      | passive               |
| entry_count                           | Entry count                           | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    3.7808   | 0.151012    | English    | agent      | nan                   |
| time_to_first_fixation                | Time to first fixation                | Kruskal-Wallis | aoi_role      | agent, object                          |    2.00512  | 0.156769    | Punjabi    | nan        | passive_dropped_agent |
| entry_count                           | Entry count                           | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    3.53529  | 0.170734    | English    | object     | nan                   |
| time_to_first_fixation                | Time to first fixation                | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    3.01644  | 0.221304    | Punjabi    | agent      | nan                   |
| time_to_first_fixation                | Time to first fixation                | Kruskal-Wallis | aoi_role      | agent, object                          |    1.45774  | 0.22729     | English    | nan        | active                |
| entry_count                           | Entry count                           | Kruskal-Wallis | language      | English, Punjabi                       |    1.35179  | 0.244965    | nan        | agent      | passive_dropped_agent |
| entry_count                           | Entry count                           | Kruskal-Wallis | language      | English, Punjabi                       |    1.16654  | 0.280113    | nan        | agent      | active                |
| dwell_time                            | Dwell time                            | Kruskal-Wallis | sentence_type | active, passive, passive_dropped_agent |    2.42604  | 0.297299    | Punjabi    | object     | nan                   |
| time_to_first_fixation                | Time to first fixation                | Kruskal-Wallis | aoi_role      | agent, object                          |    1.03607  | 0.308737    | English    | nan        | passive               |
| entry_count                           | Entry count                           | Kruskal-Wallis | aoi_role      | agent, object                          |    0.884334 | 0.347017    | English    | nan        | passive_dropped_agent |
| dwell_time_normalized_by_trial_length | Dwell time normalized by trial length | Kruskal-Wallis | language      | English, Punjabi                       |    0.831463 | 0.36185     | nan        | agent      | active                |
| time_to_first_fixation                | Time to first fixation                | Kruskal-Wallis | language      | English, Punjabi                       |    0.808866 | 0.368456    | nan        | agent      | active                |

## Interpretation Notes

- Use `delta_*` trial outcomes as sentence/audio minus same-participant same-picture free-viewing baseline.
- `aoi_role` is inferred from `ia_label`: `s_` = agent/subject, `o_` = object, everything else = bg.
- These tests do not replace GAMMs because they do not model crossed participant/image effects.
- Treat p-values here as screening evidence for the confirmatory GAMM stage.