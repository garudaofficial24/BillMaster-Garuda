#!/usr/bin/env python3

import requests
import sys
import json
from datetime import datetime
import uuid
import base64

class LettersAPITester:
    def __init__(self, base_url="https://invoicecraft-6.preview.emergentagent.com"):
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
        else:
            print(f"❌ {test_name}: FAILED - {error_msg}")
        
        self.test_results.append({
            "test": test_name,
            "success": success,
            "details": details,
            "error": error_msg
        })

    def run_test(self, name, method, endpoint, expected_status, data=None, return_response=False):
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}

        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=30)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=30)
            elif method == 'PUT':
                response = requests.put(url, json=data, headers=headers, timeout=30)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers, timeout=30)

            success = response.status_code == expected_status
            
            if success:
                self.log_result(name, True, f"Status: {response.status_code}")
                if return_response:
                    try:
                        return success, response.json()
                    except:
                        return success, response.text
                return success, {}
            else:
                error_msg = f"Expected {expected_status}, got {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f" - {error_details}"
                except:
                    error_msg += f" - {response.text[:200]}"
                
                self.log_result(name, False, error_msg=error_msg)
                return False, {}

        except Exception as e:
            error_msg = f"Request failed: {str(e)}"
            self.log_result(name, False, error_msg=error_msg)
            return False, {}

    def setup_company(self):
        """Create a test company with motto"""
        print("\n" + "="*50)
        print("SETTING UP TEST COMPANY WITH MOTTO")
        print("="*50)
        
        company_data = {
            "name": "Letters Test Company Ltd",
            "address": "Jl. Sudirman No. 123, Jakarta Pusat 10220",
            "phone": "+62-21-1234567",
            "email": "info@letterstestcompany.com",
            "website": "https://letterstestcompany.com",
            "motto": "Profesional, Terpercaya, dan Inovatif",
            "npwp": "12.345.678.9-012.000",
            "bank_name": "Bank Mandiri",
            "bank_account": "1234567890",
            "bank_account_name": "Letters Test Company Ltd"
        }
        
        success, response = self.run_test(
            "Create Company with Motto", "POST", "companies", 201, 
            company_data, return_response=True
        )
        
        if success and response:
            self.created_company_id = response.get('id')
            print(f"   Created company ID: {self.created_company_id}")
            print(f"   Company motto: {response.get('motto')}")
        
        return success

    def test_signature_upload(self):
        """Test signature image upload functionality"""
        print("\n" + "="*50)
        print("TESTING SIGNATURE UPLOAD")
        print("="*50)
        
        try:
            # Create a simple test image (1x1 pixel PNG)
            # This is a minimal 1x1 pixel PNG image in base64
            test_image_b64 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChAI9jU77mgAAAABJRU5ErkJggg=="
            test_image_bytes = base64.b64decode(test_image_b64)
            
            # Prepare multipart form data
            files = {'file': ('test_signature.png', test_image_bytes, 'image/png')}
            
            url = f"{self.api_url}/upload-signature"
            response = requests.post(url, files=files, timeout=30)
            
            if response.status_code == 200:
                response_data = response.json()
                if 'signature' in response_data:
                    self.uploaded_signature = response_data['signature']
                    self.log_result("Signature Upload", True, f"Signature uploaded successfully")
                    print(f"   Signature data length: {len(self.uploaded_signature)} characters")
                else:
                    self.log_result("Signature Upload", False, error_msg="No signature field in response")
            else:
                error_msg = f"Status: {response.status_code}"
                try:
                    error_details = response.json()
                    error_msg += f" - {error_details}"
                except:
                    error_msg += f" - {response.text[:200]}"
                self.log_result("Signature Upload", False, error_msg=error_msg)
                
        except Exception as e:
            self.log_result("Signature Upload", False, error_msg=str(e))

    def test_letter_crud(self):
        """Test complete Letter CRUD operations"""
        print("\n" + "="*50)
        print("TESTING LETTER CRUD OPERATIONS")
        print("="*50)
        
        if not self.created_company_id:
            print("❌ Cannot test letters without a company. Skipping...")
            return
        
        # Test Create Letter with comprehensive data
        today = datetime.now().strftime('%Y-%m-%d')
        
        letter_data = {
            "letter_number": f"001/TEST-LETTER/{datetime.now().strftime('%m')}/{datetime.now().year}",
            "company_id": self.created_company_id,
            "date": today,
            "subject": "Penawaran Kerjasama Strategis dalam Bidang Teknologi Informasi",
            "letter_type": "cooperation",
            "recipient_name": "Bapak Direktur Utama",
            "recipient_position": "Direktur Utama",
            "recipient_address": "PT. Mitra Strategis Indonesia\nJl. Sudirman No. 456\nJakarta Pusat 10220",
            "content": "Dengan hormat,\n\nKami dari Letters Test Company Ltd bermaksud untuk menawarkan kerjasama strategis dalam bidang teknologi informasi. Perusahaan kami telah berpengalaman lebih dari 10 tahun dalam memberikan solusi IT terpadu yang profesional, terpercaya, dan inovatif.\n\nAdapun bentuk kerjasama yang kami tawarkan meliputi:\n1. Pengembangan sistem informasi terintegrasi\n2. Konsultasi teknologi informasi\n3. Pelatihan SDM di bidang IT\n4. Maintenance dan support sistem\n5. Cloud computing solutions\n6. Cybersecurity services\n\nKami yakin bahwa kerjasama ini akan memberikan manfaat yang optimal bagi kedua belah pihak. Untuk informasi lebih lanjut, kami siap melakukan presentasi dan diskusi lebih mendalam mengenai proposal kerjasama ini.\n\nDemikian surat penawaran ini kami sampaikan. Atas perhatian dan kerjasamanya, kami ucapkan terima kasih.",
            "attachments_count": 3,
            "cc_list": "1. Direktur Operasional PT. Mitra Strategis Indonesia\n2. Manager IT PT. Mitra Strategis Indonesia\n3. Kepala Bagian Procurement PT. Mitra Strategis Indonesia\n4. Arsip Perusahaan",
            "signatories": [
                {
                    "name": "John Doe",
                    "position": "Direktur Utama",
                    "signature_image": self.uploaded_signature if self.uploaded_signature else None
                },
                {
                    "name": "Jane Smith", 
                    "position": "Manager Business Development",
                    "signature_image": None
                }
            ]
        }
        
        success, response = self.run_test(
            "Create Letter", "POST", "letters", 201, 
            letter_data, return_response=True
        )
        
        if success and response:
            self.created_letter_id = response.get('id')
            print(f"   Created letter ID: {self.created_letter_id}")
            print(f"   Letter subject: {response.get('subject')}")
            print(f"   Letter type: {response.get('letter_type')}")
            print(f"   Signatories count: {len(response.get('signatories', []))}")
        
        # Test Get All Letters
        self.run_test("Get All Letters", "GET", "letters", 200)
        
        # Test Get Single Letter
        if self.created_letter_id:
            success, response = self.run_test(
                "Get Single Letter", "GET", 
                f"letters/{self.created_letter_id}", 200, return_response=True
            )
            
            if success and response:
                print(f"   Retrieved letter subject: {response.get('subject')}")
                print(f"   Content length: {len(response.get('content', ''))}")
            
            # Test Update Letter
            update_data = {**letter_data, "subject": "Updated: Penawaran Kerjasama Strategis dalam Bidang Teknologi Informasi"}
            self.run_test(
                "Update Letter", "PUT", 
                f"letters/{self.created_letter_id}", 200, update_data
            )

    def test_letter_types(self):
        """Test different letter types"""
        print("\n" + "="*50)
        print("TESTING DIFFERENT LETTER TYPES")
        print("="*50)
        
        if not self.created_company_id:
            print("❌ Cannot test letter types without a company. Skipping...")
            return
        
        letter_types = [
            {
                "type": "general",
                "subject": "Pemberitahuan Perubahan Alamat Kantor Pusat",
                "content": "Dengan hormat,\n\nKami memberitahukan bahwa mulai tanggal 1 Januari 2024, kantor pusat perusahaan kami akan pindah ke alamat baru.\n\nAlamat baru:\nJl. Gatot Subroto No. 456\nJakarta Selatan 12930\nTelp: +62-21-7654321\nEmail: info@newoffice.com\n\nSemua kegiatan operasional akan berjalan normal di lokasi baru tersebut. Mohon untuk memperbarui data alamat perusahaan kami dalam sistem Bapak/Ibu."
            },
            {
                "type": "request", 
                "subject": "Permohonan Izin Penggunaan Fasilitas Aula",
                "content": "Dengan hormat,\n\nSehubungan dengan rencana kegiatan pelatihan karyawan, kami bermaksud memohon izin penggunaan fasilitas aula perusahaan.\n\nDetail kegiatan:\n- Tanggal: 15-16 Februari 2024\n- Waktu: 08.00 - 17.00 WIB\n- Peserta: 50 orang\n- Jenis kegiatan: Pelatihan Leadership dan Team Building\n- Peralatan yang dibutuhkan: Proyektor, sound system, flipchart\n\nAtas perkenan dan kerjasamanya, kami ucapkan terima kasih."
            }
        ]
        
        for i, letter_type_data in enumerate(letter_types):
            letter_data = {
                "letter_number": f"00{i+2}/TEST-{letter_type_data['type'].upper()}/{datetime.now().strftime('%m')}/{datetime.now().year}",
                "company_id": self.created_company_id,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "subject": letter_type_data['subject'],
                "letter_type": letter_type_data['type'],
                "recipient_name": f"Bapak/Ibu Penerima {letter_type_data['type'].title()}",
                "recipient_position": "Pimpinan",
                "recipient_address": "Alamat Penerima Surat",
                "content": letter_type_data['content'],
                "attachments_count": 1 if letter_type_data['type'] == 'request' else 0,
                "cc_list": "Arsip" if letter_type_data['type'] == 'general' else "",
                "signatories": [
                    {
                        "name": "Test Signatory",
                        "position": "Manager",
                        "signature_image": None
                    }
                ]
            }
            
            self.run_test(
                f"Create {letter_type_data['type'].title()} Letter", "POST", "letters", 201, letter_data
            )

    def test_letter_pdf_generation(self):
        """Test PDF generation for letters"""
        print("\n" + "="*50)
        print("TESTING LETTER PDF GENERATION")
        print("="*50)
        
        if self.created_letter_id:
            try:
                url = f"{self.api_url}/letters/{self.created_letter_id}/pdf"
                response = requests.get(url, timeout=30)
                
                if response.status_code == 200 and response.headers.get('content-type') == 'application/pdf':
                    self.log_result("Letter PDF Generation", True, f"PDF size: {len(response.content)} bytes")
                    print(f"   PDF Content-Type: {response.headers.get('content-type')}")
                    print(f"   PDF Content-Disposition: {response.headers.get('content-disposition')}")
                    
                    # Save PDF for manual verification if needed
                    # with open(f"/tmp/test_letter_{self.created_letter_id}.pdf", "wb") as f:
                    #     f.write(response.content)
                    
                else:
                    self.log_result("Letter PDF Generation", False, error_msg=f"Status: {response.status_code}, Content-Type: {response.headers.get('content-type')}")
                    if response.status_code != 200:
                        print(f"   Response text: {response.text[:500]}")
            except Exception as e:
                self.log_result("Letter PDF Generation", False, error_msg=str(e))
        else:
            self.log_result("Letter PDF Generation", False, error_msg="No letter ID available for PDF generation test")

    def cleanup_test_data(self):
        """Clean up created test data"""
        print("\n" + "="*50)
        print("CLEANING UP TEST DATA")
        print("="*50)
        
        # Delete Letter
        if self.created_letter_id:
            self.run_test(
                "Delete Letter", "DELETE", 
                f"letters/{self.created_letter_id}", 200
            )
        
        # Delete Company
        if self.created_company_id:
            self.run_test(
                "Delete Company", "DELETE", 
                f"companies/{self.created_company_id}", 200
            )

    def run_all_tests(self):
        """Run all Letters API tests"""
        print("🚀 Starting Letters Feature API Tests")
        print(f"📍 Base URL: {self.base_url}")
        print(f"📍 API URL: {self.api_url}")
        
        # Setup
        if not self.setup_company():
            print("❌ Failed to setup company. Aborting tests.")
            return False
        
        # Test Letters functionality
        self.test_signature_upload()
        self.test_letter_crud()
        self.test_letter_types()
        self.test_letter_pdf_generation()
        
        # Cleanup
        self.cleanup_test_data()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL LETTERS TEST RESULTS")
        print("="*60)
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
        
        return self.tests_passed == self.tests_run

def main():
    """Main test execution"""
    tester = LettersAPITester()
    
    try:
        success = tester.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())