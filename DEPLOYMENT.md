# PDF to Excel Converter - Deployment Guide

## Quick Start on Vercel

This application is optimized for deployment on **Vercel** (serverless platform).

### Prerequisites
- GitHub account
- Vercel account (free tier available)
- This repository forked or cloned to your GitHub

### Step 1: Deploy to Vercel

1. Go to [vercel.com](https://vercel.com)
2. Click "New Project"
3. Import your GitHub repository `pdf-to-excel-extractor`
4. Vercel will auto-detect the configuration from `vercel.json`
5. Click "Deploy"

Your app will be live in ~1 minute!

### Step 2: Access Your App

Your application will be available at:
```
https://pdf-to-excel-extractor-[your-project].vercel.app
```

## Project Structure

```
pdf-to-excel-extractor/
├── src/
│   ├── extractor.py         # PDF extraction logic
│   ├── api.py               # Flask API endpoints
│   └── __pycache__/
├── public/
│   ├── index.html           # Web UI
│   ├── style.css            # Styling
│   └── script.js            # Client-side JavaScript
├── requirements.txt         # Python dependencies
├── vercel.json              # Vercel configuration
├── README.md                # Documentation
└── DEPLOYMENT.md            # This file
```

## Features

✅ **Multiple extraction formats:**
- Auto (detects tables and text)
- Tables only
- Text only

✅ **Supports:**
- Lab reports (CBC, Biochemistry, etc.)
- Invoices
- Tables in PDFs
- Text-based PDFs

✅ **Optimized for City Pathology Lab reports**

## API Endpoints

### Health Check
```
GET /api/health
```

Response:
```json
{
  "status": "ok",
  "message": "PDF to Excel converter is running"
}
```

### Convert PDF to Excel
```
POST /api/convert
```

Parameters:
- `file` (form-data): PDF file to convert
- `format` (optional): 'auto', 'table', or 'text' (default: 'auto')

Response: Excel file (XLSX format)

## Local Development

### Setup

1. Clone the repository:
```bash
git clone https://github.com/citypathologylaboratory-svg/pdf-to-excel-extractor.git
cd pdf-to-excel-extractor
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run locally (with Flask):
```bash
python src/api.py
```

5. Open browser:
```
http://localhost:5000
```

## Customization

### Modify PDF Parsing

Edit `src/extractor.py` in the `_parse_text_report()` method to customize how text-based reports are parsed.

For your City Pathology lab format:
```python
def _parse_text_report(text: str) -> pd.DataFrame:
    # Add your custom parsing logic here
    lines = text.split('\n')
    # Extract test names, values, units, references
```

### Customize UI

- **Colors & Styling**: Edit `public/style.css`
- **Text & Labels**: Edit `public/index.html`
- **Functionality**: Edit `public/script.js`

## Troubleshooting

### "Module not found" errors
- Ensure all dependencies in `requirements.txt` are installed
- Check Python version (3.9+ recommended)

### Vercel Deployment Issues
- Check `vercel.json` configuration
- Review build logs in Vercel dashboard
- Ensure `src/` folder exists with all Python files

### PDF Not Extracting Correctly
- Verify PDF format (pdfplumber works best with standard PDFs)
- Check if PDF has images (scanned PDFs need OCR)
- Modify parsing logic in `extractor.py` for your format

## Performance Notes

- **File Size Limit**: 50MB (configurable in `src/api.py`)
- **Processing Time**: ~1-5 seconds per PDF
- **Serverless Cold Start**: First request may take 5-10 seconds

## Support for Scanned PDFs

For scanned/image-based PDFs, add OCR:
```bash
pip install pytesseract pillow
```

Then modify `src/extractor.py` to use OCR.

## Next Steps

1. Deploy to Vercel
2. Test with your actual lab reports
3. Customize parsing for your specific format
4. Share the URL with your team

## License

This project is for City Pathology Laboratory use.
