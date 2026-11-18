"""AI cruise finder for The Cruise Detective's comparison pages (same design as budapestadventures.com).

GET /api/cruise-finder?page=seine-river-cruises-paris&q=romantic+under+30

Reads the cards and the author's reviews from the page's own HTML (bundled with the function)
plus guest-review themes from api/_knowledge/<page>.json. Answers questions in 2-3 sentences
("kind": "question") or matches a wish ("preference"), and returns card ids plus a one-line reason. Prices and booking links always come from the page itself.
Identical questions are cached at the Vercel CDN for a day, so repeats are free.
Needs ANTHROPIC_API_KEY in the Vercel project's environment variables.
"""
import html
import json
import os
import re
import time
from http.server import BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse

import anthropic

MODEL = os.environ.get("CRUISE_FINDER_MODEL", "claude-haiku-5-5")
MAX_Q = 300
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Only these pages can be queried; value = HTML file bundled via vercel.json includeFiles.
PAGES = {
    "seine-river-cruises-paris": "seine-river-cruises-paris/index.html",
}
# What the finder is comparing on each page (goes into the prompt).
PAGE_TOPIC = {
    "seine-river-cruises-paris": "a Paris Seine sightseeing cruise comparison page",
}

_cards_cache = {}
_client = None

# Abuse limits, so a bot can't run up Anthropic costs. Counters live in the function instance's memory
# (Fluid Compute reuses instances), on top of the CDN cache that serves repeated questions for free.
# The hard money cap is the monthly spend limit set in the Anthropic Console.
PER_IP_MINUTE = int(os.environ.get("CRUISE_FINDER_IP_PER_MIN", "10"))
PER_IP_DAY = int(os.environ.get("CRUISE_FINDER_IP_PER_DAY", "80"))
INSTANCE_DAY = int(os.environ.get("CRUISE_FINDER_DAILY_CAP", "1500"))
ALLOWED_HOSTS = re.compile(r"^(www\.)?thecruisedetective\.com$|^cruisedetective[a-z0-9-]*\.vercel\.app$|^localhost(:\d+)?$|^127\.0\.0\.1(:\d+)?$")
_hits = {}          # ip -> list of request times in the last 24 h
_day = {"date": "", "n": 0}


def over_limit(ip):
    """True if this IP or this instance has used up its allowance."""
    now = time.time()
    today = time.strftime("%Y-%m-%d", time.gmtime(now))
    if _day["date"] != today:
        _day["date"], _day["n"] = today, 0
        _hits.clear()
    if _day["n"] >= INSTANCE_DAY:
        return True
    times = [t for t in _hits.get(ip, []) if now - t < 86400]
    if len(times) >= PER_IP_DAY or sum(1 for t in times if now - t < 60) >= PER_IP_MINUTE:
        _hits[ip] = times
        return True
    times.append(now)
    _hits[ip] = times
    _day["n"] += 1
    if len(_hits) > 20000:  # keep memory bounded
        _hits.clear()
    return False


BOT_UA = re.compile(r"bot|crawl|spider|slurp|scrapy|curl|wget|python|httpx|aiohttp|go-http|node-fetch|undici|axios|okhttp|"
                    r"java/|libwww|postman|insomnia|headless|phantom|puppeteer|playwright|selenium|^$", re.I)


def looks_like_a_person(headers):
    """The page's own fetch from a real browser. Scripts and crawlers fail at least one of these checks;
    no browser a visitor uses does (older Safari without Sec-Fetch still sends Referer)."""
    ua = headers.get("User-Agent") or ""
    if BOT_UA.search(ua) or "Mozilla/" not in ua:
        return False
    if not headers.get("Accept-Language"):
        return False
    site = headers.get("Sec-Fetch-Site")
    if site is not None and site != "same-origin":
        return False
    ref = headers.get("Referer") or ""
    host = urlparse(ref).netloc.lower()
    return bool(host and ALLOWED_HOSTS.match(host))

SCHEMA = {
    "type": "object",
    "properties": {
        "kind": {"type": "string", "enum": ["question", "preference"]},
        "answer": {"type": "string"},
        "lead": {"type": "string"},
        "picks": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {"id": {"type": "string"}, "why": {"type": "string"}},
                "required": ["id", "why"],
                "additionalProperties": False,
            },
        },
    },
    "required": ["kind", "answer", "lead", "picks"],
    "additionalProperties": False,
}
KNOWLEDGE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_knowledge")


def _text(fragment):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", fragment))).strip()


