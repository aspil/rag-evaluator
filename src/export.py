import os
from collections import defaultdict
from datetime import datetime
from typing import Any

import pandas as pd
from loguru import logger

from src.models.models import EvaluationResult, RAGEntry
from src.models.score_enum import (
    AnswerRelevanceScore,
    GroundednessScore,
    ClarityScore,
    CompletenessScore,
    ConcisenessScore,
    HarmfulnessScore,
)
from src.utils import format_history, format_retrieved_context

DIMENSION_ENUMS = {
    "answer_relevance": AnswerRelevanceScore,
    "groundedness": GroundednessScore,
    "clarity": ClarityScore,
    "completeness": CompletenessScore,
    "conciseness": ConcisenessScore,
    "harmfulness": HarmfulnessScore,
}


def export(
    entries: list[RAGEntry],
    results: list[EvaluationResult],
    raw_df: pd.DataFrame,
    evaluation_params: dict[str, Any],
    output_dir: str,
):
    """Exports evaluation results as both csv and markdown reports into the given output directory."""
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    _export_csv(raw_df, results, output_dir, timestamp)
    _export_markdown(entries, results, evaluation_params, output_dir, timestamp)


def _export_csv(data: pd.DataFrame, results: list[EvaluationResult], output_dir: str, timestamp: str, strict=False):
    if strict and len(data) != len(results):
        raise ValueError("Mismatch between input data and results length")

    score_data = []
    for res in results:
        flat = {f"{name}_score": detail.score for name, detail in res.scores.items()}
        flat["composite"] = res.composite
        score_data.append(flat)

    results_df = pd.DataFrame(score_data)
    final_df = pd.concat([data.reset_index(drop=True), results_df], axis=1)

    csv_path = os.path.join(output_dir, f"rag_evaluation_results_{timestamp}.csv")
    final_df.to_csv(csv_path, index=False)
    logger.info(f"Exported csv to: {csv_path}")


def _generate_summary_analysis(results: list[EvaluationResult]) -> list[str]:
    summary = ["## Summary Analysis", ""]

    # overall Performance
    composites = [res.composite for res in results]
    avg_composite = sum(composites) / len(composites)
    std_composite = pd.Series(composites).std()

    summary.append("### Overall Results")
    summary.append(f"- **Average composite score**: {avg_composite:.2f} ± {std_composite:.2f}")
    summary.append(f"- **Number of evaluated entries**: {len(results)}")
    summary.append("")

    # dimension means
    dim_scores = defaultdict(list)
    for res in results:
        for name, detail in res.scores.items():
            dim_scores[name].append(detail.score)

    dim_means = {k: sum(v) / len(v) for k, v in dim_scores.items()}
    best_dim = max(dim_means.items(), key=lambda x: x[1])
    worst_dim = min(dim_means.items(), key=lambda x: x[1])

    summary.append("### Dimension Summary")
    summary.append(f"- **Best performing dimension**: `{best_dim[0]}` (mean = {best_dim[1]:.2f})")
    summary.append(f"- **Worst performing dimension**: `{worst_dim[0]}` (mean = {worst_dim[1]:.2f})")
    summary.append("")

    # strong and total success responses
    strong_count = 0  # safe answers with maximum answer relevance and groundedness
    total_success_count = 0  # safe answers with all dimensions having maximum scores
    for res in results:
        if all(score_detail.score == DIMENSION_ENUMS[name].max() for name, score_detail in res.scores.items()):
            total_success_count += 1
        if (
            res.scores["answer_relevance"].score == DIMENSION_ENUMS["answer_relevance"].max()
            and res.scores["groundedness"].score == DIMENSION_ENUMS["groundedness"].max()
            and res.scores["harmfulness"].score == DIMENSION_ENUMS["harmfulness"].max()
        ):
            strong_count += 1

    summary.append("### High-Quality Responses")
    summary.append(f"- Entries with **max answer relevance**, **fully grounded**, and **safe**: {strong_count}")
    summary.append(f"- Entries with **maximum score in all dimensions**: {total_success_count}")
    summary.append("")

    # weaknesses
    hallucinated = sum(1 for r in results if r.scores["groundedness"].score == 0)
    incomplete = sum(1 for r in results if r.scores["completeness"].score == 0)
    unsafe = sum(1 for r in results if r.scores["harmfulness"].score == 0)
    low_quality = sum(1 for r in results if r.composite < 0.3)

    summary.append("### Quality Issues")
    summary.append(f"- Hallucinated entries (groundedness = 0): {hallucinated}")
    summary.append(f"- Incomplete answers (completeness = 0): {incomplete}")
    summary.append(f"- Unsafe responses (harmfulness = 0): {unsafe}")
    summary.append(f"- Very low composite score (< 0.3): {low_quality}")
    summary.append("")

    return summary


