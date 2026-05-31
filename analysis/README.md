# Analysis Pipeline

This folder contains a followable analysis pipeline for testing sentence-type, language, cognitive-load, and agent-first hypotheses using the processed eye-tracking datasets.

## Inputs

Run the processing pipeline first from the project root:

```bash
python process_eye_tracking_reports.py
```

Required processed inputs:

```text
data/processed/final_dataset.csv
data/processed/fixation.csv
data/processed/interest_area.csv
data/processed/saccade.csv
data/processed/interest_area_features.csv
```

## Outputs

The analysis preparation script writes:

```text
analysis/derived/trial_analysis_dataset.csv
analysis/derived/sentence_audio_baseline_adjusted.csv
analysis/derived/free_viewing_baselines.csv
analysis/derived/interest_area_agent_first_dataset.csv
analysis/derived/analysis_data_dictionary.csv
analysis/derived/analysis_validation_report.md
```

## Step 1: Prepare Analysis Data

From the project root:

```bash
python analysis/prepare_analysis_data.py
```

This creates:

- Trial-level data with recovered `image_id`, `exp_id`, `stim_id`, and `voice_id`.
- Same-picture free-viewing baselines.
- Baseline-adjusted sentence/audio outcomes.
- Cognitive-load indicators and a composite `cognitive_load_index`.
- Agent-first coding variables.

AOI role coding is inferred from `ia_label`:

```text
s_... = agent/subject
o_... = object
everything else = bg
```

## Step 1b: Run Exploratory Checks

From the project root:

```bash
python analysis/run_exploratory_analysis.py
```

This writes:

```text
analysis/results/exploratory/exploratory_report.md
analysis/results/exploratory/trial_outcome_summary.csv
analysis/results/exploratory/interest_area_outcome_summary.csv
analysis/results/exploratory/trial_omnibus_tests.csv
analysis/results/exploratory/trial_pairwise_tests.csv
analysis/results/exploratory/interest_area_omnibus_tests.csv
analysis/results/exploratory/interest_area_pairwise_tests.csv
analysis/results/exploratory/plots/
```

Initial checks include:

- Time to first fixation/view by `language × sentence_type × aoi_role`.
- Fixation duration and fixation count by `language × sentence_type`.
- Saccade rate, amplitude, velocity, and duration by `language × sentence_type`.
- Baseline-adjusted outcomes using same-participant same-picture free-viewing baselines.

These are screening analyses, not replacements for the final GAMMs.

## Step 2: Check Design Balance

Review:

```text
analysis/derived/analysis_validation_report.md
```

Check that each `language × sentence_type` condition has expected trials and that baseline matching worked.

## Step 3: Primary GAMM Models

Run:

```bash
Rscript analysis/run_gamm_models.R
```

This writes:

```text
analysis/results/gamm/gamm_model_fit.csv
analysis/results/gamm/gamm_parametric_terms.csv
analysis/results/gamm/gamm_smooth_terms.csv
analysis/results/gamm/gamm_significant_parametric_terms.csv
analysis/results/gamm/*_summary.txt
analysis/results/gamm/plots/
```

Reference templates are also available in:

```text
analysis/gamm_model_templates.R
```

Primary outcomes:

```text
delta_fixation_mean_fixation_duration
delta_fixation_total_fixation_duration
delta_interest_area_total_interest_area_dwell_time
delta_interest_area_interest_area_dwell_time_normalized
delta_saccade_saccade_rate
delta_saccade_mean_saccade_amplitude
cognitive_load_index
```

Primary predictors:

```text
language * sentence_type
language * agent_first_alignment
language * agent_overt
```

Random effects:

```text
participant_id
image_id
```

## Step 4: Agent-First Hypothesis

The agent-first principle predicts easier processing when the first-mentioned/foregrounded event participant is the agent.

In this study, the simplest coding is:

```text
active = agent_first_aligned
passive = non_agent_first
passive_dropped_agent = non_agent_first, agent_not_overt
```

Core tests:

- `active` vs `passive`: does non-agent-first passive increase processing cost?
- `active` vs `passive_dropped_agent`: does removing the overt agent reduce or increase cost?
- `passive` vs `passive_dropped_agent`: is cost driven by non-agent-first order or by the presence/absence of an overt agent?
- `language × sentence_type`: does the agent-first effect differ between English and Punjabi?

## Step 5: Cognitive Load Interpretation

Treat cognitive load as converging evidence across multiple outcomes, not one measure.

Expected passive-cost pattern:

```text
passive > active for fixation duration
passive > active for dwell time
passive > active for fixation count
passive < active for saccade amplitude
passive may show lower saccade rate if fixations are longer
```

The prepared `cognitive_load_index` combines standardized indicators:

```text
mean fixation duration
total fixation duration
fixation count
interest-area dwell time
negative saccade amplitude
```

Report the composite as secondary unless you pre-register or strongly justify it.

## Step 6: Interest-Area / AOI Role Analysis

For a stronger agent-first paper, map AOIs to event roles:

```text
agent
patient/theme
action/event
background/other
```

Optionally refine the automatic AOI-role coding in:

```text
analysis/aoi_role_lookup_template.csv
```

Then rerun:

```bash
python analysis/prepare_analysis_data.py
```

This enables models such as:

```text
dwell_time ~ language * sentence_type * aoi_role
time_to_first_fixation ~ language * sentence_type * aoi_role
```

These directly test whether passive sentences shift attention away from the agent or delay agent looks.

## Step 7: Generate Consolidated Report

After exploratory analyses and GAMMs have run:

```bash
python analysis/generate_analysis_report.py
```

This writes:

```text
analysis/analysis_report.md
```

The report includes data preparation, free-viewing baseline strategy, exploratory findings, GAMM results, interpretations, and manuscript figure placeholders.

## Recommended Journal Framing

Main claim if supported:

```text
Passive sentence processing produced greater gaze-based processing cost than active sentence processing after controlling for same-picture free-viewing baselines. This pattern is consistent with the agent-first principle because non-agent-first sentence structures elicited increased fixation/dwell-time costs. The magnitude of this effect differed/did not differ across English and Punjabi.
```

Important caution:

```text
The agent-first interpretation is strongest if AOIs can be mapped to agent and patient/theme roles. Without AOI role coding, the study can test processing cost associated with active/passive structure, but the agent-first claim is more indirect.
```
