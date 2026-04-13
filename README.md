# Patient Management System - ML Based Disease Prediction with Hospital Recommendations

A comprehensive healthcare management system combining machine learning for disease prediction with location-aware hospital recommendations.

## 🏥 Features

### 1. **Patient Record Management**
- Store comprehensive patient information (demographics, medical history, medications, allergies)
- Location tracking (city, state, pincode, latitude, longitude)
- CRUD operations for patient data
- View complete patient history timeline

### 2. **AI-Powered Disease Prediction**
- Machine Learning model using Random Forest classifier
- Analyzes symptoms to predict diseases
- Provides confidence scores and top 3 predictions
- Calculates disease severity scores
- Generates personalized health recommendations (Do's and Don'ts)

### 3. **Location-Based Hospital Finder**
- Recommends nearby hospitals based on patient location
- Prioritizes government and low-cost hospitals for high-severity cases
- Filters by cost category (free, low, medium, high)
- Shows hospital details: type, contact, emergency availability
- Calculates distance from patient location

### 4. **Doctor Appointment Booking**
- Hospital module with searchable hospital directory (city, state, pincode)
- Doctor module linked to hospitals with specialization and schedule
- Appointment booking workflow: patient -> hospital -> doctor -> slot -> book
- Double-booking prevention for doctor/date/time slot
- Appointment status tracking (Booked, Completed, Cancelled)
- Appointment history and upcoming appointments

### 5. **Prediction History & Tracking**
- Stores all predictions and recommendations
- View complete medical journey
- Track confidence levels and severity scores
- Historical data for better health management

### 6. **User-Friendly Dashboard**
- Intuitive web interface for all operations
- Real-time API documentation
- Multiple sections: Patients, Predictions, Hospitals, Doctor Directory, Appointments, History
- Responsive design for desktop and mobile

## 💻 Tech Stack

- **Backend**: Python Flask
- **Machine Learning**: Scikit-learn (Random Forest Classifier)
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **API Architecture**: REST API
- **Version Control**: Git compatible

## 📁 Project Structure

\`\`\`
patient_management_ml/
├── app.py                          # Main Flask application
├── requirements.txt                # Python dependencies
├── model/
│   ├── train_model.py             # ML model training script
│   ├── predict.py                 # Disease prediction module
│   ├── create_dataset.py          # Synthetic dataset generation
│   ├── disease_model.pkl          # Trained model (generated)
│   ├── tfidf_vectorizer.pkl       # TF-IDF vectorizer (generated)
│   ├── label_encoder.pkl          # Label encoder (generated)
│   ├── disease_remedies.pkl       # Disease remedies mapping (generated)
│   └── dataset.csv                # Training dataset (generated)
├── database/
│   ├── db.py                      # Database module
│   ├── hospital_recommender.py    # Hospital recommendation engine
│   ├── create_hospital_data.py    # Hospital dataset generation
│   ├── hospital_data.csv          # Hospital database (generated)
│   └── patients.db                # SQLite database (generated)
├── routes/
│   ├── patient_routes.py          # Patient management endpoints
│   ├── prediction_routes.py       # Disease prediction endpoints
│   └── hospital_routes.py         # Hospital recommendation endpoints
│   ├── doctor_routes.py           # Doctor management endpoints
│   └── appointment_routes.py      # Appointment booking endpoints
├── templates/
│   ├── index.html                 # Home page
│   └── dashboard.html             # Dashboard interface
└── static/
    ├── style.css                  # Home page styles
    ├── dashboard.css              # Dashboard styles
    ├── script.js                  # Home page JavaScript
    └── dashboard.js               # Dashboard JavaScript
\`\`\`

## 🚀 Quick Start

### 1. Installation

\`\`\`bash
# Clone or navigate to project directory
cd patient_management_ml

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\\Scripts\\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
\`\`\`

### 2. Generate Datasets

\`\`\`bash
# Generate training dataset
cd model
python create_dataset.py

# Generate hospital dataset
cd ../database
python create_hospital_data.py
\`\`\`

### 3. Train ML Model

\`\`\`bash
cd ../model
python train_model.py
\`\`\`

This will create the following files:
- `disease_model.pkl` - Trained Random Forest model
- `tfidf_vectorizer.pkl` - TF-IDF vectorizer for text processing
- `label_encoder.pkl` - Label encoder for disease categories
- `disease_remedies.pkl` - Mapping of diseases to remedies

### 4. Run the Application

\`\`\`bash
# From project root directory
python app.py
\`\`\`

The application will start at `http://localhost:5000`

