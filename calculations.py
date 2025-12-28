# utils/calculations.py
# Financial and technical calculations

import numpy as np
import pandas as pd

class SolarCalculator:
    """Calculate solar metrics"""
    
    def __init__(self):
        self.panel_wattage = 400  # Watts per panel
        self.panel_area_sqft = 21  # Area per panel
        self.cost_per_watt = 3.5  # USD
        self.electricity_rate = 0.13  # USD per kWh
        self.degradation_rate = 0.005  # 0.5% per year
        self.federal_tax_credit = 0.30  # 30% ITC
    
    def calculate_system_size(self, usable_area_sqft):
        """Calculate system size in kW"""
        panel_count = int(usable_area_sqft / self.panel_area_sqft)
        system_size_kw = (panel_count * self.panel_wattage) / 1000
        return system_size_kw, panel_count
    
    def calculate_production(self, system_size_kw, solar_irradiance, 
                            shading_percent=0, orientation="South"):
        """
        Calculate annual energy production
        
        Args:
            system_size_kw: System size in kilowatts
            solar_irradiance: Daily solar irradiance (kWh/m²/day)
            shading_percent: Percentage of shading (0-100)
            orientation: Roof orientation
        """
        
        # Base production
        daily_production = system_size_kw * solar_irradiance * 0.75  # 75% system efficiency
        
        # Orientation factor
        orientation_factors = {
            "South": 1.0,
            "South-West": 0.95,
            "South-East": 0.95,
            "West": 0.88,
            "East": 0.88,
            "North-West": 0.78,
            "North-East": 0.78,
            "North": 0.68
        }
        orientation_factor = orientation_factors.get(orientation, 0.9)
        
        # Shading factor
        shading_factor = 1.0 - (shading_percent / 100)
        
        # Annual production
        annual_production = daily_production * 365 * orientation_factor * shading_factor
        
        return int(annual_production)
    
    def calculate_roi(self, system_size_kw, annual_production_kwh):
        """Calculate financial metrics"""
        
        gross_cost = system_size_kw * 1000 * self.cost_per_watt
        tax_credit = gross_cost * self.federal_tax_credit
        net_cost = gross_cost - tax_credit
        
        annual_savings = annual_production_kwh * self.electricity_rate
        payback_period = net_cost / annual_savings if annual_savings > 0 else 99
        
        # 25-year projection
        total_savings = 0
        for year in range(1, 26):
            year_production = annual_production_kwh * ((1 - self.degradation_rate) ** year)
            year_savings = year_production * self.electricity_rate * ((1 + 0.03) ** year)
            total_savings += year_savings
        
        return {
            'gross_cost': int(gross_cost),
            'net_cost': int(net_cost),
            'annual_savings': int(annual_savings),
            'payback_period': round(payback_period, 1),
            'total_25yr_savings': int(total_savings),
            'roi_percent': round(((total_savings - net_cost) / net_cost) * 100, 1)
        }


class RainwaterCalculator:
    """Calculate rainwater harvesting potential"""
    
    def __init__(self):
        self.collection_efficiency = 0.85  # 85% collection efficiency
        self.water_rate = 0.02  # USD per liter (varies by location)
        self.tank_cost_per_liter = 0.5  # USD
    
    def calculate_collection(self, roof_area_sqft, annual_rainfall_mm):
        """
        Calculate annual water collection
        
        Args:
            roof_area_sqft: Roof catchment area
            annual_rainfall_mm: Annual rainfall in millimeters
        """
        
        # Convert sqft to m²
        roof_area_m2 = roof_area_sqft * 0.092903
        
        # Calculate collection (in liters)
        # 1mm of rain on 1m² = 1 liter
        annual_collection = roof_area_m2 * annual_rainfall_mm * self.collection_efficiency
        
        return int(annual_collection)
    
    def calculate_savings(self, annual_collection_liters):
        """Calculate financial savings"""
        
        annual_savings = annual_collection_liters * self.water_rate
        
        # Tank size (store 2 months supply)
        tank_size = annual_collection_liters / 6
        tank_cost = tank_size * self.tank_cost_per_liter
        
        # Additional costs
        installation_cost = 500  # Pipes, filters, pump
        total_cost = tank_cost + installation_cost
        
        payback_period = total_cost / annual_savings if annual_savings > 0 else 99
        
        return {
            'annual_collection': int(annual_collection_liters),
            'tank_size': int(tank_size),
            'installation_cost': int(total_cost),
            'annual_savings': int(annual_savings),
            'payback_period': round(payback_period, 1)
        }


