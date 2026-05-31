# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this project is

A psycholinguistics eye-tracking study comparing active and passive sentence processing in English and Punjabi. Raw EyeLink reports (fixation, interest area, saccade) are processed into a final trial-level dataset, then analyzed using exploratory Python scripts and primary GAMM models in R.

## Running the pipeline

All commands run from the project root (`/home/shobs/Desktop/punjabi_exp/Active_passive_eyetracking`).

**Step 1 — Process raw EyeLink reports into CSVs:**
```bash
python process_eye_tracking_reports.py
```
Outputs to `data/processed/` and `data/schema_reports/`.

**Step 2 — Prepare analysis-ready datasets:**
```bash
python analysis/prepare_analysis_data.py
```
Outputs to `analysis/derived/`.

**Step 3 — Exploratory statistical checks:**
```bash
python analysis/run_exploratory_analysis.py
```
Outputs to `analysis/results/exploratory/`.

**Step 4 — Primary GAMM models (requires R with `mgcv`):**
```bash
Rscript analysis/run_gamm_models.R
```
Outputs to `analysis/results/gamm/`.

**Step 5 — Consolidated analysis report:**
```bash
python analysis/generate_analysis_report.py
```
Outputs `analysis/analysis_report.md`.

## Dependencies

```bash
pip install -r requirements.txt
```
Key packages: `pandas`, `numpy`, `openpyxl`, `xlrd`, `matplotlib`, `seaborn`, `scipy`, `scikit-learn`.

R package required: `mgcv`.

## Architecture

### Processing pipeline (`process_eye_tracking_reports.py`)

Single-file pipeline that reads all `.xls`/`.tsv` EyeLink report exports from `reports/fixation/`, `reports/interest_area/`, and `reports/saccade_reports/`. Files are named `*_edfNN_*` and participant IDs are extracted from the filename.

Key design decisions:
- `.xls` files are first tried as UTF-16 tab-delimited text (EyeLink's actual export format), with Excel binary as fallback.
- Missing value markers (`"."`, `"UNDEFINED"`, `""`) are normalized to `NaN` on load.
- `sentence_type` (`active` / `passive` / `passive_dropped_agent`) is inferred from the text of `exp_id`, `sentence`, or `audio` columns using regex patterns (ACT→active, PNA/noagent/woa→passive_dropped_agent, PWA/passive→passive).
- `session_type` (`free_viewing` / `sentence_audio`) is inferred from `session_var`/`session` columns.
- Aggregation produces trial-level features (total fixation duration, mean fixation duration, saccade rate, etc.) and interest-area features.
- Schema reports (`data/schema_reports/*.json` and `*.md`) document column coverage across all participant files.

### Analysis pipeline (`analysis/`)

- `prepare_analysis_data.py` — Merges trial features with recovered trial metadata (`image_id`, `exp_id`, `voice_id`), computes free-viewing baselines, subtracts them to produce `delta_*` outcomes, builds a composite `cognitive_load_index` (mean of 5 standardized delta indicators), and adds agent-first coding variables.
- `run_gamm_models.R` — Fits GAMMs (via `mgcv`) with `language × sentence_type`, `language × agent_first_alignment`, and `language × agent_overt` as predictors; random effects for `participant_id` and `image_id`; trial order smooth.
- `aoi_role_lookup_template.csv` — Manual AOI-to-role mapping (`agent` / `object` / `bg`). If left empty, roles are auto-inferred from `ia_label` prefixes: `s_*` = agent, `o_*` = object, everything else = bg.

### Key experimental variables

| Variable | Values | Notes |
|---|---|---|
| `sentence_type` | `active`, `passive`, `passive_dropped_agent` | Inferred from stimulus text |
| `language` | `English`, `Punjabi` | From participant report; normalized from `e`/`p` shorthands |
| `session_type` | `free_viewing`, `sentence_audio` | Free-viewing trials provide same-picture baselines |
| `agent_first_alignment` | `agent_first`, `non_agent_first` | Derived: active=agent_first, both passive variants=non_agent_first |
| `agent_overt` | `agent_overt`, `agent_dropped` | Derived: active+passive=overt, passive_dropped_agent=dropped |

### Data flow

```
reports/{fixation,interest_area,saccade_reports}/*.xls
    → process_eye_tracking_reports.py
    → data/processed/{fixation,interest_area,saccade,final_dataset}.csv
    → analysis/prepare_analysis_data.py
    → analysis/derived/sentence_audio_baseline_adjusted.csv  (primary analysis input)
    → analysis/derived/interest_area_agent_first_dataset.csv (AOI-level analysis input)
    → analysis/run_gamm_models.R
    → analysis/results/gamm/
```
