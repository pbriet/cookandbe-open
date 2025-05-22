#!/bin/bash

NAME="optalim" # Name of the application
DJANGODIR=/app # Django project directory

NUM_WORKERS=4 # how many worker processes should Gunicorn spawn
DJANGO_SETTINGS_MODULE=optalim.settings
DJANGO_WSGI_MODULE=optalim.wsgi

echo "Starting $NAME"
cd $DJANGODIR
export DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE

PYTHONIOENCODING=utf-8 gunicorn ${DJANGO_WSGI_MODULE}:application \
  --name $NAME \
  --workers $NUM_WORKERS \
  --log-level info \
  --timeout 100 \
  --error-logfile "-" \
  --access-logfile "-" \
  --access-logformat '%(t)s %(b)s %(s)s - "%(r)s (%(T)ss)' \
  --bind "0.0.0.0:8080"
