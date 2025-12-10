"""Test CLI couvrant Modules A -> B -> C -> H -> E."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict, List

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_PATH = TESTS_DIR / "data" / "sample_sales.csv"
OUTPUT_DIR = TESTS_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def _ensure_fake_openai() -> None:
    if "openai" in sys.modules:
        return

    class _FakeChatCompletions:
        def create(self, **kwargs):
            user_prompt = ""
            for message in kwargs.get("messages", []):
                if message.get("role") == "user":
                    user_prompt = message.get("content", "")
                    break

            if "les clés 'analysis', 'insights', 'anomalies'" in user_prompt:
                payload = {
                    "analysis": "Analyse IA factice générée dans le test pipeline.",
                    "insights": "Insight factice cohérent avec les données.",
                    "anomalies": "Aucune anomalie détectée.",
                }
            elif "clé unique 'text'" in user_prompt:
                payload = {"text": "Bloc IA factice (intro/synthèse)."}
            else:
                payload = {}

            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=json.dumps(payload)))]
            )

    class _FakeChat:
        def __init__(self):
            self.completions = _FakeChatCompletions()

    class _FakeOpenAIClient:
        def __init__(self, api_key: str | None = None):
            self.api_key = api_key
            self.chat = _FakeChat()

    sys.modules["openai"] = SimpleNamespace(OpenAI=_FakeOpenAIClient)


def _adapt_texts_for_module_e(texts_h: Dict[str, Any], plots: List[Dict[str, Any]]) -> Dict[str, Any]:
    analyses = []
    per_column = texts_h.get("per_column", {})
    for plot in plots:
        column = plot.get("column")
        column_texts = per_column.get(column, {})
        paragraph_parts = [column_texts.get("analysis"), column_texts.get("insights")]
        text = " ".join(part for part in paragraph_parts if part)
        analyses.append(
            {
                "column": column,
                "graph_type": plot.get("graph_type"),
                "title": f"Analyse de {column}",
                "text": text or "Analyse non disponible.",
            }
        )
    return {
        "analyses": analyses,
        "conclusion": texts_h.get("global_summary") or "Conclusion indisponible.",
    }


_ensure_fake_openai()

from backend.modules.module_a_loader import load_and_parse_file
from backend.modules.module_b_analysis import analyze_dataset
from backend.modules.module_c_plotting import generate_plots
from backend.modules.module_e_ppt import build_presentation
from backend.modules.module_h_texts_ai import generate_texts_ai


def main() -> None:
    os.environ["OPENAI_API_KEY"] = "fake-test-key"

    parsed = load_and_parse_file(str(DATA_PATH))
    dataframe = parsed.get("dataframe")
    diagnostic = parsed.get("diagnostic", {})
    if dataframe is None:
        raise RuntimeError(f"Impossible de charger le dataset: {diagnostic}")

    analysis = analyze_dataset(dataframe, diagnostic)

    plots_dir = OUTPUT_DIR / "plots"
    plots_dir.mkdir(exist_ok=True)
    plot_result = generate_plots(dataframe, analysis, str(plots_dir))
    plots = plot_result.get("plots", [])
    errors = plot_result.get("errors", [])

    viz_plan = {"plots": plots}
    texts_h = generate_texts_ai(analysis, viz_plan, style="normal")

    ppt_path = OUTPUT_DIR / "test_pipeline.pptx"
    texts_for_module_e = _adapt_texts_for_module_e(texts_h, plots)
    build_summary = build_presentation(
        title="Test Pipeline IA",
        plots=plots,
        texts=texts_for_module_e,
        output_path=str(ppt_path),
        theme="corporate",
        options={"diagnostic": diagnostic},
    )

    report = {
        "rows": diagnostic.get("num_rows"),
        "columns": diagnostic.get("num_cols"),
        "plots": len(plots),
        "plot_errors": errors,
        "ppt_path": str(ppt_path),
        "slides": build_summary.get("slides"),
        "texts_keys": list(texts_h.keys()),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print("📊 Test pipeline complet terminé. PPT généré dans:", ppt_path)


if __name__ == "__main__":
    main()
