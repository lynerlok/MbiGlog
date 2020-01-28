FROM tensorflow/tensorflow:latest-gpu-py3
ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
COPY requirements.txt /code/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

RUN useradd -m user
USER user

#RUN pip install --upgrade pip
#RUN pip install -r requirements.txt
