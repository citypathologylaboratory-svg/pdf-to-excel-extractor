from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import sys
import tempfile
import io
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.extractor import PDFExtractor

app = Flask(__name__)
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "PDF to Excel converter is running"})

@app.route('/api/convert', methods=['POST'])
def convert_pdf():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({"error": "Only PDF files allowed"}), 400
        
        output_format = request.form.get('format', 'auto')
        if output_format not in ['auto', 'table', 'text']:
            output_format = 'auto'
        
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
            file.save(tmp.name)
            tmp_path = tmp.name
        
        try:
            # Process the PDF
            if output_format == 'table':
                df = PDFExtractor.extract_lab_report(tmp_path)
            elif output_format == 'text':
                text = PDFExtractor.extract_text(tmp_path)
                import pandas as pd
                df = pd.DataFrame({"Extracted Text": [text]})
            else:
                df = PDFExtractor.extract_lab_report(tmp_path)
            
            # Create Excel in memory
            excel_buffer = io.BytesIO()
            df.to_excel(excel_buffer, index=False, sheet_name="Data")
            excel_buffer.seek(0)
            
            # Return Excel file
            return send_file(
                excel_buffer,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f"{secure_filename(file.filename.rsplit('.', 1)[0])}_extracted.xlsx"
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
    except Exception as e:
        return jsonify({"error": str(e), "type": type(e).__name__}), 500

@app.route('/', methods=['GET'])
def index():
    return jsonify({
        "service": "PDF to Excel Converter",
        "endpoints": {
            "health": "/api/health",
            "convert": "/api/convert (POST with file)"
        }
    })

@app.route('/api/convert', methods=['OPTIONS'])
def handle_options():
    return '', 204