## 📊 API Endpoints

### Patient Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/add_patient` | Add a new patient |
| GET | `/api/get_patient/<id>` | Get patient details |
| GET | `/api/get_all_patients` | Get all patients |
| PUT | `/api/update_patient/<id>` | Update patient details |
| DELETE | `/api/delete_patient/<id>` | Delete patient record |
| GET | `/api/patient_history/<id>` | Get patient history |

### Disease Prediction

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/predict_disease` | Predict disease from symptoms |
| POST | `/api/get_severity` | Calculate severity score |
| GET | `/api/patient_predictions/<id>` | Get patient predictions |

### Hospital Recommendations

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/recommend_hospital` | Get hospital recommendations |
| POST | `/api/recommend_free_hospitals` | Get free hospitals nearby |
| POST | `/api/filter_hospitals_by_cost` | Filter by cost category |
| GET | `/api/patient_recommendations/<id>` | Get patient recommendations |

### Hospital Directory

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/hospitals` | Add a hospital |
| GET | `/api/hospitals` | List hospitals with filters |
| GET | `/api/hospitals/location/<location>` | Search by city/state/pincode |
| GET | `/api/hospitals/<id>` | Get hospital details and doctors |
| GET | `/api/hospitals/<id>/doctors` | Get doctors in hospital |

### Doctor Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/doctors` | Add doctor |
| GET | `/api/doctors` | List doctors with filters |
| GET | `/api/doctors/<id>/slots` | Get available slots by date |

### Appointment Booking

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/appointments/book` | Book appointment |
| PUT | `/api/appointments/<id>/cancel` | Cancel appointment |
| GET | `/api/appointments/patient/<id>` | Appointment history |
| GET | `/api/appointments/patient/<id>/upcoming` | Upcoming appointments |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/api-docs` | API documentation |

## 📝 API Usage Examples

### Add a Patient

