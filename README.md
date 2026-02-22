# 📚 Books Scraper

Este proyecto es una herramienta para extraer datos automáticamente del sitio [Books to Scrape](https://books.toscrape.com/), visualizarlos en un panel interactivo y generar reportes en PDF.

## 🛠️ Requisitos previos

Antes de empezar, asegúrate de tener instalado en tu computadora:

1. **Python** (Versión 3.10 o superior).
2. **Git** (Para clonar el proyecto).
3. **Docker** (Opcional, si prefieres no instalar nada directamente en tu PC).

---

## 🚀 Cómo empezar (Paso a paso)

### 1. Clonar el proyecto

Abre una terminal (PowerShell, CMD o Terminal de Linux) y escribe:

```bash
git clone https://github.com/SanAfaGal/books-scraper
cd books-scraper

```

---

### 2. Elegir una forma de ejecutarlo

#### **Opción A: Con Docker (La más fácil)**

Si tienes Docker instalado, no necesitas configurar Python. Solo ejecuta:

1. **Construir y arrancar:**
```bash
docker compose up --build
```


2. Abre en tu navegador: `http://localhost:8501`

---

#### **Opción B: Con Python puro (Tradicional)**

Si quieres usar tu instalación local de Python:

1. **Crear y activar el entorno virtual:**
* **En Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```


* **En Linux/Mac:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```




2. **Instalar dependencias:**
```bash
pip install -r requirements.txt
```


3. **Correr la aplicación:**
```bash
streamlit run app.py
```



---

#### **Opción C: Con `uv` (La más rápida)**

Si tienes instalado el empaquetador `uv` de Astral:

1. **Instalar y ejecutar:**
```bash
uv sync
uv run streamlit run app.py
```



---

## 📖 Cómo usar la herramienta

1. **Extraer datos:** Al abrir la URL, indica cuántos libros quieres (ej. 300) y pulsa **"Iniciar Web Scraping"**.
2. **Filtrar:** Usa la barra lateral para buscar libros por nombre, precio o calificación.
3. **Seleccionar:** En la tabla de resultados, marca la casilla **"Destacar"** en los libros que te interesen para el PDF.
4. **Reporte:** Haz clic en **"Generar informe PDF"** para descargar tu análisis con gráficos y métricas.

## 📂 Archivos generados

Al usar la app, se crearán automáticamente estos archivos:

* `data/output/books.csv`: Base de datos de los libros extraídos.
* `data/output/report.pdf`: El reporte generado con tus filtros.
* `logs/app.log`: Registro de lo que el programa está haciendo.
