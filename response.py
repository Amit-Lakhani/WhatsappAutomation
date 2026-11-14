import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)


def validate_meta_signature(raw_body, signature_header, app_secret):
    """
    Validate Meta's X-Hub-Signature-256 header.

    The expected format is: sha256=<hex digest>
    """
    if not app_secret or not signature_header:
        return False

    expected_digest = hmac.new(
        app_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256,
    ).hexdigest()

    expected_signature = f"sha256={expected_digest}"
    return hmac.compare_digest(signature_header, expected_signature)


def process_webhook_event(payload):
    """
    Minimal event handler.

    Logs the event structure without logging message text, phone numbers,
    access tokens, or other potentially sensitive customer data.
    Extend this function when you are ready to process messages.
    """
    object_type = payload.get("object", "unknown")
    entries = payload.get("entry", [])
    change_count = sum(
        len(entry.get("changes", []))
        for entry in entries
        if isinstance(entry, dict)
    )

    logger.info(
        "Webhook event received: object=%s entries=%d changes=%d",
        object_type,
        len(entries),
        change_count,
    )
