#!/usr/bin/env python3
"""News Brief — email delivery (optional fallback to Lark).

Sends the brief body via SMTP. Credentials come from the environment or
~/.config/news-brief/.env (which run_brief.sh sources). No interactive setup.

Required env vars:
  NEWSBRIEF_SMTP_USER   sender address (e.g. you@gmail.com)
  NEWSBRIEF_SMTP_PASS   SMTP password / app password
Optional:
  NEWSBRIEF_SMTP_HOST   default smtp.gmail.com
  NEWSBRIEF_SMTP_PORT   default 465 (SSL)

Usage:
  python3 send_email.py --to "addr@example.com" --subject "News Brief — 2026-06-05" \
      --body-file /tmp/newsbrief_body.txt
"""
import argparse
import os
import smtplib
import ssl
import sys
from email.mime.text import MIMEText


def load_dotenv(path):
    if not os.path.isfile(path):
        return
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    p = argparse.ArgumentParser(description="News Brief email sender")
    p.add_argument("--to", required=True, help="Recipient(s), comma-separated")
    p.add_argument("--subject", required=True)
    p.add_argument("--body-file", required=True)
    args = p.parse_args()

    load_dotenv(os.path.expanduser("~/.config/news-brief/.env"))

    user = os.environ.get("NEWSBRIEF_SMTP_USER", "")
    password = os.environ.get("NEWSBRIEF_SMTP_PASS", "")
    host = os.environ.get("NEWSBRIEF_SMTP_HOST", "smtp.gmail.com")
    port = int(os.environ.get("NEWSBRIEF_SMTP_PORT", "465"))

    if not user or not password:
        sys.exit(
            "ERROR: SMTP credentials not set. Export NEWSBRIEF_SMTP_USER and "
            "NEWSBRIEF_SMTP_PASS, or add them to ~/.config/news-brief/.env. "
            "See TUTORIAL.md (email delivery)."
        )

    with open(args.body_file) as f:
        body = f.read()

    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = args.subject
    msg["From"] = user
    msg["To"] = args.to
    recipients = [a.strip() for a in args.to.split(",") if a.strip()]

    try:
        ctx = ssl.create_default_context()
        if port == 465:
            # implicit TLS (Gmail default)
            with smtplib.SMTP_SSL(host, port, context=ctx) as s:
                s.login(user, password)
                s.sendmail(user, recipients, msg.as_string())
        else:
            # submission port (587/25): STARTTLS (Outlook/Office365, most providers)
            with smtplib.SMTP(host, port) as s:
                s.starttls(context=ctx)
                s.login(user, password)
                s.sendmail(user, recipients, msg.as_string())
        print(f"Email sent to {args.to}")
    except smtplib.SMTPAuthenticationError:
        sys.exit("ERROR: SMTP auth failed. For Gmail use a 16-char App Password, not your account password.")
    except Exception as e:  # noqa: BLE001
        sys.exit(f"ERROR: failed to send email: {e}")


if __name__ == "__main__":
    main()
