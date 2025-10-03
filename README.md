# Proyecto de Scraping de Noticias y Análisis de Calidad de Datos
**#fundamentosdeingeneriadedatos**

## Descripción

Este proyecto implementa un sistema para la extracción de noticias de sitios web, incluyendo el análisis de la calidad de los datos, la serialización en formato **JSONL** y la validación mediante **contratos de datos**. El objetivo es aplicar de manera práctica los conceptos del ciclo de vida de los datos, desde su adquisición hasta su análisis de calidad.

***

## Flujo de Adquisición de Datos

El proceso está automatizado en el script `src/scraper.py` y se divide en las siguientes fases:

### Fase 1: Extracción (Scraping)
* **Script**: `src/scraper.py`
* **Función Clave**: `fetch_content()` y `parse_articles()`
* **Entrada**: URL del portal de noticias de Reuters.
* **Salida**: Una lista de diccionarios, donde cada diccionario representa una noticia.

### Fase 2: Serialización
* **Script**: `src/scraper.py`
* **Función Clave**: `serialize_to_jsonl()`
* **Formato**: JSON Lines (`.jsonl`), donde cada noticia es un objeto JSON en una línea independiente.
* **Ubicación**: `data/raw/noticias.jsonl`.

### Fase 3: Perfilado de Calidad
* **Script**: `src/scraper.py`
* **Función Clave**: `generate_data_quality_report()`
* **Métricas**: Se evalúa la completitud (nulos), unicidad (duplicados) y consistencia (formatos).
* **Reporte**: Los resultados se guardan en `reports/perfilado.md`.

### Fase 4: Contrato de Datos
* **Archivo**: `contracts/schema.yaml`.
* **Propósito**: Define formalmente la estructura, tipos de datos, formatos y restricciones que deben cumplir los datos extraídos.

***

## Implementación del Scraper

### Elección de la Fuente
Se seleccionó **Reuters (World News)** por la consistencia de su estructura HTML, que utiliza atributos `data-testid` para identificar elementos clave, facilitando una extracción de datos más robusta y estable.
* **URL**: `https://www.reuters.com/world/`

### Tecnologías Utilizadas
* **Requests**: Para realizar las peticiones HTTP y obtener el contenido de la página web.
* **BeautifulSoup4**: Para el parseo del documento HTML y la extracción de datos mediante selectores CSS.
* **Hashlib**: Para generar un identificador único (`id`) para cada noticia a partir de su URL.

### Campos Extraídos
Se extraen los siguientes campos para cada noticia:
* **id**: Hash único generado para identificar el registro.
* **titulo**: Título del artículo.
* **fecha**: Fecha de publicación en formato `YYYY-MM-DD`.
* **url**: Enlace completo a la noticia.
* **fuente**: Nombre del sitio web ("Reuters").
* **autor**: Nombre del autor o agencia.
* **capturado_ts**: Timestamp de la captura en formato ISO 8601 (UTC).

***

## Calidad y Contrato de Datos

### Reglas del Contrato de Datos
El archivo `contracts/schema.yaml` establece las siguientes reglas:
* **Campos Obligatorios**: `id`, `titulo`, `url`, `fuente`, `capturado_ts`.
* **Restricciones**: El `id` y la `url` deben ser únicos. El campo `fuente` debe ser "Reuters".
* **Formatos**: Se validan los formatos para campos como `fecha` (`YYYY-MM-DD`) y `capturado_ts` (ISO 8601).

### Métricas de Calidad
El reporte de perfilado (`reports/perfilado.md`) incluye:
* **Completitud**: Porcentaje de valores nulos para cada campo.
* **Unicidad**: Conteo de registros duplicados basados en `id` y `url`.
* **Consistencia**: Verificación del formato correcto en fechas y URLs.

***

## Instalación y Ejecución

### Requisitos
Es necesario tener **Python 3.8+** y las siguientes librerías:
```bash
pip install requests beautifulsoup4