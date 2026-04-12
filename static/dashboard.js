// Dashboard JavaScript
let patients = [];
const API_BASE = '/api';

document.addEventListener('DOMContentLoaded', function() {
    loadPatients();
    initializeEventListeners();
});

// Initialize event listeners
function initializeEventListeners() {
    document.getElementById('addPatientForm').addEventListener('submit', handleAddPatient);
    document.getElementById('predictForm').addEventListener('submit', handlePredict);
    document.getElementById('hospitalForm').addEventListener('submit', handleFindHospitals);
}

// Show specific section
function showSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.content-section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all menu items
    document.querySelectorAll('.sidebar-menu a').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionName + '-section').classList.add('active');
    
    // Add active class to clicked menu item
    event.target.closest('a').classList.add('active');
}

// Load all patients
async function loadPatients() {
    try {
        const response = await fetch(`${API_BASE}/get_all_patients`);
        const data = await response.json();
        
        if (data.status === 'success') {
            patients = data.patients;
            displayPatients(patients);
            populatePatientSelects();
        }
    } catch (error) {
        showAlert('Error loading patients: ' + error.message, 'error');
    }
}

// Populate patient select dropdowns
function populatePatientSelects() {
    const selects = ['predict_patient_id', 'hospital_patient_id', 'history_patient_id'];
    
    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        select.innerHTML = '<option value="">Select a patient...</option>';
        
        patients.forEach(patient => {
            const option = document.createElement('option');
            option.value = patient.id;
            option.textContent = `${patient.name} (ID: ${patient.id}) - ${patient.location_city}`;
            select.appendChild(option);
        });
    });
}

// Display patients
function displayPatients(patientList) {
    const container = document.getElementById('patientsList');
    
    if (patientList.length === 0) {
        container.innerHTML = '<p>No patients found. Add a new patient to get started.</p>';
        return;
    }
    
    container.innerHTML = patientList.map(patient => `
        <div class="patient-item">
            <div class="patient-info">
                <h4><i class="fas fa-user"></i> ${patient.name}</h4>
                <div class="patient-details">
                    <span><strong>ID:</strong> ${patient.id}</span>
                    <span><strong>Age:</strong> ${patient.age}</span>
                    <span><strong>Gender:</strong> ${patient.gender}</span>
                    <span><strong>Contact:</strong> ${patient.contact}</span>
                    <span><strong>Location:</strong> ${patient.location_city}, ${patient.location_state}</span>
                    <span><strong>Pincode:</strong> ${patient.location_pincode}</span>
                </div>
                ${patient.medical_history ? `<p><strong>Medical History:</strong> ${patient.medical_history}</p>` : ''}
                ${patient.allergies ? `<p><strong>Allergies:</strong> ${patient.allergies}</p>` : ''}
            </div>
            <div class="patient-actions">
                <button class="btn btn-primary" onclick="editPatient(${patient.id})">Edit</button>
                <button class="btn btn-danger" onclick="deletePatient(${patient.id})">Delete</button>
            </div>
        </div>
    `).join('');
}

