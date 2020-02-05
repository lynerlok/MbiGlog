#!/bin/sh

# Think run before run scripts :
source /usr/local/bin/virtualenvwrapper.sh
workon PythonVenv

# Django server in development mode

# DjangoProjects/manage.py runserver <YOUR IP or 127.0.0.1>:<PORT>
python DjangoProjects/manage.py runserver 192.168.0.29:8080
