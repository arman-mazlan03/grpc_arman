FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY service1-input/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files
COPY proto/ /app/

# Generate protobuf stubs
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pipeline.proto

# Copy service code
COPY service1-input/app.py .

# Expose port
EXPOSE 8051

# Add this line for unbuffered output
ENV PYTHONUNBUFFERED=1

CMD ["python", "app.py"]