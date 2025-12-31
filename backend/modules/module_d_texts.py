"""Module D - Automatic text generation for charts.

This module receives the structured dataset analysis (Module B output) plus the
list of generated plots (Module C output) and produces professional copy for
slides. It can either call a language model (OpenAI compatible) or fall back to
predefined sentences when `use_ai=False` or if any API error occurs.
"""
from __future__ import annotations

from dataclasses import dataclass
from importlib import import_module
from typing import Any, Dict, List, Optional

try:  # Optional dependency; module still works in fallback mode without openai
    _openai_module = import_module("openai")
    _OpenAIClient = getattr(_openai_module, "OpenAI")
except ModuleNotFoundError:  # pragma: no cover
    _OpenAIClient = None

OpenAIType = Any

DEFAULT_GENERIC_TEXT = (
    "Les données présentées mettent en évidence plusieurs tendances clés. "
    "Les graphiques permettent de visualiser les variations principales et "
    "aident à comprendre rapidement la structure du dataset."
)


@dataclass
class AIConfig:
    model: str = "gpt-4o-mini"
    temperature: float = 0.4
    max_tokens: int = 220


def _normalize_column_summary(column_summary: Any) -> Dict[str, Any]:
    if isinstance(column_summary, dict):
        return column_summary
    if isinstance(column_summary, str):
        return {"dtype": column_summary}
    return {}


def _build_chart_prompt(chart: Dict[str, Any], column_summary: Any) -> str:
    column_name = chart.get("column", "colonne inconnue")
    graph_type = chart.get("graph_type", "graphique")
    info = _normalize_column_summary(column_summary)
    summary_parts = [
        f"Type de graphique : {graph_type}",
        f"Colonne analysée : {column_name}",
    ]
    dtype = info.get("dtype", "inconnu")
    missing_pct = info.get("missing_percent", "n/a")
    unique_values = info.get("unique_values", "n/a")
    summary_parts.append(f"Type détecté : {dtype}")
    summary_parts.append(f"Valeurs manquantes : {missing_pct}%")
    summary_parts.append(f"Valeurs uniques : {unique_values}")

    prompt = (
        "Voici des informations extraites d'un tableau de données.\n"
        f"{' - '.join(summary_parts)}\n"
        "Explique en 3 phrases professionnelles ce que montre ce graphique, "
        "en mettant en avant les tendances visibles et leur interprétation business."
    )
    return prompt


def _build_conclusion_prompt(analysis: Dict[str, Any], plots: List[Dict[str, Any]]) -> str:
    column_types = analysis.get("column_types", {})
    issues = analysis.get("issues", {})
    relations = analysis.get("relations", {})

    prompt = [
        "Produit une synthèse globale du dataset en 4 à 6 phrases max.",
        "Ton : professionnel, synthétique.",
        f"Colonnes et types détectés : {column_types}.",
        f"Problèmes relevés : {issues}.",
        f"Relations intéressantes : {relations}.",
        f"Graphiques générés : {[ (p.get('column'), p.get('graph_type')) for p in plots ]}.",
        "Souligne les tendances principales et une recommandation générale.",
    ]
    return "\n".join(prompt)


def _call_openai(prompt: str, client: OpenAIType, config: AIConfig) -> str:
    response = client.chat.completions.create(
        model=config.model,
        temperature=config.temperature,
        max_tokens=config.max_tokens,
        messages=[
            {"role": "system", "content": "Tu es un analyste data professionnel."},
            {"role": "user", "content": prompt},
        ],
    )
    return response.choices[0].message.content.strip()


def _ensure_client(api_key: Optional[str]) -> Optional[OpenAIType]:
    if _OpenAIClient is None or not api_key:
        return None
    try:
        return _OpenAIClient(api_key=api_key)
    except Exception:  # pragma: no cover
        return None


