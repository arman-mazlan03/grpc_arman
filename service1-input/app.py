import grpc
from concurrent import futures
import time
import os
import sys

# Add proto directory to path
sys.path.insert(0, '/app')

import pipeline_pb2
import pipeline_pb2_grpc


class TextInputServiceServicer(pipeline_pb2_grpc.TextInputServiceServicer):
    def __init__(self):
        self.service2_address = os.getenv('SERVICE2_ADDRESS', 'service2:8052')
        print(f"[Service 1] Initialized. Will forward to Service 2 at {self.service2_address}")

    def ReceiveText(self, request, context):
        print(f"\n[Service 1] ===== Received Text Request =====")
        print(f"[Service 1] Request ID: {request.request_id}")
        print(f"[Service 1] Text length: {len(request.text)} characters")
        print(f"[Service 1] Text preview: {request.text[:100]}...")
        
        start_time = time.time()
        
        try:
            # Forward to Service 2 (Preprocessing)
            print(f"[Service 1] Forwarding to Service 2 (Preprocessing) at {self.service2_address}")
            
            with grpc.insecure_channel(self.service2_address) as channel:
                stub = pipeline_pb2_grpc.PreprocessServiceStub(channel)
                clean_request = pipeline_pb2.CleanRequest(
                    text=request.text,
                    request_id=request.request_id
                )
                clean_response = stub.CleanText(clean_request, timeout=30)
            
            print(f"[Service 1] Received response from Service 2")
            print(f"[Service 1] Original length: {clean_response.original_length}")
            print(f"[Service 1] Cleaned length: {clean_response.cleaned_length}")
            
            # Count words in cleaned text
            word_count = len(clean_response.cleaned_text.split())
            
            elapsed_time = time.time() - start_time
            print(f"[Service 1] Total processing time: {elapsed_time:.3f}s")
            print(f"[Service 1] Word count: {word_count}")
            
            return pipeline_pb2.TextResponse(
                status="success",
                message=f"Text processed successfully through pipeline in {elapsed_time:.3f}s",
                word_count=word_count
            )
            
        except grpc.RpcError as e:
            print(f"[Service 1] ERROR calling Service 2: {e.code()}: {e.details()}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to call preprocessing service: {e.details()}")
            return pipeline_pb2.TextResponse(
                status="error",
                message=f"Pipeline failed: {e.details()}",
                word_count=0
            )
        except Exception as e:
            print(f"[Service 1] ERROR: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pipeline_pb2.TextResponse(
                status="error",
                message=f"Internal error: {str(e)}",
                word_count=0
            )


def serve():
    port = os.getenv('PORT', '8051')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pipeline_pb2_grpc.add_TextInputServiceServicer_to_server(
        TextInputServiceServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"[Service 1 - Text Input Service] Started on port {port}")
    print(f"[Service 1] Waiting for requests...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()