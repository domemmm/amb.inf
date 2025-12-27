#!/usr/bin/env python3
"""
Backend API Testing for Ambulatorio Infermieristico
Tests all authentication, patient management, and appointment APIs
"""

import requests
import sys
import json
from datetime import datetime, date
from typing import Dict, List, Optional

class AmbulatorioAPITester:
    def __init__(self, base_url="https://infermiere-app.preview.emergentagent.com"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api"
        self.token = None
        self.current_user = None
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []
        self.session = requests.Session()
        
    def log(self, message: str, level: str = "INFO"):
        """Log test messages"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {level}: {message}")
        
    def run_test(self, name: str, method: str, endpoint: str, expected_status: int, 
                 data: Optional[Dict] = None, params: Optional[Dict] = None) -> tuple:
        """Run a single API test"""
        url = f"{self.api_url}/{endpoint}"
        headers = {'Content-Type': 'application/json'}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'

        self.tests_run += 1
        self.log(f"🔍 Testing {name}...")
        
        try:
            if method == 'GET':
                response = self.session.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = self.session.post(url, json=data, headers=headers, params=params)
            elif method == 'PUT':
                response = self.session.put(url, json=data, headers=headers, params=params)
            elif method == 'DELETE':
                response = self.session.delete(url, headers=headers, params=params)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                self.log(f"✅ {name} - Status: {response.status_code}")
                try:
                    return True, response.json() if response.content else {}
                except:
                    return True, {}
            else:
                self.log(f"❌ {name} - Expected {expected_status}, got {response.status_code}")
                self.log(f"   Response: {response.text[:200]}")
                self.failed_tests.append({
                    "test": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })
                return False, {}

        except Exception as e:
            self.log(f"❌ {name} - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "error": str(e)
            })
            return False, {}

    def test_auth_login_domenico(self):
        """Test login with Domenico (access to both ambulatories)"""
        success, response = self.run_test(
            "Login Domenico",
            "POST",
            "auth/login",
            200,
            data={"username": "Domenico", "password": "infermiere"}
        )
        if success and 'access_token' in response:
            self.token = response['access_token']
            self.current_user = response['user']
            self.log(f"   User ambulatori: {self.current_user['ambulatori']}")
            return True
        return False

    def test_auth_login_giovanna(self):
        """Test login with Giovanna (access only to PTA Centro)"""
        success, response = self.run_test(
            "Login Giovanna",
            "POST", 
            "auth/login",
            200,
            data={"username": "Giovanna", "password": "infermiere"}
        )
        if success and 'access_token' in response:
            user = response['user']
            expected_ambulatori = ["pta_centro"]
            if user['ambulatori'] == expected_ambulatori:
                self.log(f"   ✅ Giovanna has correct ambulatori: {user['ambulatori']}")
                return True
            else:
                self.log(f"   ❌ Giovanna ambulatori mismatch. Expected: {expected_ambulatori}, Got: {user['ambulatori']}")
        return False

    def test_auth_invalid_credentials(self):
        """Test login with invalid credentials"""
        success, response = self.run_test(
            "Invalid Login",
            "POST",
            "auth/login", 
            401,
            data={"username": "invalid", "password": "wrong"}
        )
        return success

    def test_auth_me(self):
        """Test current user endpoint"""
        if not self.token:
            self.log("❌ No token available for /auth/me test")
            return False
            
        success, response = self.run_test(
            "Get Current User",
            "GET",
            "auth/me",
            200
        )
        return success

    def test_create_patient_med_pta(self):
        """Test creating MED patient in PTA Centro"""
        if not self.token:
            return False
            
        patient_data = {
            "nome": "Mario",
            "cognome": "Rossi",
            "tipo": "MED",
            "ambulatorio": "pta_centro",
            "data_nascita": "1980-01-01",
            "telefono": "123456789"
        }
        
        success, response = self.run_test(
            "Create MED Patient PTA",
            "POST",
            "patients",
            201,
            data=patient_data
        )
        
        if success and 'id' in response:
            self.created_patient_id = response['id']
            self.log(f"   Created patient ID: {self.created_patient_id}")
            return True
        return False

    def test_create_patient_picc_villa(self):
        """Test creating PICC patient in Villa Ginestre"""
        if not self.token:
            return False
            
        patient_data = {
            "nome": "Anna",
            "cognome": "Verdi", 
            "tipo": "PICC",
            "ambulatorio": "villa_ginestre",
            "data_nascita": "1975-05-15"
        }
        
        success, response = self.run_test(
            "Create PICC Patient Villa",
            "POST",
            "patients",
            201,
            data=patient_data
        )
        return success

    def test_create_patient_med_villa_should_fail(self):
        """Test creating MED patient in Villa Ginestre (should fail)"""
        if not self.token:
            return False
            
        patient_data = {
            "nome": "Test",
            "cognome": "Fail",
            "tipo": "MED", 
            "ambulatorio": "villa_ginestre"
        }
        
        success, response = self.run_test(
            "Create MED Patient Villa (Should Fail)",
            "POST",
            "patients",
            400,
            data=patient_data
        )
        return success

    def test_get_patients_pta(self):
        """Test getting patients for PTA Centro"""
        if not self.token:
            return False
            
        success, response = self.run_test(
            "Get Patients PTA Centro",
            "GET",
            "patients",
            200,
            params={"ambulatorio": "pta_centro"}
        )
        
        if success:
            self.log(f"   Found {len(response)} patients in PTA Centro")
        return success

    def test_get_patients_villa(self):
        """Test getting patients for Villa Ginestre"""
        if not self.token:
            return False
            
        success, response = self.run_test(
            "Get Patients Villa Ginestre", 
            "GET",
            "patients",
            200,
            params={"ambulatorio": "villa_ginestre"}
        )
        
        if success:
            self.log(f"   Found {len(response)} patients in Villa Ginestre")
        return success

    def test_create_appointment(self):
        """Test creating an appointment"""
        if not self.token or not hasattr(self, 'created_patient_id'):
            return False
            
        today = date.today().strftime("%Y-%m-%d")
        appointment_data = {
            "patient_id": self.created_patient_id,
            "ambulatorio": "pta_centro",
            "data": today,
            "ora": "09:00",
            "tipo": "MED",
            "prestazioni": ["medicazione_semplice"]
        }
        
        success, response = self.run_test(
            "Create Appointment",
            "POST",
            "appointments",
            201,
            data=appointment_data
        )
        
        if success and 'id' in response:
            self.created_appointment_id = response['id']
            return True
        return False

    def test_get_appointments(self):
        """Test getting appointments"""
        if not self.token:
            return False
            
        today = date.today().strftime("%Y-%m-%d")
        success, response = self.run_test(
            "Get Appointments",
            "GET", 
            "appointments",
            200,
            params={"ambulatorio": "pta_centro", "data": today}
        )
        
        if success:
            self.log(f"   Found {len(response)} appointments for today")
        return success

    def test_get_documents_pta(self):
        """Test getting documents for PTA Centro"""
        if not self.token:
            return False
            
        success, response = self.run_test(
            "Get Documents PTA Centro",
            "GET",
            "documents",
            200,
            params={"ambulatorio": "pta_centro"}
        )
        
        if success:
            self.log(f"   Found {len(response)} documents for PTA Centro")
            # Should have both MED and PICC documents
            med_docs = [d for d in response if d['categoria'] == 'MED']
            picc_docs = [d for d in response if d['categoria'] == 'PICC']
            self.log(f"   MED documents: {len(med_docs)}, PICC documents: {len(picc_docs)}")
        return success

    def test_get_documents_villa(self):
        """Test getting documents for Villa Ginestre"""
        if not self.token:
            return False
            
        success, response = self.run_test(
            "Get Documents Villa Ginestre",
            "GET",
            "documents", 
            200,
            params={"ambulatorio": "villa_ginestre"}
        )
        
        if success:
            self.log(f"   Found {len(response)} documents for Villa Ginestre")
            # Should have only PICC documents
            med_docs = [d for d in response if d['categoria'] == 'MED']
            picc_docs = [d for d in response if d['categoria'] == 'PICC']
            self.log(f"   MED documents: {len(med_docs)}, PICC documents: {len(picc_docs)}")
            if len(med_docs) == 0:
                self.log("   ✅ Villa Ginestre correctly shows no MED documents")
            else:
                self.log("   ❌ Villa Ginestre should not show MED documents")
        return success

    def test_get_statistics_pta(self):
        """Test getting statistics for PTA Centro"""
        if not self.token:
            return False
            
        current_year = datetime.now().year
        success, response = self.run_test(
            "Get Statistics PTA Centro",
            "GET",
            "statistics",
            200,
            params={"ambulatorio": "pta_centro", "anno": current_year}
        )
        
        if success:
            self.log(f"   Statistics: {response.get('totale_accessi', 0)} total accessi")
        return success

    def test_calendar_endpoints(self):
        """Test calendar helper endpoints"""
        current_year = datetime.now().year
        
        # Test holidays
        success1, response1 = self.run_test(
            "Get Calendar Holidays",
            "GET",
            "calendar/holidays",
            200,
            params={"anno": current_year}
        )
        
        if success1:
            self.log(f"   Found {len(response1)} holidays for {current_year}")
        
        # Test time slots
        success2, response2 = self.run_test(
            "Get Time Slots",
            "GET",
            "calendar/slots",
            200
        )
        
        if success2:
            morning = len(response2.get('mattina', []))
            afternoon = len(response2.get('pomeriggio', []))
            self.log(f"   Time slots: {morning} morning, {afternoon} afternoon")
        
        return success1 and success2

    def run_all_tests(self):
        """Run all tests in sequence"""
        self.log("🚀 Starting Ambulatorio Infermieristico API Tests")
        self.log(f"   Base URL: {self.base_url}")
        
        # Authentication tests
        self.log("\n📋 Authentication Tests")
        self.test_auth_login_domenico()
        self.test_auth_login_giovanna()
        self.test_auth_invalid_credentials()
        self.test_auth_me()
        
        # Patient management tests
        self.log("\n👥 Patient Management Tests")
        self.test_create_patient_med_pta()
        self.test_create_patient_picc_villa()
        self.test_create_patient_med_villa_should_fail()
        self.test_get_patients_pta()
        self.test_get_patients_villa()
        
        # Appointment tests
        self.log("\n📅 Appointment Tests")
        self.test_create_appointment()
        self.test_get_appointments()
        
        # Document tests
        self.log("\n📄 Document Tests")
        self.test_get_documents_pta()
        self.test_get_documents_villa()
        
        # Statistics tests
        self.log("\n📊 Statistics Tests")
        self.test_get_statistics_pta()
        
        # Calendar tests
        self.log("\n📆 Calendar Tests")
        self.test_calendar_endpoints()
        
        # Print results
        self.print_results()
        
        return self.tests_passed == self.tests_run

    def print_results(self):
        """Print test results summary"""
        self.log(f"\n📊 Test Results Summary")
        self.log(f"   Tests run: {self.tests_run}")
        self.log(f"   Tests passed: {self.tests_passed}")
        self.log(f"   Tests failed: {len(self.failed_tests)}")
        self.log(f"   Success rate: {(self.tests_passed/self.tests_run*100):.1f}%")
        
        if self.failed_tests:
            self.log(f"\n❌ Failed Tests:")
            for failure in self.failed_tests:
                self.log(f"   - {failure.get('test', 'Unknown')}")
                if 'error' in failure:
                    self.log(f"     Error: {failure['error']}")
                elif 'expected' in failure:
                    self.log(f"     Expected: {failure['expected']}, Got: {failure['actual']}")

def main():
    tester = AmbulatorioAPITester()
    success = tester.run_all_tests()
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())