"""Email delivery for the Agentic Digest.

Supports two backends:
  1. Resend (recommended) — proper deliverability, DKIM/SPF handled
  2. Gmail SMTP (fallback) — works but may hit spam filters at scale

Set RESEND_API_KEY in .env to use Resend. Otherwise falls back to Gmail.
"""

import os
from datetime import datetime

try:
    import markdown
except ImportError:
    markdown = None

try:
    import resend
except ImportError:
    resend = None


def _build_html(digest_content: str, unsubscribe_url: str = "#") -> str:
    """Convert markdown digest to a clean HTML email."""
    if markdown is None:
        return digest_content

    html_content = markdown.markdown(digest_content)

    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{
    font-family: Georgia, 'Times New Roman', serif;
    max-width: 600px;
    margin: 0 auto;
    padding: 24px 16px;
    color: #1a1a1a;
    line-height: 1.7;
    background: #ffffff;
  }}
  h1 {{
    font-size: 26px;
    font-weight: 700;
    margin: 0 0 4px 0;
  }}
  h3 {{
    font-size: 18px;
    margin: 28px 0 8px 0;
    line-height: 1.3;
  }}
  p {{
    margin: 8px 0 16px 0;
  }}
  a {{
    color: #7c3aed;
    text-decoration: none;
  }}
  a:hover {{
    text-decoration: underline;
  }}
  hr {{
    border: none;
    border-top: 1px solid #eee;
    margin: 24px 0;
  }}
  strong {{
    font-weight: 600;
  }}
  .footer {{
    margin-top: 40px;
    padding-top: 20px;
    border-top: 1px solid #eee;
    font-size: 13px;
    color: #999;
    text-align: center;
  }}
  .footer a {{
    color: #999;
  }}
  .upgrade-box {{
    background: #f8f5ff;
    border: 1px solid #e9e0ff;
    border-radius: 8px;
    padding: 16px 20px;
    margin: 24px 0;
    text-align: center;
  }}
  .upgrade-box a {{
    display: inline-block;
    background: #7c3aed;
    color: white;
    padding: 10px 24px;
    border-radius: 6px;
    font-weight: 600;
    font-size: 14px;
    margin-top: 8px;
    text-decoration: none;
  }}
</style>
</head>
<body>
  {html_content}

  <div class="upgrade-box">
    <strong>Want the full source list + tools?</strong><br>
    <span style="font-size: 14px; color: #666;">Pro members get 15+ ranked sources, early access, and community.</span><br>
    <a href="{os.environ.get('SITE_URL', 'https://agenticedge.com')}/upgrade">Upgrade to Pro</a>
  </div>

  <div class="footer">
    <p>Agentic Edge — curated by a Stanford engineer for AI builders.</p>
    <p><a href="{unsubscribe_url}">Unsubscribe</a> · <a href="{os.environ.get('SITE_URL', 'https://agenticedge.com')}">Web</a> · <a href="{os.environ.get('SITE_URL', 'https://agenticedge.com')}/pro">The Vault</a></p>
    <p style="font-size: 11px; color: #bbb; margin-top: 8px;">Agentic Edge · Stanford, CA</p>
  </div>
</body>
</html>"""


def send_digest_email(
    digest_content: str,
    email_from: str = None,
    email_to: str = None,
    password: str = None,
) -> bool:
    """Send the digest email. Uses Resend if available, falls back to Gmail SMTP."""

    resend_key = os.environ.get("RESEND_API_KEY")

    if resend_key and resend is not None:
        return _send_via_resend(digest_content, resend_key, email_to)
    else:
        return _send_via_gmail(digest_content, email_from, email_to, password)


def send_to_all_subscribers(digest_content: str, db) -> dict:
    """Send digest to all active subscribers, respecting tiers."""
    results = {"sent": 0, "failed": 0, "skipped": 0}

    subscribers = db.get_subscribers()
    if not subscribers:
        print("  No subscribers to email.")
        return results

    for sub in subscribers:
        email = sub["email"]
        try:
            success = send_digest_email(digest_content, email_to=email)
            if success:
                results["sent"] += 1
            else:
                results["failed"] += 1
        except Exception as e:
            print(f"  Failed to send to {email}: {e}")
            results["failed"] += 1

    print(f"  Email results: {results['sent']} sent, {results['failed']} failed")
    return results


def _send_via_resend(digest_content: str, api_key: str, email_to: str = None) -> bool:
    """Send via Resend — proper deliverability."""
    try:
        resend.api_key = api_key

        recipient = email_to or os.environ.get("DIGEST_EMAIL_TO")
        sender = os.environ.get("RESEND_FROM", "Agentic Edge <digest@agenticedge.com>")

        if not recipient:
            print("  No recipient configured.")
            return False

        today = datetime.now().strftime("%B %d, %Y")
        unsub_url = f"{os.environ.get('SITE_URL', 'https://agenticedge.com')}/unsubscribe?email={recipient}"
        html = _build_html(digest_content, unsubscribe_url=unsub_url)

        params = {
            "from": sender,
            "to": [recipient],
            "subject": f"Agentic Edge | {today}",
            "html": html,
            "text": digest_content,
            "headers": {
                "List-Unsubscribe": f"<{os.environ.get('SITE_URL', 'https://agenticedge.com')}/unsubscribe?email={recipient}>",
                "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
            },
        }

        result = resend.Emails.send(params)
        print(f"  Sent via Resend to {recipient} (id: {result.get('id', 'ok')})")
        return True

    except Exception as e:
        print(f"  Resend failed: {e}")
        return False


def _send_via_gmail(digest_content: str, email_from: str = None,
                    email_to: str = None, password: str = None) -> bool:
    """Fallback: send via Gmail SMTP."""
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    sender = email_from or os.environ.get("DIGEST_EMAIL_FROM")
    recipient = email_to or os.environ.get("DIGEST_EMAIL_TO")
    app_password = password or os.environ.get("DIGEST_EMAIL_PASSWORD")

    if not all([sender, recipient, app_password]):
        print("  Missing email config. Set DIGEST_EMAIL_FROM, DIGEST_EMAIL_TO, DIGEST_EMAIL_PASSWORD.")
        return False

    try:
        today = datetime.now().strftime("%B %d, %Y")
        unsub_url = f"{os.environ.get('SITE_URL', 'https://agenticedge.com')}/unsubscribe?email={recipient}"
        html = _build_html(digest_content, unsubscribe_url=unsub_url)

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Agentic Edge | {today}"
        msg["From"] = sender
        msg["To"] = recipient
        msg["List-Unsubscribe"] = f"<{os.environ.get('SITE_URL', 'https://agenticedge.com')}/unsubscribe?email={recipient}>"
        msg["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"

        msg.attach(MIMEText(digest_content, "plain"))
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipient, msg.as_string())

        print(f"  Sent via Gmail to {recipient}")
        return True

    except Exception as e:
        print(f"  Gmail failed: {e}")
        return False
