FROM python:3.11-slim

WORKDIR /app

# Copy requirements
COPY client/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy proto files
COPY proto/ /app/

# Generate protobuf stubs
RUN python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pipeline.proto

# Copy client code
COPY client/*.py ./

# Copy datasets directory
COPY datasets/ /app/datasets/

CMD ["python", "app.py"]