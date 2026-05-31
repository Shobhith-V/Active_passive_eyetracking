from __future__ import annotations

from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ANALYSIS = ROOT / "analysis"
DERIVED = ANALYSIS / "derived"
EXPLORATORY = ANALYSIS / "results" / "exploratory"
GAMM = ANALYSIS / "results" / "gamm"
REPORT = ANALYSIS / "analysis_report.md"


def fmt_p(value: float) -> str:
    if pd.isna(value):
        return ""
    if value < 0.001:
        return f"{value:.2e}"
    return f"{value:.3f}"


def table_or_note(df: pd.DataFrame, columns: list[str], max_rows: int = 20) -> str:
    if df.empty:
        return "No rows available."
    existing = [column for column in columns if column in df.columns]
    return df[existing].head(max_rows).to_markdown(index=False)


def condition_counts() -> str:
    path = DERIVED / "sentence_audio_baseline_adjusted.csv"
    df = pd.read_csv(path)
    counts = df.groupby(["language", "sentence_type", "agent_first_alignment", "agent_overt"], dropna=False).size().rename("rows").reset_index()
    return counts.to_markdown(index=False)


def aoi_counts() -> str:
    path = DERIVED / "interest_area_agent_first_dataset.csv"
    df = pd.read_csv(path)
    df = df[df["session_type"].eq("sentence_audio")]
    counts = df.groupby(["language", "sentence_type", "aoi_role"], dropna=False).size().rename("rows").reset_index()
    return counts.to_markdown(index=False)


def get_exploratory_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    trial_summary = pd.read_csv(EXPLORATORY / "trial_outcome_summary.csv")
    ia_summary = pd.read_csv(EXPLORATORY / "interest_area_outcome_summary.csv")
    trial_tests = pd.read_csv(EXPLORATORY / "trial_omnibus_tests.csv").sort_values("p_value")
    ia_tests = pd.read_csv(EXPLORATORY / "interest_area_omnibus_tests.csv").sort_values("p_value")
    trial_tests["p_value"] = trial_tests["p_value"].map(fmt_p)
    ia_tests["p_value"] = ia_tests["p_value"].map(fmt_p)
    return trial_summary, ia_summary, trial_tests, ia_tests


def get_gamm_tables() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    fit = pd.read_csv(GAMM / "gamm_model_fit.csv")
    param = pd.read_csv(GAMM / "gamm_parametric_terms.csv")
    smooth = pd.read_csv(GAMM / "gamm_smooth_terms.csv")
    sig = pd.read_csv(GAMM / "gamm_significant_parametric_terms.csv")
    pcol = next((column for column in param.columns if column.startswith("Pr")), None)
    if pcol:
        param["p_value"] = param[pcol]
        sig["p_value"] = sig[pcol] if pcol in sig.columns else pd.Series(dtype=float)
        param["p_value_fmt"] = param["p_value"].map(fmt_p)
        sig["p_value_fmt"] = sig["p_value"].map(fmt_p)
    fit["deviance_explained"] = fit["deviance_explained"].round(3)
    fit["r_sq"] = fit["r_sq"].round(3)
    fit["aic"] = fit["aic"].round(2)
    return fit, param, smooth, sig


def model_term(param: pd.DataFrame, outcome: str, term: str, family: str = "trial_language_by_sentence_type") -> pd.Series | None:
    rows = param[param["outcome"].eq(outcome) & param["term"].eq(term) & param["model_family"].eq(family)]
    if rows.empty:
        return None
    return rows.iloc[0]


def term_sentence(row: pd.Series | None, label: str) -> str:
    if row is None:
        return f"- {label}: not estimated."
    p = row.get("p_value", pd.NA)
    sig = "significant" if pd.notna(p) and p < 0.05 else "not significant"
    return f"- {label}: estimate = {row['Estimate']:.3f}, p = {fmt_p(p)} ({sig})."


