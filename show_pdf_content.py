#!/usr/bin/env python3

import PyPDF2
import sys

def show_pdf_content(filename):
    """Show the text content of a PDF file"""
    try:
        with open(filename, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            
            print(f"\n{'='*60}")
            print(f"PDF CONTENT: {filename}")
            print(f"{'='*60}")
            print(f"Number of pages: {len(pdf_reader.pages)}")
            
            for page_num, page in enumerate(pdf_reader.pages, 1):
                print(f"\n--- Page {page_num} ---")
                text = page.extract_text()
                print(text)
                print(f"\n--- End Page {page_num} ---")
                
    except Exception as e:
        print(f"Error reading {filename}: {str(e)}")

if __name__ == "__main__":
    show_pdf_content("/app/test_invoice.pdf")
    show_pdf_content("/app/test_quotation.pdf")