FROM python:3.12.16-slim-trixie

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app.py .

# Непривілейований користувач; /data — том із базою SQLite
RUN useradd --system --uid 10001 app && mkdir /data && chown app /data
USER app

EXPOSE 5000
CMD ["gunicorn", "--workers", "1", "--threads", "4", "--bind", "0.0.0.0:5000", "app:app"]
