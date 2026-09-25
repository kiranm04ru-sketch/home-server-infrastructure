FROM python:3.14-slim

WORKDIR /app

# Copy from current directory (now it's here)
COPY app.py .
COPY requirements.txt .
COPY templates ./templates/

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

CMD ["python3", "app.py"]
