"""
Load the saved disease prediction model and make predictions from binary symptoms.
The input must be a list of 6 binary values in the same order as the training data.
"""

import os
import pickle

import numpy as np
import pandas as pd


# Keep the feature order the same as in train_model.py.
FEATURE_COLUMNS = [
    "fever",
    "cough",
    "headache",
    "fatigue",
    "vomiting",
    "chest_pain",
]


# Load the trained model once when the module is imported.
MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model.pkl")
with open(MODEL_PATH, "rb") as file:
    model = pickle.load(file)


def predict_disease(symptoms_list):
    """
    Predict a disease from a list of binary symptoms.

    Args:
        symptoms_list: A list like [1, 0, 1, 1, 0, 0]

    Returns:
        dict with predicted disease and confidence score.
    """

    # Make sure the user passed exactly 6 symptoms.
    if len(symptoms_list) != len(FEATURE_COLUMNS):
        raise ValueError(
            f"symptoms_list must contain exactly {len(FEATURE_COLUMNS)} values"
        )

    # Build a DataFrame so the model receives the same feature names used in training.
    symptoms_frame = pd.DataFrame([symptoms_list], columns=FEATURE_COLUMNS)

    # Convert the input to a NumPy array for basic validation.
    symptoms_array = np.array(symptoms_list)

    # Ensure every symptom is binary.
    if not np.isin(symptoms_array, [0, 1]).all():
        raise ValueError("symptoms_list must contain only 0 or 1 values")

    # Get the predicted disease.
    predicted_disease = model.predict(symptoms_frame)[0]

    # Get prediction probabilities and select the confidence for the chosen class.
    probabilities = model.predict_proba(symptoms_frame)[0]
    class_index = list(model.classes_).index(predicted_disease)
    confidence = float(probabilities[class_index])

    return {
        "predicted_disease": predicted_disease,
        "confidence": confidence,
    }


if __name__ == "__main__":
    # Example input for testing the prediction function.
    sample_symptoms = [1, 0, 1, 1, 0, 0]
    result = predict_disease(sample_symptoms)

    print(f"Predicted Disease: {result['predicted_disease']}")
    print(f"Confidence: {result['confidence']:.2f}")
