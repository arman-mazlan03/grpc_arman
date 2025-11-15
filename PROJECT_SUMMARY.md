# Project Summary: Parallel gRPC Pipeline System

## 🏗️ System Overview

A distributed microservices pipeline using gRPC with horizontal scaling through load balancers and multiple service instances.

### Architecture
- **4 distinct service types** in sequential pipeline
- **4 instances of each service** (16 total instances)  
- **4 load balancers** for request distribution
- **gRPC** for inter-service communication

## 🔧 Technology Stack

- **gRPC**: High-performance RPC framework
- **Protocol Buffers**: Interface definition and serialization
- **Docker**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Python**: Service implementation

## 📡 gRPC Overview

### What is gRPC?
gRPC is a modern RPC framework that uses:
- **Protocol Buffers** as interface definition language
- **HTTP/2** for transport
- **Binary serialization** for efficiency
- **Strongly-typed** service contracts

### Service Definitions (`pipeline.proto`)
```protobuf
service TextInputService {
    rpc ReceiveText(TextRequest) returns (TextResponse);
}

service PreprocessService {
    rpc CleanText(CleanRequest) returns (CleanResponse);
}

service AnalysisService {
    rpc AnalyzeText(AnalysisRequest) returns (AnalysisResponse);
}

service ReportService {
    rpc GenerateReport(ReportRequest) returns (ReportResponse);
}
```

### Protocol Buffers (protobuf) is essential for gRPC systems.

🎯 What Problem protobuf Solves
Without protobuf:
1. Each service needs to understand each other's data formats
2. Manual serialization/deserialization
3. Error-prone data parsing
4. No type safety between services
5. Hard to maintain as APIs change

With protobuf:
1. Single source of truth for all service contracts
2. Automatic code generation for client/server stubs
3. Type-safe communication between services
4. Backward/forward compatibility
5. Efficient binary serialization

## 🔄 System Flow

### Complete Pipeline Path
```
Client 
→ Service1-LoadBalancer:8061 
→ Service1-Instance (8051/8055/8057/8059)
→ Service2-LoadBalancer:8062
→ Service2-Instance (8052/8056/8058/8060) 
→ Service3-LoadBalancer:8063
→ Service3-Instance (8053/8065/8067/8069)
→ Service4-LoadBalancer:8064
→ Service4-Instance (8054/8066/8068/8070)
→ Returns through chain
```

### Service Responsibilities
1. **Service 1 (Text Input)**: Entry point, receives client requests
2. **Service 2 (Preprocess)**: Cleans and normalizes text
3. **Service 3 (Analysis)**: Performs word frequency analysis  
4. **Service 4 (Report)**: Generates final formatted report

## 🛠️ Commands Reference

### Build & Deployment
```bash
make build              # Build all 20 containers
make up                 # Start all services
make down               # Stop all services
```

### Testing & Benchmarking
```bash
make test               # Parallel processing test
make benchmark          # Performance benchmark (20 iterations)
make large-test         # Large file processing test
```

### Monitoring & Debugging
```bash
make logs               # View all service logs
make logs-service1      # Service 1 instances only
make logs-service2      # Service 2 instances only  
make logs-service3      # Service 3 instances only
make logs-service4      # Service 4 instances only
make logs-loadbalancers # Load balancer logs only
make status             # Container status check
```

### Maintenance
```bash
make clean              # Stop and clean up
make restart            # Restart all services
make super-clean        # Complete system cleanup
```

## 📊 Performance Characteristics

### Load Distribution
- **Round-robin** algorithm across 4 instances
- **Automatic failover** to healthy instances
- **Concurrent processing** of multiple requests

### Resource Limits
- **100MB max message size** for large files
- **300 second timeout** for heavy processing
- **10+ worker threads** per service

### Benchmark Results
- **32MB file processing**: 3.5s - 8.5s per request
- **110 million words** processed with 100% success
- **2.4x parallel speedup** vs sequential processing

## 🗂️ Project Structure

```
├── client/
│   ├── benchmark.py          # Performance testing
│   ├── parallel_client.py    # Parallel file processing
│   ├── large_file_client.py  # Large file handling
│   └── app.py               # Main client
├── service1-input/          # Text Input Service
├── service2-preprocess/     # Preprocessing Service
├── service3-analysis/       # Analysis Service  
├── service4-report/         # Report Service
├── service1-loadbalancer/   # Service 1 Load Balancer
├── service2-loadbalancer/   # Service 2 Load Balancer
├── service3-loadbalancer/   # Service 3 Load Balancer
├── service4-loadbalancer/   # Service 4 Load Balancer
├── proto/
│   └── pipeline.proto       # gRPC service definitions
└── datasets/               # Test data files
```

## 🎯 Key Features Demonstrated

### Microservices Patterns
- **Service decomposition** into specialized components
- **Inter-service communication** via gRPC
- **Independent scaling** of service types
- **Loose coupling** between services

### Scalability Patterns
- **Horizontal scaling** with multiple instances
- **Load balancing** for traffic distribution
- **Parallel processing** capabilities
- **Resource isolation** through containers

### Production Readiness
- **Health monitoring** through logging
- **Error handling** and graceful degradation
- **Performance benchmarking**
- **Large dataset handling**

## 🔧 Development Details

### Protocol Buffer Generation
```bash
python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. pipeline.proto
```

### Service Implementation Pattern
Each service:
1. Implements gRPC service interface
2. Processes incoming requests
3. Calls next service in pipeline
4. Returns aggregated response

### Container Configuration
- **Python 3.11** base image
- **Automatic proto compilation** in Dockerfile
- **Environment variables** for configuration
- **Volume mounts** for datasets

## 📈 Performance Insights

### Parallel vs Sequential
- **Sequential**: One request through entire pipeline
- **Parallel**: Multiple requests processed simultaneously
- **Speedup**: 2.4x improvement with parallel processing

### Load Balancing Benefits
- **Even distribution** across instances
- **Fault tolerance** through redundancy
- **Resource utilization** optimization
- **Scalability** without code changes

```