"""Pydantic models used by the application."""

from pydantic import BaseModel, Field, StrictInt, field_validator

from .config import attempt_time_limit_ms


class Submission(BaseModel):
    password: str = Field(min_length=1, max_length=256)
    name: str = Field(min_length=1, max_length=200)
    phone_number: str = Field(min_length=1, max_length=100)
    telegram_handle: str = Field(min_length=1, max_length=100)
    duration_ms: StrictInt = Field(gt=0)

    @field_validator("password")
    @classmethod
    def password_must_not_be_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("must not be blank")
        return value

    @field_validator("name", "phone_number", "telegram_handle")
    @classmethod
    def non_whitespace(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("must not be blank")
        return value

    @field_validator("duration_ms")
    @classmethod
    def duration_must_be_within_attempt_limit(cls, value: int) -> int:
        limit_ms = attempt_time_limit_ms()
        if value > limit_ms:
            raise ValueError(
                f"must not exceed the attempt time limit of {limit_ms} milliseconds"
            )
        return value


class AdminSubmission(BaseModel):
    id: int
    name: str
    phone_number: str
    telegram_handle: str
    duration_ms: int
    created_at: str
