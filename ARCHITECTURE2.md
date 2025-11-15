```markdown
# System Architecture - Parallel gRPC Pipeline

## Pipeline Flow Diagram - Parallel System

```
┌──────────┐
│  Client  │
│ (Docker) │
└────┬─────┘
     │
     │ gRPC: ReceiveText()
     │ Port: 8061 (Load Balancer)
     │
     ▼
┌─────────────────────────┐
│  Service 1 Load Balancer│
│        :8061            │
└─────┬───┬───┬───┬───────┘
      │   │   │   │
      ▼   ▼   ▼   ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│S1a │ │S1b │ │S1c │ │S1d │
│8051│ │8055│ │8057│ │8059│
└─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘
  │      │      │      │
  └──────┴──────┴──────┘
         │
         │ gRPC: CleanText()
         │ Port: 8062 (Load Balancer)
         │
         ▼
┌─────────────────────────┐
│  Service 2 Load Balancer│
│        :8062            │
└─────┬───┬───┬───┬───────┘
      │   │   │   │
      ▼   ▼   ▼   ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│S2a │ │S2b │ │S2c │ │S2d │
│8052│ │8056│ │8058│ │8060│
└─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘
  │      │      │      │
  └──────┴──────┴──────┘
         │
         │ gRPC: AnalyzeText()
         │ Port: 8063 (Load Balancer)
         │
         ▼
┌─────────────────────────┐
│  Service 3 Load Balancer│
│        :8063            │
└─────┬───┬───┬───┬───────┘
      │   │   │   │
      ▼   ▼   ▼   ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│S3a │ │S3b │ │S3c │ │S3d │
│8053│ │8065│ │8067│ │8069│
└─┬──┘ └─┬──┘ └─┬──┘ └─┬──┘
  │      │      │      │
  └──────┴──────┴──────┘
         │
         │ gRPC: GenerateReport()
         │ Port: 8064 (Load Balancer)
         │
         ▼
┌─────────────────────────┐
│  Service 4 Load Balancer│
│        :8064            │
└─────┬───┬───┬───┬───────┘
      │   │   │   │
      ▼   ▼   ▼   ▼
┌────┐ ┌────┐ ┌────┐ ┌────┐
│S4a │ │S4b │ │S4c │ │S4d │
│8054│ │8066│ │8068│ │8070│
└────┘ └────┘ └────┘ └────┘
```

## Data Flow - Parallel Processing

### Single Request Path:
1. **Client Request**
   - Input: Raw text string (up to 100MB)
   - Request ID: Unique identifier for tracking
   - Target: Service 1 Load Balancer (port 8061)

2. **Service 1 Load Balancer → Service 1 Instance**
   - Action: Round-robin distribution to available instances
   - Targets: Service1a (8051), Service1b (8055), Service1c (8057), Service1d (8059)
   - Protocol: gRPC ReceiveText()

3. **Service 1 Instance → Service 2 Load Balancer**
   - Action: Forward text for preprocessing
   - Data: Original text + request ID
   - Target: Service 2 Load Balancer (port 8062)
   - Protocol: gRPC CleanText()

4. **Service 2 Load Balancer → Service 2 Instance**
   - Action: Round-robin distribution
   - Targets: Service2a (8052), Service2b (8056), Service2c (8058), Service2d (8060)

5. **Service 2 Instance → Service 3 Load Balancer**
   - Action: Forward cleaned text for analysis
   - Data: Cleaned text + metadata
   - Target: Service 3 Load Balancer (port 8063)
   - Protocol: gRPC AnalyzeText()

6. **Service 3 Load Balancer → Service 3 Instance**
   - Action: Round-robin distribution
   - Targets: Service3a (8053), Service3b (8065), Service3c (8067), Service3d (8069)

7. **Service 3 Instance → Service 4 Load Balancer**
   - Action: Forward analysis results for reporting
   - Data: Word frequencies, statistics
   - Target: Service 4 Load Balancer (port 8064)
   - Protocol: gRPC GenerateReport()

8. **Service 4 Load Balancer → Service 4 Instance**
   - Action: Round-robin distribution
   - Targets: Service4a (8054), Service4b (8066), Service4c (8068), Service4d (8070)

9. **Response Chain**
   - Service 4 → Service 3 → Service 2 → Service 1 → Client
   - Each service adds its processing results
   - Final response includes complete pipeline results

### Parallel Processing:
- **Multiple requests** processed simultaneously across different instances
- **Load distribution** prevents single points of failure
- **Automatic failover** if instances become unavailable

## Network Architecture - Parallel System

```
┌──────────────────────────────────────────────────────────────────┐
│               Docker Bridge Network: grpc-network                │
│                                                                  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────┐  │
│  │Service 1 LB │  │Service 2 LB │  │Service 3 LB │  │Service4 │  │
│  │   :8061     │  │   :8062     │  │   :8063     │  │LB :8064 │  │
│  └─┬─┬─┬─┬─┬───┘  └─┬─┬─┬─┬─┬───┘  └─┬─┬─┬─┬─┬───┘  └─┬─┬─┬─┬─┘  │
│    │ │ │ │ │        │ │ │ │ │        │ │ │ │ │        │ │ │ │    │
│    ▼ ▼ ▼ ▼ ▼        ▼ ▼ ▼ ▼ ▼        ▼ ▼ ▼ ▼ ▼        ▼ ▼ ▼ ▼    │
│  ┌─┐ ┌─┐ ┌─┐ ┌─┐  ┌─┐ ┌─┐ ┌─┐ ┌─┐  ┌─┐ ┌─┐ ┌─┐ ┌─┐  ┌─┐ ┌─┐ ┌─┐  │
│  │S│ │S│ │S│ │S│  │S│ │S│ │S│ │S│  │S│ │S│ │S│ │S│  │S│ │S│ │S│  │
│  │1│ │1│ │1│ │1│  │2│ │2│ │2│ │2│  │3│ │3│ │3│ │3│  │4│ │4│ │4│  │
│  │a│ │b│ │c│ │d│  │a│ │b│ │c│ │d│  │a│ │b│ │c│ │d│  │a│ │b│ │c│  │
│  └─┘ └─┘ └─┘ └─┘  └─┘ └─┘ └─┘ └─┘  └─┘ └─┘ └─┘ └─┘  └─┘ └─┘ └─┘  │
│                                                                  │
│  ┌─────────────────────────────────────────────────────────────┐ │
│  │                         Client                              │ │
│  └─────────────────────────────────────────────────────────────┘ │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Service Communication Pattern

