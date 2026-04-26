"""Module H - IA avancée pour la génération de textes métier.

Ce module se situe entre l'analyse automatique (Module B) et la génération de la
présentation (Module E). Il consomme les résultats d'analyse ainsi que la liste
des graphiques prévus, puis produit des textes professionnels structurés prêts
à être injectés dans les slides. L'appel à l'API IA est optionnel : en cas
d'absence de clé ou d'erreur, on revient automatiquement sur Module D.

Fournisseurs supportés (par ordre de priorité) :
  1. Claude (Anthropic) via CLAUDE_API_KEY
  2. OpenAI via OPENAI_API_KEY
"""
from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass
from importlib import import_module
from typing import Any, Dict, List, Optional

import pandas as pd

logger = logging.getLogger(__name__)

try:  # Optional dependency: le module doit rester importable sans openai
    _openai_module = import_module("openai")
    _OpenAIClient = getattr(_openai_module, "OpenAI", None)
except ModuleNotFoundError:  # pragma: no cover
    _OpenAIClient = None

try:  # Optional dependency: Anthropic Claude
    _anthropic_module = import_module("anthropic")
    _AnthropicClient = getattr(_anthropic_module, "Anthropic", None)
except ModuleNotFoundError:  # pragma: no cover
    _AnthropicClient = None

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
    "lite": {
        "description": "Style très concis, 2-3 phrases max.",
        "length": "2 à 3 phrases",
        "focus": "1 tendance principale, 1 insight simple, pas de recommandations lourdes.",
    },
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
        "focus": "Souligne tendances, anomalies et recommandation priorisée.",
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
    """Paramètres d'appel IA (OpenAI ou Claude)."""

    model: str = "gpt-4o-mini"
    claude_model: str = "claude-haiku-4-5-20251001"
    temperature: float = 0.4
    max_tokens: int = 380


class AIGenerationError(RuntimeError):
    """Erreur émise quand l'appel IA échoue."""


# ── Provider selection ─────────────────────────────────────────────────────

def _ensure_client(api_key: Optional[str]) -> Optional[Any]:
    """Instancie le client OpenAI si la dépendance et la clé sont présentes."""
    if _OpenAIClient is None or not api_key:
        return None
    try:
        return _OpenAIClient(api_key=api_key)
    except Exception:  # pragma: no cover
        return None


def _ensure_claude_client(api_key: Optional[str]) -> Optional[Any]:
    """Instancie le client Anthropic si la dépendance et la clé sont présentes."""
    if _AnthropicClient is None or not api_key:
        return None
    try:
        return _AnthropicClient(api_key=api_key)
    except Exception:  # pragma: no cover
        return None


def _resolve_ai_client() -> tuple[Optional[Any], str]:
    """Retourne (client, provider) en priorisant Claude sur OpenAI."""
    claude_key = os.getenv("CLAUDE_API_KEY")
    claude_client = _ensure_claude_client(claude_key)
    if claude_client is not None:
        logger.info("Module H: utilisation de Claude (Anthropic).")
        return claude_client, "claude"

    openai_key = os.getenv("OPENAI_API_KEY")
    openai_client = _ensure_client(openai_key)
    if openai_client is not None:
        logger.info("Module H: utilisation de OpenAI.")
        return openai_client, "openai"

    return None, "none"


