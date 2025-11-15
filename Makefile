.PHONY: help build up test logs down clean restart demo \
        logs-service1 logs-service2 logs-service3 logs-service4 logs-loadbalancers \
        status super-clean

# Detect OS
ifeq ($(OS),Windows_NT)
    DETECTED_OS := Windows
    SLEEP_CMD := timeout /t
else
    DETECTED_OS := $(shell uname -s)
    SLEEP_CMD := sleep
endif

help:
	@echo "🚀 gRPC PARALLEL PIPELINE - Available commands:"
	@echo ""
	@echo "MAIN COMMANDS:"
	@echo "  make build    - Build all parallel services"
	@echo "  make up       - Start all parallel services"
	@echo "  make test     - Run parallel pipeline test"
	@echo "  make large-test - Run large file parallel test"
	@echo "  make logs     - Show all parallel services logs"
	@echo "  make down     - Stop all parallel services"
	@echo "  make clean    - Clean parallel setup"
	@echo "  make restart  - Restart all parallel services"
	@echo "  make demo     - Quick demo (build + up + test)"
	@echo ""
	@echo "INDIVIDUAL LOGS:"
	@echo "  make logs-service1 - Show Service 1 instances logs"
	@echo "  make logs-service2 - Show Service 2 instances logs"
	@echo "  make logs-service3 - Show Service 3 instances logs"
	@echo "  make logs-service4 - Show Service 4 instances logs"
	@echo "  make logs-loadbalancers - Show all load balancer logs"
	@echo ""
	@echo "UTILITY:"
	@echo "  make status      - Check status of parallel services"
	@echo "  make super-clean - Complete system cleanup"
	@echo "  make proto       - Generate protobuf stubs locally"

# ==================== MAIN PARALLEL COMMANDS ====================

build:
	@echo "🏗️  Building parallel services..."
	docker-compose -f docker-compose-parallel.yml build

up:
	@echo "🚀 Starting parallel services..."
	docker-compose -f docker-compose-parallel.yml up -d \
		service1a service1b service1c service1d \
		service2a service2b service2c service2d \
		service3a service3b service3c service3d \
		service4a service4b service4c service4d \
		service1-loadbalancer service2-loadbalancer service3-loadbalancer service4-loadbalancer
	@echo "⏳ Waiting for parallel services to be ready..."
	@$(SLEEP_CMD) 15
	@echo "✅ PARALLEL SERVICES ARE RUNNING!"
	@echo ""
	@echo "🌐 LOAD BALANCERS:"
	@echo "  Service 1: localhost:8061"
	@echo "  Service 2: localhost:8062" 
	@echo "  Service 3: localhost:8063"
	@echo "  Service 4: localhost:8064"
	@echo ""
	@echo "🔧 SERVICE INSTANCES:"
	@echo "  Service1: 8051, 8055, 8057, 8059"
	@echo "  Service2: 8052, 8056, 8058, 8060"
	@echo "  Service3: 8053, 8065, 8067, 8069"
	@echo "  Service4: 8054, 8066, 8068, 8070"
	@echo ""
	@echo "💡 Run: make test to test the system"

test:
	@echo "🧪 Running parallel pipeline test..."
	docker-compose -f docker-compose-parallel.yml up --abort-on-container-exit parallel-client

large-test:
	@echo "📁 Running parallel pipeline test for large files..."
	docker-compose -f docker-compose-parallel.yml run --rm parallel-client python large_file_client.py

benchmark:
	@echo "🧪 Running benchmark test..."	
	docker-compose -f docker-compose-parallel.yml run --rm parallel-client python benchmark.py 20 4

logs:
	@echo "📋 Showing all parallel services logs..."
	docker-compose -f docker-compose-parallel.yml logs -f

down:
	@echo "🛑 Stopping parallel services..."
	docker-compose -f docker-compose-parallel.yml down

clean: down
	@echo "🧹 Cleaning parallel setup..."
	docker system prune -f
	@echo "Removing generated Python files..."
	@del /s /q pipeline_pb2.py pipeline_pb2_grpc.py 2>nul || true
	@echo "✅ Parallel cleanup complete!"

restart: down up

demo: build up
	@echo "⏳ Waiting for services to initialize..."
	@$(SLEEP_CMD) 10
	@make test

# ==================== INDIVIDUAL LOGS ====================

logs-service1:
	@echo "🔍 Showing Service 1 instances logs..."
	docker-compose -f docker-compose-parallel.yml logs -f service1a service1b service1c service1d

logs-service2:
	@echo "🔍 Showing Service 2 instances logs..."
	docker-compose -f docker-compose-parallel.yml logs -f service2a service2b service2c service2d

logs-service3:
	@echo "🔍 Showing Service 3 instances logs..."
	docker-compose -f docker-compose-parallel.yml logs -f service3a service3b service3c service3d

logs-service4:
	@echo "🔍 Showing Service 4 instances logs..."
	docker-compose -f docker-compose-parallel.yml logs -f service4a service4b service4c service4d

logs-loadbalancers:
	@echo "🔍 Showing all load balancer logs..."
	docker-compose -f docker-compose-parallel.yml logs -f service1-loadbalancer service2-loadbalancer service3-loadbalancer service4-loadbalancer

# ==================== UTILITY COMMANDS ====================

status:
	@echo "📊 PARALLEL SERVICES STATUS:"
	docker-compose -f docker-compose-parallel.yml ps

super-clean: down
	@echo "💥 Super cleaning everything..."
	docker system prune -af
	@echo "Removing all generated files..."
	@del /s /q pipeline_pb2.py pipeline_pb2_grpc.py 2>nul || true
	@rmdir /s /q __pycache__ 2>nul || true
	@echo "✅ Super cleanup complete!"

proto:
	@echo "🔧 Generating protobuf stubs locally..."
	python -m grpc_tools.protoc -I proto --python_out=. --grpc_python_out=. proto/pipeline.proto
	@echo "✅ Protobuf stubs generated!"