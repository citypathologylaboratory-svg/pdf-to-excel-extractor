# OCR to Horizontal Excel Implementation Guide

## Overview
Add OCR (Optical Character Recognition) capabilities to convert scanned PDFs and image-based PDFs to Excel with horizontal layout organization.

## Architecture

### 1. OCR Module (`src/ocr_processor.py`)

**Dependencies to add to requirements.txt:**
```
pytesseract==0.3.10
Pillow==10.1.0
pdf2image==1.16.3
opencv-python==4.8.1.78
```

**OCR Processor Class:**
```python
from pytesseract import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import cv2
import numpy as np

class OCRProcessor:
    def __init__(self):
        self.tesseract_path = None  # Auto-detect or set path
        
    def pdf_to_images(self, pdf_path: str) -> List[Image.Image]:
        """Convert PDF pages to images for OCR processing"""
        images = convert_from_path(pdf_path, dpi=300)
        return images
        
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Preprocess image for better OCR accuracy"""
        # Convert to OpenCV format
        cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Grayscale conversion
        gray = cv2.cvtColor(cv_image, cv2.COLOR_BGR2GRAY)
        
        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Thresholding
        _, threshold = cv2.threshold(denoised, 150, 255, cv2.THRESH_BINARY)
        
        return Image.fromarray(threshold)
        
    def extract_text_with_boxes(self, image: Image.Image) -> List[Dict]:
        """Extract text with bounding box information"""
        data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
        
        extracted = []
        for i in range(len(data['text'])):
            if data['text'][i].strip():
                extracted.append({
                    'text': data['text'][i],
                    'x': data['left'][i],
                    'y': data['top'][i],
                    'width': data['width'][i],
                    'height': data['height'][i],
                    'confidence': data['conf'][i]
                })
        return extracted
        
    def process_scanned_pdf(self, pdf_path: str) -> str:
        """Process scanned PDF and return extracted text"""
        images = self.pdf_to_images(pdf_path)
        full_text = ""
        
        for i, image in enumerate(images):
            # Preprocess
            processed = self.preprocess_image(image)
            
            # Extract text
            text = pytesseract.image_to_string(processed, lang='eng')
            full_text += f"\n--- Page {i+1} ---\n{text}"
            
        return full_text
```

### 2. Horizontal Layout Formatter (`src/horizontal_formatter.py`)

**Purpose:** Organize OCR-extracted data in horizontal (row-based) layout instead of vertical

```python
import pandas as pd
from typing import List, Dict

class HorizontalExcelFormatter:
    def __init__(self):
        self.data_rows = []
        
    def parse_ocr_text_to_rows(self, text: str) -> List[Dict]:
        """Parse OCR text into structured rows"""
        lines = text.strip().split('\n')
        rows = []
        
        for line in lines:
            if line.strip():
                # Split by tabs or multiple spaces
                fields = line.split('\t') or line.split('  ')
                row_data = {f'Column_{i}': field.strip() for i, field in enumerate(fields)}
                rows.append(row_data)
                
        return rows
        
    def create_horizontal_dataframe(self, ocr_results: List[Dict]) -> pd.DataFrame:
        """Create DataFrame with horizontal layout"""
        # Each OCR result becomes a row
        df = pd.DataFrame(ocr_results)
        
        # Transpose if needed for specific formats
        # df = df.T  # Uncomment if you need transposed layout
        
        return df
        
    def extract_medical_data_horizontally(self, text: str) -> pd.DataFrame:
        """Format medical test results horizontally"""
        # Example for medical lab reports
        rows = []
        lines = text.strip().split('\n')
        
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                rows.append({'Parameter': key.strip(), 'Value': value.strip()})
                
        return pd.DataFrame(rows)
        
    def extract_table_structure(self, bbox_data: List[Dict]) -> pd.DataFrame:
        """Extract table structure from bounding box data"""
        # Group by Y coordinate (vertical position)
        sorted_data = sorted(bbox_data, key=lambda x: x['y'])
        
        rows = []
        current_row = []
        current_y = None
        
        for item in sorted_data:
            if current_y is None or abs(item['y'] - current_y) < 20:
                current_row.append(item)
                current_y = item['y']
            else:
                rows.append(current_row)
                current_row = [item]
                current_y = item['y']
                
        # Sort each row by X coordinate and create DataFrame
        formatted_rows = []
        for row in rows:
            sorted_row = sorted(row, key=lambda x: x['x'])
            formatted_rows.append({f'Col_{i}': item['text'] for i, item in enumerate(sorted_row)})
            
        return pd.DataFrame(formatted_rows)
```

