# System Architecture

## Pipeline Flow Diagram

```
┌──────────┐
│  Client  │
│ (Docker) │
└────┬─────┘
     │
     │ gRPC: ReceiveText()
     │ Port: 50051
     │
     ▼
┌─────────────────────────┐
│   Service 1             │
│   Text Input Service    │
│   (Docker Container)    │
└────────┬────────────────┘
         │
         │ gRPC: CleanText()
         │ Port: 50052
         │
         ▼
┌─────────────────────────┐
│   Service 2             │
│   Preprocessing Service │
│   (Docker Container)    │
└────────┬────────────────┘
         │
         │ gRPC: AnalyzeText()
         │ Port: 50053
         │
         ▼
┌─────────────────────────┐
│   Service 3             │
│   Analysis Service      │
│   (Docker Container)    │
└────────┬────────────────┘
         │
         │ gRPC: GenerateReport()
         │ Port: 50054
         │
         ▼
┌─────────────────────────┐
│   Service 4             │
│   Report Service        │
│   (Docker Container)    │
└─────────────────────────┘
```

## Data Flow

1. **Client Request**
   - Input: Raw text string
   - Request ID: Unique identifier for tracking
   - Target: Service 1 (port 50051)

2. **Service 1 → Service 2**
   - Action: Forward text for preprocessing
   - Data: Original text + request ID
   - Protocol: gRPC CleanText()

3. **Service 2 → Service 3**
   - Action: Forward cleaned text for analysis
   - Data: Cleaned text + metadata
   - Protocol: gRPC AnalyzeText()

4. **Service 3 → Service 4**
   - Action: Forward analysis results for reporting
   - Data: Word frequencies, statistics
   - Protocol: gRPC GenerateReport()

5. **Response Chain**
   - Service 4 → Service 3 → Service 2 → Service 1 → Client
   - Each service adds its processing results
   - Final response includes complete pipeline results

## Network Architecture

```
┌─────────────────────────────────────────────────────────┐
│          Docker Bridge Network: grpc-network            │
│                                                         │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌────────┐│
│  │Service 1 │  │Service 2 │  │Service 3 │  │Service4││
│  │:50051    │→ │:50052    │→ │:50053    │→ │:50054  ││
│  └────▲─────┘  └──────────┘  └──────────┘  └────────┘│
│       │                                                 │
│  ┌────┴──────┐                                         │
│  │  Client   │                                         │
│  └───────────┘                                         │
│                                                         │
└─────────────────────────────────────────────────────────┘
         │          │          │          │
         ▼          ▼          ▼          ▼
    localhost  localhost  localhost  localhost
      :50051     :50052     :50053     :50054
```

## Service Communication Pattern

**Sequential Delegation Pattern**

Each service:
1. Receives a request
2. Processes the data
3. Delegates to the next service
4. Waits for response
5. Adds its own results
6. Returns combined response

This demonstrates:
- Service-to-service communication
- Request delegation
- Response aggregation
- Microservices architecture

## Technology Stack

- **Language**: Python 3.11
- **RPC Framework**: gRPC
- **Serialization**: Protocol Buffers (protobuf)
- **Containerization**: Docker
- **Orchestration**: Docker Compose
- **Networking**: Docker Bridge Network

## Port Assignments

| Service | Port  | Purpose              |
|---------|-------|----------------------|
| Service 1 | 50051 | Text input endpoint  |
| Service 2 | 50052 | Preprocessing endpoint |
| Service 3 | 50053 | Analysis endpoint    |
| Service 4 | 50054 | Report endpoint      |

All ports are:
- Exposed within Docker network
- Published to host machine
- Accessible for external testing

## Scalability Considerations

### Current Design
- 4 services in sequential pipeline
- One instance per service
- Synchronous communication

### Possible Enhancements
1. **Horizontal Scaling**: Run multiple instances of each service
2. **Load Balancing**: Distribute requests across instances
3. **Async Processing**: Use message queues between services
4. **Caching**: Cache preprocessed/analyzed results
5. **Monitoring**: Add health checks and metrics collection
