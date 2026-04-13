"""
Create sample hospitals and doctors for appointment booking module.
Run: python database/create_appointment_data.py
"""
from database.db import PatientDatabase


def seed_hospitals_and_doctors():
    db = PatientDatabase()

    hospitals = [
        {
            'hospital_name': 'City Heart Institute',
            'address': '12 Ring Road, Central Zone',
            'city': 'Delhi',
            'state': 'Delhi',
            'pincode': '110001',
            'contact_number': '01140001111',
            'email': 'info@cityheart.in',
            'departments': 'Cardiology,Neurology,Orthopedic,General Medicine'
        },
        {
            'hospital_name': 'Sunrise Multispeciality',
            'address': '44 MG Road, North Block',
            'city': 'Bengaluru',
            'state': 'Karnataka',
            'pincode': '560001',
            'contact_number': '08041002222',
            'email': 'help@sunrisecare.in',
            'departments': 'Dermatology,Orthopedic,Pediatrics,General Medicine'
        },
        {
            'hospital_name': 'Riverfront Medical Center',
            'address': '88 Lake View Street',
            'city': 'Mumbai',
            'state': 'Maharashtra',
            'pincode': '400001',
            'contact_number': '02242003333',
            'email': 'support@riverfrontmed.in',
            'departments': 'Cardiology,ENT,Neurology,General Surgery'
        }
    ]

    hospital_ids = {}
    existing = db.get_hospitals()
    existing_lookup = {h['hospital_name'].lower(): h['hospital_id'] for h in existing}

    for hospital in hospitals:
        name_key = hospital['hospital_name'].lower()
        if name_key in existing_lookup:
            hospital_ids[hospital['hospital_name']] = existing_lookup[name_key]
            continue

        hospital_id = db.add_hospital(**hospital)
        if hospital_id:
            hospital_ids[hospital['hospital_name']] = hospital_id
            print(f"Added hospital: {hospital['hospital_name']} (ID: {hospital_id})")

    doctors = [
        {
            'doctor_name': 'Dr. Meera Sharma',
            'specialization': 'Cardiology',
            'experience': 11,
            'hospital_name': 'City Heart Institute',
            'available_days': 'Monday,Tuesday,Thursday,Friday',
            'available_time_slots': '09:00,10:00,11:00,16:00,17:00',
            'consultation_fee': 900
        },
        {
            'doctor_name': 'Dr. Ajay Verma',
            'specialization': 'Neurology',
            'experience': 8,
            'hospital_name': 'City Heart Institute',
            'available_days': 'Monday,Wednesday,Saturday',
            'available_time_slots': '10:30,11:30,14:00,15:00',
            'consultation_fee': 1100
        },
        {
            'doctor_name': 'Dr. Kavya Nair',
            'specialization': 'Orthopedic',
            'experience': 7,
            'hospital_name': 'Sunrise Multispeciality',
            'available_days': 'Tuesday,Wednesday,Friday',
            'available_time_slots': '09:30,10:30,12:00,18:00',
            'consultation_fee': 800
        },
        {
            'doctor_name': 'Dr. Rohan Deshpande',
            'specialization': 'General Medicine',
            'experience': 6,
            'hospital_name': 'Riverfront Medical Center',
            'available_days': 'Monday,Tuesday,Wednesday,Thursday,Friday',
            'available_time_slots': '08:30,09:30,10:30,17:30',
            'consultation_fee': 600
        }
    ]

    existing_doctors = db.get_doctors()
    existing_doctor_names = {d['doctor_name'].lower() for d in existing_doctors}

    for doctor in doctors:
        if doctor['doctor_name'].lower() in existing_doctor_names:
            continue

        hospital_id = hospital_ids.get(doctor['hospital_name'])
        if not hospital_id:
            continue

        doctor_id = db.add_doctor(
            doctor_name=doctor['doctor_name'],
            specialization=doctor['specialization'],
            experience=doctor['experience'],
            hospital_id=hospital_id,
            available_days=doctor['available_days'],
            available_time_slots=doctor['available_time_slots'],
            consultation_fee=doctor['consultation_fee']
        )
        if doctor_id:
            print(f"Added doctor: {doctor['doctor_name']} (ID: {doctor_id})")

    print('Sample hospitals and doctors are ready.')


if __name__ == '__main__':
    seed_hospitals_and_doctors()
