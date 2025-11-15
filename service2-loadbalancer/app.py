import grpc
from concurrent import futures
import time
import os
import sys

sys.path.insert(0, '/app')
import pipeline_pb2
import pipeline_pb2_grpc

class Service2LoadBalancerServicer(pipeline_pb2_grpc.PreprocessServiceServicer):
    def __init__(self):
        # List of Service 2 instances
        self.service2_instances = [
            'service2a:8052',
            'service2b:8056', 
            'service2c:8058',
            'service2d:8060'
        ]
        self.current_index = 0
        self.instance_stats = {instance: {'requests': 0, 'errors': 0} for instance in self.service2_instances}
        print(f"[Load Balancer 2] Initialized with {len(self.service2_instances)} instances:")
        for instance in self.service2_instances:
            print(f"  - {instance}")

    def CleanText(self, request, context):
        # Round-robin load balancing
        start_index = self.current_index
        attempts = 0
        
        while attempts < len(self.service2_instances):
            instance = self.service2_instances[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.service2_instances)
            
            print(f"[Load Balancer 2] Routing request {request.request_id} to {instance}")
            self.instance_stats[instance]['requests'] += 1
            
            try:
                with grpc.insecure_channel(instance) as channel:
                    stub = pipeline_pb2_grpc.PreprocessServiceStub(channel)
                    response = stub.CleanText(request, timeout=60)
                    print(f"[Load Balancer 2] ✓ Success from {instance}")
                    return response
                    
            except grpc.RpcError as e:
                self.instance_stats[instance]['errors'] += 1
                print(f"[Load Balancer 2] ✗ Error from {instance}: {e.details()}")
                attempts += 1
                continue
            except Exception as e:
                self.instance_stats[instance]['errors'] += 1
                print(f"[Load Balancer 2] ✗ Unexpected error from {instance}: {str(e)}")
                attempts += 1
                continue
        
        # All instances failed
        error_msg = f"All Service 2 instances failed after {attempts} attempts"
        print(f"[Load Balancer 2] 💥 {error_msg}")
        context.set_code(grpc.StatusCode.UNAVAILABLE)
        context.set_details(error_msg)
        raise grpc.RpcError(error_msg)

def serve():
    port = os.getenv('PORT', '8062')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20))
    pipeline_pb2_grpc.add_PreprocessServiceServicer_to_server(
        Service2LoadBalancerServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"[Service 2 Load Balancer] Started on port {port}")
    print(f"[Service 2 Load Balancer] Ready to distribute traffic to Service 2 instances")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()