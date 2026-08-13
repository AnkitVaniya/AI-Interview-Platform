from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.mongo import resumes_collection
from app.db.mysql import get_db
from app.ml.skill_extractor import extract_skills, extract_known_topics
from app.ml.recommender import recommend_next_question
from app.models.user import User

router = APIRouter(tags=["ml-features"])


@router.post("/resume/upload")
async def upload_resume(file: UploadFile = File(...), current_user: User = Depends(get_current_user)):
    # NOTE: for a v1, expects .txt resumes (or already-extracted plain text).
    # For PDF/DOCX resumes, run them through the `pdf`/`docx` extraction skill first,
    # then POST the resulting text here — keeps this endpoint format-agnostic.
    raw_bytes = await file.read()
    text = raw_bytes.decode("utf-8", errors="ignore")

    skills = extract_skills(text)
    topics = extract_known_topics(text)

    await resumes_collection.update_one(
        {"user_id": current_user.id},
        {"$set": {"user_id": current_user.id, "raw_text": text, "extracted_skills": skills, "matched_topics": topics}},
        upsert=True,
    )

    return {"extracted_skills": skills, "matched_topics": topics}


@router.get("/recommend/next-question")
async def next_question(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await recommend_next_question(db, current_user.id)
