"""Welcome email sent to new subscribers."""

import os

try:
    import resend
except ImportError:
    resend = None


def _build_welcome_html(magic_link: str = None) -> str:
    site_url = os.environ.get("SITE_URL", "https://agenticedge.tech")
    signin_block = ""
    if magic_link:
        signin_block = f"""
<div class="cta-box" style="margin-bottom: 24px;">
  <strong>Sign in to your account</strong><br>
  <span style="font-size: 14px; color: #666;">Click below to access your Agentic Edge account. This link expires in 15 minutes.</span><br>
  <a href="{magic_link}">Sign in now</a>
</div>
"""
    return f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<style>
  body {{
    font-family: Georgia, 'Times New Roman', serif;
    max-width: 560px;
    margin: 0 auto;
    padding: 32px 20px;
    color: #1a1a1a;
    line-height: 1.7;
  }}
  h1 {{ font-size: 24px; margin: 0 0 16px; }}
  p {{ margin: 0 0 16px; }}
  .checklist {{ margin: 16px 0 24px; padding: 0; list-style: none; }}
  .checklist li {{ padding: 6px 0; }}
  .checklist li::before {{ content: "-> "; color: #7c3aed; font-weight: 600; }}
  .cta-box {{
    background: #f8f5ff;
    border: 1px solid #e9e0ff;
    border-radius: 8px;
    padding: 20px;
    text-align: center;
    margin: 24px 0;
  }}
  .cta-box a {{
    display: inline-block;
    background: #7c3aed;
    color: white;
    padding: 10px 24px;
    border-radius: 6px;
    text-decoration: none;
    font-weight: 600;
    margin-top: 8px;
  }}
  .footer {{ margin-top: 32px; padding-top: 16px; border-top: 1px solid #eee; font-size: 13px; color: #999; }}
  .footer a {{ color: #999; }}
  a {{ color: #7c3aed; }}
</style>
</head>
<body>

<h1>Welcome to the club of people who are at the agentic edge.</h1>

{signin_block}<p>You're now part of a small group of builders who refuse to fall behind in the AI agent space. That's why you're here. And that's exactly who this is for.</p>

<p>Here's what happens next:</p>

<ul class="checklist">
  <li>Monday morning: your first digest lands in this inbox</li>
  <li>3 deep analysis sections on what actually moved this week</li>
  <li>700+ sources scanned. You read for 5 minutes.</li>
  <li>Reply to any issue. I read every one.</li>
</ul>

<p>How it works: I built an AI agent that scans 700+ sources every week, scores them by builder relevance, and cuts the noise. I review the top stories, write the analysis, and send it Monday. No AI slop. No filler.</p>

<div class="cta-box">
  <strong>Want to go deeper?</strong><br>
  <span style="font-size: 14px; color: #666;">Pro members get 15+ source links, The Vault, and the builder Discord.</span><br>
  <a href="{site_url}/upgrade">See what's behind the paywall</a>
</div>

<p>Talk soon,<br>
<strong>Agentic Edge</strong></p>

<div class="footer">
  <p><a href="{site_url}/unsubscribe">Unsubscribe</a> · <a href="{site_url}">Web</a></p>
  <p style="font-size: 11px; color: #bbb; margin-top: 8px;">Agentic Edge · Stanford, CA</p>
</div>

</body>
</html>"""


def send_welcome_email(email: str, magic_link: str = None) -> bool:
    """Send welcome email to a new subscriber. Optionally embed a magic link."""
    resend_key = os.environ.get("RESEND_API_KEY")

    if resend_key and resend is not None:
        try:
            resend.api_key = resend_key
            sender = os.environ.get("RESEND_FROM", "Agentic Edge <digest@agenticedge.tech>")

            resend.Emails.send({
                "from": sender,
                "to": [email],
                "subject": "Welcome to Agentic Edge — you're in.",
                "html": _build_welcome_html(magic_link),
            })
            print(f"  Welcome email sent to {email}")
            return True
        except Exception as e:
            print(f"  Welcome email failed: {e}")
            return False
    else:
        # Gmail fallback
        try:
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText

            sender_email = os.environ.get("DIGEST_EMAIL_FROM")
            password = os.environ.get("DIGEST_EMAIL_PASSWORD")
            if not sender_email or not password:
                return False

            msg = MIMEMultipart("alternative")
            msg["Subject"] = "Welcome to Agentic Edge — you're in."
            msg["From"] = sender_email
            msg["To"] = email
            msg.attach(MIMEText(_build_welcome_html(magic_link), "html"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, email, msg.as_string())

            print(f"  Welcome email sent via Gmail to {email}")
            return True
        except Exception as e:
            print(f"  Welcome email failed: {e}")
            return False
