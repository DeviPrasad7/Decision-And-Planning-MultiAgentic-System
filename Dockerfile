FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ /app/app/

WORKDIR /app/app

EXPOSE 8000

CMD ["chainlit", "run", "app.py", "-w", "--host", "0.0.0.0", "--port", "8000"]