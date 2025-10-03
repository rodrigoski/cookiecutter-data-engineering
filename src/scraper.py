import requests
from bs4 import BeautifulSoup
import json
import hashlib
from datetime import datetime, timezone
import random
import time
from pathlib import Path
import re
from collections import defaultdict
import argparse

# --- Constantes y Configuración ---

# Se elige Reuters como fuente de datos según las opciones proporcionadas.
# URL: https://www.reuters.com/world/ [cite: 11]
SOURCE_URL = "https://www.reuters.com/world/"
SOURCE_NAME = "Reuters"

# Define las rutas de salida para los datos y reportes.
# Los entregables son el archivo de datos y el reporte de perfilado. [cite: 53, 55]
OUTPUT_DATA_DIR = Path("data/raw")
OUTPUT_REPORTS_DIR = Path("reports")
OUTPUT_FILE = OUTPUT_DATA_DIR / "noticias.jsonl"
REPORT_FILE = OUTPUT_REPORTS_DIR / "perfilado.md"

def get_random_user_agent():
    """Selecciona un User-Agent aleatorio para simular un navegador real."""
    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0',
    ]
    return random.choice(USER_AGENTS)

# --- Clase Principal del Scraper ---

class NewsScraper:
    """
    Una clase para encapsular la lógica de scraping de un sitio de noticias.
    """
    def __init__(self, url, source_name):
        self.url = url
        self.source_name = source_name
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive',
            'DNT': '1',
        })
        print(f"Scraper inicializado para la fuente: {self.source_name}")

    def _generate_id(self, text_input):
        """Genera un ID único basado en el hash del texto de entrada (URL)."""
        return hashlib.sha1(text_input.encode('utf-8')).hexdigest()[:16]

    def fetch_content(self):
        """Realiza la petición HTTP para obtener el contenido de la página."""
        try:
            response = self.session.get(self.url, timeout=20)
            response.raise_for_status()  # Lanza una excepción para códigos de error HTTP
            print(f"✓ Contenido de {self.url} obtenido con éxito.")
            return response.text
        except requests.exceptions.RequestException as e:
            print(f"✗ Error al intentar obtener la página: {e}")
            return None

    def parse_articles(self, html_content, max_articles=25):
        """Parsea el HTML para extraer y estructurar los datos de las noticias."""
        if not html_content:
            return []

        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Estrategia de búsqueda de contenedores de noticias
        # Se priorizan selectores específicos y luego se usan genéricos.
        article_containers = soup.select('li[data-testid="MediaStoryCard"]')
        if not article_containers:
             article_containers = soup.select('div[data-testid="MediaStoryCard"]')
        if not article_containers:
            print("! No se encontraron contenedores con selectores primarios, intentando con selectores de respaldo.")
            article_containers = soup.find_all(class_=re.compile("story-card|media-story"))

        scraped_news = []
        for article_html in article_containers[:max_articles]:
            title_element = article_html.select_one('a[data-testid="Heading"]')
            link_element = article_html.find('a', href=True)
            
            if not (title_element and link_element and link_element.get('href')):
                continue

            title = title_element.get_text(strip=True)
            relative_url = link_element['href']
            
            # Construye la URL completa si es relativa
            full_url = relative_url if relative_url.startswith('http') else f"https://www.reuters.com{relative_url}"

            # Extrae la fecha si está disponible
            date_element = article_html.find('time')
            iso_date = datetime.now().strftime('%Y-%m-%d') # Fecha por defecto
            if date_element and date_element.has_attr('datetime'):
                try:
                    iso_date = datetime.fromisoformat(date_element['datetime'].replace('Z', '+00:00')).strftime('%Y-%m-%d')
                except ValueError:
                    pass # Mantiene la fecha por defecto si el formato es inesperado

            # El autor rara vez está en la página principal, se asigna un valor por defecto.
            author = "Reuters Staff" # Campo `autor` es requerido [cite: 18]

            news_item = {
                "id": self._generate_id(full_url),
                "titulo": title,
                "fecha": iso_date, # Formato ISO si es posible [cite: 15]
                "url": full_url,
                "fuente": self.source_name,
                "autor": author,
                "capturado_ts": datetime.now(timezone.utc).isoformat() # Timestamp de captura [cite: 19]
            }
            scraped_news.append(news_item)
            print(f"  -> Noticia extraída: '{title[:40]}...'")

        return scraped_news

