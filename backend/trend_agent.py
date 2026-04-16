"""
Shirt Trend Monitor Agent

Fetches shirt trend data from Google Trends and stores results in the database.
Run automatically every 6 hours via APScheduler, or manually via POST /trends/refresh.
"""

import time
import logging
from datetime import datetime

from pytrends.request import TrendReq
from sqlalchemy.orm import Session

from .models import ShirtTrend
from .email_sender import send_trend_report

logger = logging.getLogger(__name__)

SHIRT_KEYWORDS = [
    "graphic tee",
    "oversized t-shirt",
    "polo shirt",
    "linen shirt",
    "henley shirt",
    "tie dye shirt",
    "vintage band tee",
    "floral shirt",
    "denim shirt",
    "flannel shirt",
    "compression shirt",
    "crop top shirt",
    "bowling shirt",
    "Hawaiian shirt",
    "quarter zip shirt",
]

CATEGORIES = {
    "graphic tee": "streetwear",
    "oversized t-shirt": "streetwear",
    "polo shirt": "smart-casual",
    "linen shirt": "casual",
    "henley shirt": "casual",
    "tie dye shirt": "casual",
    "vintage band tee": "streetwear",
    "floral shirt": "resort",
    "denim shirt": "casual",
    "flannel shirt": "casual",
    "compression shirt": "athletic",
    "crop top shirt": "streetwear",
    "bowling shirt": "retro",
    "Hawaiian shirt": "resort",
    "quarter zip shirt": "smart-casual",
}


def _derive_action(score: float, direction: str) -> str:
    if score >= 60 and direction == "rising":
        return "Stock up"
    if score >= 40 and direction == "rising":
        return "Trending now"
    if score >= 30:
        return "Watch closely"
    return "Low interest"


def _derive_direction(series: list[float]) -> str:
    """Compare the last data point against the prior average to classify direction."""
    if len(series) < 2:
        return "stable"
    last = series[-1]
    prior_avg = sum(series[:-1]) / len(series[:-1])
    if prior_avg == 0:
        return "rising" if last > 0 else "stable"
    if last > prior_avg * 1.15:
        return "rising"
    if last < prior_avg * 0.85:
        return "falling"
    return "stable"


def fetch_google_trends(db: Session) -> list[ShirtTrend]:
    """Fetch interest data from Google Trends for all shirt keywords."""
    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
    results: list[ShirtTrend] = []
    fetched_at = datetime.utcnow()

    # pytrends limits payload to 5 keywords per request
    chunk_size = 5
    chunks = [
        SHIRT_KEYWORDS[i : i + chunk_size]
        for i in range(0, len(SHIRT_KEYWORDS), chunk_size)
    ]

    for chunk in chunks:
        try:
            pytrends.build_payload(chunk, timeframe="now 4-w")
            df = pytrends.interest_over_time()

            if df.empty:
                logger.warning("Empty response from Google Trends for chunk: %s", chunk)
                continue

            # Drop the isPartial column if present
            if "isPartial" in df.columns:
                df = df.drop(columns=["isPartial"])

            for keyword in chunk:
                if keyword not in df.columns:
                    continue
                series = df[keyword].tolist()
                score = float(sum(series) / len(series)) if series else 0.0
                direction = _derive_direction(series)
                action = _derive_action(score, direction)

                results.append(
                    ShirtTrend(
                        name=keyword,
                        category=CATEGORIES.get(keyword, "general"),
                        score=round(score, 1),
                        trend_direction=direction,
                        suggested_action=action,
                        source="google_trends",
                        fetched_at=fetched_at,
                    )
                )

        except Exception as exc:
            logger.error("Google Trends fetch failed for chunk %s: %s", chunk, exc)

        # Avoid rate-limiting between chunks
        time.sleep(2)

    return results


def run_trend_fetch(db: Session) -> int:
    """
    Main entry point: fetch trends and persist them to the database.
    Returns the number of trend rows inserted.
    """
    logger.info("Starting shirt trend fetch run")
    trends = fetch_google_trends(db)

    if not trends:
        logger.warning("No trend data retrieved; skipping database write")
        return 0

    db.add_all(trends)
    db.commit()
    logger.info("Inserted %d trend records", len(trends))

    fetched_at = trends[0].fetched_at
    send_trend_report(trends, fetched_at)

    return len(trends)
