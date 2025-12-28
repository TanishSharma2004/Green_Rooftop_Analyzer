# utils/api_integrations.py
# Enhanced API integrations with better error handling

import os
import requests
from dotenv import load_dotenv
import json
from datetime import datetime

load_dotenv()

class WeatherAPI:
    """OpenWeatherMap API integration"""
    
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY', '')
        self.base_url = "https://api.openweathermap.org/data/2.5"
        
    def get_weather_data(self, lat, lon):
        """Get comprehensive weather data for location"""
        
        if not self.api_key:
            print("⚠️ OpenWeather API key not found, using mock data")
            return self._get_mock_weather(lat, lon)
        
        try:
            # Current weather
            current_url = f"{self.base_url}/weather?lat={lat}&lon={lon}&appid={self.api_key}&units=metric"
            current_response = requests.get(current_url, timeout=10)
            current_response.raise_for_status()
            current_data = current_response.json()
            
            # One Call API for detailed data (includes forecasts)
            onecall_url = f"{self.base_url}/onecall?lat={lat}&lon={lon}&appid={self.api_key}&units=metric&exclude=minutely,alerts"
            onecall_response = requests.get(onecall_url, timeout=10)
            onecall_response.raise_for_status()
            onecall_data = onecall_response.json()
            
            return {
                'current': {
                    'temp': round(current_data['main']['temp'], 1),
                    'feels_like': round(current_data['main']['feels_like'], 1),
                    'humidity': current_data['main']['humidity'],
                    'pressure': current_data['main']['pressure'],
                    'clouds': current_data['clouds']['all'],
                    'wind_speed': round(current_data['wind']['speed'], 1),
                    'wind_deg': current_data['wind'].get('deg', 0),
                    'description': current_data['weather'][0]['description'].title(),
                    'icon': current_data['weather'][0]['icon'],
                    'visibility': current_data.get('visibility', 10000) / 1000,  # km
                    'sunrise': datetime.fromtimestamp(current_data['sys']['sunrise']).strftime('%H:%M'),
                    'sunset': datetime.fromtimestamp(current_data['sys']['sunset']).strftime('%H:%M')
                },
                'daily': onecall_data.get('daily', [])[:7],  # 7-day forecast
                'hourly': onecall_data.get('hourly', [])[:24],  # 24-hour forecast
                'climate': {
                    'solar_irradiance': self._estimate_solar_irradiance(lat, current_data),
                    'annual_rainfall_mm': self._estimate_annual_rainfall(lat),
                    'avg_temp': round(current_data['main']['temp'], 1),
                    'uv_index': onecall_data.get('current', {}).get('uvi', 5)
                },
                'location': {
                    'name': current_data['name'],
                    'country': current_data['sys']['country'],
                    'timezone': onecall_data.get('timezone', 'UTC')
                }
            }
            
        except requests.exceptions.RequestException as e:
            print(f"⚠️ Weather API error: {e}")
            return self._get_mock_weather(lat, lon)
    
    def _estimate_solar_irradiance(self, lat, weather_data):
        """Estimate daily solar irradiance based on location and weather"""
        # Base irradiance by latitude
        base_irradiance = {
            range(0, 15): 6.0,   # Equatorial
            range(15, 30): 5.5,  # Tropical
            range(30, 45): 4.5,  # Subtropical
            range(45, 60): 3.5,  # Temperate
            range(60, 90): 2.5   # Polar
        }
        
        abs_lat = abs(lat)
        irradiance = 4.5  # Default
        
        for lat_range, value in base_irradiance.items():
            if int(abs_lat) in lat_range:
                irradiance = value
                break
        
        # Adjust for cloud cover
        clouds = weather_data.get('clouds', {}).get('all', 50)
        cloud_factor = 1 - (clouds / 200)  # Reduce by cloud percentage
        
        return round(irradiance * cloud_factor, 2)
    
    def _estimate_annual_rainfall(self, lat):
        """Estimate annual rainfall based on latitude"""
        rainfall_map = {
            range(0, 10): 2000,   # Equatorial
            range(10, 25): 1500,  # Tropical
            range(25, 35): 800,   # Subtropical
            range(35, 50): 600,   # Temperate
            range(50, 90): 400    # Polar
        }
        
        abs_lat = abs(lat)
        for lat_range, rainfall in rainfall_map.items():
            if int(abs_lat) in lat_range:
                return rainfall
        
        return 800  # Default
    
    def _get_mock_weather(self, lat, lon):
        """Mock weather data when API unavailable"""
        return {
            'current': {
                'temp': 28.5,
                'feels_like': 31.2,
                'humidity': 65,
                'pressure': 1013,
                'clouds': 40,
                'wind_speed': 3.5,
                'wind_deg': 180,
                'description': 'Partly Cloudy',
                'icon': '02d',
                'visibility': 10,
                'sunrise': '06:30',
                'sunset': '18:45'
            },
            'daily': [],
            'hourly': [],
            'climate': {
                'solar_irradiance': 5.5,
                'annual_rainfall_mm': 800,
                'avg_temp': 28,
                'uv_index': 7
            },
            'location': {
                'name': 'Location',
                'country': 'IN',
                'timezone': 'Asia/Kolkata'
            }
        }