def load_cards(page):
    if page in _cards_cache:
        return _cards_cache[page]
    with open(os.path.join(ROOT, PAGES[page]), encoding="utf-8") as f:
        src = f.read()
    try:
        with open(os.path.join(KNOWLEDGE_DIR, page + ".json"), encoding="utf-8") as f:
            know = json.load(f)
    except (OSError, ValueError):
        know = {"general": [], "cruises": {}}
    # the author's own detailed review of each cruise (Detailed Breakdown section)
    reviews = {}
    for m in re.finditer(r'<details class="bpa-details-card"[^>]*id="([^"]+)"', src):
        start = src.index(">", m.end()) + 1
        body = src[start: start + 60000]
        nxt = body.find('<details class="bpa-details-card"')
        reviews[m.group(1)] = _text(body[: nxt if nxt > 0 else 60000])[:1800]
    cards = []
    for chunk in re.split(r'<div class="bpa-card" ', src)[1:]:
        m = re.search(r'id="(card-\d+)"', chunk)
        if not m:
            continue
        anchor = re.search(r'class="bpa-sublink" href="#([^"]+)"', chunk)
        anchor = anchor.group(1) if anchor else ""
        # Stop at the card's review link so the long review sections don't leak in.
        end = chunk.find('class="bpa-sublink"')
        part = chunk[: end if end > 0 else 20000]
        facts = []
        for det in re.findall(r"<details[^>]*>(.*?)</details>", part, re.S):
            t = _text(det).replace("▾", "")
            if "Personally Tested" in t or "booking site" in t:
                continue
            facts.append(t[:280])
        cards.append({"id": m.group(1), "card": _text(part)[:1400], "details": facts[:6],
                      "my_review": reviews.get(anchor, ""),
                      "guests_say": know.get("cruises", {}).get(anchor, {}).get("guests_say", [])})
    _cards_cache[page] = (cards, know.get("general", []))
    return _cards_cache[page]


def build_prompt(q, cards, ctx=None, general=None, page="seine-river-cruises-paris"):
    static = (
        f"You are the cruise finder on {PAGE_TOPIC.get(page, 'a Paris cruise comparison page')}. "
        "The author rode several of the cruises below and wrote each card and review. A visitor typed something into the search box.\n\n"
        "First decide the kind:\n"
        "- question: they ask something (is it cold, can kids come, is the guide audible, is it worth it, what is included, which is better).\n"
        "- preference: they describe the cruise or experience they want.\n\n"
        "For a question, write answer: 2 or 3 short sentences that answer it directly from the data below (card facts, the author's "
        "review in my_review, what guests say in guests_say, and the general tips). When you use guests_say, say it plainly, for "
        "example 'Guests say...' or '14 of 64 recent guests mention...'. If the data does not cover it, say you don't know rather "
        "than guess. Then still pick the 1 to 3 cruises that best fit the question.\n"
        "For a preference, answer is an empty string; pick the 1 to 3 cruises that fit best, best first.\n\n"
        "Rules:\n"
        "- Use only the data below. Never invent prices, times, menus, features or guest opinions.\n"
        "- Never name or quote review websites or Facebook; say 'guests' or 'travellers'. No em dashes.\n"
        "- In answer, lead and why, call cruises by their name (for example 'the Bateaux Mouches cruise'), never by card id. "
        "You speak for the author in the first person: write 'I found' or 'when I tested it', never 'the author' or 'the data'.\n"
        "- If a card says it is not bookable now, pick it only if nothing else fits, and say so.\n"
        "- If nothing fits well, return the closest 1 or 2 and say plainly what does not match.\n"
        "- why: one sentence of at most 22 words, to the visitor, citing the concrete facts that match "
        "(price, pier, deck, guide, length, what is included).\n"
        "- lead: one short sentence summarising the recommendation.\n"
        "- Answer in the visitor's language.\n"
        "- If the request has nothing to do with Paris or Seine cruises, kind is preference, answer is empty, and return the #1 card with a short lead.\n"
        "- If the visitor mentions sunset, night, the lights, dark or a time of day, use the sunset and dark times for their date "
        "from the visitor's context, and the sailing times on the cards. Say when to board (for example 'board around 17:00 to "
        "catch the sunset'). A cruise whose sailings all end before dark, or that sails in daylight only, does not fit a night "
        "or lights request. The Eiffel Tower sparkles for 5 minutes at the start of every hour after dark.\n\n"
        f"General tips:\n{json.dumps(general or [], ensure_ascii=False)}\n\n"
        f"Cards:\n{json.dumps(cards, ensure_ascii=False)}"
    )
    dynamic = ((f"Visitor's context: {json.dumps(ctx, ensure_ascii=False)}\n\n" if ctx else "")
               + f"Visitor typed: {json.dumps(q, ensure_ascii=False)}")
    return static, dynamic


