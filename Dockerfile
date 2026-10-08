# FROM python:3.12-slim
# WORKDIR /app
# ENV PYTHONDONTWRITEBYTECODE=1
# ENV PYTHONUNBUFFERED=1
# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt
# COPY app.py .
# EXPOSE 8000
# CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]

FROM python:3.12-slim

WORKDIR /app

COPY dist/order_service-1.0.0-py3-none-any.whl .

RUN pip install --no-cache-dir order_service-1.0.0-py3-none-any.whl

EXPOSE 8000

CMD ["uvicorn", "order_service.app:app", "--host", "0.0.0.0", "--port", "8000"]
