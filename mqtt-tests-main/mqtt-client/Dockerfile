FROM python:alpine3.19

RUN apk update
RUN apk add --no-cache gcc libressl-dev musl-dev libffi-dev 


COPY . /opt/app/

WORKDIR /opt/app/

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

ENTRYPOINT ["python3", "mqtt-pub.py" ]