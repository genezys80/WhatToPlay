#!/usr/bin/env python3
"""Récupère les dernières annonces de chaque jeu et régénère data.js.
Les dates des sorties restent dans data/events.json (à confirmer à la main)."""
import json, re, urllib.request, xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
steam = lambda i: f"https://store.steampowered.com/feeds/news/app/{i}/"
FEEDS = {  # jeu -> flux RSS/Atom (modifiable)
    "Path of Exile": [steam(238960)],
    "Path of Exile 2": [steam(2694490)],
    "Last Epoch": [steam(899770)],
    "Hero Siege": [steam(269210)],
    "Broken Oath": [steam(5461470)],
    "TESO": [steam(306130)],
    "WoW Retail": ["https://www.wowhead.com/news&rss"],  # à vérifier
    "Aion 2": [],  # ajouter ici l'ID Steam ou un flux officiel
}
KEYWORDS = re.compile(r"league|season|saison|patch|update|expansion|extension|release|launch|early access|1\.0|chapter", re.I)
MONTHS = "January|February|March|April|May|June|July|August|September|October|November|December"
DATE_RE = re.compile(rf"\b({MONTHS})\s+(\d{{1,2}})\b", re.I)

def local(el): return el.tag.split("}")[-1]

def parse_feed(xml):
    for el in ET.fromstring(xml).iter():
        if local(el) not in ("item", "entry"): continue
        f = {local(c): c for c in el}
        title = (f["title"].text or "").strip() if "title" in f else ""
        link = ""
        if "link" in f: link = (f["link"].get("href") or f["link"].text or "").strip()
        raw = next((f[k].text for k in ("pubDate", "updated", "published") if k in f and f[k].text), "")
        yield title, link, raw or ""

def to_iso(raw):
    try: return parsedate_to_datetime(raw).astimezone(timezone.utc).date().isoformat()
    except Exception:
        try: return datetime.fromisoformat(raw.replace("Z", "+00:00")).date().isoformat()
        except Exception: return ""

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "release-tracker/1.0"})
    with urllib.request.urlopen(req, timeout=15) as r: return r.read()

def main():
    news_path = ROOT / "data" / "news.json"
    old = json.loads(news_path.read_text("utf-8")) if news_path.exists() else {}
    news = {}
    for game, urls in FEEDS.items():
        items = []
        for url in urls:
            try:
                for title, link, raw in parse_feed(fetch(url)):
                    if KEYWORDS.search(title):
                        items.append({"title": title, "link": link, "date": to_iso(raw),
                                      "dates": sorted({f"{m.group(1).title()} {m.group(2)}" for m in DATE_RE.finditer(title)})})
            except Exception as e:
                print(f"[!] {game}: {url} -> {e}")
        items.sort(key=lambda i: i["date"], reverse=True)
        news[game] = items[:4] if items else old.get(game, [])
    news_path.write_text(json.dumps(news, ensure_ascii=False, indent=1), "utf-8")
    events = json.loads((ROOT / "data" / "events.json").read_text("utf-8"))
    payload = {"generated": datetime.now(timezone.utc).isoformat(timespec="seconds"), "events": events, "news": news}
    (ROOT / "data.js").write_text("window.TRACKER = " + json.dumps(payload, ensure_ascii=False) + ";\n", "utf-8")
    print("OK:", sum(len(v) for v in news.values()), "annonces,", len(events), "événements")

if __name__ == "__main__": main()
