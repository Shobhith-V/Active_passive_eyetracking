# Agent-First Analysis Plan

## Theoretical Question

The agent-first principle proposes that comprehenders preferentially expect or process the agent/actor before other event participants. Active sentences usually align with this preference, whereas passive sentences foreground the patient/theme and therefore may create additional processing cost.

## Study-Specific Operationalization

Use sentence type as the first-pass operationalization:

| sentence_type | agent_first_alignment | agent_overt | interpretation |
|---|---|---|---|
| active | agent_first | agent_overt | agent-first aligned |
| passive | non_agent_first | agent_overt | non-agent-first, agent still overt |
| passive_dropped_agent | non_agent_first | agent_dropped | non-agent-first, agent omitted |

## Primary Hypotheses

H1: Passive sentences will be more cognitively taxing than active sentences.

Expected pattern:

```text
passive > active
```

for fixation duration, total dwell time, fixation count, and cognitive-load index.

H2: Non-agent-first sentences will show higher processing cost than agent-first sentences.

Expected pattern:

```text
non_agent_first > agent_first
```

H3: Dropped-agent passives will help distinguish two mechanisms.

Possible outcomes:

```text
passive_dropped_agent ≈ passive > active
```

This suggests non-agent-first structure is the main driver.

```text
passive > passive_dropped_agent > active
```

This suggests both non-agent-first structure and overt-agent integration contribute.

```text
passive_dropped_agent > passive > active
```

This suggests agent omission itself increases processing cost.

H4: The effect may differ by language.

Test:

```text
language × sentence_type
language × agent_first_alignment
```

## Free-Viewing Reference Logic

Use free viewing to control visual salience of the same picture.

For each outcome:

```text
delta_outcome = sentence_audio_outcome - free_viewing_baseline_for_same_picture
```

Preferred baseline:

```text
same participant + same image
```

Fallback baseline:

```text
same image averaged across participants
```

This asks whether the sentence changes looking behavior beyond what the picture itself elicits.

## Primary Dependent Variables

Use these as primary outcomes:

```text
delta_fixation_mean_fixation_duration
delta_fixation_total_fixation_duration
delta_interest_area_total_interest_area_dwell_time
delta_interest_area_interest_area_dwell_time_normalized
delta_saccade_saccade_rate
delta_saccade_mean_saccade_amplitude
cognitive_load_index
```

## Main Models

Sentence-type model:

```r
bam(
  outcome ~ language * sentence_type +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = sentence_audio_baseline_adjusted,
  method = "fREML"
)
```

Agent-first model:

```r
bam(
  outcome ~ language * agent_first_alignment +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = sentence_audio_baseline_adjusted,
  method = "fREML"
)
```

Dropped-agent model among passive trials only:

```r
bam(
  outcome ~ language * agent_overt +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re"),
  data = passive_only,
  method = "fREML"
)
```

## Stronger AOI-Based Agent-First Test

AOI role is automatically inferred from `ia_label`:

```text
s_... = agent/subject
o_... = object
everything else = bg
```

The strongest version of the agent-first analysis uses these inferred event roles:

```text
agent
patient/theme
action/event
background/other
```

Fill:

```text
analysis/aoi_role_lookup_template.csv
```

Then model:

```r
bam(
  dwell_time_normalized_by_trial_length ~ language * sentence_type * aoi_role +
    s(participant_id, bs = "re") +
    s(image_id, bs = "re") +
    s(ia_label, bs = "re"),
  data = interest_area_agent_first_dataset,
  method = "fREML"
)
```

Key prediction:

```text
passive sentences should alter timing or dwell allocation to agent/patient AOIs relative to active sentences, beyond free-viewing salience.
```

## Interpretation Guide

Evidence supporting the agent-first principle:

- Passive conditions show higher baseline-adjusted cognitive-load metrics than active.
- Non-agent-first coding predicts processing cost.
- AOI-role models show delayed or reduced early looks to agents, or increased effort when agent mapping is structurally delayed.
- Effects remain after participant and image random effects.

Evidence against or qualifying the agent-first principle:

- Passive and active do not differ after free-viewing baseline correction.
- Differences are only image-driven and disappear with `image_id` random effects.
- Effects occur in only one language without a theoretically interpretable reason.
- Dropped-agent passive behaves like active, suggesting agent-first order may not be the main driver.

## Reporting Recommendation

Report individual outcomes first, then the cognitive-load index as converging evidence.

Avoid claiming cognitive load from a single dependent variable.
