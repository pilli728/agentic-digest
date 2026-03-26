"""Welcome email sent to new subscribers."""

import os

try:
    import resend
except ImportError:
    resend = None


def _build_welcome_html() -> str:
    site_url = os.environ.get("SITE_URL", "https://agenticedge.com")
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

<h1>Welcome to Agentic Edge.</h1>

<p>You just joined a small group of builders who want to stay ahead of the AI agent space without spending hours reading.</p>

<p>Here's what to expect:</p>

<ul class="checklist">
  <li>Your first digest arrives Monday morning</li>
  <li>3 deep analysis sections on the topics reshaping the space</li>
  <li>Every story is ranked by how much it affects what you're building</li>
  <li>Reply to any issue. I read every response.</li>
</ul>

<p>A quick note on how this works: I built an AI agent that scans 700+ sources every week, scores them by builder relevance, and filters out the noise. I review the top 20, add my analysis, and send it to you. Zero AI slop.</p>

<p>I'm a Stanford-trained engineer building AI agents full-time. This newsletter is what I wish existed when I started.</p>

<div class="cta-box">
  <strong>Want to go deeper?</strong><br>
  <span style="font-size: 14px; color: #666;">Pro members get 15+ source links, community access, and early delivery every Friday.</span><br>
  <a href="{site_url}/upgrade">See Pro plans</a>
</div>

<p>Talk soon,<br>
<strong>Agentic Edge</strong></p>

<div class="footer">
  <p><a href="{site_url}/unsubscribe">Unsubscribe</a> · <a href="{site_url}">Web</a></p>
  <p style="font-size: 11px; color: #bbb; margin-top: 8px;">Agentic Edge · Stanford, CA</p>
</div>

</body>
</html>"""


def send_welcome_email(email: str) -> bool:
    """Send welcome email to a new subscriber."""
    resend_key = os.environ.get("RESEND_API_KEY")

    if resend_key and resend is not None:
        try:
            resend.api_key = resend_key
            sender = os.environ.get("RESEND_FROM", "Agentic Edge <digest@agenticedge.com>")

            resend.Emails.send({
                "from": sender,
                "to": [email],
                "subject": "Welcome to Agentic Edge",
                "html": _build_welcome_html(),
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
            msg["Subject"] = "Welcome to Agentic Edge"
            msg["From"] = sender_email
            msg["To"] = email
            msg.attach(MIMEText(_build_welcome_html(), "html"))

            with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                server.login(sender_email, password)
                server.sendmail(sender_email, email, msg.as_string())

            print(f"  Welcome email sent via Gmail to {email}")
            return True
        except Exception as e:
            print(f"  Welcome email failed: {e}")
            return False
