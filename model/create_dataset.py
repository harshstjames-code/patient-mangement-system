"""
Script to generate synthetic training dataset for disease prediction
This creates a CSV file with symptoms and corresponding diseases
"""
import pandas as pd
import numpy as np

# Define symptoms, diseases, dos, and don'ts
symptoms_list = [
    'fever', 'cough', 'sore_throat', 'runny_nose', 'sneezing',
    'body_ache', 'fatigue', 'headache', 'nausea', 'vomiting',
    'diarrhea', 'chest_pain', 'shortness_breath', 'dizziness', 'skin_rash',
    'itching', 'joint_pain', 'muscle_pain', 'loss_appetite', 'chills'
]

diseases_data = {
    'Flu': {
        'common_symptoms': ['fever', 'cough', 'sore_throat', 'body_ache', 'fatigue', 'chills'],
        'dos': 'Drink warm fluids|Take rest|Take prescribed medicines|Consume vitamin C|Use saline nasal drops',
        'donts': 'Avoid cold food|Avoid heavy exercise|Avoid dust exposure|Avoid smoking|Avoid alcohol',
        'severity': 'Medium'
    },
    'Cold': {
        'common_symptoms': ['runny_nose', 'sneezing', 'sore_throat', 'cough', 'fatigue', 'headache'],
        'dos': 'Stay hydrated|Get adequate rest|Use honey and ginger tea|Eat nutritious food|Use nasal saline',
        'donts': 'Avoid crowded places|Avoid cold weather|Avoid dairy initially|Avoid strenuous activities',
        'severity': 'Low'
    },
    'COVID-19': {
        'common_symptoms': ['fever', 'cough', 'shortness_breath', 'fatigue', 'loss_appetite', 'body_ache'],
        'dos': 'Isolate yourself|Monitor oxygen levels|Take prescribed antivirals|Stay hydrated|Seek medical help if worsening',
        'donts': 'Avoid contact with others|Avoid strenuous exercise|Avoid smoking|Dont self-medicate|Avoid public places',
        'severity': 'High'
    },
    'Bronchitis': {
        'common_symptoms': ['cough', 'chest_pain', 'shortness_breath', 'fatigue', 'body_ache', 'fever'],
        'dos': 'Use humidifier|Drink warm liquids|Take prescribed cough syrup|Rest adequately|Use steam inhalation',
        'donts': 'Avoid smoking|Avoid air pollution|Avoid cold air|Avoid irritants|Dont ignore persistent cough',
        'severity': 'High'
    },
    'Asthma': {
        'common_symptoms': ['shortness_breath', 'cough', 'chest_pain', 'wheezing', 'fatigue'],
        'dos': 'Use inhaler regularly|Avoid triggers|Stay hydrated|Exercise moderately|Maintain air quality',
        'donts': 'Avoid allergens|Avoid strenuous exercise|Avoid pollution|Avoid smoking|Dont skip medications',
        'severity': 'High'
    },
    'Gastroenteritis': {
        'common_symptoms': ['nausea', 'vomiting', 'diarrhea', 'body_ache', 'fever', 'loss_appetite'],
        'dos': 'Drink ORS|Eat light food|Rest|Take prescribed antibiotics|Stay hydrated',
        'donts': 'Avoid spicy food|Avoid dairy|Avoid oily food|Avoid antibiotics without consultation|Dont ignore dehydration',
        'severity': 'Medium'
    },
    'Headache': {
        'common_symptoms': ['headache', 'dizziness', 'nausea', 'fatigue', 'body_ache'],
        'dos': 'Rest in dark room|Stay hydrated|Apply cold compress|Take prescribed pain reliever|Relax muscles',
        'donts': 'Avoid bright lights|Avoid loud noises|Avoid caffeine excess|Avoid stress|Dont ignore persistent headaches',
        'severity': 'Low'
    },
    'Allergy': {
        'common_symptoms': ['skin_rash', 'itching', 'sneezing', 'runny_nose', 'body_ache'],
        'dos': 'Avoid allergens|Use antihistamines|Apply moisturizer|Stay hydrated|Use air purifier',
        'donts': 'Avoid triggering foods|Avoid irritants|Avoid scratching|Avoid harsh soaps|Dont ignore symptoms',
        'severity': 'Low'
    },
    'Dengue': {
        'common_symptoms': ['fever', 'body_ache', 'joint_pain', 'headache', 'skin_rash', 'chills'],
        'dos': 'Rest completely|Take paracetamol|Stay hydrated|Monitor platelet counts|Use mosquito net',
        'donts': 'Avoid aspirin|Avoid strenuous activity|Avoid going out|Dont take NSAIDs|Avoid self-treatment',
        'severity': 'High'
    },
    'Migraine': {
        'common_symptoms': ['headache', 'dizziness', 'nausea', 'fatigue', 'body_ache'],
        'dos': 'Rest in quiet dark place|Take prescribed medication|Stay hydrated|Apply warm compress|Manage stress',
        'donts': 'Avoid triggers|Avoid bright lights|Avoid loud noise|Avoid skipping meals|Dont ignore symptoms',
        'severity': 'Medium'
    }
}

# Generate synthetic dataset
np.random.seed(42)
data = []

for disease, info in diseases_data.items():
    # Generate 50 samples per disease
    for _ in range(50):
        # Create symptom combinations
        base_symptoms = info['common_symptoms'].copy()
        num_additional = np.random.randint(0, 4)
        additional_symptoms = list(np.random.choice([s for s in symptoms_list if s not in base_symptoms], 
                                                     num_additional, replace=False))
        all_symptoms = base_symptoms + additional_symptoms
        
        data.append({
            'symptoms': ', '.join(sorted(all_symptoms)),
            'disease': disease,
            'dos': info['dos'],
            'donts': info['donts'],
            'severity': info['severity']
        })

# Create DataFrame and save
df = pd.DataFrame(data)
df.to_csv('dataset.csv', index=False)
print(f"Dataset created with {len(df)} samples")
print(f"\nDataset preview:")
print(df.head(10))
print(f"\nDisease distribution:")
print(df['disease'].value_counts())
