#!/bin/bash

# Wait for all services.
waitfor postgres:5432 -- python manage.py check
waitfor redis:6379 -- python manage.py check
waitfor elasticsearch:9200 -- python manage.py check

# Set env-files according to docker-compose containers
mv /code/envs/DATABASE_URL /code/envs/DATABASE_URL.bak
mv /code/envs/ES_HOST /code/envs/ES_HOST.bak
mv /code/envs/CACHES /code/envs/CACHES.bak
echo "postgis://qcat@postgres:5432/qcat" > /code/envs/DATABASE_URL
echo "elasticsearch" > /code/envs/ES_HOST
echo "{'default': {'BACKEND': 'redis_cache.RedisCache','LOCATION': 'redis:6379','OPTIONS': {'PARSER_CLASS': 'redis.connection.HiredisParser'}}}" > /code/envs/CACHES

# Create static assets, and prepare all data for the application.
if [ "$1" = 'build' ]; then

    # prepare database and data
    python manage.py migrate --noinput
    python manage.py load_qcat_data
    python manage.py loaddata technologies approaches cca watershed

    # create static assets
    npm install
    bower install
    grunt build:deploy --force
    python manage.py collectstatic --noinput

    # refresh elasticsearch
    echo "Create and populate Elasticsearch indexes"
    python manage.py rebuild_es_indexes
else
    exec "$@"
fi
