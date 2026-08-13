from bson import ObjectId
from bson.errors import InvalidId
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.mongo import questions_collection, code_snapshots_collection
from app.db.mysql import get_db
from app.models.user import User
from app.models.submission import Submission
from app.schemas.question import (
    QuestionCreate,
    QuestionOut,
    QuestionAdminOut,
    SubmitCode,
    SubmissionResult,
)
from app.services.code_executor import evaluate_submission
from app.services.progress_service import record_attempt

router = APIRouter(prefix="/questions", tags=["questions"])


def _doc_to_out(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    return doc


@router.post("", response_model=QuestionAdminOut, status_code=201)
async def create_question(payload: QuestionCreate, _: User = Depends(require_admin)):
    doc = payload.model_dump()
    result = await questions_collection.insert_one(doc)
    doc["_id"] = result.inserted_id
    return _doc_to_out(doc)


@router.get("", response_model=list[QuestionOut])
async def list_questions(topic: str | None = None, difficulty: str | None = None):
    query = {}
    if topic:
        query["topic"] = topic
    if difficulty:
        query["difficulty"] = difficulty

    cursor = questions_collection.find(query, {"test_cases": 0})
    return [_doc_to_out(doc) async for doc in cursor]


@router.get("/{question_id}", response_model=QuestionOut)
async def get_question(question_id: str):
    try:
        oid = ObjectId(question_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid question id")

    doc = await questions_collection.find_one({"_id": oid}, {"test_cases": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Question not found")
    return _doc_to_out(doc)


@router.post("/submit", response_model=SubmissionResult)
async def submit_code(
    payload: SubmitCode,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        oid = ObjectId(payload.question_id)
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid question id")

    question = await questions_collection.find_one({"_id": oid})
    if not question:
        raise HTTPException(status_code=404, detail="Question not found")

    result = evaluate_submission(payload.code, question["test_cases"])

    # store the code snapshot in Mongo (feeds the ML pattern-analysis piece later)
    snapshot = await code_snapshots_collection.insert_one(
        {
            "user_id": current_user.id,
            "question_id": payload.question_id,
            "code": payload.code,
            "verdict": result["verdict"],
        }
    )

    submission = Submission(
        user_id=current_user.id,
        question_id=payload.question_id,
        topic=question["topic"],
        verdict=result["verdict"],
        runtime_ms=result["runtime_ms"],
        code_snapshot_id=str(snapshot.inserted_id),
        contest_id=payload.contest_id,
    )
    db.add(submission)
    db.commit()

    record_attempt(db, current_user.id, question["topic"], solved=(result["verdict"] == "Accepted"))

    return SubmissionResult(**result)
