"""
Disease Prediction Module
Uses the trained ML model to predict diseases from symptoms
"""
import pickle
import os
import numpy as np

class DiseasePredictor:
    def __init__(self):
        """Initialize the predictor with trained model and encoders"""
        self.model = None
        self.vectorizer = None
        self.label_encoder = None
        self.disease_remedies = None
        self.load_model()
    
    def load_model(self):
        """Load the trained model and supporting files"""
        try:
            # Check if model files exist
            model_files = ['disease_model.pkl', 'tfidf_vectorizer.pkl', 
                          'label_encoder.pkl', 'disease_remedies.pkl']
            
            model_dir = os.path.dirname(os.path.abspath(__file__))
            
            for file in model_files:
                file_path = os.path.join(model_dir, file)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Model file not found: {file}")
            
            # Load model files
            with open(os.path.join(model_dir, 'disease_model.pkl'), 'rb') as f:
                self.model = pickle.load(f)
            
            with open(os.path.join(model_dir, 'tfidf_vectorizer.pkl'), 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            with open(os.path.join(model_dir, 'label_encoder.pkl'), 'rb') as f:
                self.label_encoder = pickle.load(f)
            
            with open(os.path.join(model_dir, 'disease_remedies.pkl'), 'rb') as f:
                self.disease_remedies = pickle.load(f)
            
            print("✓ Model loaded successfully!")
            
        except FileNotFoundError as e:
            print(f"Error: {e}")
            print("Please train the model first using train_model.py")
            raise
    
    def predict(self, symptoms_text):
        """
        Predict disease from symptoms
        
        Args:
            symptoms_text (str): Comma-separated symptoms or symptom description
        
        Returns:
            dict: Prediction results with disease, confidence, dos, donts, severity
        """
        try:
            # Vectorize the input symptoms
            symptoms_vector = self.vectorizer.transform([symptoms_text])
            symptoms_array = symptoms_vector.toarray()
            
            # Get prediction probabilities
            probabilities = self.model.predict_proba(symptoms_array)[0]
            predicted_class = np.argmax(probabilities)
            confidence = probabilities[predicted_class]
            
            # Decode the predicted disease
            predicted_disease = self.label_encoder.inverse_transform([predicted_class])[0]
            
            # Get remedies and recommendations
            remedies = self.disease_remedies.get(predicted_disease, {})
            
            # Get top 3 possible diseases
            top_3_indices = np.argsort(probabilities)[-3:][::-1]
            top_diseases = []
            for idx in top_3_indices:
                disease = self.label_encoder.inverse_transform([idx])[0]
                prob = probabilities[idx]
                top_diseases.append({
                    'disease': disease,
                    'confidence': float(prob),
                    'severity': self.disease_remedies[disease].get('severity', 'Unknown')
                })
            
            result = {
                'status': 'success',
                'predicted_disease': predicted_disease,
                'confidence': float(confidence),
                'confidence_percentage': float(confidence * 100),
                'severity': remedies.get('severity', 'Unknown'),
                'dos': remedies.get('dos', 'N/A').split('|'),
                'donts': remedies.get('donts', 'N/A').split('|'),
                'top_3_predictions': top_diseases,
                'message': f"Based on the symptoms provided, the predicted disease is {predicted_disease} with {confidence*100:.2f}% confidence."
            }
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Prediction failed: {str(e)}"
            }
    
    def get_severity_score(self, symptoms_text):
        """
        Calculate severity score (0-100) based on symptoms
        Higher score indicates more severe condition
        """
        severity_keywords = {
            'critical': ['chest_pain', 'shortness_breath', 'unconscious', 'severe bleeding'],
            'high': ['high_fever', 'severe_vomiting', 'loss_appetite', 'difficulty_breathing'],
            'medium': ['fever', 'cough', 'body_ache', 'vomiting'],
            'low': ['cough', 'runny_nose', 'sneezing', 'headache']
        }
        
        symptoms_lower = symptoms_text.lower()
        score = 0
        
        for symptom in severity_keywords.get('critical', []):
            if symptom in symptoms_lower:
                score = 90
                break
        
        if score == 0:
            for symptom in severity_keywords.get('high', []):
                if symptom in symptoms_lower:
                    score = max(score, 70)
        
        if score == 0:
            for symptom in severity_keywords.get('medium', []):
                if symptom in symptoms_lower:
                    score = max(score, 40)
        
        if score == 0:
            score = 20
        
        return score
    
    def get_recommendation_confidence(self, prediction_result):
        """
        Get recommendation confidence based on model confidence
        Returns 'High', 'Medium', or 'Low'
        """
        confidence = prediction_result.get('confidence', 0)
        
        if confidence >= 0.7:
            return 'High'
        elif confidence >= 0.5:
            return 'Medium'
        else:
            return 'Low'


# Example usage
if __name__ == "__main__":
    # Initialize predictor
    predictor = DiseasePredictor()
    
    # Test predictions
    test_cases = [
        "fever, cough, sore_throat, body_ache, fatigue",
        "runny_nose, sneezing, sore_throat, cough",
        "fever, chest_pain, shortness_breath, cough",
        "nausea, vomiting, diarrhea, fever"
    ]
    
    print("\n" + "="*80)
    print("DISEASE PREDICTION TESTS")
    print("="*80 + "\n")
    
    for symptoms in test_cases:
        print(f"\nInput Symptoms: {symptoms}")
        print("-" * 60)
        
        result = predictor.predict(symptoms)
        
        if result['status'] == 'success':
            print(f"Predicted Disease: {result['predicted_disease']}")
            print(f"Confidence: {result['confidence_percentage']:.2f}%")
            print(f"Severity: {result['severity']}")
            print(f"Severity Score: {predictor.get_severity_score(symptoms)}/100")
            print(f"Recommendation Confidence: {predictor.get_recommendation_confidence(result)}")
            print(f"\nDo's:")
            for do in result['dos']:
                print(f"  • {do.strip()}")
            print(f"\nDon'ts:")
            for dont in result['donts']:
                print(f"  • {dont.strip()}")
            print(f"\nTop 3 Predictions:")
            for i, pred in enumerate(result['top_3_predictions'], 1):
                print(f"  {i}. {pred['disease']} ({pred['confidence']*100:.2f}%) - {pred['severity']}")
        else:
            print(f"Error: {result['message']}")
        
        print()
