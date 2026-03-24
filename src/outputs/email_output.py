"""Email delivery for the Agentic Digest."""

import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

try:
    import markdown
except ImportError:
    markdown = None


def send_digest_email(
    digest_content: str,
    email_from: str = None,
    email_to: str = None,
    password: str = None,
) -> bool:
    """
    Send the digest via Gmail SMTP.

    Requires Gmail app password and environment variables:
    - DIGEST_EMAIL_FROM (or parameter)
    - DIGEST_EMAIL_TO (or parameter)
    - DIGEST_EMAIL_PASSWORD (or parameter)

    Args:
        digest_content: Markdown content of the digest
        email_from: Sender email (defaults to env var)
        email_to: Recipient email (defaults to env var)
        password: Gmail app password (defaults to env var)

    Returns:
        True if sent successfully, False otherwise
    """
    # Get credentials from parameters or environment
    sender = email_from or os.environ.get("DIGEST_EMAIL_FROM")
    recipient = email_to or os.environ.get("DIGEST_EMAIL_TO")
    app_password = password or os.environ.get("DIGEST_EMAIL_PASSWORD")

    if not all([sender, recipient, app_password]):
        print("Missing email config. Set DIGEST_EMAIL_FROM, DIGEST_EMAIL_TO, DIGEST_EMAIL_PASSWORD.")
        return False

    if markdown is None:
        print("Install markdown: pip install markdown")
        return False

    try:
        # Convert markdown to HTML
        html_content = markdown.markdown(digest_content)

        # Wrap in email template
        html_body = f"""
<html>
<head>
    <style>
        body {{ font-family: Georgia, serif; max-width: 640px; margin: 0 auto; padding: 20px; color: #1a1a1a; line-height: 1.6; }}
        h1 {{ font-size: 24px; font-weight: 700; }}
        h3 {{ font-size: 16px; margin-top: 24px; margin-bottom: 4px; }}
        a {{ color: #0066cc; text-decoration: none; }}
        hr {{ border: none; border-top: 1px solid #ddd; margin: 24px 0; }}
        strong {{ font-weight: 600; }}
    </style>
</head>
<body>
    {html_content}
</body>
</html>
        """

        # Prepare email
        today = datetime.now().strftime("%B %d, %Y")
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Agentic Edge Digest | {today}"
        msg["From"] = sender
        msg["To"] = recipient

        msg.attach(MIMEText(digest_content, "plain"))
        msg.attach(MIMEText(html_body, "html"))

        # Send via Gmail SMTP
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender, app_password)
            server.sendmail(sender, recipient, msg.as_string())

        print(f"  ✓ Digest emailed to {recipient}")
        return True

    except Exception as e:
        print(f"  ✗ Failed to send email: {e}")
        return False
