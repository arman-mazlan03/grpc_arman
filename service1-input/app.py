import grpc
from concurrent import futures
import time
import os
import sys

sys.path.insert(0, '/app')
import pipeline_pb2
import pipeline_pb2_grpc

class TextInputServiceServicer(pipeline_pb2_grpc.TextInputServiceServicer):
    def __init__(self):
        self.service2_address = os.getenv('SERVICE2_ADDRESS', 'service2-loadbalancer:8062')
        self.instance_id = os.getenv('INSTANCE_ID', 'unknown')
        print(f"[Service 1-{self.instance_id}] Initialized. Will forward to Service 2 at {self.service2_address}")

    def ReceiveText(self, request, context):
        print(f"\n[Service 1-{self.instance_id}] ===== Received Text Request =====")
        print(f"[Service 1-{self.instance_id}] Request ID: {request.request_id}")
        print(f"[Service 1-{self.instance_id}] Text length: {len(request.text)} characters")
        print(f"[Service 1-{self.instance_id}] Instance: {self.instance_id}")
        
        start_time = time.time()
        
        try:
            print(f"[Service 1-{self.instance_id}] Forwarding to Service 2 (Preprocessing) at {self.service2_address}")
            
            # ADDED: Larger message options
            options = [
                ('grpc.max_send_message_length', 100 * 1024 * 1024),
                ('grpc.max_receive_message_length', 100 * 1024 * 1024),
            ]
            
            with grpc.insecure_channel(self.service2_address, options=options) as channel:
                stub = pipeline_pb2_grpc.PreprocessServiceStub(channel)
                clean_request = pipeline_pb2.CleanRequest(
                    text=request.text,
                    request_id=request.request_id
                )
                clean_response = stub.CleanText(clean_request, timeout=300)  # Longer timeout
            
            print(f"[Service 1-{self.instance_id}] Received response from Service 2")
            
            word_count = len(clean_response.cleaned_text.split())
            elapsed_time = time.time() - start_time
            
            print(f"[Service 1-{self.instance_id}] Total processing time: {elapsed_time:.3f}s")
            print(f"[Service 1-{self.instance_id}] Word count: {word_count}")
            
            return pipeline_pb2.TextResponse(
                status="success",
                message=f"Text processed successfully through pipeline in {elapsed_time:.3f}s",
                word_count=word_count
            )
            
        except grpc.RpcError as e:
            print(f"[Service 1-{self.instance_id}] ERROR calling Service 2: {e.code()}: {e.details()}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to call preprocessing service: {e.details()}")
            return pipeline_pb2.TextResponse(
                status="error",
                message=f"Pipeline failed: {e.details()}",
                word_count=0
            )
        except Exception as e:
            print(f"[Service 1-{self.instance_id}] ERROR: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pipeline_pb2.TextResponse(
                status="error",
                message=f"Internal error: {str(e)}",
                word_count=0
            )

def serve():
    port = os.getenv('PORT', '8051')
    instance_id = os.getenv('INSTANCE_ID', 'default')
    
    # ADDED: Server options for larger messages
    server_options = [
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024),
    ]
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10), options=server_options)
    pipeline_pb2_grpc.add_TextInputServiceServicer_to_server(TextInputServiceServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"[Service 1-{instance_id} - Text Input Service] Started on port {port} (100MB limit)")
    print(f"[Service 1-{instance_id}] Waiting for requests...")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()