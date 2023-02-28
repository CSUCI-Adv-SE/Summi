FROM python:3.10-slim-buster


COPY . summI
WORKDIR /summI

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip3 install -r requirements.txt --no-cache-dir


# RUN addgroup --gid 1001 --system app && \
#     adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

# USER app


EXPOSE 8000

RUN python3 manage.py migrate

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
