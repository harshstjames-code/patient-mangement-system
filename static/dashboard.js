// Dashboard JavaScript
let patients = [];
let hospitals = [];
let doctors = [];
const API_BASE = '/api';


document.addEventListener('DOMContentLoaded', function () {
    setMinAppointmentDate();
    initializeEventListeners();
    loadPatients();
    loadHospitals();
    loadDoctors();
});


function initializeEventListeners() {
    document.getElementById('addPatientForm').addEventListener('submit', handleAddPatient);
    document.getElementById('predictForm').addEventListener('submit', handlePredict);
    document.getElementById('predictBtn').addEventListener('click', handlePredictButtonClick);
    document.getElementById('hospitalForm').addEventListener('submit', handleFindHospitals);

    document.getElementById('hospitalSearchForm').addEventListener('submit', handleHospitalSearch);
    document.getElementById('doctorFilterForm').addEventListener('submit', handleDoctorFilter);
    document.getElementById('appointmentForm').addEventListener('submit', handleBookAppointment);
    document.getElementById('addHospitalForm').addEventListener('submit', handleAddHospital);
    document.getElementById('addDoctorForm').addEventListener('submit', handleAddDoctor);

    document.getElementById('appointment_hospital_id').addEventListener('change', loadAppointmentDoctors);
    document.getElementById('appointment_date').addEventListener('change', loadAppointmentSlots);
    document.getElementById('appointment_doctor_id').addEventListener('change', loadAppointmentSlots);
    document.getElementById('appointment_city').addEventListener('blur', loadHospitalsForAppointmentFlow);
    document.getElementById('appointment_pincode').addEventListener('blur', loadHospitalsForAppointmentFlow);
    document.getElementById('appointment_specialization').addEventListener('blur', loadAppointmentDoctors);
}


function handlePredictButtonClick() {
    // Log each button click so repeated prediction triggers are easy to verify in browser console.
    console.log('Predict button clicked');
}


function buildPredictionPayload() {
    const patientId = document.getElementById('predict_patient_id').value;
    const symptomsText = document.getElementById('symptoms').value.trim();

    // Build a fresh payload on every call so stale values are never reused.
    const payload = {
        patient_id: patientId,
        symptoms: symptomsText
    };

    // Optional checkbox mode support if these inputs exist in future UI updates.
    const checkboxIds = ['fever', 'cough', 'headache', 'fatigue', 'nausea'];
    const hasCheckboxMode = checkboxIds.every(id => document.getElementById(id));

    if (hasCheckboxMode) {
        const symptomsDict = {
            fever: Number(document.getElementById('fever').checked),
            cough: Number(document.getElementById('cough').checked),
            headache: Number(document.getElementById('headache').checked),
            fatigue: Number(document.getElementById('fatigue').checked),
            nausea: Number(document.getElementById('nausea').checked)
        };

        const selectedSymptoms = Object.keys(symptomsDict).filter(key => symptomsDict[key] === 1);
        payload.symptoms_dict = symptomsDict;
        payload.symptoms = selectedSymptoms.join(', ');
    }

    return payload;
}


function setMinAppointmentDate() {
    const dateInput = document.getElementById('appointment_date');
    const today = new Date();
    const month = String(today.getMonth() + 1).padStart(2, '0');
    const day = String(today.getDate()).padStart(2, '0');
    dateInput.min = `${today.getFullYear()}-${month}-${day}`;
}


function showSection(sectionName) {
    document.querySelectorAll('.content-section').forEach(section => section.classList.remove('active'));
    document.querySelectorAll('.sidebar-menu a').forEach(link => link.classList.remove('active'));

    const section = document.getElementById(`${sectionName}-section`);
    if (section) {
        section.classList.add('active');
    }

    const link = document.querySelector(`.sidebar-menu a[href="#${sectionName}"]`);
    if (link) {
        link.classList.add('active');
    }

    if (sectionName === 'appointments') {
        loadHospitalsForAppointmentFlow();
    }
}


