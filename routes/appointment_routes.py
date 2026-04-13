"""
Appointment Routes
Handles booking, cancellation, and appointment history
"""
from datetime import datetime
from flask import Blueprint, request, jsonify
from database.db import PatientDatabase


appointment_routes = Blueprint('appointment_routes', __name__, url_prefix='/api')
db = PatientDatabase()


@appointment_routes.route('/appointments/book', methods=['POST'])
def book_appointment():
    """Book an appointment for an existing patient"""
    try:
        data = request.get_json()
        required_fields = [
            'patient_id', 'doctor_id', 'hospital_id',
            'appointment_date', 'appointment_time'
        ]

        for field in required_fields:
            if field not in data or str(data.get(field)).strip() == '':
                return jsonify({'status': 'error', 'message': f'Missing field: {field}'}), 400

        appointment_date = data.get('appointment_date')
        appointment_time = data.get('appointment_time')

        # Validate date format and prevent past-date bookings.
        parsed_date = datetime.strptime(appointment_date, '%Y-%m-%d').date()
        if parsed_date < datetime.now().date():
            return jsonify({'status': 'error', 'message': 'Appointment date cannot be in the past'}), 400

        # Validate time format (HH:MM)
        datetime.strptime(appointment_time, '%H:%M')

        result = db.book_appointment(
            patient_id=int(data.get('patient_id')),
            doctor_id=int(data.get('doctor_id')),
            hospital_id=int(data.get('hospital_id')),
            appointment_date=appointment_date,
            appointment_time=appointment_time
        )

        status_code = 201 if result.get('status') == 'success' else 400
        return jsonify(result), status_code
    except ValueError:
        return jsonify({
            'status': 'error',
            'message': 'Invalid date/time format. Use appointment_date=YYYY-MM-DD and appointment_time=HH:MM'
        }), 400
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@appointment_routes.route('/appointments/<int:appointment_id>/cancel', methods=['PUT'])
def cancel_appointment(appointment_id):
    """Cancel an appointment"""
    try:
        success = db.cancel_appointment(appointment_id)
        if not success:
            return jsonify({'status': 'error', 'message': 'Appointment not found'}), 404

        return jsonify({
            'status': 'success',
            'message': 'Appointment cancelled successfully',
            'appointment_id': appointment_id
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@appointment_routes.route('/appointments/patient/<int:patient_id>', methods=['GET'])
def get_patient_appointments(patient_id):
    """Get complete appointment history for a patient"""
    try:
        patient = db.get_patient(patient_id)
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404

        appointments = db.get_patient_appointments(patient_id)
        return jsonify({
            'status': 'success',
            'patient_id': patient_id,
            'patient_name': patient['name'],
            'total_appointments': len(appointments),
            'appointments': appointments
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@appointment_routes.route('/appointments/patient/<int:patient_id>/upcoming', methods=['GET'])
def get_upcoming_appointments(patient_id):
    """Get upcoming booked appointments for dashboard widgets"""
    try:
        patient = db.get_patient(patient_id)
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404

        appointments = db.get_upcoming_appointments(patient_id)
        return jsonify({
            'status': 'success',
            'patient_id': patient_id,
            'patient_name': patient['name'],
            'total_upcoming': len(appointments),
            'appointments': appointments
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
