FROM python:3.11-alpine
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app

RUN apk add --update \
    python3 \
    python3-dev \
    gcc \
    py-pip \
    build-base \
    git \
    wget \
    libxslt-dev \
    xmlsec-dev \
    mariadb-dev \
    openssl \
    libffi \
    cairo-dev \
    pango-dev \
    gdk-pixbuf \
    jpeg-dev \
    zlib-dev \
    freetype-dev \
    lcms2-dev \
    openjpeg-dev \
    tiff-dev \
    tk-dev \
    tcl-dev \
    fontconfig \
    ttf-dejavu

COPY ./requirements.txt /app/requirements.txt
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ADD . /app/

EXPOSE 8000
CMD ["sh", "-c", "python manage.py runserver 0.0.0.0:8000"]
