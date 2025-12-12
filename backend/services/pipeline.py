"""High-level pipeline orchestrating Modules A through E."""
from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from modules.module_a_loader import load_and_parse_file
from modules.module_b_analysis import analyze_dataset
from modules.module_c_plotting import generate_plots
from modules.module_e_ppt import build_presentation
from modules.module_h_texts_ai import generate_texts_ai
from services.utils import (
    build_generated_filename,
    cleanup_path,
    ensure_directory,
)

GENERATED_DIR = Path(__file__).resolve().parents[1] / "generated"
ensure_directory(GENERATED_DIR)


class PipelineError(Exception):
    """Raised when one stage of the pipeline fails irrecoverably."""


def run_pipeline(
    file_path: str | Path,
    *,
    title: str,
    theme: str = "corporate",
    use_ai: bool = False,
    api_key: Optional[str] = None,
    additional_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute the full CSV/XLSX -> PPT pipeline starting from a file path."""

    parsed = load_and_parse_file(str(file_path))
    dataframe = parsed.get("dataframe")
    diagnostic = parsed.get("diagnostic", {})
    if dataframe is None:
        raise PipelineError(diagnostic.get("error") or "Impossible de lire le fichier fourni.")

    return pipeline_run(
        df=dataframe,
        diagnostic=diagnostic,
        title=title,
        theme=theme,
        use_ai=use_ai,
        api_key=api_key,
        additional_options=additional_options,
    )
    
def pipeline_run(
    *,
    df,
    diagnostic: Optional[Dict[str, Any]] = None,
    title: str,
    theme: str = "corporate",
    use_ai: bool = False,
    api_key: Optional[str] = None,
    plan_params: Optional[Dict[str, Any]] = None,
    additional_options: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Execute the pipeline from an already loaded dataframe."""

    if df is None:
        raise PipelineError("Aucune donnée fournie au pipeline.")

    workspace = Path(tempfile.mkdtemp(prefix="pipeline_"))
    plots_dir = workspace / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[str] = []

    diagnostic = diagnostic or {}
    plan_params = plan_params or {}
    additional_options = additional_options or {}

    try:
        analysis = analyze_dataset(df, diagnostic)

        plot_result = generate_plots(df, analysis, str(plots_dir))
        warnings.extend(plot_result.get("errors", []))
        plots = plot_result.get("plots", [])
        if not plots:
            warnings.append("Aucun graphique n'a pu être généré.")

        plots, trimmed = _enforce_slide_cap(plots, diagnostic, plan_params.get("max_slides"))
        if trimmed:
            warnings.append(
                f"{trimmed} graphique(s) ont été exclus pour respecter la limite de {plan_params.get('max_slides')} slides."
            )

        text_style = plan_params.get("ai_style") or additional_options.get("text_style") or "normal"
        texts_ai = _generate_texts_with_module_h(
            analysis,
            plots,
            style=text_style,
            use_ai=use_ai,
            api_key=api_key,
        )
        texts_for_ppt = _prepare_texts_for_presentation(texts_ai, plots)

        ppt_filename = build_generated_filename(title)
        ppt_path = GENERATED_DIR / ppt_filename

        presentation_options: Dict[str, Any] = {"diagnostic": diagnostic}
        presentation_options.update(additional_options)
        if plan_params.get("watermark") is not None:
            presentation_options["watermark"] = plan_params["watermark"]
        if plan_params.get("template"):
            presentation_options["template"] = plan_params["template"]
        if plan_params.get("max_slides") is not None:
            presentation_options["max_slides"] = plan_params["max_slides"]

        build_summary = build_presentation(
            title,
            plots,
            texts_for_ppt,
            str(ppt_path),
            theme=theme,
            options=presentation_options,
        )
        warnings.extend(build_summary.get("errors", []))
        return {
            "pptx_path": str(ppt_path),
            "warnings": warnings,
            "slides": build_summary.get("slides", 0),
        }
    except PipelineError:
        raise
    except Exception as exc:  # pragma: no cover
        raise PipelineError(str(exc)) from exc
    finally:
        cleanup_path(workspace)


def _enforce_slide_cap(
    plots: List[Dict[str, Any]],
    diagnostic: Dict[str, Any],
    max_slides: Optional[int],
) -> tuple[List[Dict[str, Any]], int]:
    if not max_slides:
        return plots, 0

    base_slides = 2  # title + conclusion
    if diagnostic:
        base_slides += 1  # dataset overview
    allowed_plot_slides = max(max_slides - base_slides, 0)
    if allowed_plot_slides >= len(plots):
        return plots, 0
    return plots[:allowed_plot_slides], len(plots) - allowed_plot_slides


def _generate_texts_with_module_h(
    analysis: Dict[str, Any],
    plots: List[Dict[str, Any]],
    *,
    style: str,
    use_ai: bool,
    api_key: Optional[str],
) -> Dict[str, Any]:
    """Appelle Module H en gérant la clé OpenAI et les fallback nécessaires."""

    viz_plan = {"plots": plots}
    env_var = "OPENAI_API_KEY"
    previous_value = os.environ.get(env_var)
    try:
        if api_key and use_ai:
            os.environ[env_var] = api_key
        elif not use_ai:
            os.environ.pop(env_var, None)
        # Sinon : on laisse la variable telle quelle pour utiliser une clé déjà fournie.
        return generate_texts_ai(analysis, viz_plan, style=style)
    finally:
        if previous_value is not None:
            os.environ[env_var] = previous_value
        else:
            os.environ.pop(env_var, None)


def _prepare_texts_for_presentation(
    texts_ai: Dict[str, Any],
    plots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Convertit la structure Module H en format attendu par Module E."""

    per_column = texts_ai.get("per_column", {}) if isinstance(texts_ai, dict) else {}
    analyses = []
    for plot in plots:
        column = plot.get("column")
        column_text = per_column.get(column, {}) if isinstance(per_column, dict) else {}
        segments = [
            column_text.get("analysis"),
            column_text.get("insights"),
            column_text.get("anomalies"),
        ]
        text = " ".join(segment.strip() for segment in segments if isinstance(segment, str) and segment.strip())
        analyses.append(
            {
                "column": column,
                "graph_type": plot.get("graph_type"),
                "title": f"Analyse de {column}",
                "text": text or "Analyse non disponible.",
            }
        )
    conclusion = texts_ai.get("global_summary") if isinstance(texts_ai, dict) else None
    if not conclusion:
        conclusion = texts_ai.get("global_intro") if isinstance(texts_ai, dict) else None
    return {
        "analyses": analyses,
        "conclusion": conclusion or "Synthèse indisponible.",
    }