# 1. Usar imagen base oficial
FROM python:3.10-slim

# 2. Instalar uv desde la imagen oficial (Patrón recomendado)
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# 3. Establecer el directorio de trabajo
WORKDIR /app

# 4. Habilitar la instalación de paquetes en el Python del sistema
# Esto evita el error de "virtual environment directory" que viste antes
ENV UV_SYSTEM_PYTHON=1

# 5. Optimización de caché: Copiar solo archivos de dependencias primero
# Esto permite que Docker cachee la capa de instalación si no cambian los requisitos
COPY pyproject.toml uv.lock ./

# 6. Instalar dependencias
# --frozen: asegura que el lockfile esté actualizado
# --no-install-project: evita instalar el paquete actual, solo sus dependencias
RUN uv sync --frozen --no-install-project --no-dev

# 7. Copiar el resto de la aplicación
COPY . .

# 8. Crear carpetas de datos
RUN mkdir -p data/output data/logs

# 9. Exponer puerto de Streamlit
EXPOSE 8501

# 10. Ejecutar la aplicación
# La documentación sugiere 'uv run' para asegurar que el entorno esté correctamente cargado
CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]