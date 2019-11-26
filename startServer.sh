#!/bin/sh
source PythonVenv/bin/activate

# Django server in development mode

# DjangoProjects/manage.py runserver <YOUR IP or 127.0.0.1>:<PORT>
# DjangoProjects/manage.py runserver 127.0.0.1:8080

# Run gunicorn for PGADMIN on the global python installation
# Root permission to create unix socket

sudo -b nohup gunicorn --bind unix:/var/sockets/pgadmin.sock \
         --workers=1 \
         --threads=25 \
         --chdir /usr/lib/python3.7/site-packages/pgadmin4-web \
         pgAdmin4:app

# Run Django server in production mode

cd DjangoProjects && nohup gunicorn glogServer.wsgi &
