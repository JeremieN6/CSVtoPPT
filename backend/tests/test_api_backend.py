"""Test d'intégration API /generate-report (FastAPI TestClient)."""
from __future__ import annotations

import os
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

from fastapi.testclient import TestClient

from backend.main import app

TESTS_DIR = Path(__file__).resolve().parent
DATA_PATH = TESTS_DIR / "data" / "sample_sales.csv"
OUTPUT_DIR = TESTS_DIR / "output"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_FILE = OUTPUT_DIR / "test_api_report.pptx"


def main() -> None:
    client = TestClient(app)
    with DATA_PATH.open("rb") as file_obj:
        response = client.post(
            "/generate-report",
            files={"file": ("sample_sales.csv", file_obj, "text/csv")},
            data={
                "title": "Rapport API Module H",
                "theme": "corporate",
                "use_ai": "false",
                "api_key": "",
            },
        )

    if response.status_code != 200:
        raise RuntimeError(f"Appel API échoué: {response.status_code} - {response.text}")

    OUTPUT_FILE.write_bytes(response.content)
    warnings = response.headers.get("X-Report-Warnings")
    print(
        {
            "status": response.status_code,
            "ppt_path": str(OUTPUT_FILE),
            "warnings": warnings,
            "size_bytes": OUTPUT_FILE.stat().st_size,
        }
    )


if __name__ == "__main__":
    main()
