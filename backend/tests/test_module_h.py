"""Tests manuels pour Module H (IA avancée)."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from types import SimpleNamespace
from typing import Any, Dict

import pandas as pd

TESTS_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = TESTS_DIR.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

DATA_PATH = TESTS_DIR / "data" / "sample_sales.csv"


def _ensure_fake_openai() -> None:
    """Injecte un client OpenAI factice afin de tester le flux IA."""

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
                content = json.dumps(
                    {
                        "analysis": "Analyse IA factice générée pour la colonne.",
                        "insights": "Insight factice basé sur les données fournies.",
                        "anomalies": "Aucune anomalie majeure détectée.",
                    }
                )
            elif "clé unique 'text'" in user_prompt:
                content = json.dumps({"text": "Texte IA factice pour ce bloc."})
            else:
                content = json.dumps({})

            return SimpleNamespace(
                choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
            )

    class _FakeChat:
        def __init__(self):
            self.completions = _FakeChatCompletions()

    class _FakeOpenAIClient:
        def __init__(self, api_key: str | None = None):
            self.api_key = api_key
            self.chat = _FakeChat()

    fake_module = SimpleNamespace(OpenAI=_FakeOpenAIClient)
    sys.modules["openai"] = fake_module


_ensure_fake_openai()

from backend.modules.module_b_analysis import analyze_dataset
from backend.modules.module_h_texts_ai import generate_texts_ai


def _build_diagnostic(df: pd.DataFrame) -> Dict[str, Any]:
    diagnostic: Dict[str, Any] = {
        "num_rows": len(df),
        "num_cols": df.shape[1],
        "columns": {},
    }
    for column in df.columns:
        series = df[column]
        diagnostic["columns"][column] = {
            "dtype": str(series.dtype),
            "missing_percent": round(float(series.isna().mean() * 100), 2),
            "unique_values": int(series.nunique(dropna=True)),
            "sample": series.astype(str).head(3).tolist(),
        }
    return diagnostic


def _build_visualization_plan(analysis: Dict[str, Any]) -> Dict[str, Any]:
    plots = []
    for column, options in (analysis.get("visualization_candidates") or {}).items():
        if not options:
            continue
        plots.append(
            {
                "column": column,
                "graph_type": options[0],
                "file_path": f"/tmp/{column}_{options[0]}.png",
            }
        )
    return {"plots": plots}


def _assert_structure(result: Dict[str, Any]) -> None:
    assert "global_intro" in result and isinstance(result["global_intro"], str)
    assert "global_summary" in result and isinstance(result["global_summary"], str)
    assert "per_column" in result and isinstance(result["per_column"], dict)
    for column, texts in result["per_column"].items():
        assert {"analysis", "insights", "anomalies"}.issubset(texts.keys()), column
    assert "correlations" in result and isinstance(result["correlations"], list)


def run_with_fake_ai(analysis: Dict[str, Any], viz_plan: Dict[str, Any]) -> None:
    os.environ["OPENAI_API_KEY"] = "fake-test-key"
    result = generate_texts_ai(analysis, viz_plan, style="executive")
    _assert_structure(result)
    print("✅ Test Module H avec client IA factice : OK")
    print(json.dumps({"intro": result["global_intro"][:80]}, ensure_ascii=False, indent=2))


def run_without_api_key(analysis: Dict[str, Any], viz_plan: Dict[str, Any]) -> None:
    os.environ.pop("OPENAI_API_KEY", None)
    result = generate_texts_ai(analysis, viz_plan, style="short")
    _assert_structure(result)
    print("✅ Test Module H sans clé (fallback Module D) : OK")
    first_col = next(iter(result["per_column"].values()))
    print(json.dumps(first_col, ensure_ascii=False, indent=2))


def main() -> None:
    df = pd.read_csv(DATA_PATH)
    diagnostic = _build_diagnostic(df)
    analysis = analyze_dataset(df, diagnostic)
    viz_plan = _build_visualization_plan(analysis)

    print("=== Lancement Test Module H (IA) ===")
    run_with_fake_ai(analysis, viz_plan)

    print("\n=== Lancement Test Module H (fallback) ===")
    run_without_api_key(analysis, viz_plan)


if __name__ == "__main__":
    main()
