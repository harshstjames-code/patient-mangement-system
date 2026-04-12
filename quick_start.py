"""
Patient Management System - Quick Start & Testing Guide

This file provides step-by-step instructions to run the complete system
"""

# STEP 1: INITIAL SETUP
# =====================

# Windows Users:
# 1. Open Command Prompt
# 2. Navigate to project folder
# 3. Run: setup.bat

# Linux/Mac Users:
# 1. Open Terminal
# 2. Navigate to project folder
# 3. Run: chmod +x setup.sh && ./setup.sh


# STEP 2: MANUAL SETUP (If setup scripts don't work)
# ====================================================

# 1. Create Virtual Environment
#    Windows: python -m venv venv
#    Linux/Mac: python3 -m venv venv

# 2. Activate Virtual Environment
#    Windows: venv\Scripts\activate.bat
#    Linux/Mac: source venv/bin/activate

# 3. Install Dependencies
#    pip install -r requirements.txt

# 4. Generate Training Dataset
#    cd model
#    python create_dataset.py

# 5. Generate Hospital Database
#    cd ../database
#    python create_hospital_data.py

# 6. Train ML Model
#    cd ../model
#    python train_model.py


# STEP 3: RUN THE APPLICATION
# =============================

# 1. Ensure virtual environment is activated
# 2. Navigate to project root
# 3. Run: python app.py
# 4. Open browser: http://localhost:5000


# STEP 4: DATABASE VERIFICATION
# ===============================

import sys
import os

def check_database():
    """Verify database is initialized"""
    if os.path.exists('database/patients.db'):
        print("✓ Database exists")
        # Try to connect
        try:
            from database.db import PatientDatabase
            db = PatientDatabase()
            print("✓ Database connection successful")
            db.close()
            return True
        except Exception as e:
            print(f"✗ Database error: {e}")
            return False
    else:
        print("✗ Database not found. Run app first.")
        return False


def check_model_files():
    """Verify ML model files exist"""
    model_dir = 'model'
    required_files = [
        'disease_model.pkl',
        'tfidf_vectorizer.pkl',
        'label_encoder.pkl',
        'disease_remedies.pkl'
    ]
    
    all_exist = True
    for file in required_files:
        path = os.path.join(model_dir, file)
        if os.path.exists(path):
            print(f"✓ {file}")
        else:
            print(f"✗ {file} NOT FOUND")
            all_exist = False
    
    return all_exist


def check_hospital_data():
    """Verify hospital data exists"""
    if os.path.exists('database/hospital_data.csv'):
        print("✓ Hospital database exists")
        import pandas as pd
        df = pd.read_csv('database/hospital_data.csv')
        print(f"  - Total hospitals: {len(df)}")
        print(f"  - Government: {len(df[df['type']=='government'])}")
        print(f"  - Private: {len(df[df['type']=='private'])}")
        print(f"  - Charitable: {len(df[df['type']=='charitable'])}")
        return True
    else:
        print("✗ Hospital data not found")
        return False


def check_training_data():
    """Verify training dataset exists"""
    if os.path.exists('model/dataset.csv'):
        print("✓ Training dataset exists")
        import pandas as pd
        df = pd.read_csv('model/dataset.csv')
        print(f"  - Total samples: {len(df)}")
        print(f"  - Diseases: {df['disease'].nunique()}")
        return True
    else:
        print("✗ Training dataset not found")
        return False


if __name__ == "__main__":
    print("\n" + "="*60)
    print("PATIENT MANAGEMENT SYSTEM - VERIFICATION")
    print("="*60 + "\n")
    
    print("Checking Model Files:")
    print("-" * 40)
    model_ok = check_model_files()
    
    print("\nChecking Training Data:")
    print("-" * 40)
    data_ok = check_training_data()
    
    print("\nChecking Hospital Data:")
    print("-" * 40)
    hospital_ok = check_hospital_data()
    
    print("\nChecking Database:")
    print("-" * 40)
    db_ok = check_database()
    
    print("\n" + "="*60)
    if model_ok and data_ok and hospital_ok:
        print("✓ All systems ready! Run 'python app.py' to start.")
    else:
        print("✗ Some components missing. Run setup again.")
    print("="*60 + "\n")


