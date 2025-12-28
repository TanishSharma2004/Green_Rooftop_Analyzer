from utils.api_integrations import GeminiAPI

print("Testing Gemini API...")
print("="*60)

try:
    # Create API instance
    gemini_api = GeminiAPI()
    print("✓ Gemini API initialized")
    
    # Test with dummy data
    ml_features = {
        'roof_area_sqft': 1200,
        'usable_area_sqft': 1000,
        'orientation': 'South',
        'roof_slope': 'Low',
        'shading_percent': 10,
        'roof_material': 'Asphalt',
        'obstacle_count': 2,
        'complexity_score': 6.5
    }
    
    weather_data = {
        'current': {
            'temp': 32,
            'humidity': 65,
            'clouds': 15,
            'description': 'clear sky',
            'wind_speed': 2.5
        },
        'climate': {
            'annual_rainfall_mm': 650,
            'annual_sun_hours': 2800,
            'avg_temp': 28,
            'solar_irradiance': 5.5
        }
    }
    
    location_data = {
        'lat': 28.6139,
        'lon': 77.2090,
        'address': 'New Delhi, India'
    }
    
    print("\nSending data to Gemini...")
    result = gemini_api.analyze_rooftop(ml_features, weather_data, location_data)
    
    print("\n✅ Gemini Analysis Complete!")
    print("\nSolar Suitability:", result['solar']['suitability_score'])
    print("Rainwater Suitability:", result['rainwater']['suitability_score'])
    print("Gardening Suitability:", result['gardening']['suitability_score'])
    print("Best Technology:", result['overall']['best_technology'])
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("\nMake sure your GEMINI_API_KEY is correct in .env file")