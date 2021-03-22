FROM python:3.7-slim-buster

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
COPY ./app /app

RUN useradd appuser && chown -R appuser /app
USER appuser

CMD ["python", "App.py"]

