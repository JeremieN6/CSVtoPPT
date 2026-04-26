"""Module C - Automatic chart generation.

This module turns the structured output from Module B plus the original
DataFrame into a set of PNG charts ready for downstream consumption (e.g.
PowerPoint slides). All plots are rendered with matplotlib only and saved inside
an output directory supplied by the caller.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Sequence

import matplotlib
matplotlib.use("Agg")  # backend non graphique (serveur mutualisé)

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

DEFAULT_COLORS = ["#2563EB", "#16A34A", "#F97316", "#9333EA", "#F43F5E"]


def _set_style() -> None:
    plt.rcParams.update(
        {
            "axes.facecolor": "white",
            "figure.facecolor": "white",
            "axes.titlesize": 12,
            "axes.labelsize": 10,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
        }
    )


_set_style()


def plot_histogram(series: pd.Series, output_path: Path) -> None:
    series = series.dropna()
    if series.empty:
        raise ValueError("Aucune donnée numérique pour l'histogramme.")

    fig, ax = _init_figure()
    ax.hist(series, bins=15, color=DEFAULT_COLORS[0], edgecolor="white")
    ax.set_title(f"Distribution de {series.name}")
    ax.set_xlabel(series.name)
    ax.set_ylabel("Fréquence")
    _finalize_plot(fig, output_path)


def plot_density(series: pd.Series, output_path: Path) -> None:
    series = series.dropna()
    if series.empty:
        raise ValueError("Aucune donnée numérique pour la densité.")

    fig, ax = _init_figure()
    density = series.plot(kind="kde", ax=ax, color=DEFAULT_COLORS[1], linewidth=2)
    x_values = density.get_lines()[0].get_xdata()
    y_values = density.get_lines()[0].get_ydata()
    ax.fill_between(x_values, y_values, color=DEFAULT_COLORS[1], alpha=0.2)
    ax.set_title(f"Densité de {series.name}")
    ax.set_xlabel(series.name)
    ax.set_ylabel("Densité")
    _finalize_plot(fig, output_path)


def plot_boxplot(series: pd.Series, output_path: Path) -> None:
    series = series.dropna()
    if series.empty:
        raise ValueError("Aucune donnée pour le boxplot.")

    fig, ax = _init_figure(figsize=(4, 5))
    ax.boxplot(series, vert=True, patch_artist=True, boxprops={"facecolor": DEFAULT_COLORS[2]})
    ax.set_title(f"Boxplot de {series.name}")
    ax.set_ylabel(series.name)
    _finalize_plot(fig, output_path)


def plot_barchart(series: pd.Series, output_path: Path, horizontal: bool = False) -> None:
    value_counts = series.dropna().value_counts().sort_values(ascending=False).head(20)
    if value_counts.empty:
        raise ValueError("Aucune donnée exploitable pour le diagramme en barres.")

    fig, ax = _init_figure(figsize=(6, 4 + len(value_counts) * 0.2))
    colors = _repeat_colors(len(value_counts))
    if horizontal:
        ax.barh(value_counts.index.astype(str), value_counts.values, color=colors)
        ax.set_xlabel("Occurrences")
        ax.set_ylabel(series.name)
    else:
        ax.bar(value_counts.index.astype(str), value_counts.values, color=colors)
        ax.set_ylabel("Occurrences")
        ax.set_xlabel(series.name)
        for label in ax.get_xticklabels():
            label.set_rotation(45)
            label.set_ha("right")
    ax.set_title(f"Répartition de {series.name}")
    _finalize_plot(fig, output_path)


def plot_linechart(
    index: pd.Series | pd.Index | Sequence, values: pd.Series, output_path: Path, title: str | None = None, ylabel: str | None = None
) -> None:
    x_index = pd.Index(index)
    cleaned = pd.Series(values.values, index=x_index).dropna()
    cleaned = cleaned.sort_index()
    if cleaned.empty:
        raise ValueError("Données insuffisantes pour une courbe temporelle.")

    fig, ax = _init_figure()
    ax.plot(cleaned.index, cleaned.values, color=DEFAULT_COLORS[0], linewidth=2, marker="o")
    ax.set_title(title or "Évolution")
    ax.set_xlabel("Temps")
    ax.set_ylabel(ylabel or (values.name or "Valeur"))
    fig.autofmt_xdate()
    _finalize_plot(fig, output_path)


def plot_heatmap(matrix: pd.DataFrame, output_path: Path, title: str = "Heatmap") -> None:
    if matrix.empty:
        raise ValueError("La matrice est vide, heatmap impossible.")

    fig, ax = _init_figure(figsize=(5, 4))
    heatmap = ax.imshow(matrix.values, cmap="Blues", aspect="auto")
    ax.set_xticks(range(len(matrix.columns)))
    ax.set_xticklabels(matrix.columns, rotation=45, ha="right")
    ax.set_yticks(range(len(matrix.index)))
    ax.set_yticklabels(matrix.index)
    ax.set_title(title)
    fig.colorbar(heatmap, ax=ax)
    _finalize_plot(fig, output_path)


def plot_line_with_axis(
    df: pd.DataFrame, col: str, x_col: str, output_path: Path, title: str | None = None
) -> None:
    """Line chart for a numeric column using a label column (e.g. Mois) as X-axis."""
    x = df[x_col].astype(str)
    y = pd.to_numeric(df[col], errors="coerce")

    if y.dropna().empty:
        raise ValueError(f"Aucune valeur numérique pour la colonne {col}.")

    fig, ax = _init_figure(figsize=(10, 5))
    positions = list(range(len(x)))
    ax.plot(positions, y.values, color=DEFAULT_COLORS[0], linewidth=2, marker="o", markersize=6)
    ax.fill_between(positions, y.values, alpha=0.1, color=DEFAULT_COLORS[0])
    ax.set_xticks(positions)
    ax.set_xticklabels(list(x), rotation=45, ha="right", fontsize=9)
    ax.set_title(
        title or f"Évolution de {col.replace('_', ' ')}",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.set_ylabel(col.replace("_", " "), fontsize=10)
    ax.set_xlabel(x_col.replace("_", " "), fontsize=10)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.grid(axis="y", linestyle="--", alpha=0.4)
    _finalize_plot(fig, output_path)


def plot_scatter_with_trend(
    df: pd.DataFrame, col_x: str, col_y: str, label_col: str | None, output_path: Path
) -> None:
    """Scatter plot between two numeric columns with a trend line and optional point labels."""
    x = pd.to_numeric(df[col_x], errors="coerce")
    y = pd.to_numeric(df[col_y], errors="coerce")

    if x.dropna().empty or y.dropna().empty:
        raise ValueError(f"Données insuffisantes pour le scatter {col_x} vs {col_y}.")

    fig, ax = _init_figure(figsize=(10, 5))
    ax.scatter(x, y, color=DEFAULT_COLORS[3], s=80, alpha=0.8, edgecolors="white", linewidth=0.8)

    mask = x.notna() & y.notna()
    if mask.sum() >= 2:
        z = np.polyfit(x[mask], y[mask], 1)
        p = np.poly1d(z)
        x_line = np.linspace(float(x.min()), float(x.max()), 100)
        ax.plot(
            x_line, p(x_line), "--",
            color=DEFAULT_COLORS[4], alpha=0.7, linewidth=1.5, label="Tendance"
        )

    if label_col and label_col in df.columns:
        for i, label in enumerate(df[label_col]):
            if pd.notna(x.iloc[i]) and pd.notna(y.iloc[i]):
                ax.annotate(
                    str(label),
                    (x.iloc[i], y.iloc[i]),
                    textcoords="offset points",
                    xytext=(5, 5),
                    fontsize=7,
                    alpha=0.8,
                )

    ax.set_xlabel(col_x.replace("_", " "), fontsize=10)
    ax.set_ylabel(col_y.replace("_", " "), fontsize=10)
    ax.set_title(
        f"{col_x.replace('_', ' ')} vs {col_y.replace('_', ' ')}",
        fontsize=13,
        fontweight="bold",
        pad=12,
    )
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, _: f"{v:,.0f}"))
    ax.grid(linestyle="--", alpha=0.3)
    ax.legend(fontsize=8)
    _finalize_plot(fig, output_path)


# ----------------------------- internal helpers ---------------------------- #

def _plot_single(series: pd.Series, column_type: str, graph_type: str, output_file: Path) -> None:
    numeric_series = pd.to_numeric(series, errors="coerce")
    graph_type = graph_type.lower()
    if graph_type == "histogram":
        plot_histogram(numeric_series, output_file)
    elif graph_type == "boxplot":
        plot_boxplot(numeric_series, output_file)
    elif graph_type == "density":
        plot_density(numeric_series, output_file)
    elif graph_type in {"barchart", "top_categories"}:
        if column_type == "date":
            counts = _aggregate_datetime_counts(series)
            plot_barchart_from_counts(counts, output_file)
        else:
            horizontal = series.dropna().astype(str).str.len().mean() > 12
            plot_barchart(series, output_file, horizontal=horizontal)
    elif graph_type == "linechart":
        if column_type == "date":
            counts = _aggregate_datetime_counts(series)
            if counts.empty:
                raise ValueError("Pas assez de dates pour une courbe temporelle.")
            plot_linechart(
                counts.index,
                counts,
                output_file,
                title=f"Évolution de {series.name}",
                ylabel="Occurrences",
            )
        else:
            numeric_series = numeric_series.dropna()
            if numeric_series.empty:
                raise ValueError("Pas assez de valeurs numériques pour une courbe.")
            index = pd.RangeIndex(start=0, stop=len(numeric_series))
            plot_linechart(
                index,
                numeric_series,
                output_file,
                title=f"Évolution de {series.name}",
                ylabel=series.name,
            )
    else:
        raise ValueError(f"Graphique non supporté : {graph_type}")


def _handle_relations(
    df: pd.DataFrame,
    analysis: Dict[str, Any],
    output_path: Path,
    output: Dict[str, List[Dict[str, Any]]],
    axis_column: str | None = None,
) -> None:
    relations = analysis.get("relations", {})
    seen_pairs: set = set()

    # Correlations -> scatter plot with trend line (replaces correlation heatmap)
    for relation in relations.get("correlations", []):
        cols = relation.get("columns", [])
        if len(cols) != 2:
            continue
        pair = tuple(sorted(cols))
        if pair in seen_pairs:
            continue
        seen_pairs.add(pair)
        col_x, col_y = cols[0], cols[1]
        file_path = output_path / f"{col_x}+{col_y}__scatter.png"
        try:
            plot_scatter_with_trend(df, col_x, col_y, axis_column, file_path)
            output["plots"].append(
                {
                    "column": f"{col_x}+{col_y}",
                    "graph_type": "scatter_trend",
                    "file_path": str(file_path),
                    "correlation": relation.get("value"),
                    "columns": list(cols),
                }
            )
        except Exception as exc:  # pylint: disable=broad-except
            output["errors"].append(
                {"column": f"{col_x}+{col_y}", "graph_type": "scatter_trend", "reason": str(exc)}
            )

    # Categorical pairs -> heatmap, but skip pairs already covered by correlations
    for pair in relations.get("categorical_pairs", []):
        cols = pair.get("columns", [])
        if len(cols) != 2:
            continue
        pair_key = tuple(sorted(cols))
        if pair_key in seen_pairs:
            continue
        seen_pairs.add(pair_key)
        pivot = pd.crosstab(df[cols[0]], df[cols[1]])
        if pivot.size == 0 or pivot.shape[0] > 30 or pivot.shape[1] > 30:
            continue
        file_path = output_path / f"{'_'.join(cols)}__categorical_heatmap.png"
        try:
            plot_heatmap(pivot, file_path, title="Interactions catégorielles")
            output["plots"].append(
                {
                    "column": "+".join(cols),
                    "graph_type": "categorical_heatmap",
                    "file_path": str(file_path),
                }
            )
        except Exception as exc:  # pylint: disable=broad-except
            output["errors"].append(
                {
                    "column": "+".join(cols),
                    "graph_type": "categorical_heatmap",
                    "reason": str(exc),
                }
            )


def plot_barchart_from_counts(counts: pd.Series, output_path: Path) -> None:
    counts = counts.dropna().sort_values(ascending=False).head(20)
    if counts.empty:
        raise ValueError("Aucune donnée agrégée disponible pour le diagramme en barres.")

    fig, ax = _init_figure(figsize=(6, 4 + len(counts) * 0.2))
    colors = _repeat_colors(len(counts))
    ax.bar(counts.index.astype(str), counts.values, color=colors)
    ax.set_ylabel("Occurrences")
    ax.set_xlabel("Périodes")
    for label in ax.get_xticklabels():
        label.set_rotation(45)
        label.set_ha("right")
    ax.set_title("Répartition temporelle")
    _finalize_plot(fig, output_path)


def _aggregate_datetime_counts(series: pd.Series) -> pd.Series:
    dates = pd.to_datetime(series, errors="coerce").dropna()
    if dates.empty:
        return pd.Series(dtype="int")

    span = (dates.max() - dates.min()).days
    if span > 730:
        freq = "Y"
    elif span > 365:
        freq = "Q"
    elif span > 90:
        freq = "M"
    elif span > 30:
        freq = "W"
    else:
        freq = "D"

    counts = dates.dt.to_period(freq).value_counts().sort_index()
    timestamps = counts.index.to_timestamp()
    return pd.Series(counts.values, index=timestamps, name=series.name)


def _init_figure(figsize: Sequence[float] = (6, 4)):
    fig, ax = plt.subplots(figsize=figsize, dpi=120)
    fig.patch.set_facecolor("white")
    ax.set_facecolor("white")
    fig.tight_layout()
    return fig, ax


def _finalize_plot(fig, output_path: Path) -> None:
    fig.savefig(output_path, bbox_inches="tight")
    plt.close(fig)


def _repeat_colors(n: int) -> List[str]:
    colors = []
    for idx in range(n):
        colors.append(DEFAULT_COLORS[idx % len(DEFAULT_COLORS)])
    return colors


def generate_plots(df: pd.DataFrame, analysis: Dict[str, Any], output_dir: str) -> Dict[str, List[Dict[str, Any]]]:
    output = {"plots": [], "errors": []}
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    column_types = analysis.get("column_types", {})
    candidates = analysis.get("visualization_candidates", {})
    axis_column = analysis.get("axis_column")

    for column, graph_types in candidates.items():
        series = df.get(column)
        if series is None:
            output["errors"].append({"column": column, "reason": "colonne introuvable"})
            continue

        for graph_type in graph_types:
            output_file = output_path / f"{column}__{graph_type}.png"
            try:
                if graph_type == "linechart_with_axis" and axis_column and axis_column in df.columns:
                    plot_line_with_axis(df, column, axis_column, output_file)
                else:
                    _plot_single(series, column_types.get(column, ""), graph_type, output_file)
                output["plots"].append(
                    {"column": column, "graph_type": graph_type, "file_path": str(output_file)}
                )
            except Exception as exc:  # pylint: disable=broad-except
                output["errors"].append(
                    {"column": column, "graph_type": graph_type, "reason": str(exc)}
                )

    _handle_relations(df, analysis, output_path, output, axis_column)
    return output