def generate_report() -> None:
    trial_summary, ia_summary, trial_tests, ia_tests = get_exploratory_tables()
    fit, param, smooth, sig = get_gamm_tables()

    lines: list[str] = []
    lines.extend([
        "# Eye-Tracking Analysis Report",
        "",
        "## Overview",
        "",
        "This report summarizes the analysis pipeline completed so far for the English/Punjabi active-passive eye-tracking study.",
        "The central goals were to test language and sentence-type effects, use free viewing as a same-picture baseline, evaluate cognitive-load markers, and examine whether the results support an agent-first processing principle.",
        "",
        "## Data Preparation Completed",
        "",
        "Raw EyeLink report exports were standardized into participant-level and trial-level datasets using `process_eye_tracking_reports.py`.",
        "The analysis preparation script `analysis/prepare_analysis_data.py` then recovered stimulus metadata, matched every sentence/audio trial to same-participant same-picture free-viewing baselines, and created baseline-adjusted outcomes.",
        "",
        "Primary analysis dataset:",
        "",
        "```text",
        "analysis/derived/sentence_audio_baseline_adjusted.csv",
        "```",
        "",
        "Interest-area dataset:",
        "",
        "```text",
        "analysis/derived/interest_area_agent_first_dataset.csv",
        "```",
        "",
        "All 900 sentence/audio trials had participant-specific same-image free-viewing baselines.",
        "",
        "## Experimental Balance",
        "",
        condition_counts(),
        "",
        "## AOI Role Coding",
        "",
        "AOI role was inferred from `ia_label` using the rule requested:",
        "",
        "```text",
        "s_... = agent/subject",
        "o_... = object",
        "everything else = bg",
        "```",
        "",
        aoi_counts(),
        "",
        "## Free-Viewing Baseline Strategy",
        "",
        "For each sentence/audio trial and each outcome, the analysis computed:",
        "",
        "```text",
        "delta_outcome = sentence_audio_outcome - free_viewing_outcome_for_same_participant_and_image",
        "```",
        "",
        "This controls for image-level visual salience and participant-specific image-viewing tendencies before testing linguistic effects.",
        "",
        "## Exploratory Screening Results",
        "",
        "The exploratory stage used descriptive summaries and non-parametric tests. These tests do not replace the GAMMs because they do not model crossed participant/image effects, but they identify promising patterns.",
        "",
        "### Strongest Trial-Level Exploratory Effects",
        "",
        table_or_note(trial_tests, ["outcome", "outcome_label", "group", "levels", "statistic", "p_value", "language", "sentence_type"], 15),
        "",
        "### Strongest Interest-Area Exploratory Effects",
        "",
        table_or_note(ia_tests, ["outcome", "outcome_label", "group", "levels", "statistic", "p_value", "language", "aoi_role", "sentence_type"], 15),
        "",
        "### Exploratory Interpretation",
        "",
        "Exploratory screening suggested that sentence-type effects were clearest in English for fixation count, mean fixation duration, saccade rate, and saccade duration. Interest-area screening also showed strong agent/object differences in dwell-time measures, especially in English passive and passive dropped-agent conditions. These findings motivated the confirmatory GAMM stage below.",
        "",
        "## GAMM Models",
        "",
        "GAMMs were run with `mgcv::bam` in R using participant and image/item random-effect smooths.",
        "",
        "Core trial-level model:",
        "",
        "```r",
        "outcome ~ language * sentence_type +",
        "  s(participant_id, bs = 're') +",
        "  s(image_id, bs = 're')",
        "```",
        "",
        "Agent-first model:",
        "",
        "```r",
        "cognitive_load_index ~ language * agent_first_alignment +",
        "  s(participant_id, bs = 're') +",
        "  s(image_id, bs = 're')",
        "```",
        "",
        "Interest-area model:",
        "",
        "```r",
        "outcome ~ language * sentence_type * aoi_role +",
        "  s(participant_id, bs = 're') +",
        "  s(image_id, bs = 're') +",
        "  s(ia_label, bs = 're')",
        "```",
        "",
        "### GAMM Model Fit Summary",
        "",
        table_or_note(fit, ["model", "model_family", "outcome", "n", "aic", "deviance_explained", "r_sq"], 20),
        "",
        "### Significant GAMM Parametric Terms",
        "",
        table_or_note(sig, ["model_family", "outcome", "term", "Estimate", "Std._Error", "t_value", "p_value_fmt"], 30),
        "",
        "### Key GAMM Results By Hypothesis",
        "",
        "#### Sentence-Type Effects",
        "",
        term_sentence(model_term(param, "delta_fixation_mean_fixation_duration", "sentence_typepassive"), "English passive vs English active for mean fixation duration"),
        term_sentence(model_term(param, "delta_fixation_mean_fixation_duration", "sentence_typepassive_dropped_agent"), "English passive dropped-agent vs English active for mean fixation duration"),
        term_sentence(model_term(param, "delta_fixation_fixation_count", "sentence_typepassive"), "English passive vs English active for fixation count"),
        term_sentence(model_term(param, "delta_fixation_fixation_count", "sentence_typepassive_dropped_agent"), "English passive dropped-agent vs English active for fixation count"),
        term_sentence(model_term(param, "delta_saccade_saccade_rate", "sentence_typepassive"), "English passive vs English active for saccade rate"),
        term_sentence(model_term(param, "delta_saccade_mean_saccade_duration", "sentence_typepassive"), "English passive vs English active for saccade duration"),
        "",
        "Interpretation: relative to English active sentences, English passive sentences showed longer mean fixation durations, lower fixation counts, lower saccade rate, and longer saccade duration. This is consistent with changed processing dynamics under passive syntax, but the decrease in fixation count means the cognitive-load interpretation should be framed as a pattern of longer/deeper fixations rather than globally more fixations.",
        "",
        "#### Language Differences",
        "",
        term_sentence(model_term(param, "delta_fixation_fixation_count", "languagePunjabi:sentence_typepassive"), "Punjabi modulation of the passive effect for fixation count"),
        term_sentence(model_term(param, "delta_interest_area_total_interest_area_dwell_time", "languagePunjabi:sentence_typepassive"), "Punjabi modulation of the passive effect for total IA dwell time"),
        term_sentence(model_term(param, "delta_saccade_saccade_rate", "languagePunjabi:sentence_typepassive"), "Punjabi modulation of the passive effect for saccade rate"),
        "",
        "Interpretation: several passive effects differed between English and Punjabi. The positive Punjabi interaction for fixation count and saccade rate indicates that the English passive reduction in these measures was attenuated in Punjabi. The negative Punjabi interaction for interest-area dwell time suggests a different passive-related dwell-time pattern across languages.",
        "",
        "#### Cognitive Load Composite",
        "",
        term_sentence(model_term(param, "cognitive_load_index", "sentence_typepassive"), "Passive vs active for composite cognitive-load index"),
        term_sentence(model_term(param, "cognitive_load_index", "sentence_typepassive_dropped_agent"), "Passive dropped-agent vs active for composite cognitive-load index"),
        term_sentence(model_term(param, "cognitive_load_index", "agent_first_alignmentnon_agent_first", "trial_language_by_agent_first"), "Non-agent-first vs agent-first for composite cognitive-load index"),
        term_sentence(model_term(param, "cognitive_load_index", "agent_overtagent_dropped", "passive_only_language_by_agent_overt"), "Dropped-agent vs overt-agent passive for composite cognitive-load index"),
        "",
        "Interpretation: the composite cognitive-load index did not show a significant sentence-type, agent-first, or dropped-agent effect in the GAMMs. Therefore, the current evidence does not support a broad claim that passive sentences uniformly increased cognitive load across all combined gaze indicators. The stronger claim is that passive syntax altered specific gaze dynamics, especially mean fixation duration and saccade behavior.",
        "",
        "#### Agent-First Principle",
        "",
        "The agent-first hypothesis receives partial, indirect support only. Active sentences, coded as agent-first aligned, differed from passive structures on some gaze measures, especially in English. However, the direct `agent_first_alignment` GAMM on the composite cognitive-load index was not significant, and the interest-area GAMMs did not show robust significant `aoi_role` interactions after accounting for participant, image, and IA-label random effects.",
        "",
        "A defensible interpretation is:",
        "",
        "```text",
        "The data show evidence that passive sentence structure changes gaze behavior relative to active structure, particularly in English, but the current GAMM results do not provide strong standalone evidence that this is specifically driven by an agent-first processing mechanism. The agent-first account remains plausible, especially given AOI-level exploratory agent/object differences, but should be presented as partially supported and requiring stronger time-course or AOI-role evidence.",
        "```",
        "",
        "## Figures And Placeholders",
        "",
        "Use these placeholders when preparing the journal manuscript. The corresponding plot files already exist for many of them.",
        "",
        "### Figure 1. Study Design And Pipeline",
        "",
        "[Placeholder: schematic showing raw reports -> standardized data -> free-viewing baselines -> GAMMs]",
        "",
        "### Figure 2. Baseline-Adjusted Mean Fixation Duration",
        "",
        "[Placeholder: line/point plot by language and sentence type]",
        "",
        "Existing plot:",
        "",
        "```text",
        "analysis/results/gamm/plots/trial_sentence_type_delta_fixation_mean_fixation_duration_predicted_means.png",
        "```",
        "",
        "### Figure 3. Baseline-Adjusted Fixation Count",
        "",
        "[Placeholder: line/point plot by language and sentence type]",
        "",
        "Existing plot:",
        "",
        "```text",
        "analysis/results/gamm/plots/trial_sentence_type_delta_fixation_fixation_count_predicted_means.png",
        "```",
        "",
        "### Figure 4. Saccade Rate And Saccade Duration",
        "",
        "[Placeholder: two-panel figure showing saccade rate and saccade duration by language and sentence type]",
        "",
        "Existing plots:",
        "",
        "```text",
        "analysis/results/gamm/plots/trial_sentence_type_delta_saccade_saccade_rate_predicted_means.png",
        "analysis/results/gamm/plots/trial_sentence_type_delta_saccade_mean_saccade_duration_predicted_means.png",
        "```",
        "",
        "### Figure 5. Time To First Fixation By AOI Role",
        "",
        "[Placeholder: agent vs object time-to-first-fixation by language and sentence type]",
        "",
        "Existing plot:",
        "",
        "```text",
        "analysis/results/gamm/plots/ia_role_time_to_first_fixation_predicted_means.png",
        "```",
        "",
        "### Figure 6. Dwell Time By AOI Role",
        "",
        "[Placeholder: normalized dwell time for agent vs object AOIs by sentence type and language]",
        "",
        "Existing plot:",
        "",
        "```text",
        "analysis/results/gamm/plots/ia_role_dwell_time_normalized_by_trial_length_predicted_means.png",
        "```",
        "",
        "## Journal-Ready Summary",
        "",
        "The analysis pipeline successfully standardizes raw EyeLink exports, constructs trial-level and AOI-level datasets, creates same-participant same-picture free-viewing baselines, derives cognitive-load and agent-first variables, and fits GAMMs with crossed participant and image/item random effects.",
        "",
        "The strongest GAMM evidence is for sentence-type effects on specific gaze measures in English: passive sentences increased mean fixation duration, reduced fixation count, reduced saccade rate, and increased saccade duration relative to active sentences. Some of these passive effects differed in Punjabi, suggesting language-specific processing patterns. However, the composite cognitive-load index and direct agent-first composite model were not significant, so the paper should avoid claiming a general passive cognitive-load increase without qualification.",
        "",
        "Recommended manuscript framing:",
        "",
        "```text",
        "Passive syntax modulated gaze dynamics after controlling for same-picture free-viewing baselines. These effects were strongest in English and were expressed in fixation duration and saccadic timing rather than a uniform increase across all cognitive-load markers. The findings are compatible with an agent-first processing account, but the direct evidence for agent-first processing is partial rather than conclusive.",
        "```",
        "",
        "## Files Produced",
        "",
        "```text",
        "analysis/derived/sentence_audio_baseline_adjusted.csv",
        "analysis/derived/interest_area_agent_first_dataset.csv",
        "analysis/results/exploratory/",
        "analysis/results/gamm/",
        "analysis/analysis_report.md",
        "```",
    ])

    REPORT.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    generate_report()
