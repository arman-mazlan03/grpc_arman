import grpc
from concurrent import futures
import time
import os
import sys
from collections import Counter

# Add proto directory to path
sys.path.insert(0, '/app')

import pipeline_pb2
import pipeline_pb2_grpc


class AnalysisServiceServicer(pipeline_pb2_grpc.AnalysisServiceServicer):
    def __init__(self):
        self.service4_address = os.getenv('SERVICE4_ADDRESS', 'service4-loadbalancer:8064')
        self.instance_id = os.getenv('INSTANCE_ID', 'unknown')
        print(f"[Service 3-{self.instance_id}] Initialized. Will forward to Service 4 at {self.service4_address}")

    def AnalyzeText(self, request, context):
        print(f"\n[Service 3-{self.instance_id}] ===== Received Analysis Request =====")
        print(f"[Service 3-{self.instance_id}] Request ID: {request.request_id}")
        print(f"[Service 3-{self.instance_id}] Text length: {len(request.text)} characters")
        print(f"[Service 3-{self.instance_id}] Instance: {self.instance_id}")
        
        start_time = time.time()
        
        try:
            # Analyze the text
            print(f"[Service 3-{self.instance_id}] Analyzing text...")
            
            # Tokenize
            words = request.text.split()
            total_words = len(words)
            
            # Count word frequencies
            word_counts = Counter(words)
            unique_words = len(word_counts)
            
            # Get top 10 most common words
            top_words = word_counts.most_common(10)
            
            print(f"[Service 3-{self.instance_id}] Total words: {total_words}")
            print(f"[Service 3-{self.instance_id}] Unique words: {unique_words}")
            print(f"[Service 3-{self.instance_id}] Top 5 words: {top_words[:5]}")
            
            # Prepare word frequencies for response
            word_frequencies = [
                pipeline_pb2.WordFrequency(word=word, count=count)
                for word, count in top_words
            ]
            
            # Forward to Service 4 (Report)
            print(f"[Service 3-{self.instance_id}] Forwarding to Service 4 (Report) at {self.service4_address}")
            
            with grpc.insecure_channel(self.service4_address) as channel:
                stub = pipeline_pb2_grpc.ReportServiceStub(channel)
                report_request = pipeline_pb2.ReportRequest(
                    request_id=request.request_id,
                    word_frequencies=word_frequencies,
                    total_words=total_words,
                    unique_words=unique_words,
                    original_length=0,  # These would be passed through in a real system
                    cleaned_length=len(request.text)
                )
                report_response = stub.GenerateReport(report_request, timeout=30)
            
            print(f"[Service 3-{self.instance_id}] Received response from Service 4")
            print(f"[Service 3-{self.instance_id}] Report generated in {report_response.processing_time:.3f}s")
            
            elapsed_time = time.time() - start_time
            print(f"[Service 3-{self.instance_id}] Processing time: {elapsed_time:.3f}s")
            
            return pipeline_pb2.AnalysisResponse(
                top_words=word_frequencies,
                total_words=total_words,
                unique_words=unique_words
            )
            
        except grpc.RpcError as e:
            print(f"[Service 3-{self.instance_id}] ERROR calling Service 4: {e.code()}: {e.details()}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(f"Failed to call report service: {e.details()}")
            raise
        except Exception as e:
            print(f"[Service 3-{self.instance_id}] ERROR: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise


def serve():
    port = os.getenv('PORT', '8053')
    instance_id = os.getenv('INSTANCE_ID', 'default')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pipeline_pb2_grpc.add_AnalysisServiceServicer_to_server(
        AnalysisServiceServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"[Service 3-{instance_id} - Analysis Service] Started on port {port}")
    print(f"[Service 3-{instance_id}] Waiting for requests...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()