import requests
from bs4 import BeautifulSoup
import json
import hashlib
from datetime import datetime, timezone
import time
import os
import re
import argparse
import random

def get_headers():
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    ]
    
    return {
        'User-Agent': random.choice(user_agents),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,es;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Cache-Control': 'max-age=0',
    }

def generate_id(url, title):
    content = f"{url}_{title}".encode('utf-8')
    return hashlib.md5(content).hexdigest()[:12]

def scrape_reuters_news():
    urls_to_try = [
        "https://www.reuters.com/world/",
        "https://www.reuters.com/news/archive/worldNews",
    ]
    
    articles = []
    
    for url in urls_to_try:
        try:
            print(f"Intentando con URL: {url}")
            response = requests.get(url, headers=get_headers(), timeout=15)
            
            if response.status_code == 403:
                print("✓ Acceso bloqueado (403). Intentando con sesión...")
                session = requests.Session()
                session.headers.update(get_headers())
                response = session.get(url, timeout=15)
            
            response.raise_for_status()
            print("✓ Conexión exitosa")
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            selectors = [
                'article[data-testid="MediaStoryCard"]',
                'div[data-testid="MediaStoryCard"]',
                'li[data-testid="MediaStoryCard"]',
                'a[data-testid="Heading"]',  
                '.media-story-card__body__3tRWy',  
            ]
            
            for selector in selectors:
                news_items = soup.select(selector)[:25]
                if news_items:
                    print(f"✓ Encontrados {len(news_items)} elementos con selector: {selector}")
                    break
            else:
                news_items = soup.find_all(['article', 'div'], class_=re.compile(r'(card|story|article|news)'))[:25]
                print(f"✓ Encontrados {len(news_items)} elementos con búsqueda general")
            
            for item in news_items[:20]: 
                try:
                    title = None
                    title_selectors = [
                        'h2', 'h3', 'h4',
                        '[data-testid="Heading"]',
                        '.media-story-card__title__',
                        '.text__text__1FZLe',
                        'a[data-testid="Link"]'
                    ]
                    
                    for title_selector in title_selectors:
                        title_elem = item.select_one(title_selector)
                        if title_elem and title_elem.get_text().strip():
                            title = title_elem.get_text().strip()
                            break
                    
                    if not title:
                        continue
                    
                    link = None
                    link_elem = item.find('a', href=True)
                    if link_elem:
                        link = link_elem['href']
                        if link and link.startswith('/'):
                            link = f"https://www.reuters.com{link}"
                    
                    if not link:
                        continue
                    
                    fecha = datetime.now().strftime('%Y-%m-%d')  
                    time_elem = item.find('time')
                    if time_elem and time_elem.get('datetime'):
                        try:
                            fecha_str = time_elem['datetime']
                            fecha_dt = datetime.fromisoformat(fecha_str.replace('Z', '+00:00'))
                            fecha = fecha_dt.strftime('%Y-%m-%d')
                        except:
                            pass
                    
                    author = "Reuters"
                    author_selectors = ['span', 'p', 'div']
                    for author_selector in author_selectors:
                        author_elem = item.select_one(f'{author_selector}[class*="author"], {author_selector}[class*="byline"]')
                        if author_elem and author_elem.get_text().strip():
                            author_text = author_elem.get_text().strip()
                            if 'Reuters' not in author_text and len(author_text) < 50:
                                author = author_text
                                break
                    
                    article_data = {
                        "id": generate_id(link, title),
                        "titulo": title,
                        "fecha": fecha,
                        "url": link,
                        "fuente": "Reuters",
                        "autor": author,
                        "capturado_ts": datetime.now(timezone.utc).isoformat(),
                        "categoria": "World News"
                    }
                    
                    articles.append(article_data)
                    print(f"  ✓ Noticia: {title[:50]}...")
                    
                except Exception as e:
                    print(f"  ✗ Error procesando artículo: {e}")
                    continue
            
            if articles:
                break  
                
            time.sleep(2)  
            
        except requests.RequestException as e:
            print(f"✗ Error con {url}: {e}")
            continue
        except Exception as e:
            print(f"✗ Error inesperado con {url}: {e}")
            continue
    
    return articles

