# fundamentosdeingeneriadedatos

A short description of the project.

Proyecto de Scraping de Noticias y Análisis de Calidad de Datos
Descripción
Este proyecto lo qu ehace es que implementa un sistema de scraping para paginas web con noticias con análisis de de datos, serialización en formato JSONL y definición de contratos de datos.
Objetivos

    Aplicar técnicas de web scraping en sitios de noticias

    Estructurar datos en formato JSON Lines (.jsonl)

    Realizar perfilado de calidad de datos

    Implementar contratos de datos

    Documentar el ciclo completo de adquisición de datos

Flujo de Adquisición de Datos
Fase 1: Scraping

    Script: src/scraper.py

    Función: scrape_reuters_news()

    Entrada: URLs de Reuters World News

    Salida: Lista de diccionarios con noticias

Fase 2: Serialización

    Script: src/scraper.py

    Función: save_to_jsonl()

    Formato: JSON Lines (.jsonl)

    Ubicación: data/raw/noticias.jsonl

Fase 3: Perfilado de Calidad

    Script: src/scraper.py

    Función: profile_results()

    Métricas: Nulos, duplicados, formatos

    Reporte: reports/perfilado.md

Fase 4: Data Contract

    Archivo: contracts/schema.yaml

    Propósito: Definir reglas de calidad

    Validación: Tipos, formatos, restricciones

Elección del Sitio
Reuters World News

URL: https://www.reuters.com/world/

Implementación del Scraper
Tecnologías Utilizadas

    BeautifulSoup4: Parsing y navegación del HTML

    Requests: Cliente HTTP para descargar contenido

    Regex: Validación de formatos (fechas, URLs)

    Hashlib: Generación de IDs únicos

Estrategias de Scraping

1. Selectores Múltiples
   python

selectors = [
'article[data-testid="MediaStoryCard"]',
'div[data-testid="MediaStoryCard"]',
'li[data-testid="MediaStoryCard"]',
'.media-story-card**body**3tRWy'
]

2. Fallback a RSS
   python

rss_urls = [
"https://www.reuters.com/world/rss",
"https://www.reuters.com/rssFeed/worldNews",
]

Campos Extraídos

    id (hash único generado)

    titulo

    fecha (formato YYYY-MM-DD)

    url (absoluta)

    fuente ("Reuters")

    autor

    capturado_ts (timestamp UTC)

    categoria ("World News")

Data Contract
Reglas Definidas en contracts/schema.yaml
Campos Obligatorios

    id: string, único, formato hash

    titulo: string, 5-500 caracteres

    url: string, formato http(s)

    fuente: string, valor fijo "Reuters"

    capturado_ts: datetime, formato ISO8601

Campos Opcionales

    fecha: date, formato YYYY-MM-DD

    autor: string

    categoria: string

Reglas de Validación

    URLs únicas

    Fechas válidas (no futuras)

    IDs únicos por hash

Métricas de Calidad
Implementadas en profile_results()

    Completitud: Porcentaje de nulos por campo

    Unicidad: Duplicados por ID y URL

    Consistencia: Formatos de fecha y URL

    Conformidad: Cumplimiento del data contract

Reporte Generado

    Resumen estadístico

    Distribución de nulos

    Identificación de duplicados

    Recomendaciones de mejora

Instalación y Ejecución
Requisitos
bash

pip install requests beautifulsoup4

Ejecución
bash

# Scraping directo

# Con este script ejectuas la aplicación del scrapping para general el .jsonl necesitado

python src/scraper.py --source reuters
