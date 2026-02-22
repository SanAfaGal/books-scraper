import matplotlib.pyplot as plt
from fpdf import FPDF
import os


class BookReportGenerator(FPDF):
    """Clase encargada de la construcción modular del reporte PDF."""

    def __init__(self, df_metrics, df_featured):
        super().__init__()
        self.df_metrics = df_metrics
        self.df_featured = df_featured
        self.chart_path = "data/output/temp_chart.png"

        # Configuración de página y fuentes
        self.set_auto_page_break(auto=True, margin=15)
        self.set_font("Arial", size=11)

    def header(self):
        """Encabezado que se repite en todas las páginas."""
        self.set_font("Arial", "B", 10)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, "Reporte - Books to Scrape", 0, 1, "R")
        self.ln(5)

    def footer(self):
        """Pie de página con numeración."""
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128, 128, 128)
        self.cell(0, 10, f"Página {self.page_no()}", 0, 0, "C")

    def _safe_text(self, text):
        """Limpia el texto para evitar errores de codificación en FPDF."""
        return str(text).encode("latin-1", "replace").decode("latin-1")

    def _generate_price_chart(self):
        """Crea el histograma de precios usando el dataset completo de métricas."""
        plt.figure(figsize=(7, 4))
        plt.hist(self.df_metrics["price"], bins=12, color="#3498db", edgecolor="white")
        plt.title("Distribución de Precios (Catálogo Filtrado)", fontsize=14)
        plt.xlabel("Precio (£)")
        plt.ylabel("Cantidad")
        plt.savefig(self.chart_path, dpi=150, bbox_inches="tight")
        plt.close()

    def add_analysis_page(self):
        """Crea la primera sección: Métricas y Gráficos globales."""
        self.add_page()
        self._generate_price_chart()

        # Título de sección
        self.set_font("Arial", "B", 18)
        self.set_text_color(44, 62, 80)
        self.cell(0, 15, "Análisis General de Mercado", ln=True)
        self.ln(5)

        # Métricas Calculadas
        total_books = len(self.df_metrics)
        avg_price = self.df_metrics["price"].mean()
        avg_rating = self.df_metrics["rating"].mean()

        self.set_font("Arial", "", 11)
        self.set_text_color(0, 0, 0)
        texto_analisis = (
            f"Este reporte analiza un total de {total_books} libros que coinciden con los criterios "
            f"seleccionados. El precio promedio del mercado actual es de £{avg_price:.2f}, "
            f"con una calificación media de {avg_rating:.1f} estrellas."
        )
        self.multi_cell(0, 8, texto_analisis)
        self.ln(5)

        # Insertar Gráfico
        if os.path.exists(self.chart_path):
            self.image(self.chart_path, x=25, w=160)
            self.ln(10)

    def add_featured_page(self):
        """Crea la sección de Libros Destacados (Dataset de selección)."""
        if self.df_featured.empty:
            return

        self.add_page()
        self.set_font("Arial", "B", 16)
        self.set_text_color(192, 57, 43)  # Rojo para destacar
        self.cell(0, 15, "Libros destacados", ln=True)
        self.ln(5)

        for _, row in self.df_featured.iterrows():
            # Título
            self.set_font("Arial", "B", 11)
            self.set_text_color(41, 128, 185)
            self.multi_cell(0, 7, f"TITULO: {self._safe_text(row['title'])}")

            # Info básica (Precio, Stock, Rating)
            self.set_font("Arial", "B", 9)
            self.set_text_color(0, 0, 0)
            stock = row.get("stock_quantity", "N/A")
            info = f"Precio: £{row['price']} | Rating: {row['rating']} | Stock: {stock}"
            self.cell(0, 6, info, ln=True)

            # Descripción (Truncada a 200 caracteres para el PDF)
            self.set_font("Arial", "", 9)
            desc = str(row.get("description", "Sin descripción disponible."))
            desc_trunc = (desc[:200] + "...") if len(desc) > 200 else desc
            self.multi_cell(0, 5, f"Descripción: {self._safe_text(desc_trunc)}")

            # Link
            self.set_font("Arial", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(
                0, 5, f"URL: {row['product_url']}", ln=True, link=row["product_url"]
            )

            self.ln(3)
            self.line(self.get_x(), self.get_y(), self.get_x() + 190, self.get_y())
            self.ln(5)

    def save_report(self, output_path):
        """Orquesta y guarda el PDF."""
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.output(output_path)
            return True
        except Exception as e:
            print(f"Error al guardar el PDF: {e}")
            return False
        finally:
            if os.path.exists(self.chart_path):
                os.remove(self.chart_path)


def generate_pdf_report(
    df_all_filtered, df_selected_featured, output_path="data/output/report.pdf"
):
    """Función principal de integración (Entry Point)."""
    report = BookReportGenerator(df_all_filtered, df_selected_featured)
    report.add_analysis_page()
    report.add_featured_page()
    return report.save_report(output_path)
