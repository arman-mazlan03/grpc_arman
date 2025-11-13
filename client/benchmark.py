#!/usr/bin/env python3
"""
Benchmark script to compare performance of the distributed pipeline.
Runs multiple test iterations and calculates statistics.
"""

import grpc
import sys
import time
import statistics
import uuid

# Add proto directory to path
sys.path.insert(0, '/app')

import pipeline_pb2
import pipeline_pb2_grpc


def run_single_test(text, service1_address='service1:8051'):
    """Run a single pipeline test and return the execution time."""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        with grpc.insecure_channel(service1_address) as channel:
            stub = pipeline_pb2_grpc.TextInputServiceStub(channel)
            request = pipeline_pb2.TextRequest(
                text=text,
                request_id=request_id
            )
            response = stub.ReceiveText(request, timeout=60)
            
        elapsed_time = time.time() - start_time
        return elapsed_time, True, response.word_count
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"Error: {str(e)}")
        return elapsed_time, False, 0


def run_benchmark(num_iterations=10):
    """Run benchmark with multiple iterations."""
    
    # Test text
    test_text = """
    Docker is a platform for developing, shipping, and running applications 
    in containers. gRPC is a high-performance RPC framework that can run in 
    any environment. Together, they enable building distributed microservices 
    that are scalable and efficient. This demonstration shows how multiple 
    services can communicate and delegate tasks to each other. The architecture
    consists of four different services working in a pipeline pattern.
    """ * 5  # Make it longer for more realistic testing
    
    print("\n" + "=" * 70)
    print("gRPC DISTRIBUTED PIPELINE BENCHMARK")
    print("=" * 70)
    print(f"Test text length: {len(test_text)} characters")
    print(f"Number of iterations: {num_iterations}")
    print(f"Services: 4 (Input → Preprocessing → Analysis → Report)")
    print("=" * 70)
    
    # Warm-up run
    print("\nPerforming warm-up run...")
    run_single_test(test_text)
    time.sleep(1)
    
    # Benchmark runs
    print(f"\nRunning {num_iterations} benchmark iterations...")
    times = []
    successes = 0
    
    for i in range(num_iterations):
        print(f"  Iteration {i+1}/{num_iterations}...", end=' ')
        elapsed, success, word_count = run_single_test(test_text)
        times.append(elapsed)
        
        if success:
            successes += 1
            print(f"✓ {elapsed:.3f}s (words: {word_count})")
        else:
            print(f"✗ {elapsed:.3f}s (failed)")
        
        # Small delay between iterations
        if i < num_iterations - 1:
            time.sleep(0.5)
    
    # Calculate statistics
    print("\n" + "=" * 70)
    print("BENCHMARK RESULTS")
    print("=" * 70)
    print(f"Total iterations: {num_iterations}")
    print(f"Successful: {successes}")
    print(f"Failed: {num_iterations - successes}")
    print(f"\nTiming Statistics:")
    print(f"  Mean:     {statistics.mean(times):.3f}s")
    print(f"  Median:   {statistics.median(times):.3f}s")
    print(f"  Min:      {min(times):.3f}s")
    print(f"  Max:      {max(times):.3f}s")
    
    if len(times) > 1:
        print(f"  Std Dev:  {statistics.stdev(times):.3f}s")
    
    # Calculate throughput
    total_time = sum(times)
    throughput = num_iterations / total_time
    print(f"\nThroughput: {throughput:.2f} requests/second")
    print(f"Average latency: {statistics.mean(times)*1000:.1f}ms")
    
    print("=" * 70)
    
    # Performance breakdown estimate
    print("\nEstimated Pipeline Breakdown:")
    print("  Service 1 (Input):        ~10% of total time")
    print("  Service 2 (Preprocessing): ~30% of total time")
    print("  Service 3 (Analysis):      ~40% of total time")
    print("  Service 4 (Report):        ~15% of total time")
    print("  Network overhead:          ~5% of total time")
    print("=" * 70)
    
    return times


if __name__ == '__main__':
    # Check if custom iteration count provided
    num_iterations = 10
    if len(sys.argv) > 1:
        try:
            num_iterations = int(sys.argv[1])
        except ValueError:
            print("Usage: python benchmark.py [num_iterations]")
            sys.exit(1)
    
    # Wait for services to be ready
    print("Waiting for services to be ready...")
    time.sleep(3)
    
    run_benchmark(num_iterations)