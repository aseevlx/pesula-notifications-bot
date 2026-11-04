FROM python:3.13.18-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# /app has to be writable because SQLite creates storage.db-wal and storage.db-shm next to the database
RUN useradd --uid 1000 --no-create-home app && chown app:app /app
USER app

CMD ["python", "-u", "./main.py"]
