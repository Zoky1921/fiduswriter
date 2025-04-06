# Usa una imagen base con Python 3.11
FROM python:3.11-slim

# Establece el directorio de trabajo
WORKDIR /app

# Instala dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    libpq-dev \
    python3-dev \
    python3-pip \
    libmagic1 \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copia los archivos del proyecto
COPY . /app

# Instala las dependencias de Python
RUN pip install --upgrade pip
RUN pip install .

# Ejecuta migraciones antes de iniciar el servidor
RUN python manage.py migrate

# Expone el puerto 8000 para Render
EXPOSE 8000

# Comando para arrancar el servidor con Daphne (ASGI)
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "fiduswriter.asgi:application"]
