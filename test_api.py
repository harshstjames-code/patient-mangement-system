"""
API Testing Guide for Patient Management System
Run this file to test all API endpoints after starting the Flask app
"""

import requests
import json

# Base API URL
BASE_URL = "http://localhost:5000/api"

def print_header(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70)

def print_result(endpoint, method, status_code, response):
    print(f"\n{method} {endpoint}")
    print(f"Status Code: {status_code}")
    print(f"Response: {json.dumps(response, indent=2)}")

def test_health_check():
    """Test health check endpoint"""
    print_header("TEST 1: HEALTH CHECK")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print_result("/health", "GET", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_get_all_patients(existing=False):
    """Test get all patients endpoint"""
    print_header("TEST: GET ALL PATIENTS")
    try:
        response = requests.get(f"{BASE_URL}/get_all_patients")
        print_result("/get_all_patients", "GET", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_add_patient():
    """Test add patient endpoint"""
    print_header("TEST 2: ADD PATIENT")
    
    patient_data = {
        "name": "Rajesh Kumar",
        "age": 45,
        "gender": "Male",
        "contact": "9876543210",
        "location_city": "Delhi",
        "location_state": "Delhi",
        "location_pincode": "110001",
        "latitude": 28.6032,
        "longitude": 77.1824,
        "medical_history": "Hypertension, Type 2 Diabetes",
        "current_medications": "Lisinopril, Metformin",
        "allergies": "Aspirin"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/add_patient", json=patient_data)
        print_result("/add_patient", "POST", response.status_code, response.json())
        
        if response.status_code == 201:
            patient_id = response.json().get('patient_id')
            print(f"\n✓ Patient added successfully with ID: {patient_id}")
            return patient_id
        else:
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def test_get_patient(patient_id):
    """Test get patient endpoint"""
    print_header("TEST 3: GET PATIENT DETAILS")
    
    try:
        response = requests.get(f"{BASE_URL}/get_patient/{patient_id}")
        print_result(f"/get_patient/{patient_id}", "GET", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_predict_disease(patient_id):
    """Test disease prediction endpoint"""
    print_header("TEST 4: PREDICT DISEASE")
    
    prediction_data = {
        "patient_id": patient_id,
        "symptoms": "fever, cough, sore_throat, body_ache, fatigue, chills"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/predict_disease", json=prediction_data)
        print_result("/predict_disease", "POST", response.status_code, response.json())
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n✓ Disease: {result.get('predicted_disease')}")
            print(f"✓ Confidence: {result.get('confidence_percentage'):.2f}%")
            print(f"✓ Severity: {result.get('severity')}")
            return result
        else:
            return None
    except Exception as e:
        print(f"ERROR: {e}")
        return None

def test_get_severity():
    """Test severity score endpoint"""
    print_header("TEST 5: GET SEVERITY SCORE")
    
    severity_data = {
        "symptoms": "chest_pain, shortness_breath, severe headache"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/get_severity", json=severity_data)
        print_result("/get_severity", "POST", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_recommend_hospital(patient_id):
    """Test hospital recommendation endpoint"""
    print_header("TEST 6: RECOMMEND HOSPITALS")
    
    hospital_data = {
        "patient_id": patient_id,
        "severity": "Medium",
        "top_n": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/recommend_hospital", json=hospital_data)
        print_result("/recommend_hospital", "POST", response.status_code, response.json())
        
        if response.status_code == 200:
            hospitals = response.json().get('recommendations', [])
            print(f"\n✓ Found {len(hospitals)} hospitals")
            if hospitals:
                print(f"✓ Nearest hospital: {hospitals[0]['hospital_name']} ({hospitals[0]['distance_km']} km)")
            return True
        else:
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_recommend_free_hospitals(patient_id):
    """Test free hospital recommendation"""
    print_header("TEST 7: RECOMMEND FREE HOSPITALS")
    
    hospital_data = {
        "patient_id": patient_id,
        "top_n": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/recommend_free_hospitals", json=hospital_data)
        print_result("/recommend_free_hospitals", "POST", response.status_code, response.json())
        
        if response.status_code == 200:
            hospitals = response.json().get('recommendations', [])
            print(f"\n✓ Found {len(hospitals)} free hospitals")
            return True
        else:
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_filter_hospitals_by_cost(patient_id):
    """Test hospital filtering by cost"""
    print_header("TEST 8: FILTER HOSPITALS BY COST")
    
    hospital_data = {
        "patient_id": patient_id,
        "cost_category": "low",
        "top_n": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/filter_hospitals_by_cost", json=hospital_data)
        print_result("/filter_hospitals_by_cost", "POST", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_patient_history(patient_id):
    """Test patient history endpoint"""
    print_header("TEST 9: GET PATIENT HISTORY")
    
    try:
        response = requests.get(f"{BASE_URL}/patient_history/{patient_id}")
        print_result(f"/patient_history/{patient_id}", "GET", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_update_patient(patient_id):
    """Test update patient endpoint"""
    print_header("TEST 10: UPDATE PATIENT")
    
    update_data = {
        "age": 46,
        "medical_history": "Hypertension, Type 2 Diabetes, Thyroid Issues"
    }
    
    try:
        response = requests.put(f"{BASE_URL}/update_patient/{patient_id}", json=update_data)
        print_result(f"/update_patient/{patient_id}", "PUT", response.status_code, response.json())
        return response.status_code == 200
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def test_api_docs():
    """Test API documentation endpoint"""
    print_header("TEST: API DOCUMENTATION")
    
    try:
        response = requests.get(f"{BASE_URL}/api-docs")
        if response.status_code == 200:
            docs = response.json()
            print(f"✓ API Documentation available")
            print(f"✓ Total endpoint groups: {len(docs.get('endpoints', {}))}")
            return True
        else:
            return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False

def main():
    """Run all tests"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*15 + "PATIENT MANAGEMENT SYSTEM - API TESTS" + " "*15 + "║")
    print("╚" + "="*68 + "╝")
    
    print("\nMake sure the Flask application is running:")
    print("  python app.py")
    
    input("\nPress Enter to start testing...")
    
    results = {
        "Health Check": False,
        "Get All Patients": False,
        "Add Patient": False,
        "Get Patient": False,
        "Predict Disease": False,
        "Get Severity": False,
        "Recommend Hospital": False,
        "Recommend Free Hospitals": False,
        "Filter Hospitals": False,
        "Patient History": False,
        "Update Patient": False,
        "API Documentation": False
    }
    
    try:
        # Test health check
        results["Health Check"] = test_health_check()
        
        # Test get all patients
        results["Get All Patients"] = test_get_all_patients()
        
        # Test add patient
        patient_id = test_add_patient()
        results["Add Patient"] = patient_id is not None
        
        if patient_id:
            # Test get patient
            results["Get Patient"] = test_get_patient(patient_id)
            
            # Test predict disease
            pred_result = test_predict_disease(patient_id)
            results["Predict Disease"] = pred_result is not None
            
            # Test severity
            results["Get Severity"] = test_get_severity()
            
            # Test hospital recommendations
            results["Recommend Hospital"] = test_recommend_hospital(patient_id)
            
            # Test free hospitals
            results["Recommend Free Hospitals"] = test_recommend_free_hospitals(patient_id)
            
            # Test filter hospitals
            results["Filter Hospitals"] = test_filter_hospitals_by_cost(patient_id)
            
            # Test patient history
            results["Patient History"] = test_patient_history(patient_id)
            
            # Test update patient
            results["Update Patient"] = test_update_patient(patient_id)
        
        # Test API docs
        results["API Documentation"] = test_api_docs()
        
    except requests.exceptions.ConnectionError:
        print("\n" + "!"*70)
        print("ERROR: Cannot connect to Flask application!")
        print("Make sure the app is running: python app.py")
        print("!"*70 + "\n")
        return
    except Exception as e:
        print(f"\nUnexpected error: {e}")
        return
    
    # Print summary
    print_header("TEST SUMMARY")
    
    total_tests = len(results)
    passed_tests = sum(1 for v in results.values() if v)
    
    print(f"\nTests Passed: {passed_tests}/{total_tests}\n")
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status:<10} {test_name}")
    
    print("\n" + "="*70)
    if passed_tests == total_tests:
        print("✓ ALL TESTS PASSED! System is working correctly.")
    elif passed_tests >= total_tests - 2:
        print("⚠ MOST TESTS PASSED. Check failed tests for details.")
    else:
        print("✗ SOME TESTS FAILED. Check the errors above.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()
