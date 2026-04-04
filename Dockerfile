FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY . /app

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir ".[web]"

RUN mkdir -p /app/uploads /app/output

EXPOSE 5000

CMD ["python", "app.py"]
