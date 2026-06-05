#!/usr/bin/env python3
"""News Brief — deterministic feed fetcher.

Reads the `feeds` registry from ~/.config/news-brief/sources.json and pulls:
  - RSS / Atom feeds (labs, BBC/NYT/Guardian/Al Jazeera/Diplomat/NPR, markets)
  - JSON APIs: Hacker News top, Hugging Face daily papers
  - YouTube per-channel RSS (keyless) — and, IF a YouTube key is present, an
    outlier ranking from view counts.

Writes /tmp/newsbrief_candidates.json. SKILL.md Step 2 reads that file and scores
these alongside WebSearch results. This script is best-effort: per-source
try/except, browser UA, curl fallback for blocked hosts, and it ALWAYS exits 0
with a valid (possibly empty) JSON file so the skill can fall back to WebSearch.

Stdlib only. `pip install feedparser` would simplify RSS/date handling but is NOT
required.

YouTube key (optional): read from env YOUTUBE_API_KEY or ~/.config/news-brief/.env.
Without it, YouTube still works in recency mode; the per-channel RSS also exposes
media:statistics views, so an outlier flag is attempted keyless too.
"""
import json
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from xml.etree import ElementTree as ET

CFG = os.path.expanduser("~/.config/news-brief")
CONFIG_PATH = os.path.join(CFG, "sources.json")
ENV_PATH = os.path.join(CFG, ".env")
OUT_PATH = "/tmp/newsbrief_candidates.json"
WINDOW_DEFAULT = 48
TIMEOUT = 12
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 news-brief/1.0"
NS = {
    "atom": "http://www.w3.org/2005/Atom",
    "media": "http://search.yahoo.com/mrss/",
    "yt": "http://www.youtube.com/xml/schemas/2015",
}


def now_utc():
    return datetime.now(timezone.utc)


def load_env_key():
    k = os.environ.get("YOUTUBE_API_KEY")
    if k:
        return k.strip()
    if os.path.isfile(ENV_PATH):
        for line in open(ENV_PATH):
            line = line.strip()
            if line.startswith("YOUTUBE_API_KEY="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def load_registry():
    try:
        return json.load(open(CONFIG_PATH)).get("feeds", {}) or {}
    except Exception:
        return {}


def _curl_get(url):
    try:
        r = subprocess.run(
            ["curl", "-sL", "--max-time", str(TIMEOUT), "-A", UA, url],
            capture_output=True, timeout=TIMEOUT + 3,
        )
        return r.stdout if r.returncode == 0 and r.stdout else None
    except Exception:
        return None


def http_get(url, use_curl=False):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": UA})
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            return resp.read()
    except Exception:
        return _curl_get(url) if use_curl else None


def parse_date(raw):
    if not raw:
        return None
    raw = raw.strip()
    try:
        dt = parsedate_to_datetime(raw)  # RFC822 (BBC/NYT/RSS)
        if dt:
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        pass
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))  # ISO8601 (Atom)
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
    except Exception:
        return None


def hours_ago(dt):
    return round((now_utc() - dt).total_seconds() / 3600, 1) if dt else None


def strip_html(s):
    if not s:
        return ""
    s = re.sub(r"<[^>]+>", " ", s)
    s = re.sub(r"&\w+;", " ", s)
    return re.sub(r"\s+", " ", s).strip()[:300]


def slug(s):
    return re.sub(r"[^a-z0-9]+", "-", (s or "").lower()).strip("-")[:60]


def make_hash(title, source, dt):
    d = dt.strftime("%b%d-%Y").lower() if dt else "nodate"
    return f"{slug(title)}-{slug(source)}-{d}"


def text(el):
    return el.text.strip() if el is not None and el.text else ""


def candidate(title, url, source, lens, dt, summary, origin, extra=None):
    c = {
        "title": title, "url": url, "source": source, "lens": lens,
        "published": dt.astimezone(timezone.utc).isoformat() if dt else None,
        "published_hours_ago": hours_ago(dt),
        "summary": strip_html(summary), "origin": origin,
        "headline_hash": make_hash(title, source, dt),
    }
    if extra:
        c.update(extra)
    return c


