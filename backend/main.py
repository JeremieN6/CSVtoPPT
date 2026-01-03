"""FastAPI application exposing the CSV -> PPT pipeline."""
from __future__ import annotations

import os
import traceback
from pathlib import Path
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from fastapi import BackgroundTasks, Depends, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from services.pipeline import PipelineError, pipeline_run, run_pipeline
from services import utils

from auth.router import router as auth_router
from billing import billing_router, billing_webhook_router
from auth.models import User
from auth.security import require_active_user
from auth.service import get_session
from modules.module_a_loader import load_and_parse_file
from modules.module_j_plan_limits import check_usage_limits


app = FastAPI(title="CSV to PPT API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Auth"])
app.include_router(billing_router)
app.include_router(billing_webhook_router)


# Load environment variables early so pipeline can see OPENAI_API_KEY even on /generate-report
BASE_DIR = Path(__file__).resolve().parents[1]
for env_name in (".env.local", ".env"):
    env_path = BASE_DIR / env_name
    if env_path.exists():
        load_dotenv(env_path, override=False)

_openai_env = os.getenv("OPENAI_API_KEY")
if _openai_env:
    print(f"[startup] OPENAI_API_KEY détectée (longueur={len(_openai_env)}, suffixe=***{_openai_env[-4:]})")
else:
    print("[startup] Aucune OPENAI_API_KEY trouvée dans l'environnement.")

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/generate-report")
async def generate_report(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form("Rapport - Présentation du jour"),
    theme: str = Form("corporate"),
    use_ai: bool = Form(True),
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


@app.post("/convert")
async def convert_dataset(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: str = Form("Rapport - Présentation du jour"),
    theme: str = Form("corporate"),
    use_ai: bool = Form(False),
    api_key: Optional[str] = Form(None),
    current_user: User = Depends(require_active_user),
    session: Session = Depends(get_session),
) -> FileResponse:
    if not file.filename:
        raise HTTPException(status_code=400, detail="Aucun fichier reçu.")
    if not utils.is_allowed_extension(file.filename):
        raise HTTPException(status_code=400, detail="Format non supporté. Fournissez un CSV ou XLSX.")

    upload_dir = utils.make_temp_dir("upload_")
    ppt_path: Optional[str] = None
    usage_snapshot = _snapshot_usage_state(current_user)

    try:
        saved_file = await utils.save_upload_file(file, upload_dir)
        utils.validate_file_size(saved_file)

        parsed = load_and_parse_file(str(saved_file))
        dataframe = parsed.get("dataframe")
        diagnostic = parsed.get("diagnostic", {})
        if dataframe is None:
            raise HTTPException(status_code=400, detail=diagnostic.get("error") or "Impossible de lire le fichier fourni.")

        enforcement = check_usage_limits(current_user, dataframe, requested_slide_count=None)
        if not enforcement.get("allowed"):
            raise HTTPException(status_code=403, detail=enforcement.get("error") or "Limite de plan atteinte.")

        pipeline_result = pipeline_run(
            df=dataframe,
            diagnostic=diagnostic,
            title=title,
            theme=theme,
            use_ai=use_ai,
            api_key=api_key,
            plan_params=enforcement.get("params"),
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

        session.add(current_user)
        session.commit()

        return response
    except HTTPException:
        session.rollback()
        _restore_usage_state(current_user, usage_snapshot)
        if ppt_path:
            utils.safe_delete_file(ppt_path)
        raise
    except ValueError as exc:
        session.rollback()
        _restore_usage_state(current_user, usage_snapshot)
        if ppt_path:
            utils.safe_delete_file(ppt_path)
        raise HTTPException(status_code=400, detail=str(exc))
    except PipelineError as exc:
        session.rollback()
        _restore_usage_state(current_user, usage_snapshot)
        if ppt_path:
            utils.safe_delete_file(ppt_path)
        raise HTTPException(status_code=400, detail=str(exc))
    except Exception as exc:  # pragma: no cover
        session.rollback()
        _restore_usage_state(current_user, usage_snapshot)
        if ppt_path:
            utils.safe_delete_file(ppt_path)
        print(f"ERROR in convert_dataset: {exc}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Erreur interne: {str(exc)}") from exc
    finally:
        utils.cleanup_path(upload_dir)


def _snapshot_usage_state(user: User) -> Dict[str, Any]:
    return {
        "conversions_this_month": getattr(user, "conversions_this_month", 0),
        "conversions_last_month": getattr(user, "conversions_last_month", 0),
        "last_reset_date": getattr(user, "last_reset_date", None),
    }


def _restore_usage_state(user: User, snapshot: Dict[str, Any]) -> None:
    for field, value in snapshot.items():
        setattr(user, field, value)
