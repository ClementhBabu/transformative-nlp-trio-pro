# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository layout

The actual code lives one directory down, in `Transformative_NLP_Trio_Pro/` (underscores, not the
hyphenated repo name). Inside it are `backend/` (FastAPI + SQLAlchemy) and `frontend/`
(Create React App). The README's project tree and some of its tech claims are aspirational —
trust the code over the README where they disagree (see "README drift" below).

## Commands

### Backend (run from `Transformative_NLP_Trio_Pro/backend/`)

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload          # serves on http://localhost:8000
```

- Interactive API docs at `http://localhost:8000/docs` (Swagger) — use this to explore the live
  route surface, which is large (14 routers).
- There is **no test suite** and **no linter config** on the backend. `alembic` is in
  requirements but there are no migrations — schema is created at startup (see below).

### Frontend (run from `Transformative_NLP_Trio_Pro/frontend/`)

```bash
npm install
npm start        # CRA dev server on http://localhost:3000 (NOT `npm run dev`)
npm run build    # production build
npm test         # react-scripts (Jest) — no tests are currently written
```

## Architecture

### Request flow

`Frontend (axios) → FastAPI router → service module → (DB and/or ML model) → response`

- **Routers** (`app/routes/*.py`) are thin: validate input, call a service, translate exceptions
  into `HTTPException`. Every router mounts under an `/api/<feature>` prefix and is registered in
  `app/routes/__init__.py` and included in `app/main.py`. To add a feature, create
  `routes/<x>.py` + `services/<x>_service.py`, export the router from `routes/__init__.py`, and
  `include_router` it in `main.py`.
- **Services** (`app/services/*.py`) hold all business logic and own every ML model call.

### The pipeline is the core abstraction

`services/pipeline_service.py` orchestrates the full chain in one call (STT → summarize →
translate → sentiment → keywords → meeting minutes → TTS → save history → optional PDF report).
Each step after STT/summarize is wrapped in its own try/except and logs a warning on failure
rather than aborting — a partial result is still returned and persisted. The individual feature
routes (`/api/summarize`, `/api/translate`, etc.) reuse these same service functions standalone.

### ML models load lazily and degrade gracefully

Every ML-backed service imports its heavy dependency (`whisper`, `transformers`, `nltk`) **inside
the function**, not at module top level. Each has an `except ImportError` branch that returns a
**placeholder/stub result** so the API stays functional without the models installed. When
editing these services, preserve this pattern — do not hoist imports to module scope. Models are
also re-instantiated per call (e.g. `whisper.load_model(...)`, `pipeline("summarization", ...)`),
so first requests are slow and there is no model caching.

Note `speech_service.py` and `detect_language` disable SSL verification globally
(`ssl._create_default_https_context = ssl._create_unverified_context`) to work around model
download cert issues — this is intentional in this codebase.

### Persistence

- `database/database.py` uses `NullPool` (no connection pooling) and **creates all tables at app
  startup** via `init_db()` in the FastAPI lifespan handler. There are no migrations — model
  changes in `database/models.py` take effect by recreating tables, so altering existing columns
  requires manual DB intervention.
- Models: `User`, `ProcessingHistory` (the main artifact — stores recognized/summary/translated
  text plus `sentiment`/`keywords`/`meeting_minutes` as JSON columns), `AnalyticsLog`,
  `PasswordResetToken`. All PKs are UUIDs; deletes cascade from `User`.
- In-memory dicts (`_pipeline_store`, `_task_store`) track async task/pipeline status. These are
  process-local and lost on restart — not suitable for multi-worker deployment.

### Auth

JWT bearer tokens via `python-jose` + `passlib[bcrypt]`. `utils/auth.py` provides
`get_current_user` (the FastAPI dependency guarding protected routes), `hash_password`,
`create_access_token`, etc. The `sub` claim holds the user UUID. Frontend stores the token in
`localStorage` and an axios interceptor (`frontend/src/services/api.js`) attaches it and redirects
to `/login` on any 401.

### Configuration

`app/config.py` reads everything from env vars / `.env` (in `backend/`) via pydantic-settings.
Key vars: `DATABASE_URL`, `SECRET_KEY`, `WHISPER_MODEL` (default `base`), `SUMMARIZATION_MODEL`,
`TTS_ENGINE`, `OPENAI_API_KEY`, `GEMINI_API_KEY`. The upload/audio/reports directories are derived
paths and auto-created at import time. Frontend API base URL comes from `REACT_APP_API_URL`
(default `http://localhost:8000`).

### Frontend

CRA + React Router + **MUI (Material UI)** + Emotion (not Bootstrap; `npm start`, not Vite). All
server calls go through the typed API objects in `src/services/api.js` (`authAPI`, `speechAPI`,
`pipelineAPI`, …) — add new endpoints there rather than calling axios directly from components.
Routes are split into public pages and `ProtectedRoute`-wrapped pages in `src/App.jsx`. Auth state
lives in the `useAuth` hook.

## API contract conventions

- **Every text-input POST endpoint takes a JSON body backed by a Pydantic request schema** (in
  `app/schemas/processing.py`). Do not accept body data as bare `str`/`int` parameters — FastAPI
  would treat those as query/form params, which silently breaks the frontend. Add a `*Request`
  schema and type the route parameter with it, matching the existing pattern.
- `frontend/src/services/api.js` is the single source of truth for endpoint paths/payloads on the
  client. When you add or change a backend route, update the matching wrapper here so the two
  stay in sync. `/docs` (Swagger) is the authoritative live reference for the route surface.
- Routes whose path is `"/"` are served at the trailing-slash URL (e.g. `/api/summarize/`); the
  frontend wrappers call those exact paths to avoid 307 redirects.
