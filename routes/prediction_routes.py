"""
Disease Prediction Routes
Handles disease prediction requests
"""
from flask import Blueprint, request, jsonify
from model.predict import DiseasePredictor
from database.db import PatientDatabase

prediction_routes = Blueprint('prediction_routes', __name__, url_prefix='/api')
predictor = DiseasePredictor()
db = PatientDatabase()


@prediction_routes.route('/predict_disease', methods=['POST'])
def predict_disease():
    """
    Predict disease from symptoms
    Expected JSON:
    {
        "patient_id": 1,
        "symptoms": "fever, cough, sore_throat, body_ache"
    }
    """
    try:
        data = request.get_json()
        
        if 'symptoms' not in data:
            return jsonify({'status': 'error', 'message': 'symptoms field is required'}), 400
        
        patient_id = data.get('patient_id')
        symptoms = data.get('symptoms')
        
        # Get prediction
        prediction_result = predictor.predict(symptoms)
        
        if prediction_result['status'] == 'error':
            return jsonify(prediction_result), 400
        
        # Calculate severity score
        severity_score = predictor.get_severity_score(symptoms)
        recommendation_confidence = predictor.get_recommendation_confidence(prediction_result)
        
        # Add to database if patient_id provided
        if patient_id:
            patient = db.get_patient(patient_id)
            if not patient:
                return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
            
            pred_id = db.add_prediction(
                patient_id=patient_id,
                symptoms=symptoms,
                predicted_disease=prediction_result['predicted_disease'],
                confidence=prediction_result['confidence'],
                severity=prediction_result['severity'],
                dos=prediction_result['dos'],
                donts=prediction_result['donts']
            )
            prediction_result['prediction_id'] = pred_id
        
        # Add additional metrics
        prediction_result['severity_score'] = severity_score
        prediction_result['recommendation_confidence'] = recommendation_confidence
        
        return jsonify(prediction_result), 200
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Prediction error: {str(e)}'
        }), 500


@prediction_routes.route('/get_severity', methods=['POST'])
def get_severity():
    """
    Get severity score for symptoms
    Expected JSON:
    {
        "symptoms": "fever, chest_pain, shortness_breath"
    }
    """
    try:
        data = request.get_json()
        
        if 'symptoms' not in data:
            return jsonify({'status': 'error', 'message': 'symptoms field is required'}), 400
        
        symptoms = data.get('symptoms')
        severity_score = predictor.get_severity_score(symptoms)
        
        # Determine severity level
        if severity_score >= 70:
            severity_level = 'High'
        elif severity_score >= 40:
            severity_level = 'Medium'
        else:
            severity_level = 'Low'
        
        return jsonify({
            'status': 'success',
            'symptoms': symptoms,
            'severity_score': severity_score,
            'severity_level': severity_level,
            'recommendation': 'Seek immediate medical attention' if severity_level == 'High' else 
                            'Consult a doctor' if severity_level == 'Medium' else 'Monitor symptoms'
        }), 200
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@prediction_routes.route('/patient_predictions/<int:patient_id>', methods=['GET'])
def get_patient_predictions(patient_id):
    """Get all predictions for a patient"""
    try:
        patient = db.get_patient(patient_id)
        if not patient:
            return jsonify({'status': 'error', 'message': 'Patient not found'}), 404
        
        predictions = db.get_patient_predictions(patient_id)
        
        return jsonify({
            'status': 'success',
            'patient_id': patient_id,
            'patient_name': patient['name'],
            'total_predictions': len(predictions),
            'predictions': predictions
        }), 200
            
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500
