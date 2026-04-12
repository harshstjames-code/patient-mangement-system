"""
Hospital Recommendation Engine
Recommends nearby hospitals based on patient location and disease severity
"""
import pandas as pd
import math
import os

class HospitalRecommender:
    def __init__(self, hospital_data_path='hospital_data.csv'):
        """Initialize the hospital recommender with hospital database"""
        self.hospitals_df = None
        self.load_hospital_data(hospital_data_path)
    
    def load_hospital_data(self, hospital_data_path):
        """Load hospital data from CSV"""
        try:
            if os.path.exists(hospital_data_path):
                self.hospitals_df = pd.read_csv(hospital_data_path)
                print(f"✓ Loaded {len(self.hospitals_df)} hospitals from database")
            else:
                print(f"Warning: Hospital data file not found at {hospital_data_path}")
                self.hospitals_df = pd.DataFrame()
                
        except Exception as e:
            print(f"Error loading hospital data: {e}")
            self.hospitals_df = pd.DataFrame()
    
    def calculate_distance(self, lat1, lon1, lat2, lon2):
        """
        Calculate distance between two coordinates using Haversine formula
        Returns distance in kilometers
        """
        try:
            # Haversine formula
            R = 6371  # Earth's radius in kilometers
            
            lat1_rad = math.radians(lat1)
            lat2_rad = math.radians(lat2)
            delta_lat = math.radians(lat2 - lat1)
            delta_lon = math.radians(lon2 - lon1)
            
            a = math.sin(delta_lat/2) ** 2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2) ** 2
            c = 2 * math.asin(math.sqrt(a))
            
            distance = R * c
            return round(distance, 2)
            
        except Exception as e:
            print(f"Error calculating distance: {e}")
            return float('inf')
    
    def recommend_hospitals(self, patient_latitude, patient_longitude, 
                          predicted_severity='Medium', top_n=5):
        """
        Recommend hospitals based on patient location and disease severity
        
        Args:
            patient_latitude (float): Patient's latitude
            patient_longitude (float): Patient's longitude
            predicted_severity (str): Disease severity - 'Low', 'Medium', 'High'
            top_n (int): Number of hospitals to recommend
        
        Returns:
            list: List of recommended hospitals with distances
        """
        try:
            if self.hospitals_df.empty:
                return {
                    'status': 'error',
                    'message': 'Hospital database not available'
                }
            
            # Create a copy and calculate distances
            hospitals = self.hospitals_df.copy()
            hospitals['distance_km'] = hospitals.apply(
                lambda row: self.calculate_distance(
                    patient_latitude, patient_longitude,
                    row['latitude'], row['longitude']
                ), axis=1
            )
            
            # Sort by priority based on severity
            if predicted_severity == 'High':
                # For high severity: prioritize government and charitable hospitals
                # Then sort by distance
                priority_order = {'government': 0, 'charitable': 1, 'private': 2}
                hospitals['priority'] = hospitals['type'].map(priority_order)
                hospitals = hospitals.sort_values(['priority', 'distance_km'])
            else:
                # For low/medium severity: just sort by distance
                hospitals = hospitals.sort_values('distance_km')
            
            # Get top N hospitals
            recommended = hospitals.head(top_n).to_dict('records')
            
            # Format the response
            recommendations = []
            for i, hospital in enumerate(recommended, 1):
                recommendations.append({
                    'rank': i,
                    'hospital_name': hospital['hospital_name'],
                    'city': hospital['city'],
                    'state': hospital['state'],
                    'type': hospital['type'],
                    'cost_category': hospital['cost_category'],
                    'distance_km': hospital['distance_km'],
                    'contact': hospital['contact'],
                    'emergency_available': hospital['emergency'],
                    'latitude': hospital['latitude'],
                    'longitude': hospital['longitude']
                })
            
            # Count hospital types
            gov_count = len([h for h in recommendations if h['type'] == 'government'])
            charity_count = len([h for h in recommendations if h['type'] == 'charitable'])
            private_count = len([h for h in recommendations if h['type'] == 'private'])
            
            result = {
                'status': 'success',
                'hospitals_found': len(recommendations),
                'severity_level': predicted_severity,
                'patient_location': {
                    'latitude': patient_latitude,
                    'longitude': patient_longitude
                },
                'recommendations': recommendations,
                'summary': {
                    'government_hospitals': gov_count,
                    'charitable_hospitals': charity_count,
                    'private_hospitals': private_count,
                    'nearest_distance_km': recommendations[0]['distance_km'] if recommendations else None,
                    'farthest_distance_km': recommendations[-1]['distance_km'] if recommendations else None
                }
            }
            
            return result
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Recommendation failed: {str(e)}"
            }
    
    def filter_hospitals_by_cost(self, patient_latitude, patient_longitude, 
                                cost_category='free', top_n=5):
        """
        Recommend hospitals filtered by cost category
        
        Args:
            patient_latitude (float): Patient's latitude
            patient_longitude (float): Patient's longitude
            cost_category (str): 'free', 'low', 'medium', 'high'
            top_n (int): Number of hospitals to recommend
        
        Returns:
            list: List of recommended hospitals matching cost criteria
        """
        try:
            if self.hospitals_df.empty:
                return {'status': 'error', 'message': 'Hospital database not available'}

            requested_cost = str(cost_category).strip().lower()
            available_costs = sorted(
                self.hospitals_df['cost_category'].dropna().astype(str).str.lower().unique().tolist()
            )
            
            # Filter by cost category
            filtered = self.hospitals_df[
                self.hospitals_df['cost_category'].astype(str).str.lower() == requested_cost
            ].copy()
            
            if filtered.empty:
                # Fallback: return nearest hospitals instead of an empty list.
                fallback = self.recommend_hospitals(
                    patient_latitude=patient_latitude,
                    patient_longitude=patient_longitude,
                    predicted_severity='Medium',
                    top_n=top_n
                )
                if fallback.get('status') == 'success':
                    fallback['cost_category'] = requested_cost
                    fallback['fallback_used'] = True
                    fallback['requested_cost_category'] = requested_cost
                    fallback['available_cost_categories'] = available_costs
                    fallback['message'] = (
                        f"No hospitals found in '{requested_cost}' cost category. "
                        "Showing nearest available hospitals instead."
                    )
                return fallback
            
            # Calculate distances
            filtered['distance_km'] = filtered.apply(
                lambda row: self.calculate_distance(
                    patient_latitude, patient_longitude,
                    row['latitude'], row['longitude']
                ), axis=1
            )
            
            # Sort by distance and get top N
            filtered = filtered.sort_values('distance_km').head(top_n)
            
            recommendations = []
            for i, hospital in enumerate(filtered.to_dict('records'), 1):
                recommendations.append({
                    'rank': i,
                    'hospital_name': hospital['hospital_name'],
                    'city': hospital['city'],
                    'state': hospital['state'],
                    'type': hospital['type'],
                    'cost_category': hospital['cost_category'],
                    'distance_km': hospital['distance_km'],
                    'contact': hospital['contact'],
                    'emergency_available': hospital['emergency'],
                    'latitude': hospital['latitude'],
                    'longitude': hospital['longitude']
                })
            
            return {
                'status': 'success',
                'hospitals_found': len(recommendations),
                'cost_category': requested_cost,
                'fallback_used': False,
                'available_cost_categories': available_costs,
                'recommendations': recommendations
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': f"Filtering failed: {str(e)}"
            }
    
    def get_free_hospitals_nearby(self, patient_latitude, patient_longitude, top_n=3):
        """Get free government and charitable hospitals nearby"""
        return self.filter_hospitals_by_cost(
            patient_latitude, patient_longitude, 
            cost_category='free', top_n=top_n
        )


