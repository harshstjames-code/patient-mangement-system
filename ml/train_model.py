"""
Train a simple disease prediction model from binary symptom data.
The model uses a Random Forest Classifier and saves the trained model with pickle.
"""

import os
import pickle

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split


# Define the feature columns in the exact order used by the dataset.
FEATURE_COLUMNS = [
    "fever",
    "cough",
    "headache",
    "fatigue",
    "vomiting",
    "chest_pain",
]


def main():
    # Find the dataset in the same folder as this script.
    base_dir = os.path.dirname(os.path.abspath(__file__))
    dataset_path = os.path.join(base_dir, "dataset.csv")
    model_path = os.path.join(base_dir, "model.pkl")

    # Load the CSV dataset into a pandas DataFrame.
    df = pd.read_csv(dataset_path)

    # Split the data into input features and target label.
    X = df[FEATURE_COLUMNS]
    y = df["disease"]

    # Split the data so we can check how well the model performs.
    # Stratify keeps the disease distribution similar in train and test sets.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.25,
        random_state=42,
        stratify=y,
    )

    # Create the Random Forest model.
    model = RandomForestClassifier(
        n_estimators=100,
        random_state=42,
    )

    # Train the model on the training data.
    model.fit(X_train, y_train)

    # Measure accuracy on the training set.
    training_accuracy = model.score(X_train, y_train)
    test_accuracy = model.score(X_test, y_test)

    # Save the trained model to a pickle file.
    with open(model_path, "wb") as file:
        pickle.dump(model, file)

    # Print a short summary so the user can see the model trained correctly.
    print("[OK] Model training completed")
    print(f"Training Accuracy: {training_accuracy:.2f}")
    print(f"Test Accuracy: {test_accuracy:.2f}")
    print(f"Model saved to: {model_path}")


if __name__ == "__main__":
    main()
