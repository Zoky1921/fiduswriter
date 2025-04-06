FROM python:3.11

# Crear directorio para la app
WORKDIR /app

# Copiar todos los archivos
COPY . .

# Instalar dependencias
RUN pip install --upgrade pip
RUN pip install .

# Recopilar archivos estáticos (si es necesario, se puede quitar)
RUN python manage.py collectstatic --noinput

# Comando para migrar la base de datos e iniciar el servidor
CMD ["sh", "-c", "python manage.py migrate && daphne fiduswriter.asgi:application"]
