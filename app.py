"""Zeus Client App — Mobile PWA for clients to manage their WhatsApp AI bot.

Each client gets credentials (client_id + password) that map to their
Modal backend instance. The app proxies all API calls to the correct
Modal URL using the client's API key.

Deploy on Replit. Set these env vars:
    SECRET_KEY        = (random string for Flask sessions)
    SANDBOX_MODE      = true  (use mock data, no real WhatsApp/Modal)

Client config is stored in CLIENTS dict (or loaded from env/Supabase).
"""

import os
import json
import time
import pathlib
from functools import wraps
from datetime import datetime
from urllib.parse import unquote

import httpx
from flask import (
    Flask, render_template, request, redirect, url_for,
    session, jsonify, Response, stream_with_context,
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "zeus-client-secret-change-me")

SANDBOX = os.environ.get("SANDBOX_MODE", "true").lower() in ("true", "1", "yes")

# Per-client hidden chat lists stored in data/hidden_<client_id>.json
DATA_DIR = pathlib.Path("data")
DATA_DIR.mkdir(exist_ok=True)


def _hidden_file(client_id: str) -> pathlib.Path:
    return DATA_DIR / f"hidden_{client_id}.json"


def get_hidden_chats(client_id: str) -> set:
    p = _hidden_file(client_id)
    if not p.exists():
        return set()
    try:
        return set(json.loads(p.read_text()))
    except Exception:
        return set()


def hide_chat(client_id: str, chat_id: str) -> None:
    hidden = get_hidden_chats(client_id)
    hidden.add(chat_id)
    p = _hidden_file(client_id)
    tmp = p.with_suffix(".tmp")
    tmp.write_text(json.dumps(list(hidden)))
    os.replace(tmp, p)


# ---------------------------------------------------------------------------
# Client registry — each client has their own Modal backend + credentials
# In production, load from Supabase or env vars.
# ---------------------------------------------------------------------------
CLIENTS = {
    # Add more clients here:
    # "chens-bakery": {
    #     "password": "securepass",
    #     "business_name": "Chen's Bakery",
    #     "bot_name": "Bakery Bot",
    #     "modal_url": "https://affy--zeus-whatsapp-chens-web.modal.run",
    #     "api_key": os.environ.get("CHENS_API_KEY", ""),
    #     "accent_color": "#e88c3a",
    # },
}

# Load additional clients from env (CLIENT_<id>_PASSWORD, CLIENT_<id>_URL, etc.)
for key in os.environ:
    if key.startswith("CLIENT_") and key.endswith("_PASSWORD"):
        cid = key.replace("CLIENT_", "").replace("_PASSWORD", "").lower()
        if cid not in CLIENTS:
            CLIENTS[cid] = {
                "password": os.environ[key],
                "business_name": os.environ.get(f"CLIENT_{cid.upper()}_BUSINESS", cid.title()),
                "bot_name": os.environ.get(f"CLIENT_{cid.upper()}_BOTNAME", "AI Assistant"),
                "modal_url": os.environ.get(f"CLIENT_{cid.upper()}_URL", ""),
                "api_key": os.environ.get(f"CLIENT_{cid.upper()}_APIKEY", ""),
                "accent_color": os.environ.get(f"CLIENT_{cid.upper()}_COLOR", "#00a884"),
            }

if SANDBOX:
    import mock_data
    CLIENTS.setdefault("demo", {
        "password": "demo123",
        "business_name": "Demo Business",
        "bot_name": "Demo Bot",
        "modal_url": "",
        "api_key": "",
        "accent_color": "#00a884",
    })


def get_client_config():
    """Get the logged-in client's config."""
    cid = session.get("client_id")
    return CLIENTS.get(cid, {})


