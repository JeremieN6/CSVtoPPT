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
    """Execute the full CSV/XLSX -> PPT pipeline.

    Returns a dictionary containing ``pptx_path``, ``warnings`` and ``slides``.
    """

    workspace = Path(tempfile.mkdtemp(prefix="pipeline_"))
    plots_dir = workspace / "plots"
    plots_dir.mkdir(parents=True, exist_ok=True)
    warnings: List[str] = []

    try:
        parsed = load_and_parse_file(str(file_path))
        dataframe = parsed.get("dataframe")
        diagnostic = parsed.get("diagnostic", {})
        if dataframe is None:
            raise PipelineError(diagnostic.get("error") or "Impossible de lire le fichier fourni.")

        analysis = analyze_dataset(dataframe, diagnostic)

        plot_result = generate_plots(dataframe, analysis, str(plots_dir))
        plot_errors = plot_result.get("errors", [])
        warnings.extend(plot_errors)
        plots = plot_result.get("plots", [])
        if not plots:
            warnings.append("Aucun graphique n'a pu être généré.")

        text_style = (additional_options or {}).get("text_style", "normal")
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
        if additional_options:
            presentation_options.update(additional_options)

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