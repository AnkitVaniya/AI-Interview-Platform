from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.sql import func

from app.db.mysql import Base


class Submission(Base):
    __tablename__ = "submissions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    question_id = Column(String(24), nullable=False, index=True)  # Mongo ObjectId as string
    topic = Column(String(100), nullable=True, index=True)  # denormalized for fast weak-topic stats
    verdict = Column(String(30), nullable=False)  # "Accepted" | "Wrong Answer" | "Error" | "Timeout"
    runtime_ms = Column(Float, nullable=True)
    code_snapshot_id = Column(String(24), nullable=True)  # pointer to Mongo code_snapshots doc
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=True, index=True)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
