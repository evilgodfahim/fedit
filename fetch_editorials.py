#!/usr/bin/env python3
import feedparser
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timezone

FEEDS = [
    "https://politepol.com/fd/BaUjoEn6s1Rx.xml",
    "https://politepol.com/fd/cjcFELwr80sj.xml"
]

OUTPUT = "feed.xml"
MAX_ITEMS = 500

FILTER_KEYS = [
    "/editorial/",
    "/views-opinion/",
    "/views-reviews/"
]

def link_matches(link):
    for key in FILTER_KEYS:
        if key in link:
            return True
    return False


def fetch_all():
    collected = []

    for url in FEEDS:
        feed = feedparser.parse(url)

        for entry in feed.entries:
            link = getattr(entry, "link", "")
            if not link_matches(link):
                continue

            pub = getattr(entry, "published", None) or getattr(entry, "updated", None)
            dt = datetime.now(timezone.utc) if pub is None else datetime.now(timezone.utc)

            collected.append({
                "title": getattr(entry, "title", "No title"),
                "link": link,
                "published": dt.isoformat(),
                "summary": getattr(entry, "summary", "")
            })

    collected.sort(key=lambda x: x["published"], reverse=True)
    return collected[:MAX_ITEMS]


def build_xml(items):
    rss = ET.Element("rss")
    rss.set("version", "2.0")

    channel = ET.SubElement(rss, "channel")

    ET.SubElement(channel, "title").text = "Filtered Editorial Feed"
    ET.SubElement(channel, "link").text = "https://example.com"
    ET.SubElement(channel, "description").text = "Auto-filtered Editorial + Views Feed"
    ET.SubElement(channel, "lastBuildDate").text = datetime.now(timezone.utc).isoformat()

    for item in items:
        it = ET.SubElement(channel, "item")
        ET.SubElement(it, "title").text = item["title"]
        ET.SubElement(it, "link").text = item["link"]
        ET.SubElement(it, "pubDate").text = item["published"]
        ET.SubElement(it, "description").text = item["summary"]

    rough = ET.tostring(rss, encoding="utf-8")
    pretty = minidom.parseString(rough).toprettyxml(indent="  ")

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(pretty)


def main():
    items = fetch_all()
    build_xml(items)


if __name__ == "__main__":
    main()
