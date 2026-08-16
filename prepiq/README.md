# PrepIQ

An AI-powered interview prep platform. Full-stack project: FastAPI backend,
MySQL + MongoDB databases, vanilla JS frontend, custom DSA implementations,
and a working ML pipeline — built phase by phase, all in this one codebase.

## Project structure by phase

| Phase | What it is | Where |
|---|---|---|
| 0 | Architecture decisions (MySQL vs MongoDB split) | see below |
| 1 | Backend skeleton, DB connections, health check | `app/main.py`, `app/core/config.py`, `app/db/` |
| 2 | Auth (JWT, bcrypt) | `app/core/security.py`, `app/api/auth.py`, `app/api/deps.py` |
| 3 | Question bank + code execution + submissions | `app/api/questions.py`, `app/services/code_executor.py` |
| 4 | DSA features: Trie, Heap, Graph | `app/dsa/`, `app/api/dsa_routes.py` |
| 5 | ML: skill extraction, difficulty model, recommender | `app/ml/`, `app/api/resume.py` |
| 6 | Contests & timers | `app/models/contest.py`, `app/api/contests.py` |
| 7 | Frontend (vanilla JS) | `frontend/` |
| 8 | Tests + Docker deployment | `tests/`, `Dockerfile`, `docker-compose.yml` |

## Architecture: why two databases

- **MySQL** — users, submissions, contests, topic progress. Relational,
  needs integrity (foreign keys, ACID) — a submission must belong to a real user.
- **MongoDB** — questions, resumes, code snapshots. Flexible schema — a question's
  test cases and tags don't fit neatly into fixed columns, and this data is
  read far more than it's transactionally updated.

## Run everything with one command

```bash
cp .env.example .env
docker compose up --build
```

This starts **four containers**: `api` (FastAPI), `mysql`, `mongo`, and
`frontend` (nginx serving the static files).

Once you see "Application startup complete" in the logs, seed sample data
(second terminal):

```bash
docker compose exec api python -m app.seed
```

Then open:
- **http://localhost:5500** — the actual app (register, solve questions, see leaderboard)
- **http://localhost:8000/docs** — Swagger API explorer
- **http://localhost:8000/health** — confirms MySQL + MongoDB are connected

Seeded login: `admin@prepiq.dev` / `admin123` (admin — can create questions/contests)

## Running tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

11 tests covering the Trie, Heap, topic Graph, and code executor's four
verdict paths (Accepted / Wrong Answer / Error / Timeout).

## Full endpoint list

```
POST   /auth/register
POST   /auth/login
POST   /auth/refresh
GET    /auth/me

GET    /questions
GET    /questions/{id}
POST   /questions            (admin)
POST   /questions/submit

GET    /search/autocomplete
GET    /leaderboard
GET    /topics/order
GET    /topics/next-unlocked

POST   /resume/upload
GET    /recommend/next-question

POST   /contests             (admin)
GET    /contests
GET    /contests/{id}
POST   /contests/{id}/join
GET    /contests/{id}/leaderboard

GET    /health
```

## Known limitations (documented in-code, intentional for a learning project)

- **Code execution** (`app/services/code_executor.py`) runs Python via subprocess
  on the host — fine for local dev, not a security sandbox. Upgrade path: Judge0.
- **Skill extraction** (`app/ml/skill_extractor.py`) is keyword-matching, not a
  trained NER model — zero extra downloads needed. Upgrade path: spaCy NER.
- **Difficulty model** (`app/ml/difficulty_model.py`) is a real trained
  scikit-learn classifier, but trained on synthetic data. Upgrade path: retrain
  on real `submissions` data periodically.
- **Redis** was intentionally left out — leaderboard computes on read instead
  of being cached. Add it back if you want that optimization later.

## Alternative: running via a Python venv (no Docker for the app itself)

Useful if you want VS Code debugging on the FastAPI app while still using
Docker just for the databases:

```bash
# start only the databases
docker compose up mysql mongo

# in a separate terminal, with your venv activated:
pip install -r requirements.txt
# edit .env: set MYSQL_HOST=localhost and MONGO_URI=mongodb://localhost:27017
uvicorn app.main:app --reload
python -m app.seed
```

Then open the `frontend/index.html` file directly, or serve it with
`python -m http.server 5500` from inside the `frontend/` folder.
