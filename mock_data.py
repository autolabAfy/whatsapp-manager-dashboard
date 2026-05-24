"""Mock data for sandbox/demo mode — no real WhatsApp or Modal connections."""

import json
import time
from datetime import datetime, timedelta, timezone

SGT = timezone(timedelta(hours=8))


def _now():
    return datetime.now(SGT)


def _iso(dt):
    return dt.isoformat()


CONTACTS = [
    {
        "phone": "6591234567",
        "name": "Sarah Chen",
        "booking_status": "Booked",
        "human_handover": False,
        "dashboard_read_at": _iso(_now() - timedelta(minutes=25)),
    },
    {
        "phone": "6598765432",
        "name": "Marcus Tan",
        "booking_status": "Enquiry",
        "human_handover": True,
        "dashboard_read_at": _iso(_now() - timedelta(hours=2)),
    },
    {
        "phone": "6587654321",
        "name": "Priya Sharma",
        "booking_status": "Confirmed",
        "human_handover": False,
        "dashboard_read_at": _iso(_now() - timedelta(days=1)),
    },
    {
        "phone": "6581112222",
        "name": "James Lim",
        "booking_status": "New",
        "human_handover": False,
        "dashboard_read_at": None,
    },
    {
        "phone": "6592223333",
        "name": "Rachel Wong",
        "booking_status": "Interested",
        "human_handover": False,
        "dashboard_read_at": None,
    },
    {
        "phone": "6583334444",
        "name": "David Koh",
        "booking_status": "Follow-up",
        "human_handover": True,
        "dashboard_read_at": _iso(_now() - timedelta(hours=3)),
    },
    {
        "phone": "6594445555",
        "name": "Michelle Ng",
        "booking_status": "New",
        "human_handover": False,
        "dashboard_read_at": None,
    },
]

IMG_UNICORN = {
    "type": "image",
    "url": "/static/demo-media/unicorn-cake.jpg",
    "thumb_url": "/static/demo-media/unicorn-cake-thumb.jpg",
    "mime": "image/jpeg",
    "width": 800,
    "height": 600,
}
IMG_CUPCAKES = {
    "type": "image",
    "url": "/static/demo-media/cupcakes.jpg",
    "thumb_url": "/static/demo-media/cupcakes-thumb.jpg",
    "mime": "image/jpeg",
    "width": 800,
    "height": 600,
}
DOC_MENU = {
    "type": "document",
    "url": "/static/demo-media/chens-bakery-menu.pdf",
    "filename": "Chens-Bakery-Spring-Menu.pdf",
    "mime": "application/pdf",
    "size": 2131,
    "pages": 1,
}
VOICE_DAVID = {
    "type": "voice",
    "url": "/static/demo-media/voice-david.ogg",
    "mime": "audio/ogg",
    "duration": 3,
}
VOICE_BOT = {
    "type": "voice",
    "url": "/static/demo-media/voice-bot.ogg",
    "mime": "audio/ogg",
    "duration": 5,
}
VID_CAKE = {
    "type": "video",
    "url": "/static/demo-media/cake-demo.mp4",
    "mime": "video/mp4",
    "duration": 4,
    "width": 480,
    "height": 854,
}

