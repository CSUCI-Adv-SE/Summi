FROM ubuntu:latest

RUN apt-get update && apt upgrade -y

RUN apt install software-properties-common -y && add-apt-repository ppa:deadsnakes/ppa && apt install python3.10 python3-pip -y

RUN apt install tesseract-ocr -y

RUN apt-get install --reinstall libpq-dev -y



COPY . summI
WORKDIR /summI

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip3 install -r requirements.txt --no-cache-dir


# RUN addgroup --gid 1001 --system app && \
#     adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

# USER app


EXPOSE 8080

RUN python3 manage.py migrate

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
