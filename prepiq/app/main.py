from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, auth, questions, dsa_routes, resume, contests
from app.db.mysql import Base, engine
# noqa: F401 — imported so SQLAlchemy registers every model before create_all() runs
from app.models import user, submission, topic_progress, contest  # noqa: F401

app = FastAPI(title="PrepIQ API", version="0.1.0")

# Allow the vanilla-JS frontend (served from a different port/origin during dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this to your actual frontend origin before deploying
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(auth.router)
app.include_router(questions.router)
app.include_router(dsa_routes.router)
app.include_router(resume.router)
app.include_router(contests.router)


@app.on_event("startup")
def create_tables():
    # In real projects use Alembic migrations instead of this — fine for early dev
    Base.metadata.create_all(bind=engine)


@app.get("/")
def root():
    return {"message": "PrepIQ API is running"}
