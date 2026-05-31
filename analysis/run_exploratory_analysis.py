from __future__ import annotations

from itertools import combinations
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from scipy import stats


ROOT = Path(__file__).resolve().parents[1]
DERIVED = ROOT / "analysis" / "derived"
OUT = ROOT / "analysis" / "results" / "exploratory"
PLOTS = OUT / "plots"

TRIAL_OUTCOMES = {
    "delta_fixation_mean_fixation_duration": "Baseline-adjusted mean fixation duration",
    "delta_fixation_total_fixation_duration": "Baseline-adjusted total fixation duration",
    "delta_fixation_fixation_count": "Baseline-adjusted fixation count",
    "delta_saccade_saccade_rate": "Baseline-adjusted saccade rate",
    "delta_saccade_mean_saccade_amplitude": "Baseline-adjusted saccade amplitude",
    "delta_saccade_mean_saccade_velocity": "Baseline-adjusted saccade velocity",
    "delta_saccade_mean_saccade_duration": "Baseline-adjusted saccade duration",
    "cognitive_load_index": "Composite cognitive-load index",
}

IA_OUTCOMES = {
    "time_to_first_fixation": "Time to first fixation",
    "dwell_time_normalized_by_trial_length": "Dwell time normalized by trial length",
    "dwell_time": "Dwell time",
    "entry_count": "Entry count",
}


def ensure_inputs() -> tuple[pd.DataFrame, pd.DataFrame]:
    trial_path = DERIVED / "sentence_audio_baseline_adjusted.csv"
    ia_path = DERIVED / "interest_area_agent_first_dataset.csv"
    if not trial_path.exists() or not ia_path.exists():
        raise FileNotFoundError("Run python analysis/prepare_analysis_data.py first.")
    return pd.read_csv(trial_path), pd.read_csv(ia_path)


def summarize(df: pd.DataFrame, group_cols: list[str], outcome_cols: dict[str, str]) -> pd.DataFrame:
    rows = []
    for outcome, label in outcome_cols.items():
        if outcome not in df.columns:
            continue
        grouped = df.groupby(group_cols, dropna=False)[outcome]
        summary = grouped.agg(n="count", mean="mean", sd="std", median="median", min="min", max="max").reset_index()
        summary.insert(0, "outcome", outcome)
        summary.insert(1, "outcome_label", label)
        rows.append(summary)
    return pd.concat(rows, ignore_index=True) if rows else pd.DataFrame()


def kruskal_tests(df: pd.DataFrame, group_col: str, outcome_cols: dict[str, str], strata: list[str] | None = None) -> pd.DataFrame:
    strata = strata or []
    rows = []
    strata_groups = [((), df)] if not strata else df.groupby(strata, dropna=False)
    for strata_values, subset in strata_groups:
        if not isinstance(strata_values, tuple):
            strata_values = (strata_values,)
        for outcome, label in outcome_cols.items():
            if outcome not in subset.columns:
                continue
            valid = subset[[group_col, outcome]].dropna()
            groups = [group[outcome].to_numpy() for _, group in valid.groupby(group_col) if len(group) > 1]
            group_names = [name for name, group in valid.groupby(group_col) if len(group) > 1]
            if len(groups) < 2:
                continue
            statistic, p_value = stats.kruskal(*groups)
            row = {"outcome": outcome, "outcome_label": label, "test": "Kruskal-Wallis", "group": group_col, "levels": ", ".join(map(str, group_names)), "statistic": statistic, "p_value": p_value}
            row.update({name: value for name, value in zip(strata, strata_values)})
            rows.append(row)
    return pd.DataFrame(rows)


