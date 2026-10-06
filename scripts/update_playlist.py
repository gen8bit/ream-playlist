#!/usr/bin/env python3
"""
Descarga el feed RSS de iVoox de Retro Entre Amigos y regenera
el archivo .m3u con todas las URLs de los episodios, ordenados
del más antiguo al más reciente.
"""

import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

FEED_URL = "https://feeds.ivoox.com/feed_fg_f138739_filtro_1.xml"
OUTPUT_FILE = Path(__file__).parent.parent / "retro_entre_amigos.m3u"
USER_AGENT = "Mozilla/5.0 (compatible; REAM-Playlist-Updater/1.0)"


def fetch_feed(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read()


def extract_enclosures(xml_bytes: bytes) -> list[str]:
    root = ET.fromstring(xml_bytes)
    urls = []
    for item in root.findall(".//item"):
        enc = item.find("enclosure")
        if enc is not None:
            u = enc.get("url")
            if u:
                urls.append(u.strip())
    return urls


def write_m3u(urls: list[str], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        for u in urls:
            f.write(u + "\n")


def main() -> int:
    try:
        xml_bytes = fetch_feed(FEED_URL)
    except Exception as e:
        print(f"ERROR descargando feed: {e}", file=sys.stderr)
        return 1

    urls = extract_enclosures(xml_bytes)
    if not urls:
        print("ERROR: no se encontraron enclosures en el feed", file=sys.stderr)
        return 1

    # El feed viene del más nuevo al más antiguo → invertimos
    urls.reverse()

    write_m3u(urls, OUTPUT_FILE)
    print(f"OK: {len(urls)} episodios escritos en {OUTPUT_FILE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
