from __future__ import annotations

import re
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "analysis" / "derived"

TRIAL_OUTCOMES = [
    "fixation_trial_length_ms",
    "fixation_total_fixation_duration",
    "fixation_mean_fixation_duration",
    "fixation_fixation_count",
    "fixation_mean_fixation_x",
    "fixation_mean_fixation_y",
    "interest_area_trial_length_ms",
    "interest_area_total_interest_area_dwell_time",
    "interest_area_total_interest_area_entry_count",
    "interest_area_min_time_to_first_fixation",
    "interest_area_interest_area_dwell_time_normalized",
    "saccade_trial_length_ms",
    "saccade_mean_saccade_amplitude",
    "saccade_saccade_count",
    "saccade_mean_saccade_velocity",
    "saccade_mean_saccade_duration",
    "saccade_saccade_rate",
]

LOAD_COMPONENTS = [
    "delta_fixation_mean_fixation_duration",
    "delta_fixation_total_fixation_duration",
    "delta_fixation_fixation_count",
    "delta_interest_area_total_interest_area_dwell_time",
    "neg_delta_saccade_mean_saccade_amplitude",
]


def first_non_null(series: pd.Series):
    non_null = series.dropna()
    return non_null.iloc[0] if not non_null.empty else pd.NA


def normalize_key_columns(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    result = df.copy()
    for key in keys:
        if key in result.columns:
            result[key] = result[key].astype("string").fillna("<missing>")
    return result


def recover_trial_metadata() -> pd.DataFrame:
    files = ["fixation.csv", "interest_area.csv", "saccade.csv"]
    frames = []
    wanted = [
        "participant_id",
        "trial_id",
        "language",
        "session_type",
        "sentence_type",
        "image_id",
        "image",
        "exp_id",
        "stim_id",
        "stimulus_file",
        "voice_id",
        "audio",
        "sentence",
    ]
    for file_name in files:
        path = PROCESSED / file_name
        if not path.exists():
            continue
        columns = pd.read_csv(path, nrows=0).columns
        usecols = [column for column in wanted if column in columns]
        frame = pd.read_csv(path, usecols=usecols)
        frames.append(frame)

    if not frames:
        raise FileNotFoundError("No processed row-level files found. Run process_eye_tracking_reports.py first.")

    metadata = pd.concat(frames, ignore_index=True, sort=False)
    keys = ["participant_id", "trial_id", "language", "session_type", "sentence_type"]
    metadata = normalize_key_columns(metadata, keys)
    value_cols = [column for column in metadata.columns if column not in keys]
    grouped = metadata.groupby(keys, dropna=False)[value_cols].agg(first_non_null).reset_index()
    for key in keys:
        grouped[key] = grouped[key].replace("<missing>", pd.NA)
    return grouped


def add_agent_first_coding(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    result["grammatical_voice"] = result["sentence_type"].map(
        {
            "active": "active",
            "passive": "passive_with_agent",
            "passive_dropped_agent": "passive_dropped_agent",
        }
    )
    is_active = result["sentence_type"].eq("active").fillna(False).to_numpy(dtype=bool)
    is_passive_family = result["sentence_type"].isin(["passive", "passive_dropped_agent"]).fillna(False).to_numpy(dtype=bool)
    is_overt_agent = result["sentence_type"].isin(["active", "passive"]).fillna(False).to_numpy(dtype=bool)
    is_dropped_agent = result["sentence_type"].eq("passive_dropped_agent").fillna(False).to_numpy(dtype=bool)
    is_passive = result["sentence_type"].eq("passive").fillna(False).to_numpy(dtype=bool)

    result["agent_first_alignment"] = np.select(
        [is_active, is_passive_family],
        ["agent_first", "non_agent_first"],
        default=None,
    )
    result["agent_overt"] = np.select(
        [is_overt_agent, is_dropped_agent],
        ["agent_overt", "agent_dropped"],
        default=None,
    )
    result["passive_cost_contrast"] = np.select(
        [is_active, is_passive_family],
        [0, 1],
        default=np.nan,
    )
    result["dropped_agent_contrast"] = np.select(
        [is_passive, is_dropped_agent],
        [0, 1],
        default=np.nan,
    )
    return result


def attach_metadata(final: pd.DataFrame, metadata: pd.DataFrame) -> pd.DataFrame:
    keys = ["participant_id", "trial_id", "language", "session_type", "sentence_type"]
    left = normalize_key_columns(final, keys)
    right = normalize_key_columns(metadata, keys)
    merged = left.merge(right, on=keys, how="left", validate="many_to_one")
    for key in keys:
        merged[key] = merged[key].replace("<missing>", pd.NA)
    return add_agent_first_coding(merged)


def make_free_viewing_baselines(trial_data: pd.DataFrame) -> pd.DataFrame:
    free = trial_data[trial_data["session_type"].eq("free_viewing")].copy()
    free = free[free["image_id"].notna()].copy()

    participant_baseline = free.groupby(["participant_id", "image_id"], dropna=False)[TRIAL_OUTCOMES].mean().reset_index()
    participant_baseline["baseline_level"] = "participant_image"

    image_baseline = free.groupby(["image_id"], dropna=False)[TRIAL_OUTCOMES].mean().reset_index()
    image_baseline["baseline_level"] = "image"

    participant_baseline.to_csv(OUT / "free_viewing_participant_image_baselines.csv", index=False)
    image_baseline.to_csv(OUT / "free_viewing_image_baselines.csv", index=False)
    return participant_baseline


def add_baseline_adjusted_outcomes(trial_data: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    free = trial_data[trial_data["session_type"].eq("free_viewing") & trial_data["image_id"].notna()].copy()
    sentence = trial_data[trial_data["session_type"].eq("sentence_audio")].copy()

    participant_base = free.groupby(["participant_id", "image_id"], dropna=False)[TRIAL_OUTCOMES].mean().reset_index()
    image_base = free.groupby(["image_id"], dropna=False)[TRIAL_OUTCOMES].mean().reset_index()

    participant_base = participant_base.rename(columns={column: f"baseline_{column}" for column in TRIAL_OUTCOMES})
    image_base = image_base.rename(columns={column: f"image_baseline_{column}" for column in TRIAL_OUTCOMES})

    adjusted = sentence.merge(participant_base, on=["participant_id", "image_id"], how="left")
    adjusted = adjusted.merge(image_base, on="image_id", how="left")
    adjusted["baseline_source"] = np.where(adjusted[f"baseline_{TRIAL_OUTCOMES[0]}"].notna(), "participant_image", "image")

    for outcome in TRIAL_OUTCOMES:
        baseline = adjusted[f"baseline_{outcome}"].combine_first(adjusted[f"image_baseline_{outcome}"])
        adjusted[f"baseline_{outcome}"] = baseline
        adjusted[f"delta_{outcome}"] = adjusted[outcome] - baseline
        adjusted = adjusted.drop(columns=[f"image_baseline_{outcome}"])

    adjusted["neg_delta_saccade_mean_saccade_amplitude"] = -adjusted["delta_saccade_mean_saccade_amplitude"]
    for column in LOAD_COMPONENTS:
        mean = adjusted[column].mean(skipna=True)
        std = adjusted[column].std(skipna=True)
        adjusted[f"z_{column}"] = (adjusted[column] - mean) / std if std and not np.isnan(std) else np.nan
    z_cols = [f"z_{column}" for column in LOAD_COMPONENTS]
    adjusted["cognitive_load_index"] = adjusted[z_cols].mean(axis=1, skipna=True)

    baseline_summary = participant_base.copy()
    return adjusted, baseline_summary


def load_aoi_role_lookup() -> pd.DataFrame | None:
    path = ROOT / "analysis" / "aoi_role_lookup_template.csv"
    if not path.exists():
        pd.DataFrame(columns=["image_id", "ia_label", "aoi_role", "notes"]).to_csv(path, index=False)
        return None
    lookup = pd.read_csv(path)
    if lookup.empty or not {"image_id", "ia_label", "aoi_role"}.issubset(lookup.columns):
        return None
    return lookup


def infer_aoi_role_from_label(label: object) -> str:
    if pd.isna(label):
        return "bg"
    text = str(label).strip().lower()
    if re.match(r"^s(?:_|-|\b)", text):
        return "agent"
    if re.match(r"^o(?:_|-|\b)", text):
        return "object"
    return "bg"


def make_interest_area_agent_dataset(trial_adjusted: pd.DataFrame) -> pd.DataFrame:
    path = PROCESSED / "interest_area_features.csv"
    if not path.exists():
        return pd.DataFrame()
    ia = pd.read_csv(path)
    metadata = recover_trial_metadata()
    keys = ["participant_id", "trial_id", "language", "session_type", "sentence_type"]
    ia = normalize_key_columns(ia, keys).merge(normalize_key_columns(metadata, keys), on=keys, how="left")
    for key in keys:
        ia[key] = ia[key].replace("<missing>", pd.NA)
    ia = add_agent_first_coding(ia)

    lookup = load_aoi_role_lookup()
    if lookup is not None:
        ia = ia.merge(lookup[["image_id", "ia_label", "aoi_role"]], on=["image_id", "ia_label"], how="left")
        ia["aoi_role"] = ia["aoi_role"].fillna(ia["ia_label"].map(infer_aoi_role_from_label))
    else:
        ia["aoi_role"] = ia["ia_label"].map(infer_aoi_role_from_label)
    return ia


def make_first_aoi_visit_dataset(metadata: pd.DataFrame) -> pd.DataFrame:
    """
    For each sentence-audio trial, find the first fixation (index >= 2) that
    lands on a coded AOI (agent or object).  Fixation index 1 is excluded
    because it is the crosshair-return fixation clustered at screen centre.

    Outputs one row per trial with:
      first_aoi_role       - 'agent' | 'object'
      agent_first_look     - 1 if agent, 0 if object
      first_aoi_fix_index  - ordinal position of that fixation
      first_aoi_fix_start  - trial-relative start time (ms)
    """
    path = PROCESSED / "fixation.csv"
    if not path.exists():
        return pd.DataFrame()

    usecols_wanted = [
        "participant_id", "trial_id", "language", "session_type", "sentence_type",
        "current_fix_index", "current_fix_interest_area_label",
        "current_fix_start", "current_fix_x", "current_fix_y",
    ]
    available = pd.read_csv(path, nrows=0).columns.tolist()
    usecols = [c for c in usecols_wanted if c in available]
    fix = pd.read_csv(path, usecols=usecols)

    fix = fix[fix["session_type"].eq("sentence_audio")].copy()
    idx_col = "current_fix_index"
    if idx_col in fix.columns:
        fix = fix[pd.to_numeric(fix[idx_col], errors="coerce") > 1].copy()

    ia_col = "current_fix_interest_area_label"
    if ia_col not in fix.columns:
        return pd.DataFrame()
    fix["aoi_role"] = fix[ia_col].map(infer_aoi_role_from_label)
    fix = fix[fix["aoi_role"].isin(["agent", "object"])].copy()

    if fix.empty:
        return pd.DataFrame()

    fix[idx_col] = pd.to_numeric(fix[idx_col], errors="coerce")
    keys = ["participant_id", "trial_id", "language", "session_type", "sentence_type"]
    available_keys = [k for k in keys if k in fix.columns]

    first_visit = (
        fix.sort_values(idx_col)
        .groupby(available_keys, dropna=False)
        .first()
        .reset_index()
    )
    first_visit = first_visit.rename(columns={
        idx_col: "first_aoi_fix_index",
        "current_fix_start": "first_aoi_fix_start",
        "current_fix_x": "first_aoi_fix_x",
        "current_fix_y": "first_aoi_fix_y",
        "aoi_role": "first_aoi_role",
    })
    first_visit["agent_first_look"] = (first_visit["first_aoi_role"] == "agent").astype(int)

    mkeys = [k for k in keys if k in metadata.columns]
    first_visit = normalize_key_columns(first_visit, mkeys).merge(
        normalize_key_columns(metadata, mkeys), on=mkeys, how="left"
    )
    for k in mkeys:
        first_visit[k] = first_visit[k].replace("<missing>", pd.NA)

    return add_agent_first_coding(first_visit)


def write_dictionary(columns: list[str]) -> None:
    descriptions = {
        "agent_first_alignment": "active=agent_first; passive/passive_dropped_agent=non_agent_first",
        "agent_overt": "active/passive=agent_overt; passive_dropped_agent=agent_dropped",
        "passive_cost_contrast": "0 for active, 1 for passive and passive_dropped_agent",
        "dropped_agent_contrast": "0 for passive, 1 for passive_dropped_agent",
        "cognitive_load_index": "Mean of standardized baseline-adjusted load indicators; larger means greater inferred processing cost",
        "baseline_source": "participant_image if same participant/image free-viewing baseline exists, else image baseline",
    }
    rows = []
    for column in columns:
        if column.startswith("delta_"):
            desc = "Sentence/audio value minus same-picture free-viewing baseline"
        elif column.startswith("baseline_"):
            desc = "Free-viewing baseline for the same image, participant-specific when available"
        else:
            desc = descriptions.get(column, "See source dataset or schema reports")
        rows.append({"column": column, "description": desc})
    pd.DataFrame(rows).to_csv(OUT / "analysis_data_dictionary.csv", index=False)


def write_validation(trial_data: pd.DataFrame, adjusted: pd.DataFrame, ia: pd.DataFrame, first_visit: pd.DataFrame) -> None:
    lines = ["# Analysis Validation Report", ""]
    lines.extend(["## Trial Analysis Dataset", "", f"Rows: {len(trial_data)}", f"Columns: {len(trial_data.columns)}", ""])
    if {"language", "sentence_type", "session_type"}.issubset(trial_data.columns):
        counts = trial_data.groupby(["language", "sentence_type", "session_type"], dropna=False).size().rename("rows").reset_index()
        lines.extend(["### Condition Counts", "", counts.fillna("<missing>").to_markdown(index=False), ""])

    lines.extend(["## Baseline-Adjusted Sentence/Audio Dataset", "", f"Rows: {len(adjusted)}", f"Columns: {len(adjusted.columns)}", ""])
    if not adjusted.empty:
        baseline_counts = adjusted.groupby("baseline_source", dropna=False).size().rename("rows").reset_index()
        lines.extend(["### Baseline Sources", "", baseline_counts.fillna("<missing>").to_markdown(index=False), ""])
        counts = adjusted.groupby(["language", "sentence_type"], dropna=False).size().rename("rows").reset_index()
        lines.extend(["### Sentence/Language Counts", "", counts.fillna("<missing>").to_markdown(index=False), ""])

    lines.extend(["## Agent-First Coding", ""])
    if not adjusted.empty:
        agent_counts = adjusted.groupby(["sentence_type", "agent_first_alignment", "agent_overt"], dropna=False).size().rename("rows").reset_index()
        lines.extend([agent_counts.fillna("<missing>").to_markdown(index=False), ""])

    lines.extend(["## Interest-Area Agent Dataset", "", f"Rows: {len(ia)}", f"Columns: {len(ia.columns)}", ""])
    if not ia.empty and "aoi_role" in ia.columns:
        role_missing = int(ia["aoi_role"].isna().sum())
        lines.append(f"AOI role missing rows: {role_missing}")

    lines.extend(["", "## First AOI Visit Dataset (centre-bias excluded)", "", f"Rows: {len(first_visit)}", ""])
    if not first_visit.empty and "agent_first_look" in first_visit.columns:
        fv_counts = first_visit.groupby(["language", "sentence_type", "first_aoi_role"], dropna=False).size().rename("trials").reset_index()
        lines.extend(["### First AOI visit counts", "", fv_counts.fillna("<missing>").to_markdown(index=False), ""])
        prop = first_visit.groupby(["language", "sentence_type"], dropna=False)["agent_first_look"].mean().rename("prop_agent_first").reset_index()
        lines.extend(["### Proportion agent-first look by condition", "", prop.fillna("<missing>").to_markdown(index=False), ""])
    (OUT / "analysis_validation_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    final = pd.read_csv(PROCESSED / "final_dataset.csv")
    metadata = recover_trial_metadata()
    trial_data = attach_metadata(final, metadata)
    adjusted, baselines = add_baseline_adjusted_outcomes(trial_data)
    ia = make_interest_area_agent_dataset(adjusted)
    first_visit = make_first_aoi_visit_dataset(metadata)

    trial_data.to_csv(OUT / "trial_analysis_dataset.csv", index=False)
    adjusted.to_csv(OUT / "sentence_audio_baseline_adjusted.csv", index=False)
    baselines.to_csv(OUT / "free_viewing_baselines.csv", index=False)
    ia.to_csv(OUT / "interest_area_agent_first_dataset.csv", index=False)
    first_visit.to_csv(OUT / "first_aoi_visit_dataset.csv", index=False)
    write_dictionary(list(adjusted.columns))
    write_validation(trial_data, adjusted, ia, first_visit)


if __name__ == "__main__":
    main()
