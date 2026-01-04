from http.server import BaseHTTPRequestHandler
import json
import os
import sys
import tempfile
from urllib.parse import parse_qs
import io

# Add src to path to import our modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.extractor import PDFExtractor, process_pdf_to_excel

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {"status": "ok", "message": "PDF to Excel converter is running"}
            self.wfile.write(json.dumps(response).encode())
        elif self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            response = {
                "service": "PDF to Excel Converter",
                "endpoints": {
                    "health": "/api/health",
                    "convert": "/api/convert (POST with file and optional format parameter)"
                }
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        try:
            if self.path == '/api/convert':
                content_length = int(self.headers.get('Content-Length', 0))
                post_data = self.rfile.read(content_length)
                
                # Parse multipart form data
                content_type = self.headers.get('Content-Type', '')
                if 'multipart/form-data' not in content_type:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "Content-Type must be multipart/form-data"}).encode())
                    return
                
                # Extract boundary
                boundary = content_type.split("boundary=")[1].encode()
                parts = post_data.split(b'--' + boundary)
                
                file_content = None
                file_name = None
                format_type = 'auto'
                
                for part in parts:
                    if b'Content-Disposition' in part:
                        if b'filename=' in part:
                            # Extract file content
                            file_start = part.find(b'\r\n\r\n') + 4
                            file_end = part.rfind(b'\r\n')
                            file_content = part[file_start:file_end]
                            
                            # Extract filename
                            filename_start = part.find(b'filename="') + 10
                            filename_end = part.find(b'"', filename_start)
                            file_name = part[filename_start:filename_end].decode()
                        elif b'name="format"' in part:
                            # Extract format
                            format_start = part.find(b'\r\n\r\n') + 4
                            format_end = part.rfind(b'\r\n')
                            format_type = part[format_start:format_end].decode().strip()
                
                if not file_content or not file_name:
                    self.send_response(400)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.end_headers()
                    self.wfile.write(json.dumps({"error": "No file provided"}).encode())
                    return
                
                # Save temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
                    tmp.write(file_content)
                    tmp_path = tmp.name
                
                try:
                    # Process the PDF
                    if format_type == 'table':
                        df = PDFExtractor.extract_lab_report(tmp_path)
                    elif format_type == 'text':
                        text = PDFExtractor.extract_text(tmp_path)
                        import pandas as pd
                        df = pd.DataFrame({"Extracted Text": [text]})
                    else:
                        df = PDFExtractor.extract_lab_report(tmp_path)
                    
                    # Create Excel file in memory
                    excel_buffer = io.BytesIO()
                    df.to_excel(excel_buffer, index=False, sheet_name="Data")
                    excel_buffer.seek(0)
                    excel_data = excel_buffer.getvalue()
                    
                    # Send response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    self.send_header('Content-Disposition', f'attachment; filename="{file_name.replace(".pdf", "_extracted.xlsx")}"')
                    self.send_header('Access-Control-Allow-Origin', '*')
                    self.send_header('Content-Length', str(len(excel_data)))
                    self.end_headers()
                    self.wfile.write(excel_data)
                finally:
                    # Clean up temp file
                    if os.path.exists(tmp_path):
                        os.remove(tmp_path)
            else:
                self.send_response(404)
                self.end_headers()
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e), "type": type(e).__name__}).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
