"""
Next-question recommender. Combines three signals:
1. Weak topics (from real submission stats)
2. Topic graph (don't recommend a locked topic)
3. Difficulty model (don't recommend something too hard/easy for current skill)

This is intentionally rule-based on top of one real ML model (difficulty
prediction) rather than a full collaborative-filtering system — a good
upgrade path once you have enough users generating interaction data.
"""
from sqlalchemy.orm import Session

from app.db.mongo import questions_collection
from app.dsa.graph import topic_graph
from app.ml.difficulty_model import difficulty_predictor
from app.models.submission import Submission
from app.models.topic_progress import UserTopicProgress
from app.services.progress_service import get_weak_topics


def _user_overall_stats(db: Session, user_id: int) -> tuple[float, float]:
    rows = db.query(Submission).filter(Submission.user_id == user_id).all()
    if not rows:
        return 0.3, 5.0  # cold-start default: assume beginner

    total = len(rows)
    accepted = sum(1 for r in rows if r.verdict == "Accepted")
    accuracy = accepted / total

    # attempts-per-solve: total submissions divided by distinct solved questions
    solved_questions = {r.question_id for r in rows if r.verdict == "Accepted"}
    avg_attempts = total / len(solved_questions) if solved_questions else float(total)

    return accuracy, avg_attempts


async def recommend_next_question(db: Session, user_id: int) -> dict:
    accuracy, avg_attempts = _user_overall_stats(db, user_id)
    difficulty_pred = difficulty_predictor.predict(accuracy, avg_attempts)
    target_difficulty = difficulty_pred["recommended_difficulty"]

    weak_topics = get_weak_topics(db, user_id)
    mastered_rows = db.query(UserTopicProgress).filter(UserTopicProgress.user_id == user_id).all()
    mastered = {r.topic for r in mastered_rows if r.mastery_score >= 0.7}
    unlocked = set(topic_graph.unlocked_topics(mastered))

    # priority 1: a weak topic that's actually unlocked (don't push something locked)
    candidate_topics = [t["topic"] for t in weak_topics if t["topic"] in unlocked]
    if not candidate_topics:
        # priority 2: any unlocked topic not yet mastered
        candidate_topics = sorted(unlocked) or ["Arrays"]  # "Arrays" as an absolute fallback start

    for topic in candidate_topics:
        question = await questions_collection.find_one(
            {"topic": topic, "difficulty": target_difficulty}, {"test_cases": 0}
        )
        if question:
            question["id"] = str(question.pop("_id"))
            return {
                "question": question,
                "reasoning": {
                    "target_difficulty": target_difficulty,
                    "confidence": difficulty_pred["confidence"],
                    "chosen_topic": topic,
                    "why_this_topic": "weak topic, unlocked" if topic in [t["topic"] for t in weak_topics] else "next unlocked topic",
                },
            }

    return {"question": None, "reasoning": {"message": "No matching question found — add more questions to the bank"}}
