import grpc
import sys
import time
import uuid
import os
import glob

# Add proto directory to path
sys.path.insert(0, '/app')

import pipeline_pb2
import pipeline_pb2_grpc


def run_pipeline(text, service1_address='service1:8051'):
    """
    Runs the complete pipeline by calling Service 1.
    Service 1 will then delegate to Service 2, 3, and 4 automatically.
    """
    print("\n" + "=" * 70)
    print("CLIENT: Starting Pipeline Request")
    print("=" * 70)
    
    request_id = str(uuid.uuid4())[:8]
    print(f"CLIENT: Request ID: {request_id}")
    print(f"CLIENT: Text length: {len(text)} characters")
    print(f"CLIENT: Text preview: {text[:100]}...")
    print(f"CLIENT: Connecting to Service 1 at {service1_address}")
    
    start_time = time.time()
    
    try:
        with grpc.insecure_channel(service1_address) as channel:
            stub = pipeline_pb2_grpc.TextInputServiceStub(channel)
            
            request = pipeline_pb2.TextRequest(
                text=text,
                request_id=request_id
            )
            
            print(f"CLIENT: Sending request to Service 1...")
            response = stub.ReceiveText(request, timeout=60)
            
            total_time = time.time() - start_time
            
            print(f"\nCLIENT: ===== Pipeline Complete =====")
            print(f"CLIENT: Status: {response.status}")
            print(f"CLIENT: Message: {response.message}")
            print(f"CLIENT: Word Count: {response.word_count}")
            print(f"CLIENT: Total Time: {total_time:.3f}s")
            print("=" * 70)
            
            return response
            
    except grpc.RpcError as e:
        print(f"\nCLIENT: ERROR - gRPC Error")
        print(f"CLIENT: Code: {e.code()}")
        print(f"CLIENT: Details: {e.details()}")
        raise
    except Exception as e:
        print(f"\nCLIENT: ERROR - {str(e)}")
        raise


def read_text_files(datasets_path='/app/datasets'):
    """
    Read all .txt files from the datasets directory and return their contents.
    """
    text_files = []
    
    # Check if datasets directory exists
    if not os.path.exists(datasets_path):
        print(f"WARNING: Datasets directory '{datasets_path}' not found!")
        return []
    
    # Find all .txt files in the directory and subdirectories
    pattern = os.path.join(datasets_path, '**', '*.txt')
    txt_files = glob.glob(pattern, recursive=True)
    
    # Alternative: Only direct files in datasets folder
    if not txt_files:
        pattern = os.path.join(datasets_path, '*.txt')
        txt_files = glob.glob(pattern)
    
    if not txt_files:
        print(f"WARNING: No .txt files found in '{datasets_path}'")
        return []
    
    print(f"Found {len(txt_files)} .txt file(s):")
    
    for file_path in txt_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                filename = os.path.basename(file_path)
                
                if content:  # Only add non-empty files
                    text_files.append({
                        'filename': filename,
                        'content': content,
                        'file_path': file_path
                    })
                    print(f"  - {filename} ({len(content)} characters)")
                else:
                    print(f"  - {filename} (EMPTY - skipping)")
                    
        except Exception as e:
            print(f"  - ERROR reading {os.path.basename(file_path)}: {str(e)}")
    
    return text_files


def main():
    print("\n" + "=" * 70)
    print("gRPC DISTRIBUTED PIPELINE DEMONSTRATION")
    print("=" * 70)
    print("\nThis client will demonstrate:")
    print("1. Service 1 (Input) receives text from client")
    print("2. Service 1 delegates to Service 2 (Preprocessing)")
    print("3. Service 2 delegates to Service 3 (Analysis)")
    print("4. Service 3 delegates to Service 4 (Report)")
    print("5. Results flow back through the chain to the client")
    print("=" * 70)
    
    # Read all text files from datasets directory
    print("\nScanning for text files in datasets directory...")
    text_files = read_text_files('/app/datasets')
    
    if not text_files:
        print("\nNo text files found! Using fallback sample texts...")
        # Fallback to original sample texts if no files found
        sample_texts = [
            """
            The quick brown fox jumps over the lazy dog. This is a sample text 
            for testing the distributed gRPC pipeline. The pipeline consists of 
            four different services that work together to process and analyze text.
            Service 1 receives the text, Service 2 preprocesses it, Service 3 
            analyzes it, and Service 4 generates a report.
            """,
            """
            Docker is a platform for developing, shipping, and running applications 
            in containers. gRPC is a high-performance RPC framework that can run in 
            any environment. Together, they enable building distributed microservices 
            that are scalable and efficient.
            """
        ]
        text_files = [{'filename': f'fallback_{i+1}.txt', 'content': text.strip()} 
                     for i, text in enumerate(sample_texts)]
    
    # Run pipeline for each text file
    total_files = len(text_files)
    successful_runs = 0
    
    for i, file_info in enumerate(text_files, 1):
        print(f"\n\n{'#' * 70}")
        print(f"# PROCESSING FILE {i}/{total_files}: {file_info['filename']}")
        print(f"{'#' * 70}")
        
        try:
            response = run_pipeline(file_info['content'])
            successful_runs += 1
            
            # Wait a bit between tests (except for the last one)
            if i < total_files:
                print(f"\nWaiting 2 seconds before next file...")
                time.sleep(2)
                
        except Exception as e:
            print(f"ERROR processing {file_info['filename']}: {str(e)}")
            continue
    
    print("\n" + "=" * 70)
    print("ALL FILES PROCESSED")
    print("=" * 70)
    print(f"Successful: {successful_runs}/{total_files} files")
    
    # Summary of processed files
    if successful_runs > 0:
        print(f"\nProcessed files:")
        for file_info in text_files:
            print(f"  ✓ {file_info['filename']}")
    
    print("=" * 70)


if __name__ == '__main__':
    main()