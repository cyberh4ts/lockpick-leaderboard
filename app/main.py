"""FastAPI application for the lockpicking challenge."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import attempt_time_limit_seconds, database_path, submission_password
from .db import initialize
from .routes import router


@asynccontextmanager
async def lifespan(_: FastAPI):
    submission_password()
    attempt_time_limit_seconds()
    initialize(database_path())
    yield


app = FastAPI(title="Lockpick Leaderboard", lifespan=lifespan)
app.mount(
    "/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static"
)
app.include_router(router)