// Handle add patient form submission
async function handleAddPatient(e) {
    e.preventDefault();
    
    const formData = {
        name: document.getElementById('name').value,
        age: parseInt(document.getElementById('age').value),
        gender: document.getElementById('gender').value,
        contact: document.getElementById('contact').value,
        location_city: document.getElementById('location_city').value,
        location_state: document.getElementById('location_state').value,
        location_pincode: document.getElementById('location_pincode').value,
        latitude: parseFloat(document.getElementById('latitude').value),
        longitude: parseFloat(document.getElementById('longitude').value),
        medical_history: document.getElementById('medical_history').value,
        current_medications: document.getElementById('current_medications').value,
        allergies: document.getElementById('allergies').value
    };
    
    try {
        const response = await fetch(`${API_BASE}/add_patient`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showAlert('Patient added successfully!', 'success');
            document.getElementById('addPatientForm').reset();
            loadPatients();
        } else {
            showAlert('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showAlert('Error adding patient: ' + error.message, 'error');
    }
}

// Delete patient
async function deletePatient(patientId) {
    if (!confirm('Are you sure you want to delete this patient?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/delete_patient/${patientId}`, {
            method: 'DELETE'
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            showAlert('Patient deleted successfully!', 'success');
            loadPatients();
        } else {
            showAlert('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showAlert('Error deleting patient: ' + error.message, 'error');
    }
}

// Handle predict disease form
async function handlePredict(e) {
    e.preventDefault();
    
    const patientId = document.getElementById('predict_patient_id').value;
    const symptoms = document.getElementById('symptoms').value;
    
    if (!patientId) {
        showAlert('Please select a patient', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/predict_disease`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                patient_id: patientId,
                symptoms: symptoms
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayPredictionResult(data);
        } else {
            showAlert('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showAlert('Error predicting disease: ' + error.message, 'error');
    }
}

// Display prediction result
function displayPredictionResult(data) {
    const result = document.getElementById('predictionResult');
    const content = document.getElementById('resultContent');
    
    const severity_color = data.severity === 'High' ? '#dc3545' : 
                          data.severity === 'Medium' ? '#ffc107' : '#28a745';
    
    const topPredictions = data.top_3_predictions.map((pred, index) => `
        <div style="display: grid; grid-template-columns: 20px 1fr; gap: 10px; margin-bottom: 8px;">
            <span>${index + 1}.</span>
            <span>
                <strong>${pred.disease}</strong> - 
                ${(pred.confidence * 100).toFixed(2)}% 
                (${pred.severity})
            </span>
        </div>
    `).join('');
    
    content.innerHTML = `
        <div class="prediction-card">
            <div class="prediction-header">
                <div class="prediction-stat">
                    <div class="label">Predicted Disease</div>
                    <div class="value" style="color: ${severity_color};">${data.predicted_disease}</div>
                </div>
                <div class="prediction-stat">
                    <div class="label">Confidence</div>
                    <div class="value">${data.confidence_percentage.toFixed(2)}%</div>
                </div>
                <div class="prediction-stat">
                    <div class="label">Severity</div>
                    <div class="value" style="color: ${severity_color};">${data.severity}</div>
                </div>
                <div class="prediction-stat">
                    <div class="label">Severity Score</div>
                    <div class="value">${data.severity_score}/100</div>
                </div>
            </div>
            
            <p><strong>Input Symptoms:</strong> ${data.symptoms}</p>
            
            <div class="dos-donts">
                <div class="dos-list">
                    <h4><i class="fas fa-check-circle"></i> Do's</h4>
                    <ul>
                        ${data.dos.map(item => `<li>${item.trim()}</li>`).join('')}
                    </ul>
                </div>
                <div class="donts-list">
                    <h4><i class="fas fa-times-circle"></i> Don'ts</h4>
                    <ul>
                        ${data.donts.map(item => `<li>${item.trim()}</li>`).join('')}
                    </ul>
                </div>
            </div>
            
            <div style="margin-top: 20px; padding: 15px; background: #f0f7ff; border-radius: 5px;">
                <strong>Top Predictions:</strong>
                ${topPredictions}
            </div>
            
            <div style="margin-top: 15px;">
                <button class="btn btn-primary" onclick="findHospitalsForPrediction('${data.severity}')">
                    Find Nearby Hospitals
                </button>
            </div>
        </div>
    `;
    
    result.style.display = 'block';
}

// Find hospitals for prediction
function findHospitalsForPrediction(severity) {
    document.getElementById('severity').value = severity;
    showSection('hospitals');
    setTimeout(() => {
        document.getElementById('hospital_patient_id').value = document.getElementById('predict_patient_id').value;
    }, 100);
}

// Handle find hospitals form
async function handleFindHospitals(e) {
    e.preventDefault();
    
    const patientId = document.getElementById('hospital_patient_id').value;
    const severity = document.getElementById('severity').value;
    const costFilter = document.getElementById('cost_filter').value;
    
    if (!patientId) {
        showAlert('Please select a patient', 'error');
        return;
    }
    
    try {
        let endpoint = `${API_BASE}/recommend_hospital`;
        let requestBody = {
            patient_id: patientId,
            severity: severity,
            top_n: 5
        };
        
        if (costFilter) {
            endpoint = `${API_BASE}/filter_hospitals_by_cost`;
            requestBody = {
                patient_id: patientId,
                cost_category: costFilter,
                top_n: 5
            };
        }
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestBody)
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            displayHospitalResults(data);
        } else {
            showAlert('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showAlert('Error finding hospitals: ' + error.message, 'error');
    }
}

// Display hospital results
function displayHospitalResults(data) {
    const result = document.getElementById('hospitalResult');
    const content = document.getElementById('hospitalContent');
    
    if (!data.recommendations || data.recommendations.length === 0) {
        content.innerHTML = '<p>No hospitals found matching your criteria.</p>';
        result.style.display = 'block';
        return;
    }
    
    const hospitalsHTML = data.recommendations.map(hospital => {
        const emergencyClass = hospital.emergency_available === 'Yes' ? 'emergency-yes' : 'emergency-no';
        return `
            <div class="hospital-card">
                <div class="hospital-rank">${hospital.rank}</div>
                <div class="hospital-name">${hospital.hospital_name}</div>
                <div class="hospital-info">
                    <span><strong>Type:</strong> ${hospital.type}</span>
                    <span><strong>Cost:</strong> ${hospital.cost_category}</span>
                    <span><strong>Distance:</strong> ${hospital.distance_km} km</span>
                    <span><strong>Location:</strong> ${hospital.city}, ${hospital.state}</span>
                    <span><strong>Contact:</strong> ${hospital.contact}</span>
                    <span><strong>Emergency:</strong> <span class="${emergencyClass}">${hospital.emergency_available}</span></span>
                </div>
                <div class="distance-badge">
                    <i class="fas fa-location-dot"></i> ${hospital.distance_km} km away
                </div>
            </div>
        `;
    }).join('');
    
    const summaryHTML = data.summary ? `
        <div style="background: #f0f7ff; padding: 15px; border-radius: 5px; margin-bottom: 20px;">
            <strong>Summary:</strong> 
            Government Hospitals: ${data.summary.government_hospitals} | 
            Charitable: ${data.summary.charitable_hospitals} | 
            Private: ${data.summary.private_hospitals}
        </div>
    ` : '';
    
    content.innerHTML = `
        ${summaryHTML}
        <div class="hospitals-grid">
            ${hospitalsHTML}
        </div>
    `;
    
    result.style.display = 'block';
}

// Load patient history
async function loadPatientHistory() {
    const patientId = document.getElementById('history_patient_id').value;
    
    if (!patientId) {
        showAlert('Please select a patient', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/patient_history/${patientId}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            displayPatientHistory(data);
        } else {
            showAlert('Error: ' + data.message, 'error');
        }
    } catch (error) {
        showAlert('Error loading history: ' + error.message, 'error');
    }
}

// Display patient history
function displayPatientHistory(data) {
    const result = document.getElementById('historyResult');
    const content = document.getElementById('historyContent');
    
    const predictionsHTML = data.predictions.map(pred => `
        <div style="padding: 15px; background: #f9f9f9; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #0066cc;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                <div>
                    <strong>Disease:</strong> ${pred.predicted_disease}
                </div>
                <div>
                    <strong>Confidence:</strong> ${(pred.confidence * 100).toFixed(2)}%
                </div>
                <div>
                    <strong>Severity:</strong> ${pred.severity}
                </div>
                <div>
                    <strong>Date:</strong> ${new Date(pred.predicted_at).toLocaleDateString()}
                </div>
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #666;">
                Symptoms: ${pred.symptoms}
            </p>
        </div>
    `).join('');
    
    content.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h4><i class="fas fa-history"></i> Prediction History (${data.total_predictions})</h4>
            ${data.total_predictions === 0 ? 
                '<p>No predictions yet.</p>' : 
                predictionsHTML
            }
        </div>
        <div>
            <h4><i class="fas fa-hospital"></i> Hospital Recommendations (${data.total_recommendations})</h4>
            ${data.total_recommendations === 0 ? 
                '<p>No hospital recommendations yet.</p>' : 
                '<p>Hospital recommendations are stored with each prediction.</p>'
            }
        </div>
    `;
    
    result.style.display = 'block';
}

// Show alert message
function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;
    
    container.appendChild(alert);
    
    setTimeout(() => {
        alert.remove();
    }, 4000);
}

// Sidebar menu click handler
document.addEventListener('load', function() {
    // Set first section as active
    document.getElementById('patients-section').classList.add('active');
    document.querySelector('.sidebar-menu a').classList.add('active');
});

// Initialize sidebar
window.addEventListener('load', function() {
    document.getElementById('patients-section').classList.add('active');
    if (document.querySelector('.sidebar-menu a')) {
        document.querySelector('.sidebar-menu a').classList.add('active');
    }
});
