.PHONY: help build up down logs clean proto test parallel-build parallel-up parallel-test parallel-logs parallel-down parallel-clean

# Detect OS
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    SLEEP_CMD := timeout /t
else
    DETECTED_OS := $(shell uname -s)
    SLEEP_CMD := sleep
endif

help:
	@echo "gRPC Distributed Pipeline - Available commands:"
	@echo ""
	@echo "SEQUENTIAL SYSTEM:"
	@echo "  make build    - Build all Docker images"
	@echo "  make up       - Start all services"
	@echo "  make down     - Stop all services"
	@echo "  make logs     - Show logs from all services"
	@echo "  make clean    - Remove all containers, images, and generated files"
	@echo "  make proto    - Generate protobuf stubs locally"
	@echo "  make test     - Run the pipeline test"
	@echo "  make restart  - Restart all services"
	@echo ""
	@echo "PARALLEL SYSTEM:"
	@echo "  make parallel-build    - Build parallel services"
	@echo "  make parallel-up       - Start parallel services"
	@echo "  make parallel-test     - Run parallel pipeline test"
	@echo "  make parallel-logs     - Show parallel services logs"
	@echo "  make parallel-down     - Stop parallel services"
	@echo "  make parallel-clean    - Clean parallel setup"
	@echo "  make parallel-demo     - Quick demo (build + up + test)"
	@echo ""
	@echo "COMPARISON:"
	@echo "  make compare-all       - Compare sequential vs parallel"
	@echo "  make status            - Check status of all services"

# ==================== SEQUENTIAL COMMANDS ====================

build:
	@echo "Building all Docker images..."
	docker-compose build

up:
	@echo "Starting all services..."
	docker-compose up -d service1 service2 service3 service4
	@echo "Waiting for services to be ready..."
	@$(SLEEP_CMD) 5
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

# ==================== PARALLEL COMMANDS ====================

parallel-build:
	@echo "Building parallel services..."
	docker-compose -f docker-compose-parallel.yml build

parallel-up:
	@echo "Starting parallel services..."
	docker-compose -f docker-compose-parallel.yml up -d \
		service1a service1b service1c service1d \
		service2a service2b service2c service2d \
		service3a service3b service3c service3d \
		service4a service4b service4c service4d \
		service1-loadbalancer service2-loadbalancer service3-loadbalancer service4-loadbalancer
	@echo "Waiting for parallel services to be ready..."
	@$(SLEEP_CMD) 15
	@echo "🚀 PARALLEL SERVICES ARE RUNNING!"
	@echo ""
	@echo "Service 1 Load Balancer: localhost:8061"
	@echo "Service 2 Load Balancer: localhost:8062" 
	@echo "Service 3 Load Balancer: localhost:8063"
	@echo "Service 4 Load Balancer: localhost:8064"
	@echo ""
	@echo "Individual Service Instances:"
	@echo "  Service1: 8051, 8055, 8057, 8059"
	@echo "  Service2: 8052, 8056, 8058, 8060"
	@echo "  Service3: 8053, 8065, 8067, 8069"
	@echo "  Service4: 8054, 8066, 8068, 8070"
	@echo ""
	@echo "Run: make parallel-test to test the parallel system"

parallel-test:
	@echo "Running parallel pipeline test..."
	docker-compose -f docker-compose-parallel.yml up --abort-on-container-exit parallel-client

parallel-large-test:
	@echo "Running parallel pipeline test for large files..."
	docker-compose -f docker-compose-parallel.yml run --rm parallel-client python large_file_client.py

parallel-logs:
	@echo "Showing parallel services logs..."
	docker-compose -f docker-compose-parallel.yml logs -f

parallel-logs-service1:
	docker-compose -f docker-compose-parallel.yml logs -f service1a service1b service1c service1d

parallel-logs-service2:
	docker-compose -f docker-compose-parallel.yml logs -f service2a service2b service2c service2d

parallel-logs-service3:
	docker-compose -f docker-compose-parallel.yml logs -f service3a service3b service3c service3d

parallel-logs-service4:
	docker-compose -f docker-compose-parallel.yml logs -f service4a service4b service4c service4d

parallel-logs-loadbalancers:
	docker-compose -f docker-compose-parallel.yml logs -f service1-loadbalancer service2-loadbalancer service3-loadbalancer service4-loadbalancer

parallel-down:
	@echo "Stopping parallel services..."
	docker-compose -f docker-compose-parallel.yml down

parallel-clean: parallel-down
	@echo "Cleaning parallel setup..."
	docker system prune -f
	@echo "Removing generated Python files..."
	@del /s /q pipeline_pb2.py pipeline_pb2_grpc.py 2>nul || true
	@echo "Parallel cleanup complete!"

parallel-restart: parallel-down parallel-up

# Quick parallel test (build + up + test)
parallel-demo: parallel-build parallel-up
	@echo "Waiting for services to initialize..."
	@$(SLEEP_CMD) 10
	@make parallel-test

# ==================== MIXED COMMANDS ====================

# Compare sequential vs parallel
compare-all:
	@echo "=== SEQUENTIAL SYSTEM ==="
	@make test
	@echo ""
	@echo "=== PARALLEL SYSTEM ==="  
	@make parallel-test

# Status check
status:
	@echo "=== SEQUENTIAL SERVICES ==="
	@docker-compose ps
	@echo ""
	@echo "=== PARALLEL SERVICES ==="
	@docker-compose -f docker-compose-parallel.yml ps

# Full system cleanup
super-clean: down parallel-down
	@echo "Super cleaning everything..."
	docker system prune -af
	@echo "Removing all generated files..."
	@del /s /q pipeline_pb2.py pipeline_pb2_grpc.py 2>nul || true
	@rmdir /s /q __pycache__ 2>nul || true
	@echo "Super cleanup complete!"