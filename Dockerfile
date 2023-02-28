FROM python:3.11-slim-buster



COPY . summI
WORKDIR /summI

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN python -m pip install --upgrade pip
RUN pip3 install -r requirements.txt



# RUN addgroup --gid 1001 --system app && \
#     adduser --no-create-home --shell /bin/false --disabled-password --uid 1001 --system --group app

# USER app


EXPOSE 8000


CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
