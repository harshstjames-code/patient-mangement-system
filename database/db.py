"""
Database Module
Handles patient data persistence using SQLite
"""
import sqlite3
import os
from datetime import datetime
from pathlib import Path

class PatientDatabase:
    def __init__(self, db_name='patients.db'):
        """Initialize database connection"""
        base_dir = Path(__file__).resolve().parent.parent
        self.db_path = str(base_dir / db_name)
        self.conn = None
        self.init_database()
    
    def init_database(self):
        """Create database and tables if they don't exist"""
        try:
            # Flask handles requests in different threads in dev mode.
            # Allow the same connection object to be used by request threads.
            self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
            self.conn.row_factory = sqlite3.Row
            cursor = self.conn.cursor()
            
            # Create patients table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patients (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    contact TEXT,
                    location_city TEXT,
                    location_state TEXT,
                    location_pincode TEXT,
                    latitude REAL,
                    longitude REAL,
                    medical_history TEXT,
                    current_medications TEXT,
                    allergies TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create predictions table (for storing prediction history)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS predictions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    symptoms TEXT NOT NULL,
                    predicted_disease TEXT,
                    confidence REAL,
                    severity TEXT,
                    dos TEXT,
                    donts TEXT,
                    predicted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id)
                )
            ''')
            
            # Create hospital recommendations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hospital_recommendations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    prediction_id INTEGER,
                    hospital_name TEXT,
                    hospital_city TEXT,
                    hospital_type TEXT,
                    cost_category TEXT,
                    distance_km REAL,
                    contact TEXT,
                    emergency TEXT,
                    recommended_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id),
                    FOREIGN KEY (prediction_id) REFERENCES predictions (id)
                )
            ''')
            
            self.conn.commit()
            print("✓ Database initialized successfully!")
            
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise
    
    def add_patient(self, name, age, gender, contact, location_city, location_state, 
                    location_pincode, latitude, longitude, medical_history='', 
                    current_medications='', allergies=''):
        """Add a new patient to the database"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO patients 
                (name, age, gender, contact, location_city, location_state, 
                 location_pincode, latitude, longitude, medical_history, 
                 current_medications, allergies)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (name, age, gender, contact, location_city, location_state, 
                  location_pincode, latitude, longitude, medical_history, 
                  current_medications, allergies))
            
            self.conn.commit()
            patient_id = cursor.lastrowid
            
            print(f"✓ Patient added with ID: {patient_id}")
            return patient_id
            
        except sqlite3.Error as e:
            print(f"Error adding patient: {e}")
            return None
    
    def get_patient(self, patient_id):
        """Get patient details by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM patients WHERE id = ?
            ''', (patient_id,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            else:
                return None
                
        except sqlite3.Error as e:
            print(f"Error fetching patient: {e}")
            return None
    
    def get_all_patients(self):
        """Get all patients"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM patients ORDER BY id DESC')
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"Error fetching patients: {e}")
            return []
    
    def update_patient(self, patient_id, **kwargs):
        """Update patient details"""
        try:
            # Build the SET clause dynamically
            set_clause = ', '.join([f"{key} = ?" for key in kwargs.keys()])
            set_clause += ', updated_at = CURRENT_TIMESTAMP'
            
            values = list(kwargs.values()) + [patient_id]
            
            cursor = self.conn.cursor()
            cursor.execute(f'''
                UPDATE patients SET {set_clause} WHERE id = ?
            ''', values)
            
            self.conn.commit()
            print(f"✓ Patient {patient_id} updated successfully")
            return True
            
        except sqlite3.Error as e:
            print(f"Error updating patient: {e}")
            return False
    
    def delete_patient(self, patient_id):
        """Delete a patient record"""
        try:
            cursor = self.conn.cursor()
            
            # Delete related predictions and recommendations first
            cursor.execute('DELETE FROM hospital_recommendations WHERE patient_id = ?', (patient_id,))
            cursor.execute('DELETE FROM predictions WHERE patient_id = ?', (patient_id,))
            cursor.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
            
            self.conn.commit()
            print(f"✓ Patient {patient_id} and related records deleted")
            return True
            
        except sqlite3.Error as e:
            print(f"Error deleting patient: {e}")
            return False
    
    def add_prediction(self, patient_id, symptoms, predicted_disease, confidence, 
                       severity, dos, donts):
        """Store a disease prediction"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO predictions 
                (patient_id, symptoms, predicted_disease, confidence, severity, dos, donts)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, symptoms, predicted_disease, confidence, severity, 
                  '|'.join(dos) if isinstance(dos, list) else dos,
                  '|'.join(donts) if isinstance(donts, list) else donts))
            
            self.conn.commit()
            prediction_id = cursor.lastrowid
            return prediction_id
            
        except sqlite3.Error as e:
            print(f"Error saving prediction: {e}")
            return None
    
    def get_patient_predictions(self, patient_id):
        """Get all predictions for a patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM predictions WHERE patient_id = ? ORDER BY predicted_at DESC
            ''', (patient_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"Error fetching predictions: {e}")
            return []
    
    def add_hospital_recommendation(self, patient_id, prediction_id, hospital_name, 
                                   hospital_city, hospital_type, cost_category, 
                                   distance_km, contact, emergency):
        """Store a hospital recommendation"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO hospital_recommendations 
                (patient_id, prediction_id, hospital_name, hospital_city, hospital_type, 
                 cost_category, distance_km, contact, emergency)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (patient_id, prediction_id, hospital_name, hospital_city, hospital_type, 
                  cost_category, distance_km, contact, emergency))
            
            self.conn.commit()
            rec_id = cursor.lastrowid
            return rec_id
            
        except sqlite3.Error as e:
            print(f"Error saving hospital recommendation: {e}")
            return None
    
    def get_patient_recommendations(self, patient_id):
        """Get all hospital recommendations for a patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM hospital_recommendations WHERE patient_id = ? 
                ORDER BY recommended_at DESC
            ''', (patient_id,))
            
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
            
        except sqlite3.Error as e:
            print(f"Error fetching recommendations: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("✓ Database connection closed")


# Example usage
if __name__ == "__main__":
    # Initialize database
    db = PatientDatabase('patients.db')
    
    # Add a sample patient
    patient_id = db.add_patient(
        name="John Doe",
        age=35,
        gender="Male",
        contact="9876543210",
        location_city="Delhi",
        location_state="Delhi",
        location_pincode="110001",
        latitude=28.6032,
        longitude=77.1824,
        medical_history="Diabetes, Hypertension",
        current_medications="Metformin, Lisinopril",
        allergies="Penicillin"
    )
    
    # Get patient details
    if patient_id:
        patient = db.get_patient(patient_id)
        print(f"\nPatient Details:")
        for key, value in patient.items():
            print(f"  {key}: {value}")
    
    # Close connection
    db.close()
