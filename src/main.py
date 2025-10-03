#!/usr/bin/env python3
"""
src/main.py
Scraper genérico para noticias (El Universal / BBC Mundo / Reuters).
Guarda JSON Lines en data/raw/noticias.jsonl y genera un perfil en reports/perfilado.md

Uso:
  python src/main.py --source reuters --limit 20 --output data/raw/noticias.jsonl
"""
import argparse
import os
import re
import time
import json
import hashlib
import random
from datetime import datetime, timezone
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
from dateutil import parser as dateparser
from tqdm import tqdm
import validators

DEFAULT_OUTPUT = "data/raw/noticias.jsonl"

SOURCES = {
    "eluniversal": {
        "name": "El Universal",
        "listing": "https://www.eluniversal.com.mx/ultimas-noticias",
        "domain": "eluniversal.com.mx"
    },
    "bbc": {
        "name": "BBC Mundo",
        "listing": "https://www.bbc.com/mundo",
        "domain": "bbc.com"
    },
    "reuters": {
        "name": "Reuters",
        "listing": "https://www.reuters.com/world/",
        "domain": "reuters.com"
    },
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; noticias-scraper/1.0; +https://example.com/bot)"
}

def ensure_dirs(path):
    d = os.path.dirname(path)
    if d:
        os.makedirs(d, exist_ok=True)

def discover_links(session, listing_url, domain, limit=200):
    r = session.get(listing_url, headers=HEADERS, timeout=15)
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "lxml")
    links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.startswith("//"):
            href = "https:" + href
        if href.startswith("/"):
            href = urljoin(listing_url, href)
        parsed = urlparse(href)
        if domain in parsed.netloc:
            if href not in links and not re.search(r'/videos?/|/audio/|/live/', href):
                links.append(href)
        if len(links) >= limit:
            break
    return links

# 🔹 Corrección aquí: usamos attrs=attrs en lugar de **attrs
def extract_meta(soup, attrs_list):
    for attrs in attrs_list:
        tag = soup.find("meta", attrs=attrs)
        if tag and tag.get("content"):
            return tag.get("content")
    return None

def parse_article(session, url, source_key):
    try:
        r = session.get(url, headers=HEADERS, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[WARN] no se pudo obtener {url}: {e}")
        return None

    soup = BeautifulSoup(r.text, "lxml")

    title = extract_meta(soup, [{"property":"og:title"}, {"name":"twitter:title"}, {"name":"title"}])
    if not title:
        h1 = soup.find("h1")
        title = h1.get_text(strip=True) if h1 else None

    snippet = extract_meta(soup, [{"property":"og:description"}, {"name":"description"}, {"name":"twitter:description"}])
    author = extract_meta(soup, [{"name":"author"}, {"property":"article:author"}])
    if not author:
        auth_el = soup.find(class_=re.compile("author", re.I))
        if auth_el:
            author = auth_el.get_text(" ", strip=True)

    date_str = extract_meta(soup, [{"property":"article:published_time"}, {"name":"pubdate"}, {"name":"date"}, {"property":"og:updated_time"}])
    if not date_str:
        time_tag = soup.find("time")
        if time_tag and time_tag.has_attr("datetime"):
            date_str = time_tag["datetime"]
        elif time_tag:
            date_str = time_tag.get_text(strip=True)

    fecha_iso = None
    try:
        if date_str:
            dt = dateparser.parse(date_str)
            if not dt.tzinfo:
                dt = dt.replace(tzinfo=timezone.utc)
            fecha_iso = dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
    except Exception:
        fecha_iso = None

    h = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
    id_ = f"{source_key}-{h}"

    record = {
        "id": id_,
        "titulo": title,
        "fecha": fecha_iso,
        "url": url,
        "fuente": SOURCES[source_key]["name"],
        "autor": author,
        "capturado_ts": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
        "snippet": snippet
    }
    return record

def save_jsonl(records, path):
    ensure_dirs(path)
    with open(path, "w", encoding="utf-8") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")

def profile(records):
    fields = ["id","titulo","fecha","url","fuente","autor","capturado_ts"]
    total = len(records)
    nulls = {field: sum(1 for r in records if not r.get(field)) for field in fields}
    dup_urls = total - len({r.get("url") for r in records})
    dup_ids = total - len({r.get("id") for r in records})
    valid_dates = sum(1 for r in records if r.get("fecha"))
    valid_urls = sum(1 for r in records if validators.url(r.get("url","")))
    return {
        "total": total,
        "nulls": {k: {"count":v, "pct": (v/total*100) if total else 0} for k,v in nulls.items()},
        "duplicates": {"by_url": dup_urls, "by_id": dup_ids},
        "valid_dates": {"count": valid_dates, "pct": (valid_dates/total*100) if total else 0},
        "valid_urls": {"count": valid_urls, "pct": (valid_urls/total*100) if total else 0}
    }

def write_profile_md(stats, out_md):
    ensure_dirs(out_md)
    with open(out_md, "w", encoding="utf-8") as f:
        f.write("# Perfilado de Calidad\n\n")
        f.write(f"- **Total de registros**: {stats['total']}\n")
        f.write(f"- **Duplicados por URL**: {stats['duplicates']['by_url']}\n")
        f.write(f"- **Duplicados por id**: {stats['duplicates']['by_id']}\n\n")
        f.write("## Valores nulos por campo\n\n")
        for field, info in stats["nulls"].items():
            f.write(f"- {field}: {info['count']} ({info['pct']:.2f}%)\n")
        f.write("\n")
        f.write(f"- **Fechas válidas**: {stats['valid_dates']['count']} ({stats['valid_dates']['pct']:.2f}%)\n")
        f.write(f"- **URLs válidas**: {stats['valid_urls']['count']} ({stats['valid_urls']['pct']:.2f}%)\n")

def main():
    parser = argparse.ArgumentParser(description="Scraper de noticias y export JSONL")
    parser.add_argument("--source", required=True, choices=SOURCES.keys(), help="Fuente: eluniversal, bbc, reuters")
    parser.add_argument("--limit", type=int, default=20, help="Número de noticias a extraer")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Archivo JSONL de salida")
    parser.add_argument("--profile", default="reports/perfilado.md", help="Ruta del reporte Markdown")
    args = parser.parse_args()

    session = requests.Session()
    listing = SOURCES[args.source]["listing"]
    domain = SOURCES[args.source]["domain"]

    print(f"[INFO] Descubriendo enlaces en {listing} ...")
    links = discover_links(session, listing, domain, limit=args.limit*4)
    print(f"[INFO] Enlaces candidatos: {len(links)}. Will attempt to scrape up to {args.limit} articles.")

    records = []
    for url in tqdm(links, desc="scraping"):
        if len(records) >= args.limit:
            break
        rec = parse_article(session, url, args.source)
        if rec:
            records.append(rec)
        time.sleep(random.uniform(0.5, 1.3))

    save_jsonl(records, args.output)
    stats = profile(records)
    write_profile_md(stats, args.profile)

    print(f"[DONE] Guardado {len(records)} registros en {args.output}")
    print(f"[DONE] Perfilado guardado en {args.profile}")

if __name__ == "__main__":
    main()
