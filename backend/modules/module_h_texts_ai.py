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


ISSUE_LABELS = {
    "empty_columns": "colonne vide",
    "high_missing": "taux de valeurs manquantes élevé",
    "bad_format": "format incohérent",
    "duplicated_columns": "risque de doublon",
    "long_text_columns": "texte très long",
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


def _friendly_dtype(dtype: str) -> str:
    mapping = {
        "numeric_continuous": "variable numérique continue",
        "numeric_discrete": "variable numérique discrète",
        "categorical": "variable catégorielle",
        "categorie": "variable catégorielle",
        "boolean": "champ booléen",
        "text": "champ texte",
        "date": "donnée temporelle",
        "numerique": "variable numérique",
    }
    stripped = (dtype or "colonne").strip().lower()
    return mapping.get(stripped, dtype or "colonne")


def _describe_missing_ratio(value: Any) -> str:
    try:
        pct = float(value)
    except (TypeError, ValueError):
        return ""
    if pct <= 0:
        return "Aucune valeur manquante n'a été détectée."
    if pct <= 10:
        return f"Seulement {pct:.0f}% de valeurs manquent à ce stade."
    if pct <= 30:
        return f"Le taux de valeurs manquantes reste modéré ({pct:.0f}%)."
    return f"Attention : environ {pct:.0f}% des valeurs sont absentes."


def _describe_unique_values(value: Any, column: str) -> str:
    try:
        count = int(value)
    except (TypeError, ValueError):
        return ""
    if count <= 1:
        return f"La colonne {column} est quasi constante."
    if count <= 5:
        return f"La colonne {column} ne compte que {count} modalités distinctes."
    if count <= 20:
        return f"La diversité reste contenue avec {count} valeurs distinctes."
    return f"On observe une forte variété avec {count} valeurs distinctes."


def _format_notable_values(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        items = list(value)
        preview = ", ".join(str(item) for item in items[:5])
        if len(items) > 5:
            preview += ", ..."
        return preview
    return str(value)


def _friendly_issue_name(issue_key: str) -> str:
    return ISSUE_LABELS.get(issue_key, issue_key.replace("_", " "))


def _insight_guidance_for_dtype(dtype_key: str) -> str:
    dtype_key = (dtype_key or "").lower()
    if dtype_key.startswith("numeric") or dtype_key == "numerique":
        return "Surveillez la dispersion et les valeurs extrêmes pour repérer rapidement les comportements atypiques."
    if dtype_key in {"categorical", "categorie"}:
        return "Comparez le poids des catégories dominantes afin d'identifier les segments prioritaires."
    if dtype_key == "date":
        return "Une lecture chronologique mettra en évidence la saisonnalité et les ruptures d'activité."
    if dtype_key == "boolean":
        return "Mesurez l'équilibre entre les deux modalités pour prévoir la charge opérationnelle."
    return "Inspectez les termes les plus fréquents pour comprendre les thèmes récurrents."


def _local_column_text(column: str, metadata: Dict[str, Any]) -> Dict[str, str]:
    profile = metadata.get("profile", {}) or {}
    dtype_key = (profile.get("column_type") or profile.get("dtype") or "colonne").lower()
    dtype_label = _friendly_dtype(dtype_key)
    graph_types = metadata.get("graph_types") or []
    graph_sentence = (
        "les graphiques " + ", ".join(graph_types)
        if graph_types
        else "les indicateurs descriptifs disponibles"
    )
    analysis_parts = [
        f"La colonne {column} ({dtype_label}) est explorée via {graph_sentence}."
    ]
    unique_sentence = _describe_unique_values(profile.get("unique_values"), column)
    if unique_sentence:
        analysis_parts.append(unique_sentence)
    missing_sentence = _describe_missing_ratio(profile.get("missing_percent"))
    if missing_sentence:
        analysis_parts.append(missing_sentence)

    insights_parts = [_insight_guidance_for_dtype(dtype_key)]
    notable = profile.get("sample") or profile.get("examples")
    formatted_values = _format_notable_values(notable)
    if formatted_values:
        insights_parts.append(f"Valeurs mises en avant : {formatted_values}.")

    issues = metadata.get("issues") or []
    if issues:
        labels = ", ".join(_friendly_issue_name(issue) for issue in issues)
        anomalies = f"Points de vigilance : {labels}."
    else:
        anomalies = "Aucun signal faible particulier n'a été détecté pour cette colonne."

    return {
        "analysis": " ".join(analysis_parts),
        "insights": " ".join(insights_parts),
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
    column_types = (analysis_results or {}).get("column_types", {}) or {}
    diagnostic_columns = {}
    diagnostic = (analysis_results or {}).get("diagnostic")
    if isinstance(diagnostic, dict):
        diagnostic_columns = diagnostic.get("columns", {}) if isinstance(diagnostic.get("columns"), dict) else {}

    per_column: Dict[str, Dict[str, str]] = {}
    grouped_plots = _group_plots_by_column(plots)

    def _profile_for(column: str) -> Dict[str, Any]:
        profile = {}
        if isinstance(diagnostic_columns, dict):
            candidate = diagnostic_columns.get(column)
            if isinstance(candidate, dict):
                profile = candidate.copy()
        if column in column_types and "column_type" not in profile:
            profile["column_type"] = column_types[column]
        return profile

    if grouped_plots:
        for column, column_plots in grouped_plots.items():
            graph_types = sorted(
                {
                    plot.get("graph_type", "graphique")
                    for plot in column_plots
                    if plot.get("graph_type")
                }
            )
            per_column[column] = _local_column_text(
                column,
                {
                    "profile": _profile_for(column),
                    "graph_types": graph_types,
                    "issues": _column_issues(column, analysis_results),
                },
            )
    else:
        for column, dtype in column_types.items():
            profile = _profile_for(column)
            if not profile:
                profile = {"column_type": dtype}
            per_column[column] = _local_column_text(
                column,
                {
                    "profile": profile,
                    "graph_types": [],
                    "issues": _column_issues(column, analysis_results),
                },
            )

    if not per_column:
        per_column["dataset"] = {
            "analysis": "Le dataset ne contient pas de colonnes exploitables, mais la structure reste disponible.",
            "insights": "Chargez un fichier avec davantage de colonnes numériques ou catégorielles pour enrichir le rapport.",
            "anomalies": "Aucune anomalie détectée sur l'échantillon disponible.",
        }

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
