# Lockpick Leaderboard

Simple FastAPI webapp for recording lockpicking challenge times.

## Docker Compose

Copy the example configuration and set a private password:

```sh
cp .env.example .env
docker compose up --build -d
```

## Run directly with uv

Install [uv](https://docs.astral.sh/uv/) and export the required settings before running:

```sh
uv sync
export SUBMISSION_PASSWORD='change-me'
export ATTEMPT_TIME_LIMIT_SECONDS=60
export DATABASE_PATH='./data/leaderboard.sqlite'
uv run uvicorn app.main:app --host 127.0.0.1 --port 3000
```

## Admin API

Admin requests use the configured `SUBMISSION_PASSWORD` in the `X-Submission-Password` header.
The delete endpoint returns `204` when the submission exists and `404` otherwise. Missing or invalid password returns `403`.

```sh
curl http://localhost:3000/api/admin/submissions \
  -H 'X-Submission-Password: change-me'
curl -X DELETE http://localhost:3000/api/admin/submissions/1 \
  -H 'X-Submission-Password: change-me'
```
