from __future__ import annotations

import argparse
import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


REPORTS = {
    "fixation": Path("reports/fixation"),
    "interest_area": Path("reports/interest_area"),
    "saccade": Path("reports/saccade_reports"),
}

MISSING_MARKERS = [".", "UNDEFINED", "undefined", "", " "]
METADATA_COLUMNS = ["participant_id", "language", "session_type", "sentence_type"]


@dataclass
class LoadedReport:
    report_type: str
    path: Path
    data: pd.DataFrame


def normalize_column_name(name: object) -> str:
    text = str(name).strip().lower()
    text = text.replace("%", "pct")
    text = re.sub(r"[^0-9a-zA-Z]+", "_", text)
    text = re.sub(r"_+", "_", text).strip("_")
    return text


def make_unique_columns(columns: Iterable[object]) -> list[str]:
    seen: dict[str, int] = {}
    unique = []
    for column in columns:
        base = normalize_column_name(column) or "unnamed"
        seen[base] = seen.get(base, 0) + 1
        unique.append(base if seen[base] == 1 else f"{base}_{seen[base]}")
    return unique


def participant_from_filename(path: Path) -> str:
    match = re.search(r"(edf\d+)", path.stem, flags=re.IGNORECASE)
    return match.group(1).lower() if match else path.stem


