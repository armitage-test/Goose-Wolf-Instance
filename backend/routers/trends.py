from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import ShirtTrend
from ..schemas import ShirtTrendOut, TrendSummaryOut
from ..trend_agent import run_trend_fetch

router = APIRouter(prefix="/trends", tags=["trends"])


def _latest_fetch_subquery(db: Session):
    """Return a subquery scalar for the most recent fetched_at timestamp."""
    return db.query(func.max(ShirtTrend.fetched_at)).scalar()


@router.get("/", response_model=list[ShirtTrendOut])
def list_trends(source: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    """Return the most recent trend snapshot, ordered by score descending."""
    latest = _latest_fetch_subquery(db)
    if latest is None:
        return []

    query = db.query(ShirtTrend).filter(ShirtTrend.fetched_at == latest)
    if source:
        query = query.filter(ShirtTrend.source == source)

    return query.order_by(ShirtTrend.score.desc()).limit(limit).all()


@router.post("/refresh")
def refresh_trends(db: Session = Depends(get_db)):
    """Manually trigger a fresh trend fetch from Google Trends."""
    inserted = run_trend_fetch(db)
    return {"status": "ok", "keywords_updated": inserted}


@router.get("/summary", response_model=TrendSummaryOut)
def trend_summary(db: Session = Depends(get_db)):
    """Return aggregate stats for the latest trend snapshot."""
    latest = _latest_fetch_subquery(db)
    if latest is None:
        return TrendSummaryOut(
            total=0,
            top_trend=None,
            top_score=None,
            last_fetched=None,
            by_action={},
        )

    rows = db.query(ShirtTrend).filter(ShirtTrend.fetched_at == latest).all()

    by_action: dict[str, int] = {}
    for row in rows:
        by_action[row.suggested_action] = by_action.get(row.suggested_action, 0) + 1

    top = max(rows, key=lambda r: r.score) if rows else None

    return TrendSummaryOut(
        total=len(rows),
        top_trend=top.name if top else None,
        top_score=top.score if top else None,
        last_fetched=latest,
        by_action=by_action,
    )
