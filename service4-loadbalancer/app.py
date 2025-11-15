import grpc
from concurrent import futures
import time
import os
import sys

sys.path.insert(0, '/app')
import pipeline_pb2
import pipeline_pb2_grpc

class Service4LoadBalancerServicer(pipeline_pb2_grpc.ReportServiceServicer):
    def __init__(self):
        self.service4_instances = [
            'service4a:8054',
            'service4b:8066', 
            'service4c:8068',
            'service4d:8070'
        ]
        self.current_index = 0
        self.instance_stats = {instance: {'requests': 0, 'errors': 0} for instance in self.service4_instances}
        print(f"[Load Balancer 4] Initialized with {len(self.service4_instances)} instances:")
        for instance in self.service4_instances:
            print(f"  - {instance}")

    def GenerateReport(self, request, context):
        start_index = self.current_index
        attempts = 0
        
        print(f"[Load Balancer 4] Routing request {request.request_id}")
        
        while attempts < len(self.service4_instances):
            instance = self.service4_instances[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.service4_instances)
            
            print(f"[Load Balancer 4] → Sending to {instance}")
            self.instance_stats[instance]['requests'] += 1
            
            try:
                options = [
                    ('grpc.max_send_message_length', 100 * 1024 * 1024),
                    ('grpc.max_receive_message_length', 100 * 1024 * 1024),
                ]
                
                with grpc.insecure_channel(instance, options=options) as channel:
                    stub = pipeline_pb2_grpc.ReportServiceStub(channel)
                    response = stub.GenerateReport(request, timeout=300)
                    print(f"[Load Balancer 4] ✓ Success from {instance}")
                    return response
                    
            except grpc.RpcError as e:
                self.instance_stats[instance]['errors'] += 1
                print(f"[Load Balancer 4] ✗ Error from {instance}: {e.details()}")
                attempts += 1
                continue
            except Exception as e:
                self.instance_stats[instance]['errors'] += 1
                print(f"[Load Balancer 4] ✗ Unexpected error from {instance}: {str(e)}")
                attempts += 1
                continue
        
        error_msg = f"All Service 4 instances failed after {attempts} attempts"
        print(f"[Load Balancer 4] 💥 {error_msg}")
        context.set_code(grpc.StatusCode.UNAVAILABLE)
        context.set_details(error_msg)
        raise grpc.RpcError(error_msg)

def serve():
    port = os.getenv('PORT', '8064')
    
    server_options = [
        ('grpc.max_send_message_length', 100 * 1024 * 1024),
        ('grpc.max_receive_message_length', 100 * 1024 * 1024),
    ]
    
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=20), options=server_options)
    pipeline_pb2_grpc.add_ReportServiceServicer_to_server(Service4LoadBalancerServicer(), server)
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"[Service 4 Load Balancer] Started on port {port} (100MB limit)")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()