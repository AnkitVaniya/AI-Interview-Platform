from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float, UniqueConstraint
from sqlalchemy.sql import func

from app.db.mysql import Base


class Contest(Base):
    __tablename__ = "contests"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    question_ids = Column(String(500), nullable=False)  # comma-separated Mongo ObjectIds
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class ContestParticipant(Base):
    __tablename__ = "contest_participants"
    __table_args__ = (UniqueConstraint("user_id", "contest_id", name="uq_user_contest"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    contest_id = Column(Integer, ForeignKey("contests.id"), nullable=False, index=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