# Example usage
if __name__ == "__main__":
    # Initialize recommender
    recommender = HospitalRecommender()
    
    # Test recommendations for Delhi
    print("\n" + "="*80)
    print("HOSPITAL RECOMMENDATION TEST - DELHI")
    print("="*80)
    
    delhi_lat = 28.6032
    delhi_lon = 77.1824
    
    # High severity case
    print("\n1. HIGH SEVERITY - Recommending nearest hospitals (prioritizing government)")
    result_high = recommender.recommend_hospitals(delhi_lat, delhi_lon, 
                                                   predicted_severity='High', top_n=5)
    
    if result_high['status'] == 'success':
        print(f"\nFound {result_high['hospitals_found']} hospitals")
        print(f"Summary: Gov-{result_high['summary']['government_hospitals']}, " +
              f"Charity-{result_high['summary']['charitable_hospitals']}, " +
              f"Private-{result_high['summary']['private_hospitals']}")
        print("\nRecommendations:")
        for rec in result_high['recommendations']:
            print(f"\n  {rec['rank']}. {rec['hospital_name']}")
            print(f"     Type: {rec['type']} | Cost: {rec['cost_category']}")
            print(f"     Distance: {rec['distance_km']} km")
            print(f"     Contact: {rec['contact']}")
            print(f"     Emergency: {rec['emergency_available']}")
    
    # Low severity case - only free hospitals
    print("\n\n2. LOW SEVERITY - Recommending only FREE hospitals")
    result_free = recommender.get_free_hospitals_nearby(delhi_lat, delhi_lon, top_n=3)
    
    if result_free['status'] == 'success':
        print(f"\nFound {result_free['hospitals_found']} free hospitals")
        print("\nRecommendations:")
        for rec in result_free['recommendations']:
            print(f"\n  {rec['rank']}. {rec['hospital_name']}")
            print(f"     Type: {rec['type']}")
            print(f"     Distance: {rec['distance_km']} km")
            print(f"     Contact: {rec['contact']}")
