"""Module H - IA avancée pour la génération de textes métier.

Ce module se situe entre l'analyse automatique (Module B) et la génération de la
présentation (Module E). Il consomme les résultats d'analyse ainsi que la liste
des graphiques prévus, puis produit des textes professionnels structurés prêts
à être injectés dans les slides. L'appel à l'API OpenAI est optionnel : en cas
d'absence de clé ou d'erreur, on revient automatiquement sur Module D.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Dict, List, Optional

try:  # Optional dependency: le module doit rester importable sans openai
    _openai_module = import_module("openai")
    _OpenAIClient = getattr(_openai_module, "OpenAI", None)
except ModuleNotFoundError:  # pragma: no cover
    _OpenAIClient = None

try:  # Fallback officiel Module D
    from .module_d_texts import generate_default_texts as _module_d_fallback
except (ImportError, AttributeError):  # pragma: no cover
    _module_d_fallback = None

try:  # Ancien générateur Module D (permet un fallback supplémentaire)
    from .module_d_texts import generate_texts as _legacy_module_d_generate_texts
except (ImportError, AttributeError):  # pragma: no cover
    _legacy_module_d_generate_texts = None

DEFAULT_GENERIC_TEXT = (
    "Analyse non disponible faute d'informations suffisantes dans le dataset."
)
DEFAULT_STYLE = "normal"

STYLE_PRESETS: Dict[str, Dict[str, str]] = {
    "short": {
        "description": "Ton ultra synthétique, bullet-friendly, 1 à 2 phrases max.",
        "length": "1 à 2 phrases",
        "focus": "Direct au but, aucune digression.",
    },
    "normal": {
        "description": "Style business standard, 3 à 5 phrases structurées.",
        "length": "3 à 5 phrases",
        "focus": "Explique la tendance, son impact et un insight concret.",
    },
    "executive": {
        "description": "Ton consultant senior, 4 à 6 phrases avec recommandations.",
        "length": "4 à 6 phrases",
        "focus": "Met en avant l'impact stratégique et les prochaines étapes.",
    },
}


@dataclass
class AIModelConfig:
    """Paramètres d'appel OpenAI."""

    model: str = "gpt-4o-mini"
    temperature: float = 0.4
    max_tokens: int = 380


class AIGenerationError(RuntimeError):
    """Erreur émise quand l'appel IA échoue."""


def _ensure_client(api_key: Optional[str]) -> Optional[Any]:
    """Instancie le client OpenAI si la dépendance et la clé sont présentes."""

    if _OpenAIClient is None or not api_key:
        return None
    try:
        return _OpenAIClient(api_key=api_key)
    except Exception:  # pragma: no cover
        return None


def _style_prompt(style_key: str) -> str:
    preset = STYLE_PRESETS.get(style_key, STYLE_PRESETS[DEFAULT_STYLE])
    return (
    "Tu es un analyste data senior.\n"
    "Écris en français, ton professionnel.\n"
    f"Style: {preset['description']} ({preset['length']}).\n"
    f"Consigne: {preset['focus']} Ne mentionne jamais de données absentes."
    )


def _safe_json_loads(value: str) -> Optional[Dict[str, Any]]:
    try:
        return json.loads(value)
    except Exception:
        return None


def _call_openai_json(
    client: Any,
    config: AIModelConfig,
    style_key: str,
    user_prompt: str,
) -> Dict[str, Any]:
    if client is None:
        raise AIGenerationError("Client OpenAI indisponible")
    try:
        response = client.chat.completions.create(
            model=config.model,
            temperature=config.temperature,
            max_tokens=config.max_tokens,
            messages=[
                {
                    "role": "system",
                    "content": _style_prompt(style_key)
                    + " Réponds STRICTEMENT en JSON valide.",
                },
                {"role": "user", "content": user_prompt},
            ],
        )
    except Exception as exc:  # pragma: no cover
        raise AIGenerationError(f"Échec OpenAI: {exc}") from exc

    content = (response.choices[0].message.content or "").strip()
    data = _safe_json_loads(content)
    if not isinstance(data, dict):
        raise AIGenerationError("Réponse OpenAI vide ou non JSON.")
    return data


def _extract_plots(visualization_plan: Any) -> List[Dict[str, Any]]:
    if isinstance(visualization_plan, dict):
        plots = visualization_plan.get("plots", [])
    elif isinstance(visualization_plan, list):
        plots = visualization_plan
    else:
        plots = []
    return [plot for plot in plots if isinstance(plot, dict)]


