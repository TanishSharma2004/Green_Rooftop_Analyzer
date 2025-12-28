from PIL import Image
from models.roof_segmentation import SimplifiedRoofSegmenter

# Load sample image
image = Image.open("data/sample_images/roof1.jpg")

# Create segmenter
print("Creating segmenter...")
segmenter = SimplifiedRoofSegmenter()

# Segment roof
print("Segmenting roof...")
result = segmenter.segment_roof(image)

# Print results
print("\n" + "="*50)
print("SEGMENTATION RESULTS:")
print("="*50)
print(f"Roof Area: {result['roof_area_sqft']} sqft")
print(f"Usable Area: {result['usable_area_sqft']} sqft")
print(f"Obstacles: {result['obstacle_count']}")
print("="*50)