class GardeningCalculator:
    """Calculate rooftop gardening potential"""
    
    def __init__(self):
        self.soil_depth_inches = 12  # Standard raised bed depth
        self.soil_cost_per_cuft = 40  # USD
        self.setup_cost_per_sqft = 15  # USD (includes structure, irrigation)
        self.yield_per_sqft = 2  # kg per sq ft per year (average)
        self.crop_value_per_kg = 3  # USD
    
    def calculate_potential(self, usable_area_sqft, sunlight_hours=6):
        """
        Calculate gardening potential
        
        Args:
            usable_area_sqft: Available flat area
            sunlight_hours: Daily sunlight hours
        """
        
        # Only 30% of roof typically suitable for gardening
        plantable_area = usable_area_sqft * 0.3
        
        # Adjust for sunlight
        sunlight_factor = min(sunlight_hours / 6, 1.0)  # 6 hours is ideal
        
        # Calculate yield
        annual_yield = plantable_area * self.yield_per_sqft * sunlight_factor
        
        # Costs
        soil_volume_cuft = plantable_area * (self.soil_depth_inches / 12)
        soil_cost = soil_volume_cuft * self.soil_cost_per_cuft
        setup_cost = plantable_area * self.setup_cost_per_sqft
        total_cost = int(soil_cost + setup_cost)
        
        # Value
        annual_value = annual_yield * self.crop_value_per_kg
        
        # Recommended crops based on area
        if plantable_area < 50:
            crops = ["Herbs", "Lettuce", "Spinach"]
        elif plantable_area < 150:
            crops = ["Tomatoes", "Peppers", "Lettuce", "Herbs"]
        else:
            crops = ["Tomatoes", "Peppers", "Eggplant", "Beans", "Lettuce"]
        
        return {
            'plantable_area': int(plantable_area),
            'annual_yield_kg': int(annual_yield),
            'setup_cost': total_cost,
            'annual_value': int(annual_value),
            'recommended_crops': crops,
            'payback_period': round(total_cost / annual_value, 1) if annual_value > 0 else 99
        }


class EnvironmentalImpact:
    """Calculate environmental benefits"""
    
    def calculate_solar_impact(self, annual_production_kwh):
        """Calculate CO2 offset from solar"""
        
        # Average grid CO2: 0.92 lbs per kWh
        co2_lbs_per_kwh = 0.92
        co2_offset_lbs = annual_production_kwh * co2_lbs_per_kwh
        co2_offset_tons = co2_offset_lbs / 2204.62
        
        return {
            'co2_offset_tons': round(co2_offset_tons, 2),
            'trees_equivalent': int(co2_offset_tons * 16),
            'cars_off_road': round(co2_offset_tons / 4.6, 2)
        }
    
    def calculate_water_impact(self, annual_collection_liters):
        """Calculate water conservation impact"""
        
        # Groundwater saved
        return {
            'groundwater_saved_liters': int(annual_collection_liters),
            'bottles_equivalent': int(annual_collection_liters)  # 1L bottles
        }
    
    def calculate_food_impact(self, annual_yield_kg):
        """Calculate food production impact"""
        
        return {
            'food_produced_kg': int(annual_yield_kg),
            'meals_equivalent': int(annual_yield_kg * 3)  # ~3 meals per kg
        }


# Usage example
if __name__ == "__main__":
    print("Testing Calculators...")
    print("="*60)
    
    # Test Solar Calculator
    print("\n1. Solar Calculator")
    solar_calc = SolarCalculator()
    system_size, panel_count = solar_calc.calculate_system_size(1000)
    print(f"System Size: {system_size} kW ({panel_count} panels)")
    
    production = solar_calc.calculate_production(system_size, 5.5, 10, "South")
    print(f"Annual Production: {production:,} kWh")
    
    roi = solar_calc.calculate_roi(system_size, production)
    print(f"Payback Period: {roi['payback_period']} years")
    print(f"25-Year ROI: {roi['roi_percent']}%")
    
    # Test Rainwater Calculator
    print("\n2. Rainwater Calculator")
    rain_calc = RainwaterCalculator()
    collection = rain_calc.calculate_collection(1000, 800)
    print(f"Annual Collection: {collection:,} liters")
    
    savings = rain_calc.calculate_savings(collection)
    print(f"Tank Size: {savings['tank_size']:,} liters")
    print(f"Payback: {savings['payback_period']} years")
    
    # Test Gardening Calculator
    print("\n3. Gardening Calculator")
    garden_calc = GardeningCalculator()
    potential = garden_calc.calculate_potential(1000, 6)
    print(f"Plantable Area: {potential['plantable_area']} sqft")
    print(f"Annual Yield: {potential['annual_yield_kg']} kg")
    print(f"Crops: {', '.join(potential['recommended_crops'])}")
    
    print("\n" + "="*60)
    print("All calculators working!")