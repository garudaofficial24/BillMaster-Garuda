#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid
import PyPDF2
import io

def create_and_verify_pdfs():
    """Create test data and verify PDF content"""
    base_url = "https://invoicecraft-6.preview.emergentagent.com"
    api_url = f"{base_url}/api"
    
    print("🔍 Creating test data and verifying PDF content...")
    
    # Create Company
    company_data = {
        "name": "Verification Test Company",
        "address": "123 Verification Street, Test City",
        "phone": "+62-21-1234567",
        "email": "test@verification.com",
        "npwp": "12.345.678.9-012.000",
        "bank_name": "Bank Verification",
        "bank_account": "1234567890",
        "bank_account_name": "Verification Test Company"
    }
    
    response = requests.post(f"{api_url}/companies", json=company_data)
    if response.status_code != 201:
        print(f"❌ Failed to create company: {response.status_code}")
        return False
    
    company_id = response.json().get('id')
    print(f"✅ Created company: {company_id}")
    
    # Create Item
    item_data = {
        "name": "Test Service",
        "description": "Professional testing service",
        "unit_price": 1500000.0,
        "unit": "hours"
    }
    
    response = requests.post(f"{api_url}/items", json=item_data)
    if response.status_code != 201:
        print(f"❌ Failed to create item: {response.status_code}")
        return False
    
    item_id = response.json().get('id')
    print(f"✅ Created item: {item_id}")
    
    # Create Invoice with large total to test formatting
    invoice_data = {
        "invoice_number": f"INV-VERIFY-{datetime.now().strftime('%Y%m%d')}-001",
        "company_id": company_id,
        "client_name": "Big Client Corporation",
        "client_address": "456 Client Street, Jakarta",
        "date": datetime.now().strftime('%Y-%m-%d'),
        "items": [
            {
                "item_id": item_id,
                "name": "Test Service",
                "description": "Professional testing service",
                "quantity": 50.0,
                "unit_price": 1500000.0,
                "unit": "hours",
                "total": 75000000.0
            }
        ],
        "subtotal": 75000000.0,
        "tax_rate": 11.0,
        "tax_amount": 8250000.0,
        "discount_rate": 0.0,
        "discount_amount": 0.0,
        "total": 83250000.0,
        "currency": "IDR",
        "status": "sent"
    }
    
    response = requests.post(f"{api_url}/invoices", json=invoice_data)
    if response.status_code != 201:
        print(f"❌ Failed to create invoice: {response.status_code}")
        return False
    
    invoice_id = response.json().get('id')
    print(f"✅ Created invoice: {invoice_id}")
    
    # Generate and verify Invoice PDF
    print("\n📄 Generating and verifying Invoice PDF...")
    response = requests.get(f"{api_url}/invoices/{invoice_id}/pdf")
    if response.status_code != 200:
        print(f"❌ Failed to generate invoice PDF: {response.status_code}")
        return False
    
    # Save PDF file
    with open('/app/test_invoice.pdf', 'wb') as f:
        f.write(response.content)
    print(f"✅ Saved invoice PDF: /app/test_invoice.pdf ({len(response.content)} bytes)")
    
    # Extract and verify text
    pdf_text = extract_pdf_text(response.content)
    if pdf_text:
        print(f"📝 Invoice PDF text length: {len(pdf_text)} characters")
        
        # Check for HTML tags
        html_tags = ['<b>', '</b>', '<strong>', '</strong>', '<i>', '</i>']
        found_tags = [tag for tag in html_tags if tag in pdf_text]
        
        if found_tags:
            print(f"❌ Found HTML tags in invoice PDF: {found_tags}")
            print(f"Sample text: {pdf_text[:500]}...")
        else:
            print("✅ No HTML tags found in invoice PDF")
            
        # Check for expected formatted content
        expected_total = "Rp 83,250,000"
        expected_subtotal = "Rp 75,000,000"
        
        if expected_total in pdf_text and expected_subtotal in pdf_text:
            print(f"✅ Found correctly formatted totals: {expected_total}, {expected_subtotal}")
        else:
            print(f"❌ Missing expected formatted totals")
            print(f"Looking for: {expected_total}, {expected_subtotal}")
            print(f"Sample text: {pdf_text[:1000]}...")
    
    # Create Quotation
    quotation_data = {
        "quotation_number": f"QUO-VERIFY-{datetime.now().strftime('%Y%m%d')}-001",
        "company_id": company_id,
        "client_name": "Potential Big Client",
        "client_address": "789 Prospect Avenue, Surabaya",
        "date": datetime.now().strftime('%Y-%m-%d'),
        "valid_until": (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d'),
        "items": [
            {
                "item_id": item_id,
                "name": "Test Service",
                "description": "Professional testing service",
                "quantity": 100.0,
                "unit_price": 1500000.0,
                "unit": "hours",
                "total": 150000000.0
            }
        ],
        "subtotal": 150000000.0,
        "tax_rate": 11.0,
        "tax_amount": 16500000.0,
        "discount_rate": 5.0,
        "discount_amount": 7500000.0,
        "total": 159000000.0,
        "currency": "IDR",
        "status": "draft"
    }
    
    response = requests.post(f"{api_url}/quotations", json=quotation_data)
    if response.status_code != 201:
        print(f"❌ Failed to create quotation: {response.status_code}")
        return False
    
    quotation_id = response.json().get('id')
    print(f"✅ Created quotation: {quotation_id}")
    
    # Generate and verify Quotation PDF
    print("\n📄 Generating and verifying Quotation PDF...")
    response = requests.get(f"{api_url}/quotations/{quotation_id}/pdf")
    if response.status_code != 200:
        print(f"❌ Failed to generate quotation PDF: {response.status_code}")
        return False
    
    # Save PDF file
    with open('/app/test_quotation.pdf', 'wb') as f:
        f.write(response.content)
    print(f"✅ Saved quotation PDF: /app/test_quotation.pdf ({len(response.content)} bytes)")
    
    # Extract and verify text
    pdf_text = extract_pdf_text(response.content)
    if pdf_text:
        print(f"📝 Quotation PDF text length: {len(pdf_text)} characters")
        
        # Check for HTML tags
        found_tags = [tag for tag in html_tags if tag in pdf_text]
        
        if found_tags:
            print(f"❌ Found HTML tags in quotation PDF: {found_tags}")
            print(f"Sample text: {pdf_text[:500]}...")
        else:
            print("✅ No HTML tags found in quotation PDF")
            
        # Check for expected formatted content
        expected_total = "Rp 159,000,000"
        expected_subtotal = "Rp 150,000,000"
        
        if expected_total in pdf_text and expected_subtotal in pdf_text:
            print(f"✅ Found correctly formatted totals: {expected_total}, {expected_subtotal}")
        else:
            print(f"❌ Missing expected formatted totals")
            print(f"Looking for: {expected_total}, {expected_subtotal}")
            print(f"Sample text: {pdf_text[:1000]}...")
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    requests.delete(f"{api_url}/invoices/{invoice_id}")
    requests.delete(f"{api_url}/quotations/{quotation_id}")
    requests.delete(f"{api_url}/items/{item_id}")
    requests.delete(f"{api_url}/companies/{company_id}")
    print("✅ Cleanup completed")
    
    return True

def extract_pdf_text(pdf_content):
    """Extract text from PDF content"""
    try:
        pdf_file = io.BytesIO(pdf_content)
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text
    except Exception as e:
        print(f"Error extracting PDF text: {str(e)}")
        return None

if __name__ == "__main__":
    create_and_verify_pdfs()