#!/bin/sh

source /usr/local/bin/virtualenvwrapper.sh
workon PythonVenv

gunicorn glogServer.wsgi
