from PIL import Image
from models.roof_segmentation import SimplifiedRoofSegmenter
from models.feature_extractor import RoofFeatureExtractor

print("Testing Full ML Pipeline...")
print("="*60)

# Load image
image = Image.open("data/sample_images/roof1.jpg")
print("✓ Image loaded")

# Segmentation
segmenter = SimplifiedRoofSegmenter()
seg_result = segmenter.segment_roof(image)
print("✓ Segmentation complete")

# Feature extraction
extractor = RoofFeatureExtractor()
features = extractor.extract_all_features(image)
print("✓ Feature extraction complete")

# Combine results
ml_features = {**seg_result, **features}

# Display everything
print("\n" + "="*60)
print("COMPLETE ML ANALYSIS:")
print("="*60)
print(f"Roof Area: {ml_features['roof_area_sqft']} sqft")
print(f"Usable Area: {ml_features['usable_area_sqft']} sqft")
print(f"Orientation: {ml_features['orientation']}")
print(f"Roof Slope: {ml_features['roof_slope']}")
print(f"Shading: {ml_features['shading_percent']:.1f}%")
print(f"Material: {ml_features['roof_material']}")
print(f"Obstacles: {ml_features['obstacle_count']}")
print(f"Complexity: {ml_features['complexity_score']}/10")
print("="*60)
print("\n✅ ML Pipeline Working!")