from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
import os
import tempfile
from extractor import PDFExtractor, process_pdf_to_excel

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
        
        # Process the PDF
        excel_buffer, df = process_pdf_to_excel(file, output_format)
        
        return send_file(
            excel_buffer,
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            as_attachment=True,
            download_name=f"{secure_filename(file.filename.rsplit('.', 1)[0])}_extracted.xlsx"
        )
    
    except Exception as e:
        return jsonify({"error": str(e), "type": type(e).__name__}), 500

@app.route('/', methods=['GET'])
def index():
    return {
        "service": "PDF to Excel Converter",
        "endpoints": {
            "health": "/api/health",
            "convert": "/api/convert (POST with file and optional format parameter)"
        }
    }

if __name__ == '__main__':
    app.run(debug=False)
