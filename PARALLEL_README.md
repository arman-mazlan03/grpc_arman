# 🚀 Parallel gRPC Pipeline System

A fully distributed, horizontally-scaled microservice pipeline with **16 service instances**, **4 load balancers**, and full **parallel request processing**.

This project demonstrates how to build a real-world, production-style distributed system using **gRPC**, **Docker**, and **parallel pipelines**.

---

# 🌟 What This System Demonstrates

```
┌───────────────────────────────┐
│        DISTRIBUTED SYSTEM      │
└───────────────────────────────┘
• Horizontal Scaling (4× instances per service)
• Load Balancing (round-robin + failover)
• Parallel Processing (multi-pipeline execution)
• Service Discovery via internal LB routing
• Fault Tolerance (automatic rerouting on failure)
```

---

# 🏗️ System Architecture

This system consists of **4 microservice stages**, each with:

* **1 Load Balancer**
* **4 Service Instances**

Total: **20 running containers** (16 services + 4 load balancers)

### 🔄 High-Level Pipeline

```
Client
   ↓
Service1-LB (8061) → Service1 instances (×4)
   ↓
Service2-LB (8062) → Service2 instances (×4)
   ↓
Service3-LB (8063) → Service3 instances (×4)
   ↓
Service4-LB (8064) → Service4 instances (×4)
   ↓
Final Response
```

### 📘 Detailed Architecture

```
┌──────────────────────────────────────────────────────────────────────────────┐
│                             PARALLEL PIPELINE                                │
└──────────────────────────────────────────────────────────────────────────────┘

Client
   │
   ▼
───────────────────────────  Stage 1: Service Group 1  ─────────────────────────
Load Balancer (Service1-LB:8061)
    ├── Service1a : 8051
    ├── Service1b : 8055
    ├── Service1c : 8057
    └── Service1d : 8059
   ▼
───────────────────────────  Stage 2: Service Group 2  ─────────────────────────
Load Balancer (Service2-LB:8062)
    ├── Service2a : 8052
    ├── Service2b : 8056
    ├── Service2c : 8058
    └── Service2d : 8060
   ▼
───────────────────────────  Stage 3: Service Group 3  ─────────────────────────
Load Balancer (Service3-LB:8063)
    ├── Service3a : 8053
    ├── Service3b : 8065
    ├── Service3c : 8067
    └── Service3d : 8069
   ▼
───────────────────────────  Stage 4: Service Group 4  ─────────────────────────
Load Balancer (Service4-LB:8064)
    ├── Service4a : 8054
    ├── Service4b : 8066
    ├── Service4c : 8068
    └── Service4d : 8070
   ▼
Response Back to Client
```

---

# 🔄 How Data Flows Through the Pipeline

### **Single Request Path**

```
Client 
   → Service1-LB (8061)
   → Service1 instance
   → Service2-LB (8062)
   → Service2 instance
   → Service3-LB (8063)
   → Service3 instance
   → Service4-LB (8064)
   → Service4 instance 
   → Response returned to client
```

### **Parallel Behavior**

Multiple requests (or text chunks) can move through the pipeline **independently and simultaneously**.

---

# 🛠️ Commands Overview

## ▶️ Build & Start

```bash
make build        # Build all services + load balancers
make up           # Start entire distributed system
make restart      # Restart everything
```

## 🧪 Testing Tools

```bash
make test         # Parallel file-splitting client
make benchmark    # Performance benchmarking (20 iterations)
make large-test   # Test large files (up to 100MB)
```

## 📡 Monitoring

```bash
make logs               # View logs for all services
make logs-service1      # Logs for only Service1 instances
make logs-service2      # Logs for only Service2 instances
make logs-service3      # Logs for only Service3 instances
make logs-service4      # Logs for only Service4 instances
make logs-loadbalancers # View all load balancers
make status             # Show container status
```

## 🧹 Management

```bash
make down          # Stop all containers
make clean         # Stop & remove containers
make super-clean   # Remove everything (hard reset)
```

---

# ⚙️ How Parallel Processing Works

Running `make test` performs the following:

1. Reads a file from `/app/datasets/`
2. Splits it into **4 chunks**
3. Sends all chunks to **Service1-LB:8061**
4. LB distributes chunks to different Service1 instances
5. Each chunk independently traverses the entire pipeline
6. Client merges results into a single final output

This models how large systems process data across multiple parallel pipelines.

---

# 🌐 Load Balancer Logic

Each LB uses:

✔ **Round-robin** request distribution
✔ **Failover** retries when an instance is down
✔ **Automatic fallback** until all instances fail
✔ **Zero configuration** on client side

Clients only see a single endpoint per stage.

---

# 📊 Performance Testing Modes

### **Benchmark Mode (`make benchmark`)**

* Full text processed *per request*
* 20 iterations in batches of 4
* Measures:

  * Latency per request
  * Throughput
  * Parallel efficiency
  * Max & min timings

### **Parallel Client (`make test`)**

* Splits one file into 4 chunks
* Processes chunks simultaneously
* Measures end-to-end parallel speedup

### **Large File Client (`make large-test`)**

* Optimized for files up to **100MB**
* Tests 2-way and 4-way parallelism
* Designed for stress testing

---

# ⚡ Key Features

### 🌐 Horizontal Scaling

* 4 instances per service type
* Spread across load balancers
* Prevents bottlenecks and overload

### 🛡️ Fault Tolerance

* LB retries on failure
* Pipeline continues even if multiple instances crash
* Graceful degradation under heavy load

### 🚀 Performance Optimizations

* 100MB message size limits
* 300-second timeouts
* Fully parallel request handling

---

# 🔧 Troubleshooting

### Services Not Ready?

```bash
make up
sleep 15
make test
```

### Check container health:

```bash
make status
```

### View service logs:

```bash
docker-compose -f docker-compose-parallel.yml logs service1a
```

### Port Issues?

Ensure **8051–8070** and **8061–8064** are free.

### File Issues?

* Place files in `datasets/`
* Max tested size: **100MB**
* Automatically mounted into containers

