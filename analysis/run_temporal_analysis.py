"""
Temporal gaze dynamics analysis.

Computes proportion of agent looks over fixation ordinal position (VWP-style)
and over time bins, for sentence-audio trials only.  Fixation index 1 is
excluded (crosshair-return, 87% land at screen centre).

Run from project root after prepare_analysis_data.py:
    python analysis/run_temporal_analysis.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from analysis.prepare_analysis_data import infer_aoi_role_from_label

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed"
OUT = ROOT / "analysis" / "results" / "temporal"
OUT.mkdir(parents=True, exist_ok=True)
PLOT_DIR = OUT / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)

CONDITION_COLORS = {
    ("English", "active"):                "#1f77b4",
    ("English", "passive"):               "#aec7e8",
    ("English", "passive_dropped_agent"): "#6baed6",
    ("Punjabi", "active"):                "#d62728",
    ("Punjabi", "passive"):               "#fc9090",
    ("Punjabi", "passive_dropped_agent"): "#f06060",
}
CONDITION_STYLES = {
    "active": "-",
    "passive": "--",
    "passive_dropped_agent": ":",
}


def load_fixation_data() -> pd.DataFrame:
    path = PROCESSED / "fixation.csv"
    if not path.exists():
        raise FileNotFoundError("data/processed/fixation.csv not found. Run process_eye_tracking_reports.py first.")
    usecols_wanted = [
        "participant_id", "trial_id", "language", "session_type", "sentence_type",
        "current_fix_index", "current_fix_interest_area_label",
        "current_fix_start", "current_fix_duration",
        "current_fix_x", "current_fix_y",
    ]
    available = pd.read_csv(path, nrows=0).columns.tolist()
    usecols = [c for c in usecols_wanted if c in available]
    fix = pd.read_csv(path, usecols=usecols)
    fix = fix[fix["session_type"].eq("sentence_audio")].copy()
    fix["current_fix_index"] = pd.to_numeric(fix["current_fix_index"], errors="coerce")
    # Exclude index 1 — crosshair-return, not a sentence-driven fixation
    fix = fix[fix["current_fix_index"] > 1].copy()
    fix["aoi_role"] = fix["current_fix_interest_area_label"].map(infer_aoi_role_from_label)
    return fix


def compute_proportion_by_fixation_index(fix: pd.DataFrame, max_index: int = 18) -> pd.DataFrame:
    """
    For each fixation_index × language × sentence_type, compute:
      - proportion of fixations on agent
      - proportion on object
      - trial count (number of trials contributing that fixation)
    Only indices 2..max_index are kept (most trials have <18 fixations).
    """
    rows = []
    fix_coded = fix[fix["aoi_role"].isin(["agent", "object"])].copy()
    fix_coded["is_agent"] = (fix_coded["aoi_role"] == "agent").astype(int)

    conditions = fix_coded[["language", "sentence_type"]].drop_duplicates().dropna()
    for _, row in conditions.iterrows():
        lang, stype = row["language"], row["sentence_type"]
        subset = fix_coded[
            fix_coded["language"].eq(lang) & fix_coded["sentence_type"].eq(stype)
        ]
        for idx in range(2, max_index + 1):
            at_idx = subset[subset["current_fix_index"] == idx]
            n_trials = at_idx["participant_id"].nunique() if not at_idx.empty else 0
            n_total = len(at_idx)
            prop_agent = at_idx["is_agent"].mean() if n_total > 0 else np.nan
            rows.append({
                "language": lang,
                "sentence_type": stype,
                "fixation_index": idx,
                "n_fixations": n_total,
                "n_trials_contributing": n_trials,
                "prop_agent_look": prop_agent,
                "prop_object_look": 1 - prop_agent if not np.isnan(prop_agent) else np.nan,
            })
    return pd.DataFrame(rows)


def compute_proportion_by_time_bin(fix: pd.DataFrame, bin_ms: int = 500) -> pd.DataFrame:
    """
    Time-bin agent look proportions.  Time is computed as each fixation's start
    relative to the earliest fixation start within that trial (so bin 0 = time
    from first non-centre fixation, not from absolute trial start).
    """
    fix = fix.copy()
    if "current_fix_start" not in fix.columns:
        return pd.DataFrame()
    fix["current_fix_start"] = pd.to_numeric(fix["current_fix_start"], errors="coerce")
    trial_min = fix.groupby(["participant_id", "trial_id"])["current_fix_start"].transform("min")
    fix["time_from_onset_ms"] = fix["current_fix_start"] - trial_min

    fix["time_bin"] = (fix["time_from_onset_ms"] // bin_ms) * bin_ms
    fix_coded = fix[fix["aoi_role"].isin(["agent", "object"])].copy()
    fix_coded["is_agent"] = (fix_coded["aoi_role"] == "agent").astype(int)

    max_time = int(fix_coded["time_bin"].quantile(0.95))
    fix_coded = fix_coded[fix_coded["time_bin"] <= max_time]

    rows = []
    conditions = fix_coded[["language", "sentence_type"]].drop_duplicates().dropna()
    for _, row in conditions.iterrows():
        lang, stype = row["language"], row["sentence_type"]
        subset = fix_coded[
            fix_coded["language"].eq(lang) & fix_coded["sentence_type"].eq(stype)
        ]
        for tbin in sorted(subset["time_bin"].unique()):
            at_bin = subset[subset["time_bin"] == tbin]
            prop_agent = at_bin["is_agent"].mean() if len(at_bin) > 0 else np.nan
            rows.append({
                "language": lang,
                "sentence_type": stype,
                "time_bin_ms": tbin,
                "n_fixations": len(at_bin),
                "prop_agent_look": prop_agent,
            })
    return pd.DataFrame(rows)


def compute_fixation_index_duration_profile(fix: pd.DataFrame, max_index: int = 18) -> pd.DataFrame:
    """Mean fixation duration at each ordinal position, by condition."""
    if "current_fix_duration" not in fix.columns:
        return pd.DataFrame()
    fix = fix.copy()
    fix["current_fix_duration"] = pd.to_numeric(fix["current_fix_duration"], errors="coerce")
    rows = []
    conditions = fix[["language", "sentence_type"]].drop_duplicates().dropna()
    for _, row in conditions.iterrows():
        lang, stype = row["language"], row["sentence_type"]
        subset = fix[fix["language"].eq(lang) & fix["sentence_type"].eq(stype)]
        for idx in range(2, max_index + 1):
            at_idx = subset[subset["current_fix_index"] == idx]
            rows.append({
                "language": lang,
                "sentence_type": stype,
                "fixation_index": idx,
                "mean_duration_ms": at_idx["current_fix_duration"].mean(),
                "n": len(at_idx),
            })
    return pd.DataFrame(rows)


def plot_proportion_curves(prop_df: pd.DataFrame, x_col: str, x_label: str, filename: str) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, lang in zip(axes, ["English", "Punjabi"]):
        subset = prop_df[prop_df["language"] == lang]
        for stype in ["active", "passive", "passive_dropped_agent"]:
            s = subset[subset["sentence_type"] == stype].sort_values(x_col)
            if s.empty or s["prop_agent_look"].isna().all():
                continue
            color = CONDITION_COLORS.get((lang, stype), "gray")
            linestyle = CONDITION_STYLES.get(stype, "-")
            label = stype.replace("_", " ")
            # Only plot bins with at least 20 fixations for stability
            s_filtered = s[s.get("n_fixations", pd.Series(999, index=s.index)) >= 20] if "n_fixations" in s.columns else s
            ax.plot(s_filtered[x_col], s_filtered["prop_agent_look"],
                    color=color, linestyle=linestyle, linewidth=2, label=label, marker="o", markersize=4)
        ax.axhline(0.5, color="gray", linestyle="--", linewidth=0.8, alpha=0.6)
        ax.set_title(lang, fontsize=13)
        ax.set_xlabel(x_label, fontsize=11)
        ax.set_ylim(0.2, 0.8)
        ax.legend(fontsize=9, loc="upper right")
        ax.set_ylabel("Proportion agent looks", fontsize=11)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Agent-look proportion by condition (fixation index 1 excluded)", fontsize=13, y=1.01)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / filename, dpi=150, bbox_inches="tight")
    plt.close()


def plot_duration_profile(dur_df: pd.DataFrame) -> None:
    if dur_df.empty:
        return
    fig, axes = plt.subplots(1, 2, figsize=(14, 5), sharey=True)
    for ax, lang in zip(axes, ["English", "Punjabi"]):
        subset = dur_df[dur_df["language"] == lang]
        for stype in ["active", "passive", "passive_dropped_agent"]:
            s = subset[subset["sentence_type"] == stype].sort_values("fixation_index")
            if s.empty:
                continue
            color = CONDITION_COLORS.get((lang, stype), "gray")
            linestyle = CONDITION_STYLES.get(stype, "-")
            ax.plot(s["fixation_index"], s["mean_duration_ms"],
                    color=color, linestyle=linestyle, linewidth=2,
                    label=stype.replace("_", " "), marker="o", markersize=4)
        ax.set_title(lang, fontsize=13)
        ax.set_xlabel("Fixation ordinal position", fontsize=11)
        ax.set_ylabel("Mean fixation duration (ms)", fontsize=11)
        ax.legend(fontsize=9)
        ax.grid(axis="y", alpha=0.3)
    fig.suptitle("Fixation duration profile over trial (index 1 excluded)", fontsize=13, y=1.01)
    plt.tight_layout()
    plt.savefig(PLOT_DIR / "fixation_duration_over_index.png", dpi=150, bbox_inches="tight")
    plt.close()


def write_agent_first_summary(fix: pd.DataFrame) -> pd.DataFrame:
    """
    Per-trial binary: did the first AOI fixation (index >= 2) land on agent or object?
    Summarised by condition.
    """
    fix_coded = fix[fix["aoi_role"].isin(["agent", "object"])].copy()
    fix_coded["is_agent"] = (fix_coded["aoi_role"] == "agent").astype(int)
    keys = ["participant_id", "trial_id", "language", "sentence_type"]
    available_keys = [k for k in keys if k in fix_coded.columns]
    first = fix_coded.sort_values("current_fix_index").groupby(available_keys, dropna=False).first().reset_index()
    summary = first.groupby(["language", "sentence_type"], dropna=False)["is_agent"].agg(
        prop_agent_first_look="mean",
        n_trials="count",
    ).reset_index()
    summary["prop_object_first_look"] = 1 - summary["prop_agent_first_look"]
    return summary


def main() -> None:
    print("Loading fixation data...")
    fix = load_fixation_data()
    print(f"  Loaded {len(fix)} fixations (index >= 2, sentence_audio only)")

    print("Computing proportion-by-fixation-index curves...")
    prop_idx = compute_proportion_by_fixation_index(fix)
    prop_idx.to_csv(OUT / "prop_agent_by_fixation_index.csv", index=False)

    print("Computing proportion-by-time-bin curves...")
    prop_time = compute_proportion_by_time_bin(fix)
    if not prop_time.empty:
        prop_time.to_csv(OUT / "prop_agent_by_time_bin.csv", index=False)

    print("Computing fixation duration profile...")
    dur_profile = compute_fixation_index_duration_profile(fix)
    if not dur_profile.empty:
        dur_profile.to_csv(OUT / "fixation_duration_by_index.csv", index=False)

    print("Computing agent-first look summary...")
    first_summary = write_agent_first_summary(fix)
    first_summary.to_csv(OUT / "agent_first_look_summary.csv", index=False)

    print("Plotting...")
    plot_proportion_curves(prop_idx, x_col="fixation_index",
                           x_label="Fixation ordinal position (index 1 excluded)",
                           filename="prop_agent_by_fixation_index.png")
    if not prop_time.empty:
        plot_proportion_curves(prop_time, x_col="time_bin_ms",
                               x_label="Time from first non-centre fixation (ms)",
                               filename="prop_agent_by_time_bin.png")
    plot_duration_profile(dur_profile)

    print("\n=== Agent-First Look Summary ===")
    print(first_summary.to_string(index=False))
    print(f"\nOutputs written to {OUT}")


if __name__ == "__main__":
    main()