CONVERSATIONS = {
    "6591234567@c.us": [
        {"role": "user", "content": "Hi, I saw your bakery on Instagram. Do you take custom cake orders?", "mins_ago": 120},
        {"role": "assistant", "content": "Hey Sarah! Welcome to Chen's Bakery! Yes, we do custom cakes for all occasions — birthdays, weddings, corporate events.\n\nWhat kind of cake are you looking for?", "mins_ago": 119},
        {"role": "user", "content": "I need a birthday cake for my daughter. She loves unicorns! Here's the reference she picked:", "mins_ago": 60},
        {"role": "user", "content": "", "mins_ago": 60, "media": IMG_UNICORN},
        {"role": "assistant", "content": "Absolutely! Our unicorn cakes are super popular 🦄\n\n🎂 8-inch (serves 12–15) — $88\n🎂 2-tier (serves 20–25) — $128\n\nAll come with fondant unicorn topper, rainbow buttercream, and edible glitter.\n\nWhen is the birthday?", "mins_ago": 59},
        {"role": "user", "content": "This Saturday! The 8-inch please. Can I do vanilla sponge?", "mins_ago": 28},
        {"role": "assistant", "content": "✅ 8-inch Unicorn Cake — Vanilla Sponge\n📅 Ready by Saturday 22 March\n💰 $88\n\nA $30 deposit locks in the slot — PayNow or cash on collection works!", "mins_ago": 27},
    ],
    "6598765432@c.us": [
        {"role": "user", "content": "Do you deliver to Jurong West?", "mins_ago": 300},
        {"role": "assistant", "content": "Hi Marcus! Yes, island-wide delivery:\n\n🚗 Central — $10\n🚗 East/West — $15\n🚗 North/Jurong — $18\n\nWhat would you like to order?", "mins_ago": 299},
        {"role": "user", "content": "Got a menu I can share with my team?", "mins_ago": 200},
        {"role": "assistant", "content": "[HUMAN] Sure — here's our Spring 2026 menu 📎", "mins_ago": 199},
        {"role": "assistant", "content": "", "mins_ago": 199, "media": DOC_MENU},
        {"role": "user", "content": "2 dozen cupcakes for our office. Mix of red velvet, matcha, and salted caramel?", "mins_ago": 180},
        {"role": "assistant", "content": "Great mix! 2 dozen (24 pcs) at $72 + $18 delivery = $90 total.\n\nI'll throw in a free box upgrade for the bigger order 🎁\n\nWhen do you need them?", "mins_ago": 179},
        {"role": "user", "content": "This Friday afternoon if possible", "mins_ago": 60},
        {"role": "assistant", "content": "[HUMAN] Hey Marcus! Friday 2–5 PM works for us. Want me to confirm the order and send you the PayNow details?", "mins_ago": 10},
    ],
    "6587654321@c.us": [
        {"role": "user", "content": "Hi, looking for a 3-tier wedding cake for 150 guests in June", "mins_ago": 1500},
        {"role": "assistant", "content": "Congratulations Priya! 💐 We'd love to create your wedding cake.\n\nFor 150 guests, a 3-tier is perfect. We offer a free 30-min consultation with flavour tasting.\n\nAvailable slots this week:\n📅 Thu 20 March — 4:00 PM\n📅 Sat 22 March — 10:00 AM\n\nWhich works for you?", "mins_ago": 1499},
        {"role": "user", "content": "Thursday 4pm! Can my fiancé join too?", "mins_ago": 1450},
        {"role": "assistant", "content": "Of course — bring him along! 🎉\n\n✅ Booked: Thu 20 March, 4:00 PM\n📍 Chen's Bakery, 123 Toa Payoh Lorong 1\n\nSee you both then!", "mins_ago": 1449},
    ],
    "6581112222@c.us": [
        {"role": "user", "content": "Hi do you have gluten-free options?", "mins_ago": 15},
        {"role": "assistant", "content": "Hey James! Yes we do:\n\n🍰 Flourless Chocolate Cake — $58 (6-inch)\n🍰 Almond Orange Cake — $52 (6-inch)\n🧁 GF Cupcakes — $4.50 each\n\nAll baked separately to avoid cross-contamination. Anything catch your eye?", "mins_ago": 14},
        {"role": "user", "content": "The flourless chocolate sounds great. Can I order for next week?", "mins_ago": 3},
    ],
    "6592223333@c.us": [
        {"role": "user", "content": "Hello! I'm interested in a customised cake for a retirement party. About 40 pax.", "mins_ago": 45},
        {"role": "assistant", "content": "Hi Rachel! Happy to help plan something special 🎂\n\nFor 40 guests, a 2-tier cake would be ideal ($108–$148 depending on design).\n\nWhat's the theme or colour palette you have in mind?", "mins_ago": 44},
        {"role": "user", "content": "Something elegant — gold and white. She loves roses.", "mins_ago": 20},
        {"role": "assistant", "content": "Gorgeous choice! Gold & white with sugar roses is very popular for milestone events.\n\nI can put together a design quote — what's the date of the party?", "mins_ago": 19},
        {"role": "user", "content": "April 5th. Is that enough lead time?", "mins_ago": 5},
    ],
    "6583334444@c.us": [
        {"role": "user", "content": "Hey, I ordered a cake last week — order #2841. Can I change the pickup time?", "mins_ago": 200},
        {"role": "assistant", "content": "Hi David! Let me pull up order #2841 for you.\n\nYour current pickup is Saturday 22 March at 11 AM. What time works better?", "mins_ago": 199},
        {"role": "user", "content": "", "mins_ago": 181, "media": VOICE_DAVID},
        {"role": "user", "content": "Can we do 2pm instead?", "mins_ago": 180},
        {"role": "assistant", "content": "", "mins_ago": 176, "media": VOICE_BOT},
        {"role": "assistant", "content": "[HUMAN] Hi David! 2 PM on Saturday is fine — I've updated your order. See you then! 😊", "mins_ago": 175},
    ],
    "6594445555@c.us": [
        {"role": "user", "content": "Hi! Do you do corporate gifting? Like cupcake boxes for clients?", "mins_ago": 8},
        {"role": "assistant", "content": "Hi Michelle! Yes, corporate gifting is one of our specialties 🎁\n\nWe do branded cupcake boxes (4, 6, or 12 pcs) with your logo printed on the box and cupcake toppers.\n\nMinimum order 10 boxes. Do you have a quantity and date in mind?", "mins_ago": 7},
        {"role": "assistant", "content": "", "mins_ago": 7, "media": IMG_CUPCAKES},
        {"role": "user", "content": "Wow that sounds perfect. We need about 30 boxes for an event on March 28.", "mins_ago": 2},
        {"role": "user", "content": "Quick video of our office setup so you know the vibe:", "mins_ago": 1},
        {"role": "user", "content": "", "mins_ago": 1, "media": VID_CAKE},
    ],
}