async function loadPatients() {
    try {
        const response = await fetch(`${API_BASE}/get_all_patients`);
        const data = await response.json();

        if (data.status === 'success') {
            patients = data.patients || [];
            displayPatients(patients);
            populatePatientSelects();
        }
    } catch (error) {
        showAlert(`Error loading patients: ${error.message}`, 'error');
    }
}


function populatePatientSelects() {
    const selects = [
        'predict_patient_id',
        'hospital_patient_id',
        'history_patient_id',
        'appointment_patient_id',
        'appointment_history_patient_id'
    ];

    selects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (!select) {
            return;
        }

        select.innerHTML = '<option value="">Select a patient...</option>';
        patients.forEach(patient => {
            const option = document.createElement('option');
            option.value = patient.id;
            option.textContent = `${patient.name} (ID: ${patient.id}) - ${patient.location_city}`;
            select.appendChild(option);
        });
    });
}


function displayPatients(patientList) {
    const container = document.getElementById('patientsList');
    if (!container) {
        return;
    }

    if (!patientList.length) {
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
                <button class="btn btn-danger" onclick="deletePatient(${patient.id})">Delete</button>
            </div>
        </div>
    `).join('');
}


async function handleAddPatient(e) {
    e.preventDefault();

    const formData = {
        name: document.getElementById('name').value,
        age: parseInt(document.getElementById('age').value, 10),
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
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        });

        const data = await response.json();
        if (data.status === 'success') {
            showAlert('Patient added successfully!', 'success');
            document.getElementById('addPatientForm').reset();
            loadPatients();
        } else {
            showAlert(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error adding patient: ${error.message}`, 'error');
    }
}


