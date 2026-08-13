from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, require_admin
from app.db.mysql import get_db
from app.dsa.heap import LeaderboardEntry, build_leaderboard
from app.models.contest import Contest, ContestParticipant
from app.models.submission import Submission
from app.models.user import User
from app.schemas.contest import ContestCreate, ContestOut, ContestStatus

router = APIRouter(prefix="/contests", tags=["contests"])


def _status_of(contest: Contest) -> ContestStatus:
    now = datetime.now(timezone.utc)
    start = contest.start_time if contest.start_time.tzinfo else contest.start_time.replace(tzinfo=timezone.utc)
    end = contest.end_time if contest.end_time.tzinfo else contest.end_time.replace(tzinfo=timezone.utc)

    if now < start:
        status, remaining = "upcoming", int((start - now).total_seconds())
    elif now <= end:
        status, remaining = "live", int((end - now).total_seconds())
    else:
        status, remaining = "ended", None

    return ContestStatus(id=contest.id, title=contest.title, status=status, seconds_remaining=remaining)


@router.post("", response_model=ContestOut, status_code=201)
def create_contest(payload: ContestCreate, db: Session = Depends(get_db), _: User = Depends(require_admin)):
    contest = Contest(
        title=payload.title,
        question_ids=",".join(payload.question_ids),
        start_time=payload.start_time,
        end_time=payload.end_time,
    )
    db.add(contest)
    db.commit()
    db.refresh(contest)
    return contest


@router.get("", response_model=list[ContestStatus])
def list_contests(db: Session = Depends(get_db)):
    contests = db.query(Contest).order_by(Contest.start_time.desc()).all()
    return [_status_of(c) for c in contests]


@router.post("/{contest_id}/join", status_code=201)
def join_contest(contest_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")

    existing = (
        db.query(ContestParticipant)
        .filter(ContestParticipant.contest_id == contest_id, ContestParticipant.user_id == current_user.id)
        .first()
    )
    if existing:
        return {"message": "Already joined"}

    db.add(ContestParticipant(contest_id=contest_id, user_id=current_user.id))
    db.commit()
    return {"message": "Joined contest", "question_ids": contest.question_ids.split(",")}


@router.get("/{contest_id}", response_model=ContestStatus)
def contest_status(contest_id: int, db: Session = Depends(get_db)):
    contest = db.query(Contest).filter(Contest.id == contest_id).first()
    if not contest:
        raise HTTPException(status_code=404, detail="Contest not found")
    return _status_of(contest)


@router.get("/{contest_id}/leaderboard")
def contest_leaderboard(contest_id: int, db: Session = Depends(get_db), top_n: int = 10):
    """Same heap-ranking logic as the global leaderboard, scoped to one contest."""
    rows = (
        db.query(Submission.user_id, User.name, Submission.verdict, Submission.submitted_at)
        .join(User, User.id == Submission.user_id)
        .filter(Submission.contest_id == contest_id)
        .all()
    )

    scores: dict[int, dict] = {}
    for user_id, name, verdict, submitted_at in rows:
        entry = scores.setdefault(user_id, {"name": name, "score": 0, "last_ts": submitted_at.timestamp()})
        if verdict == "Accepted":
            entry["score"] += 1
        entry["last_ts"] = min(entry["last_ts"], submitted_at.timestamp())

    entries = [
        LeaderboardEntry(user_id=uid, user_name=v["name"], score=v["score"], last_submission_ts=v["last_ts"])
        for uid, v in scores.items()
    ]
    top = build_leaderboard(entries, top_n=top_n)
    return [
        {"rank": i + 1, "user_id": e.user_id, "user_name": e.user_name, "score": e.score}
        for i, e in enumerate(top)
    ]
