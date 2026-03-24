"""
Simple API server for handling article feedback from the website.
Run this in the background to enable feedback buttons in the UI.

Usage:
    python3 src/feedback_server.py

Then feedback buttons on http://localhost:4321 will work!
"""

import json
import sqlite3
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))
from feedback_api import FeedbackHandler


class FeedbackHandler_HTTP(BaseHTTPRequestHandler):
    """HTTP request handler for feedback API."""

    feedback = FeedbackHandler()

    def do_POST(self):
        """Handle POST requests to /api/feedback."""
        if self.path != "/api/feedback":
            self.send_error(404)
            return

        # Read request body
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body.decode("utf-8"))
        except:
            self.send_error(400, "Invalid JSON")
            return

        article_id = data.get("articleId")
        reaction = data.get("reaction")
        comment = data.get("comment")

        if not article_id:
            self.send_error(400, "Missing articleId")
            return

        # Save feedback
        success = self.feedback.save_feedback(article_id, reaction, comment)

        # Send response
        self.send_response(200 if success else 500)
        self.send_header("Content-Type", "application/json")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()

        response = {
            "success": success,
            "message": "Feedback saved!" if success else "Error saving feedback"
        }
        self.wfile.write(json.dumps(response).encode())

    def do_GET(self):
        """Handle GET requests for feedback stats."""
        if self.path == "/api/feedback/summary":
            summary = self.feedback.get_feedback_summary()

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(json.dumps(summary).encode())

        elif self.path.startswith("/api/feedback/article/"):
            article_id = self.path.split("/")[-1]
            feedback = self.feedback.get_article_feedback(article_id)

            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            self.wfile.write(json.dumps(feedback).encode())
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        """Handle CORS preflight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def log_message(self, format, *args):
        """Suppress default logging."""
        pass


def main():
    """Start the feedback API server."""
    port = 8000
    server = HTTPServer(("localhost", port), FeedbackHandler_HTTP)

    print()
    print("=" * 60)
    print("🚀 Feedback API Server Started")
    print("=" * 60)
    print(f"Listening on: http://localhost:{port}/api/feedback")
    print()
    print("✅ Feedback buttons on http://localhost:4321 are now active!")
    print()
    print("Available endpoints:")
    print(f"  POST {port}/api/feedback          - Save feedback")
    print(f"  GET  {port}/api/feedback/summary  - Get feedback stats")
    print(f"  GET  {port}/api/feedback/article/<id> - Get article feedback")
    print()
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n✋ Feedback API server stopped")


if __name__ == "__main__":
    main()