def api_headers():
    cfg = get_client_config()
    return {"X-Dashboard-Key": cfg.get("api_key", ""), "Content-Type": "application/json"}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("logged_in") or not session.get("client_id"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


# ---------------------------------------------------------------------------
# Auth
# ---------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        client_id = request.form.get("client_id", "").strip().lower()
        password = request.form.get("password", "")
        client = CLIENTS.get(client_id)

        if client and client["password"] == password:
            session["logged_in"] = True
            session["client_id"] = client_id
            return redirect(url_for("inbox"))
        error = "Invalid credentials"

    return render_template("login.html", error=error, sandbox=SANDBOX)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------------------------------------------------------------------------
# Pages
# ---------------------------------------------------------------------------

@app.route("/")
@login_required
def inbox():
    cfg = get_client_config()
    return render_template("inbox.html",
                           sandbox=SANDBOX,
                           business_name=cfg.get("business_name", "Dashboard"),
                           bot_name=cfg.get("bot_name", "AI Assistant"),
                           accent=cfg.get("accent_color", "#00a884"))


@app.route("/chat/<path:chat_id>")
@login_required
def chat(chat_id):
    cfg = get_client_config()
    return render_template("chat.html",
                           chat_id=chat_id,
                           sandbox=SANDBOX,
                           business_name=cfg.get("business_name", "Dashboard"),
                           bot_name=cfg.get("bot_name", "AI Assistant"),
                           accent=cfg.get("accent_color", "#00a884"))


# ---------------------------------------------------------------------------
# API — sandbox mode uses mock_data, live mode proxies to client's Modal
# ---------------------------------------------------------------------------

@app.route("/api/conversations")
@login_required
def proxy_conversations():
    cid = session.get("client_id")
    hidden = get_hidden_chats(cid)

    if SANDBOX:
        data = mock_data.get_conversations()
        if hidden and "conversations" in data:
            data["conversations"] = [c for c in data["conversations"] if c["chat_id"] not in hidden]
        return jsonify(data)

    cfg = get_client_config()
    try:
        with httpx.Client(timeout=30) as client:
            r = client.get(f"{cfg['modal_url']}/api/conversations", headers=api_headers())
            data = r.json()
            if hidden and "conversations" in data:
                data["conversations"] = [c for c in data["conversations"] if c["chat_id"] not in hidden]
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversations/<path:chat_id>", methods=["DELETE"])
@login_required
def hide_conversation(chat_id):
    chat_id = unquote(chat_id)
    cid = session.get("client_id")
    hide_chat(cid, chat_id)
    return jsonify({"ok": True, "hidden": chat_id})


@app.route("/api/conversations/<path:chat_id>/messages")
@login_required
def proxy_messages(chat_id):
    chat_id = unquote(chat_id)
    since = request.args.get("since")
    if SANDBOX:
        return jsonify(mock_data.get_messages(chat_id, since=since))
    cfg = get_client_config()
    try:
        limit = request.args.get("limit", "50")
        offset = request.args.get("offset", "0")
        params = {"limit": limit, "offset": offset}
        if since:
            params["since"] = since
        with httpx.Client(timeout=30) as client:
            r = client.get(
                f"{cfg['modal_url']}/api/conversations/{chat_id}/messages",
                headers=api_headers(),
                params=params,
            )
            data = r.json()
            if since and isinstance(data.get("messages"), list):
                data["messages"] = [m for m in data["messages"] if m.get("created_at", "") > since]
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversations/<path:chat_id>/send", methods=["POST"])
@login_required
def proxy_send(chat_id):
    chat_id = unquote(chat_id)
    if SANDBOX:
        text = request.json.get("text", "")
        return jsonify(mock_data.send_message(chat_id, text))
    cfg = get_client_config()
    try:
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"{cfg['modal_url']}/api/conversations/{chat_id}/send",
                headers=api_headers(),
                json=request.json,
            )
            try:
                data = r.json()
            except Exception:
                data = {"error": "Send failed", "detail": r.text[:300]}
            return jsonify(data), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Media upload size cap (50MB — WhatsApp's outbound media limit is 100MB but most
# real-world voice/photo/doc is under 10MB; cap at 50 to stay safe)
app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024


@app.route("/api/conversations/<path:chat_id>/send-image", methods=["POST"])
@app.route("/api/conversations/<path:chat_id>/send-video", methods=["POST"])
@app.route("/api/conversations/<path:chat_id>/send-document", methods=["POST"])
@app.route("/api/conversations/<path:chat_id>/send-voice", methods=["POST"])
@app.route("/api/conversations/<path:chat_id>/send-audio", methods=["POST"])
@login_required
def proxy_send_media(chat_id):
    """Multipart media send. Sandbox stores file under /static/uploads; live mode
    streams the file to the Modal bot's matching endpoint."""
    chat_id = unquote(chat_id)
    # Derive media type from URL path
    media_type = request.path.rstrip("/").rsplit("-", 1)[-1]  # image / video / document / voice / audio
    f = request.files.get("file")
    caption = request.form.get("caption", "")
    if not f:
        return jsonify({"error": "missing file"}), 400

    if SANDBOX:
        cid = session["client_id"]
        upload_dir = pathlib.Path("static") / "uploads" / cid
        upload_dir.mkdir(parents=True, exist_ok=True)
        # Sanitize filename
        safe_name = pathlib.Path(f.filename or f"upload-{int(time.time())}").name
        target = upload_dir / f"{int(time.time()*1000)}-{safe_name}"
        f.save(target)
        public_url = f"/static/uploads/{cid}/{target.name}"
        size = target.stat().st_size
        result = mock_data.send_media(
            chat_id, media_type, safe_name, f.mimetype or "application/octet-stream",
            size, caption=caption, data_url=public_url,
        )
        return jsonify(result)

    cfg = get_client_config()
    try:
        with httpx.Client(timeout=120) as client:
            files = {"file": (f.filename, f.stream, f.mimetype or "application/octet-stream")}
            data = {"caption": caption} if caption else {}
            r = client.post(
                f"{cfg['modal_url']}/api/conversations/{chat_id}/send-{media_type}",
                headers={"X-Dashboard-Key": cfg.get("api_key", "")},
                files=files,
                data=data,
            )
            try:
                return jsonify(r.json()), r.status_code
            except Exception:
                return jsonify({"error": "Send failed", "detail": r.text[:300]}), r.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversations/<path:chat_id>/mode", methods=["POST"])
@login_required
def proxy_mode(chat_id):
    chat_id = unquote(chat_id)
    if SANDBOX:
        human_mode = request.json.get("human_mode", False)
        return jsonify(mock_data.toggle_mode(chat_id, human_mode))
    cfg = get_client_config()
    try:
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"{cfg['modal_url']}/api/conversations/{chat_id}/mode",
                headers=api_headers(),
                json=request.json,
            )
            return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/conversations/<path:chat_id>/read", methods=["POST"])
