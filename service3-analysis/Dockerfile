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

# Expose port
EXPOSE 8053

# Add this line for unbuffered output
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]