def _style_prompt(style_key: str) -> str:
    preset = STYLE_PRESETS.get(style_key, STYLE_PRESETS[DEFAULT_STYLE])
    extra = {
        "lite": "Fournis uniquement l'essentiel, pas de jargon, pas de listes à puces.",
        "short": "Reste ultra synthétique.",
        "normal": "Reste factuel et utile.",
        "executive": "Ajoute une recommandation priorisée quand pertinent.",
    }.get(style_key, "")
    return (
        "Tu es un analyste data senior.\n"
        "Écris en français, ton professionnel.\n"
        f"Style: {preset['description']} ({preset['length']}).\n"
        f"Consigne: {preset['focus']} {extra} Ne mentionne jamais de données absentes."
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
            response_format={"type": "json_object"},
        )
    except Exception as exc:  # pragma: no cover
        raise AIGenerationError(f"Échec OpenAI: {exc}") from exc

    content = (response.choices[0].message.content or "").strip()
    data = _safe_json_loads(content)

    if not isinstance(data, dict):
        fenced = content.strip("` ")
        data = _safe_json_loads(fenced)

    if not isinstance(data, dict):
        raise AIGenerationError("Réponse OpenAI vide ou non JSON.")
    return data


def _call_claude_json(
    client: Any,
    config: AIModelConfig,
    style_key: str,
    user_prompt: str,
) -> Dict[str, Any]:
    if client is None:
        raise AIGenerationError("Client Claude indisponible")
    system_prompt = _style_prompt(style_key) + " Réponds STRICTEMENT en JSON valide, sans aucun texte avant ou après."
    try:
        response = client.messages.create(
            model=config.claude_model,
            max_tokens=config.max_tokens,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
    except Exception as exc:  # pragma: no cover
        raise AIGenerationError(f"Échec Claude: {exc}") from exc

    content = (response.content[0].text if response.content else "").strip()
    # Nettoie les blocs ```json...``` si Claude les ajoute
    if content.startswith("```"):
        content = content.strip("`").lstrip("json").strip()
    data = _safe_json_loads(content)
    if not isinstance(data, dict):
        raise AIGenerationError("Réponse Claude vide ou non JSON.")
    return data


def _call_ai_json(
    client: Any,
    provider: str,
    config: AIModelConfig,
    style_key: str,
    user_prompt: str,
) -> Dict[str, Any]:
    """Appel unifié : dispatche vers OpenAI ou Claude selon le provider."""
    if provider == "claude":
        return _call_claude_json(client, config, style_key, user_prompt)
    return _call_openai_json(client, config, style_key, user_prompt)


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


def _compute_numeric_trend(df: pd.DataFrame, col: str, axis_col: Optional[str] = None) -> Dict[str, Any]:
    """Compute trend stats for a numeric column: direction, pct change, labels for min/max."""
    try:
        values = pd.to_numeric(df[col], errors="coerce")
        valid = values.dropna()
        if len(valid) < 2:
            return {}
        n = len(valid)
        first_half_avg = float(valid.iloc[: n // 2].mean())
        second_half_avg = float(valid.iloc[n // 2 :].mean())
        pct_half = (
            (second_half_avg - first_half_avg) / abs(first_half_avg) * 100
            if first_half_avg != 0
            else 0.0
        )
        trend = "hausse" if pct_half > 1 else "baisse" if pct_half < -1 else "stable"

        start_val = float(valid.iloc[0])
        end_val = float(valid.iloc[-1])
        total_pct = (end_val - start_val) / abs(start_val) * 100 if start_val != 0 else 0.0

        # Min / max labels via axis column
        min_label, max_label = "", ""
        if axis_col and axis_col in df.columns:
            idx_min = values.idxmin()
            idx_max = values.idxmax()
            if pd.notna(idx_min):
                min_label = str(df[axis_col].iloc[int(idx_min)])
            if pd.notna(idx_max):
                max_label = str(df[axis_col].iloc[int(idx_max)])

        return {
            "trend": trend,
            "pct_change_half": round(abs(pct_half), 1),
            "total_pct_change": round(total_pct, 1),
            "start_value": round(start_val, 2),
            "end_value": round(end_val, 2),
            "min_val": round(float(valid.min()), 2),
            "max_val": round(float(valid.max()), 2),
            "mean_val": round(float(valid.mean()), 2),
            "min_label": min_label,
            "max_label": max_label,
        }
    except Exception:  # pragma: no cover
        return {}


def _compute_conclusion_stats(df: pd.DataFrame, axis_col: Optional[str]) -> List[Dict[str, Any]]:
    """Compute overall % evolution per numeric column for the conclusion prompt."""
    result: List[Dict[str, Any]] = []
    try:
        period_start = str(df[axis_col].iloc[0]) if axis_col and axis_col in df.columns else None
        period_end = str(df[axis_col].iloc[-1]) if axis_col and axis_col in df.columns else None
        for col in df.select_dtypes(include="number").columns:
            vals = pd.to_numeric(df[col], errors="coerce").dropna()
            if len(vals) < 2:
                continue
            start = float(vals.iloc[0])
            end = float(vals.iloc[-1])
            pct = (end - start) / abs(start) * 100 if start != 0 else 0.0
            result.append(
                {
                    "col": col,
                    "pct_change": round(pct, 1),
                    "start": round(start, 2),
                    "end": round(end, 2),
                    "period_start": period_start,
                    "period_end": period_end,
                }
            )
    except Exception:  # pragma: no cover
        pass
    return result


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

    return {
        "analysis": " ".join(analysis_parts),
        "insights": " ".join(insights_parts),
        "anomalies": "",
    }


def generate_column_text(
    column: str,
    column_meta: Dict[str, Any],
    plots: List[Dict[str, Any]],
    analysis_results: Dict[str, Any],
    style: str,
    client: Any,
    config: AIModelConfig,
    provider: str = "openai",
    df: Optional[pd.DataFrame] = None,
    axis_column: Optional[str] = None,
) -> Dict[str, str]:
    graph_types = sorted({plot.get("graph_type", "?") for plot in plots})

    # ── Bivariate / correlation column (name = "ColA+ColB") ─────────────────
    if "+" in column:
        col_parts = column.split("+", 1)
        col_a, col_b = col_parts[0].strip(), col_parts[1].strip()
        corr_value = next(
            (p.get("correlation") for p in plots if p.get("correlation") is not None),
            None,
        )
        r = corr_value if corr_value is not None else 0.0
        if abs(r) >= 0.90:
            strength = "quasi-parfaite"
        elif abs(r) >= 0.70:
            strength = "forte"
        elif abs(r) >= 0.50:
            strength = "modérée"
        else:
            strength = "faible"
        direction = "positive" if r >= 0 else "négative"

        prompt = (
            f"Corrélation {direction} {strength} (r = {r:.2f}) entre '{col_a}' et '{col_b}'.\n\n"
            "Écris en JSON avec deux clés :\n"
            "- 'analysis' (1 phrase) : décris la relation en termes business concrets — "
            "traduis la force de la corrélation en mots, pas en chiffres bruts.\n"
            "- 'insights' (1-2 phrases) : quelle implication opérationnelle ? "
            "Si les deux variables croissent en parallèle dans le temps, précise que c'est "
            "peut-être lié à une tendance commune plutôt qu'un lien causal direct. "
            "Conclus par ce que ça implique concrètement (coût, opportunité, risque).\n"
            "Interdiction : pas de jargon statistique, pas de 'il est recommandé', "
            "parle comme un consultant senior."
        )
    else:
        # ── Single numeric column — use computed stats if df is available ───
        trend_stats = _compute_numeric_trend(df, column, axis_column) if df is not None else {}
        diag_cols = (analysis_results or {}).get("diagnostic", {}).get("columns", {})
        col_type = (analysis_results or {}).get("column_types", {}).get(column, "")
        axis_col_val = (
            f"{df[axis_column].iloc[0]} à {df[axis_column].iloc[-1]}"
            if axis_column and df is not None and axis_column in df.columns
            else "inconnue"
        )

        if trend_stats:
            prompt = (
                "Tu analyses une colonne d'un rapport de performance business.\n\n"
                f"Colonne : {column} | Type : {_friendly_dtype(col_type)}\n"
                f"Période couverte : {axis_col_val}\n"
                f"Min : {trend_stats['min_val']}"
                + (f" ({trend_stats['min_label']})" if trend_stats.get("min_label") else "")
                + f" | Max : {trend_stats['max_val']}"
                + (f" ({trend_stats['max_label']})" if trend_stats.get("max_label") else "")
                + f" | Moyenne : {trend_stats['mean_val']}\n"
                f"Évolution totale : {trend_stats['start_value']} → {trend_stats['end_value']} "
                f"({trend_stats['total_pct_change']:+.1f}%)\n"
                f"Tendance sur la période : en {trend_stats['trend']} "
                f"de {trend_stats['pct_change_half']:.0f}% entre la 1re et la 2e moitié\n\n"
                "Écris en JSON avec deux clés :\n"
                "- 'analysis' (2 phrases max) : tendance principale + valeurs remarquables. "
                "Mentionne la progression ou le pic si pertinent.\n"
                "- 'insights' (1-2 phrases) : interprétation business actionnable. "
                "Qu'est-ce qui est notable ou à surveiller ? Aucune reformulation des chiffres bruts. "
                "Pas de formulations génériques type 'les données montrent'. "
                "Parle comme un consultant orienté décision."
            )
        else:
            # Fallback when df is not available or column is non-numeric
            payload = {
                "column": column,
                "profile": column_meta,
                "graph_types": graph_types,
                "issues": _column_issues(column, analysis_results),
                "min": column_meta.get("min"),
                "max": column_meta.get("max"),
                "mean": column_meta.get("mean"),
                "max_label": column_meta.get("max_label"),
                "min_label": column_meta.get("min_label"),
            }
            prompt = (
                "Analyse uniquement la colonne décrite par le JSON ci-dessous.\n"
                "Écris en français, ton professionnel.\n"
                "- 'analysis' : 2 phrases descriptives (tendance, valeurs dominantes).\n"
                "- 'insights' : 1-2 phrases d'interprétation métier concrète. Pas de formulations génériques.\n"
                "Réponds en JSON avec uniquement les clés 'analysis' et 'insights'.\n"
                f"JSON: {json.dumps(payload, ensure_ascii=False)}"
            )

    response = _call_ai_json(client, provider, config, style, prompt)
    if not all(key in response for key in ("analysis", "insights")):
        raise AIGenerationError("Format JSON inattendu pour l'analyse de colonne.")
    return {
        "analysis": response.get("analysis") or DEFAULT_GENERIC_TEXT,
        "insights": response.get("insights") or DEFAULT_GENERIC_TEXT,
        "anomalies": "",
    }


def generate_global_intro(
    dataset_context: Dict[str, Any],
    style: str,
    client: Any,
    config: AIModelConfig,
    provider: str = "openai",
) -> str:
    prompt = (
        "À partir du résumé JSON suivant, écris une introduction de rapport.\n"
        "Mentionne le volume de données disponible s'il est fourni et les familles de colonnes.\n"
        f"JSON: {json.dumps(dataset_context, ensure_ascii=False)}"
    )
    response = _call_ai_json(client, provider, config, style, prompt + "\nRéponds en JSON avec la clé unique 'text'.")
    if "text" not in response or not str(response.get("text", "")).strip():
        raise AIGenerationError("Réponse JSON invalide pour l'introduction.")
    return str(response["text"]).strip()


def generate_summary(
    dataset_context: Dict[str, Any],
    per_column: Dict[str, Dict[str, str]],
    style: str,
    client: Any,
    config: AIModelConfig,
    provider: str = "openai",
    df: Optional[pd.DataFrame] = None,
    axis_column: Optional[str] = None,
) -> str:
    conclusion_stats = _compute_conclusion_stats(df, axis_column) if df is not None else []

    if conclusion_stats:
        n_periods = len(df) if df is not None else "?"
        period_start = conclusion_stats[0].get("period_start") or "début"
        period_end = conclusion_stats[0].get("period_end") or "fin"
        evolutions = "\n".join(
            f"- {s['col']} : {s['pct_change']:+.0f}% ({s['start']} → {s['end']})"
            for s in conclusion_stats
        )
        prompt = (
            f"Synthèse d'un rapport de performance sur {n_periods} périodes "
            f"({period_start} → {period_end}).\n\n"
            f"Évolutions clés :\n{evolutions}\n\n"
            "Écris une conclusion de 3-4 phrases pour un dirigeant.\n"
            "Structure : 1 phrase sur les points forts, 1 sur les points de vigilance, "
            "1 recommandation concrète pour la suite.\n"
            "Ton direct, orienté action. Pas de liste à puces. Pas de répétition des chiffres bruts.\n"
            "Réponds en JSON avec la clé unique 'text'."
        )
    else:
        condensed = {
            "dataset": dataset_context,
            "highlights": {
                column: texts.get("insights") for column, texts in per_column.items()
            },
        }
        prompt = (
            "Génère une conclusion finale orientée décision à partir du JSON fourni.\n"
            "Structure : points forts, points de vigilance, recommandation concrète.\n"
            "Ton direct, 3-4 phrases max, pour un dirigeant.\n"
            f"JSON: {json.dumps(condensed, ensure_ascii=False)}\n"
            "Réponds en JSON avec la clé unique 'text'."
        )

    response = _call_ai_json(client, provider, config, style, prompt)
    if "text" not in response or not str(response.get("text", "")).strip():
        raise AIGenerationError("Réponse JSON invalide pour la synthèse.")
    return str(response["text"]).strip()


def generate_correlation_text(
    correlation: Dict[str, Any],
    style: str,
    client: Any,
    config: AIModelConfig,
    provider: str = "openai",
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
    response = _call_ai_json(client, provider, config, style, prompt)
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
    df: Optional[pd.DataFrame] = None,
    axis_column: Optional[str] = None,
) -> Dict[str, Any]:
    analysis_results = analysis_results or {}
    plots = _extract_plots(visualization_plan)
    style_key = (style or DEFAULT_STYLE).lower()
    if style_key not in STYLE_PRESETS:
        style_key = DEFAULT_STYLE

    # Resolve axis_column from analysis if not passed explicitly
    if axis_column is None:
        axis_column = (analysis_results or {}).get("axis_column")

    model_override = os.getenv("OPENAI_TEXT_MODEL")
    config = AIModelConfig(model=model_override or AIModelConfig.model)

    client, provider = _resolve_ai_client()

    if client is None:
        logger.warning("Module H: aucune clé API disponible → fallback Module D.")
        result = _call_module_d_fallback(analysis_results, visualization_plan, style_key)
        result["_fallback"] = True
        result["_fallback_reason"] = "clé API absente"
        return result

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
                provider=provider,
                df=df,
                axis_column=axis_column,
            )

        correlations_texts: List[Dict[str, Any]] = []
        relations = (analysis_results or {}).get("relations", {})
        for correlation in relations.get("correlations", []) if isinstance(relations, dict) else []:
            text = generate_correlation_text(correlation, style_key, client, config, provider=provider)
            correlations_texts.append({"cols": correlation.get("columns", []), "text": text})

        global_intro = generate_global_intro(dataset_context, style_key, client, config, provider=provider)
        global_summary = generate_summary(
            dataset_context,
            per_column,
            style_key,
            client,
            config,
            provider=provider,
            df=df,
            axis_column=axis_column,
        )

        return {
            "global_intro": global_intro,
            "global_summary": global_summary,
            "per_column": per_column,
            "correlations": correlations_texts,
        }
    except AIGenerationError as exc:
        logger.warning("Module H: échec de la génération IA (%s) → fallback Module D.", exc)
        result = _call_module_d_fallback(analysis_results, visualization_plan, style_key)
        result["_fallback"] = True
        result["_fallback_reason"] = str(exc)
        return result


__all__ = ["generate_texts_ai"]