**Parallel Delegation Pattern with Load Balancing**

Each service:
1. Receives a request (via load balancer)
2. Processes the data
3. Delegates to next service's load balancer
4. Waits for response
5. Adds its own results
6. Returns combined response

**Load Balancer Behavior:**
- Round-robin request distribution
- Automatic failover to healthy instances
- Connection pooling and management
- Error handling and retries

This demonstrates:
- Horizontal scaling with multiple instances
- Load distribution and fault tolerance
- Service discovery through load balancers
- Microservices architecture at scale

## Technology Stack

- **Language**: Python 3.11
- **RPC Framework**: gRPC with HTTP/2
- **Serialization**: Protocol Buffers (protobuf)
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Networking**: Docker Bridge Network
- **Load Balancing**: Custom round-robin implementation

## Port Assignments - Parallel System

### Load Balancer Ports
| Load Balancer | Port | Purpose |
|---------------|------|---------|
| Service 1 LB | 8061 | Text input load distribution |
| Service 2 LB | 8062 | Preprocessing load distribution |
| Service 3 LB | 8063 | Analysis load distribution |
| Service 4 LB | 8064 | Report generation load distribution |

### Service Instance Ports
| Service Type | Instances | Ports |
|--------------|-----------|-------|
| Service 1 | 4 instances | 8051, 8055, 8057, 8059 |
| Service 2 | 4 instances | 8052, 8056, 8058, 8060 |
| Service 3 | 4 instances | 8053, 8065, 8067, 8069 |
| Service 4 | 4 instances | 8054, 8066, 8068, 8070 |

**Total: 20 containers** (16 service instances + 4 load balancers)

All ports are:
- Exposed within Docker network for inter-service communication
- Published to host machine for external access and testing
- Managed through Docker Compose networking

## Scalability Implementation

### Current Parallel Design
- **4 services** in sequential pipeline
- **4 instances** of each service type (16 total)
- **4 load balancers** for intelligent distribution
- **Synchronous communication** with parallel execution

### Horizontal Scaling Benefits
1. **Increased Throughput**: Handle 4x more concurrent requests
2. **Fault Tolerance**: System continues with instance failures
3. **Load Distribution**: No single point of bottleneck
4. **Resource Optimization**: Better CPU and memory utilization

### Performance Characteristics
- **Message Size**: Up to 100MB per request
- **Timeout**: 300 seconds for large file processing
- **Concurrency**: 4 parallel requests simultaneously
- **Failover**: Automatic retry with different instances

### Monitoring and Management
- **Health Checks**: Built-in service availability monitoring
- **Logging**: Instance-level logging for debugging
- **Metrics**: Performance tracking through benchmark tools
- **Resource Management**: Docker resource limits and isolation

This architecture demonstrates enterprise-grade microservices patterns with horizontal scaling, load balancing, and fault tolerance - matching production cloud system designs.
```