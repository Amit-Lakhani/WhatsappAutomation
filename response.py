
import hashlib
import hmac
import logging

logger = logging.getLogger(__name__)


def validate_meta_signature(raw_body, signature_header, app_secret):
    """Validate Meta's X-Hub-Signature-256 header."""

    if not app_secret or not signature_header:
        return False

    digest = hmac.new(
        app_secret.encode("utf-8"),
        raw_body,
        hashlib.sha256
    ).hexdigest()

    expected_signature = f"sha256={digest}"

    return hmac.compare_digest(
        signature_header,
        expected_signature
    )


def log_incoming_message(message):
    """Extract and log incoming WhatsApp message details."""

    sender = message.get("from", "unknown")
    message_id = message.get("id", "unknown")
    message_type = message.get("type", "unknown")
    timestamp = message.get("timestamp", "unknown")

    if message_type == "text":
        content = message.get("text", {}).get("body", "")

    elif message_type == "button":
        button = message.get("button", {})
        content = button.get("text") or button.get("payload", "")

    elif message_type == "interactive":
        interactive = message.get("interactive", {})
        reply = (
            interactive.get("button_reply")
            or interactive.get("list_reply")
            or {}
        )
        content = reply.get("title") or reply.get("id", "")

    else:
        content = message.get(
            message_type, {}
        ).get("caption", "")

    logger.info("========== INCOMING WHATSAPP MESSAGE ==========")
    logger.info("From: %s", sender)
    logger.info("Type: %s", message_type)
    logger.info("Message: %s", content or f"[{message_type} message]")
    logger.info("Message ID: %s", message_id)
    logger.info("Timestamp: %s", timestamp)
    logger.info("================================================")


def log_message_status(status):
    """Log sent, delivered, read or failed status updates."""

    logger.info(
        "WHATSAPP STATUS UPDATE | Status: %s | Recipient: %s | Message ID: %s",
        status.get("status", "unknown"),
        status.get("recipient_id", "unknown"),
        status.get("id", "unknown")
    )


def process_webhook_event(payload):
    """Process incoming WhatsApp messages and status notifications."""

    entries = payload.get("entry", [])

    if not isinstance(entries, list):
        logger.warning("Invalid webhook entry format")
        return

    for entry in entries:

        if not isinstance(entry, dict):
            continue

        changes = entry.get("changes", [])

        if not isinstance(changes, list):
            continue

        for change in changes:

            if not isinstance(change, dict):
                continue

            field = change.get("field", "unknown")
            value = change.get("value", {})

            if not isinstance(value, dict):
                continue

            if field != "messages":
                logger.info("Received webhook field: %s", field)
                continue

            # Process incoming messages
            messages = value.get("messages", [])

            if isinstance(messages, list):
                for message in messages:
                    if isinstance(message, dict):
                        log_incoming_message(message)

            # Process message status notifications
            statuses = value.get("statuses", [])

            if isinstance(statuses, list):
                for status in statuses:
                    if isinstance(status, dict):
                        log_message_status(status)
