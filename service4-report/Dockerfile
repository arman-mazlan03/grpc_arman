FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY service4-report/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files
COPY proto/ /app/

# Generate protobuf stubs
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pipeline.proto

# Copy service code
COPY service4-report/app.py .

# Enable unbuffered logging and set instance ID
ENV PYTHONUNBUFFERED=1
ENV INSTANCE_ID=default

# Expose port
EXPOSE 8054

CMD ["python", "app.py"]