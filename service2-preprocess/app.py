import grpc
from concurrent import futures
import time
import os
import sys
import re

# Add proto directory to path
sys.path.insert(0, '/app')

import pipeline_pb2
import pipeline_pb2_grpc


class PreprocessServiceServicer(pipeline_pb2_grpc.PreprocessServiceServicer):
    def __init__(self):
        self.service3_address = os.getenv('SERVICE3_ADDRESS', 'service3:8053')
        print(f"[Service 2] Initialized. Will forward to Service 3 at {self.service3_address}")

    def CleanText(self, request, context):
        print(f"\n[Service 2] ===== Received Clean Request =====")
        print(f"[Service 2] Request ID: {request.request_id}")
        print(f"[Service 2] Text length: {len(request.text)} characters")
        
        start_time = time.time()
        
        try:
            # Clean the text
            print(f"[Service 2] Cleaning text...")
            original_length = len(request.text)
            
            # Convert to lowercase
            cleaned = request.text.lower()
            
            # Remove special characters but keep spaces and basic punctuation
            cleaned = re.sub(r'[^a-z0-9\s\']', ' ', cleaned)
            
            # Remove extra whitespace
            cleaned = ' '.join(cleaned.split())
            
            cleaned_length = len(cleaned)
            
            print(f"[Service 2] Original length: {original_length}")
            print(f"[Service 2] Cleaned length: {cleaned_length}")
            print(f"[Service 2] Cleaned preview: {cleaned[:100]}...")
            
            # Forward to Service 3 (Analysis)
            print(f"[Service 2] Forwarding to Service 3 (Analysis) at {self.service3_address}")
            
            with grpc.insecure_channel(self.service3_address) as channel:
                stub = pipeline_pb2_grpc.AnalysisServiceStub(channel)
                analysis_request = pipeline_pb2.AnalysisRequest(
                    text=cleaned,
                    request_id=request.request_id
                )
                analysis_response = stub.AnalyzeText(analysis_request, timeout=30)
            
            print(f"[Service 2] Received response from Service 3")
            print(f"[Service 2] Total words analyzed: {analysis_response.total_words}")
            print(f"[Service 2] Unique words: {analysis_response.unique_words}")
            
            elapsed_time = time.time() - start_time
            print(f"[Service 2] Processing time: {elapsed_time:.3f}s")
            
            return pipeline_pb2.CleanResponse(
                cleaned_text=cleaned,
                original_length=original_length,
                cleaned_length=cleaned_length
            )
            
        except grpc.RpcError as e:
            print(f"[Service 2] ERROR calling Service 3: {e.code()}: {e.details()}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to call analysis service: {e.details()}")
            raise
        except Exception as e:
            print(f"[Service 2] ERROR: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise


def serve():
    port = os.getenv('PORT', '8052')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pipeline_pb2_grpc.add_PreprocessServiceServicer_to_server(
        PreprocessServiceServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"[Service 2 - Preprocessing Service] Started on port {port}")
    print(f"[Service 2] Waiting for requests...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()