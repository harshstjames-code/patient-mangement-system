"""
Script to generate hospital database with location-based information
"""
import pandas as pd

# Hospital data with latitude, longitude (sample Indian cities)
hospitals_data = [
    # Delhi
    {'hospital_name': 'Apollo Hospital Delhi', 'city': 'Delhi', 'state': 'Delhi', 'type': 'private', 'cost_category': 'high', 'latitude': 28.5355, 'longitude': 77.1234, 'contact': '011-4910-5000', 'emergency': 'Yes'},
    {'hospital_name': 'Government Hospital Delhi', 'city': 'Delhi', 'state': 'Delhi', 'type': 'government', 'cost_category': 'free', 'latitude': 28.5921, 'longitude': 77.1891, 'contact': '011-2334-5678', 'emergency': 'Yes'},
    {'hospital_name': 'Charitable Clinic Delhi', 'city': 'Delhi', 'state': 'Delhi', 'type': 'charitable', 'cost_category': 'low', 'latitude': 28.6032, 'longitude': 77.1824, 'contact': '011-2345-6789', 'emergency': 'Yes'},
    {'hospital_name': 'Max Healthcare Delhi', 'city': 'Delhi', 'state': 'Delhi', 'type': 'private', 'cost_category': 'high', 'latitude': 28.4595, 'longitude': 77.1230, 'contact': '011-4015-9000', 'emergency': 'Yes'},
    {'hospital_name': 'Primary Health Center Delhi', 'city': 'Delhi', 'state': 'Delhi', 'type': 'government', 'cost_category': 'free', 'latitude': 28.7041, 'longitude': 77.2753, 'contact': '011-2567-8901', 'emergency': 'No'},
    
    # Mumbai
    {'hospital_name': 'Tata Memorial Hospital Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'type': 'government', 'cost_category': 'low', 'latitude': 19.0176, 'longitude': 72.8298, 'contact': '022-2417-7000', 'emergency': 'Yes'},
    {'hospital_name': 'Apollo Hospital Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'type': 'private', 'cost_category': 'high', 'latitude': 19.0896, 'longitude': 72.8656, 'contact': '022-2828-1000', 'emergency': 'Yes'},
    {'hospital_name': 'Fortis Hospital Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'type': 'private', 'cost_category': 'high', 'latitude': 19.1136, 'longitude': 72.8696, 'contact': '022-6876-6000', 'emergency': 'Yes'},
    {'hospital_name': 'Municipal Hospital Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'type': 'government', 'cost_category': 'free', 'latitude': 19.0176, 'longitude': 72.8476, 'contact': '022-2262-1234', 'emergency': 'Yes'},
    {'hospital_name': 'BMC Health Center Mumbai', 'city': 'Mumbai', 'state': 'Maharashtra', 'type': 'government', 'cost_category': 'free', 'latitude': 19.0760, 'longitude': 72.8777, 'contact': '022-2181-1111', 'emergency': 'No'},
    
    # Bangalore
    {'hospital_name': 'Apollo Hospital Bangalore', 'city': 'Bangalore', 'state': 'Karnataka', 'type': 'private', 'cost_category': 'high', 'latitude': 13.0827, 'longitude': 80.2707, 'contact': '080-4040-4040', 'emergency': 'Yes'},
    {'hospital_name': 'Government Medical College Bangalore', 'city': 'Bangalore', 'state': 'Karnataka', 'type': 'government', 'cost_category': 'free', 'latitude': 13.0047, 'longitude': 80.2394, 'contact': '080-2260-2060', 'emergency': 'Yes'},
    {'hospital_name': 'Manipal Hospital Bangalore', 'city': 'Bangalore', 'state': 'Karnataka', 'type': 'private', 'cost_category': 'high', 'latitude': 13.1939, 'longitude': 77.6245, 'contact': '080-6969-6969', 'emergency': 'Yes'},
    {'hospital_name': 'St. Martha Hospital Bangalore', 'city': 'Bangalore', 'state': 'Karnataka', 'type': 'charitable', 'cost_category': 'low', 'latitude': 13.1939, 'longitude': 77.5700, 'contact': '080-2555-8888', 'emergency': 'Yes'},
    {'hospital_name': 'Bangalore Health Center', 'city': 'Bangalore', 'state': 'Karnataka', 'type': 'government', 'cost_category': 'free', 'latitude': 13.1939, 'longitude': 77.6245, 'contact': '080-2341-2341', 'emergency': 'No'},
    
    # Kolkata
    {'hospital_name': 'SSKM Hospital Kolkata', 'city': 'Kolkata', 'state': 'West Bengal', 'type': 'government', 'cost_category': 'free', 'latitude': 22.5726, 'longitude': 88.3787, 'contact': '033-2356-0556', 'emergency': 'Yes'},
    {'hospital_name': 'Apollo Hospital Kolkata', 'city': 'Kolkata', 'state': 'West Bengal', 'type': 'private', 'cost_category': 'high', 'latitude': 22.5090, 'longitude': 88.3857, 'contact': '033-3066-3737', 'emergency': 'Yes'},
    {'hospital_name': 'Woodlands Hospital Kolkata', 'city': 'Kolkata', 'state': 'West Bengal', 'type': 'private', 'cost_category': 'high', 'latitude': 22.5487, 'longitude': 88.3570, 'contact': '033-4450-9999', 'emergency': 'Yes'},
    {'hospital_name': 'Mother Charity Hospital Kolkata', 'city': 'Kolkata', 'state': 'West Bengal', 'type': 'charitable', 'cost_category': 'low', 'latitude': 22.5567, 'longitude': 88.3651, 'contact': '033-2487-8900', 'emergency': 'Yes'},
    
    # Hyderabad
    {'hospital_name': 'Apollo Hospital Hyderabad', 'city': 'Hyderabad', 'state': 'Telangana', 'type': 'private', 'cost_category': 'high', 'latitude': 17.3850, 'longitude': 78.4867, 'contact': '040-2359-0000', 'emergency': 'Yes'},
    {'hospital_name': 'Osmania General Hospital', 'city': 'Hyderabad', 'state': 'Telangana', 'type': 'government', 'cost_category': 'free', 'latitude': 17.3862, 'longitude': 78.5036, 'contact': '040-2335-8851', 'emergency': 'Yes'},
    {'hospital_name': 'Care Hospital Hyderabad', 'city': 'Hyderabad', 'state': 'Telangana', 'type': 'private', 'cost_category': 'high', 'latitude': 17.4009, 'longitude': 78.4506, 'contact': '040-4025-7000', 'emergency': 'Yes'},
    {'hospital_name': 'Public Health Center Hyderabad', 'city': 'Hyderabad', 'state': 'Telangana', 'type': 'government', 'cost_category': 'free', 'latitude': 17.3900, 'longitude': 78.4735, 'contact': '040-2345-6789', 'emergency': 'No'},
]

# Create DataFrame and save
df = pd.DataFrame(hospitals_data)
df.to_csv('hospital_data.csv', index=False)
print(f"Hospital dataset created with {len(df)} hospitals")
print(f"\nHospital distribution by type:")
print(df['type'].value_counts())
print(f"\nHospital distribution by cost category:")
print(df['cost_category'].value_counts())
