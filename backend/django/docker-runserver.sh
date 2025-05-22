#!/bin/bash

if [ "$RUN_MODE" = "celery" ]; then
    WORKER_OR_BEAT="worker"
elif [ "$RUN_MODE" = "beat" ]; then
    WORKER_OR_BEAT="beat"
fi

if [[ -v WORKER_OR_BEAT ]]; then
    echo "*** STARTING CELERY"
    if [ "$DEBUG" == "True" ]; then
        watchmedo auto-restart --directory=./ --pattern=*.py --recursive -- celery -A optalim.celery ${WORKER_OR_BEAT} --loglevel=info --schedule=/tmp/celerybeat-schedule
    else
        celery -A optalim.celery ${WORKER_OR_BEAT} --loglevel=info --schedule=/tmp/celerybeat-schedule
    fi
fi

if [ "$RUN_MODE" = "api" ]; then
    if [ "$DEBUG" == "True" ]; then
        python3 manage.py runserver 0.0.0.0:8080
    else
        gunicorn optalim.wsgi --bind 0.0.0.0:8080
    fi
fi
