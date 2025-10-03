# Reporte de Calidad de Datos: Extracción de Noticias

- **Fuente Analizada:** Reuters
- **Fecha de Generación:** 2025-10-02

---

## Resumen General 

El análisis se realizó sobre un conjunto de **20 registros** extraídos. Los resultados generales indican una alta calidad en los datos capturados, sin valores nulos ni duplicados detectados.

---

##  1. Análisis de Completitud

No se encontraron valores ausentes en ninguno de los campos, lo que representa una completitud del 100% en el conjunto de datos.

| Campo         | Registros Nulos | Completitud |
|---------------|-----------------|-------------|
| `id`          | 0               | 100.00%     |
| `titulo`      | 0               | 100.00%     |
| `fecha`       | 0               | 100.00%     |
| `url`         | 0               | 100.00%     |
| `fuente`      | 0               | 100.00%     |
| `autor`       | 0               | 100.00%     |
| `capturado_ts`| 0               | 100.00%     |
| `categoria`   | 0               | 100.00%     |

---

## 2. Verificación de Unicidad

El análisis confirma que no existen registros duplicados en el conjunto de datos.

- **Unicidad de ID:** Se verificó que los 20 identificadores son únicos.
- **Unicidad de URL:** Las 20 URLs son distintas entre sí.

---

## 3. Consistencia de Formato

Todos los registros cumplen con los formatos definidos en el contrato de datos.

- **Formato de Fechas:** El 100% de las fechas (`20 de 20`) se ajustan al formato `YYYY-MM-DD`.
- **Formato de URLs:** El 100% de las URLs (`20 de 20`) comienzan con `http(s)://`, validando su estructura.

---

## 4. Observaciones y Pasos a Seguir

1.  **Monitoreo Continuo:** Aunque esta extracción fue exitosa, los campos `autor` y `fecha` a menudo varían en sitios de noticias. Se recomienda mantener una vigilancia constante sobre ellos en futuras extracciones.
2.  **Explorar Fuentes Estables:** Para mejorar la robustez del scraper a largo plazo, se sugiere investigar si la fuente (Reuters) ofrece un **feed RSS o una API pública**, ya que estos suelen ser más estables que la estructura del HTML.
3.  **Garantizar la Unicidad:** La estrategia de generar IDs únicos a partir de las URLs demostró ser efectiva. Es crucial mantener esta validación para prevenir la ingesta de datos duplicados en el futuro.