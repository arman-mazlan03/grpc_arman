.PHONY: help build up down logs clean proto test

help:
	@echo "gRPC Distributed Pipeline - Available commands:"
	@echo "  make build    - Build all Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - Show logs from all services"
	@echo "  make clean    - Remove all containers, images, and generated files"
	@echo "  make proto    - Generate protobuf stubs locally"
	@echo "  make test     - Run the pipeline test"
	@echo "  make restart  - Restart all services"

build:
	@echo "Building all Docker images..."
	docker-compose build

up:
	@echo "Starting all services..."
	docker-compose up -d service1 service2 service3 service4
	@echo "Waiting for services to be ready..."
	@powershell -Command "Start-Sleep -Seconds 5"
	@echo "All services are running!"
	@echo "Service 1 (Input):       localhost:8051"
	@echo "Service 2 (Preprocess):  localhost:8052"
	@echo "Service 3 (Analysis):    localhost:8053"
	@echo "Service 4 (Report):      localhost:8054"

down:
	@echo "Stopping all services..."
	docker-compose down

logs:
	docker-compose logs -f

clean:
	@echo "Cleaning up..."
	docker-compose down -v
	docker system prune -f
	# Windows-compatible file cleanup
	@echo "Removing generated Python files..."
	@del /s /q pipeline_pb2.py pipeline_pb2_grpc.py 2>nul || true
	@echo "Removing Python cache directories..."
	@rmdir /s /q __pycache__ 2>nul || true
	@echo "Cleanup complete!"

proto:
	@echo "Generating protobuf stubs locally..."
	python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/pipeline.proto
	@echo "Protobuf stubs generated!"

test:
	@echo "Running pipeline test..."
	docker-compose up --abort-on-container-exit client
	@echo "Test complete!"

restart: down up

# Single container management
logs-service1:
	docker-compose logs -f service1

logs-service2:
	docker-compose logs -f service2

logs-service3:
	docker-compose logs -f service3

logs-service4:
	docker-compose logs -f service4

logs-client:
	docker-compose logs -f client