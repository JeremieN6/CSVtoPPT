"""Module B - Automatic dataset analysis.

This module consumes a pandas DataFrame plus the diagnostic summary emitted by
Module A and returns a structured description of column semantics, charting
opportunities, potential relations, and data issues.

Only pandas/numpy are used so the module can run in CLI tools or later inside a
Flask/FastAPI backend.
"""
from __future__ import annotations

import warnings
from itertools import combinations
from typing import Any, Dict, Iterable, List

import numpy as np
import pandas as pd

IDENTIFIER_UNIQUE_RATIO = 0.95
NUMERIC_DISCRETE_MAX_UNIQUE = 20
TEXT_CATEGORY_MAX_UNIQUE = 30
TEXT_CATEGORY_MAX_RATIO = 0.3
BOOLEAN_CANONICAL = {"0", "1", "true", "false", "oui", "non", "yes", "no"}
LONG_TEXT_AVG_THRESHOLD = 80
LONG_TEXT_MAX_THRESHOLD = 200
HIGH_MISSING_THRESHOLD = 40.0  # percent
CORRELATION_MIN_ABS = 0.5


def infer_column_type(series: pd.Series) -> str:
    """Classify a column into semantic buckets."""

    if series is None:
        return "constant"

    non_na = series.dropna()
    total_non_na = len(non_na)
    if total_non_na == 0:
        return "constant"

    unique_count = non_na.nunique(dropna=True)
    if unique_count <= 1:
        return "constant"

    unique_ratio = unique_count / max(total_non_na, 1)

    if _is_boolean_series(series):
        return "boolean"

    if _is_datetime_series(non_na):
        return "date"

    if _looks_identifier(series, unique_ratio):
        return "identifier"

    if _is_numeric_series(series):
        return (
            "numeric_discrete"
            if unique_count <= NUMERIC_DISCRETE_MAX_UNIQUE
            else "numeric_continuous"
        )

    if _is_categorical_text(series, unique_count, unique_ratio):
        return "categorical"

    return "text"


def detect_visualization_options(
    dataframe: pd.DataFrame, column_types: Dict[str, str]
) -> Dict[str, List[str]]:
    """List per-column chart types that make sense without generating them."""

    candidates: Dict[str, List[str]] = {}

    for column, col_type in column_types.items():
        options: List[str] = []
        if col_type == "numeric_continuous":
            options.extend(["histogram", "boxplot", "density"])
            if _has_time_index(dataframe.index):
                options.append("linechart")
        elif col_type == "numeric_discrete":
            options.append("barchart")
        elif col_type in {"categorical", "boolean"}:
            options.extend(["barchart", "top_categories"])
        elif col_type == "date":
            options.append("linechart")
        if options:
            candidates[column] = options
    return candidates


def detect_relations(
    dataframe: pd.DataFrame, column_types: Dict[str, str]
) -> Dict[str, List[Dict[str, Any]]]:
    """Infer interesting column pairs for later visualizations."""

    relations: Dict[str, List[Dict[str, Any]]] = {
        "correlations": [],
        "categorical_pairs": [],
    }

    numeric_cols = [col for col, typ in column_types.items() if typ.startswith("numeric")]
    if len(numeric_cols) >= 2:
        numeric_df = dataframe[numeric_cols].apply(pd.to_numeric, errors="coerce")
        corr_matrix = numeric_df.corr(method="pearson", min_periods=3)
        for col_a, col_b in combinations(numeric_cols, 2):
            corr_value = corr_matrix.loc[col_a, col_b]
            if pd.notna(corr_value) and abs(corr_value) >= CORRELATION_MIN_ABS:
                relations["correlations"].append(
                    {
                        "columns": [col_a, col_b],
                        "value": round(float(corr_value), 3),
                    }
                )

    categorical_cols = [
        col
        for col, typ in column_types.items()
        if typ in {"categorical", "boolean", "numeric_discrete"}
    ]
    if len(categorical_cols) >= 2:
        for col_a, col_b in combinations(categorical_cols, 2):
            if _is_pair_small(dataframe, col_a, col_b):
                relations["categorical_pairs"].append(
                    {"columns": [col_a, col_b], "suggestion": "heatmap"}
                )

    return relations


def detect_issues(
    dataframe: pd.DataFrame, column_types: Dict[str, str], diagnostic: Dict[str, Any]
) -> Dict[str, List[str]]:
    """Scan the dataset for common data-quality problems."""

    issues = {
        "empty_columns": [],
        "high_missing": [],
        "bad_format": [],
        "duplicated_columns": [],
        "long_text_columns": [],
    }

    diag_columns = (diagnostic or {}).get("columns", {})
    for column in dataframe.columns:
        series = dataframe[column]
        stripped = _strip_strings(series)
        if stripped.dropna().empty:
            issues["empty_columns"].append(column)
        stats = diag_columns.get(column, {})
        if stats.get("missing_percent", 0) >= HIGH_MISSING_THRESHOLD:
            issues["high_missing"].append(column)
        if _needs_format_fix(series):
            issues["bad_format"].append(column)
        if column_types.get(column) == "text" and _is_long_text(series):
            issues["long_text_columns"].append(column)

    duplicated = _find_duplicated_columns(dataframe)
    if duplicated:
        issues["duplicated_columns"].extend(duplicated)

    return issues


