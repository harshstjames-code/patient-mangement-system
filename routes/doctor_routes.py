"""
Doctor Routes
Handles doctor CRUD and availability operations
"""
from flask import Blueprint, request, jsonify
from database.db import PatientDatabase


doctor_routes = Blueprint('doctor_routes', __name__, url_prefix='/api')
db = PatientDatabase()


@doctor_routes.route('/doctors', methods=['POST'])
def add_doctor():
    """Add a doctor linked to a hospital"""
    try:
        data = request.get_json()
        required_fields = [
            'doctor_name', 'specialization', 'experience',
            'hospital_id', 'available_days', 'available_time_slots', 'consultation_fee'
        ]

        for field in required_fields:
            if field not in data or str(data.get(field)).strip() == '':
                return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400

        hospital = db.get_hospital(int(data.get('hospital_id')))
        if not hospital:
            return jsonify({'status': 'error', 'message': 'Hospital not found'}), 404

        doctor_id = db.add_doctor(
            doctor_name=data.get('doctor_name'),
            specialization=data.get('specialization'),
            experience=int(data.get('experience', 0)),
            hospital_id=int(data.get('hospital_id')),
            available_days=data.get('available_days', ''),
            available_time_slots=data.get('available_time_slots', ''),
            consultation_fee=float(data.get('consultation_fee', 0))
        )

        if not doctor_id:
            return jsonify({'status': 'error', 'message': 'Failed to add doctor'}), 500

        return jsonify({
            'status': 'success',
            'message': 'Doctor added successfully',
            'doctor_id': doctor_id
        }), 201
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@doctor_routes.route('/doctors', methods=['GET'])
def list_doctors():
    """List doctors by hospital and/or specialization"""
    try:
        hospital_id = request.args.get('hospital_id')
        specialization = request.args.get('specialization')

        doctors = db.get_doctors(
            hospital_id=int(hospital_id) if hospital_id else None,
            specialization=specialization
        )

        return jsonify({
            'status': 'success',
            'total_doctors': len(doctors),
            'hospital_id': hospital_id,
            'specialization_filter': specialization,
            'doctors': doctors
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@doctor_routes.route('/doctors/<int:doctor_id>/slots', methods=['GET'])
def get_doctor_slots(doctor_id):
    """Get available slots for a doctor on a given date"""
    try:
        appointment_date = request.args.get('appointment_date')
        if not appointment_date:
            return jsonify({'status': 'error', 'message': 'appointment_date is required'}), 400

        doctor = db.get_doctor(doctor_id)
        if not doctor:
            return jsonify({'status': 'error', 'message': 'Doctor not found'}), 404

        slots = db.get_doctor_available_slots(doctor_id, appointment_date)
        return jsonify({
            'status': 'success',
            'doctor_id': doctor_id,
            'doctor_name': doctor['doctor_name'],
            'appointment_date': appointment_date,
            'available_slots': slots,
            'total_slots': len(slots)
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
