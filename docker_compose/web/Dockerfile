FROM python:3.6

ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code

# Django-gis packages and dependencies for static assets
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    nodejs \
    nodejs-legacy \
    npm \
    libmemcached-dev

ADD requirements/* /code/
RUN pip install -r development.txt
RUN pip install -r production.txt

ADD . /code/

# Make 'wait' script available for the entrypoint-script.
ADD https://raw.githubusercontent.com/eficode/wait-for/master/wait-for /usr/local/bin/waitfor
RUN chmod +x /usr/local/bin/waitfor