\`\`\`bash
curl -X POST http://localhost:5000/api/add_patient \\
  -H "Content-Type: application/json" \\
  -d '{
    "name": "John Doe",
    "age": 35,
    "gender": "Male",
    "contact": "9876543210",
    "location_city": "Delhi",
    "location_state": "Delhi",
    "location_pincode": "110001",
    "latitude": 28.6032,
    "longitude": 77.1824,
    "medical_history": "Diabetes, Hypertension",
    "current_medications": "Metformin, Lisinopril",
    "allergies": "Penicillin"
  }'
\`\`\`

### Predict Disease

\`\`\`bash
curl -X POST http://localhost:5000/api/predict_disease \\
  -H "Content-Type: application/json" \\
  -d '{
    "patient_id": 1,
    "symptoms": "fever, cough, sore_throat, body_ache, fatigue"
  }'
\`\`\`

### Find Hospitals

\`\`\`bash
curl -X POST http://localhost:5000/api/recommend_hospital \\
  -H "Content-Type: application/json" \\
  -d '{
    "patient_id": 1,
    "severity": "High",
    "top_n": 5
  }'
\`\`\`

## 🧠 ML Model Details

### Algorithm: Random Forest Classifier

**Configuration:**
- Number of trees: 100
- Max depth: 15
- Min samples split: 5
- Min samples leaf: 2

**Features:**
- TF-IDF vectorization of symptoms
- Text preprocessing (lowercase, stop words removal)

**Training Data:**
- 500 samples (50 per disease)
- 10 disease categories
- 20+ symptom features

**Accuracy:**
- Training accuracy: ~95%+
- Testing accuracy: ~90%+

### Supported Diseases

1. Flu
2. Cold
3. COVID-19
4. Bronchitis
5. Asthma
6. Gastroenteritis
7. Headache
8. Allergy
9. Dengue
10. Migraine

## 🏥 Hospital Database

The system includes 24 sample hospitals across 5 major Indian cities:
- Delhi
- Mumbai
- Bangalore
- Kolkata
- Hyderabad

Each hospital includes:
- Type: Government, Private, Charitable
- Cost category: Free, Low, Medium, High
- Location coordinates (latitude, longitude)
- Contact information
- Emergency availability

## 🔧 Configuration

### Modify Disease Categories

Edit `model/create_dataset.py` to add/modify diseases:

\`\`\`python
diseases_data = {
    'New Disease': {
        'common_symptoms': ['symptom1', 'symptom2'],
        'dos': 'do1|do2|do3',
        'donts': 'dont1|dont2|dont3',
        'severity': 'Medium'
    }
}
\`\`\`

### Add Hospital Data

Edit `database/create_hospital_data.py` to add hospitals:

\`\`\`python
hospitals_data = [
    {
        'hospital_name': 'Hospital Name',
        'city': 'City',
        'state': 'State',
        'type': 'government',  # or 'private', 'charitable'
        'cost_category': 'free',  # or 'low', 'medium', 'high'
        'latitude': 28.6032,
        'longitude': 77.1824,
        'contact': 'Phone number',
        'emergency': 'Yes'  # or 'No'
    }
]
\`\`\`

## 🌐 Browser Compatibility

- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

## 🔒 Security Considerations

- Input validation on all API endpoints
- Error handling without exposing sensitive information
- CORS enabled for cross-origin requests
- Database queries use parameterized statements

## 📱 Future Enhancements

- User authentication and authorization
- Email notifications for hospital recommendations
- Integration with Google Maps API
- Mobile app (React Native/Flutter)
- Advanced analytics dashboard
- Multi-language support
- Integration with real hospital databases
- Telemedicine features
- Payment gateway integration
- Real-time notifications

## 🐛 Troubleshooting

### Model Not Found Error

Make sure you've run the training scripts:
\`\`\`bash
cd model
python create_dataset.py
python train_model.py
\`\`\`

### Hospital Data Not Loading

Ensure hospital data is generated:
\`\`\`bash
cd database
python create_hospital_data.py
\`\`\`

### Port Already in Use

If port 5000 is busy, modify `app.py`:
\`\`\`python
app.run(debug=True, host='0.0.0.0', port=5001)  # Use different port
\`\`\`

### Missing Dependencies

Reinstall requirements:
\`\`\`bash
pip install --upgrade -r requirements.txt
\`\`\`

## 📚 Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Scikit-learn Documentation](https://scikit-learn.org/)
- [Machine Learning Basics](https://www.coursera.org/learn/machine-learning)

## 📄 License

This project is open source and available for educational purposes.

## 👥 Authors

Created for demonstration of ML-based healthcare solutions.

## 💡 Tips

1. **First Run**: Start by accessing the dashboard at `http://localhost:5000/dashboard`
2. **Add Test Data**: Manually add patients through the dashboard
3. **Test Predictions**: Use the symptom suggestions provided
4. **View Results**: Check prediction confidence and hospital recommendations
5. **API Testing**: Use Postman or cURL for API endpoint testing

## 🤝 Contributing

Suggestions and improvements are welcome!

## ❓ FAQ

**Q: Can I use real medical datasets?**
A: Yes, replace the synthetic dataset with real data, but ensure compliance with healthcare regulations (HIPAA, GDPR).

**Q: How do I improve model accuracy?**
A: Provide more training data, tune hyperparameters, or use advanced ML algorithms (Neural Networks, Gradient Boosting).

**Q: Can I deploy this to production?**
A: Yes, but ensure proper security measures, HTTPS, authentication, and compliance with regulations.

**Q: How do I add more hospitals?**
A: Edit `database/create_hospital_data.py` and re-run it to regenerate the hospital database.

---

**Version**: 1.0.0  
**Last Updated**: 2024