# ---------------------------- helper utilities ---------------------------- #

def _is_boolean_series(series: pd.Series) -> bool:
    if pd.api.types.is_bool_dtype(series):
        return True
    non_na = series.dropna()
    if non_na.empty:
        return False
    lower_values = {str(value).strip().lower() for value in non_na.unique()}
    return lower_values.issubset(BOOLEAN_CANONICAL)


def _is_datetime_series(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Could not infer format, so each element will be parsed individually",
            category=UserWarning,
        )
        converted = pd.to_datetime(series, errors="coerce")
    non_na_ratio = converted.notna().sum() / max(len(series), 1)
    return non_na_ratio >= 0.8


def _looks_identifier(series: pd.Series, unique_ratio: float) -> bool:
    if unique_ratio < IDENTIFIER_UNIQUE_RATIO:
        return False
    return pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)


def _is_numeric_series(series: pd.Series) -> bool:
    if pd.api.types.is_numeric_dtype(series):
        return True
    coerced = pd.to_numeric(series, errors="coerce")
    ratio = coerced.notna().sum() / max(len(series), 1)
    return ratio >= 0.9


def _is_categorical_text(series: pd.Series, unique_count: int, unique_ratio: float) -> bool:
    if pd.api.types.is_categorical_dtype(series):
        return True
    if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)):
        return False
    return unique_count <= TEXT_CATEGORY_MAX_UNIQUE or unique_ratio <= TEXT_CATEGORY_MAX_RATIO


def _has_time_index(index: pd.Index) -> bool:
    if isinstance(index, (pd.DatetimeIndex, pd.PeriodIndex)):
        return True
    try:
        with warnings.catch_warnings():
            warnings.filterwarnings(
                "ignore",
                message="Could not infer format, so each element will be parsed individually",
                category=UserWarning,
            )
            converted = pd.to_datetime(index, errors="coerce")
        non_na_ratio = converted.notna().sum() / max(len(index), 1)
        return non_na_ratio >= 0.8
    except Exception:  # pylint: disable=broad-except
        return False


def _is_pair_small(dataframe: pd.DataFrame, col_a: str, col_b: str) -> bool:
    unique_a = dataframe[col_a].nunique(dropna=True)
    unique_b = dataframe[col_b].nunique(dropna=True)
    return (unique_a <= TEXT_CATEGORY_MAX_UNIQUE) and (unique_b <= TEXT_CATEGORY_MAX_UNIQUE)


def _strip_strings(series: pd.Series) -> pd.Series:
    if pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series):
        return series.astype(str).str.strip().replace({"": np.nan})
    return series


def _needs_format_fix(series: pd.Series) -> bool:
    if not (pd.api.types.is_object_dtype(series) or pd.api.types.is_string_dtype(series)):
        return False
    non_na = series.dropna()
    if non_na.empty:
        return False
    numeric_ratio = pd.to_numeric(non_na, errors="coerce").notna().sum() / len(non_na)
    if numeric_ratio >= 0.9:
        return True
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Could not infer format, so each element will be parsed individually",
            category=UserWarning,
        )
        datetime_ratio = pd.to_datetime(non_na, errors="coerce").notna().sum() / len(non_na)
    if datetime_ratio >= 0.8:
        return True
    whitespace_ratio = _whitespace_ratio(non_na)
    return whitespace_ratio >= 0.3


def _whitespace_ratio(series: pd.Series) -> float:
    stringified = series.astype(str)
    total = len(stringified)
    if total == 0:
        return 0.0
    count = (stringified != stringified.str.strip()).sum()
    return count / total


def _is_long_text(series: pd.Series) -> bool:
    if not (pd.api.types.is_string_dtype(series) or pd.api.types.is_object_dtype(series)):
        return False
    non_na = series.dropna()
    if non_na.empty:
        return False
    lengths = non_na.astype(str).str.len()
    return (lengths.mean() >= LONG_TEXT_AVG_THRESHOLD) or (lengths.max() >= LONG_TEXT_MAX_THRESHOLD)


def _find_duplicated_columns(dataframe: pd.DataFrame) -> List[str]:
    duplicates: List[str] = []
    seen: Dict[str, pd.Series] = {}
    for column in dataframe.columns:
        series = dataframe[column]
        for prev_name, prev_series in seen.items():
            if series.equals(prev_series):
                duplicates.append(column)
                break
        else:
            seen[column] = series
    return duplicates

def analyze_dataset(df: pd.DataFrame, diagnostic: Dict[str, Any]) -> Dict[str, Any]:
    column_types = {column: infer_column_type(df[column]) for column in df.columns}

    return {
        "column_types": column_types,
        "visualization_candidates": detect_visualization_options(df, column_types),
        "relations": detect_relations(df, column_types),
        "issues": detect_issues(df, column_types, diagnostic),
    }
