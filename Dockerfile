FROM python:3.11

RUN apt-get update && apt-get install -y \
    build-essential \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    wkhtmltopdf \
    pandoc \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -e .

EXPOSE 8000

CMD ["fiduswriter", "runserver", "0.0.0.0:8000"]
