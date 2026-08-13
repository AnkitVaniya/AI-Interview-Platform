from sqlalchemy.orm import Session

from app.models.topic_progress import UserTopicProgress


def record_attempt(db: Session, user_id: int, topic: str, solved: bool) -> None:
    """Upserts the user's attempt/solved counters for a topic. Call this after every submission."""
    progress = (
        db.query(UserTopicProgress)
        .filter(UserTopicProgress.user_id == user_id, UserTopicProgress.topic == topic)
        .first()
    )
    if progress is None:
        progress = UserTopicProgress(user_id=user_id, topic=topic, attempts=0, solved=0)
        db.add(progress)

    progress.attempts += 1
    if solved:
        progress.solved += 1
    db.commit()


def get_weak_topics(db: Session, user_id: int, threshold: float = 0.5) -> list[dict]:
    """Returns topics where the user's mastery score is below threshold, weakest first."""
    rows = db.query(UserTopicProgress).filter(UserTopicProgress.user_id == user_id).all()
    weak = [
        {"topic": r.topic, "mastery_score": r.mastery_score, "attempts": r.attempts}
        for r in rows
        if r.mastery_score < threshold
    ]
    return sorted(weak, key=lambda x: x["mastery_score"])
