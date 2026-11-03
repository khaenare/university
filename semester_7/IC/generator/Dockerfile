FROM python:3.12.16-slim-trixie

ENV PYTHONUNBUFFERED=1
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY generator.py .

# Непривілейований користувач
RUN useradd --system --uid 10001 app
USER app

EXPOSE 8000
CMD ["python", "generator.py"]