def _group_plots_by_column(plots: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
    grouped: Dict[str, List[Dict[str, Any]]] = {}
    for plot in plots:
        column = plot.get("column") or "inconnu"
        grouped.setdefault(column, []).append(plot)
    return grouped


def _column_profile(column: str, analysis_results: Dict[str, Any]) -> Dict[str, Any]:
    diagnostic_cols = (analysis_results or {}).get("diagnostic", {}).get("columns", {})
    profile = diagnostic_cols.get(column, {}) if isinstance(diagnostic_cols, dict) else {}
    if not profile:
        profile = {
            "dtype": (analysis_results or {}).get("column_types", {}).get(column),
        }
    return profile or {}


def _column_issues(column: str, analysis_results: Dict[str, Any]) -> List[str]:
    issues = (analysis_results or {}).get("issues", {})
    result: List[str] = []
    if isinstance(issues, dict):
        for name, columns in issues.items():
            if isinstance(columns, list) and column in columns:
                result.append(name)
    return result


def _build_dataset_context(analysis_results: Dict[str, Any], plots: List[Dict[str, Any]]) -> Dict[str, Any]:
    diagnostic = (analysis_results or {}).get("diagnostic", {})
    column_types = (analysis_results or {}).get("column_types", {})
    issues = (analysis_results or {}).get("issues", {})
    relations = (analysis_results or {}).get("relations", {})
    return {
        "num_rows": diagnostic.get("num_rows"),
        "num_cols": diagnostic.get("num_cols") or len(column_types),
        "column_types": column_types,
        "issue_counts": {k: len(v) for k, v in issues.items()} if isinstance(issues, dict) else {},
        "plots": [
            {
                "column": plot.get("column"),
                "graph_type": plot.get("graph_type"),
            }
            for plot in plots
        ],
        "correlations": relations.get("correlations", []) if isinstance(relations, dict) else [],
    }


def _local_column_text(column: str, metadata: Dict[str, Any]) -> Dict[str, str]:
    dtype = metadata.get("profile", {}).get("dtype") or "colonne"
    graph_types = metadata.get("graph_types") or []
    issues = metadata.get("issues") or []
    analysis = f"La colonne {column} ({dtype}) présente des informations exploitables via {', '.join(graph_types) or 'les graphiques disponibles'}."
    insights = "Les distributions observées suggèrent de vérifier les valeurs dominantes et l'étendue générale."
    anomalies = (
        "Points de vigilance : " + ", ".join(issues)
        if issues
        else "Aucune anomalie majeure détectée au regard des diagnostics disponibles."
    )
    return {
        "analysis": analysis,
        "insights": insights,
        "anomalies": anomalies,
    }


def generate_column_text(
    column: str,
    column_meta: Dict[str, Any],
    plots: List[Dict[str, Any]],
    analysis_results: Dict[str, Any],
    style: str,
    client: Any,
    config: AIModelConfig,
) -> Dict[str, str]:
    graph_types = sorted({plot.get("graph_type", "?") for plot in plots})
    payload = {
        "column": column,
        "profile": column_meta,
        "graph_types": graph_types,
        "issues": _column_issues(column, analysis_results),
        "notable_values": column_meta.get("sample", column_meta.get("examples")),
        "missing_percent": column_meta.get("missing_percent"),
    }
    prompt = (
        "Analyse exclusivement la colonne décrite par le JSON suivant.\n"
        "Écris en français, ton neutre professionnel.\n"
        "Réponds en JSON avec les clés 'analysis', 'insights', 'anomalies'.\n"
        "N'invente aucune statistique.\n"
        f"JSON: {json.dumps(payload, ensure_ascii=False)}"
    )
    response = _call_openai_json(client, config, style, prompt)
    if not all(key in response for key in ("analysis", "insights", "anomalies")):
        raise AIGenerationError("Format JSON inattendu pour l'analyse de colonne.")
    return {
        "analysis": response.get("analysis") or DEFAULT_GENERIC_TEXT,
        "insights": response.get("insights") or DEFAULT_GENERIC_TEXT,
        "anomalies": response.get("anomalies") or "",
    }


def generate_global_intro(
    dataset_context: Dict[str, Any],
    style: str,
    client: Any,
    config: AIModelConfig,
) -> str:
    prompt = (
        "À partir du résumé JSON suivant, écris une introduction de rapport.\n"
        "Mentionne le volume de données disponible s'il est fourni et les familles de colonnes.\n"
        f"JSON: {json.dumps(dataset_context, ensure_ascii=False)}"
    )
    response = _call_openai_json(
        client,
        config,
        style,
        prompt + "\nRéponds en JSON avec la clé unique 'text'.",
    )
    if "text" not in response:
        raise AIGenerationError("Réponse JSON invalide pour l'introduction.")
    return response["text"]


def generate_summary(
    dataset_context: Dict[str, Any],
    per_column: Dict[str, Dict[str, str]],
    style: str,
    client: Any,
    config: AIModelConfig,
) -> str:
    condensed = {
        "dataset": dataset_context,
        "highlights": {
            column: texts.get("insights") for column, texts in per_column.items()
        },
    }
    prompt = (
        "Génère une synthèse finale à partir du JSON fourni.\n"
        "Structure : rappel rapide du périmètre + 2 à 3 enseignements + prochaine étape.\n"
        f"JSON: {json.dumps(condensed, ensure_ascii=False)}\n"
        "Réponds en JSON avec la clé unique 'text'."
    )
    response = _call_openai_json(client, config, style, prompt)
    if "text" not in response:
        raise AIGenerationError("Réponse JSON invalide pour la synthèse.")
    return response["text"]


def generate_correlation_text(
    correlation: Dict[str, Any],
    style: str,
    client: Any,
    config: AIModelConfig,
) -> str:
    payload = {
        "columns": correlation.get("columns", []),
        "value": correlation.get("value"),
    }
    prompt = (
        "Explique la corrélation décrite par le JSON ci-dessous (ton professionnel).\n"
        "Réponds en JSON avec la clé 'text'.\n"
        f"JSON: {json.dumps(payload, ensure_ascii=False)}"
    )
    response = _call_openai_json(client, config, style, prompt)
    if "text" not in response:
        raise AIGenerationError("Réponse JSON invalide pour la corrélation.")
    return response["text"]


def _call_module_d_fallback(
    analysis_results: Dict[str, Any],
    visualization_plan: Any,
    style: str,
) -> Dict[str, Any]:
    if callable(_module_d_fallback):
        try:
            return _module_d_fallback(analysis_results, visualization_plan, style=style)
        except TypeError:
            return _module_d_fallback(analysis_results, visualization_plan)  # type: ignore[misc]
    if callable(_legacy_module_d_generate_texts):
        plots = _extract_plots(visualization_plan)
        try:
            legacy = _legacy_module_d_generate_texts(analysis_results, plots, use_ai=False)
        except Exception:  # pragma: no cover
            return _local_default_structure(analysis_results, plots)
        per_column: Dict[str, Dict[str, str]] = {}
        for entry in legacy.get("analyses", []):
            column = entry.get("column") or "colonne"
            text = entry.get("text") or DEFAULT_GENERIC_TEXT
            per_column[column] = {
                "analysis": text,
                "insights": text,
                "anomalies": "",
            }
        conclusion = legacy.get("conclusion") or DEFAULT_GENERIC_TEXT
        return {
            "global_intro": conclusion,
            "global_summary": conclusion,
            "per_column": per_column,
            "correlations": [],
        }
    return _local_default_structure(analysis_results, _extract_plots(visualization_plan))


def _local_default_structure(
    analysis_results: Dict[str, Any],
    plots: List[Dict[str, Any]],
) -> Dict[str, Any]:
    column_types = (analysis_results or {}).get("column_types", {})
    per_column = {
        column: _local_column_text(column, {"profile": {"dtype": dtype}, "graph_types": []})
        for column, dtype in column_types.items()
    }
    if not per_column and plots:
        for plot in plots:
            column = plot.get("column") or "colonne"
            per_column[column] = _local_column_text(column, {"profile": {"dtype": ""}, "graph_types": []})
    intro = "Rapport généré sans IA avancée. Les éléments principaux restent disponibles."

    summary = "Conclusion : exploitez les graphiques pour approfondir les tendances identifiées."
    return {
        "global_intro": intro,
        "global_summary": summary,
        "per_column": per_column,
        "correlations": [],
    }


def generate_texts_ai(
    analysis_results: Optional[Dict[str, Any]],
    visualization_plan: Optional[Any],
    style: str = DEFAULT_STYLE,
) -> Dict[str, Any]:
    analysis_results = analysis_results or {}
    plots = _extract_plots(visualization_plan)
    style_key = (style or DEFAULT_STYLE).lower()
    if style_key not in STYLE_PRESETS:
        style_key = DEFAULT_STYLE

    api_key = os.getenv("OPENAI_API_KEY")
    model_override = os.getenv("OPENAI_TEXT_MODEL")
    config = AIModelConfig(model=model_override or AIModelConfig.model)
    client = _ensure_client(api_key)

    if client is None:
        return _call_module_d_fallback(analysis_results, visualization_plan, style_key)

    try:
        dataset_context = _build_dataset_context(analysis_results, plots)
        per_column: Dict[str, Dict[str, str]] = {}
        grouped_plots = _group_plots_by_column(plots)
        for column, column_plots in grouped_plots.items():
            column_meta = _column_profile(column, analysis_results)
            per_column[column] = generate_column_text(
                column,
                column_meta,
                column_plots,
                analysis_results,
                style_key,
                client,
                config,
            )

        correlations_texts: List[Dict[str, Any]] = []
        relations = (analysis_results or {}).get("relations", {})
        for correlation in relations.get("correlations", []) if isinstance(relations, dict) else []:
            text = generate_correlation_text(correlation, style_key, client, config)
            correlations_texts.append({"cols": correlation.get("columns", []), "text": text})

        global_intro = generate_global_intro(dataset_context, style_key, client, config)
        global_summary = generate_summary(dataset_context, per_column, style_key, client, config)

        return {
            "global_intro": global_intro,
            "global_summary": global_summary,
            "per_column": per_column,
            "correlations": correlations_texts,
        }
    except AIGenerationError:
        return _call_module_d_fallback(analysis_results, visualization_plan, style_key)


__all__ = ["generate_texts_ai"]
