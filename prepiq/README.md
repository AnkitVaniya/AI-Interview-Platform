# PrepIQ Backend

FastAPI + MySQL + MongoDB backend for an AI-powered interview prep platform.
This is the **complete project through Phase 6** — phases were built incrementally
in the same codebase, not as separate folders, since each phase extends the last.

## What's included, by phase

| Phase | Files |
|---|---|
| 1 — Skeleton | `app/main.py`, `app/core/config.py`, `app/db/mysql.py`, `app/db/mongo.py`, `app/models/user.py`, `app/api/health.py` |
| 2 — Auth | `app/core/security.py`, `app/api/deps.py`, `app/api/auth.py`, `app/schemas/user.py` |
| 3 — Questions & execution | `app/models/submission.py`, `app/models/topic_progress.py`, `app/schemas/question.py`, `app/services/code_executor.py`, `app/services/progress_service.py`, `app/api/questions.py` |
| 4 — DSA features | `app/dsa/trie.py`, `app/dsa/heap.py`, `app/dsa/graph.py`, `app/api/dsa_routes.py` |
| 5 — ML | `app/ml/skill_extractor.py`, `app/ml/difficulty_model.py`, `app/ml/recommender.py`, `app/api/resume.py` |
| 6 — Contests | `app/models/contest.py`, `app/schemas/contest.py`, `app/api/contests.py` |

Redis was intentionally left out (see earlier conversation) — the leaderboard is
computed on read instead of cached. Add it back later if you want that optimization.

## Quick start (Docker)

```bash
cp .env.example .env
docker compose up --build
```

Once you see "Application startup complete" in the logs, in a second terminal:

```bash
docker compose exec api python -m app.seed
```

This creates an admin user (`admin@prepiq.dev` / `admin123`) and 3 sample questions.

Then open:
- http://localhost:8000/docs — interactive API explorer (Swagger UI)
- http://localhost:8000/health — confirms MySQL + MongoDB are connected

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

## Known limitations (by design, documented in-code)

- **Code execution** (`app/services/code_executor.py`) runs submitted Python via
  subprocess on the host — fine for local dev/demo, not a security sandbox.
  Upgrade path: Judge0 (self-hosted or API).
- **Skill extraction** (`app/ml/skill_extractor.py`) uses keyword matching, not a
  trained NER model — kept dependency-light so it runs with zero extra downloads.
  Upgrade path: spaCy NER fine-tuned on resumes.
- **Difficulty prediction** (`app/ml/difficulty_model.py`) is a real trained
  scikit-learn `LogisticRegression`, but trained on synthetic data at startup.
  Upgrade path: retrain periodically on real `submissions` + `user_topic_progress` data.

## What's next

**Phase 7** — vanilla JS frontend (not yet built): login/register forms, question
list + code editor (CodeMirror/Monaco), leaderboard view, resume upload UI,
contest timer.
