import os
import json
import pandas as pd
from pathlib import Path
import io
from typing import List, Dict, Tuple

try:
    import pdfplumber
except ImportError:
    pdfplumber = None


class PDFExtractor:
    """Extract tables and text from PDF files."""

    @staticmethod
    def extract_tables(pdf_path: str) -> List[pd.DataFrame]:
        """Extract all tables from PDF."""
        if pdfplumber is None:
            raise ImportError("pdfplumber required: pip install pdfplumber")

        tables = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_tables = page.extract_tables()
                if page_tables:
                    for table in page_tables:
                        df = pd.DataFrame(table[1:], columns=table[0])
                        tables.append(df)
        return tables

    @staticmethod
    def extract_text(pdf_path: str) -> str:
        """Extract all text from PDF."""
        if pdfplumber is None:
            raise ImportError("pdfplumber required")

        text_pages = []
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    text_pages.append(text)
        return "\n".join(text_pages)

    @staticmethod
    def extract_lab_report(pdf_path: str) -> pd.DataFrame:
        """
        Extract lab report data optimized for City Pathology format.
        Handles CBC, Biochemistry, and other test reports.
        """
        tables = PDFExtractor.extract_tables(pdf_path)
        
        if tables:
            df = tables[0].copy()
            return df
        else:
            text = PDFExtractor.extract_text(pdf_path)
            return PDFExtractor._parse_text_report(text)

    @staticmethod
    def _parse_text_report(text: str) -> pd.DataFrame:
        """Parse text-based lab report."""
        lines = text.split('\n')
        data = []
        
        for line in lines:
            line = line.strip()
            if not line or len(line) < 5:
                continue
            data.append({"Test": line, "Value": "", "Unit": "", "Reference": ""})
        
        return pd.DataFrame(data) if data else pd.DataFrame({"Data": ["No data found"]})


def process_pdf_to_excel(pdf_file, output_format="auto"):
    """
    Convert PDF to Excel format.
    output_format: 'auto', 'table', 'text'
    """
    pdf_path = "/tmp/temp_upload.pdf"
    pdf_file.save(pdf_path)
    
    try:
        if output_format == "table":
            df = PDFExtractor.extract_lab_report(pdf_path)
        elif output_format == "text":
            text = PDFExtractor.extract_text(pdf_path)
            df = pd.DataFrame({"Extracted Text": [text]})
        else:
            df = PDFExtractor.extract_lab_report(pdf_path)
        
        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False, sheet_name="Data")
        excel_buffer.seek(0)
        
        return excel_buffer, df
    finally:
        if os.path.exists(pdf_path):
            os.remove(pdf_path)