def pairwise_mannwhitney(df: pd.DataFrame, group_col: str, outcome_cols: dict[str, str], strata: list[str] | None = None) -> pd.DataFrame:
    strata = strata or []
    rows = []
    strata_groups = [((), df)] if not strata else df.groupby(strata, dropna=False)
    for strata_values, subset in strata_groups:
        if not isinstance(strata_values, tuple):
            strata_values = (strata_values,)
        for outcome, label in outcome_cols.items():
            if outcome not in subset.columns:
                continue
            valid = subset[[group_col, outcome]].dropna()
            levels = list(valid[group_col].dropna().unique())
            for a, b in combinations(levels, 2):
                x = valid.loc[valid[group_col].eq(a), outcome]
                y = valid.loc[valid[group_col].eq(b), outcome]
                if len(x) < 2 or len(y) < 2:
                    continue
                statistic, p_value = stats.mannwhitneyu(x, y, alternative="two-sided")
                row = {
                    "outcome": outcome,
                    "outcome_label": label,
                    "test": "Mann-Whitney U",
                    "group": group_col,
                    "level_a": a,
                    "level_b": b,
                    "mean_a": x.mean(),
                    "mean_b": y.mean(),
                    "mean_difference_a_minus_b": x.mean() - y.mean(),
                    "statistic": statistic,
                    "p_value_uncorrected": p_value,
                }
                row.update({name: value for name, value in zip(strata, strata_values)})
                rows.append(row)
    result = pd.DataFrame(rows)
    if not result.empty:
        result["p_value_bh"] = bh_adjust(result["p_value_uncorrected"])
    return result


def bh_adjust(p_values: pd.Series) -> pd.Series:
    p = p_values.astype(float)
    order = p.argsort()
    ranked = p.iloc[order]
    n = len(ranked)
    adjusted = ranked * n / range(1, n + 1)
    adjusted = adjusted.iloc[::-1].cummin().iloc[::-1].clip(upper=1)
    output = pd.Series(index=ranked.index, data=adjusted)
    return output.reindex(p.index)


