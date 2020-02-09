#!/bin/bash

# Think run before run script :
source /home/marina/.local/bin/virtualenvwrapper.sh
workon PythonVenv

# Django server in development mode

# DjangoProjects/manage.py runserver <YOUR IP or 127.0.0.1>:<PORT>
python DjangoProjects/manage.py runserver 192.168.0.29:8080
