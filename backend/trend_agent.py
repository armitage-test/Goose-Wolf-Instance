"""
Word Trend Monitor Agent — Nene & Wolf

Tracks trending words and short phrases relevant to humor/sarcasm and
empowerment/identity graphic tees. High-interest, rising phrases signal
the right moment to print a new design.

Runs automatically every 6 hours via APScheduler, or manually via POST /trends/refresh.
"""

import time
import logging
from datetime import datetime

from pytrends.request import TrendReq
from sqlalchemy.orm import Session

from .models import ShirtTrend
from .email_sender import send_trend_report

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Tracked words & phrases
# Each entry is a standalone search term — we track cultural interest in the
# word/phrase itself, not shirt searches. Rising interest = good design timing.
# ---------------------------------------------------------------------------

WORD_KEYWORDS = [
    # Humor & sarcasm — single words / short punchy phrases
    "unhinged",
    "feral",
    "chaotic",
    "not today",
    "send help",
    "hot mess",
    "goblin mode",
    "big yikes",
    "no thoughts",
    "chaos gremlin",
    # Empowerment & identity — single words / short punchy phrases
    "main character",
    "villain era",
    "soft life",
    "that girl",
    "delulu",
    "unbothered",
    "slay",
    "it's giving",
    "understood the assignment",
    "no apologies",
]

CATEGORIES = {
    # humor
    "unhinged": "humor",
    "feral": "humor",
    "chaotic": "humor",
    "not today": "humor",
    "send help": "humor",
    "hot mess": "humor",
    "goblin mode": "humor",
    "big yikes": "humor",
    "no thoughts": "humor",
    "chaos gremlin": "humor",
    # empowerment
    "main character": "empowerment",
    "villain era": "empowerment",
    "soft life": "empowerment",
    "that girl": "empowerment",
    "delulu": "empowerment",
    "unbothered": "empowerment",
    "slay": "empowerment",
    "it's giving": "empowerment",
    "understood the assignment": "empowerment",
    "no apologies": "empowerment",
}


def _derive_action(score: float, direction: str) -> str:
    """
    Translate a trend score + direction into a design timing recommendation.
    High interest + rising = peak cultural moment, ideal time to print the design.
    """
    if score >= 60 and direction == "rising":
        return "Design now"
    if score >= 40 and direction == "rising":
        return "Trending — act fast"
    if score >= 25:
        return "Worth watching"
    return "Fading out"


def _derive_direction(series: list[float]) -> str:
    """Compare the most recent data point against the prior average."""
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
    """Fetch 4-week interest data from Google Trends for all tracked words."""
    pytrends = TrendReq(hl="en-US", tz=360, timeout=(10, 25))
    results: list[ShirtTrend] = []
    fetched_at = datetime.utcnow()

    # pytrends limits each payload to 5 keywords
    chunk_size = 5
    chunks = [
        WORD_KEYWORDS[i : i + chunk_size]
        for i in range(0, len(WORD_KEYWORDS), chunk_size)
    ]

    for chunk in chunks:
        try:
            pytrends.build_payload(chunk, timeframe="now 4-w")
            df = pytrends.interest_over_time()

            if df.empty:
                logger.warning("Empty response from Google Trends for chunk: %s", chunk)
                continue

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
    Main entry point: fetch word trends and persist them to the database.
    Returns the number of trend rows inserted.
    """
    logger.info("Starting Nene & Wolf word trend fetch")
    trends = fetch_google_trends(db)

    if not trends:
        logger.warning("No trend data retrieved; skipping database write")
        return 0

    db.add_all(trends)
    db.commit()
    logger.info("Inserted %d word trend records", len(trends))

    fetched_at = trends[0].fetched_at
    send_trend_report(trends, fetched_at)

    return len(trends)
