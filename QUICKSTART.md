# Quick Start Guide

## 🚀 Get Running in 5 Minutes

### Step 1: Verify Setup (30 seconds)

```bash
./verify-setup.sh
```

This will check if Docker and Docker Compose are installed and running.

### Step 2: Build the Project (2-3 minutes)

```bash
make build
```

Or without make:
```bash
docker-compose build
```

This builds all 4 service containers and the client.

### Step 3: Start Services (10 seconds)

```bash
make up
```

Or without make:
```bash
docker-compose up -d service1 service2 service3 service4
```

Wait 5 seconds for services to initialize.

### Step 4: Run the Test (5 seconds)

```bash
make test
```

Or without make:
```bash
docker-compose up client
```

### Step 5: View Results

You should see output showing:
- Client sending request to Service 1
- Service 1 forwarding to Service 2
- Service 2 forwarding to Service 3
- Service 3 forwarding to Service 4
- Service 4 generating report
- Results flowing back to client

## 📊 View Logs

To see what each service is doing:

```bash
# All services
make logs

# Individual services
docker-compose logs -f service1
docker-compose logs -f service2
docker-compose logs -f service3
docker-compose logs -f service4
```

## 🧪 Run Benchmarks

To run performance tests:

```bash
docker-compose run --rm client python benchmark.py 20
```

This runs 20 iterations and shows timing statistics.

## 🛑 Stop Services

```bash
make down
```

Or:
```bash
docker-compose down
```

## 🧹 Clean Up Everything

```bash
make clean
```

This removes all containers, images, and generated files.

## 🔧 Troubleshooting

### Services won't start?

```bash
# Check what's running
docker-compose ps

# Restart everything
make restart
```

### Port conflicts?

Edit `docker-compose.yml` and change the port mappings:
```yaml
ports:
  - "50051:50051"  # Change first number to something else
```

### See what's happening inside a container?

```bash
docker exec -it grpc-service1 /bin/bash
```

## 📝 Test Your Understanding

1. **Which service receives the initial client request?**
   - Service 1 (Text Input Service) on port 50051

2. **What is the order of service calls?**
   - Client → Service 1 → Service 2 → Service 3 → Service 4

3. **How many different service types are there?**
   - 4 distinct service types (matching group size)

4. **What does Service 2 do?**
   - Preprocesses/cleans the text

5. **Where does the final report come from?**
   - Service 4 (Report Service)

## 🎯 Next Steps

1. **Modify a service**: Try changing what Service 2 does
2. **Add timing**: Add timestamps to see how long each step takes
3. **Add a 5th service**: Extend the pipeline for larger groups
4. **Test with different data**: Modify the test text in client/app.py
5. **Benchmark**: Compare single container vs distributed performance

## 📚 Need More Help?

- Read the full **README.md** for detailed documentation
- Check **ARCHITECTURE.md** for system design details
- Look at the code comments in each service's `app.py`
- Review `proto/pipeline.proto` to understand the interface contracts

---

**Remember**: This demonstrates Instruction 3 by showing a pipeline of 4 different services (one per group member) that delegate tasks to each other!
