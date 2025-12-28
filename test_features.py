from PIL import Image
from models.feature_extractor import RoofFeatureExtractor

# Load image
image = Image.open("data/sample_images/roof1.jpg")

# Create extractor
print("Creating feature extractor...")
extractor = RoofFeatureExtractor()

# Extract features
print("Extracting features...")
features = extractor.extract_all_features(image)

# Print results
print("\n" + "="*50)
print("EXTRACTED FEATURES:")
print("="*50)
for key, value in features.items():
    print(f"{key}: {value}")
print("="*50)