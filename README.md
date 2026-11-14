# WhatsApp Flask Webhook

Minimal Flask webhook for Meta WhatsApp Cloud API verification and event delivery.

## Files

- `main.py` — Flask routes: `/`, `/health`, and `/webhook`
- `verify.py` — GET verification-token validation
- `response.py` — POST signature validation and minimal event logging
- `requirements.txt` — Python dependencies
- `render.yaml` — Render Blueprint configuration

## Deploy on Render

1. Push these files to the root of a GitHub repository.
2. In Render, create a new **Blueprint** from that repository, or create a Web Service manually.
3. For a manual Web Service, use:
   - Runtime: Python
   - Build command: `pip install -r requirements.txt`
   - Start command: `gunicorn main:app`
   - Health check path: `/health`
4. Add environment variables in Render:
   - `VERIFY_TOKEN`: a secret string you choose. Enter exactly the same string in Meta.
   - `META_APP_SECRET`: your Meta App Secret. This is used to validate POST webhook signatures.
5. Deploy and copy the service's public HTTPS URL.

## Configure Meta

- Callback URL: `https://YOUR-SERVICE.onrender.com/webhook`
- Verify Token: the exact value stored in `VERIFY_TOKEN`
- Subscribe to the WhatsApp webhook fields you need, such as `messages`.

Meta sends a GET request for verification. The app checks `hub.mode`, `hub.verify_token`, and `hub.challenge`. On success it returns the challenge as plain text with HTTP 200.

After verification, Meta sends POST requests to the same path. When `META_APP_SECRET` is configured, the app validates `X-Hub-Signature-256` before accepting the event.

## Test after deployment

- Open `https://YOUR-SERVICE.onrender.com/` — should return service status JSON.
- Open `https://YOUR-SERVICE.onrender.com/health` — should return `{"status":"ok"}`.
- Meta performs the actual signed verification handshake through its dashboard.

Do not put secrets in source code or commit `.env` files. Set them in Render's Environment settings.

## Important notes

- `VERIFY_TOKEN` is a value you create; it is not your Meta access token.
- `META_APP_SECRET` is the App Secret from your Meta app settings; it is not the WhatsApp access token.
- If `META_APP_SECRET` is missing, GET verification still works, but POST signature validation is disabled and a warning is logged. Configure it before production use.
- This starter acknowledges events with HTTP 200 and logs only basic event counts. It does not yet send WhatsApp replies, persist messages, or process business logic.
- Render free web services can spin down when idle; the first request after inactivity may be delayed. For production webhooks, use an always-on service.
