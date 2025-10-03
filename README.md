# Fundamentos de Ingeniería de Datos: Extracción de Noticias

Este proyecto presenta un sistema integral para la **extracción de noticias desde portales web**, incorporando análisis de calidad, almacenamiento en formato **JSONL** y la aplicación de **contratos de datos** para garantizar la integridad de la información.

---

## Propósitos del Proyecto

- Recolectar información de sitios de noticias mediante técnicas de **web scraping**.  
- Almacenar los datos extraídos de manera estructurada en formato **JSON Lines (.jsonl)**.  
- Evaluar la **calidad de los datos** a través de un perfilado detallado.  
- Garantizar la **consistencia de los datos** mediante la implementación de un contrato de datos.  
- Documentar el **pipeline completo**, desde la adquisición hasta la validación.  

---

## Flujo del Proceso de Datos

El pipeline se divide en **cuatro fases principales**:

### Fase 1: Extracción de Datos
- **Componente:** `src/scraper.py`  
- **Operación:** `scrape_reuters_news()`  
- **Fuente:** URLs del portal Reuters *World News*  
- **Resultado:** Lista de diccionarios con cada noticia extraída  

### Fase 2: Almacenamiento Estructurado
- **Componente:** `src/scraper.py`  
- **Operación:** `save_to_jsonl()`  
- **Formato:** JSON Lines (`.jsonl`)  
- **Destino:** `data/raw/noticias.jsonl`  

### Fase 3: Análisis de Calidad
- **Componente:** `src/scraper.py`  
- **Operación:** `profile_results()`  
- **Indicadores:** Nulos, duplicados, conformidad de formatos  
- **Informe:** `reports/perfilado.md`  

### Fase 4: Validación con Contrato de Datos
- **Definición:** `contracts/schema.yaml`  
- **Finalidad:** Establecer un esquema formal con reglas de calidad  
- **Verificación:** Validación de tipos de datos, formatos y restricciones  

---

## Portal Seleccionado

Se eligió **Reuters World News** como fuente de datos principal.  
URL: [https://www.reuters.com/world/](https://www.reuters.com/world/)  

---

## Detalles de Implementación del Scraper

### Herramientas Utilizadas
- **BeautifulSoup4:** Análisis del DOM y navegación en HTML.  
- **Requests:** Peticiones HTTP para obtener contenido.  
- **Regex:** Validación de patrones en fechas y URLs.  
- **Hashlib:** Creación de identificadores únicos por noticia.  

### Estrategias de Extracción
- **Selectores Flexibles:** Lista de posibles selectores CSS para localizar artículos, robusto ante cambios en la página.  
- **Fallback con RSS:** Si la extracción HTML falla, se intenta obtener datos desde los feeds RSS.  

---

## Datos Recolectados

- `id`: Hash único generado a partir del contenido.  
- `titulo`: Título del artículo.  
- `fecha`: Fecha de publicación (`YYYY-MM-DD`).  
- `url`: Enlace absoluto a la noticia.  
- `fuente`: Nombre de la fuente (`"Reuters"`).  
- `autor`: Nombre del autor (si está disponible).  
- `capturado_ts`: Timestamp en UTC de la captura.  
- `categoria`: Categoría de la noticia (`"World News"`).  

---

## Contrato de Datos (`contracts/schema.yaml`)

### Campos Requeridos
- `id`: string, hash único.  
- `titulo`: string, longitud 5–500 caracteres.  
- `url`: string, formato de URL válida.  
- `fuente`: string, valor fijo `"Reuters"`.  
- `capturado_ts`: datetime en formato ISO8601.  

### Campos Opcionales
- `fecha`: date (`YYYY-MM-DD`).  
- `autor`: string.  
- `categoria`: string.  

### Reglas de Integridad
- No debe haber **URLs duplicadas**.  
- Las **fechas no pueden ser futuras**.  
- Cada `id` debe ser **único**.  

---

## Métricas de Calidad de Datos

La función `profile_results()` evalúa:

- **Completitud:** Porcentaje de valores nulos.  
- **Unicidad:** Registros duplicados por `id` y `url`.  
- **Consistencia:** Fechas y URLs cumplen formato esperado.  
- **Conformidad:** Cumplimiento del contrato de datos.  

El reporte incluye:  
- Resumen estadístico  
- Distribución de valores faltantes  
- Lista de duplicados  
- Sugerencias de mejora  

---

## Instalación y Uso

### Requisitos Previos
Instala las dependencias necesarias:

```bash
pip install requests beautifulsoup4
