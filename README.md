🛠️ Commands Reference
Build & Deployment
make build              # Build all 20 containers
make up                 # Start all services
make down               # Stop all services
Testing & Benchmarking
make test               # Parallel processing test
make benchmark          # Performance benchmark (20 iterations)
make large-test         # Large file processing test
Monitoring & Debugging
make logs               # View all service logs
make logs-service1      # Service 1 instances only
make logs-service2      # Service 2 instances only  
make logs-service3      # Service 3 instances only
make logs-service4      # Service 4 instances only
make logs-loadbalancers # Load balancer logs only
make status             # Container status check
Maintenance
make clean              # Stop and clean up
make restart            # Restart all services
make super-clean        # Complete system cleanup
