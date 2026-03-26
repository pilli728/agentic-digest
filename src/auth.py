"""
Magic link authentication for Agentic Edge.

Flow:
  1. User enters email on /login
  2. Server generates a token, sends email with magic link
  3. User clicks link → /auth/verify?token=xxx
  4. Server validates token, sets a session cookie
  5. Cookie checked on premium pages to gate content by tier
"""

import os
import hashlib
import secrets
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

try:
    import resend
except ImportError:
    resend = None


TOKEN_EXPIRY_MINUTES = 15
SESSION_EXPIRY_DAYS = 30

DB_PATH = str(Path(__file__).parent.parent / "data" / "digest.db")


def _get_db():
    """Get a SQLite connection and ensure auth tables exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS auth_sessions (
        session_id TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        tier TEXT NOT NULL,
        expires_at TEXT NOT NULL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS auth_tokens (
        token TEXT PRIMARY KEY,
        email TEXT NOT NULL,
        tier TEXT NOT NULL,
        expires_at TEXT NOT NULL
    )""")
    conn.commit()
    return conn


def create_magic_link(email: str, db) -> str:
    """Generate a magic link token for the given email. Returns the token."""
    # Check subscriber exists and get their tier
    cursor = db.conn.cursor()
    cursor.execute("SELECT tier FROM subscribers WHERE email = ? AND active = 1", (email,))
    row = cursor.fetchone()

    if not row:
        return None  # Not a subscriber

    tier = dict(row)["tier"]
    token = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(minutes=TOKEN_EXPIRY_MINUTES)).isoformat()

    conn = _get_db()
    conn.execute(
        "INSERT OR REPLACE INTO auth_tokens (token, email, tier, expires_at) VALUES (?, ?, ?, ?)",
        (token, email, tier, expires_at),
    )
    conn.commit()
    conn.close()

    return token


def send_magic_link_email(email: str, token: str, base_url: str = None) -> bool:
    """Send the magic link email."""
    if base_url is None:
        base_url = os.environ.get("SITE_URL", "http://localhost:4321")
    link = f"{base_url}/auth/verify?token={token}"

    html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"></head>
<body style="font-family: Georgia, serif; max-width: 480px; margin: 0 auto; padding: 32px 20px; color: #1a1a1a; line-height: 1.6;">
  <h2 style="margin: 0 0 16px;">Sign in to Agentic Edge</h2>
  <p>Click the button below to sign in. This link expires in {TOKEN_EXPIRY_MINUTES} minutes.</p>
  <a href="{link}" style="display: inline-block; background: #7c3aed; color: white; padding: 12px 28px; border-radius: 8px; text-decoration: none; font-weight: 600; margin: 16px 0;">Sign in</a>
  <p style="font-size: 13px; color: #999;">If you didn't request this, you can ignore this email.</p>
  <p style="font-size: 13px; color: #999;">Or copy this link: {link}</p>
</body>
</html>"""

    resend_key = os.environ.get("RESEND_API_KEY")
    if resend_key and resend is not None:
        try:
            resend.api_key = resend_key
            sender = os.environ.get("RESEND_FROM", "Agentic Edge <digest@agenticedge.com>")
            resend.Emails.send({
                "from": sender,
                "to": [email],
                "subject": "Sign in to Agentic Edge",
                "html": html,
            })
            return True
        except Exception as e:
            print(f"  Magic link email failed: {e}")
            return False
    else:
        # Gmail fallback
        try:
            import smtplib
            from email.mime.text import MIMEText

            sender_email = os.environ.get("DIGEST_EMAIL_FROM")
            password = os.environ.get("DIGEST_EMAIL_PASSWORD")
            if not sender_email or not password:
                return False

            msg = MIMEText(html, "html")
            msg["Subject"] = "Sign in to Agentic Edge"
            msg["From"] = sender_email
            msg["To"] = email

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, email, msg.as_string())
            return True
        except Exception:
            return False


def verify_token(token: str) -> dict:
    """Verify a magic link token. Returns session info or None."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT email, tier, expires_at FROM auth_tokens WHERE token = ?", (token,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    pending = dict(row)
    if datetime.now() > datetime.fromisoformat(pending["expires_at"]):
        conn.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
        conn.commit()
        conn.close()
        return None

    # Create session
    session_id = secrets.token_urlsafe(32)
    expires_at = (datetime.now() + timedelta(days=SESSION_EXPIRY_DAYS)).isoformat()
    conn.execute(
        "INSERT OR REPLACE INTO auth_sessions (session_id, email, tier, expires_at) VALUES (?, ?, ?, ?)",
        (session_id, pending["email"], pending["tier"], expires_at),
    )

    # Clean up token
    conn.execute("DELETE FROM auth_tokens WHERE token = ?", (token,))
    conn.commit()
    conn.close()

    return {"session_id": session_id, "email": pending["email"], "tier": pending["tier"]}


def get_session(session_id: str) -> dict:
    """Get session info from a session ID. Returns None if invalid/expired."""
    conn = _get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT email, tier, expires_at FROM auth_sessions WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()

    if not row:
        conn.close()
        return None

    session = dict(row)
    if datetime.now() > datetime.fromisoformat(session["expires_at"]):
        conn.execute("DELETE FROM auth_sessions WHERE session_id = ?", (session_id,))
        conn.commit()
        conn.close()
        return None

    conn.close()
    return {"email": session["email"], "tier": session["tier"]}


def logout(session_id: str):
    """Invalidate a session."""
    conn = _get_db()
    conn.execute("DELETE FROM auth_sessions WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()
