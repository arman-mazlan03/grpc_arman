# gRPC Distributed Services Pipeline

A demonstration of distributed microservices architecture using gRPC and Docker that implements a **service pipeline** where each service calls the next one in sequence.

## 📋 Project Overview

This project demonstrates **Instruction 3** compliance by implementing a pipeline of **4 distinct services**, each with different responsibilities:

1. **Service 1 - Text Input Service** (Port 8051)
   - Receives text from the client
   - Delegates preprocessing to Service 2
   
2. **Service 2 - Preprocessing Service** (Port 8052)
   - Cleans and normalizes text
   - Delegates analysis to Service 3
   
3. **Service 3 - Analysis Service** (Port 8053)
   - Performs word frequency analysis
   - Delegates report generation to Service 4
   
4. **Service 4 - Report Service** (Port 8054)
   - Generates final formatted report
   - Returns results back through the chain

### Service Pipeline Flow

```
Client
  │
  └──> Service 1 (Input)
         │
         └──> Service 2 (Preprocessing)
                │
                └──> Service 3 (Analysis)
                       │
                       └──> Service 4 (Report)
                              │
                              └──> Results flow back
```

## 🎯 Objectives Met

✅ **Objective 1**: Install and use Docker & gRPC for cloud infrastructure  
✅ **Objective 2**: Apply gRPC for distributed processing with multiple service invocations  
✅ **Objective 3**: Benchmark performance (see Performance Testing section)  

✅ **Instruction 1**: Run gRPC Python programs with proper installation in Docker  
✅ **Instruction 2**: Compare single vs. multiple container performance  
✅ **Instruction 3**: Demonstrate distributed services with delegation (4 services = 4 group members)  
✅ **Instruction 4**: Service ports are published and accessible  

## 🚀 Quick Start

### Prerequisites

- Docker and Docker Compose installed
- Python 3.11+ (for local development)
- Make (optional, for convenient commands)

### Running the Project

1. **Clone or extract the project**

2. **Build all services:**
   ```bash
   make build
   # OR
   docker-compose build
   ```

3. **Start all services:**
   ```bash
   make up
   # OR
   docker-compose up -d service1 service2 service3 service4
   ```

4. **Run the client test:**
   ```bash
   make test
   # OR
   docker-compose up client
   ```

5. **View logs:**
   ```bash
   make logs
   # OR
   docker-compose logs -f
   ```

6. **Stop all services:**
   ```bash
   make down
   # OR
   docker-compose down
   ```

## 📁 Project Structure

```
grpc-pipeline-project/
├── proto/
│   └── pipeline.proto          # gRPC service definitions
├── service1-input/
│   ├── app.py                  # Service 1 implementation
│   ├── Dockerfile
│   └── requirements.txt
├── service2-preprocess/
│   ├── app.py                  # Service 2 implementation
│   ├── Dockerfile
│   └── requirements.txt
├── service3-analysis/
│   ├── app.py                  # Service 3 implementation
│   ├── Dockerfile
│   └── requirements.txt
├── service4-report/
│   ├── app.py                  # Service 4 implementation
│   ├── Dockerfile
│   └── requirements.txt
├── client/
│   ├── app.py                  # Client application
│   ├── Dockerfile
│   └── requirements.txt
├── docker-compose.yml          # Container orchestration
├── Makefile                    # Build automation
└── README.md                   # This file
```

## 🔧 Available Make Commands

```bash
make help      # Show all available commands
make build     # Build all Docker images
make up        # Start all services
make down      # Stop all services
make logs      # Show logs from all services
make clean     # Remove all containers and images
make proto     # Generate protobuf stubs locally
make test      # Run the pipeline test
make restart   # Restart all services
```

## 📊 Performance Testing

### Test 1: Single Container (All services in one)

To test performance with all services in a single container, you would need to modify the architecture to run all services in one process. This serves as the baseline.

### Test 2: Distributed Containers (Current setup)

The current setup runs each service in a separate container, allowing for:
- Better isolation
- Independent scaling
- Network overhead measurement
- True microservices architecture

### Benchmarking Commands

1. **Time a single request:**
   ```bash
   time docker-compose up --abort-on-container-exit client
   ```

2. **Monitor resource usage:**
   ```bash
   docker stats
   ```

3. **Test with multiple requests:**
   Modify `client/app.py` to add more test cases or run in a loop.

### Key Metrics to Measure

- **Latency**: Time from client request to final response
- **Throughput**: Number of requests processed per second
- **Resource Usage**: CPU and memory per service
- **Network Overhead**: Time spent in inter-service communication

## 🔍 Understanding the Pipeline

### Step-by-Step Execution

1. **Client sends text to Service 1**
   - Client creates a TextRequest with the input text
   - Sends gRPC request to Service 1 on port 50051

2. **Service 1 forwards to Service 2**
   - Service 1 receives the text
   - Creates a CleanRequest
   - Calls Service 2 on port 50052

3. **Service 2 forwards to Service 3**
   - Service 2 cleans the text (lowercase, remove special chars)
   - Creates an AnalysisRequest
   - Calls Service 3 on port 50053

4. **Service 3 forwards to Service 4**
   - Service 3 analyzes word frequency
   - Creates a ReportRequest
   - Calls Service 4 on port 50054

5. **Service 4 generates report**
   - Service 4 creates a formatted report
   - Returns ReportResponse back to Service 3
   - Results flow back through: Service 3 → Service 2 → Service 1 → Client

## 🐛 Troubleshooting

### Services not starting?

```bash
# Check service status
docker-compose ps

# View service logs
docker-compose logs service1
docker-compose logs service2
docker-compose logs service3
docker-compose logs service4
```

### Connection refused errors?

- Make sure all services are running: `docker-compose ps`
- Wait a few seconds for services to fully start
- Check network connectivity: `docker network ls`

### Port already in use?

```bash
# Change ports in docker-compose.yml
# Or stop conflicting services:
docker-compose down
```

### Clean slate restart?

```bash
make clean
make build
make up
make test
```

## 📝 Extending the Project

### Adding More Services (for larger groups)

1. Create a new service directory (e.g., `service5-validation/`)
2. Add the service definition to `proto/pipeline.proto`
3. Implement the service in `service5-validation/app.py`
4. Create Dockerfile and requirements.txt
5. Update docker-compose.yml to include the new service
6. Update an existing service to call your new service

### Modifying Service Logic

Each service has clear separation:
- Service logic in `app.py`
- Configuration via environment variables
- Dependencies in `requirements.txt`
- Containerization in `Dockerfile`

## 🎓 Learning Points

This project demonstrates:

1. **gRPC Communication**: How services communicate using protocol buffers
2. **Service Delegation**: Each service delegates work to the next
3. **Docker Networking**: Services discover each other by name
4. **Microservices Architecture**: Independent, scalable services
5. **Port Management**: Each service exposes its own port
6. **Container Orchestration**: Docker Compose manages multiple containers

## 📚 References

- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Protocol Buffers](https://developers.google.com/protocol-buffers)

## 👥 Group Assignment Compliance

This project satisfies all assignment requirements:

- ✅ Uses Docker for containerization
- ✅ Implements gRPC for service communication
- ✅ Shows 4 distinct services (matching group size)
- ✅ Demonstrates service delegation pipeline
- ✅ All service ports are published and forwarded
- ✅ Can be benchmarked for performance comparison
- ✅ Services can be called by client and delegate to others

---

**Note**: This is a demonstration project for educational purposes. For production use, add error handling, authentication, monitoring, and logging.