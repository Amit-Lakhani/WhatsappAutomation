import hmac
import logging

logger = logging.getLogger(__name__)


def verify_webhook(query_params, expected_token):
    """
    Validate Meta's GET webhook verification request.

    Returns (response_body, HTTP_status).
    Meta expects the hub.challenge value as plain text on success.
    """
    mode = query_params.get("hub.mode", "")
    supplied_token = query_params.get("hub.verify_token", "")
    challenge = query_params.get("hub.challenge", "")

    if not expected_token:
        logger.error("VERIFY_TOKEN environment variable is not configured")
        return "Webhook verification token is not configured", 500

    if mode == "subscribe" and challenge and hmac.compare_digest(
        supplied_token, expected_token
    ):
        logger.info("Webhook verification successful")
        return challenge, 200

    logger.warning("Webhook verification rejected")
    return "Forbidden", 403
