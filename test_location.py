from utils.api_integrations import LocationAPI

print("Testing Location API...")
print("="*60)

location_api = LocationAPI()

# Test address to coordinates
print("\n1. Address to Coordinates:")
result = location_api.address_to_coords("New Delhi, India")
print(f"Address: {result['address']}")
print(f"Latitude: {result['lat']}")
print(f"Longitude: {result['lon']}")

# Test coordinates to address
print("\n2. Coordinates to Address:")
address = location_api.coords_to_address(28.6139, 77.2090)
print(f"Address: {address}")

print("\n✅ Location API Working!")