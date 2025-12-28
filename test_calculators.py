from utils.calculations import (
    SolarCalculator, 
    RainwaterCalculator, 
    GardeningCalculator,
    EnvironmentalImpact
)

print("Testing Calculators...")
print("="*60)

# Test Solar Calculator
print("\n1. SOLAR CALCULATOR")
print("-" * 60)
solar_calc = SolarCalculator()
system_size, panel_count = solar_calc.calculate_system_size(1000)
print(f"System Size: {system_size} kW")
print(f"Panel Count: {panel_count}")

production = solar_calc.calculate_production(system_size, 5.5, 10, "South")
print(f"Annual Production: {production:,} kWh")

roi = solar_calc.calculate_roi(system_size, production)
print(f"Installation Cost: ${roi['gross_cost']:,}")
print(f"After Tax Credit: ${roi['net_cost']:,}")
print(f"Annual Savings: ${roi['annual_savings']:,}")
print(f"Payback Period: {roi['payback_period']} years")
print(f"25-Year ROI: {roi['roi_percent']}%")

# Test Rainwater Calculator
print("\n2. RAINWATER CALCULATOR")
print("-" * 60)
rain_calc = RainwaterCalculator()
collection = rain_calc.calculate_collection(1000, 800)
print(f"Annual Collection: {collection:,} liters")

savings = rain_calc.calculate_savings(collection)
print(f"Tank Size Needed: {savings['tank_size']:,} liters")
print(f"Installation Cost: ${savings['installation_cost']:,}")
print(f"Annual Savings: ${savings['annual_savings']:,}")
print(f"Payback Period: {savings['payback_period']} years")

# Test Gardening Calculator
print("\n3. GARDENING CALCULATOR")
print("-" * 60)
garden_calc = GardeningCalculator()
potential = garden_calc.calculate_potential(1000, 6)
print(f"Plantable Area: {potential['plantable_area']} sqft")
print(f"Annual Yield: {potential['annual_yield_kg']} kg")
print(f"Setup Cost: ${potential['setup_cost']:,}")
print(f"Annual Value: ${potential['annual_value']:,}")
print(f"Recommended Crops: {', '.join(potential['recommended_crops'])}")

# Test Environmental Impact
print("\n4. ENVIRONMENTAL IMPACT")
print("-" * 60)
env_calc = EnvironmentalImpact()
impact = env_calc.calculate_solar_impact(15000)
print(f"CO2 Offset: {impact['co2_offset_tons']:.2f} tons/year")
print(f"Trees Equivalent: {impact['trees_equivalent']} trees")
print(f"Cars Off Road: {impact['cars_off_road']:.2f}")

print("\n" + "="*60)
print("✅ All Calculators Working!")