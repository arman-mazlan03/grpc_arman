import grpc
from concurrent import futures
import time
import os
import sys

# Add proto directory to path
sys.path.insert(0, '/app')

import pipeline_pb2
import pipeline_pb2_grpc


class ReportServiceServicer(pipeline_pb2_grpc.ReportServiceServicer):
    def __init__(self):
        print(f"[Service 4] Initialized. This is the final service in the pipeline.")

    def GenerateReport(self, request, context):
        print(f"\n[Service 4] ===== Received Report Request =====")
        print(f"[Service 4] Request ID: {request.request_id}")
        print(f"[Service 4] Total words: {request.total_words}")
        print(f"[Service 4] Unique words: {request.unique_words}")
        
        start_time = time.time()
        
        try:
            # Generate the report
            print(f"[Service 4] Generating report...")
            
            report_lines = []
            report_lines.append("=" * 60)
            report_lines.append("TEXT ANALYSIS REPORT")
            report_lines.append("=" * 60)
            report_lines.append(f"Request ID: {request.request_id}")
            report_lines.append(f"\nSTATISTICS:")
            report_lines.append(f"  Total Words: {request.total_words}")
            report_lines.append(f"  Unique Words: {request.unique_words}")
            report_lines.append(f"  Original Length: {request.original_length} chars")
            report_lines.append(f"  Cleaned Length: {request.cleaned_length} chars")
            
            if request.word_frequencies:
                report_lines.append(f"\nTOP {len(request.word_frequencies)} MOST FREQUENT WORDS:")
                for i, wf in enumerate(request.word_frequencies, 1):
                    report_lines.append(f"  {i}. '{wf.word}' - {wf.count} times")
            
            processing_time = time.time() - start_time
            report_lines.append(f"\nReport generated in {processing_time:.3f} seconds")
            report_lines.append("=" * 60)
            
            report = "\n".join(report_lines)
            
            print(f"[Service 4] Report generated successfully")
            print(f"[Service 4] Processing time: {processing_time:.3f}s")
            print(f"\n[Service 4] Generated Report:")
            print(report)
            
            return pipeline_pb2.ReportResponse(
                report=report,
                processing_time=processing_time
            )
            
        except Exception as e:
            print(f"[Service 4] ERROR: {str(e)}")
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            raise


def serve():
    port = os.getenv('PORT', '8054')
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    pipeline_pb2_grpc.add_ReportServiceServicer_to_server(
        ReportServiceServicer(), server
    )
    server.add_insecure_port(f'[::]:{port}')
    server.start()
    print(f"[Service 4 - Report Service] Started on port {port}")
    print(f"[Service 4] Waiting for requests...")
    server.wait_for_termination()


if __name__ == '__main__':
    serve()