# STEP 5: USAGE EXAMPLES
# =======================

"""

1. ACCESS WEB INTERFACE:
   http://localhost:5000
   - Dashboard: http://localhost:5000/dashboard

2. ADD PATIENT EXAMPLE:
   Use the "Add Patient" form in dashboard with:
   - Name: John Doe
   - Age: 35
   - Gender: Male
   - Contact: 9876543210
   - City: Delhi
   - State: Delhi
   - Pincode: 110001
   - Latitude: 28.6032
   - Longitude: 77.1824

3. PREDICT DISEASE EXAMPLE:
   Use the "Predict Disease" form with:
   - Patient: John Doe
   - Symptoms: fever, cough, sore_throat, body_ache, fatigue

4. FIND HOSPITALS EXAMPLE:
   Use the "Find Hospitals" form with:
   - Patient: John Doe
   - Severity: High
   - This will show 5 nearest hospitals

5. API TESTING (using cURL):

   Get all patients:
   curl http://localhost:5000/api/get_all_patients

   Add patient:
   curl -X POST http://localhost:5000/api/add_patient \\
     -H "Content-Type: application/json" \\
     -d '{"name":"Test","age":30,"gender":"Male","contact":"98765","location_city":"Delhi","location_state":"Delhi","location_pincode":"110001","latitude":28.6032,"longitude":77.1824}'

   Predict disease:
   curl -X POST http://localhost:5000/api/predict_disease \\
     -H "Content-Type: application/json" \\
     -d '{"patient_id":1,"symptoms":"fever, cough, sore_throat"}'

   Find hospitals:
   curl -X POST http://localhost:5000/api/recommend_hospital \\
     -H "Content-Type: application/json" \\
     -d '{"patient_id":1,"severity":"High"}'

"""

# STEP 6: TROUBLESHOOTING
# ========================

"""

Problem: "ModuleNotFoundError: No module named 'flask'"
Solution: Activate virtual environment and run: pip install -r requirements.txt

Problem: "No such file or directory: 'model/disease_model.pkl'"
Solution: Train the model by running: cd model && python train_model.py

Problem: "Port 5000 already in use"
Solution: Edit app.py line and change port from 5000 to 5001

Problem: "Database is locked"
Solution: Close the application and delete patients.db, then restart

Problem: "Static files not loading"
Solution: Make sure you're in the correct project directory

Problem: "Predictions are inaccurate"
Solution: More training data and hyperparameter tuning can improve accuracy

"""

# STEP 7: FILES CHECKLIST
# ========================

"""

Project Structure:
✓ app.py - Main Flask application
✓ requirements.txt - Python dependencies
✓ README.md - Full documentation
✓ setup.bat - Windows setup script
✓ setup.sh - Linux/Mac setup script

/model:
✓ __init__.py - Package marker
✓ create_dataset.py - Generate synthetic training data
✓ train_model.py - Train ML model
✓ predict.py - Disease prediction module

/database:
✓ __init__.py - Package marker
✓ db.py - SQLite database management
✓ hospital_recommender.py - Hospital recommendation engine
✓ create_hospital_data.py - Generate hospital database

/routes:
✓ __init__.py - Package marker
✓ patient_routes.py - Patient management endpoints
✓ prediction_routes.py - Disease prediction endpoints
✓ hospital_routes.py - Hospital recommendation endpoints

/templates:
✓ index.html - Home page
✓ dashboard.html - Main dashboard

/static:
✓ style.css - Home page styles
✓ dashboard.css - Dashboard styles
✓ script.js - Home page JavaScript
✓ dashboard.js - Dashboard JavaScript

"""

print("""
COMPLETE! The Patient Management System is ready.

NEXT STEPS:
1. Verify everything is working: python quick_start.py
2. Start the application: python app.py
3. Open http://localhost:5000 in your browser
4. Add a patient, predict disease, and find hospitals!

For detailed documentation, see README.md
""")
