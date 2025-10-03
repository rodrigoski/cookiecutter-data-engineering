# Fundamentos de Ingeniería de Datos

## Proyecto de Scraping de Noticias y Análisis de Calidad de Datos

### Descripción
Este proyecto implementa un sistema de **web scraping** para la extracción de noticias, acompañado de un análisis de calidad de datos, serialización en formato **JSONL** y definición de **contratos de datos** para garantizar integridad y consistencia.

---

### Objetivos
- Aplicar técnicas de **web scraping** en sitios de noticias.  
- Estructurar datos en formato **JSON Lines (.jsonl)**.  
- Realizar **perfilado de calidad de datos**.  
- Implementar **contratos de datos**.  
- Documentar el ciclo completo de adquisición de datos.  

---

### Flujo de Adquisición de Datos

#### Fase 1: Scraping
- **Script:** `src/scraper.py`  
- **Función:** `scrape_reuters_news()`  
- **Entrada:** URLs de Reuters World News  
- **Salida:** Lista de diccionarios con noticias  

#### Fase 2: Serialización
- **Script:** `src/scraper.py`  
- **Función:** `save_to_jsonl()`  
- **Formato:** JSON Lines (`.jsonl`)  
- **Ubicación:** `data/raw/noticias.jsonl`  

#### Fase 3: Perfilado de Calidad
- **Script:** `src/scraper.py`  
- **Función:** `profile_results()`  
- **Métricas:** Nulos, duplicados, formatos  
- **Reporte:** `reports/perfilado.md`  

#### Fase 4: Data Contract
- **Archivo:** `contracts/schema.yaml`  
- **Propósito:** Definir reglas de calidad  
- **Validación:** Tipos, formatos, restricciones  

---

### Fuente de Datos
- **Sitio elegido:** [Reuters World News](https://www.reuters.com/world/)  

---

### Implementación del Scraper

#### Tecnologías Utilizadas
- **BeautifulSoup4:** Parsing y navegación del HTML  
- **Requests:** Cliente HTTP para descarga de contenido  
- **Regex:** Validación de formatos (fechas, URLs)  
- **Hashlib:** Generación de IDs únicos  

#### Estrategias de Scraping
1. **Selectores Múltiples**  
   ```python
   selectors = [
       'article[data-testid="MediaStoryCard"]',
       'div[data-testid="MediaStoryCard"]',
       'li[data-testid="MediaStoryCard"]',
       '.media-story-card**body**3tRWy'
   ]
