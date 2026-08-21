"""HTTP routes for the lockpicking challenge."""

import secrets
from pathlib import Path

from fastapi import APIRouter, Form, Header, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from .config import attempt_time_limit_ms, database_path, submission_password
from .db import add_submission, admin_submissions, delete_submission, leaderboard
from .models import AdminSubmission, Submission

router = APIRouter()
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def _host_error(request: Request, message: str, status_code: int):
    """Render form errors without exposing contact fields or database details."""

    return templates.TemplateResponse(
        request=request,
        name="host.html",
        context={
            "submitted": False,
            "error": message,
            "attempt_time_limit_ms": attempt_time_limit_ms(),
        },
        status_code=status_code,
    )


def _require_admin_password(password: str | None) -> None:
    expected_password = submission_password()
    if not secrets.compare_digest(password or "", expected_password):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid admin password",
        )


def _store_submission(payload: Submission):
    return add_submission(
        database_path(),
        name=payload.name,
        phone_number=payload.phone_number,
        telegram_handle=payload.telegram_handle,
        duration_ms=payload.duration_ms,
    )


def _form_duration(value: str) -> int:
    try:
        return int(value)
    except ValueError:
        return 0


@router.get("/", include_in_schema=False)
async def host_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="host.html",
        context={
            "submitted": request.query_params.get("submitted") == "1",
            "attempt_time_limit_ms": attempt_time_limit_ms(),
        },
    )


@router.get("/leaderboard", include_in_schema=False)
async def leaderboard_page(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="leaderboard.html",
        context={"entries": leaderboard(database_path())},
    )


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/api/admin/submissions", response_model=list[AdminSubmission])
async def get_admin_submissions(
    password: str | None = Header(default=None, alias="X-Submission-Password"),
) -> list[dict]:
    _require_admin_password(password)
    return admin_submissions(database_path())


@router.delete(
    "/api/admin/submissions/{submission_id}", status_code=status.HTTP_204_NO_CONTENT
)
async def delete_admin_submission(
    submission_id: int,
    password: str | None = Header(default=None, alias="X-Submission-Password"),
) -> None:
    _require_admin_password(password)
    if not delete_submission(database_path(), submission_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Submission not found",
        )


@router.post(
    "/submissions",
    include_in_schema=False,
    status_code=status.HTTP_303_SEE_OTHER,
)
async def create_form_submission(
    request: Request,
    password: str = Form(default=""),
    name: str = Form(default=""),
    phone_number: str = Form(default=""),
    telegram_handle: str = Form(default=""),
    duration_ms: str = Form(default=""),
):
    try:
        payload = Submission(
            password=password,
            name=name,
            phone_number=phone_number,
            telegram_handle=telegram_handle,
            duration_ms=_form_duration(duration_ms),
        )
    except ValidationError as error:
        message = (
            "Please provide a valid password, participant name, contact details, "
            "and positive duration."
        )
        for item in error.errors():
            if item["loc"] == ("duration_ms",):
                message = f"Invalid duration: {item['msg']}."
                break
        return _host_error(request, message, status.HTTP_422_UNPROCESSABLE_ENTITY)

    if not secrets.compare_digest(payload.password, submission_password()):
        return _host_error(
            request,
            "Invalid submission password.",
            status.HTTP_403_FORBIDDEN,
        )

    _store_submission(payload)
    return RedirectResponse(url="/?submitted=1", status_code=status.HTTP_303_SEE_OTHER)
