from sqlalchemy import Column, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.db.mysql import Base


class UserTopicProgress(Base):
    __tablename__ = "user_topic_progress"
    __table_args__ = (UniqueConstraint("user_id", "topic", name="uq_user_topic"),)

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    topic = Column(String(100), nullable=False)
    attempts = Column(Integer, default=0, nullable=False)
    solved = Column(Integer, default=0, nullable=False)

    @property
    def mastery_score(self) -> float:
        # simple accuracy-based mastery; swap for something fancier later if you want
        return round(self.solved / self.attempts, 2) if self.attempts else 0.0