def fetch_rss(feed):
    """RSS 2.0 + Atom. Returns list of candidate dicts."""
    raw = http_get(feed["url"], use_curl=feed.get("curl_fallback"))
    if not raw:
        raise RuntimeError("no data")
    root = ET.fromstring(raw)
    out = []
    items = root.iter("item")
    items = list(items)
    is_atom = not items
    if is_atom:
        items = root.findall("atom:entry", NS) or root.findall(".//{http://www.w3.org/2005/Atom}entry")
    for it in items:
        try:
            if is_atom:
                title = text(it.find("atom:title", NS))
                link_el = it.find("atom:link", NS)
                url = link_el.get("href") if link_el is not None else ""
                dt = parse_date(text(it.find("atom:published", NS)) or text(it.find("atom:updated", NS)))
                summary = text(it.find("atom:summary", NS)) or text(it.find("atom:content", NS))
            else:
                title = text(it.find("title"))
                url = text(it.find("link"))
                dt = parse_date(text(it.find("pubDate")) or text(it.find("{http://purl.org/dc/elements/1.1/}date")))
                summary = text(it.find("description"))
            if not title or not url:
                continue
            out.append(candidate(title, url, feed["source"], feed["lens"], dt, summary, "rss"))
        except Exception:
            continue
    # optional relevance filter for broad world feeds
    kws = feed.get("filter_keywords")
    if kws:
        kws = [k.lower() for k in kws]
        out = [c for c in out if any(k in (c["title"] + " " + c["summary"]).lower() for k in kws)]
    # newest-first, cap per feed so no single feed floods the pool
    out.sort(key=lambda c: (c["published_hours_ago"] is None, c["published_hours_ago"] or 1e9))
    return out[: feed.get("max_items", 25)]


def fetch_youtube(ch):
    """Per-channel RSS (Atom). Grabs yt:videoId + media:statistics views when present."""
    cid = ch.get("channel_id", "")
    if not cid or "CHANNEL_ID" in cid:
        return []
    url = "https://www.youtube.com/feeds/videos.xml?channel_id=" + cid
    raw = http_get(url)
    if not raw:
        raise RuntimeError("no data")
    root = ET.fromstring(raw)
    out = []
    for e in root.findall("atom:entry", NS):
        try:
            title = text(e.find("atom:title", NS))
            vid = text(e.find("yt:videoId", NS))
            link_el = e.find("atom:link", NS)
            vurl = link_el.get("href") if link_el is not None else (f"https://youtu.be/{vid}" if vid else "")
            dt = parse_date(text(e.find("atom:published", NS)))
            grp = e.find("media:group", NS)
            summary = ""
            views = None
            if grp is not None:
                summary = text(grp.find("media:description", NS))
                stats = grp.find("media:community/media:statistics", NS)
                if stats is not None and stats.get("views"):
                    try:
                        views = int(stats.get("views"))
                    except Exception:
                        views = None
            if not title or not vurl:
                continue
            out.append(candidate(title, vurl, ch["source"], ch["lens"], dt, summary, "youtube",
                                 {"video_id": vid, "views": views, "outlier": None}))
        except Exception:
            continue
    return out