class LocationAPI:
    """Nominatim (OpenStreetMap) API for geocoding"""
    
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
        self.headers = {'User-Agent': 'GreenRooftopAnalyzer/1.0'}
    
    def address_to_coords(self, address):
        """Convert address to coordinates"""
        
        try:
            # Check if input is already coordinates (lat, lon)
            if ',' in address:
                parts = address.split(',')
                if len(parts) == 2:
                    try:
                        lat = float(parts[0].strip())
                        lon = float(parts[1].strip())
                        # Reverse geocode to get address
                        reverse_data = self.coords_to_address(lat, lon)
                        return reverse_data
                    except ValueError:
                        pass  # Not coordinates, treat as address
            
            # Geocode address
            url = f"{self.base_url}/search"
            params = {
                'q': address,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if not data:
                print(f"⚠️ Location not found: {address}")
                return self._get_default_location()
            
            result = data[0]
            address_parts = result.get('address', {})
            
            return {
                'lat': float(result['lat']),
                'lon': float(result['lon']),
                'address': result['display_name'],
                'city': address_parts.get('city') or address_parts.get('town') or address_parts.get('village', ''),
                'state': address_parts.get('state', ''),
                'country': address_parts.get('country', ''),
                'postcode': address_parts.get('postcode', '')
            }
            
        except Exception as e:
            print(f"⚠️ Geocoding error: {e}")
            return self._get_default_location()
    
    def coords_to_address(self, lat, lon):
        """Reverse geocode coordinates to address"""
        
        try:
            url = f"{self.base_url}/reverse"
            params = {
                'lat': lat,
                'lon': lon,
                'format': 'json',
                'addressdetails': 1
            }
            
            response = requests.get(url, params=params, headers=self.headers, timeout=10)
            response.raise_for_status()
            result = response.json()
            
            address_parts = result.get('address', {})
            
            return {
                'lat': lat,
                'lon': lon,
                'address': result.get('display_name', f"{lat}, {lon}"),
                'city': address_parts.get('city') or address_parts.get('town') or address_parts.get('village', ''),
                'state': address_parts.get('state', ''),
                'country': address_parts.get('country', ''),
                'postcode': address_parts.get('postcode', '')
            }
            
        except Exception as e:
            print(f"⚠️ Reverse geocoding error: {e}")
            return {
                'lat': lat,
                'lon': lon,
                'address': f"{lat}, {lon}",
                'city': '',
                'state': '',
                'country': '',
                'postcode': ''
            }
    
    def _get_default_location(self):
        """Default location (New Delhi)"""
        return {
            'lat': 28.6139,
            'lon': 77.2090,
            'address': 'New Delhi, Delhi, India',
            'city': 'New Delhi',
            'state': 'Delhi',
            'country': 'India',
            'postcode': '110001'
        }


class GeminiAPI:
    """Google Gemini AI API integration"""
    
    def __init__(self):
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent"
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    def analyze_rooftop(self, ml_features, weather_data, location_data):
        """Comprehensive rooftop analysis using Gemini"""
        
        prompt = self._create_analysis_prompt(ml_features, weather_data, location_data)
        
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{
                    "parts": [{
                        "text": prompt
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.4,
                    "topK": 32,
                    "topP": 1,
                    "maxOutputTokens": 4096
                }
            }
            
            response = requests.post(
                f"{self.base_url}?key={self.api_key}",
                headers=headers,
                json=data,
                timeout=30
            )
            response.raise_for_status()
            
            result = response.json()
            text_response = result['candidates'][0]['content']['parts'][0]['text']
            
            # Parse JSON response
            json_start = text_response.find('{')
            json_end = text_response.rfind('}') + 1
            json_str = text_response[json_start:json_end]
            
            analysis = json.loads(json_str)
            return analysis
            
        except Exception as e:
            print(f"⚠️ Gemini API error: {e}")
            raise
    
    def _create_analysis_prompt(self, ml_features, weather_data, location_data):
        """Create detailed analysis prompt"""
        
        return f"""You are an expert in green building technologies and sustainable architecture. Analyze this rooftop for three technologies: Solar Panels, Rainwater Harvesting, and Rooftop Gardening.

ROOFTOP DATA:
- Total Area: {ml_features.get('roof_area_sqft', 0)} sqft
- Usable Area: {ml_features.get('usable_area_sqft', 0)} sqft
- Orientation: {ml_features.get('orientation', 'Unknown')}
- Roof Slope: {ml_features.get('roof_slope', 'Unknown')}
- Material: {ml_features.get('roof_material', 'Unknown')}
- Shading: {ml_features.get('shading_percent', 0)}%
- Obstacles: {ml_features.get('obstacle_count', 0)}
- Complexity: {ml_features.get('complexity_score', 0)}/10

LOCATION:
- Address: {location_data.get('address', 'Unknown')}
- Coordinates: {location_data.get('lat', 0)}, {location_data.get('lon', 0)}

WEATHER/CLIMATE:
- Current Temp: {weather_data['current']['temp']}°C
- Humidity: {weather_data['current']['humidity']}%
- Cloud Cover: {weather_data['current']['clouds']}%
- Solar Irradiance: {weather_data['climate']['solar_irradiance']} kWh/m²/day
- Annual Rainfall: {weather_data['climate']['annual_rainfall_mm']}mm
- UV Index: {weather_data['climate']['uv_index']}

Provide a comprehensive analysis in the following JSON format:

{{
  "solar": {{
    "suitability_score": 0-10,
    "system_size_kw": float,
    "panel_count": int,
    "annual_production_kwh": int,
    "installation_cost_usd": int,
    "annual_savings_usd": int,
    "payback_years": float,
    "key_points": ["point1", "point2", "point3"],
    "pros": ["pro1", "pro2"],
    "cons": ["con1", "con2"],
    "optimization_tips": ["tip1", "tip2"]
  }},
  "rainwater": {{
    "suitability_score": 0-10,
    "annual_collection_liters": int,
    "tank_size_needed_liters": int,
    "installation_cost_usd": int,
    "annual_savings_usd": int,
    "water_self_sufficiency_percent": int,
    "key_points": ["point1", "point2", "point3"],
    "pros": ["pro1", "pro2"],
    "cons": ["con1", "con2"],
    "usage_recommendations": ["rec1", "rec2"]
  }},
  "gardening": {{
    "suitability_score": 0-10,
    "plantable_area_sqft": int,
    "recommended_crops": ["crop1", "crop2", "crop3"],
    "annual_yield_kg": int,
    "setup_cost_usd": int,
    "annual_value_usd": int,
    "key_points": ["point1", "point2", "point3"],
    "pros": ["pro1", "pro2"],
    "cons": ["con1", "con2"],
    "seasonal_tips": ["tip1", "tip2"]
  }},
  "overall": {{
    "best_technology": "solar|rainwater|gardening",
    "combined_score": float,
    "recommendation": "detailed recommendation text",
    "implementation_priority": ["1st", "2nd", "3rd"],
    "environmental_impact": {{
      "co2_offset_tons_per_year": float,
      "water_saved_liters_per_year": int,
      "food_produced_kg_per_year": int
    }},
    "total_investment_usd": int,
    "total_annual_savings_usd": int
  }}
}}

Be precise with calculations and provide practical, actionable insights."""

        return prompt