def plot_trial_outcomes(trial: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    for outcome, label in TRIAL_OUTCOMES.items():
        if outcome not in trial.columns:
            continue
        plt.figure(figsize=(9, 5))
        sns.pointplot(data=trial, x="sentence_type", y=outcome, hue="language", errorbar=("ci", 95), dodge=True)
        plt.title(label)
        plt.xlabel("Sentence type")
        plt.ylabel(label)
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        plt.savefig(PLOTS / f"trial_{outcome}.png", dpi=200)
        plt.close()


def plot_ia_outcomes(ia: pd.DataFrame) -> None:
    sns.set_theme(style="whitegrid")
    sentence = ia[ia["session_type"].eq("sentence_audio")].copy()
    for outcome, label in IA_OUTCOMES.items():
        if outcome not in sentence.columns:
            continue
        plt.figure(figsize=(10, 5))
        sns.pointplot(data=sentence, x="sentence_type", y=outcome, hue="aoi_role", errorbar=("ci", 95), dodge=True)
        plt.title(f"{label} by sentence type and AOI role")
        plt.xlabel("Sentence type")
        plt.ylabel(label)
        plt.xticks(rotation=20, ha="right")
        plt.tight_layout()
        plt.savefig(PLOTS / f"ia_{outcome}_by_role.png", dpi=200)
        plt.close()


def write_report(trial: pd.DataFrame, ia: pd.DataFrame, trial_tests: pd.DataFrame, ia_tests: pd.DataFrame) -> None:
    lines = ["# Exploratory Analysis Report", ""]
    lines.extend([
        "## Scope",
        "",
        "This report gives initial descriptive and non-parametric checks before the planned GAMM analyses.",
        "The inferential journal models should still use the GAMM templates with participant and image random effects.",
        "",
    ])
    lines.extend(["## Trial-Level Sentence/Language Counts", ""])
    lines.append(trial.groupby(["language", "sentence_type"], dropna=False).size().rename("rows").reset_index().to_markdown(index=False))
    lines.extend(["", "## AOI Role Counts", ""])
    sentence_ia = ia[ia["session_type"].eq("sentence_audio")]
    lines.append(sentence_ia.groupby(["language", "sentence_type", "aoi_role"], dropna=False).size().rename("rows").reset_index().to_markdown(index=False))

    lines.extend(["", "## Omnibus Trial-Level Checks", ""])
    lines.append(trial_tests.sort_values("p_value").head(30).to_markdown(index=False) if not trial_tests.empty else "No tests available.")
    lines.extend(["", "## Omnibus Interest-Area Checks", ""])
    lines.append(ia_tests.sort_values("p_value").head(30).to_markdown(index=False) if not ia_tests.empty else "No tests available.")

    lines.extend([
        "",
        "## Interpretation Notes",
        "",
        "- Use `delta_*` trial outcomes as sentence/audio minus same-participant same-picture free-viewing baseline.",
        "- `aoi_role` is inferred from `ia_label`: `s_` = agent/subject, `o_` = object, everything else = bg.",
        "- These tests do not replace GAMMs because they do not model crossed participant/image effects.",
        "- Treat p-values here as screening evidence for the confirmatory GAMM stage.",
    ])
    (OUT / "exploratory_report.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    PLOTS.mkdir(parents=True, exist_ok=True)
    trial, ia = ensure_inputs()
    ia_sentence = ia[ia["session_type"].eq("sentence_audio")].copy()

    trial_summary = summarize(trial, ["language", "sentence_type", "agent_first_alignment", "agent_overt"], TRIAL_OUTCOMES)
    ia_summary = summarize(ia_sentence, ["language", "sentence_type", "aoi_role"], IA_OUTCOMES)

    trial_summary.to_csv(OUT / "trial_outcome_summary.csv", index=False)
    ia_summary.to_csv(OUT / "interest_area_outcome_summary.csv", index=False)

    trial_tests_sentence = kruskal_tests(trial, "sentence_type", TRIAL_OUTCOMES, strata=["language"])
    trial_tests_language = kruskal_tests(trial, "language", TRIAL_OUTCOMES, strata=["sentence_type"])
    trial_tests = pd.concat([trial_tests_sentence, trial_tests_language], ignore_index=True)
    trial_tests.to_csv(OUT / "trial_omnibus_tests.csv", index=False)

    trial_pairs_sentence = pairwise_mannwhitney(trial, "sentence_type", TRIAL_OUTCOMES, strata=["language"])
    trial_pairs_language = pairwise_mannwhitney(trial, "language", TRIAL_OUTCOMES, strata=["sentence_type"])
    pd.concat([trial_pairs_sentence, trial_pairs_language], ignore_index=True).to_csv(OUT / "trial_pairwise_tests.csv", index=False)

    ia_tests_sentence = kruskal_tests(ia_sentence, "sentence_type", IA_OUTCOMES, strata=["language", "aoi_role"])
    ia_tests_language = kruskal_tests(ia_sentence, "language", IA_OUTCOMES, strata=["sentence_type", "aoi_role"])
    ia_tests_role = kruskal_tests(ia_sentence, "aoi_role", IA_OUTCOMES, strata=["language", "sentence_type"])
    ia_tests = pd.concat([ia_tests_sentence, ia_tests_language, ia_tests_role], ignore_index=True)
    ia_tests.to_csv(OUT / "interest_area_omnibus_tests.csv", index=False)

    ia_pairs_sentence = pairwise_mannwhitney(ia_sentence, "sentence_type", IA_OUTCOMES, strata=["language", "aoi_role"])
    ia_pairs_language = pairwise_mannwhitney(ia_sentence, "language", IA_OUTCOMES, strata=["sentence_type", "aoi_role"])
    ia_pairs_role = pairwise_mannwhitney(ia_sentence, "aoi_role", IA_OUTCOMES, strata=["language", "sentence_type"])
    pd.concat([ia_pairs_sentence, ia_pairs_language, ia_pairs_role], ignore_index=True).to_csv(OUT / "interest_area_pairwise_tests.csv", index=False)

    plot_trial_outcomes(trial)
    plot_ia_outcomes(ia)
    write_report(trial, ia, trial_tests, ia_tests)


if __name__ == "__main__":
    main()
