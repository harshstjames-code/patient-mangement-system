"""
Patient Management System - Main Flask Application
Machine Learning based disease prediction with location-aware hospital recommendations
"""
from flask import Flask, render_template, jsonify
from flask_cors import CORS
import os

# Import routes
from routes.patient_routes import patient_routes
from routes.prediction_routes import prediction_routes
from routes.hospital_routes import hospital_routes
from routes.doctor_routes import doctor_routes
from routes.appointment_routes import appointment_routes

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
CORS(app)

# Register blueprints (routes)
app.register_blueprint(patient_routes)
app.register_blueprint(prediction_routes)
app.register_blueprint(hospital_routes)
app.register_blueprint(doctor_routes)
app.register_blueprint(appointment_routes)


@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """Dashboard page"""
    return render_template('dashboard.html')


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'success',
        'message': 'Patient Management System is running!',
        'version': '1.0.0'
    }), 200


@app.route('/api/api-docs', methods=['GET'])
def api_docs():
    """API documentation"""
    docs = {
        'status': 'success',
        'message': 'Patient Management System API Documentation',
        'endpoints': {
            'Patient Management': {
                'POST /api/add_patient': 'Add a new patient',
                'GET /api/get_patient/<id>': 'Get patient details',
                'GET /api/get_all_patients': 'Get all patients',
                'PUT /api/update_patient/<id>': 'Update patient details',
                'DELETE /api/delete_patient/<id>': 'Delete a patient',
                'GET /api/patient_history/<id>': 'Get patient history'
            },
            'Disease Prediction': {
                'POST /api/predict_disease': 'Predict disease from symptoms',
                'POST /api/get_severity': 'Get severity score for symptoms',
                'GET /api/patient_predictions/<id>': 'Get patient predictions'
            },
            'Hospital Recommendations': {
                'POST /api/recommend_hospital': 'Get hospital recommendations',
                'POST /api/recommend_free_hospitals': 'Get free hospitals nearby',
                'POST /api/filter_hospitals_by_cost': 'Filter hospitals by cost',
                'GET /api/patient_recommendations/<id>': 'Get patient recommendations'
            },
            'Hospitals': {
                'POST /api/hospitals': 'Add hospital',
                'GET /api/hospitals': 'List hospitals (city/state/pincode filters)',
                'GET /api/hospitals/location/<location>': 'Get hospitals by city/state/pincode',
                'GET /api/hospitals/<id>': 'Get hospital with available doctors',
                'GET /api/hospitals/<id>/doctors': 'Get doctors in hospital (optional specialization filter)'
            },
            'Doctors': {
                'POST /api/doctors': 'Add doctor',
                'GET /api/doctors': 'List doctors (hospital/specialization filters)',
                'GET /api/doctors/<id>/slots?appointment_date=YYYY-MM-DD': 'Get available slots for doctor'
            },
            'Appointments': {
                'POST /api/appointments/book': 'Book appointment',
                'PUT /api/appointments/<id>/cancel': 'Cancel appointment',
                'GET /api/appointments/patient/<patient_id>': 'Get appointment history',
                'GET /api/appointments/patient/<patient_id>/upcoming': 'Get upcoming appointments'
            },
            'System': {
                'GET /api/health': 'Health check',
                'GET /api/api-docs': 'API documentation'
            }
        }
    }
    return jsonify(docs), 200


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Endpoint not found',
        'error': str(error)
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'status': 'error',
        'message': 'Internal server error',
        'error': str(error)
    }), 500


if __name__ == '__main__':
    print("="*80)
    print("PATIENT MANAGEMENT SYSTEM - ML Based Disease Prediction")
    print("="*80)
    print("\nStarting Flask application...")
    print("\nAPI Endpoints:")
    print("  - Patient Management: /api/add_patient, /api/get_patient, etc.")
    print("  - Disease Prediction: /api/predict_disease")
    print("  - Hospital Recommendations: /api/recommend_hospital")
    print("\nVisit http://localhost:5000 for the web interface")
    print("Visit http://localhost:5000/api/api-docs for API documentation")
    print("="*80 + "\n")
    
    # Run the app
    app.run(debug=True, host='0.0.0.0', port=5000)
