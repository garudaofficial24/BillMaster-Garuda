#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import uuid
import base64
import io
from PIL import Image
import PyPDF2

class LetterPDFTester:
    def __init__(self, base_url="https://documaster-2.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Store created IDs for cleanup and testing
        self.created_company_id = None
        self.created_letter_id = None
        self.uploaded_signature = None

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

    def create_test_company_with_logo(self):
        """Create a test company with logo for PDF testing"""
        print("\n" + "="*60)
        print("CREATING TEST COMPANY WITH LOGO")
        print("="*60)
        
        # Create a simple logo image
        logo_img = Image.new('RGB', (120, 60), color='#1e40af')
        logo_buffer = io.BytesIO()
        logo_img.save(logo_buffer, format='PNG')
        logo_base64 = base64.b64encode(logo_buffer.getvalue()).decode('utf-8')
        logo_data_uri = f"data:image/png;base64,{logo_base64}"
        
        company_data = {
            "name": "PDF Test Company Ltd",
            "address": "Jl. Sudirman No. 123, Jakarta Pusat 10220",
            "phone": "+62-21-1234567",
            "email": "info@pdftestcompany.com",
            "website": "https://pdftestcompany.com",
            "motto": "Excellence in Every Service - Innovation for Tomorrow",
            "npwp": "12.345.678.9-012.000",
            "bank_name": "Bank Mandiri",
            "bank_account": "1234567890",
            "bank_account_name": "PDF Test Company Ltd",
            "logo": logo_data_uri
        }
        
        try:
            url = f"{self.api_url}/companies"
            response = requests.post(url, json=company_data, headers={'Content-Type': 'application/json'}, timeout=30)
            
            if response.status_code == 201:
                response_data = response.json()
                self.created_company_id = response_data.get('id')
                self.log_result("Create Test Company with Logo", True, f"Company ID: {self.created_company_id}")
                return True
            else:
                self.log_result("Create Test Company with Logo", False, error_msg=f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Create Test Company with Logo", False, error_msg=str(e))
            return False

    def upload_test_signature(self):
        """Upload a test signature image"""
        print("\n" + "="*60)
        print("UPLOADING TEST SIGNATURE IMAGE")
        print("="*60)
        
        try:
            # Create a more realistic signature image (larger for testing)
            sig_img = Image.new('RGBA', (200, 100), color=(255, 255, 255, 0))  # Transparent background
            # Add some simple signature-like content
            from PIL import ImageDraw
            draw = ImageDraw.Draw(sig_img)
            draw.text((10, 30), "John Doe", fill=(0, 0, 0, 255))
            draw.line([(10, 60), (180, 60)], fill=(0, 0, 0, 255), width=2)
            
            sig_buffer = io.BytesIO()
            sig_img.save(sig_buffer, format='PNG')
            test_signature_bytes = sig_buffer.getvalue()
            
            # Prepare multipart form data
            files = {'file': ('test_signature.png', test_signature_bytes, 'image/png')}
            
            url = f"{self.api_url}/upload-signature"
            response = requests.post(url, files=files, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'signature' in response_data:
                    self.uploaded_signature = response_data['signature']
                    self.log_result("Upload Test Signature", True, "Signature uploaded successfully")
                    return True
                else:
                    self.log_result("Upload Test Signature", False, error_msg="No signature field in response")
                    return False
            else:
                self.log_result("Upload Test Signature", False, error_msg=f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Upload Test Signature", False, error_msg=str(e))
            return False

    def create_test_letter_with_signatures(self):
        """Create a comprehensive test letter with multiple signatories"""
        print("\n" + "="*60)
        print("CREATING TEST LETTER WITH SIGNATURES")
        print("="*60)
        
        if not self.created_company_id:
            self.log_result("Create Test Letter", False, error_msg="No company ID available")
            return False
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        letter_data = {
            "letter_number": f"001/PDF-TEST/{datetime.now().strftime('%m')}/{datetime.now().year}",
            "company_id": self.created_company_id,
            "date": today,
            "subject": "Testing PDF Generation with Enhanced Signature Display",
            "letter_type": "cooperation",
            "recipient_name": "Bapak Direktur Utama",
            "recipient_position": "Direktur Utama",
            "recipient_address": "PT. Mitra Strategis Indonesia\nJl. Gatot Subroto No. 456\nJakarta Selatan 12930",
            "content": "Dengan hormat,\n\nKami dari PDF Test Company Ltd bermaksud untuk menguji sistem PDF generation yang telah diperbaharui, khususnya dalam hal tampilan signature yang lebih besar dan layout yang lebih profesional.\n\nPerbaikan yang telah dilakukan meliputi:\n1. Ukuran signature diperbesar menjadi 2x lipat (160x80 pixels)\n2. Layout header yang terpusat dengan logo perusahaan\n3. Nama perusahaan dengan format bold dan ukuran lebih besar\n4. Motto perusahaan dalam format italic\n5. Format profesional secara keseluruhan\n\nDengan perbaikan ini, kami yakin bahwa kualitas dokumen PDF yang dihasilkan akan lebih baik dan lebih mudah dibaca, terutama untuk bagian signature yang sebelumnya terlalu kecil.\n\nDemikian surat pengujian ini kami sampaikan untuk memastikan semua fitur berfungsi dengan baik.",
            "attachments_count": 3,
            "cc_list": "1. Manager IT\n2. Quality Assurance Team\n3. Document Management Team",
            "signatories": [
                {
                    "name": "John Doe",
                    "position": "Chief Executive Officer",
                    "signature_image": self.uploaded_signature if self.uploaded_signature else None
                },
                {
                    "name": "Jane Smith", 
                    "position": "Chief Technology Officer",
                    "signature_image": self.uploaded_signature if self.uploaded_signature else None
                },
                {
                    "name": "Bob Wilson",
                    "position": "Quality Assurance Manager",
                    "signature_image": None  # Test without signature image
                }
            ]
        }
        
        try:
            url = f"{self.api_url}/letters"
            response = requests.post(url, json=letter_data, headers={'Content-Type': 'application/json'}, timeout=30)
            
            if response.status_code == 201:
                response_data = response.json()
                self.created_letter_id = response_data.get('id')
                self.log_result("Create Test Letter with Signatures", True, f"Letter ID: {self.created_letter_id}")
                return True
            else:
                self.log_result("Create Test Letter with Signatures", False, error_msg=f"Status: {response.status_code}")
                return False
                
        except Exception as e:
            self.log_result("Create Test Letter with Signatures", False, error_msg=str(e))
            return False

    def test_pdf_generation_and_analysis(self):
        """Generate PDF and analyze its content and structure"""
        print("\n" + "="*60)
        print("TESTING PDF GENERATION AND ANALYSIS")
        print("="*60)
        
        if not self.created_letter_id:
            self.log_result("PDF Generation Test", False, error_msg="No letter ID available")
            return False
        
        try:
            url = f"{self.api_url}/letters/{self.created_letter_id}/pdf"
            response = requests.get(url, timeout=30)
            
            if response.status_code != 200:
                self.log_result("PDF Generation Test", False, error_msg=f"Status: {response.status_code}")
                return False
            
            if response.headers.get('content-type') != 'application/pdf':
                self.log_result("PDF Generation Test", False, error_msg=f"Wrong content type: {response.headers.get('content-type')}")
                return False
            
            pdf_content = response.content
            pdf_size = len(pdf_content)
            
            # Save PDF for analysis
            pdf_path = f"/tmp/test_letter_{self.created_letter_id}.pdf"
            with open(pdf_path, "wb") as f:
                f.write(pdf_content)
            
            self.log_result("PDF Generation Test", True, f"PDF generated successfully, size: {pdf_size} bytes")
            
            # Analyze PDF content
            self.analyze_pdf_content(pdf_path, pdf_content)
            
            return True
            
        except Exception as e:
            self.log_result("PDF Generation Test", False, error_msg=str(e))
            return False

    def analyze_pdf_content(self, pdf_path, pdf_content):
        """Analyze PDF content to verify structure and formatting"""
        print("\n" + "="*60)
        print("ANALYZING PDF CONTENT AND STRUCTURE")
        print("="*60)
        
        try:
            # Read PDF content using PyPDF2
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            if len(pdf_reader.pages) == 0:
                self.log_result("PDF Content Analysis", False, error_msg="PDF has no pages")
                return
            
            # Extract text from first page
            first_page = pdf_reader.pages[0]
            text_content = first_page.extract_text()
            
            # Check for key elements in the PDF
            checks = [
                ("Company Name Present", "PDF Test Company Ltd" in text_content),
                ("Company Motto Present", "Excellence in Every Service" in text_content),
                ("Letter Number Present", "001/PDF-TEST" in text_content),
                ("Subject Present", "Testing PDF Generation" in text_content),
                ("Recipient Present", "Bapak Direktur Utama" in text_content),
                ("Content Present", "sistem PDF generation" in text_content),
                ("Signature Section Present", "Chief Executive Officer" in text_content),
                ("CC List Present", "Manager IT" in text_content),
                ("Multiple Signatories", "Chief Technology Officer" in text_content),
                ("Attachments Info", "3 berkas" in text_content or "Lampiran: 3" in text_content)
            ]
            
            passed_checks = 0
            for check_name, check_result in checks:
                if check_result:
                    passed_checks += 1
                    self.log_result(f"PDF Content Check: {check_name}", True)
                else:
                    self.log_result(f"PDF Content Check: {check_name}", False, error_msg="Content not found in PDF")
            
            # Overall content analysis
            content_score = (passed_checks / len(checks)) * 100
            if content_score >= 80:
                self.log_result("PDF Content Analysis", True, f"Content verification: {content_score:.1f}% ({passed_checks}/{len(checks)} checks passed)")
            else:
                self.log_result("PDF Content Analysis", False, error_msg=f"Content verification failed: {content_score:.1f}% ({passed_checks}/{len(checks)} checks passed)")
            
            # Check PDF structure
            self.verify_pdf_structure(text_content)
            
        except Exception as e:
            self.log_result("PDF Content Analysis", False, error_msg=str(e))

    def verify_pdf_structure(self, text_content):
        """Verify PDF structure matches expected format"""
        print("\n" + "="*50)
        print("VERIFYING PDF STRUCTURE")
        print("="*50)
        
        # Check for proper Indonesian letter structure
        structure_checks = [
            ("Header Section", "PDF Test Company Ltd" in text_content),
            ("Letter Info Section", "Nomor:" in text_content and "Tanggal:" in text_content),
            ("Recipient Section", "Kepada Yth," in text_content),
            ("Greeting", "Dengan hormat," in text_content),
            ("Content Paragraphs", "Perbaikan yang telah dilakukan" in text_content),
            ("Closing", "Demikian surat" in text_content),
            ("Signature Section", "Chief Executive Officer" in text_content),
            ("CC Section", "Tembusan:" in text_content)
        ]
        
        structure_passed = 0
        for check_name, check_result in structure_checks:
            if check_result:
                structure_passed += 1
                self.log_result(f"Structure Check: {check_name}", True)
            else:
                self.log_result(f"Structure Check: {check_name}", False, error_msg="Structure element not found")
        
        structure_score = (structure_passed / len(structure_checks)) * 100
        if structure_score >= 85:
            self.log_result("PDF Structure Verification", True, f"Structure verification: {structure_score:.1f}% ({structure_passed}/{len(structure_checks)} elements found)")
        else:
            self.log_result("PDF Structure Verification", False, error_msg=f"Structure verification failed: {structure_score:.1f}% ({structure_passed}/{len(structure_checks)} elements found)")

    def test_signature_size_verification(self):
        """Test to verify signature images are properly sized (2x larger)"""
        print("\n" + "="*60)
        print("VERIFYING SIGNATURE SIZE IMPROVEMENTS")
        print("="*60)
        
        # This test verifies the code implementation for signature sizing
        # The actual signature size is set in the backend code at lines 889-890:
        # max_sig_width, max_sig_height = 160, 80
        
        # Check if the backend code has the correct signature size settings
        try:
            with open('/app/backend/server.py', 'r') as f:
                backend_code = f.read()
            
            # Look for the signature size configuration
            if "max_sig_width, max_sig_height = 160, 80" in backend_code:
                self.log_result("Signature Size Configuration", True, "Backend configured for 2x larger signatures (160x80)")
            else:
                self.log_result("Signature Size Configuration", False, error_msg="Signature size not set to 160x80 in backend code")
            
            # Check for the signature resize code
            if "# Resize signature - 2x larger for better visibility" in backend_code:
                self.log_result("Signature Resize Comment", True, "Code comment confirms 2x larger signature implementation")
            else:
                self.log_result("Signature Resize Comment", False, error_msg="Missing comment about 2x larger signature")
            
            # Check for proper thumbnail resizing
            if "sig_img_pil.thumbnail((max_sig_width, max_sig_height)" in backend_code:
                self.log_result("Signature Thumbnail Implementation", True, "Proper thumbnail resizing implementation found")
            else:
                self.log_result("Signature Thumbnail Implementation", False, error_msg="Signature thumbnail resizing not properly implemented")
                
        except Exception as e:
            self.log_result("Signature Size Code Verification", False, error_msg=str(e))

    def test_layout_improvements(self):
        """Test PDF layout improvements"""
        print("\n" + "="*60)
        print("VERIFYING PDF LAYOUT IMPROVEMENTS")
        print("="*60)
        
        try:
            with open('/app/backend/server.py', 'r') as f:
                backend_code = f.read()
            
            layout_checks = [
                ("Centered Company Header", "alignment=TA_CENTER" in backend_code and "company_style" in backend_code),
                ("Bold Company Name", "company_name_style" in backend_code and "fontSize=14" in backend_code),
                ("Italic Motto Style", "company_motto_style" in backend_code and "Helvetica-Oblique" in backend_code),
                ("Logo Centering", "logo_table" in backend_code and "ALIGN.*CENTER" in backend_code),
                ("Professional Separator", "separator_table" in backend_code and "LINEABOVE" in backend_code)
            ]
            
            layout_passed = 0
            for check_name, check_result in layout_checks:
                if check_result:
                    layout_passed += 1
                    self.log_result(f"Layout Check: {check_name}", True)
                else:
                    self.log_result(f"Layout Check: {check_name}", False, error_msg="Layout feature not found in code")
            
            layout_score = (layout_passed / len(layout_checks)) * 100
            if layout_score >= 80:
                self.log_result("PDF Layout Improvements", True, f"Layout verification: {layout_score:.1f}% ({layout_passed}/{len(layout_checks)} features implemented)")
            else:
                self.log_result("PDF Layout Improvements", False, error_msg=f"Layout verification failed: {layout_score:.1f}% ({layout_passed}/{len(layout_checks)} features implemented)")
                
        except Exception as e:
            self.log_result("PDF Layout Verification", False, error_msg=str(e))

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n" + "="*50)
        print("CLEANING UP TEST DATA")
        print("="*50)
        
        # Delete Letter
        if self.created_letter_id:
            try:
                url = f"{self.api_url}/letters/{self.created_letter_id}"
                response = requests.delete(url, timeout=30)
                if response.status_code == 200:
                    self.log_result("Delete Test Letter", True)
                else:
                    self.log_result("Delete Test Letter", False, error_msg=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Delete Test Letter", False, error_msg=str(e))
        
        # Delete Company
        if self.created_company_id:
            try:
                url = f"{self.api_url}/companies/{self.created_company_id}"
                response = requests.delete(url, timeout=30)
                if response.status_code == 200:
                    self.log_result("Delete Test Company", True)
                else:
                    self.log_result("Delete Test Company", False, error_msg=f"Status: {response.status_code}")
            except Exception as e:
                self.log_result("Delete Test Company", False, error_msg=str(e))

    def run_letter_pdf_tests(self):
        """Run all Letter PDF specific tests"""
        print("🚀 Starting Letter PDF Generation Tests")
        print(f"📍 Base URL: {self.base_url}")
        print(f"📍 API URL: {self.api_url}")
        print("\n🎯 Focus: Testing 2x larger signatures and improved PDF layout")
        
        # Setup test data
        if not self.create_test_company_with_logo():
            print("❌ Failed to create test company. Aborting tests.")
            return False
        
        if not self.upload_test_signature():
            print("❌ Failed to upload test signature. Continuing without signature...")
        
        if not self.create_test_letter_with_signatures():
            print("❌ Failed to create test letter. Aborting tests.")
            return False
        
        # Run PDF tests
        self.test_pdf_generation_and_analysis()
        self.test_signature_size_verification()
        self.test_layout_improvements()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print final results
        print("\n" + "="*70)
        print("LETTER PDF GENERATION TEST RESULTS")
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
            print(f"\n🎉 All tests passed! Letter PDF generation improvements are working correctly.")
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = LetterPDFTester()
    
    try:
        success = tester.run_letter_pdf_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())