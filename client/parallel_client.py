import grpc
import sys
import time
import uuid
import os
import glob
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, '/app')
import pipeline_pb2
import pipeline_pb2_grpc

class ParallelPipelineClient:
    def __init__(self):
        self.service1_lb = 'service1-loadbalancer:8061'
        self.num_parallel_pipelines = 4  # Can be 2, 4, 8, etc.
        
    def split_text_into_chunks(self, text, num_chunks):
        """Split text into chunks with optimized handling for large files"""
        text_length = len(text)
        
        # For very large files (>5MB), use character-based splitting
        if text_length > 5 * 1024 * 1024:
            print(f"📊 Large file detected: {text_length:,} characters, using optimized chunking...")
            chunk_size = text_length // num_chunks
            chunks = []
            
            for i in range(num_chunks):
                start = i * chunk_size
                if i == num_chunks - 1:  # Last chunk gets remaining characters
                    end = text_length
                else:
                    end = (i + 1) * chunk_size
                chunk_text = text[start:end]
                chunks.append(chunk_text)
        else:
            # For smaller files, use word-based splitting (better for analysis)
            words = text.split()
            chunk_size = len(words) // num_chunks
            chunks = []
            
            for i in range(num_chunks):
                start = i * chunk_size
                if i == num_chunks - 1:
                    end = len(words)
                else:
                    end = (i + 1) * chunk_size
                chunk_text = ' '.join(words[start:end])
                chunks.append(chunk_text)
            
        print(f"Split {text_length:,} characters into {num_chunks} chunks:")
        for i, chunk in enumerate(chunks):
            word_count = len(chunk.split())
            print(f"  Chunk {i+1}: {word_count:,} words, {len(chunk):,} chars")
            
        return chunks
    
    def process_single_chunk(self, chunk_text, chunk_id, request_id_base):
        """Process a single text chunk through the entire pipeline with large file support"""
        request_id = f"{request_id_base}_chunk{chunk_id}"
        
        print(f"\n[Pipeline {chunk_id}] Starting processing...")
        print(f"[Pipeline {chunk_id}] Chunk size: {len(chunk_text):,} chars, {len(chunk_text.split()):,} words")
        
        start_time = time.time()
        
        try:
            # ADDED: Larger message size options and longer timeout
            options = [
                ('grpc.max_send_message_length', 100 * 1024 * 1024),      # 100MB send limit
                ('grpc.max_receive_message_length', 100 * 1024 * 1024),   # 100MB receive limit
            ]
            
            with grpc.insecure_channel(self.service1_lb, options=options) as channel:
                stub = pipeline_pb2_grpc.TextInputServiceStub(channel)
                
                request = pipeline_pb2.TextRequest(
                    text=chunk_text,
                    request_id=request_id
                )
                
                # ADDED: Longer timeout for large files (5 minutes)
                response = stub.ReceiveText(request, timeout=300)
                
                elapsed_time = time.time() - start_time
                print(f"[Pipeline {chunk_id}] ✓ Completed in {elapsed_time:.3f}s - {response.word_count:,} words")
                
                return {
                    'chunk_id': chunk_id,
                    'success': True,
                    'word_count': response.word_count,
                    'processing_time': elapsed_time,
                    'status': response.status,
                    'message': response.message
                }
                
        except grpc.RpcError as e:
            elapsed_time = time.time() - start_time
            error_msg = f"gRPC Error: {e.code().name} - {e.details()}"
            print(f"[Pipeline {chunk_id}] ✗ Failed in {elapsed_time:.3f}s: {error_msg}")
            
            return {
                'chunk_id': chunk_id,
                'success': False,
                'error': error_msg,
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
    
    def process_parallel(self, text, num_parallel=None):
        """Process text through multiple parallel pipelines"""
        if num_parallel is None:
            num_parallel = self.num_parallel_pipelines
            
        print("\n" + "="*80)
        print("🚀 PARALLEL PIPELINE PROCESSING")
        print("="*80)
        print(f"Total text length: {len(text):,} characters")
        print(f"Number of parallel pipelines: {num_parallel}")
        print(f"Service instances: 4x each service type")
        print(f"Message size limit: 100MB per chunk")
        print(f"Timeout: 300 seconds")
        
        # Split text into chunks
        chunks = self.split_text_into_chunks(text, num_parallel)
        request_id_base = str(uuid.uuid4())[:8]
        
        print(f"\nStarting {num_parallel} parallel pipelines...")
        overall_start = time.time()
        
        # Process chunks in parallel
        results = []
        with ThreadPoolExecutor(max_workers=num_parallel) as executor:
            # Submit all chunks for parallel processing
            future_to_chunk = {
                executor.submit(self.process_single_chunk, chunk, i, request_id_base): i 
                for i, chunk in enumerate(chunks)
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_chunk):
                chunk_id = future_to_chunk[future]
                try:
                    result = future.result()
                    results.append(result)
                except Exception as e:
                    print(f"Chunk {chunk_id} generated exception: {e}")
                    results.append({
                        'chunk_id': chunk_id,
                        'success': False,
                        'error': str(e),
                        'processing_time': 0
                    })
        
        overall_time = time.time() - overall_start
        
        # Aggregate results
        return self.aggregate_results(results, chunks, overall_time)
    
    def aggregate_results(self, results, chunks, total_time):
        """Aggregate results from all parallel pipelines"""
        successful = [r for r in results if r['success']]
        failed = [r for r in results if not r['success']]
        
        total_words = sum(r['word_count'] for r in successful)
        avg_time = sum(r['processing_time'] for r in results) / len(results) if results else 0
        
        print("\n" + "="*80)
        print("📊 PARALLEL PROCESSING RESULTS")
        print("="*80)
        print(f"Total processing time: {total_time:.3f}s")
        print(f"Successful pipelines: {len(successful)}/{len(results)}")
        print(f"Failed pipelines: {len(failed)}/{len(results)}")
        print(f"Total words processed: {total_words:,}")
        print(f"Average pipeline time: {avg_time:.3f}s")
        
        speedup = 0
    
        if successful and len(successful) > 1:
            speedup = (avg_time * len(results)) / total_time if total_time > 0 else 1
            print(f"Parallel speedup: {speedup:.2f}x")
        
        print("\nPipeline Details:")
        for result in sorted(results, key=lambda x: x['chunk_id']):
            status = "✓" if result['success'] else "✗"
            words = result.get('word_count', 0) if result['success'] else "N/A"
            time_taken = result['processing_time']
            print(f"  Pipeline {result['chunk_id']}: {status} {time_taken:.3f}s, {words:,} words")
        
        if failed:
            print(f"\nFailures:")
            for fail in failed:
                print(f"  Pipeline {fail['chunk_id']}: {fail['error']}")
        
        return {
            'total_time': total_time,
            'successful_count': len(successful),
            'failed_count': len(failed),
            'total_words': total_words,
            'speedup': speedup,
            'pipeline_results': results
        }


def read_text_files(datasets_path='/app/datasets'):
    """Read all .txt files from datasets directory with better error handling"""
    text_files = []
    
    if not os.path.exists(datasets_path):
        print(f"WARNING: Datasets directory '{datasets_path}' not found!")
        return []
    
    pattern = os.path.join(datasets_path, '*.txt')
    txt_files = glob.glob(pattern)
    
    if not txt_files:
        print(f"WARNING: No .txt files found in '{datasets_path}'")
        return []
    
    print(f"Found {len(txt_files)} .txt file(s):")
    
    for file_path in txt_files:
        try:
            file_size = os.path.getsize(file_path)
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                filename = os.path.basename(file_path)
                
                if content:
                    text_files.append({
                        'filename': filename,
                        'content': content,
                        'file_path': file_path,
                        'file_size': file_size
                    })
                    word_count = len(content.split())
                    print(f"  - {filename} ({file_size:,} bytes, {len(content):,} chars, {word_count:,} words)")
                else:
                    print(f"  - {filename} (EMPTY - skipping)")
                    
        except UnicodeDecodeError:
            print(f"  - {os.path.basename(file_path)} (ENCODING ERROR - not UTF-8)")
        except Exception as e:
            print(f"  - ERROR reading {os.path.basename(file_path)}: {str(e)}")
    
    return text_files


def main():
    client = ParallelPipelineClient()
    
    print("\n" + "="*80)
    print("🚀 MASSIVE PARALLEL TEXT PROCESSING PIPELINE")
    print("="*80)
    print("This demonstrates:")
    print("• 4x instances of each service type")
    print("• Parallel processing of text chunks")  
    print("• Load balancing across service instances")
    print("• Horizontal scaling performance")
    print("• Large file support (up to 100MB per chunk)")
    print("• Optimized chunking for different file sizes")
    print("="*80)
    
    # Read text files
    print("\nScanning for text files...")
    text_files = read_text_files('/app/datasets')
    
    if not text_files:
        print("No text files found! Using sample text...")
        # Use a large sample text for demonstration
        sample_text = """
        Distributed systems are computer systems in which components located on networked computers 
        communicate and coordinate their actions by passing messages. The components interact with 
        each other in order to achieve a common goal. Three significant characteristics of distributed 
        systems are: concurrency of components, lack of a global clock, and independent failure of components.
        
        What is considered a distributed system? Examples of distributed systems vary from SOA-based 
        systems to massively multiplayer online games to peer-to-peer applications. A distributed system 
        may have a common goal, such as solving a large computational problem. Alternatively, each computer 
        may have its own user with individual needs, and the purpose of the distributed system is to 
        coordinate the use of shared resources or provide communication services to the users.
        
        Other typical properties of distributed systems include the following: The system has to tolerate 
        failures in individual computers. The structure of the system (network topology, network latency, 
        number of computers) is not known in advance, the system may consist of different kinds of computers 
        and network links, and the system may change during the execution of a distributed program.
        
        Distributed computing also refers to the use of distributed systems to solve computational problems. 
        In distributed computing, a problem is divided into many tasks, each of which is solved by one or 
        more computers, which communicate with each other via message passing.
        
        Parallel computing is a type of computation in which many calculations or the execution of processes 
        are carried out simultaneously. Large problems can often be divided into smaller ones, which can then 
        be solved at the same time. There are several different forms of parallel computing: bit-level, 
        instruction-level, data, and task parallelism. Parallelism has been employed for many years, 
        mainly in high-performance computing, but interest in it has grown lately due to the physical 
        constraints preventing frequency scaling.
        """ * 20  # Make it larger for better demonstration
        
        text_files = [{'filename': 'sample_distributed_systems.txt', 'content': sample_text}]
    
    # Process each file with different parallelism levels
    for file_info in text_files:
        print(f"\n\n{'#'*80}")
        print(f"📄 PROCESSING: {file_info['filename']}")
        if 'file_size' in file_info:
            print(f"📊 FILE SIZE: {file_info['file_size']:,} bytes")
        print(f"{'#'*80}")
        
        # Test different parallelism levels
        parallelism_levels = [1, 2, 4]
        
        for parallelism in parallelism_levels:
            print(f"\n{'='*60}")
            print(f"🧪 TESTING WITH {parallelism} PARALLEL PIPELINES")
            print(f"{'='*60}")
            
            result = client.process_parallel(file_info['content'], parallelism)
            
            # Wait between tests
            if parallelism < max(parallelism_levels):
                print(f"\nWaiting 3 seconds before next test...")
                time.sleep(3)


if __name__ == '__main__':
    main()