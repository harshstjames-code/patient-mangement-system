"""
Hospital Recommendation Routes
Handles hospital recommendation requests
"""
from flask import Blueprint, request, jsonify
from database.hospital_recommender import HospitalRecommender
from database.db import PatientDatabase

hospital_routes = Blueprint('hospital_routes', __name__, url_prefix='/api')
recommender = HospitalRecommender()
db = PatientDatabase()


@hospital_routes.route('/recommend_hospital', methods=['POST'])
def recommend_hospital():
    """
    Recommend hospitals based on patient location and disease severity
    Expected JSON:
    {
        "patient_id": 1,
        "latitude": 28.6032,
        "longitude": 77.1824,
        "severity": "High",
        "top_n": 5
    }
    """
    try:
        data = request.get_json()
        
        # Get location - either from request or from patient record
        if 'latitude' in data and 'longitude' in data:
            latitude = float(data.get('latitude'))
            longitude = float(data.get('longitude'))
        elif 'patient_id' in data:
            patient = db.get_patient(data['patient_id'])
            if not patient:
                return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
            latitude = patient['latitude']
            longitude = patient['longitude']
        else:
            return jsonify({
                'status': 'error',
                'message': 'Please provide either (latitude, longitude) or patient_id'
            }), 400
        
        severity = data.get('severity', 'Medium')
        top_n = data.get('top_n', 5)
        
        # Get recommendations
        result = recommender.recommend_hospitals(
            patient_latitude=latitude,
            patient_longitude=longitude,
            predicted_severity=severity,
            top_n=top_n
        )
        
        # Store recommendations in database if patient_id provided
        if 'patient_id' in data and result['status'] == 'success':
            for rec in result['recommendations']:
                db.add_hospital_recommendation(
                    patient_id=data['patient_id'],
                    prediction_id=data.get('prediction_id'),
                    hospital_name=rec['hospital_name'],
                    hospital_city=rec['city'],
                    hospital_type=rec['type'],
                    cost_category=rec['cost_category'],
                    distance_km=rec['distance_km'],
                    contact=rec['contact'],
                    emergency=rec['emergency_available']
                )
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@hospital_routes.route('/recommend_free_hospitals', methods=['POST'])
def recommend_free_hospitals():
    """
    Recommend free government and charitable hospitals near patient
    Expected JSON:
    {
        "patient_id": 1,
        "top_n": 3
    }
    """
    try:
        data = request.get_json()
        
        if 'patient_id' not in data:
            return jsonify({
                'status': 'error',
                'message': 'patient_id is required'
            }), 400
        
        patient = db.get_patient(data['patient_id'])
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
        
        top_n = data.get('top_n', 3)
        
        result = recommender.get_free_hospitals_nearby(
            patient_latitude=patient['latitude'],
            patient_longitude=patient['longitude'],
            top_n=top_n
        )
        
        # Add patient info to result
        result['patient_name'] = patient['name']
        result['patient_location'] = {
            'city': patient['location_city'],
            'state': patient['location_state']
        }
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@hospital_routes.route('/filter_hospitals_by_cost', methods=['POST'])
def filter_hospitals_by_cost():
    """
    Filter and recommend hospitals by cost category
    Expected JSON:
    {
        "patient_id": 1,
        "cost_category": "free",  # free, low, medium, high
        "top_n": 5
    }
    """
    try:
        data = request.get_json()
        
        if 'patient_id' not in data or 'cost_category' not in data:
            return jsonify({
                'status': 'error',
                'message': 'patient_id and cost_category are required'
            }), 400
        
        patient = db.get_patient(data['patient_id'])
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
        
        cost_category = data.get('cost_category')
        top_n = data.get('top_n', 5)
        
        result = recommender.filter_hospitals_by_cost(
            patient_latitude=patient['latitude'],
            patient_longitude=patient['longitude'],
            cost_category=cost_category,
            top_n=top_n
        )
        
        result['patient_name'] = patient['name']
        
        return jsonify(result), 200 if result['status'] == 'success' else 400
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@hospital_routes.route('/patient_recommendations/<int:patient_id>', methods=['GET'])
def get_patient_recommendations(patient_id):
    """Get all hospital recommendations for a patient"""
    try:
        patient = db.get_patient(patient_id)
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
        
        recommendations = db.get_patient_recommendations(patient_id)
        
        return jsonify({
            'status': 'success',
            'patient_id': patient_id,
            'patient_name': patient['name'],
            'total_recommendations': len(recommendations),
            'recommendations': recommendations
        }), 200
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
