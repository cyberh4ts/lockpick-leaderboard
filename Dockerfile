FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.12 /uv /uvx /bin/

WORKDIR /app

COPY pyproject.toml uv.lock ./
COPY app ./app
RUN uv sync --locked --no-dev

EXPOSE 3000
CMD ["uv", "run", "--no-sync", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
