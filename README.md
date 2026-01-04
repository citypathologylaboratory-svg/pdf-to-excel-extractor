# PDF to Excel Extractor

A powerful Python tool to extract data from multiple PDF files and convert them into properly formatted Excel spreadsheets with column-wise organization. Ideal for batch processing medical lab reports, invoices, receipts, and other document types.

## Features

- **Batch Processing**: Extract data from multiple PDFs at once
- **Column-Wise Organization**: Automatically organize extracted data into Excel columns
- **Medical Lab Reports**: Special support for lab test results and medical documents
- **Invoice Processing**: Extract invoice details (amount, date, vendor, etc.)
- **Flexible Parsing**: Customizable extraction patterns for different document types
- **Error Handling**: Robust handling of corrupted or problematic PDFs
- **Progress Tracking**: Real-time progress indicators for large batch operations
- **Excel Export**: Clean, formatted Excel output with headers and styling

## Installation

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone https://github.com/citypathologylaboratory-svg/pdf-to-excel-extractor.git
cd pdf-to-excel-extractor
```

2. Create a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\\Scripts\\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```python
from pdf_extractor import PDFtoExcelConverter

# Create converter instance
converter = PDFtoExcelConverter()

# Convert single PDF
converter.convert_pdf('path/to/file.pdf', 'output.xlsx')

# Convert multiple PDFs
converter.batch_convert('path/to/pdf/folder', 'output_folder')
```

### Command Line Usage

```bash
# Single file conversion
python main.py --input file.pdf --output result.xlsx

# Batch conversion
python main.py --input ./pdfs --output ./xlsx --batch

# With custom settings
python main.py --input pdfs/ --output results/ --batch --format medical
```

## Project Structure

```
pdf-to-excel-extractor/
├── src/
│   ├── __init__.py
│   ├── pdf_extractor.py          # Main extraction logic
│   ├── excel_writer.py            # Excel file generation
│   ├── data_parser.py             # Data parsing utilities
│   └── config.py                  # Configuration settings
├── tests/
│   ├── test_pdf_extractor.py
│   ├── test_excel_writer.py
│   └── test_data_parser.py
├── examples/
│   ├── sample_lab_report.pdf
│   ├── sample_invoice.pdf
│   └── example_usage.py
├── main.py                        # Command-line interface
├── requirements.txt               # Python dependencies
├── README.md                      # This file
└── .gitignore                     # Git ignore file
```

## Supported File Formats

- **Input**: PDF files (scanned and searchable PDFs)
- **Output**: XLSX (Microsoft Excel), CSV (optional)

## Use Cases

### Medical Laboratory
- Extract patient names, test results, reference ranges
- Organize lab reports by date and patient
- Generate consolidated reports for analysis

### Invoice Processing
- Extract invoice numbers, dates, amounts
- Vendor information extraction
- Payment term organization

### Financial Documents
- Receipt data extraction
- Bank statement processing
- Transaction history compilation

## Configuration

Edit `src/config.py` to customize:
- PDF reading parameters
- Excel formatting styles
- Column definitions
- Data validation rules
- Error handling behavior

## Troubleshooting

### Common Issues

1. **"No text found in PDF"**
   - The PDF may be image-based. Consider using OCR preprocessing
   - Ensure the PDF is not password-protected

2. **"Encoding errors"**
   - Check file encoding in config.py
   - Verify PDF text encoding

3. **"Memory error with large PDFs"**
   - Process PDFs in smaller batches
   - Increase available system memory

## Performance Tips

- Process large batches in chunks (100 PDFs at a time)
- Use SSD storage for better I/O performance
- Close other applications to free up memory
- Enable parallel processing for faster batch operations

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review example files in `/examples` folder

## Roadmap

- [ ] OCR support for image-based PDFs
- [ ] Web interface for easier batch processing
- [ ] API endpoint for integration
- [ ] Advanced data validation and cleaning
- [ ] PDF watermark removal
- [ ] Multi-language text extraction
- [ ] Real-time monitoring dashboard

## Acknowledgments

- Built for City Pathology Laboratory
- Leverages PyPDF2 and openpyxl libraries
- Community contributions and feedback

---

**Last Updated**: 2026
**Version**: 1.0.0
