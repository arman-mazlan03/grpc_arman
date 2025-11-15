FROM python:3.11-slim

WORKDIR /app

COPY service1-loadbalancer/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY proto/ /app/
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pipeline.proto

COPY service1-loadbalancer/app.py .

ENV PYTHONUNBUFFERED=1

EXPOSE 8061

CMD ["python", "app.py"]