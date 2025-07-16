#!/bin/sh
python manage.py migrate
gunicorn gps_collar_project.wsgi:application --bind 0.0.0.0:8010
