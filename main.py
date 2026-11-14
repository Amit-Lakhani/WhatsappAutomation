import logging
import os

from flask import Flask, jsonify, request

from verify import verify_webhook
from response import process_webhook_event, validate_meta_signature

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO").upper(),
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

app = Flask(__name__)


@app.get("/")
def index():
    return jsonify({
        "service": "WhatsApp webhook",
        "status": "running",
        "endpoints": {
            "verification": "GET /webhook",
            "events": "POST /webhook",
            "health": "GET /health",
        },
    }), 200


@app.get("/health")
def health():
    return jsonify({"status": "ok"}), 200


@app.get("/webhook")
def webhook_verification():
    """Meta webhook verification handshake."""
    verify_token = os.getenv("VERIFY_TOKEN", "")
    result, status_code = verify_webhook(request.args, verify_token)
    return result, status_code, {"Content-Type": "text/plain; charset=utf-8"}


@app.post("/webhook")
def webhook_events():
    """Receive WhatsApp webhook event notifications from Meta."""
    app_secret = os.getenv("META_APP_SECRET", "")
    raw_body = request.get_data(cache=True)

    # Signature verification is enforced whenever META_APP_SECRET is configured.
    # Configure this environment variable before using the endpoint in production.
    if app_secret and not validate_meta_signature(
        raw_body,
        request.headers.get("X-Hub-Signature-256", ""),
        app_secret,
    ):
        logger.warning("Rejected webhook: invalid X-Hub-Signature-256")
        return jsonify({"error": "Invalid signature"}), 403

    if not app_secret:
        logger.warning(
            "META_APP_SECRET is not configured; POST signature validation is disabled."
        )

    try:
        payload = request.get_json(silent=False)
    except Exception:
        return jsonify({"error": "Request body must contain valid JSON"}), 400

    if not isinstance(payload, dict):
        return jsonify({"error": "Expected a JSON object"}), 400

    process_webhook_event(payload)
    return jsonify({"status": "received"}), 200


if __name__ == "__main__":
    # Local development only. Render runs the app with Gunicorn.
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")), debug=False)
