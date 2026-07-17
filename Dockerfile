FROM python:3.14-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Traer el binario oficial de uv directamente desde su imagen distroless
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

# Optimizar el comportamiento de uv y python en Docker
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copiar especificaciones de dependencias primero para aprovechar el caché de Docker
COPY pyproject.toml uv.lock ./

# Sincronizar dependencias
RUN uv sync --frozen --no-dev

# Copiar el código fuente de tu aplicación Flask
COPY . .

# Agregar el entorno virtual generado por uv directamente al PATH
ENV PATH="/app/.venv/bin:$PATH"

# Exponer el puerto de producción
EXPOSE 5000

CMD ["uvicorn", "pjecz_delphinus_flask.app:app", "--host", "0.0.0.0", "--port", "5000"]
# CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:5000", "pjecz_delphinus_flask.app:app"]
