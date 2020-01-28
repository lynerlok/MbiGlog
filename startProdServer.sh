#!/bin/sh

# DjangoProjects/manage.py runserver <YOUR IP or 127.0.0.1>:<PORT>
IMAGE_NAME=glogserver:1.0
IP=192.168.0.29
PORT=8080

docker run --name DjangoTensorFlow --env-file ~/docker-env -v /media/Datas/MbiGlogAmyDocker/:/media/Datas/MbiGlog --network host -d --rm --gpus all $IMAGE_NAME python /media/Datas/MbiGlog/DjangoProjects/manage.py runserver $IP:$PORT
