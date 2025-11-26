#!/usr/bin/env python3
"""
Enhanced Benchmark that tests different pipeline configurations
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

def run_parallel_test(text, num_parallel, service1_address='service1-loadbalancer:8061'):
    """Run parallel pipeline test with chunking"""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    
    def split_text_into_chunks(text, num_chunks):
        """Split text into chunks"""
        text_length = len(text)
        chunk_size = text_length // num_chunks
        chunks = []
        
        for i in range(num_chunks):
            start = i * chunk_size
            if i == num_chunks - 1:
                end = text_length
            else:
                end = (i + 1) * chunk_size
            chunks.append(text[start:end])
        
        return chunks
    
    chunks = split_text_into_chunks(text, num_parallel)
    request_id_base = str(uuid.uuid4())[:8]
    
    overall_start = time.time()
    results = []
    
    with ThreadPoolExecutor(max_workers=num_parallel) as executor:
        future_to_chunk = {
            executor.submit(run_single_test, chunk, service1_address): i 
            for i, chunk in enumerate(chunks)
        }
        
        for future in as_completed(future_to_chunk):
            chunk_id = future_to_chunk[future]
            try:
                elapsed, success, word_count = future.result()
                results.append({
                    'chunk_id': chunk_id,
                    'success': success,
                    'processing_time': elapsed,
                    'word_count': word_count
                })
            except Exception as e:
                print(f"Chunk {chunk_id} generated exception: {e}")
                results.append({
                    'chunk_id': chunk_id,
                    'success': False,
                    'processing_time': 0,
                    'word_count': 0
                })
    
    overall_time = time.time() - overall_start
    
    # Calculate results
    successful = [r for r in results if r['success']]
    total_words = sum(r['word_count'] for r in successful)
    
    return {
        'total_time': overall_time,
        'successful_count': len(successful),
        'total_words': total_words,
        'pipeline_results': results
    }

def run_comprehensive_benchmark():
    """Run comprehensive benchmark testing different pipeline configurations"""
    
    print("\n" + "=" * 80)
    print("🚀 COMPREHENSIVE PIPELINE BENCHMARK")
    print("=" * 80)
    
    # Load dataset files
    dataset_files = load_dataset_files()
    
    if not dataset_files:
        print("Using fallback text (no dataset files found)")
        test_text = "Docker is a platform for developing, shipping, and running applications in containers. " * 500
        file_info = {'filename': 'fallback.txt', 'content': test_text, 'file_size': len(test_text)}
    else:
        # Use the first dataset file
        file_info = dataset_files[0]
    
    test_text = file_info['content']
    
    print(f"📄 Using: {file_info['filename']}")
    print(f"📊 File size: {file_info['file_size']:,} characters")
    print(f"🔢 Testing pipelines: 1, 2, and 4 parallel pipelines")
    print(f"🔄 Runs per configuration: 3")
    print("=" * 80)
    
    # Test configurations
    pipeline_configs = [1, 2, 4]
    num_runs = 10
    
    # Store results
    all_results = {}
    
    for num_pipelines in pipeline_configs:
        print(f"\n\n{'#'*60}")
        print(f"🧪 TESTING {num_pipelines} PARALLEL PIPELINE(S)")
        print(f"{'#'*60}")
        
        config_times = []
        config_successes = []
        
        for run in range(num_runs):
            print(f"\n--- Run {run+1}/{num_runs} ---")
            
            if num_pipelines == 1:
                # Single pipeline test
                start_time = time.time()
                elapsed, success, word_count = run_single_test(test_text)
                total_time = time.time() - start_time
                result = {
                    'total_time': elapsed,
                    'successful_count': 1 if success else 0,
                    'total_words': word_count if success else 0
                }
            else:
                # Parallel pipeline test
                result = run_parallel_test(test_text, num_pipelines)
            
            config_times.append(result['total_time'])
            config_successes.append(result['successful_count'])
            
            print(f"  Time: {result['total_time']:.3f}s")
            print(f"  Success: {result['successful_count']}/{num_pipelines}")
            print(f"  Words processed: {result['total_words']:,}")
            
            # Wait between runs
            if run < num_runs - 1:
                print("  Waiting 2 seconds...")
                time.sleep(2)
        
        # Store configuration results
        all_results[num_pipelines] = {
            'times': config_times,
            'successes': config_successes,
            'avg_time': statistics.mean(config_times),
            'best_time': min(config_times),
            'worst_time': max(config_times),
            'success_rate': sum(config_successes) / (num_pipelines * num_runs) * 100
        }
    
    # Print comprehensive results
    print("\n" + "=" * 80)
    print("📊 COMPREHENSIVE BENCHMARK RESULTS")
    print("=" * 80)
    print(f"File: {file_info['filename']} ({file_info['file_size']:,} chars)")
    print(f"Configuration: {num_runs} runs per pipeline type")
    print("=" * 80)
    
    # Print comparison table
    print("\n🏆 GRPC PERFORMANCE COMPARISON:")
    print("┌────────────┬────────────┬────────────┬────────────┬────────────┬────────────┐")
    print("│ Pipelines  │  Avg Time  │  Best Time │ Worst Time │ Success %  │ Speedup    │")
    print("├────────────┼────────────┼────────────┼────────────┼────────────┼────────────┤")
    
    base_time = all_results[1]['avg_time']
    
    for num_pipelines in pipeline_configs:
        results = all_results[num_pipelines]
        speedup = base_time / results['avg_time'] if results['avg_time'] > 0 else 1
        
        print(f"│     {num_pipelines}      │  {results['avg_time']:7.3f}s  │  {results['best_time']:7.3f}s  │  {results['worst_time']:7.3f}s  │  {results['success_rate']:6.1f}%   │    {speedup:5.2f}x  │")
    
    print("└────────────┴────────────┴────────────┴────────────┴────────────┴────────────┘")
    
    # Print detailed results
    print(f"\n📈 DETAILED RESULTS:")
    for num_pipelines in pipeline_configs:
        results = all_results[num_pipelines]
        print(f"\n  {num_pipelines} Pipeline(s):")
        print(f"    • Average time: {results['avg_time']:.3f}s")
        print(f"    • Best time: {results['best_time']:.3f}s")
        print(f"    • Worst time: {results['worst_time']:.3f}s")
        print(f"    • Success rate: {results['success_rate']:.1f}%")
        print(f"    • Individual times: {[f'{t:.3f}s' for t in results['times']]}")
    
    # Performance analysis
    print(f"\n💡 PERFORMANCE ANALYSIS:")
    single_avg = all_results[1]['avg_time']
    double_avg = all_results[2]['avg_time']
    quad_avg = all_results[4]['avg_time']
    
    print(f"  • 2 pipelines vs 1: {single_avg/double_avg:.2f}x faster")
    print(f"  • 4 pipelines vs 1: {single_avg/quad_avg:.2f}x faster") 
    print(f"  • 4 pipelines vs 2: {double_avg/quad_avg:.2f}x faster")
    
    print("=" * 80)
    
    return all_results

if __name__ == '__main__':
    print("⏳ Waiting for services to be ready...")
    time.sleep(10)
    
    run_comprehensive_benchmark()