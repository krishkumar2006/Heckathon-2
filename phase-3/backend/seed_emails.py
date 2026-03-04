"""
backend/seed_emails.py — Phase 3 Email Seed Script
Usage: python seed_emails.py --user_id <id>
Inserts 8 sample EmailLog records for demo purposes.
"""

import argparse
from datetime import datetime, timedelta, timezone

from dotenv import load_dotenv

load_dotenv()

from db import engine  # noqa: E402
from models import EmailLog, SQLModel  # noqa: E402
from sqlmodel import Session  # noqa: E402


def utc_days_ago(days: int) -> datetime:
    return datetime.now(timezone.utc) - timedelta(days=days)


SAMPLE_EMAILS = [
    {
        "from_address": "github@github.com",
        "subject": "[GitHub] Your pull request was merged",
        "preview": "Great news! Your pull request 'Add Phase 3 AI chat feature' has been merged into main by a collaborator. Check the repository for the latest changes.",
        "received_at": utc_days_ago(0),
        "is_read": False,
    },
    {
        "from_address": "noreply@netlify.app",
        "subject": "Deploy succeeded: todo-app-phase3",
        "preview": "Your site todo-app-phase3 deployed successfully! Your deploy is live at https://todo-app-phase3.netlify.app. Build time: 42 seconds.",
        "received_at": utc_days_ago(0),
        "is_read": False,
    },
    {
        "from_address": "team@hackathon.dev",
        "subject": "Hackathon submission deadline reminder",
        "preview": "This is a reminder that the Phase 3 hackathon submission deadline is in 24 hours. Make sure your demo video is uploaded and your repo is public before the cutoff.",
        "received_at": utc_days_ago(1),
        "is_read": True,
    },
    {
        "from_address": "noreply@neon.tech",
        "subject": "Your Neon database usage report",
        "preview": "Monthly usage summary for your Neon project: Storage used: 45 MB / 512 MB. Compute hours: 12.3 / 191.9. You are well within the free tier limits.",
        "received_at": utc_days_ago(2),
        "is_read": True,
    },
    {
        "from_address": "security@github.com",
        "subject": "Dependabot alert: 1 new vulnerability found",
        "preview": "A dependency in your repository todo-app has a known vulnerability. Package: next.js. Severity: moderate. Please review and update to the patched version.",
        "received_at": utc_days_ago(3),
        "is_read": False,
    },
    {
        "from_address": "groq@console.groq.com",
        "subject": "Welcome to Groq Cloud — your API key is ready",
        "preview": "Welcome! Your Groq API key has been created. You can now use llama-3.3-70b-versatile and other models. Free tier includes 30 RPM and 14,400 RPD at no cost.",
        "received_at": utc_days_ago(5),
        "is_read": True,
    },
    {
        "from_address": "newsletter@anthropic.com",
        "subject": "Claude 4.6 Release Notes — New Features",
        "preview": "We are excited to announce Claude Sonnet 4.6, featuring improved reasoning, better tool use accuracy, and faster response times. See the full changelog for details.",
        "received_at": utc_days_ago(6),
        "is_read": True,
    },
    {
        "from_address": "no-reply@vercel.com",
        "subject": "Your deployment is ready",
        "preview": "Your project todo-app-frontend has been deployed successfully. Preview URL: https://todo-app-frontend-git-phase3.vercel.app. Production domain: todo-app.vercel.app",
        "received_at": utc_days_ago(7),
        "is_read": False,
    },
]


def seed_emails(user_id: str) -> None:
    SQLModel.metadata.create_all(engine)

    with Session(engine) as session:
        for email_data in SAMPLE_EMAILS:
            email = EmailLog(user_id=user_id, **email_data)
            session.add(email)
        session.commit()

    print(f"Successfully seeded 8 emails for user: {user_id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed sample emails for a user")
    parser.add_argument("--user_id", required=True, help="The user ID to seed emails for")
    args = parser.parse_args()
    seed_emails(args.user_id)
