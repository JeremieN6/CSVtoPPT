"""FastAPI application exposing the CSV -> PPT pipeline."""
from __future__ import annotations

import traceback
from pathlib import Path
from typing import Optional

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from backend.services.pipeline import PipelineError, run_pipeline
from backend.services import utils

app = FastAPI(title="CSV to PPT API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/generate-report")
async def generate_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form("Rapport automatique"),
    theme: str = Form("corporate"),
    use_ai: bool = Form(False),
    api_key: Optional[str] = Form(None),
) -> FileResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Aucun fichier reçu.")
    if not utils.is_allowed_extension(file.filename):
        raise HTTPException(status_code=400, detail="Format non supporté. Fournissez un CSV ou XLSX.")

    upload_dir = utils.make_temp_dir("upload_")
    ppt_path: Optional[str] = None

    try:
        saved_file = await utils.save_upload_file(file, upload_dir)
        utils.validate_file_size(saved_file)

        pipeline_result = run_pipeline(
            saved_file,
            title=title,
            theme=theme,
            use_ai=use_ai,
            api_key=api_key,
        )
        ppt_path = pipeline_result["pptx_path"]
        warnings = pipeline_result.get("warnings") or []

        filename = f"{utils.slugify(title)}.pptx"
        response = FileResponse(
            ppt_path,
            filename=filename,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
        )
        if warnings:
            response.headers["X-Report-Warnings"] = " | ".join(warnings[:5])

        background_tasks.add_task(utils.safe_delete_file, ppt_path)
        return response
    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except PipelineError as exc:
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:
        print(f"ERROR in generate_report: {exc}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(exc)}") from exc
    finally:
        utils.cleanup_path(upload_dir)
