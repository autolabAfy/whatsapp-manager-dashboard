# Zeus WhatsApp Manager — Client PWA

A Flask-based mobile-first PWA for clients to monitor and manage their WhatsApp AI bot conversations. Proxies API calls to a Modal backend.

## Architecture

- **Backend**: Flask + Gunicorn (port 5000), Python 3.11
- **Frontend**: Server-rendered HTML/CSS/JS, mobile-first PWA with service worker
- **Live backend**: `https://affy--zeus-whatsapp-web.modal.run`
- **Mock mode**: `SANDBOX_MODE=true` uses `mock_data.py` for development

## Key Files

| File | Purpose |
|------|---------|
| `app.py` | Flask app, auth, API proxy routes, hide-chat logic |
| `templates/inbox.html` | Conversation list with swipe-to-delete, FAB, SSE |
| `templates/chat.html` | Chat view with mode toggle, real-time messages, delete button |
| `templates/login.html` | Login page |
| `static/style.css` | All styles (dark WhatsApp theme, mobile-first) |
| `static/sw.js` | Service worker (PWA offline support) |
| `mock_data.py` | Mock conversations/messages for sandbox mode |
| `data/hidden_<client>.json` | Per-client hidden conversation list (auto-created) |
| `scripts/post-merge.sh` | Post-merge setup: runs `pip install -r requirements.txt` |

## Client Configuration

Clients are loaded from environment variables:
- `CLIENT_<ID>_PASSWORD` — triggers client registration
- `CLIENT_<ID>_URL` — Modal backend URL
- `CLIENT_<ID>_APIKEY` — API key for Modal
- `CLIENT_<ID>_BUSINESS` — Business display name
- `CLIENT_<ID>_BOTNAME` — Bot display name
- `CLIENT_<ID>_COLOR` — Accent color (hex)

Current clients: `demo` (loaded from `CLIENT_DEMO_*` env vars)

## Features

- Real-time updates via SSE (`/api/events`) with 8s polling fallback
- AI / Human mode toggle per conversation (calls Modal backend)
- Swipe-left on inbox rows to reveal red Delete button
- Delete button in chat header (trash icon)
- Hidden conversations persisted per client in `data/hidden_<id>.json`
- New conversation flow via FAB → phone number modal → chat page (auto-enables human mode)
- Pull-to-refresh, search, tab filters (All / AI / Human)
- PWA: installable on iOS/Android via "Add to Home Screen"

## Login

- Client ID: `demo`
- Password: `demo123`

## Important Notes

- Do NOT hardcode `demo` in `CLIENTS` dict — it must load from env vars
- Modal backend does not support DELETE (returns 404) — delete is Flask-side only
- SSE proxy uses `iter_raw()` not `iter_lines()` to preserve `\n\n` separators
- Port 5000 conflict fix: `fuser -k 5000/tcp`