def visitor_context(params, cards):
    """Date, lighting and active filters sent by the page, trimmed to safe sizes."""
    one = lambda k, n: re.sub(r"\s+", " ", (params.get(k) or [""])[0]).strip()[:n]
    ctx = {}
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", one("date", 10)):
        ctx["cruise_date"] = one("date", 10)
    if one("light", 160):
        ctx["light_on_that_date"] = one("light", 160)
    if one("filters", 200):
        ctx["active_filters"] = one("filters", 200)
    try:
        slots = json.loads((params.get("slots") or ["{}"])[0])
        valid = {c["id"] for c in cards}
        slots = {str(k): re.sub(r"\s+", " ", str(v))[:180] for k, v in slots.items() if str(k) in valid}
        if slots:
            ctx["sailing_lights_per_card"] = slots
    except (ValueError, AttributeError):
        pass
    return ctx


def ask_claude(q, cards, ctx=None, general=None, allowed=None, page="seine-river-cruises-paris"):
    global _client
    if _client is None:
        _client = anthropic.Anthropic(max_retries=1, timeout=25.0)
    static, dynamic = build_prompt(q, cards, ctx, general, page)
    if allowed:
        dynamic = (f"The visitor's filters leave only these cruises on screen; pick only from them: {json.dumps(sorted(allowed))}\n\n"
                   + dynamic)
    t0 = time.time()
    response = _client.messages.create(
        model=MODEL,
        max_tokens=700,
        # Speed: no thinking step (allowed on Haiku 5.5 at effort low). The card data is an identical prefix
        # on every call, so the prompt cache serves it; filters only change the small dynamic part.
        thinking={"type": "disabled"},
        output_config={"effort": "low", "format": {"type": "json_schema", "schema": SCHEMA}},
        messages=[{"role": "user", "content": [
            {"type": "text", "text": static, "cache_control": {"type": "ephemeral"}},
            {"type": "text", "text": dynamic},
        ]}],
    )
    if response.stop_reason == "refusal":
        raise ValueError("refused")
    text = next(b.text for b in response.content if b.type == "text")
    data = json.loads(text)
    valid = set(allowed) if allowed else {c["id"] for c in cards}
    picks = []
    for p in data.get("picks", []):
        pid = str(p.get("id", ""))
        if pid in valid and pid not in {x["id"] for x in picks}:
            picks.append({"id": pid, "why": str(p.get("why", ""))[:220].replace("\u2014", ",")})
    if not picks:
        raise ValueError("no valid picks")
    kind = "question" if data.get("kind") == "question" else "preference"
    answer = str(data.get("answer", ""))[:600].replace("\u2014", ",") if kind == "question" else ""
    u = response.usage
    print(json.dumps({"finder_log": {"q": q, "kind": kind, "picks": [p["id"] for p in picks], "ms": int((time.time() - t0) * 1000),
                                     "in": u.input_tokens, "cache_read": getattr(u, "cache_read_input_tokens", 0) or 0,
                                     "cache_write": getattr(u, "cache_creation_input_tokens", 0) or 0, "out": u.output_tokens}}, ensure_ascii=False))
    return {"kind": kind, "answer": answer, "lead": str(data.get("lead", ""))[:220].replace("\u2014", ","), "picks": picks[:3]}


class handler(BaseHTTPRequestHandler):
    def _send(self, status, payload, cache=False):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "public, max-age=0, s-maxage=86400" if cache else "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        params = parse_qs(urlparse(self.path).query)
        page = (params.get("page") or [""])[0]
        q = re.sub(r"\s+", " ", (params.get("q") or [""])[0]).strip().lower()[:MAX_Q]
        if page not in PAGES:
            return self._send(400, {"error": "unknown_page"})
        if len(q) < 2:
            return self._send(400, {"error": "empty_question"})
        if not looks_like_a_person(self.headers):
            return self._send(403, {"error": "forbidden"})
        ip = (self.headers.get("X-Forwarded-For") or self.headers.get("X-Real-Ip") or "?").split(",")[0].strip()
        if over_limit(ip):
            print(json.dumps({"finder_limited": {"ip_hash": hash(ip) & 0xFFFFFF}}))
            return self._send(429, {"error": "busy"})
        try:
            cards, general = load_cards(page)
            # only the cards the visitor's filters leave on screen (all of them if none sent)
            ids = [i for i in (params.get("ids") or [""])[0].split(",") if i]
            allowed = [c["id"] for c in cards if c["id"] in ids]
            pool = [c for c in cards if c["id"] in allowed] or cards
            return self._send(200, ask_claude(q, cards, visitor_context(params, pool), general, allowed or None, page), cache=True)
        except anthropic.RateLimitError:
            return self._send(429, {"error": "busy"})
        except anthropic.APIConnectionError:
            return self._send(503, {"error": "unavailable"})
        except anthropic.APIStatusError as e:
            print(f"cruise-finder API error {e.status_code}: {e.message}")
            return self._send(502, {"error": "unavailable"})
        except Exception as e:  # bad JSON, refusal, no valid picks
            print(f"cruise-finder failed: {e!r}")
            return self._send(502, {"error": "no_answer"})
