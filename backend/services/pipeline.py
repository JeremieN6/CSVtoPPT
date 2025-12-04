"""High-level pipeline orchestrating Modules A through E."""
from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional

from backend.modules.module_a_loader import load_and_parse_file
from backend.modules.module_b_analysis import analyze_dataset
from backend.modules.module_c_plotting import generate_plots
from backend.modules.module_d_texts import generate_texts
from backend.modules.module_e_ppt import build_presentation
from backend.services.utils import (
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

        texts = generate_texts(
            analysis,
            plots,
            use_ai=use_ai,
            api_key=api_key,
        )

        ppt_filename = build_generated_filename(title)
        ppt_path = GENERATED_DIR / ppt_filename
        presentation_options: Dict[str, Any] = {"diagnostic": diagnostic}
        if additional_options:
            presentation_options.update(additional_options)

        build_summary = build_presentation(
            title,
            plots,
            texts,
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