import streamlit as st
import pandas as pd
import os
from src.scraper import scrape_books
from src.pdf_maker import generate_pdf_report

# --- CONFIGURACIÓN Y ESTILOS ---
st.set_page_config(page_title="Books Scraper Dashboard", layout="wide")

# --- PERSISTENCIA DE ESTADO (Session State) ---
if "data" not in st.session_state:
    if os.path.exists("data/output/books.csv"):
        st.session_state["data"] = pd.read_csv("data/output/books.csv")
    else:
        st.session_state["data"] = pd.DataFrame()

# Importante: Aquí guardamos las URLs de los libros seleccionados globalmente
if "selected_urls" not in st.session_state:
    st.session_state["selected_urls"] = set()

# --- UI: CABECERA ---
st.title("Dashboard - Books to Scrape")

col_input, col_btn = st.columns([2, 1])
with col_input:
    books_count = st.number_input("Cantidad de libros:", min_value=1, value=300)

deep_scrape = st.checkbox(
    "Extraer detalles profundos (Stock y Descripción)", value=False
)
if deep_scrape:
    st.warning(
        "**Aviso de rendimiento:** Esto realizará una petición individual por cada libro. El proceso tardará unos segundos más."
    )

with col_btn:
    st.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
    if st.button(
        "Iniciar Web Scraping", icon=":material/play_arrow:", use_container_width=True
    ):
        # El spinner aparecerá justo después de hacer clic y desaparecerá al terminar
        with st.spinner("Extrayendo libros... Por favor, espera."):
            # Pasamos el nuevo parámetro
            df = scrape_books(target_count=books_count, include_details=deep_scrape)
            st.session_state["data"] = df

        # El success se muestra fuera del spinner para que persista un momento antes del rerun
        st.success("¡Extracción completada!")
        st.rerun()

# --- UI: CUERPO PRINCIPAL ---
if not st.session_state["data"].empty:
    df_raw = st.session_state["data"]

    # 1. SIDEBAR: FILTROS
    st.sidebar.header("Filtros de Búsqueda")
    search_title = st.sidebar.text_input("Buscar por título:")

    # Slider de precio dinámico
    min_p, max_p = float(df_raw["price"].min()), float(df_raw["price"].max())

    if min_p < max_p:
        price_range = st.sidebar.slider(
            "Rango de Precio (£)", min_p, max_p, (min_p, max_p)
        )
    else:
        st.sidebar.info(f"Precio único detectado: £{min_p}")
        price_range = (min_p, min_p)  # Forzamos el rango al valor único

    selected_ratings = st.sidebar.multiselect(
        "Rating (Estrellas):", [1, 2, 3, 4, 5], default=[1, 2, 3, 4, 5]
    )

    # 2. LÓGICA DE FILTRADO
    mask = (df_raw["price"].between(*price_range)) & (
        df_raw["rating"].isin(selected_ratings)
    )
    if search_title:
        mask &= df_raw["title"].str.contains(search_title, case=False, na=False)

    # DataFrame con filtros aplicados
    df_filtered = df_raw[mask].copy()

    # 3. SINCRONIZACIÓN DE SELECCIÓN
    df_filtered["Seleccionar"] = df_filtered["product_url"].apply(
        lambda x: x in st.session_state["selected_urls"]
    )

    # Reordenar para que 'Seleccionar' sea la primera columna
    cols = ["Seleccionar"] + [c for c in df_filtered.columns if c != "Seleccionar"]
    df_filtered = df_filtered[cols]

    st.subheader(f"Resultados del filtro ({len(df_filtered)} libros)")

    # 4. EDITOR DE DATOS (Interacción)
    config_columnas = {
        "Seleccionar": st.column_config.CheckboxColumn(
            "Destacar", width="small", help="Añadir a destacados"
        ),
        "title": st.column_config.TextColumn("Título del libro", width="large"),
        "availability": st.column_config.TextColumn("Disp.", width="small"),
        "product_url": st.column_config.LinkColumn(
            "Web", display_text="🔗 Ver libro", width="small"
        ),
        "price": st.column_config.NumberColumn("Precio", width="small", format="£%.2f"),
        "rating": st.column_config.NumberColumn("Calificación", width="small"),
    }

    if not deep_scrape:
        config_columnas["description"] = None
        config_columnas["stock_quantity"] = None
    else:
        config_columnas["description"] = st.column_config.TextColumn(
            "Descripción", width="medium"
        )
        config_columnas["stock_quantity"] = st.column_config.NumberColumn(
            "Stock", width="small"
        )

    # --- EDITOR DE DATOS ---
    edited_df = st.data_editor(
        df_filtered,
        column_config=config_columnas,  # Usamos el diccionario dinámico
        disabled=[c for c in df_filtered.columns if c != "Seleccionar"],
        hide_index=True,
        width="stretch",
        key="editor_libros",
    )

    # 5. ACTUALIZAR SET DE SELECCIÓN (Persistencia)
    for _, row in edited_df.iterrows():
        url = row["product_url"]
        if row["Seleccionar"]:
            st.session_state["selected_urls"].add(url)
        else:
            st.session_state["selected_urls"].discard(url)

    # 6. RESUMEN DE SELECCIONADOS
    df_selected = df_raw[df_raw["product_url"].isin(st.session_state["selected_urls"])]

    if not df_selected.empty:
        with st.expander(
            f"Libros seleccionados para el reporte ({len(df_selected)})", expanded=True
        ):
            st.write(", ".join(df_selected["title"].tolist()))

            if st.button(
                "Borrar todas las selecciones", icon=":material/delete:", type="primary"
            ):
                st.session_state["selected_urls"] = set()
                st.rerun()

    # 7. GENERACIÓN DE PDF
    st.divider()
    if st.button("Generar informe PDF", icon=":material/file_export:"):
        if len(df_filtered) > 0:
            with st.spinner("Generando reporte..."):
                pdf_path = "data/output/report.pdf"
                success = generate_pdf_report(df_filtered, df_selected, pdf_path)
                if success:
                    st.success(f"¡PDF generado correctamente en `{pdf_path}`!")
                    with open(pdf_path, "rb") as f:
                        st.download_button("Descargar PDF", f, file_name="report.pdf")
        else:
            st.warning("No hay datos para generar el reporte con los filtros actuales.")
