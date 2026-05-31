# Analysis Validation Report

## Trial Analysis Dataset

Rows: 1800
Columns: 35

### Condition Counts

| language   | sentence_type         | session_type   |   rows |
|:-----------|:----------------------|:---------------|-------:|
| English    | active                | sentence_audio |    150 |
| English    | passive               | sentence_audio |    150 |
| English    | passive_dropped_agent | sentence_audio |    150 |
| Punjabi    | active                | sentence_audio |    150 |
| Punjabi    | passive               | sentence_audio |    150 |
| Punjabi    | passive_dropped_agent | sentence_audio |    150 |
| <missing>  | <missing>             | free_viewing   |    900 |

## Baseline-Adjusted Sentence/Audio Dataset

Rows: 900
Columns: 77

### Baseline Sources

| baseline_source   |   rows |
|:------------------|-------:|
| image             |      2 |
| participant_image |    898 |

### Sentence/Language Counts

| language   | sentence_type         |   rows |
|:-----------|:----------------------|-------:|
| English    | active                |    150 |
| English    | passive               |    150 |
| English    | passive_dropped_agent |    150 |
| Punjabi    | active                |    150 |
| Punjabi    | passive               |    150 |
| Punjabi    | passive_dropped_agent |    150 |

## Agent-First Coding

| sentence_type         | agent_first_alignment   | agent_overt   |   rows |
|:----------------------|:------------------------|:--------------|-------:|
| active                | agent_first             | agent_overt   |    300 |
| passive               | non_agent_first         | agent_overt   |    300 |
| passive_dropped_agent | non_agent_first         | agent_dropped |    300 |

## Interest-Area Agent Dataset

Rows: 3636
Columns: 26

AOI role missing rows: 0

## First AOI Visit Dataset (centre-bias excluded)

Rows: 893

### First AOI visit counts

| language   | sentence_type         | first_aoi_role   |   trials |
|:-----------|:----------------------|:-----------------|---------:|
| English    | active                | agent            |       56 |
| English    | active                | object           |       94 |
| English    | passive               | agent            |       53 |
| English    | passive               | object           |       95 |
| English    | passive_dropped_agent | agent            |       47 |
| English    | passive_dropped_agent | object           |      101 |
| Punjabi    | active                | agent            |       62 |
| Punjabi    | active                | object           |       88 |
| Punjabi    | passive               | agent            |       73 |
| Punjabi    | passive               | object           |       76 |
| Punjabi    | passive_dropped_agent | agent            |       60 |
| Punjabi    | passive_dropped_agent | object           |       88 |

### Proportion agent-first look by condition

| language   | sentence_type         |   prop_agent_first |
|:-----------|:----------------------|-------------------:|
| English    | active                |           0.373333 |
| English    | passive               |           0.358108 |
| English    | passive_dropped_agent |           0.317568 |
| Punjabi    | active                |           0.413333 |
| Punjabi    | passive               |           0.489933 |
| Punjabi    | passive_dropped_agent |           0.405405 |