def enrich_youtube_outliers(yt_items, key):
    """If key present, fill missing views via videos.list (batched). Then compute
    per-channel outlier = views / channel median over its recent items."""
    if key:
        missing = [c for c in yt_items if c.get("views") is None and c.get("video_id")]
        for i in range(0, len(missing), 50):
            ids = ",".join(c["video_id"] for c in missing[i:i + 50])
            u = "https://www.googleapis.com/youtube/v3/videos?" + urllib.parse.urlencode(
                {"part": "statistics", "id": ids, "key": key})
            raw = http_get(u)
            if not raw:
                continue
            try:
                data = json.loads(raw)
                vmap = {it["id"]: int(it["statistics"].get("viewCount", 0)) for it in data.get("items", [])}
                for c in missing[i:i + 50]:
                    if c["video_id"] in vmap:
                        c["views"] = vmap[c["video_id"]]
            except Exception:
                continue
    # per-channel median + outlier ratio
    by_src = {}
    for c in yt_items:
        if c.get("views"):
            by_src.setdefault(c["source"], []).append(c["views"])
    med = {}
    for s, vs in by_src.items():
        vs = sorted(vs)
        n = len(vs)
        med[s] = vs[n // 2] if n % 2 else (vs[n // 2 - 1] + vs[n // 2]) / 2
    for c in yt_items:
        m = med.get(c["source"])
        if c.get("views") and m:
            c["outlier"] = round(c["views"] / m, 2)


def fetch_hn(api):
    base = api["url"].rstrip("/")
    top_n = api.get("top_n", 30)
    min_score = api.get("min_score", 100)
    raw = http_get(f"{base}/topstories.json")
    if not raw:
        raise RuntimeError("no data")
    ids = json.loads(raw)[:top_n]
    out = []
    for i in ids:
        raw = http_get(f"{base}/item/{i}.json")
        if not raw:
            continue
        try:
            it = json.loads(raw)
            if it.get("type") != "story" or not it.get("url") or it.get("score", 0) < min_score:
                continue
            dt = datetime.fromtimestamp(it["time"], tz=timezone.utc) if it.get("time") else None
            out.append(candidate(it.get("title", ""), it["url"], "Hacker News", api["lens"], dt,
                                 f"{it.get('score',0)} points", "api",
                                 {"hn_score": it.get("score", 0)}))
        except Exception:
            continue
    return out


def fetch_hf_papers(api):
    raw = http_get(api["url"])
    if not raw:
        raise RuntimeError("no data")
    out = []
    for row in json.loads(raw):
        try:
            p = row.get("paper", row)
            pid = p.get("id", "")
            title = p.get("title", "")
            if not title or not pid:
                continue
            dt = parse_date(row.get("publishedAt") or p.get("publishedAt"))
            out.append(candidate(title, f"https://arxiv.org/abs/{pid}", "Hugging Face Papers",
                                 api["lens"], dt, p.get("summary", ""), "api",
                                 {"upvotes": p.get("upvotes")}))
        except Exception:
            continue
    return out


def collect():
    reg = load_registry()
    window = reg.get("window_hours", WINDOW_DEFAULT)
    key = load_env_key()
    cands, failed, ok = [], [], 0
    yt_items = []

    for feed in reg.get("rss", []):
        try:
            cands += fetch_rss(feed); ok += 1
        except Exception as e:
            failed.append({"source": feed.get("source"), "url": feed.get("url"), "error": str(e)[:80]})

    for api in reg.get("api", []):
        try:
            fn = fetch_hn if api.get("type") == "api_hn" else fetch_hf_papers
            cands += fn(api); ok += 1
        except Exception as e:
            failed.append({"source": api.get("source"), "url": api.get("url"), "error": str(e)[:80]})

    for ch in reg.get("youtube_channels", []):
        try:
            yt_items += fetch_youtube(ch); ok += 1
        except Exception as e:
            failed.append({"source": ch.get("source"), "url": ch.get("channel_id"), "error": str(e)[:80]})
    try:
        enrich_youtube_outliers(yt_items, key)
    except Exception:
        pass

    # window filter (keep null-dated items, flagged): RSS/API
    def in_window(c):
        h = c["published_hours_ago"]
        return h is None or h <= window
    cands = [c for c in cands if in_window(c)]
    yt_cands = [c for c in yt_items if in_window(c)]
    cands += yt_cands

    # dedup within run by url
    seen, deduped = set(), []
    for c in sorted(cands, key=lambda x: (x["published_hours_ago"] is None, x["published_hours_ago"] or 1e9)):
        if c["url"] in seen:
            continue
        seen.add(c["url"]); deduped.append(c)

    return {
        "generated_at": now_utc().isoformat(),
        "window_hours": window,
        "youtube_mode": "outlier" if key else "recency",
        "counts": {
            "rss": sum(1 for c in deduped if c["origin"] == "rss"),
            "api": sum(1 for c in deduped if c["origin"] == "api"),
            "youtube": sum(1 for c in deduped if c["origin"] == "youtube"),
            "total": len(deduped),
            "feeds_ok": ok,
            "feeds_failed": len(failed),
        },
        "failed_feeds": failed,
        "candidates": deduped,
    }


def main():
    try:
        out = collect()
    except Exception as e:
        out = {"generated_at": now_utc().isoformat(), "error": str(e)[:120],
               "counts": {"total": 0}, "candidates": []}
    tmp = OUT_PATH + ".tmp"
    try:
        json.dump(out, open(tmp, "w"), ensure_ascii=False, indent=2)
        os.replace(tmp, OUT_PATH)
    except Exception:
        pass
    c = out.get("counts", {})
    print(f"fetch_feeds: {c.get('total',0)} candidates "
          f"(rss {c.get('rss',0)}, api {c.get('api',0)}, youtube {c.get('youtube',0)}; "
          f"{c.get('feeds_ok',0)} sources ok, {c.get('feeds_failed',0)} failed; "
          f"yt={out.get('youtube_mode','-')})")
    sys.exit(0)


if __name__ == "__main__":
    main()