def read_report_file(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix in {".xls", ".txt", ".tsv", ".csv"}:
        for encoding in ("utf-16", "utf-8-sig", "utf-8", "latin1"):
            try:
                return pd.read_csv(
                    path,
                    sep="\t" if suffix != ".csv" else None,
                    engine="python",
                    encoding=encoding,
                    na_values=MISSING_MARKERS,
                    keep_default_na=True,
                )
            except UnicodeError:
                continue
            except pd.errors.ParserError:
                continue
    if suffix in {".xlsx", ".xlsm", ".xls"}:
        return pd.read_excel(path, na_values=MISSING_MARKERS)
    raise ValueError(f"Unsupported report format: {path}")


def coerce_data_types(df: pd.DataFrame) -> pd.DataFrame:
    result = df.copy()
    for column in result.columns:
        if column in METADATA_COLUMNS:
            result[column] = result[column].astype("string")
            continue
        if result[column].dtype == object:
            non_null = result[column].dropna()
            lowered = non_null.astype(str).str.lower().unique()
            if len(lowered) and set(lowered).issubset({"true", "false"}):
                result[column] = result[column].astype(str).str.lower().map({"true": True, "false": False})
                continue
            numeric = pd.to_numeric(result[column], errors="coerce")
            if non_null.empty or numeric.notna().sum() / max(len(non_null), 1) >= 0.9:
                result[column] = numeric
    return result


def first_existing(df: pd.DataFrame, candidates: Iterable[str]) -> str | None:
    for candidate in candidates:
        if candidate in df.columns:
            return candidate
    return None


def normalize_language(series: pd.Series | None) -> pd.Series:
    if series is None:
        return pd.Series(pd.NA, dtype="string")
    lowered = series.astype("string").str.strip().str.lower()
    return lowered.map({"english": "English", "punjabi": "Punjabi", "e": "English", "p": "Punjabi"}).astype("string")


def infer_session_type(df: pd.DataFrame) -> pd.Series:
    source = first_existing(df, ["session_var", "session", "session_type"])
    if source is None:
        return pd.Series(pd.NA, index=df.index, dtype="string")
    values = df[source].astype("string").str.lower()
    inferred = np.select(
        [
            values.str.contains("free", na=False).to_numpy(dtype=bool),
            values.str.contains("experiment|sentence|audio", na=False).to_numpy(dtype=bool),
        ],
        ["free_viewing", "sentence_audio"],
        default=None,
    )
    return pd.Series(inferred, index=df.index, dtype="string")


def infer_sentence_type(df: pd.DataFrame) -> pd.Series:
    pieces = []
    for column in ["exp_id", "sentence", "audio", "stimulus_file", "stim_id"]:
        if column in df.columns:
            pieces.append(df[column].astype("string"))
    if not pieces:
        return pd.Series(pd.NA, index=df.index, dtype="string")
    text = pd.concat(pieces, axis=1).fillna("").agg(" ".join, axis=1).str.lower()
    inferred = np.select(
        [
            text.str.contains(r"(?:^|[_/\\\s-])act(?:$|[_/\\\s-])|\bactive\b", regex=True, na=False).to_numpy(dtype=bool),
            text.str.contains(r"pna|noagent|woa|without_agent|dropped", regex=True, na=False).to_numpy(dtype=bool),
            text.str.contains(r"pwa|passive", regex=True, na=False).to_numpy(dtype=bool),
        ],
        ["active", "passive_dropped_agent", "passive"],
        default=None,
    )
    return pd.Series(inferred, index=df.index, dtype="string")


def add_standard_metadata(df: pd.DataFrame, path: Path) -> pd.DataFrame:
    result = df.copy()
    result.insert(0, "source_file", path.name)
    result.insert(0, "participant_id", participant_from_filename(path))
    if "language" in result.columns:
        result["language"] = normalize_language(result["language"])
    else:
        result["language"] = pd.NA
    result["session_type"] = infer_session_type(result)
    result["sentence_type"] = infer_sentence_type(result)
    result.loc[result["session_type"].eq("free_viewing"), "sentence_type"] = pd.NA
    if "trial_id" not in result.columns:
        trial_col = first_existing(result, ["trial_index", "trial_label", "ip_index", "ip_label"])
        result["trial_id"] = result[trial_col].astype("string") if trial_col else pd.NA
    return result


def load_and_standardize(report_type: str, path: Path) -> LoadedReport:
    df = read_report_file(path)
    df.columns = make_unique_columns(df.columns)
    df = add_standard_metadata(df, path)
    df = coerce_data_types(df)
    return LoadedReport(report_type=report_type, path=path, data=df)


def numeric_summary(df: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    numeric = df.select_dtypes(include="number")
    summary = numeric.agg(["mean", "std", "min", "max"]).replace({np.nan: None})
    return summary.to_dict() if not summary.empty else {}


def write_schema_report(report_type: str, loaded: list[LoadedReport], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    all_columns = [set(item.data.columns) for item in loaded]
    common = sorted(set.intersection(*all_columns)) if all_columns else []
    union = sorted(set.union(*all_columns)) if all_columns else []
    inconsistent = {
        column: [item.path.name for item in loaded if column not in item.data.columns]
        for column in union
        if any(column not in item.data.columns for item in loaded)
    }
    report = {
        "report_type": report_type,
        "file_count": len(loaded),
        "common_columns": common,
        "inconsistent_columns_missing_by_file": inconsistent,
        "files": [],
    }
    sample_items = loaded[:3]
    for item in loaded:
        df = item.data
        entry = {
            "file": item.path.name,
            "rows": int(len(df)),
            "columns": list(df.columns),
            "dtypes": {column: str(dtype) for column, dtype in df.dtypes.items()},
            "missing_values": {column: int(count) for column, count in df.isna().sum().items() if count > 0},
            "numeric_summary": numeric_summary(df),
        }
        if item in sample_items:
            entry["sample_rows"] = df.head(3).replace({np.nan: None}).to_dict(orient="records")
        report["files"].append(entry)
    (output_dir / f"{report_type}_schema.json").write_text(json.dumps(report, indent=2), encoding="utf-8")

    lines = [f"# {report_type} schema", "", f"Files inspected: {len(loaded)}", "", "## Common columns", ""]
    lines.extend(f"- `{column}`" for column in common)
    lines.extend(["", "## Inconsistent columns", ""])
    if inconsistent:
        lines.extend(f"- `{column}` missing in {len(files)} file(s)" for column, files in inconsistent.items())
    else:
        lines.append("- None detected")
    lines.extend(["", "## Sample files", ""])
    for item in sample_items:
        lines.extend([
            f"### {item.path.name}",
            "",
            f"Rows: {len(item.data)}, columns: {len(item.data.columns)}",
            "",
            "First rows:",
            "",
            item.data.head(3).to_markdown(index=False),
            "",
        ])
    (output_dir / f"{report_type}_schema.md").write_text("\n".join(lines), encoding="utf-8")


def load_report_type(report_type: str, directory: Path) -> pd.DataFrame:
    paths = sorted([path for path in directory.iterdir() if path.is_file()])
    loaded = [load_and_standardize(report_type, path) for path in paths]
    write_schema_report(report_type, loaded, Path("data/schema_reports"))
    if not loaded:
        return pd.DataFrame()
    return pd.concat([item.data for item in loaded], ignore_index=True, sort=False)


def trial_length_ms(df: pd.DataFrame) -> pd.Series:
    start_col = first_existing(df, ["trial_start_time", "ip_start_time"])
    end_col = first_existing(
        df,
        [
            "ip_end_time",
            "current_fix_end",
            "current_sac_end_time",
            "ia_end_time",
            "trial_dwell_time",
        ],
    )
    if start_col and end_col:
        return pd.to_numeric(df[end_col], errors="coerce") - pd.to_numeric(df[start_col], errors="coerce")
    if "trial_dwell_time" in df.columns:
        return pd.to_numeric(df["trial_dwell_time"], errors="coerce")
    return pd.Series(np.nan, index=df.index)


def group_keys(df: pd.DataFrame, include_interest_area: bool = False) -> list[str]:
    keys = ["participant_id", "trial_id", "language", "session_type", "sentence_type"]
    if include_interest_area:
        ia_col = first_existing(df, ["ia_label", "current_fix_interest_area_label", "current_sac_end_interest_area_label"])
        if ia_col and ia_col not in keys:
            keys.append(ia_col)
    return [key for key in keys if key in df.columns]


def aggregate_fixations(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    duration = first_existing(df, ["current_fix_duration", "fixation_duration", "duration"])
    x_col = first_existing(df, ["current_fix_x", "fix_x", "x"])
    y_col = first_existing(df, ["current_fix_y", "fix_y", "y"])
    work = df.copy()
    work["trial_length_ms"] = trial_length_ms(work)
    aggregations = {"trial_length_ms": "max"}
    if duration:
        work[duration] = pd.to_numeric(work[duration], errors="coerce")
        aggregations[duration] = ["sum", "mean", "count"]
    if x_col:
        aggregations[x_col] = "mean"
    if y_col:
        aggregations[y_col] = "mean"
    grouped = work.groupby(group_keys(work), dropna=False).agg(aggregations)
    grouped.columns = ["_".join(filter(None, col)).strip("_") if isinstance(col, tuple) else col for col in grouped.columns]
    grouped = grouped.reset_index()
    rename = {"trial_length_ms_max": "trial_length_ms"}
    if duration:
        rename.update({
            f"{duration}_sum": "total_fixation_duration",
            f"{duration}_mean": "mean_fixation_duration",
            f"{duration}_count": "fixation_count",
        })
    if x_col:
        rename[f"{x_col}_mean"] = "mean_fixation_x"
    if y_col:
        rename[f"{y_col}_mean"] = "mean_fixation_y"
    return grouped.rename(columns=rename)


def aggregate_interest_areas(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if df.empty:
        return pd.DataFrame(), pd.DataFrame()
    dwell = first_existing(df, ["ia_dwell_time", "dwell_time"])
    entry_count = first_existing(df, ["ia_run_count", "ia_instances_count", "ia_fixation_count"])
    tff = first_existing(df, ["ia_first_fixation_time", "time_to_first_fixation"])
    trial_dwell = first_existing(df, ["trial_dwell_time", "trial_length_ms"])
    work = df.copy()
    if trial_dwell is None:
        work["trial_length_ms"] = trial_length_ms(work)
        trial_dwell = "trial_length_ms"
    aggregations = {trial_dwell: "max"}
    if dwell:
        work[dwell] = pd.to_numeric(work[dwell], errors="coerce")
        aggregations[dwell] = "sum"
    if entry_count:
        aggregations[entry_count] = "sum"
    if tff:
        aggregations[tff] = ["min", "mean"]
    by_area = work.groupby(group_keys(work, include_interest_area=True), dropna=False).agg(aggregations)
    by_area.columns = ["_".join(filter(None, col)).strip("_") if isinstance(col, tuple) else col for col in by_area.columns]
    by_area = by_area.reset_index()
    rename = {f"{trial_dwell}_max": "trial_length_ms"}
    if dwell:
        rename[f"{dwell}_sum"] = "dwell_time"
    if entry_count:
        rename[f"{entry_count}_sum"] = "entry_count"
    if tff:
        rename.update({f"{tff}_min": "time_to_first_fixation", f"{tff}_mean": "mean_time_to_first_fixation"})
    by_area = by_area.rename(columns=rename)
    if "dwell_time" in by_area.columns and "trial_length_ms" in by_area.columns:
        by_area["dwell_time_normalized_by_trial_length"] = by_area["dwell_time"] / by_area["trial_length_ms"].replace(0, np.nan)

    trial_aggs = {"trial_length_ms": "max"} if "trial_length_ms" in by_area.columns else {}
    if "dwell_time" in by_area.columns:
        trial_aggs["dwell_time"] = "sum"
    if "entry_count" in by_area.columns:
        trial_aggs["entry_count"] = "sum"
    if "time_to_first_fixation" in by_area.columns:
        trial_aggs["time_to_first_fixation"] = "min"
    trial = by_area.groupby(group_keys(by_area), dropna=False).agg(trial_aggs).reset_index()
    trial = trial.rename(
        columns={
            "dwell_time": "total_interest_area_dwell_time",
            "entry_count": "total_interest_area_entry_count",
            "time_to_first_fixation": "min_time_to_first_fixation",
        }
    )
    if "total_interest_area_dwell_time" in trial.columns and "trial_length_ms" in trial.columns:
        trial["interest_area_dwell_time_normalized"] = trial["total_interest_area_dwell_time"] / trial["trial_length_ms"].replace(0, np.nan)
    return by_area, trial


def aggregate_saccades(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame()
    amplitude = first_existing(df, ["current_sac_amplitude", "saccade_amplitude"])
    velocity = first_existing(df, ["current_sac_avg_velocity", "current_sac_peak_velocity", "saccade_velocity"])
    duration = first_existing(df, ["current_sac_duration", "saccade_duration"])
    work = df.copy()
    work["trial_length_ms"] = trial_length_ms(work)
    aggregations = {"trial_length_ms": "max"}
    for column in [amplitude, velocity, duration]:
        if column:
            work[column] = pd.to_numeric(work[column], errors="coerce")
            aggregations[column] = ["mean", "count"] if column == amplitude else "mean"
    grouped = work.groupby(group_keys(work), dropna=False).agg(aggregations)
    grouped.columns = ["_".join(filter(None, col)).strip("_") if isinstance(col, tuple) else col for col in grouped.columns]
    grouped = grouped.reset_index()
    rename = {"trial_length_ms_max": "trial_length_ms"}
    if amplitude:
        rename.update({f"{amplitude}_mean": "mean_saccade_amplitude", f"{amplitude}_count": "saccade_count"})
    if velocity:
        rename[f"{velocity}_mean"] = "mean_saccade_velocity"
    if duration:
        rename[f"{duration}_mean"] = "mean_saccade_duration"
    grouped = grouped.rename(columns=rename)
    if "saccade_count" in grouped.columns:
        grouped["saccade_rate"] = grouped["saccade_count"] / (grouped["trial_length_ms"].replace(0, np.nan) / 1000)
    return grouped


def merge_trial_datasets(fix: pd.DataFrame, ia: pd.DataFrame, sac: pd.DataFrame) -> pd.DataFrame:
    datasets = [("fixation", fix), ("interest_area", ia), ("saccade", sac)]
    merged: pd.DataFrame | None = None
    for name, df in datasets:
        if df.empty:
            continue
        keys = group_keys(df)
        value_cols = [column for column in df.columns if column not in keys]
        renamed = df[keys + value_cols].rename(columns={column: f"{name}_{column}" for column in value_cols})
        merged = renamed if merged is None else merged.merge(renamed, on=keys, how="outer")
    return merged if merged is not None else pd.DataFrame()


def write_assumptions(outputs: dict[str, pd.DataFrame], output_dir: Path) -> None:
    rows = [
        {
            "topic": "file_format",
            "assumption": ".xls reports are read as UTF-16 tab-delimited EyeLink text exports, with Excel fallback.",
            "impact": "Preserves original export columns while allowing non-binary .xls files to load reproducibly.",
        },
        {
            "topic": "missing_values",
            "assumption": "'.', 'UNDEFINED', empty strings, and pandas default NA markers are treated as missing.",
            "impact": "Raw placeholder values become nulls in processed datasets and validation reports.",
        },
        {
            "topic": "sentence_type",
            "assumption": "exp_id/sentence/audio text containing ACT is active; PNA/noagent/woa is passive_dropped_agent; PWA/passive is passive.",
            "impact": "Rows that cannot match these patterns remain null rather than being guessed.",
        },
        {
            "topic": "session_type",
            "assumption": "session_var containing free is free_viewing; experiment/sentence/audio is sentence_audio.",
            "impact": "Unknown session values remain null.",
        },
    ]
    for name, df in outputs.items():
        if df.empty:
            rows.append({"topic": f"{name}_empty", "assumption": f"No rows loaded for {name}.", "impact": "Related output is empty."})
            continue
        for column in METADATA_COLUMNS + ["trial_id"]:
            if column in df.columns:
                missing = int(df[column].isna().sum())
                if missing:
                    rows.append({
                        "topic": f"{name}_{column}_missing",
                        "assumption": f"{missing} row(s) have unresolved {column}.",
                        "impact": "These rows are retained with null metadata for transparent downstream filtering.",
                    })
    pd.DataFrame(rows).to_csv(output_dir / "assumptions_log.csv", index=False)


def write_validation_report(outputs: dict[str, pd.DataFrame], final: pd.DataFrame, output_dir: Path) -> None:
    lines = ["# Validation report", ""]
    for name, df in outputs.items():
        lines.extend([f"## {name}", "", f"Rows: {len(df)}", f"Columns: {len(df.columns)}", ""])
        if not df.empty and "participant_id" in df.columns:
            lines.extend(["### Row counts per participant", "", df.groupby("participant_id", dropna=False).size().rename("rows").to_markdown(), ""])
        metadata_cols = [column for column in ["language", "sentence_type", "session_type"] if column in df.columns]
        if metadata_cols:
            condition_counts = df.groupby(metadata_cols, dropna=False).size().rename("rows").reset_index()
            lines.extend(["### Condition distribution", "", condition_counts.fillna("<missing>").to_markdown(index=False), ""])
        missing = df.isna().sum().loc[lambda value: value > 0].sort_values(ascending=False).head(30)
        lines.extend(["### Top missing columns", "", missing.to_markdown() if not missing.empty else "No missing values detected.", ""])
    lines.extend(["## final_dataset", "", f"Rows: {len(final)}", f"Columns: {len(final.columns)}", ""])
    if not final.empty:
        lines.extend(["### Condition distribution", ""])
        metadata_cols = [column for column in ["language", "sentence_type", "session_type"] if column in final.columns]
        if metadata_cols:
            final_counts = final.groupby(metadata_cols, dropna=False).size().rename("rows").reset_index()
            lines.append(final_counts.fillna("<missing>").to_markdown(index=False))
    (output_dir / "validation_report.md").write_text("\n".join(lines), encoding="utf-8")


def create_metadata_lookup_template(output_dir: Path) -> None:
    path = output_dir / "metadata_lookup_template.csv"
    if not path.exists():
        pd.DataFrame(columns=["participant_id", "trial_id", "language", "session_type", "sentence_type", "notes"]).to_csv(path, index=False)


def run_pipeline(root: Path) -> None:
    processed_dir = root / "data/processed"
    schema_dir = root / "data/schema_reports"
    processed_dir.mkdir(parents=True, exist_ok=True)
    schema_dir.mkdir(parents=True, exist_ok=True)

    outputs: dict[str, pd.DataFrame] = {}
    for report_type, relative_dir in REPORTS.items():
        df = load_report_type(report_type, root / relative_dir)
        outputs[report_type] = df
        output_name = "saccade.csv" if report_type == "saccade" else f"{report_type}.csv"
        df.to_csv(processed_dir / output_name, index=False)

    # Exclude fixation index 1 from trial-level aggregation: it is the crosshair-return
    # fixation (87 % land within 100 px of screen centre) and carries no sentence-processing
    # signal. The raw fixation.csv above retains all rows for temporal/first-look analyses.
    fix_idx_col = first_existing(outputs["fixation"], ["current_fix_index", "fix_index"])
    if fix_idx_col:
        fix_for_agg = outputs["fixation"][
            pd.to_numeric(outputs["fixation"][fix_idx_col], errors="coerce") > 1
        ].copy()
    else:
        fix_for_agg = outputs["fixation"]
    fixation_trial = aggregate_fixations(fix_for_agg)
    ia_by_area, ia_trial = aggregate_interest_areas(outputs["interest_area"])
    saccade_trial = aggregate_saccades(outputs["saccade"])

    fixation_trial.to_csv(processed_dir / "fixation_trial_features.csv", index=False)
    ia_by_area.to_csv(processed_dir / "interest_area_features.csv", index=False)
    ia_trial.to_csv(processed_dir / "interest_area_trial_features.csv", index=False)
    saccade_trial.to_csv(processed_dir / "saccade_trial_features.csv", index=False)

    final = merge_trial_datasets(fixation_trial, ia_trial, saccade_trial)
    final.to_csv(processed_dir / "final_dataset.csv", index=False)

    create_metadata_lookup_template(root / "data")
    write_assumptions(outputs, processed_dir)
    write_validation_report(outputs, final, processed_dir)


def main() -> None:
    parser = argparse.ArgumentParser(description="Standardize and consolidate EyeLink eye-tracking reports.")
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="Project root containing reports/.")
    args = parser.parse_args()
    run_pipeline(args.root.resolve())


if __name__ == "__main__":
    main()