async function deletePatient(patientId) {
    if (!confirm('Are you sure you want to delete this patient?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/delete_patient/${patientId}`, { method: 'DELETE' });
        const data = await response.json();

        if (data.status === 'success') {
            showAlert('Patient deleted successfully!', 'success');
            loadPatients();
        } else {
            showAlert(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error deleting patient: ${error.message}`, 'error');
    }
}


async function handlePredict(e) {
    e.preventDefault();

    const payload = buildPredictionPayload();
    const patientId = payload.patient_id;

    if (!patientId) {
        showAlert('Please select a patient', 'error');
        return;
    }

    if (!payload.symptoms) {
        showAlert('Please enter at least one symptom', 'error');
        return;
    }

    console.log('Prediction running with symptoms:', payload);

    // Clear previous output while new prediction is in progress.
    const content = document.getElementById('resultContent');
    content.innerHTML = '<p>Running prediction...</p>';
    document.getElementById('predictionResult').style.display = 'block';

    try {
        const response = await fetch(`${API_BASE}/predict_disease?t=${Date.now()}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            cache: 'no-store',
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (data.status === 'success') {
            console.log('Prediction completed:', data);
            displayPredictionResult(data);
        } else {
            showAlert(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error predicting disease: ${error.message}`, 'error');
    }
}


function displayPredictionResult(data) {
    const result = document.getElementById('predictionResult');
    const content = document.getElementById('resultContent');

    const severityColor = data.severity === 'High' ? '#dc3545' : data.severity === 'Medium' ? '#ffc107' : '#28a745';

    const topPredictions = (data.top_3_predictions || []).map((pred, index) => `
        <div style="display: grid; grid-template-columns: 20px 1fr; gap: 10px; margin-bottom: 8px;">
            <span>${index + 1}.</span>
            <span><strong>${pred.disease}</strong> - ${(pred.confidence * 100).toFixed(2)}% (${pred.severity})</span>
        </div>
    `).join('');

    content.innerHTML = `
        <div class="prediction-card">
            <div class="prediction-header">
                <div class="prediction-stat">
                    <div class="label">Predicted Disease</div>
                    <div class="value" style="color: ${severityColor};">${data.predicted_disease}</div>
                </div>
                <div class="prediction-stat">
                    <div class="label">Confidence</div>
                    <div class="value">${data.confidence_percentage.toFixed(2)}%</div>
                </div>
                <div class="prediction-stat">
                    <div class="label">Severity</div>
                    <div class="value" style="color: ${severityColor};">${data.severity}</div>
                </div>
                <div class="prediction-stat">
                    <div class="label">Severity Score</div>
                    <div class="value">${data.severity_score}/100</div>
                </div>
            </div>

            <p><strong>Input Symptoms:</strong> ${data.symptoms || 'N/A'}</p>
            <p><strong>Last Updated:</strong> ${new Date().toLocaleTimeString()}</p>
            <div class="dos-donts">
                <div class="dos-list">
                    <h4><i class="fas fa-check-circle"></i> Do's</h4>
                    <ul>${data.dos.map(item => `<li>${item.trim()}</li>`).join('')}</ul>
                </div>
                <div class="donts-list">
                    <h4><i class="fas fa-times-circle"></i> Don'ts</h4>
                    <ul>${data.donts.map(item => `<li>${item.trim()}</li>`).join('')}</ul>
                </div>
            </div>
            <div style="margin-top: 20px; padding: 15px; background: #f0f7ff; border-radius: 5px;">
                <strong>Top Predictions:</strong>${topPredictions}
            </div>
            <div style="margin-top: 15px;">
                <button class="btn btn-primary" onclick="findHospitalsForPrediction('${data.severity}')">Find Nearby Hospitals</button>
            </div>
        </div>
    `;

    result.style.display = 'block';
}


function findHospitalsForPrediction(severity) {
    document.getElementById('severity').value = severity;
    showSection('hospitals');
    setTimeout(() => {
        document.getElementById('hospital_patient_id').value = document.getElementById('predict_patient_id').value;
    }, 100);
}


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
        let requestBody = { patient_id: patientId, severity, top_n: 5 };

        if (costFilter) {
            endpoint = `${API_BASE}/filter_hospitals_by_cost`;
            requestBody = { patient_id: patientId, cost_category: costFilter, top_n: 5 };
        }

        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestBody)
        });

        const data = await response.json();
        if (data.status === 'success') {
            displayHospitalResults(data);
        } else {
            showAlert(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error finding hospitals: ${error.message}`, 'error');
    }
}


function displayHospitalResults(data) {
    const result = document.getElementById('hospitalResult');
    const content = document.getElementById('hospitalContent');

    if (!data.recommendations || !data.recommendations.length) {
        content.innerHTML = '<p>No hospitals found matching your criteria.</p>';
        result.style.display = 'block';
        return;
    }

    const hospitalsHtml = data.recommendations.map(hospital => {
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
            </div>
        `;
    }).join('');

    content.innerHTML = `<div class="hospitals-grid">${hospitalsHtml}</div>`;
    result.style.display = 'block';
}


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
            showAlert(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error loading history: ${error.message}`, 'error');
    }
}


function displayPatientHistory(data) {
    const result = document.getElementById('historyResult');
    const content = document.getElementById('historyContent');

    const predictionsHtml = (data.predictions || []).map(pred => `
        <div style="padding: 15px; background: #f9f9f9; border-radius: 5px; margin-bottom: 10px; border-left: 4px solid #0066cc;">
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px;">
                <div><strong>Disease:</strong> ${pred.predicted_disease}</div>
                <div><strong>Confidence:</strong> ${(pred.confidence * 100).toFixed(2)}%</div>
                <div><strong>Severity:</strong> ${pred.severity}</div>
                <div><strong>Date:</strong> ${new Date(pred.predicted_at).toLocaleDateString()}</div>
            </div>
            <p style="margin-top: 8px; font-size: 12px; color: #666;">Symptoms: ${pred.symptoms}</p>
        </div>
    `).join('');

    content.innerHTML = `
        <div style="margin-bottom: 20px;">
            <h4><i class="fas fa-history"></i> Prediction History (${data.total_predictions})</h4>
            ${data.total_predictions === 0 ? '<p>No predictions yet.</p>' : predictionsHtml}
        </div>
    `;

    result.style.display = 'block';
}


async function loadHospitals(city = '', state = '', pincode = '') {
    try {
        const params = new URLSearchParams();
        if (city) {
            params.append('city', city);
        }
        if (state) {
            params.append('state', state);
        }
        if (pincode) {
            params.append('pincode', pincode);
        }

        const endpoint = `${API_BASE}/hospitals${params.toString() ? `?${params.toString()}` : ''}`;
        const response = await fetch(endpoint);
        const data = await response.json();

        if (data.status !== 'success') {
            showAlert(`Error loading hospitals: ${data.message}`, 'error');
            return;
        }

        hospitals = data.hospitals || [];
        displayHospitalDirectory(hospitals);
        populateHospitalSelects();
    } catch (error) {
        showAlert(`Error loading hospitals: ${error.message}`, 'error');
    }
}


async function handleHospitalSearch(e) {
    e.preventDefault();
    const city = document.getElementById('search_city').value.trim();
    const state = document.getElementById('search_state').value.trim();
    const pincode = document.getElementById('search_pincode').value.trim();
    await loadHospitals(city, state, pincode);
}


function displayHospitalDirectory(hospitalList) {
    const container = document.getElementById('hospitalDirectoryList');
    if (!container) {
        return;
    }

    if (!hospitalList.length) {
        container.innerHTML = '<p>No hospitals found for the selected filters.</p>';
        return;
    }

    container.innerHTML = hospitalList.map(hospital => `
        <div class="hospital-card">
            <div class="hospital-name">${hospital.hospital_name}</div>
            <div class="hospital-info">
                <span><strong>Address:</strong> ${hospital.address}</span>
                <span><strong>Location:</strong> ${hospital.city}, ${hospital.state} - ${hospital.pincode}</span>
                <span><strong>Contact:</strong> ${hospital.contact_number}</span>
                <span><strong>Email:</strong> ${hospital.email || 'N/A'}</span>
                <span><strong>Departments:</strong> ${hospital.departments || 'N/A'}</span>
            </div>
            <div style="margin-top: 10px;">
                <button class="btn btn-primary" onclick="openDoctorsForHospital(${hospital.hospital_id})">View Doctors</button>
            </div>
        </div>
    `).join('');
}


function populateHospitalSelects() {
    const hospitalSelects = ['doctor_hospital_filter', 'appointment_hospital_id', 'doctor_hospital_id'];

    hospitalSelects.forEach(selectId => {
        const select = document.getElementById(selectId);
        if (!select) {
            return;
        }

        const defaultOption = selectId === 'doctor_hospital_filter'
            ? '<option value="">All hospitals</option>'
            : '<option value="">Select hospital...</option>';

        select.innerHTML = defaultOption;
        hospitals.forEach(hospital => {
            const option = document.createElement('option');
            option.value = hospital.hospital_id;
            option.textContent = `${hospital.hospital_name} (${hospital.city})`;
            select.appendChild(option);
        });
    });
}


async function handleAddHospital(e) {
    e.preventDefault();

    const payload = {
        hospital_name: document.getElementById('hospital_name').value.trim(),
        address: document.getElementById('hospital_address').value.trim(),
        city: document.getElementById('hospital_city').value.trim(),
        state: document.getElementById('hospital_state').value.trim(),
        pincode: document.getElementById('hospital_pincode').value.trim(),
        contact_number: document.getElementById('hospital_contact').value.trim(),
        email: document.getElementById('hospital_email').value.trim(),
        departments: document.getElementById('hospital_departments').value.trim()
    };

    try {
        const response = await fetch(`${API_BASE}/hospitals`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (data.status === 'success') {
            showAlert('Hospital added successfully', 'success');
            document.getElementById('addHospitalForm').reset();
            await loadHospitals();
        } else {
            showAlert(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error adding hospital: ${error.message}`, 'error');
    }
}


async function handleAddDoctor(e) {
    e.preventDefault();

    const payload = {
        doctor_name: document.getElementById('doctor_name').value.trim(),
        specialization: document.getElementById('doctor_specialization').value.trim(),
        experience: parseInt(document.getElementById('doctor_experience').value, 10),
        hospital_id: parseInt(document.getElementById('doctor_hospital_id').value, 10),
        available_days: document.getElementById('doctor_available_days').value.trim(),
        available_time_slots: document.getElementById('doctor_available_slots').value.trim(),
        consultation_fee: parseFloat(document.getElementById('doctor_fee').value)
    };

    if (!payload.hospital_id) {
        showAlert('Please select a hospital for doctor assignment.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/doctors`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        const data = await response.json();

        if (data.status === 'success') {
            showAlert('Doctor added successfully', 'success');
            document.getElementById('addDoctorForm').reset();
            await loadDoctors();
        } else {
            showAlert(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error adding doctor: ${error.message}`, 'error');
    }
}


async function loadDoctors(hospitalId = '', specialization = '') {
    try {
        const params = new URLSearchParams();
        if (hospitalId) {
            params.append('hospital_id', hospitalId);
        }
        if (specialization) {
            params.append('specialization', specialization);
        }

        const endpoint = `${API_BASE}/doctors${params.toString() ? `?${params.toString()}` : ''}`;
        const response = await fetch(endpoint);
        const data = await response.json();

        if (data.status !== 'success') {
            showAlert(`Error loading doctors: ${data.message}`, 'error');
            return;
        }

        doctors = data.doctors || [];
        displayDoctorDirectory(doctors);
    } catch (error) {
        showAlert(`Error loading doctors: ${error.message}`, 'error');
    }
}


async function handleDoctorFilter(e) {
    e.preventDefault();
    const hospitalId = document.getElementById('doctor_hospital_filter').value;
    const specialization = document.getElementById('doctor_specialization_filter').value.trim();
    await loadDoctors(hospitalId, specialization);
}


function displayDoctorDirectory(doctorList) {
    const container = document.getElementById('doctorDirectoryList');
    if (!container) {
        return;
    }

    if (!doctorList.length) {
        container.innerHTML = '<p>No doctors found for selected filters.</p>';
        return;
    }

    container.innerHTML = doctorList.map(doctor => `
        <div class="patient-item">
            <div class="patient-info">
                <h4><i class="fas fa-user-doctor"></i> ${doctor.doctor_name}</h4>
                <div class="patient-details">
                    <span><strong>Specialization:</strong> ${doctor.specialization}</span>
                    <span><strong>Experience:</strong> ${doctor.experience} years</span>
                    <span><strong>Hospital:</strong> ${doctor.hospital_name}</span>
                    <span><strong>Fee:</strong> Rs ${doctor.consultation_fee}</span>
                    <span><strong>Days:</strong> ${doctor.available_days || 'N/A'}</span>
                    <span><strong>Slots:</strong> ${doctor.available_time_slots || 'N/A'}</span>
                </div>
            </div>
            <div class="patient-actions">
                <button class="btn btn-primary" onclick="startBookingForDoctor(${doctor.hospital_id}, ${doctor.doctor_id})">Book Appointment</button>
            </div>
        </div>
    `).join('');
}


function openDoctorsForHospital(hospitalId) {
    showSection('doctor-directory');
    document.getElementById('doctor_hospital_filter').value = String(hospitalId);
    loadDoctors(hospitalId, document.getElementById('doctor_specialization_filter').value.trim());
}


function startBookingForDoctor(hospitalId, doctorId) {
    showSection('appointments');
    document.getElementById('appointment_hospital_id').value = String(hospitalId);
    loadAppointmentDoctors().then(() => {
        document.getElementById('appointment_doctor_id').value = String(doctorId);
        loadAppointmentSlots();
    });
}


async function loadHospitalsForAppointmentFlow() {
    const city = document.getElementById('appointment_city').value.trim();
    const pincode = document.getElementById('appointment_pincode').value.trim();
    await loadHospitals(city, '', pincode);
}


async function loadAppointmentDoctors() {
    const hospitalId = document.getElementById('appointment_hospital_id').value;
    const specialization = document.getElementById('appointment_specialization').value.trim();
    const doctorSelect = document.getElementById('appointment_doctor_id');

    doctorSelect.innerHTML = '<option value="">Select doctor...</option>';
    document.getElementById('appointment_time').innerHTML = '<option value="">Select slot...</option>';

    if (!hospitalId) {
        return;
    }

    try {
        const params = new URLSearchParams();
        if (specialization) {
            params.append('specialization', specialization);
        }

        const endpoint = `${API_BASE}/hospitals/${hospitalId}/doctors${params.toString() ? `?${params.toString()}` : ''}`;
        const response = await fetch(endpoint);
        const data = await response.json();

        if (data.status !== 'success') {
            showAlert(`Error loading doctors: ${data.message}`, 'error');
            return;
        }

        (data.doctors || []).forEach(doctor => {
            const option = document.createElement('option');
            option.value = doctor.doctor_id;
            option.textContent = `${doctor.doctor_name} - ${doctor.specialization} (${doctor.experience} yrs)`;
            doctorSelect.appendChild(option);
        });
    } catch (error) {
        showAlert(`Error loading hospital doctors: ${error.message}`, 'error');
    }
}


async function loadAppointmentSlots() {
    const doctorId = document.getElementById('appointment_doctor_id').value;
    const date = document.getElementById('appointment_date').value;
    const slotSelect = document.getElementById('appointment_time');

    slotSelect.innerHTML = '<option value="">Select slot...</option>';

    if (!doctorId || !date) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/doctors/${doctorId}/slots?appointment_date=${date}`);
        const data = await response.json();

        if (data.status !== 'success') {
            showAlert(`Error loading slots: ${data.message}`, 'error');
            return;
        }

        if (!data.available_slots.length) {
            slotSelect.innerHTML = '<option value="">No slots available</option>';
            return;
        }

        data.available_slots.forEach(slot => {
            const option = document.createElement('option');
            option.value = slot;
            option.textContent = slot;
            slotSelect.appendChild(option);
        });
    } catch (error) {
        showAlert(`Error loading available slots: ${error.message}`, 'error');
    }
}


async function handleBookAppointment(e) {
    e.preventDefault();

    const payload = {
        patient_id: parseInt(document.getElementById('appointment_patient_id').value, 10),
        hospital_id: parseInt(document.getElementById('appointment_hospital_id').value, 10),
        doctor_id: parseInt(document.getElementById('appointment_doctor_id').value, 10),
        appointment_date: document.getElementById('appointment_date').value,
        appointment_time: document.getElementById('appointment_time').value
    };

    if (!payload.patient_id || !payload.hospital_id || !payload.doctor_id || !payload.appointment_date || !payload.appointment_time) {
        showAlert('Please complete all required appointment fields.', 'error');
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/appointments/book`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await response.json();
        if (data.status === 'success') {
            showAlert(`Appointment booked! ID: ${data.appointment_id}`, 'success');
            document.getElementById('appointment_time').innerHTML = '<option value="">Select slot...</option>';
            loadAppointmentSlots();
        } else {
            showAlert(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error booking appointment: ${error.message}`, 'error');
    }
}


async function loadAppointmentHistory() {
    const patientId = document.getElementById('appointment_history_patient_id').value;
    if (!patientId) {
        showAlert('Please select a patient', 'error');
        return;
    }

    try {
        const [historyResponse, upcomingResponse] = await Promise.all([
            fetch(`${API_BASE}/appointments/patient/${patientId}`),
            fetch(`${API_BASE}/appointments/patient/${patientId}/upcoming`)
        ]);

        const historyData = await historyResponse.json();
        const upcomingData = await upcomingResponse.json();

        if (historyData.status === 'success') {
            renderAppointmentHistory(historyData.appointments || []);
        } else {
            showAlert(`Error: ${historyData.message}`, 'error');
        }

        if (upcomingData.status === 'success') {
            renderUpcomingAppointments(upcomingData.appointments || []);
        } else {
            showAlert(`Error: ${upcomingData.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error loading appointment history: ${error.message}`, 'error');
    }
}


function renderUpcomingAppointments(appointments) {
    const container = document.getElementById('upcomingAppointmentsContent');
    if (!appointments.length) {
        container.innerHTML = '<p>No upcoming appointments.</p>';
        return;
    }

    container.innerHTML = appointments.map(appt => `
        <div class="patient-item">
            <div class="patient-info">
                <h4>${appt.appointment_date} at ${appt.appointment_time}</h4>
                <div class="patient-details">
                    <span><strong>Doctor:</strong> ${appt.doctor_name} (${appt.specialization})</span>
                    <span><strong>Hospital:</strong> ${appt.hospital_name}</span>
                    <span><strong>Location:</strong> ${appt.hospital_city}, ${appt.hospital_state}</span>
                    <span><strong>Status:</strong> ${appt.appointment_status}</span>
                </div>
            </div>
            <div class="patient-actions">
                <button class="btn btn-danger" onclick="cancelAppointment(${appt.appointment_id})">Cancel</button>
            </div>
        </div>
    `).join('');
}


function renderAppointmentHistory(appointments) {
    const container = document.getElementById('appointmentHistoryContent');
    if (!appointments.length) {
        container.innerHTML = '<p>No appointment history found.</p>';
        return;
    }

    container.innerHTML = appointments.map(appt => `
        <div class="patient-item">
            <div class="patient-info">
                <h4>${appt.appointment_date} at ${appt.appointment_time}</h4>
                <div class="patient-details">
                    <span><strong>Doctor:</strong> ${appt.doctor_name} (${appt.specialization})</span>
                    <span><strong>Hospital:</strong> ${appt.hospital_name}</span>
                    <span><strong>Hospital Contact:</strong> ${appt.hospital_contact}</span>
                    <span><strong>Status:</strong> ${appt.appointment_status}</span>
                </div>
            </div>
        </div>
    `).join('');
}


async function cancelAppointment(appointmentId) {
    if (!confirm('Cancel this appointment?')) {
        return;
    }

    try {
        const response = await fetch(`${API_BASE}/appointments/${appointmentId}/cancel`, {
            method: 'PUT'
        });
        const data = await response.json();

        if (data.status === 'success') {
            showAlert('Appointment cancelled successfully', 'success');
            loadAppointmentHistory();
            loadAppointmentSlots();
        } else {
            showAlert(`Error: ${data.message}`, 'error');
        }
    } catch (error) {
        showAlert(`Error cancelling appointment: ${error.message}`, 'error');
    }
}


function showAlert(message, type = 'info') {
    const container = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type}`;
    alert.textContent = message;

    container.appendChild(alert);
    setTimeout(() => alert.remove(), 4000);
}


window.showSection = showSection;
window.loadPatientHistory = loadPatientHistory;
window.loadAppointmentHistory = loadAppointmentHistory;
window.cancelAppointment = cancelAppointment;
window.deletePatient = deletePatient;
window.findHospitalsForPrediction = findHospitalsForPrediction;
window.openDoctorsForHospital = openDoctorsForHospital;
window.startBookingForDoctor = startBookingForDoctor;
