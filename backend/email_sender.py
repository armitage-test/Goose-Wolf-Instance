"""
Email reporter for the Shirt Trend Monitor.

Sends an HTML digest to RECIPIENT_EMAIL via Gmail SMTP after each trend fetch.

Required environment variables (set in .env):
    GMAIL_ADDRESS      — the Gmail account used to send (e.g. you@gmail.com)
    GMAIL_APP_PASSWORD — a Gmail app-specific password (not your login password)
    RECIPIENT_EMAIL    — where the report is delivered
"""

import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv

from .models import ShirtTrend

load_dotenv()

logger = logging.getLogger(__name__)

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
RECIPIENT_EMAIL = os.getenv("RECIPIENT_EMAIL", "")

_ACTION_COLOR = {
    "Stock up": "#27ae60",
    "Trending now": "#2980b9",
    "Watch closely": "#e67e22",
    "Low interest": "#95a5a6",
}

_DIRECTION_SYMBOL = {
    "rising": "↑",
    "stable": "→",
    "falling": "↓",
}


def _build_html(trends: list[ShirtTrend], fetched_at: datetime) -> str:
    rows = ""
    for t in sorted(trends, key=lambda x: x.score, reverse=True):
        color = _ACTION_COLOR.get(t.suggested_action, "#ccc")
        symbol = _DIRECTION_SYMBOL.get(t.trend_direction, "")
        bar_width = int(t.score)
        rows += f"""
        <tr>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;">
            <strong>{t.name}</strong>
            <br><small style="color:#888;">{t.category}</small>
          </td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:center;">
            <div style="background:#eee;border-radius:4px;height:10px;width:120px;display:inline-block;vertical-align:middle;">
              <div style="background:{color};width:{bar_width}%;height:100%;border-radius:4px;"></div>
            </div>
            <span style="margin-left:6px;font-weight:bold;">{t.score:.1f}</span>
          </td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;text-align:center;font-size:1.1em;">
            {symbol} {t.trend_direction.capitalize()}
          </td>
          <td style="padding:8px 12px;border-bottom:1px solid #eee;">
            <span style="background:{color};color:#fff;padding:3px 10px;border-radius:12px;font-size:0.82em;font-weight:bold;">
              {t.suggested_action}
            </span>
          </td>
        </tr>"""

    timestamp = fetched_at.strftime("%B %d, %Y at %H:%M UTC")
    return f"""
<!DOCTYPE html>
<html>
<body style="font-family:Arial,sans-serif;color:#333;max-width:680px;margin:0 auto;">
  <h2 style="border-bottom:2px solid #3498db;padding-bottom:8px;">
    Shirt Trend Report
  </h2>
  <p style="color:#666;font-size:0.9em;">Fetched: {timestamp}</p>
  <table style="width:100%;border-collapse:collapse;font-size:0.9em;">
    <thead>
      <tr style="background:#f4f4f4;text-align:left;">
        <th style="padding:10px 12px;">Keyword</th>
        <th style="padding:10px 12px;text-align:center;">Interest (0–100)</th>
        <th style="padding:10px 12px;text-align:center;">Direction</th>
        <th style="padding:10px 12px;">Action</th>
      </tr>
    </thead>
    <tbody>{rows}
    </tbody>
  </table>
  <p style="margin-top:24px;font-size:0.8em;color:#aaa;">
    Sent by your Shirt Trend Monitor · Next report in ~6 hours
  </p>
</body>
</html>"""


def send_trend_report(trends: list[ShirtTrend], fetched_at: datetime) -> None:
    """Send a trend digest email. Logs a warning and returns silently if config is missing."""
    if not all([GMAIL_ADDRESS, GMAIL_APP_PASSWORD, RECIPIENT_EMAIL]):
        logger.warning(
            "Email not sent: GMAIL_ADDRESS, GMAIL_APP_PASSWORD, or RECIPIENT_EMAIL "
            "is not set in the environment."
        )
        return

    subject = f"Shirt Trend Report — {fetched_at.strftime('%b %d, %Y %H:%M UTC')}"
    html_body = _build_html(trends, fetched_at)

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = RECIPIENT_EMAIL
    msg.attach(MIMEText(html_body, "html"))

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            smtp.sendmail(GMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        logger.info("Trend report emailed to %s", RECIPIENT_EMAIL)
    except smtplib.SMTPException as exc:
        logger.error("Failed to send trend report email: %s", exc)