def _build_messages(chat_id):
    raw = CONVERSATIONS.get(chat_id, [])
    now = _now()
    result = []
    for i, m in enumerate(raw):
        ts = now - timedelta(minutes=m["mins_ago"])
        entry = {
            "id": f"mock-{chat_id}-{i}",
            "role": m["role"],
            "content": m["content"],
            "created_at": _iso(ts),
        }
        if m.get("media"):
            entry["media"] = m["media"]
        result.append(entry)
    return result


def get_conversations():
    convos = []
    for c in CONTACTS:
        chat_id = f"{c['phone']}@c.us"
        msgs = _build_messages(chat_id)
        last_msg = msgs[-1] if msgs else None

        unread = 0
        read_at = c.get("dashboard_read_at")
        for m in msgs:
            if m["role"] == "user":
                if not read_at or m["created_at"] > read_at:
                    unread += 1

        preview = ""
        if last_msg:
            content = last_msg["content"]
            preview = content[:100] if isinstance(content, str) else ""

        convos.append({
            "chat_id": chat_id,
            "phone": c["phone"],
            "name": c.get("name") or c["phone"],
            "business_name": c.get("business_name"),
            "booking_status": c.get("booking_status"),
            "human_handover": bool(c.get("human_handover")),
            "last_message": {
                "role": last_msg["role"] if last_msg else None,
                "preview": preview,
                "created_at": last_msg["created_at"] if last_msg else None,
            },
            "unread": unread,
        })

    convos.sort(key=lambda c: c["last_message"]["created_at"] or "", reverse=True)
    return {"conversations": convos}


def get_messages(chat_id, since=None):
    msgs = _build_messages(chat_id)
    result = []
    for m in msgs:
        if since and m.get("created_at", "") <= since:
            continue
        entry = {
            "id": m["id"],
            "role": m["role"],
            "content": m["content"],
            "raw_content": m["content"],
            "created_at": m["created_at"],
        }
        if m.get("media"):
            entry["media"] = m["media"]
        result.append(entry)
    return {"messages": result, "chat_id": chat_id}


def send_media(chat_id, media_type, filename, mime, size, caption="", data_url=None):
    """Append a sent-media message to the mock conversation. Used by sandbox proxies."""
    if chat_id not in CONVERSATIONS:
        CONVERSATIONS[chat_id] = []
    media = {
        "type": media_type,
        "url": data_url or f"/static/demo-media/{filename}",
        "mime": mime,
        "filename": filename,
        "size": size,
    }
    CONVERSATIONS[chat_id].append({
        "role": "assistant",
        "content": f"[HUMAN] {caption}" if caption else "",
        "mins_ago": 0,
        "media": media,
    })
    return {"status": "sent (sandbox)", "media": media}


def send_message(chat_id, text):
    if chat_id not in CONVERSATIONS:
        CONVERSATIONS[chat_id] = []
    CONVERSATIONS[chat_id].append({
        "role": "assistant",
        "content": f"[HUMAN] {text}",
        "mins_ago": 0,
    })
    return {"status": "sent (sandbox)", "result": {"idMessage": "mock-sent"}}


def toggle_mode(chat_id, human_mode):
    phone = chat_id.replace("@c.us", "")
    for c in CONTACTS:
        if c["phone"] == phone:
            c["human_handover"] = human_mode
            break
    return {"status": "ok", "human_handover": human_mode, "chat_id": chat_id}


def mark_read(chat_id):
    phone = chat_id.replace("@c.us", "")
    now = _iso(_now())
    for c in CONTACTS:
        if c["phone"] == phone:
            c["dashboard_read_at"] = now
            break
    return {"status": "ok", "dashboard_read_at": now}