def _export_markdown(
    entries: list[RAGEntry],
    results: list[EvaluationResult],
    evaluation_params: dict[str, Any],
    output_dir: str,
    timestamp: str,
    strict=False,
):
    if strict and len(entries) != len(results):
        raise ValueError("Mismatch between input data and results length")

    import pandas as pd

    # Build dataframe with both raw and normalized scores
    score_data = []
    for res in results:
        row = {f"{name}_score": detail.score for name, detail in res.scores.items()}
        row.update({f"{name}_normalized": detail.normalized_score for name, detail in res.scores.items()})
        row["composite"] = res.composite
        score_data.append(row)
    df = pd.DataFrame(score_data)

    # Begin markdown
    md_lines = [
        "# RAG Automatic Evaluation Report\n",
        "This report presents an automatic evaluation of assistant responses on the following evaluation "
        "dimensions: answer relevance, clarity, completeness, conciseness, groundedness, and "
        "harmfulness. It provides both aggregate statistics (e.g., mean, standard deviation, percentiles) "
        "and detailed per-csv-entry assessments.\n\n"
        "Entries containing unsafe answers, as identified by the "
        "harmfulness score, are marked with a ⚠️ symbol for visibility.\n",
        "## Evaluation Parameters\n",
    ]

    # Evaluation parameters
    for param_name, param in evaluation_params.items():
        md_lines.append(f"- {param_name.replace('_', ' ').capitalize()}: {param}")
        md_lines.append("")

    # Summary Analysis
    md_lines.extend(_generate_summary_analysis(results))

    # Aggregate Raw Score Statistics
    md_lines.append("## Aggregate Raw Score Statistics\n")
    raw_summary = (
        df[[c for c in df.columns if c.endswith("_score") or c == "composite"]]
        .describe(percentiles=[0.25, 0.5, 0.75])
        .T
    )
    md_lines.append("| Metric | Count | Mean | Std | Min | 25% | 50% | 75% | Max |")
    md_lines.append("|--------|-------|------|-----|-----|-----|-----|-----|-----|")
    for metric, row in raw_summary.iterrows():
        md_lines.append(
            f"| {metric} | {int(row['count'])} | {row['mean']:.2f} | {row['std']:.2f} | {row['min']:.2f} | "
            f"{row['25%']:.2f} | {row['50%']:.2f} | {row['75%']:.2f} | {row['max']:.2f} |"
        )
    md_lines.append("")

    # Aggregate Normalized Score Statistics
    md_lines.append("## Aggregate Normalized Score Statistics\n")
    norm_summary = df[[c for c in df.columns if c.endswith("_normalized")]].describe(percentiles=[0.25, 0.5, 0.75]).T
    md_lines.append("| Metric | Count | Mean | Std | Min | 25% | 50% | 75% | Max |")
    md_lines.append("|--------|-------|------|-----|-----|-----|-----|-----|-----|")
    for metric, row in norm_summary.iterrows():
        md_lines.append(
            f"| {metric} | {int(row['count'])} | {row['mean']:.2f} | {row['std']:.2f} | {row['min']:.2f} | "
            f"{row['25%']:.2f} | {row['50%']:.2f} | {row['75%']:.2f} | {row['max']:.2f} |"
        )
    md_lines.append("")

    # Per-entry results
    for i, (entry, result) in enumerate(zip(entries, results), 1):
        harmfulness_score = result.scores.get("harmfulness", None)
        is_unsafe = harmfulness_score is not None and harmfulness_score.score == 0.0
        entry_title = f"## Entry {i} {'⚠️' if is_unsafe else ''}"
        md_lines.append(entry_title)
        md_lines.append("")
        md_lines.append("**Conversation History:**")
        md_lines.append(format_history(entry.conversation_history))
        md_lines.append("")
        md_lines.append(f"**User Question:** {entry.current_user_question}")
        md_lines.append("")
        md_lines.append("**Retrieved Context:**")
        md_lines.append("")
        md_lines.append(format_retrieved_context(entry.fragment_texts))
        md_lines.append("")
        md_lines.append(f"**Assistant Answer:** {entry.assistant_answer}")
        md_lines.append("")
        md_lines.append("### Scores")
        md_lines.append("")
        md_lines.append(f"**Composite Score:** {result.composite:.3f}")
        md_lines.append("")

        for name, detail in result.scores.items():
            md_lines.append(f"#### {name.replace('_', ' ').capitalize()}")
            md_lines.append(f"- **Score**: {detail.score}")
            md_lines.append(f"- **Explanation**: {detail.explanation}")
            md_lines.append("")

    # Save
    md_path = os.path.join(output_dir, f"rag_evaluation_results_{timestamp}.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md_lines))

    logger.info(f"Exported Markdown report to: {md_path}")
