# Usa una imagen base liviana con Python 3.11
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

# Copia el contenido del proyecto
COPY . /app

# Instala dependencias de Python
RUN pip install --upgrade pip
RUN pip install .

# Expone el puerto (Render usa este por defecto)
EXPOSE 8000

# Comando de inicio: servidor ASGI con Daphne
CMD ["daphne", "-b", "0.0.0.0", "-p", "8000", "fiduswriter.asgi:application"]