def scrape_reuters_alternative():
    print("Intentando método alternativo con RSS...")
    
    rss_urls = [
        "https://www.reuters.com/world/rss",
        "https://www.reuters.com/rssFeed/worldNews",
    ]
    
    articles = []
    
    for rss_url in rss_urls:
        try:
            response = requests.get(rss_url, headers=get_headers(), timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'xml')
            items = soup.find_all('item')[:20]
            
            for item in items:
                try:
                    title = item.title.get_text().strip() if item.title else None
                    link = item.link.get_text().strip() if item.link else None
                    
                    if title and link:
                        fecha = datetime.now().strftime('%Y-%m-%d')
                        if item.pubDate:
                            try:
                                fecha_dt = datetime.strptime(item.pubDate.get_text(), '%a, %d %b %Y %H:%M:%S %Z')
                                fecha = fecha_dt.strftime('%Y-%m-%d')
                            except:
                                pass
                        
                        article_data = {
                            "id": generate_id(link, title),
                            "titulo": title,
                            "fecha": fecha,
                            "url": link,
                            "fuente": "Reuters",
                            "autor": "Reuters Staff",
                            "capturado_ts": datetime.now(timezone.utc).isoformat(),
                            "categoria": "World News"
                        }
                        articles.append(article_data)
                        print(f"  ✓ RSS Noticia: {title[:50]}...")
                        
                except Exception as e:
                    print(f"  ✗ Error procesando item RSS: {e}")
                    continue
            
            if articles:
                break
                
        except Exception as e:
            print(f"✗ Error con RSS {rss_url}: {e}")
            continue
    
    return articles

def save_to_jsonl(articles, filename):
    """Guarda los artículos en formato JSONL"""
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    with open(filename, 'w', encoding='utf-8') as f:
        for article in articles:
            f.write(json.dumps(article, ensure_ascii=False) + '\n')

def profile_results(records: list) -> str:
    total = len(records)
    fields = ["id", "titulo", "fecha", "url", "fuente", "autor", "capturado_ts", "categoria"]
    null_counts = {f: 0 for f in fields}
    urls = []
    ids = []
    date_format_ok = 0
    url_format_ok = 0

    for r in records:
        for f in fields:
            if not r.get(f):
                null_counts[f] += 1
        urls.append(r.get("url"))
        ids.append(r.get("id"))
        if r.get("fecha"):
            if re.match(r"^\d{4}-\d{2}-\d{2}$", r.get("fecha")):
                date_format_ok += 1
        if r.get("url") and re.match(r"^https?://", r.get("url")):
            url_format_ok += 1

    dup_urls = len(urls) - len(set(urls))
    dup_ids = len(ids) - len(set(ids))

    lines = []
    lines.append(f"# Perfilado de Calidad - {datetime.now(timezone.utc).isoformat()}\n")
    lines.append(f"**Número total de registros:** {total}\n")
    lines.append("\n## Porcentaje de valores nulos por campo:\n")
    for f in fields:
        pct = (null_counts[f] / total * 100) if total else 0
        lines.append(f"- {f}: {null_counts[f]} nulos ({pct:.2f}%)\n")

    lines.append("\n## Duplicados:\n")
    lines.append(f"- Duplicados por URL: {dup_urls}\n")
    lines.append(f"- Duplicados por ID: {dup_ids}\n")

    lines.append("\n## Consistencia de formatos:\n")
    lines.append(f"- Fechas con formato YYYY-MM-DD: {date_format_ok}/{total}\n")
    lines.append(f"- URLs con formato http(s): {url_format_ok}/{total}\n")

    lines.append("\n## Observaciones / recomendaciones:\n")
    lines.append("- Verificar campos autor y fecha, suelen ser los más inconsistentes entre fuentes.\n")
    lines.append("- Considerar usar feeds RSS/JSON oficiales o APIs cuando estén disponibles para mayor estabilidad.\n")
    lines.append("- Validar que todos los IDs sean únicos para evitar duplicados.\n")

    return "\n".join(lines)

def main():
    parser = argparse.ArgumentParser(description='Scraping de noticias y perfilado de calidad')
    parser.add_argument('--source', default='reuters', choices=['reuters'],
                       help='Fuente de noticias (por defecto: reuters)')
    parser.add_argument('--use-rss', action='store_true', 
                       help='Usar RSS como fuente alternativa')
    
    args = parser.parse_args()
    
    print("Iniciando scraping de noticias...")
    
    if args.use_rss:
        articles = scrape_reuters_alternative()
    else:
        articles = scrape_reuters_news()
        if not articles:
            print("Scraping directo falló, intentando con RSS...")
            articles = scrape_reuters_alternative()
    
    if articles:
        output_file = "data/raw/noticias.jsonl"
        save_to_jsonl(articles, output_file)
        print(f"✓ {len(articles)} noticias guardadas en {output_file}")
        
        perfil = profile_results(articles)
        report_dir = "reports"
        os.makedirs(report_dir, exist_ok=True)
        report_file = os.path.join(report_dir, "perfilado.md")
        
        with open(report_file, "w", encoding="utf-8") as f:
            f.write(perfil)
        print(f"✓ Reporte de perfilado generado en {report_file}")
        
        print(f"\nResumen:")
        print(f"- Noticias obtenidas: {len(articles)}")
        print(f"- Archivo de datos: {output_file}")
        print(f"- Reporte de calidad: {report_file}")
        
    else:
        print("✗ No se pudieron obtener noticias. Posibles soluciones:")
        print("  1. Verificar conexión a internet")
        print("  2. Intentar con: python src/scraper.py --use-rss")
        print("  3. Usar un VPN o cambiar red")
        print("  4. Esperar y reintentar más tarde")

if __name__ == '__main__':
    main()