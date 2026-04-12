"""
Patient Management Routes
Handles CRUD operations for patient records
"""
from flask import Blueprint, request, jsonify
from database.db import PatientDatabase

patient_routes = Blueprint('patient_routes', __name__, url_prefix='/api')
db = PatientDatabase()


@patient_routes.route('/add_patient', methods=['POST'])
def add_patient():
    """
    Add a new patient
    Expected JSON:
    {
        "name": "John Doe",
        "age": 35,
        "gender": "Male",
        "contact": "9876543210",
        "location_city": "Delhi",
        "location_state": "Delhi",
        "location_pincode": "110001",
        "latitude": 28.6032,
        "longitude": 77.1824,
        "medical_history": "Diabetes",
        "current_medications": "Metformin",
        "allergies": "Penicillin"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['name', 'age', 'gender', 'contact', 'location_city', 
                          'location_state', 'location_pincode', 'latitude', 'longitude']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400
        
        patient_id = db.add_patient(
            name=data['name'],
            age=data.get('age'),
            gender=data.get('gender'),
            contact=data.get('contact'),
            location_city=data.get('location_city'),
            location_state=data.get('location_state'),
            location_pincode=data.get('location_pincode'),
            latitude=float(data.get('latitude', 0)),
            longitude=float(data.get('longitude', 0)),
            medical_history=data.get('medical_history', ''),
            current_medications=data.get('current_medications', ''),
            allergies=data.get('allergies', '')
        )
        
        if patient_id:
            return jsonify({
                'status': 'success',
                'message': 'Patient added successfully',
                'patient_id': patient_id
            }), 201
        else:
            return jsonify({'status': 'error', 'message': 'Failed to add patient'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@patient_routes.route('/get_patient/<int:patient_id>', methods=['GET'])
def get_patient(patient_id):
    """Get patient details by ID"""
    try:
        patient = db.get_patient(patient_id)
        
        if patient:
            return jsonify({
                'status': 'success',
                'patient': patient
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@patient_routes.route('/get_all_patients', methods=['GET'])
def get_all_patients():
    """Get all patients"""
    try:
        patients = db.get_all_patients()
        
        return jsonify({
            'status': 'success',
            'total_patients': len(patients),
            'patients': patients
        }), 200
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@patient_routes.route('/update_patient/<int:patient_id>', methods=['PUT'])
def update_patient(patient_id):
    """
    Update patient details
    Can update any fields
    """
    try:
        data = request.get_json()
        
        # Check if patient exists
        patient = db.get_patient(patient_id)
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
        
        # Update patient
        success = db.update_patient(patient_id, **data)
        
        if success:
            updated_patient = db.get_patient(patient_id)
            return jsonify({
                'status': 'success',
                'message': 'Patient updated successfully',
                'patient': updated_patient
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to update patient'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@patient_routes.route('/delete_patient/<int:patient_id>', methods=['DELETE'])
def delete_patient(patient_id):
    """Delete a patient record"""
    try:
        # Check if patient exists
        patient = db.get_patient(patient_id)
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
        
        # Delete patient
        success = db.delete_patient(patient_id)
        
        if success:
            return jsonify({
                'status': 'success',
                'message': 'Patient deleted successfully'
            }), 200
        else:
            return jsonify({'status': 'error', 'message': 'Failed to delete patient'}), 500
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@patient_routes.route('/patient_history/<int:patient_id>', methods=['GET'])
def get_patient_history(patient_id):
    """Get patient's prediction history"""
    try:
        patient = db.get_patient(patient_id)
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
        
        predictions = db.get_patient_predictions(patient_id)
        recommendations = db.get_patient_recommendations(patient_id)
        
        return jsonify({
            'status': 'success',
            'patient_name': patient['name'],
            'total_predictions': len(predictions),
            'total_recommendations': len(recommendations),
            'predictions': predictions,
            'recommendations': recommendations
        }), 200
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
