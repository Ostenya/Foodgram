#!/bin/bash

if [ -z "$1" ]
  then
    echo "No argument supplied"
    exit 1
elif [ $1 = "migrate" ]
  then
    python manage.py migrate
elif [ $1 = "load_ingredients" ]
  then
    python manage.py load_ingredients
elif [ $1 = "pre-run" ]
  then
    python manage.py collectstatic --noinput
elif [ $1 = "run" ]
  then
    exec $(which gunicorn) foodgram.wsgi:application --bind=0:8000
    exit $?
else
  echo "Invalid argument"
  exit 1
fi