FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY facu_assistant.py .

CMD ["python", "facu_assistant.py"]
