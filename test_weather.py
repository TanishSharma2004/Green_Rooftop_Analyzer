from utils.api_integrations import WeatherAPI

print("Testing Weather API...")
print("="*60)

# Create API instance
weather_api = WeatherAPI()

# Test with Delhi coordinates
lat, lon = 28.6139, 77.2090

print(f"Getting weather for: {lat}, {lon}")
weather_data = weather_api.get_weather_data(lat, lon)

print("\nCurrent Weather:")
print(f"Temperature: {weather_data['current']['temp']}°C")
print(f"Humidity: {weather_data['current']['humidity']}%")
print(f"Clouds: {weather_data['current']['clouds']}%")
print(f"Description: {weather_data['current']['description']}")

print("\nClimate Data:")
print(f"Annual Rainfall: {weather_data['climate']['annual_rainfall_mm']}mm")
print(f"Sun Hours: {weather_data['climate']['annual_sun_hours']}")
print(f"Solar Irradiance: {weather_data['climate']['solar_irradiance']} kWh/m²/day")

print("\n✅ Weather API Working!")