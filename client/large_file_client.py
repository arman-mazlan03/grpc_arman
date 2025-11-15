import grpc
import sys
import time
import uuid
import os
import glob
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '/app')
import pipeline_pb2
import pipeline_pb2_grpc

class LargeFilePipelineClient:
    def __init__(self):
        self.service1_lb = 'service1-loadbalancer:8061'
        
    def split_text_into_chunks(self, text, num_chunks):
        """Split text into chunks optimized for large files"""
        print(f"Splitting {len(text):,} characters into {num_chunks} chunks...")
        
        # For large files, use character-based splitting
        chunk_size = len(text) // num_chunks
        chunks = []
        
        for i in range(num_chunks):
            start = i * chunk_size
            if i == num_chunks - 1:
                end = len(text)
            else:
                end = (i + 1) * chunk_size
            chunks.append(text[start:end])
        
        # Print chunk sizes
        for i, chunk in enumerate(chunks):
            word_count_estimate = len(chunk.split())
            print(f"  Chunk {i+1}: {len(chunk):,} chars, ~{word_count_estimate:,} words")
        
        return chunks
    
    def process_single_chunk(self, chunk_text, chunk_id, request_id_base):
        """Process chunk with larger message limits"""
        request_id = f"{request_id_base}_chunk{chunk_id}"
        
        print(f"[Pipeline {chunk_id}] Processing {len(chunk_text):,} characters...")
        start_time = time.time()
        
        try:
            # LARGER MESSAGE LIMITS
            options = [
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_receive_message_length', 100 * 1024 * 1024),
            ]
            
            with grpc.insecure_channel(self.service1_lb, options=options) as channel:
                stub = pipeline_pb2_grpc.TextInputServiceStub(channel)
                
                request = pipeline_pb2.TextRequest(
                    text=chunk_text,
                    request_id=request_id
                )
                
                # LONGER TIMEOUT
                response = stub.ReceiveText(request, timeout=300)
                
                elapsed_time = time.time() - start_time
                print(f"[Pipeline {chunk_id}] ✓ Completed in {elapsed_time:.3f}s - {response.word_count:,} words")
                
                return {
                    'chunk_id': chunk_id,
                    'success': True,
                    'word_count': response.word_count,
                    'processing_time': elapsed_time
                }
                
        except Exception as e:
            elapsed_time = time.time() - start_time
            print(f"[Pipeline {chunk_id}] ✗ Failed in {elapsed_time:.3f}s: {str(e)}")
            return {
                'chunk_id': chunk_id,
                'success': False,
                'error': str(e),
                'processing_time': elapsed_time
            }
    
    def process_large_file(self, filepath, num_parallel=4):
        """Process a single large file"""
        print(f"\n📖 Processing large file: {os.path.basename(filepath)}")
        
        # Read file
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        print(f"📊 File size: {len(content):,} characters, ~{len(content.split()):,} words")
        
        if len(content) > 100 * 1024 * 1024:
            print("⚠️  Warning: File is very large (>100MB), consider splitting it manually")
        
        # Split and process
        chunks = self.split_text_into_chunks(content, num_parallel)
        request_id_base = str(uuid.uuid4())[:8]
        
        print(f"🚀 Starting {num_parallel} parallel pipelines...")
        overall_start = time.time()
        
        results = []
        with ThreadPoolExecutor(max_workers=num_parallel) as executor:
            future_to_chunk = {
                executor.submit(self.process_single_chunk, chunk, i, request_id_base): i 
                for i, chunk in enumerate(chunks)
            }
            
            for future in as_completed(future_to_chunk):
                chunk_id = future_to_chunk[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Chunk {chunk_id} generated exception: {e}")
        
        overall_time = time.time() - overall_start
        
        # Calculate results
        successful = [r for r in results if r['success']]
        total_words = sum(r['word_count'] for r in successful)
        
        print(f"\n🎉 PROCESSING COMPLETE")
        print(f"Total time: {overall_time:.3f}s")
        print(f"Successful pipelines: {len(successful)}/{len(results)}")
        print(f"Total words processed: {total_words:,}")
        
        if successful and len(results) > 1:
            avg_time = sum(r['processing_time'] for r in results) / len(results)
            speedup = (avg_time * len(results)) / overall_time
            print(f"Parallel speedup: {speedup:.2f}x")
        
        return overall_time

def main():
    client = LargeFilePipelineClient()
    
    print("\n" + "="*80)
    print("🚀 LARGE FILE PROCESSING CLIENT")
    print("="*80)
    print("This client can process files up to 100MB")
    print("="*80)
    
    # Find all text files in datasets
    datasets_path = '/app/datasets'
    pattern = os.path.join(datasets_path, '*.txt')
    txt_files = glob.glob(pattern)
    
    if not txt_files:
        print("No .txt files found in datasets folder!")
        return
    
    print(f"\nFound {len(txt_files)} text file(s):")
    for filepath in txt_files:
        file_size = os.path.getsize(filepath)
        print(f"  - {os.path.basename(filepath)} ({file_size:,} bytes)")
    
    # Process each file
    for filepath in txt_files:
        print(f"\n{'#'*80}")
        print(f"📄 PROCESSING: {os.path.basename(filepath)}")
        print(f"{'#'*80}")
        
        # Test with different parallelism levels
        for parallelism in [2, 4]:
            print(f"\n🧪 Testing with {parallelism} pipelines")
            processing_time = client.process_large_file(filepath, parallelism)
            
            if parallelism < 4:
                print("\nWaiting 5 seconds before next test...")
                time.sleep(5)

if __name__ == '__main__':
    main()