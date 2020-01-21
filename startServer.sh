#!/bin/bash

# Think run before run script :
source /home/marina/.local/bin/virtualenvwrapper.sh
workon PythonVenv

# Django server in development mode

# DjangoProjects/manage.py runserver <YOUR IP or 127.0.0.1>:<PORT>
DjangoProjects/manage.py runserver 127.0.0.1:8080
