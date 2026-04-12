"""
Machine Learning Model Training Script
Trains a Random Forest classifier for disease prediction
"""
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import pickle
import os

# Create dataset if it doesn't exist
if not os.path.exists('dataset.csv'):
    print("Generating dataset...")
    from create_dataset import *
    print("Dataset generated successfully!")

# Load the dataset
print("Loading dataset...")
df = pd.read_csv('dataset.csv')

# Prepare features and target
print("\nPreparing features and target...")
# Convert symptoms (text) to numerical features using TF-IDF
vectorizer = TfidfVectorizer(lowercase=True, stop_words='english')
X_symptoms = vectorizer.fit_transform(df['symptoms'])

# Convert to dense array for RandomForest
X = X_symptoms.toarray()

# Target variable: disease
y = df['disease']

# Encode target labels
label_encoder = LabelEncoder()
y_encoded = label_encoder.fit_transform(y)

print(f"Features shape: {X.shape}")
print(f"Number of diseases: {len(label_encoder.classes_)}")
print(f"Diseases: {label_encoder.classes_}")

# Split the data
print("\nSplitting data into train and test sets...")
X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

# Train Random Forest model
print(f"\nTraining Random Forest classifier...")
print(f"Training set size: {len(X_train)}, Test set size: {len(X_test)}")

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=15,
    min_samples_split=5,
    min_samples_leaf=2,
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

# Evaluate the model
train_score = rf_model.score(X_train, y_train)
test_score = rf_model.score(X_test, y_test)

print(f"\nModel Training Complete!")
print(f"Training Accuracy: {train_score:.4f}")
print(f"Testing Accuracy: {test_score:.4f}")

# Save the model, vectorizer, and label encoder
print("\nSaving model files...")
with open('disease_model.pkl', 'wb') as f:
    pickle.dump(rf_model, f)
    
with open('tfidf_vectorizer.pkl', 'wb') as f:
    pickle.dump(vectorizer, f)
    
with open('label_encoder.pkl', 'wb') as f:
    pickle.dump(label_encoder, f)

# Create a mapping of diseases to dos and donts
disease_remedies = {}
for disease in label_encoder.classes_:
    disease_data = df[df['disease'] == disease].iloc[0]
    disease_remedies[disease] = {
        'dos': disease_data['dos'],
        'donts': disease_data['donts'],
        'severity': disease_data['severity']
    }

print("\nDisease Remedies Mapping:")
for disease, remedies in disease_remedies.items():
    print(f"\n{disease}:")
    print(f"  Severity: {remedies['severity']}")
    print(f"  Dos: {remedies['dos'][:50]}...")
    print(f"  Donts: {remedies['donts'][:50]}...")

# Save disease remedies
with open('disease_remedies.pkl', 'wb') as f:
    pickle.dump(disease_remedies, f)

print(f"\n✓ All model files saved successfully!")
print(f"✓ disease_model.pkl")
print(f"✓ tfidf_vectorizer.pkl")
print(f"✓ label_encoder.pkl")
print(f"✓ disease_remedies.pkl")