### 3. Updated PDF Extractor (`src/pdf_extractor.py` - modifications)

```python
from .ocr_processor import OCRProcessor
from .horizontal_formatter import HorizontalExcelFormatter

class PDFtoExcelConverter:
    def __init__(self, format_type: str = 'generic', enable_ocr: bool = False):
        self.format_type = format_type
        self.enable_ocr = enable_ocr
        self.ocr_processor = OCRProcessor() if enable_ocr else None
        self.horizontal_formatter = HorizontalExcelFormatter() if enable_ocr else None
        self.excel_writer = ExcelWriter()
        
    def is_scanned_pdf(self, pdf_path: str) -> bool:
        """Detect if PDF is scanned (image-based)"""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page in pdf_reader.pages:
                    if page.extract_text().strip():
                        return False
            return True
        except:
            return True
            
    def convert_pdf(self, input_pdf: str, output_excel: str, use_ocr: bool = None) -> None:
        """Convert PDF to Excel with optional OCR"""
        use_ocr = use_ocr if use_ocr is not None else self.enable_ocr
        
        if use_ocr or self.is_scanned_pdf(input_pdf):
            # Use OCR pipeline
            text = self.ocr_processor.process_scanned_pdf(input_pdf)
            df = self.horizontal_formatter.create_horizontal_dataframe(
                self.horizontal_formatter.parse_ocr_text_to_rows(text)
            )
        else:
            # Use traditional text extraction
            text = self.extract_text_from_pdf(input_pdf)
            data = self.parse_extracted_data(text)
            df = pd.DataFrame([data])
            
        self.excel_writer.write_dataframe(df, output_excel)
```

### 4. Frontend Updates (`public/index.html` or React component)

**Add OCR toggle to UI:**
```html
<div class="extraction-options">
  <label>
    <input type="radio" name="mode" value="auto" checked>
    Auto (detect text/OCR)
  </label>
  <label>
    <input type="radio" name="mode" value="text">
    Text Extraction Only
  </label>
  <label>
    <input type="radio" name="mode" value="ocr">
    OCR (Scanned PDFs)
  </label>
  <label>
    <input type="radio" name="mode" value="horizontal">
    OCR + Horizontal Layout
  </label>
</div>
```

### 5. API Updates (`api/convert.py`)

```python
@app.post("/api/convert")
async def convert_pdf(file: UploadFile, mode: str = "auto"):
    """API endpoint with OCR support"""
    
    pdf_path = f"/tmp/{file.filename}"
    with open(pdf_path, "wb") as f:
        f.write(await file.read())
        
    converter = PDFtoExcelConverter(
        format_type="medical",
        enable_ocr=(mode in ["ocr", "horizontal", "auto"])
    )
    
    output_path = pdf_path.replace(".pdf", ".xlsx")
    
    if mode == "horizontal":
        # Use horizontal formatter
        converter.convert_pdf(pdf_path, output_path, use_ocr=True)
    else:
        converter.convert_pdf(pdf_path, output_path, use_ocr=(mode == "ocr"))
        
    return FileResponse(output_path, filename=output_path.split("/")[-1])
```

## Installation Steps

1. **Update requirements.txt:**
```bash
pip install pytesseract pdf2image Pillow opencv-python
```

2. **System Dependencies:**
   - **Windows:** Download Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
   - **Ubuntu/Debian:** `sudo apt-get install tesseract-ocr`
   - **macOS:** `brew install tesseract`

3. **Create new modules:**
   - `src/ocr_processor.py`
   - `src/horizontal_formatter.py`

4. **Update existing modules:**
   - Modify `src/pdf_extractor.py`
   - Modify API endpoint
   - Update frontend UI

## Testing Strategy

1. Test with scanned medical lab reports
2. Test with image-based invoices
3. Test horizontal layout formatting
4. Performance testing on large PDFs
5. Accuracy testing with different DPI settings

## Performance Considerations

- OCR is CPU-intensive; consider caching results
- Use DPI optimization (300 DPI is standard)
- Implement async processing for large files
- Consider serverless function timeout limits (Vercel: 10s, 60s for Pro)

## Future Enhancements

- Language detection for multi-language documents
- Handwriting recognition
- Table detection and preservation
- Confidence scoring UI
- Batch OCR processing
- Cloud-based OCR (Google Vision API, AWS Textract)
