FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ /app/
RUN groupadd --system --gid 10001 app && useradd --system --uid 10001 --gid app --create-home app \
    && mkdir -p /app/staticfiles && chown -R app:app /app
USER app

EXPOSE 8000
CMD ["gunicorn", "todo_backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