# --- Funciones de Apoyo ---

def serialize_to_jsonl(data, file_path):
    """
    Guarda una lista de diccionarios en un archivo con formato JSON Lines.
    Cada noticia es un objeto JSON en una nueva línea. [cite: 21, 23]
    """
    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            for item in data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        print(f"✓ {len(data)} registros guardados en {file_path}")
    except IOError as e:
        print(f"✗ Error al escribir en el archivo {file_path}: {e}")

def generate_data_quality_report(records):
    """
    Analiza los datos recolectados y genera un reporte en formato Markdown.
    El reporte incluye total de registros, nulos, duplicados y consistencia. [cite: 27, 29-32]
    """
    if not records:
        return "No se encontraron registros para analizar."

    total_records = len(records)
    null_counts = defaultdict(int)
    url_set = set()
    id_set = set()
    
    date_format_regex = re.compile(r'^\d{4}-\d{2}-\d{2}$')
    url_format_regex = re.compile(r'^https?://')
    
    valid_dates = 0
    valid_urls = 0

    for record in records:
        for key, value in record.items():
            if value is None or (isinstance(value, str) and not value.strip()):
                null_counts[key] += 1
        
        # Conteo de duplicados y validación de formatos
        url_set.add(record.get("url"))
        id_set.add(record.get("id"))
        if record.get("fecha") and date_format_regex.match(record.get("fecha")):
            valid_dates += 1
        if record.get("url") and url_format_regex.match(record.get("url")):
            valid_urls += 1

    # Construcción del reporte
    report = [
        f"# Reporte de Calidad de Datos - {datetime.now(timezone.utc).date()}",
        f"**Fuente de Datos:** {records[0].get('fuente', 'N/A')}\n",
        f"## 1. Resumen General",
        f"- **Número total de registros:** {total_records}\n",
        f"## 2. Completitud (Valores Nulos)",
        "| Campo          | % Nulos |",
        "|----------------|---------|",
    ]
    
    fields = list(records[0].keys())
    for field in fields:
        percentage = (null_counts[field] / total_records) * 100
        report.append(f"| {field:<14} | {percentage:.2f}%   |")

    report.extend([
        "\n## 3. Unicidad",
        f"- **IDs únicos:** {len(id_set)} de {total_records} (Duplicados: {total_records - len(id_set)})",
        f"- **URLs únicas:** {len(url_set)} de {total_records} (Duplicados: {total_records - len(url_set)})\n",
        "## 4. Consistencia de Formato",
        f"- **Fechas en formato YYYY-MM-DD:** {valid_dates / total_records:.2%}",
        f"- **URLs con prefijo http(s)://:** {valid_urls / total_records:.2%}"
    ])

    return "\n".join(report)

# --- Punto de Entrada Principal ---

def main():
    """Función principal que orquesta el proceso de scraping y reporte."""
    parser = argparse.ArgumentParser(description="Web scraper de noticias para Reuters.")
    parser.add_argument(
        "--max",
        type=int,
        default=25,
        help="Número máximo de artículos a intentar extraer."
    )
    args = parser.parse_args()

    print("--- Iniciando Proceso de Extracción de Noticias ---")
    scraper = NewsScraper(SOURCE_URL, SOURCE_NAME)
    
    # Simula un comportamiento más humano con una pequeña pausa
    time.sleep(random.uniform(1, 3))
    
    html = scraper.fetch_content()
    
    if html:
        articles = scraper.parse_articles(html, max_articles=args.max)
        
        if articles:
            # Serializa los datos en JSONL
            serialize_to_jsonl(articles, OUTPUT_FILE)
            
            # Genera y guarda el reporte de calidad
            report_content = generate_data_quality_report(articles)
            REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
            REPORT_FILE.write_text(report_content, encoding="utf-8")
            print(f"✓ Reporte de calidad generado en: {REPORT_FILE}")
            
            print("\n--- Proceso Finalizado con Éxito ---")
            print(f"Total de noticias procesadas: {len(articles)}")
        else:
            print("✗ No se pudieron extraer artículos. El HTML del sitio pudo haber cambiado.")
    else:
        print("✗ No se pudo obtener el contenido de la página. Verifique la conexión o posibles bloqueos.")

if __name__ == "__main__":
    main()