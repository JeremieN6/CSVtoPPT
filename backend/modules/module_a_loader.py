"""Module A - Lecture & Parsing CSV/XLSX.

This module exposes a single public function `load_and_parse_file` that takes a
path to a CSV or XLSX file, attempts to read it in a tolerant way, and returns a
structured dictionary with both the pandas DataFrame and a diagnostic summary.

The function never raises unhandled exceptions: failures are surfaced through an
`error` field within the diagnostic payload so the caller can decide how to
react without crashing the broader application.
"""
from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import pandas as pd

SUPPORTED_ENCODINGS = ("utf-8", "latin-1", "cp1252")
SUPPORTED_CSV_EXTENSIONS = {".csv", ".tsv", ".txt"}
SUPPORTED_EXCEL_EXTENSIONS = {".xlsx", ".xls"}


@dataclass
class DataFramePayload:
    """Internal helper to keep track of metadata alongside the DataFrame."""

    dataframe: pd.DataFrame
    metadata: Dict[str, Any]


def load_and_parse_file(file_path: str) -> Dict[str, Any]:
    """Load a CSV/XLSX file and return a dict with the DataFrame and diagnostic.

    Args:
        file_path: Absolute or relative path to the file provided by the user.

    Returns:
        A dictionary with two keys:
            - "dataframe": the pandas DataFrame (or None when an error occurs)
            - "diagnostic": metadata about the dataset or the error details
    """

    path = Path(file_path)
    try:
        _validate_path(path)
        payload = _load_dataframe(path)
        diagnostic = _build_diagnostic(payload.dataframe)
        diagnostic.update(payload.metadata)
        return {
            "dataframe": payload.dataframe,
            "diagnostic": diagnostic,
        }
    except Exception as exc:  # pylint: disable=broad-except
        return {
            "dataframe": None,
            "diagnostic": {"error": str(exc)},
        }


def _validate_path(path: Path) -> None:
    if not path:
        raise ValueError("Le chemin fourni est vide.")
    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")
    if not path.is_file():
        raise ValueError(f"Le chemin n'est pas un fichier valide : {path}")


def _load_dataframe(path: Path) -> DataFramePayload:
    suffix = path.suffix.lower()
    if suffix in SUPPORTED_CSV_EXTENSIONS:
        return _load_csv(path)
    if suffix in SUPPORTED_EXCEL_EXTENSIONS:
        return _load_excel(path)
    raise ValueError(
        "Format non supporté. Fournissez un fichier CSV ou XLSX (première feuille utilisée)."
    )


def _load_csv(path: Path) -> DataFramePayload:
    errors = []
    for encoding in SUPPORTED_ENCODINGS:
        try:
            dataframe = pd.read_csv(
                path,
                encoding=encoding,
                sep=None,  # auto-detect among common separators via csv.Sniffer
                engine="python",
                on_bad_lines="skip",
            )
            _ensure_dataframe_is_usable(dataframe)
            return DataFramePayload(
                dataframe=dataframe,
                metadata={
                    "source_format": "csv",
                    "encoding_used": encoding,
                },
            )
        except UnicodeDecodeError as err:
            errors.append(f"{encoding}: {err}")
        except pd.errors.ParserError as err:  # type: ignore[attr-defined]
            errors.append(f"{encoding}: {err}")
        except pd.errors.EmptyDataError:
            raise ValueError("Le fichier CSV est vide.") from None
    raise ValueError(
        "Impossible de lire le fichier CSV avec les encodages supportés.\n" + "\n".join(errors)
    )


def _load_excel(path: Path) -> DataFramePayload:
    try:
        excel_file = pd.ExcelFile(path)
    except ImportError as err:
        raise ImportError(
            "La lecture des fichiers XLSX nécessite la dépendance 'openpyxl'."
        ) from err

    try:
        first_sheet = excel_file.sheet_names[0]
    except IndexError as err:
        raise ValueError("Le classeur Excel ne contient aucune feuille.") from err

    dataframe = pd.read_excel(excel_file, sheet_name=first_sheet)
    _ensure_dataframe_is_usable(dataframe)
    return DataFramePayload(
        dataframe=dataframe,
        metadata={
            "source_format": "xlsx",
            "sheet_name": first_sheet,
        },
    )


def _ensure_dataframe_is_usable(dataframe: pd.DataFrame) -> None:
    if dataframe is None or dataframe.empty:
        raise ValueError("Aucune donnée exploitable n'a été trouvée dans le fichier.")
    dataframe.columns = dataframe.columns.astype(str).str.strip()


def _build_diagnostic(dataframe: pd.DataFrame) -> Dict[str, Any]:
    num_rows, num_cols = dataframe.shape
    columns_info = {}
    for column in dataframe.columns:
        series = dataframe[column]
        missing = int(series.isna().sum())
        missing_percent = _safe_percentage(missing, num_rows)
        columns_info[column] = {
            "dtype": _infer_semantic_dtype(series),
            "missing": missing,
            "missing_percent": missing_percent,
            "unique_values": int(series.nunique(dropna=True)),
        }
    return {
        "num_rows": num_rows,
        "num_cols": num_cols,
        "columns": columns_info,
    }


def _safe_percentage(value: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round((value / total) * 100, 2)


def _infer_semantic_dtype(series: pd.Series) -> str:
    non_na = series.dropna()
    if non_na.empty:
        return "texte"

    if _looks_numeric(series):
        return "numerique"
    if _looks_datetime(series):
        return "date"

    unique_ratio = non_na.nunique() / max(len(series), 1)
    if unique_ratio <= 0.05 or non_na.nunique() <= 20:
        return "categorie"
    return "texte"


def _looks_numeric(series: pd.Series) -> bool:
    if pd.api.types.is_numeric_dtype(series):
        return True
    coerced = pd.to_numeric(series, errors="coerce")
    non_na_ratio = coerced.notna().sum() / max(len(series), 1)
    return non_na_ratio >= 0.9


def _looks_datetime(series: pd.Series) -> bool:
    if pd.api.types.is_datetime64_any_dtype(series):
        return True
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="Could not infer format, so each element will be parsed individually",
            category=UserWarning,
        )
        coerced = pd.to_datetime(series, errors="coerce")
    non_na_ratio = coerced.notna().sum() / max(len(series), 1)
    return non_na_ratio >= 0.85


__all__ = ["load_and_parse_file"]
