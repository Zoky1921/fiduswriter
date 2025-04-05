FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libmagic-dev \
    libjpeg-dev \
    zlib1g-dev \
    libxslt1-dev \
    libxml2-dev \
    libffi-dev \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

COPY . /app

RUN pip install --upgrade pip && pip install -r requirements.txt

RUN python manage.py collectstatic --noinput

EXPOSE 8000

CMD ["gunicorn", "fiduswriter.wsgi:application", "--bind", "0.0.0.0:8000"]
