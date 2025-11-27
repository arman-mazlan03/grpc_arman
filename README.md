# **Distributed Text Processing System**

A high-performance distributed system comparing **gRPC**, **RPC**, and **REST** protocols for parallel text processing. Features a 4-stage microservices pipeline with load balancing and horizontal scaling.

## **🏗️ System Architecture**

- **4 Microservices**: Text Input → Preprocessing → Analysis → Report Generation
- **Load Balancing**: 4 instances per service behind round-robin load balancers
- **20 Containers Total**: 16 service instances + 4 load balancers
- **Protocol Support**: gRPC, XML-RPC, and REST implementations

## **🚀 Quick Start**

# **📋 Installation Guide**

## **Required Software Installation**

### **1. Install Docker Desktop**
**Windows/macOS:**
- Download from [docker.com/products/docker-desktop](https://www.docker.com/products/docker-desktop)
- Run the installer and follow setup wizard
- **Windows users**: Enable WSL 2 backend during installation
- **macOS users**: Allocate at least 4GB RAM in Docker Preferences

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install docker.io
sudo systemctl enable docker
sudo systemctl start docker

# Add your user to docker group (logout/login required after)
sudo usermod -aG docker $USER
```

### **2. Install Docker Compose**
**Windows/macOS:** *Already included with Docker Desktop*

**Linux:**
```bash
sudo apt install docker-compose
```

### **3. Install Make** (if not available)
**Windows:**
- Install via Chocolatey: `choco install make`
- Or download from [GnuWin32](http://gnuwin32.sourceforge.net/packages/make.htm)

**macOS:**
```bash
xcode-select --install
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt install make
```

### **4. Verify Installation**
```bash
docker --version
docker-compose --version
make --version
```

All commands should show version numbers without errors.

### **Install Python gRPC Tools** (for code modification)
```bash
pip install grpcio==1.60.0 grpcio-tools==1.60.0 protobuf==4.25.1
```

### **Install VS Code** (recommended editor)
- Download from [code.visualstudio.com](https://code.visualstudio.com/)
- Install Docker and Python extensions

## **Quick Verification**
After installation, run our verification script:
```bash
./verify-setup.sh
```

This will check if all required components are properly installed and configured.

---

**You're now ready to run the system!**

### **Installation & Running**
```bash
# Clone the repository
git clone https://github.com/arman-mazlan03/grpc_arman

# Build and start the system
make build
make up

# Run performance tests
make benchmark
```

## **🛠️ Commands Reference**

### **Build & Deployment**
```bash
make build              # Build all 20 containers
make up                 # Start all services  
make down               # Stop all services
```

### **Testing & Benchmarking**
```bash
make test               # Parallel processing test
make benchmark          # Performance benchmark (10 iterations per pipeline)
make large-test         # Large file processing test
```

### **Monitoring & Debugging**
```bash
make logs               # View all service logs in real-time
make logs-service1      # Service 1 instances only
make logs-service2      # Service 2 instances only
make logs-service3      # Service 3 instances only  
make logs-service4      # Service 4 instances only
make logs-loadbalancers # Load balancer logs only
make status             # Check container status and ports
```

### **Maintenance**
```bash
make clean              # Stop services and clean Docker resources
make restart            # Quick restart of all services
make super-clean        # Complete system reset (containers + images)
```

## **🌐 Access Points**

- **Load Balancers**: `localhost:8061-8064`
- **Service Instances**: `localhost:8051-8070`

## **💡 Key Features**

- **Horizontal Scaling**: 4 instances per service for load distribution
- **Large File Support**: Up to 100MB file processing
- **Parallel Processing**: Split text across multiple pipelines
- **Comprehensive Logging**: Real-time monitoring per service
- **Performance Benchmarking**: Automated comparison testing

## **🎯 Use Case Recommendations**

- **gRPC**: Internal microservices, real-time systems, high-performance applications
- **REST**: Public APIs, web applications, horizontally scalable systems  
- **RPC**: Legacy enterprise systems, internal tools, maintenance projects

---

**Quick Demo**: Run `make demo` for automated build → start → test sequence
