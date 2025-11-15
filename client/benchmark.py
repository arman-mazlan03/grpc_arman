#!/usr/bin/env python3
"""
Enhanced Benchmark that uses dataset files
"""

import grpc
import sys
import time
import statistics
import uuid
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '/app')
import pipeline_pb2
import pipeline_pb2_grpc

def load_dataset_files(datasets_path='/app/datasets'):
    """Load text from dataset files"""
    text_files = []
    
    if not os.path.exists(datasets_path):
        print(f"⚠️  Dataset folder not found: {datasets_path}")
        return []
    
    pattern = os.path.join(datasets_path, '*.txt')
    txt_files = glob.glob(pattern)
    
    if not txt_files:
        print("⚠️  No .txt files found in datasets folder!")
        return []
    
    print(f"📁 Found {len(txt_files)} dataset file(s):")
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
            filename = os.path.basename(file_path)
            text_files.append({
                'filename': filename,
                'content': content,
                'file_size': len(content)
            })
            print(f"  - {filename} ({len(content):,} chars, ~{len(content.split()):,} words)")
        except Exception as e:
            print(f"  - ERROR reading {os.path.basename(file_path)}: {str(e)}")
    
    return text_files

def run_single_test(text, service1_address='service1-loadbalancer:8061'):
    """Run a single pipeline test"""
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        options = [
            ('grpc.max_send_message_length', 100 * 1024 * 1024),
            ('grpc.max_receive_message_length', 100 * 1024 * 1024),
        ]
        
        with grpc.insecure_channel(service1_address, options=options) as channel:
            stub = pipeline_pb2_grpc.TextInputServiceStub(channel)
            request = pipeline_pb2.TextRequest(
                text=text,
                request_id=request_id
            )
            response = stub.ReceiveText(request, timeout=300)
            
        elapsed_time = time.time() - start_time
        return elapsed_time, True, response.word_count
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"Error: {str(e)}")
        return elapsed_time, False, 0

def run_dataset_benchmark(num_iterations=10, num_parallel=4):
    """Run benchmark using actual dataset files"""
    
    print("\n" + "=" * 80)
    print("🚀 DATASET-BASED BENCHMARK")
    print("=" * 80)
    
    # Load dataset files
    dataset_files = load_dataset_files()
    
    if not dataset_files:
        print("Using fallback text (no dataset files found)")
        # Fallback to original text
        test_text = "Docker is a platform... " * 100
        file_info = {'filename': 'fallback.txt', 'content': test_text, 'file_size': len(test_text)}
    else:
        # Use the first dataset file
        file_info = dataset_files[0]
    
    test_text = file_info['content']
    
    print(f"📄 Using: {file_info['filename']}")
    print(f"📊 File size: {file_info['file_size']:,} characters")
    print(f"🔢 Iterations: {num_iterations}")
    print(f"⚡ Parallel: {num_parallel} requests")
    print("=" * 80)
    
    # Warm-up
    print("\n🔥 Warm-up run...")
    run_single_test(test_text[:1000])  # Small sample for warm-up
    time.sleep(2)
    
    # Benchmark
    print(f"\n🔄 Running benchmark...")
    all_times = []
    all_successes = 0
    
    batch_size = num_parallel
    batches = (num_iterations + batch_size - 1) // batch_size
    
    for batch in range(batches):
        batch_start = batch * batch_size
        batch_end = min((batch + 1) * batch_size, num_iterations)
        batch_iterations = batch_end - batch_start
        
        print(f"\n📦 Batch {batch+1}/{batches} ({batch_iterations} parallel):")
        
        batch_times = []
        batch_successes = 0
        
        with ThreadPoolExecutor(max_workers=num_parallel) as executor:
            future_to_iteration = {
                executor.submit(run_single_test, test_text): i 
                for i in range(batch_start, batch_end)
            }
            
            for future in as_completed(future_to_iteration):
                iteration = future_to_iteration[future]
                try:
                    elapsed, success, word_count = future.result()
                    batch_times.append(elapsed)
                    
                    if success:
                        batch_successes += 1
                        print(f"  Iteration {iteration+1}: ✓ {elapsed:.3f}s ({word_count} words)")
                    else:
                        print(f"  Iteration {iteration+1}: ✗ {elapsed:.3f}s (failed)")
                        
                except Exception as e:
                    print(f"  Iteration {iteration+1}: ✗ Exception: {str(e)}")
                    batch_times.append(0)
        
        all_times.extend(batch_times)
        all_successes += batch_successes
        
        if batch < batches - 1:
            print("⏳ Waiting 2 seconds...")
            time.sleep(2)
    
    # Results
    successful_times = [t for t in all_times if t > 0]
    
    print("\n" + "=" * 80)
    print("📊 DATASET BENCHMARK RESULTS")
    print("=" * 80)
    print(f"File: {file_info['filename']}")
    print(f"Success rate: {all_successes}/{num_iterations} ({(all_successes/num_iterations)*100:.1f}%)")
    
    if successful_times:
        print(f"\n⏱️  Performance:")
        print(f"  Average time: {statistics.mean(successful_times):.3f}s")
        print(f"  Throughput: {len(successful_times)/sum(successful_times):.2f} req/sec")
        print(f"  Best: {min(successful_times):.3f}s, Worst: {max(successful_times):.3f}s")
    
    print("=" * 80)
    return successful_times

if __name__ == '__main__':
    num_iterations = 10
    num_parallel = 4
    
    if len(sys.argv) > 1:
        num_iterations = int(sys.argv[1])
    if len(sys.argv) > 2:
        num_parallel = int(sys.argv[2])
    
    print("⏳ Waiting for services...")
    time.sleep(10)
    
    run_dataset_benchmark(num_iterations, num_parallel)