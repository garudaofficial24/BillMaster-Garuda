#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime, timedelta
import uuid
import PyPDF2
import io

class PDFHTMLTagsTester:
    def __init__(self, base_url="https://invoicecraft-6.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Store created IDs for cleanup and testing
        self.created_company_id = None
        self.created_item_id = None
        self.created_invoice_id = None
        self.created_quotation_id = None

    def log_result(self, test_name, success, details="", error_msg=""):
        """Log test result"""
        self.tests_run += 1
        if success:
            self.tests_passed += 1
            print(f"✅ {test_name}: PASSED")
            if details:
                print(f"   {details}")
        else:
            print(f"❌ {test_name}: FAILED - {error_msg}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "error": error_msg
        })

    def create_test_data(self):
        """Create test company and item for PDF testing"""
        print("\n" + "="*60)
        print("CREATING TEST DATA FOR PDF HTML TAGS VERIFICATION")
        print("="*60)
        
        # Create Company
        company_data = {
            "name": "PDF Test Company Ltd",
            "address": "123 PDF Test Street, Test City, 12345",
            "phone": "+62-21-1234567",
            "email": "test@pdfcompany.com",
            "website": "https://pdfcompany.com",
            "npwp": "12.345.678.9-012.000",
            "bank_name": "Bank Test Indonesia",
            "bank_account": "1234567890",
            "bank_account_name": "PDF Test Company Ltd"
        }
        
        try:
            response = requests.post(f"{self.api_url}/companies", json=company_data, timeout=30)
            if response.status_code == 201:
                self.created_company_id = response.json().get('id')
                self.log_result("Create Test Company", True, f"Company ID: {self.created_company_id}")
            else:
                self.log_result("Create Test Company", False, error_msg=f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Create Test Company", False, error_msg=str(e))
            return False
        
        # Create Item
        item_data = {
            "name": "Premium Software License",
            "description": "Annual software license with premium support",
            "unit_price": 2500000.0,
            "unit": "license"
        }
        
        try:
            response = requests.post(f"{self.api_url}/items", json=item_data, timeout=30)
            if response.status_code == 201:
                self.created_item_id = response.json().get('id')
                self.log_result("Create Test Item", True, f"Item ID: {self.created_item_id}")
                return True
            else:
                self.log_result("Create Test Item", False, error_msg=f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Create Test Item", False, error_msg=str(e))
            return False

    def create_test_invoice(self):
        """Create test invoice with multiple items and complex totals"""
        print("\n" + "="*60)
        print("CREATING TEST INVOICE WITH COMPLEX TOTALS")
        print("="*60)
        
        today = datetime.now().strftime('%Y-%m-%d')
        due_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        invoice_data = {
            "invoice_number": f"INV-PDF-{datetime.now().strftime('%Y%m%d')}-001",
            "company_id": self.created_company_id,
            "client_name": "Premium Client Corporation",
            "client_address": "456 Client Avenue, Business District, Jakarta 12345",
            "client_phone": "+62-21-9876543",
            "client_email": "billing@premiumclient.com",
            "date": today,
            "due_date": due_date,
            "items": [
                {
                    "item_id": self.created_item_id,
                    "name": "Premium Software License",
                    "description": "Annual software license with premium support",
                    "quantity": 5.0,
                    "unit_price": 2500000.0,
                    "unit": "license",
                    "total": 12500000.0
                },
                {
                    "name": "Implementation Service",
                    "description": "Professional implementation and setup service",
                    "quantity": 40.0,
                    "unit_price": 750000.0,
                    "unit": "hours",
                    "total": 30000000.0
                },
                {
                    "name": "Training Package",
                    "description": "Comprehensive user training program",
                    "quantity": 2.0,
                    "unit_price": 2500000.0,
                    "unit": "package",
                    "total": 5000000.0
                }
            ],
            "subtotal": 47500000.0,
            "tax_rate": 11.0,
            "tax_amount": 5225000.0,
            "discount_rate": 5.0,
            "discount_amount": 2375000.0,
            "total": 50350000.0,
            "currency": "IDR",
            "notes": "Payment terms: Net 30 days. Late payment subject to 2% monthly interest.",
            "template_id": "template1",
            "status": "sent",
            "signature_name": "John Doe",
            "signature_position": "Finance Manager"
        }
        
        try:
            response = requests.post(f"{self.api_url}/invoices", json=invoice_data, timeout=30)
            if response.status_code == 201:
                self.created_invoice_id = response.json().get('id')
                self.log_result("Create Test Invoice", True, f"Invoice ID: {self.created_invoice_id}")
                return True
            else:
                self.log_result("Create Test Invoice", False, error_msg=f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Create Test Invoice", False, error_msg=str(e))
            return False

    def create_test_quotation(self):
        """Create test quotation with multiple items and complex totals"""
        print("\n" + "="*60)
        print("CREATING TEST QUOTATION WITH COMPLEX TOTALS")
        print("="*60)
        
        today = datetime.now().strftime('%Y-%m-%d')
        valid_until = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        
        quotation_data = {
            "quotation_number": f"QUO-PDF-{datetime.now().strftime('%Y%m%d')}-001",
            "company_id": self.created_company_id,
            "client_name": "Potential Client Ltd",
            "client_address": "789 Prospect Street, Business Park, Surabaya 60123",
            "client_phone": "+62-31-1234567",
            "client_email": "procurement@potentialclient.com",
            "date": today,
            "valid_until": valid_until,
            "items": [
                {
                    "item_id": self.created_item_id,
                    "name": "Premium Software License",
                    "description": "Annual software license with premium support",
                    "quantity": 10.0,
                    "unit_price": 2500000.0,
                    "unit": "license",
                    "total": 25000000.0
                },
                {
                    "name": "Consulting Service",
                    "description": "Strategic consulting and optimization service",
                    "quantity": 60.0,
                    "unit_price": 1000000.0,
                    "unit": "hours",
                    "total": 60000000.0
                }
            ],
            "subtotal": 85000000.0,
            "tax_rate": 11.0,
            "tax_amount": 9350000.0,
            "discount_rate": 10.0,
            "discount_amount": 8500000.0,
            "total": 85850000.0,
            "currency": "IDR",
            "notes": "This quotation is valid for 30 days. All prices are in Indonesian Rupiah.",
            "template_id": "template1",
            "status": "draft",
            "signature_name": "Jane Smith",
            "signature_position": "Sales Director"
        }
        
        try:
            response = requests.post(f"{self.api_url}/quotations", json=quotation_data, timeout=30)
            if response.status_code == 201:
                self.created_quotation_id = response.json().get('id')
                self.log_result("Create Test Quotation", True, f"Quotation ID: {self.created_quotation_id}")
                return True
            else:
                self.log_result("Create Test Quotation", False, error_msg=f"Status: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Create Test Quotation", False, error_msg=str(e))
            return False

    def extract_pdf_text(self, pdf_content):
        """Extract text from PDF content"""
        try:
            pdf_file = io.BytesIO(pdf_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            
            return text
        except Exception as e:
            print(f"   Error extracting PDF text: {str(e)}")
            return None

    def test_invoice_pdf_html_tags(self):
        """Test invoice PDF for HTML tags in content"""
        print("\n" + "="*60)
        print("TESTING INVOICE PDF FOR HTML TAGS")
        print("="*60)
        
        if not self.created_invoice_id:
            self.log_result("Invoice PDF HTML Tags Test", False, error_msg="No invoice ID available")
            return False
        
        try:
            url = f"{self.api_url}/invoices/{self.created_invoice_id}/pdf"
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                self.log_result("Invoice PDF HTML Tags Test", False, error_msg=f"PDF generation failed with status {response.status_code}")
                return False
            
            if response.headers.get('content-type') != 'application/pdf':
                self.log_result("Invoice PDF HTML Tags Test", False, error_msg=f"Wrong content type: {response.headers.get('content-type')}")
                return False
            
            # Extract text from PDF
            pdf_text = self.extract_pdf_text(response.content)
            if pdf_text is None:
                self.log_result("Invoice PDF HTML Tags Test", False, error_msg="Failed to extract PDF text")
                return False
            
            print(f"   PDF size: {len(response.content)} bytes")
            print(f"   Extracted text length: {len(pdf_text)} characters")
            
            # Check for HTML tags that should NOT be present
            html_tags_to_check = [
                '<b>',
                '</b>',
                '<strong>',
                '</strong>',
                '<i>',
                '</i>',
                '<em>',
                '</em>',
                '<br>',
                '<br/>',
                '<p>',
                '</p>',
                '<div>',
                '</div>'
            ]
            
            found_html_tags = []
            for tag in html_tags_to_check:
                if tag in pdf_text:
                    found_html_tags.append(tag)
            
            if found_html_tags:
                self.log_result("Invoice PDF HTML Tags Test", False, 
                              error_msg=f"Found HTML tags in PDF: {', '.join(found_html_tags)}")
                print(f"   PDF text sample: {pdf_text[:500]}...")
                return False
            
            # Check that important content is present (without HTML tags)
            expected_content = [
                "INVOICE",
                "PDF Test Company Ltd",
                "Total:",
                "Rp 50,350,000",  # Expected formatted total
                "Subtotal:",
                "Rp 47,500,000",  # Expected formatted subtotal
                "Premium Software License",
                "Implementation Service",
                "Training Package"
            ]
            
            missing_content = []
            for content in expected_content:
                if content not in pdf_text:
                    missing_content.append(content)
            
            if missing_content:
                self.log_result("Invoice PDF HTML Tags Test", False,
                              error_msg=f"Missing expected content: {', '.join(missing_content)}")
                print(f"   PDF text sample: {pdf_text[:1000]}...")
                return False
            
            self.log_result("Invoice PDF HTML Tags Test", True, 
                          "PDF generated correctly without HTML tags, all expected content present")
            return True
            
        except Exception as e:
            self.log_result("Invoice PDF HTML Tags Test", False, error_msg=str(e))
            return False

    def test_quotation_pdf_html_tags(self):
        """Test quotation PDF for HTML tags in content"""
        print("\n" + "="*60)
        print("TESTING QUOTATION PDF FOR HTML TAGS")
        print("="*60)
        
        if not self.created_quotation_id:
            self.log_result("Quotation PDF HTML Tags Test", False, error_msg="No quotation ID available")
            return False
        
        try:
            url = f"{self.api_url}/quotations/{self.created_quotation_id}/pdf"
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                self.log_result("Quotation PDF HTML Tags Test", False, error_msg=f"PDF generation failed with status {response.status_code}")
                return False
            
            if response.headers.get('content-type') != 'application/pdf':
                self.log_result("Quotation PDF HTML Tags Test", False, error_msg=f"Wrong content type: {response.headers.get('content-type')}")
                return False
            
            # Extract text from PDF
            pdf_text = self.extract_pdf_text(response.content)
            if pdf_text is None:
                self.log_result("Quotation PDF HTML Tags Test", False, error_msg="Failed to extract PDF text")
                return False
            
            print(f"   PDF size: {len(response.content)} bytes")
            print(f"   Extracted text length: {len(pdf_text)} characters")
            
            # Check for HTML tags that should NOT be present
            html_tags_to_check = [
                '<b>',
                '</b>',
                '<strong>',
                '</strong>',
                '<i>',
                '</i>',
                '<em>',
                '</em>',
                '<br>',
                '<br/>',
                '<p>',
                '</p>',
                '<div>',
                '</div>'
            ]
            
            found_html_tags = []
            for tag in html_tags_to_check:
                if tag in pdf_text:
                    found_html_tags.append(tag)
            
            if found_html_tags:
                self.log_result("Quotation PDF HTML Tags Test", False, 
                              error_msg=f"Found HTML tags in PDF: {', '.join(found_html_tags)}")
                print(f"   PDF text sample: {pdf_text[:500]}...")
                return False
            
            # Check that important content is present (without HTML tags)
            expected_content = [
                "QUOTATION",
                "PDF Test Company Ltd",
                "Total:",
                "Rp 85,850,000",  # Expected formatted total
                "Subtotal:",
                "Rp 85,000,000",  # Expected formatted subtotal
                "Premium Software License",
                "Consulting Service"
            ]
            
            missing_content = []
            for content in expected_content:
                if content not in pdf_text:
                    missing_content.append(content)
            
            if missing_content:
                self.log_result("Quotation PDF HTML Tags Test", False,
                              error_msg=f"Missing expected content: {', '.join(missing_content)}")
                print(f"   PDF text sample: {pdf_text[:1000]}...")
                return False
            
            self.log_result("Quotation PDF HTML Tags Test", True, 
                          "PDF generated correctly without HTML tags, all expected content present")
            return True
            
        except Exception as e:
            self.log_result("Quotation PDF HTML Tags Test", False, error_msg=str(e))
            return False

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n" + "="*60)
        print("CLEANING UP TEST DATA")
        print("="*60)
        
        # Delete Invoice
        if self.created_invoice_id:
            try:
                response = requests.delete(f"{self.api_url}/invoices/{self.created_invoice_id}", timeout=30)
                if response.status_code == 200:
                    self.log_result("Delete Test Invoice", True)
                else:
                    self.log_result("Delete Test Invoice", False, error_msg=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Delete Test Invoice", False, error_msg=str(e))
        
        # Delete Quotation
        if self.created_quotation_id:
            try:
                response = requests.delete(f"{self.api_url}/quotations/{self.created_quotation_id}", timeout=30)
                if response.status_code == 200:
                    self.log_result("Delete Test Quotation", True)
                else:
                    self.log_result("Delete Test Quotation", False, error_msg=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Delete Test Quotation", False, error_msg=str(e))
        
        # Delete Item
        if self.created_item_id:
            try:
                response = requests.delete(f"{self.api_url}/items/{self.created_item_id}", timeout=30)
                if response.status_code == 200:
                    self.log_result("Delete Test Item", True)
                else:
                    self.log_result("Delete Test Item", False, error_msg=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Delete Test Item", False, error_msg=str(e))
        
        # Delete Company
        if self.created_company_id:
            try:
                response = requests.delete(f"{self.api_url}/companies/{self.created_company_id}", timeout=30)
                if response.status_code == 200:
                    self.log_result("Delete Test Company", True)
                else:
                    self.log_result("Delete Test Company", False, error_msg=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Delete Test Company", False, error_msg=str(e))

    def run_pdf_html_tests(self):
        """Run all PDF HTML tags tests"""
        print("🚀 Starting PDF HTML Tags Verification Tests")
        print(f"📍 Base URL: {self.base_url}")
        print(f"📍 API URL: {self.api_url}")
        
        # Create test data
        if not self.create_test_data():
            print("❌ Failed to create test data. Aborting tests.")
            return False
        
        # Create test invoice and quotation
        invoice_created = self.create_test_invoice()
        quotation_created = self.create_test_quotation()
        
        if not invoice_created and not quotation_created:
            print("❌ Failed to create test invoice and quotation. Aborting tests.")
            return False
        
        # Test PDF generation and HTML tags
        invoice_test_passed = True
        quotation_test_passed = True
        
        if invoice_created:
            invoice_test_passed = self.test_invoice_pdf_html_tags()
        
        if quotation_created:
            quotation_test_passed = self.test_quotation_pdf_html_tags()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print final results
        print("\n" + "="*70)
        print("FINAL PDF HTML TAGS TEST RESULTS")
        print("="*70)
        print(f"📊 Tests Run: {self.tests_run}")
        print(f"✅ Tests Passed: {self.tests_passed}")
        print(f"❌ Tests Failed: {self.tests_run - self.tests_passed}")
        print(f"📈 Success Rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        # Print failed tests
        failed_tests = [r for r in self.test_results if not r['success']]
        if failed_tests:
            print(f"\n❌ Failed Tests ({len(failed_tests)}):")
            for test in failed_tests:
                print(f"   • {test['test']}: {test['error']}")
        else:
            print("\n🎉 All PDF HTML tags tests passed! No HTML tags found in PDF content.")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = PDFHTMLTagsTester()
    
    try:
        success = tester.run_pdf_html_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())