@login_required
def proxy_read(chat_id):
    chat_id = unquote(chat_id)
    if SANDBOX:
        return jsonify(mock_data.mark_read(chat_id))
    cfg = get_client_config()
    try:
        with httpx.Client(timeout=30) as client:
            r = client.post(
                f"{cfg['modal_url']}/api/conversations/{chat_id}/read",
                headers=api_headers(),
                json={},
            )
            return jsonify(r.json())
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/events")
@login_required
def proxy_events():
    """SSE stream — sandbox sends keepalives, live proxies from Modal."""
    if SANDBOX:
        def sandbox_stream():
            while True:
                yield ": keepalive\n\n"
                time.sleep(5)

        return Response(
            stream_with_context(sandbox_stream()),
            content_type="text/event-stream",
            headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
        )

    cfg = get_client_config()

    def generate():
        try:
            with httpx.Client(timeout=None) as client:
                with client.stream(
                    "GET",
                    f"{cfg['modal_url']}/api/events",
                    headers=api_headers(),
                ) as r:
                    for chunk in r.iter_raw():
                        yield chunk
        except Exception as e:
            yield f"event: error\ndata: {json.dumps({'error': str(e)})}\n\n"

    return Response(
        stream_with_context(generate()),
        content_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


# ---------------------------------------------------------------------------
# PWA
# ---------------------------------------------------------------------------

@app.route("/manifest.json")
def manifest():
    cfg = get_client_config() if session.get("logged_in") else {}
    accent = cfg.get("accent_color", "#00a884")
    name = cfg.get("business_name", "Zeus Client")

    return jsonify({
        "name": f"{name} — WhatsApp Manager",
        "short_name": name,
        "start_url": "/",
        "display": "standalone",
        "background_color": "#0b141a",
        "theme_color": accent,
        "orientation": "portrait",
        "icons": [
            {"src": "/static/icon-192.png", "sizes": "192x192", "type": "image/png"},
            {"src": "/static/icon-512.png", "sizes": "512x512", "type": "image/png"},
        ],
    })


@app.route("/sw.js")
def service_worker():
    return app.send_static_file("sw.js"), 200, {"Content-Type": "application/javascript"}


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)
