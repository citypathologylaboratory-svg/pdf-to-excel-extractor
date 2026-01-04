#!/usr/bin/env python3
"""Main entry point for PDF to Excel extractor."""

import click
import os
from pathlib import Path
from loguru import logger
from src.pdf_extractor import PDFtoExcelConverter

# Configure logger
logger.remove()
logger.add("logs/pdf_extractor.log", rotation="500 MB")
logger.add(lambda msg: print(msg, end=""))


@click.group()
def cli():
    """PDF to Excel Extractor - Convert PDF files to Excel spreadsheets."""
    pass


@cli.command()
@click.option('--input', '-i', required=True, help='Input PDF file path')
@click.option('--output', '-o', required=True, help='Output Excel file path')
@click.option('--format', '-f', default='generic', 
              help='Document format type: generic, medical, invoice')
def convert(input, output, format):
    """Convert a single PDF file to Excel."""
    try:
        logger.info(f"Starting conversion: {input} -> {output}")
        converter = PDFtoExcelConverter(format_type=format)
        converter.convert_pdf(input, output)
        logger.success(f"Successfully converted {input} to {output}")
        click.echo(f"\u2713 Conversion completed: {output}")
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        click.echo(f"\u2717 Error: {str(e)}", err=True)


@cli.command()
@click.option('--input', '-i', required=True, help='Input PDF folder path')
@click.option('--output', '-o', required=True, help='Output folder path')
@click.option('--format', '-f', default='generic',
              help='Document format type: generic, medical, invoice')
@click.option('--pattern', '-p', default='*.pdf', help='File pattern to match')
def batch(input, output, format, pattern):
    """Convert multiple PDF files in a folder to Excel."""
    try:
        logger.info(f"Starting batch conversion: {input} -> {output}")
        converter = PDFtoExcelConverter(format_type=format)
        converter.batch_convert(input, output, pattern)
        logger.success(f"Batch conversion completed")
        click.echo(f"\u2713 Batch conversion completed")
    except Exception as e:
        logger.error(f"Batch conversion failed: {str(e)}")
        click.echo(f"\u2717 Error: {str(e)}", err=True)


if __name__ == '__main__':
    cli()
