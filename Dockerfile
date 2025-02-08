FROM python:3.13.2-slim

WORKDIR /usr/src/app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY config.py ./
COPY api_handler ./

CMD ["python", "./main.py"]