def _generate_text(
    prompt: str,
    client: Optional[OpenAIType],
    config: AIConfig,
    fallback_text: str,
) -> str:
    if not client:
        return fallback_text
    try:
        return _call_openai(prompt, client, config)
    except Exception:
        return fallback_text


def _generate_fallback_text(column_name: str, column_summary: Dict[str, Any], graph_type: str) -> str:
    """Generate unique descriptive text for each column based on its statistics."""
    
    dtype = column_summary.get("dtype", "données")
    missing_pct = column_summary.get("missing_percent", 0)
    unique_values = column_summary.get("unique_values", "n/a")
    
    # Build unique sentences based on column characteristics
    sentences = []
    
    # Intro sentence with column name and type
    type_labels = {
        "numerique": "numérique",
        "categorie": "catégorielle",
        "date": "temporelle",
        "texte": "textuelle"
    }
    friendly_type = type_labels.get(dtype, dtype)
    sentences.append(f"La colonne {column_name} contient des données {friendly_type}.")
    
    # Add diversity info
    if isinstance(unique_values, int):
        if unique_values <= 5:
            sentences.append(f"On observe une faible diversité avec seulement {unique_values} valeurs distinctes.")
        elif unique_values <= 20:
            sentences.append(f"La diversité est modérée avec {unique_values} modalités différentes.")
        else:
            sentences.append(f"Une forte variété est constatée avec {unique_values} valeurs uniques.")
    
    # Add missing data info
    if missing_pct > 0:
        if missing_pct < 10:
            sentences.append(f"Les données sont quasi-complètes ({missing_pct:.1f}% de valeurs manquantes).")
        elif missing_pct < 30:
            sentences.append(f"Attention au taux modéré de valeurs manquantes ({missing_pct:.1f}%).")
        else:
            sentences.append(f"Important : {missing_pct:.1f}% des valeurs sont absentes, ce qui peut impacter l'analyse.")
    else:
        sentences.append("Aucune valeur manquante détectée, données complètes.")
    
    # Add graph-specific insight
    graph_insights = {
        "histogram": "La distribution permet d'identifier les valeurs les plus fréquentes et les éventuels pics.",
        "barchart": "Le graphique révèle les catégories dominantes et leur répartition.",
        "linechart": "L'évolution temporelle met en évidence les tendances et variations.",
        "boxplot": "Les statistiques montrent la dispersion et les valeurs extrêmes.",
        "density": "La courbe de densité illustre la concentration des valeurs."
    }
    if graph_type in graph_insights:
        sentences.append(graph_insights[graph_type])
    
    return " ".join(sentences)


def generate_texts(
    analysis: Dict[str, Any],
    plots: List[Dict[str, Any]],
    use_ai: bool = True,
    api_key: Optional[str] = None,
    model_config: Optional[AIConfig] = None,
) -> Dict[str, Any]:
    config = model_config or AIConfig()
    client = _ensure_client(api_key) if use_ai else None

    column_info = (analysis or {}).get("diagnostic", {}).get("columns", {})
    if not column_info:
        column_info = analysis.get("column_types", {})

    analyses_output = []
    for plot in plots:
        column_name = plot.get("column")
        column_summary = column_info.get(column_name, {}) if isinstance(column_info, dict) else {}
        
        # Generate unique text per column based on stats
        if client:
            prompt = _build_chart_prompt(plot, column_summary)
            text = _generate_text(prompt, client, config, DEFAULT_GENERIC_TEXT)
        else:
            # Fallback: generate specific text from column stats
            text = _generate_fallback_text(column_name, column_summary, plot.get("graph_type"))
        
        analyses_output.append(
            {
                "column": column_name,
                "graph_type": plot.get("graph_type"),
                "title": f"Analyse de {column_name}",
                "text": text,
            }
        )

    conclusion_prompt = _build_conclusion_prompt(analysis, plots)
    conclusion_text = _generate_text(conclusion_prompt, client, config, DEFAULT_GENERIC_TEXT)

    return {
        "analyses": analyses_output,
        "conclusion": conclusion_text,
    }
