FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY service3-analysis/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files
COPY proto/ /app/

# Generate protobuf stubs
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pipeline.proto

# Copy service code
COPY service3-analysis/app.py .

# Enable unbuffered logging and set instance ID
ENV PYTHONUNBUFFERED=1
ENV INSTANCE_ID=default

# Expose port
EXPOSE 8053

CMD ["python", "app.py"]