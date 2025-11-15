import grpc
from concurrent import futures
import time
import os
import sys

sys.path.insert(0, '/app')
import pipeline_pb2
import pipeline_pb2_grpc

class Service1LoadBalancerServicer(pipeline_pb2_grpc.TextInputServiceServicer):
    def __init__(self):
        self.service1_instances = [
            'service1a:8051',
            'service1b:8055', 
            'service1c:8057',
            'service1d:8059'
        ]
        self.current_index = 0
        self.instance_stats = {instance: {'requests': 0, 'errors': 0} for instance in self.service1_instances}
        print(f"[Load Balancer 1] Initialized with {len(self.service1_instances)} instances:")
        for instance in self.service1_instances:
            print(f"  - {instance}")

    def ReceiveText(self, request, context):
        start_index = self.current_index
        attempts = 0
        
        request_size = len(request.text)
        print(f"[Load Balancer 1] Routing request {request.request_id} ({request_size} chars)")
        
        while attempts < len(self.service1_instances):
            instance = self.service1_instances[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.service1_instances)
            
            print(f"[Load Balancer 1] → Sending to {instance}")
            self.instance_stats[instance]['requests'] += 1
            
            try:
                options = [
                    ('grpc.max_send_message_length', 100 * 1024 * 1024),
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),
                ]
                
                with grpc.insecure_channel(instance, options=options) as channel:
                    stub = pipeline_pb2_grpc.TextInputServiceStub(channel)
                    response = stub.ReceiveText(request, timeout=300)
                    print(f"[Load Balancer 1] ✓ Success from {instance}")
                    return response
                    
            except grpc.RpcError as e:
                self.instance_stats[instance]['errors'] += 1
                print(f"[Load Balancer 1] ✗ Error from {instance}: {e.details()}")
                attempts += 1
                continue
            except Exception as e:
                self.instance_stats[instance]['errors'] += 1
                print(f"[Load Balancer 1] ✗ Unexpected error from {instance}: {str(e)}")
                attempts += 1
                continue
        
        error_msg = f"All Service 1 instances failed after {attempts} attempts"
        print(f"[Load Balancer 1] 💥 {error_msg}")
        context.set_code(grpc.StatusCode.UNAVAILABLE)
        context.set_details(error_msg)
        return pipeline_pb2.TextResponse(
            status="error",
            message=error_msg,
            word_count=0
        )

def serve():
    port = os.getenv('PORT', '8061')
    
    server_options = [
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024),
    ]
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20), options=server_options)
    pipeline_pb2_grpc.add_TextInputServiceServicer_to_server(Service1LoadBalancerServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"[Service 1 Load Balancer] Started on port {port} (100MB limit)")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()