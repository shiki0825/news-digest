from __future__ import annotations
import datetime as dt
import os
import pathlib
import textwrap
from typing import List, Dict
import feedparser
import requests
from openai import OpenAI

ROOT = pathlib.Path(__file__).resolve().parent
DOCS = ROOT / "docs"
ARCHIVE = DOCS / "archive"
TEMPLATES = ROOT / "templates"

DEFAULT_FEEDS = [
    "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja",
]

def fetch_rss(url: str, timeout: int = 20):
    r = requests.get(url, timeout=timeout)
    r.raise_for_status()
    return feedparser.parse(r.content)

def collect_items(feeds: List[str], max_items: int = 10) -> List[Dict[str, str]]:
    items = []
    for feed_url in feeds:
        parsed = fetch_rss(feed_url)
        for e in parsed.entries[:max_items]:
            items.append({
                "title": e.get("title", ""),
                "link": e.get("link", ""),
            })
    return items

def build_prompt(items, date_str):
    bullets = "\n".join(f"- {i['title']} {i['link']}" for i in items)
    return f"今日のニュースを簡潔にまとめて:\n{bullets}"

def summarize(prompt: str) -> str:
    client = OpenAI()
    r = client.responses.create(model="gpt-5.2", input=prompt)
    return r.output_text

def main():
    today = dt.date.today().strftime("%Y-%m-%d")
    items = collect_items(DEFAULT_FEEDS)
    digest = summarize(build_prompt(items, today))

    DOCS.mkdir(exist_ok=True)
    html = f"<html><body><pre>{digest}</pre></body></html>"
    (DOCS / "index.html").write_text(html, encoding="utf-8")

if __name__ == "__main__":
    main()
