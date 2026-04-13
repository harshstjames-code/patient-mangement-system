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
            cursor.execute('PRAGMA foreign_keys = ON')
            
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

            # Create hospitals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS hospitals (
                    hospital_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    hospital_name TEXT NOT NULL,
                    address TEXT NOT NULL,
                    city TEXT NOT NULL,
                    state TEXT NOT NULL,
                    pincode TEXT NOT NULL,
                    contact_number TEXT NOT NULL,
                    email TEXT,
                    departments TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Create doctors table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS doctors (
                    doctor_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    doctor_name TEXT NOT NULL,
                    specialization TEXT NOT NULL,
                    experience INTEGER DEFAULT 0,
                    hospital_id INTEGER NOT NULL,
                    available_days TEXT,
                    available_time_slots TEXT,
                    consultation_fee REAL DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (hospital_id) REFERENCES hospitals (hospital_id) ON DELETE CASCADE
                )
            ''')

            # Create appointments table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS appointments (
                    appointment_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    patient_id INTEGER NOT NULL,
                    doctor_id INTEGER NOT NULL,
                    hospital_id INTEGER NOT NULL,
                    appointment_date TEXT NOT NULL,
                    appointment_time TEXT NOT NULL,
                    appointment_status TEXT NOT NULL DEFAULT 'Booked',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (patient_id) REFERENCES patients (id) ON DELETE CASCADE,
                    FOREIGN KEY (doctor_id) REFERENCES doctors (doctor_id) ON DELETE CASCADE,
                    FOREIGN KEY (hospital_id) REFERENCES hospitals (hospital_id) ON DELETE CASCADE,
                    UNIQUE (doctor_id, appointment_date, appointment_time)
                )
            ''')
            
            self.conn.commit()
            print("[OK] Database initialized successfully!")
            
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
            
            print(f"[OK] Patient added with ID: {patient_id}")
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
            print(f"[OK] Patient {patient_id} updated successfully")
            return True
            
        except sqlite3.Error as e:
            print(f"Error updating patient: {e}")
            return False
    
    def delete_patient(self, patient_id):
        """Delete a patient record"""
        try:
            cursor = self.conn.cursor()
            
            # Delete related predictions and recommendations first
            cursor.execute('DELETE FROM appointments WHERE patient_id = ?', (patient_id,))
            cursor.execute('DELETE FROM hospital_recommendations WHERE patient_id = ?', (patient_id,))
            cursor.execute('DELETE FROM predictions WHERE patient_id = ?', (patient_id,))
            cursor.execute('DELETE FROM patients WHERE id = ?', (patient_id,))
            
            self.conn.commit()
            print(f"[OK] Patient {patient_id} and related records deleted")
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

    def add_hospital(self, hospital_name, address, city, state, pincode,
                     contact_number, email='', departments=''):
        """Add a new hospital"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO hospitals
                (hospital_name, address, city, state, pincode, contact_number, email, departments)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (hospital_name, address, city, state, pincode, contact_number, email, departments))

            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding hospital: {e}")
            return None

    def get_hospitals(self, city=None, state=None, pincode=None):
        """Get hospitals with optional location filters"""
        try:
            cursor = self.conn.cursor()
            query = 'SELECT * FROM hospitals WHERE 1=1'
            values = []

            if city:
                query += ' AND LOWER(city) = LOWER(?)'
                values.append(city)
            if state:
                query += ' AND LOWER(state) = LOWER(?)'
                values.append(state)
            if pincode:
                query += ' AND pincode = ?'
                values.append(pincode)

            query += ' ORDER BY hospital_name ASC'
            cursor.execute(query, values)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching hospitals: {e}")
            return []

    def get_hospital(self, hospital_id):
        """Get hospital by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM hospitals WHERE hospital_id = ?', (hospital_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error fetching hospital: {e}")
            return None

    def get_hospitals_by_location(self, location):
        """Search hospitals by city/state/pincode"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT * FROM hospitals
                WHERE LOWER(city) = LOWER(?) OR LOWER(state) = LOWER(?) OR pincode = ?
                ORDER BY hospital_name ASC
            ''', (location, location, location))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error searching hospitals by location: {e}")
            return []

    def add_doctor(self, doctor_name, specialization, experience, hospital_id,
                   available_days='', available_time_slots='', consultation_fee=0):
        """Add a doctor linked to a hospital"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO doctors
                (doctor_name, specialization, experience, hospital_id, available_days,
                 available_time_slots, consultation_fee)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (doctor_name, specialization, experience, hospital_id, available_days,
                  available_time_slots, consultation_fee))

            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error adding doctor: {e}")
            return None

    def get_doctors(self, hospital_id=None, specialization=None):
        """Get doctors with optional hospital and specialization filters"""
        try:
            cursor = self.conn.cursor()
            query = '''
                SELECT d.*, h.hospital_name, h.city, h.state, h.contact_number
                FROM doctors d
                JOIN hospitals h ON h.hospital_id = d.hospital_id
                WHERE 1=1
            '''
            values = []

            if hospital_id:
                query += ' AND d.hospital_id = ?'
                values.append(hospital_id)
            if specialization:
                query += ' AND LOWER(d.specialization) = LOWER(?)'
                values.append(specialization)

            query += ' ORDER BY d.doctor_name ASC'
            cursor.execute(query, values)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching doctors: {e}")
            return []

    def get_doctor(self, doctor_id):
        """Get doctor by ID"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('SELECT * FROM doctors WHERE doctor_id = ?', (doctor_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
        except sqlite3.Error as e:
            print(f"Error fetching doctor: {e}")
            return None

    def get_doctor_available_slots(self, doctor_id, appointment_date):
        """Return available slots by removing already booked doctor slots"""
        try:
            doctor = self.get_doctor(doctor_id)
            if not doctor:
                return None

            raw_slots = doctor.get('available_time_slots') or ''
            declared_slots = [slot.strip() for slot in raw_slots.split(',') if slot.strip()]
            if not declared_slots:
                return []

            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT appointment_time
                FROM appointments
                WHERE doctor_id = ? AND appointment_date = ? AND appointment_status = 'Booked'
            ''', (doctor_id, appointment_date))
            rows = cursor.fetchall()
            booked = {row['appointment_time'] for row in rows}

            return [slot for slot in declared_slots if slot not in booked]
        except sqlite3.Error as e:
            print(f"Error getting available slots: {e}")
            return []

    def book_appointment(self, patient_id, doctor_id, hospital_id, appointment_date, appointment_time):
        """Book appointment with double-booking prevention"""
        try:
            patient = self.get_patient(patient_id)
            if not patient:
                return {'status': 'error', 'message': 'Patient not found'}

            doctor = self.get_doctor(doctor_id)
            if not doctor:
                return {'status': 'error', 'message': 'Doctor not found'}

            hospital = self.get_hospital(hospital_id)
            if not hospital:
                return {'status': 'error', 'message': 'Hospital not found'}

            if doctor['hospital_id'] != hospital_id:
                return {'status': 'error', 'message': 'Doctor is not linked to selected hospital'}

            available_slots = self.get_doctor_available_slots(doctor_id, appointment_date)
            if available_slots is None:
                return {'status': 'error', 'message': 'Doctor not found'}
            if appointment_time not in available_slots:
                return {
                    'status': 'error',
                    'message': 'Selected time slot is unavailable for this doctor'
                }

            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO appointments
                (patient_id, doctor_id, hospital_id, appointment_date, appointment_time, appointment_status)
                VALUES (?, ?, ?, ?, ?, 'Booked')
            ''', (patient_id, doctor_id, hospital_id, appointment_date, appointment_time))

            self.conn.commit()
            return {
                'status': 'success',
                'appointment_id': cursor.lastrowid,
                'message': 'Appointment booked successfully'
            }
        except sqlite3.IntegrityError:
            return {
                'status': 'error',
                'message': 'This doctor is already booked for the selected date and time'
            }
        except sqlite3.Error as e:
            print(f"Error booking appointment: {e}")
            return {'status': 'error', 'message': 'Failed to book appointment'}

    def cancel_appointment(self, appointment_id):
        """Cancel an appointment"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                UPDATE appointments
                SET appointment_status = 'Cancelled', updated_at = CURRENT_TIMESTAMP
                WHERE appointment_id = ?
            ''', (appointment_id,))

            self.conn.commit()
            if cursor.rowcount == 0:
                return False
            return True
        except sqlite3.Error as e:
            print(f"Error cancelling appointment: {e}")
            return False

    def get_patient_appointments(self, patient_id):
        """Get appointment history for a patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT a.*, d.doctor_name, d.specialization,
                       h.hospital_name, h.city AS hospital_city, h.state AS hospital_state,
                       h.contact_number AS hospital_contact
                FROM appointments a
                JOIN doctors d ON d.doctor_id = a.doctor_id
                JOIN hospitals h ON h.hospital_id = a.hospital_id
                WHERE a.patient_id = ?
                ORDER BY a.appointment_date DESC, a.appointment_time DESC
            ''', (patient_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching patient appointments: {e}")
            return []

    def get_upcoming_appointments(self, patient_id):
        """Get booked upcoming appointments for a patient"""
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                SELECT a.*, d.doctor_name, d.specialization,
                       h.hospital_name, h.city AS hospital_city, h.state AS hospital_state
                FROM appointments a
                JOIN doctors d ON d.doctor_id = a.doctor_id
                JOIN hospitals h ON h.hospital_id = a.hospital_id
                WHERE a.patient_id = ?
                  AND a.appointment_status = 'Booked'
                  AND DATE(a.appointment_date) >= DATE('now')
                ORDER BY a.appointment_date ASC, a.appointment_time ASC
            ''', (patient_id,))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as e:
            print(f"Error fetching upcoming appointments: {e}")
            return []
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            print("[OK] Database connection closed")


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
