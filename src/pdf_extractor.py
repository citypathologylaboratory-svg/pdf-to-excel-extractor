"""PDF extraction module for converting PDFs to structured data."""

import os
from pathlib import Path
from typing import List, Dict, Optional
import PyPDF2
import pandas as pd
from loguru import logger
from .excel_writer import ExcelWriter


class PDFtoExcelConverter:
    """Main converter class for PDF to Excel operations."""

    def __init__(self, format_type: str = 'generic'):
        """Initialize the converter.
        
        Args:
            format_type: Type of document format (generic, medical, invoice)
        """
        self.format_type = format_type
        self.excel_writer = ExcelWriter()

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Extracted text content
        """
        try:
            text = ""
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text()
            return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {str(e)}")
            raise

    def parse_extracted_data(self, text: str) -> Dict[str, str]:
        """Parse extracted text into structured data.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Dictionary of parsed data
        """
        data = {}
        lines = text.split('\\n')
        
        if self.format_type == 'medical':
            data = self._parse_medical_format(lines)
        elif self.format_type == 'invoice':
            data = self._parse_invoice_format(lines)
        else:
            data = self._parse_generic_format(lines)
            
        return data

    def _parse_medical_format(self, lines: List[str]) -> Dict[str, str]:
        """Parse medical document format."""
        data = {
            'patient_name': '',
            'test_date': '',
            'test_results': []
        }
        # Implement medical parsing logic
        return data

    def _parse_invoice_format(self, lines: List[str]) -> Dict[str, str]:
        """Parse invoice format."""
        data = {
            'invoice_number': '',
            'date': '',
            'amount': '',
            'vendor': ''
        }
        # Implement invoice parsing logic
        return data

    def _parse_generic_format(self, lines: List[str]) -> Dict[str, str]:
        """Parse generic document format."""
        data = {}
        for line in lines:
            if ':' in line:
                key, value = line.split(':', 1)
                data[key.strip()] = value.strip()
        return data

    def convert_pdf(self, input_pdf: str, output_excel: str) -> None:
        """Convert a single PDF to Excel.
        
        Args:
            input_pdf: Path to input PDF
            output_excel: Path to output Excel file
        """
        logger.info(f"Converting {input_pdf}...")
        
        # Extract text
        text = self.extract_text_from_pdf(input_pdf)
        
        # Parse data
        data = self.parse_extracted_data(text)
        
        # Create DataFrame
        df = pd.DataFrame([data])
        
        # Write to Excel
        self.excel_writer.write_dataframe(df, output_excel)
        logger.success(f"Created {output_excel}")

    def batch_convert(self, input_dir: str, output_dir: str, 
                     pattern: str = '*.pdf') -> None:
        """Convert multiple PDFs in a directory.
        
        Args:
            input_dir: Input directory containing PDFs
            output_dir: Output directory for Excel files
            pattern: File pattern to match
        """
        input_path = Path(input_dir)
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        pdf_files = list(input_path.glob(pattern))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        for pdf_file in pdf_files:
            try:
                excel_file = output_path / f"{pdf_file.stem}.xlsx"
                self.convert_pdf(str(pdf_file), str(excel_file))
            except Exception as e:
                logger.error(f"Failed to convert {pdf_file}: {str(e)}")
                continue
        
        logger.info(f"Batch conversion completed. Output saved to {output_dir}")
