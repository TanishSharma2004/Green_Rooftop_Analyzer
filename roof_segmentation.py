# models/roof_segmentation.py
# Use Meta's SAM - Zero training required!

import cv2
import numpy as np
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator
import torch
from PIL import Image

class RoofSegmenter:
    """
    Roof segmentation using pre-trained SAM (Segment Anything Model)
    NO TRAINING NEEDED - Works out of the box!
    """
    
    def __init__(self, model_path="models/pretrained/sam_vit_b.pth"):
        print("Loading SAM model...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        
        # Load SAM model
        sam = sam_model_registry["vit_b"](checkpoint=model_path)
        sam.to(device=self.device)
        
        # Create mask generator
        self.mask_generator = SamAutomaticMaskGenerator(sam)
        print(f"✓ SAM loaded on {self.device}")
    
    def segment_roof(self, image):
        """
        Segment the roof from aerial image
        
        Args:
            image: PIL Image or numpy array
            
        Returns:
            dict with roof_mask, roof_area, obstacles
        """
        
        # Convert PIL to numpy if needed
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image
        
        # Generate masks
        print("Generating segments...")
        masks = self.mask_generator.generate(image_np)
        
        # Find largest mask (usually the roof)
        if len(masks) == 0:
            return {
                'roof_mask': None,
                'roof_area_sqft': 0,
                'obstacles': [],
                'usable_area_sqft': 0
            }
        
        # Sort by area
        masks = sorted(masks, key=lambda x: x['area'], reverse=True)
        
        # Largest segment is likely the roof
        roof_mask = masks[0]['segmentation']
        
        # Smaller segments are obstacles
        obstacles = []
        for mask in masks[1:6]:  # Top 5 other segments
            if mask['area'] > 100:  # Filter small noise
                obstacles.append({
                    'mask': mask['segmentation'],
                    'area': mask['area'],
                    'bbox': mask['bbox']
                })
        
        # Calculate areas (assuming 1 pixel = 0.3m based on typical satellite images)
        pixel_to_sqm = 0.09  # (0.3m)^2
        sqm_to_sqft = 10.764
        
        roof_area_pixels = np.sum(roof_mask)
        roof_area_sqft = roof_area_pixels * pixel_to_sqm * sqm_to_sqft
        
        # Calculate usable area (roof - obstacles)
        obstacle_area_pixels = sum([obs['area'] for obs in obstacles])
        usable_area_sqft = (roof_area_pixels - obstacle_area_pixels) * pixel_to_sqm * sqm_to_sqft
        
        return {
            'roof_mask': roof_mask,
            'roof_area_sqft': int(roof_area_sqft),
            'obstacles': obstacles,
            'usable_area_sqft': int(usable_area_sqft),
            'obstacle_count': len(obstacles)
        }
    
    def visualize_segmentation(self, image, segmentation_result):
        """Create visualization of segmentation"""
        
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image.copy()
        
        roof_mask = segmentation_result['roof_mask']
        
        if roof_mask is None:
            return image_np
        
        # Create colored overlay
        overlay = image_np.copy()
        overlay[roof_mask] = overlay[roof_mask] * 0.5 + np.array([0, 255, 0]) * 0.5
        
        # Draw obstacles
        for obs in segmentation_result['obstacles']:
            obs_mask = obs['mask']
            overlay[obs_mask] = overlay[obs_mask] * 0.5 + np.array([255, 0, 0]) * 0.5
        
        return overlay.astype(np.uint8)


# Alternative: Simple Computer Vision approach (if SAM is too heavy)
class SimplifiedRoofSegmenter:
    """
    Lightweight alternative using traditional CV
    NO ML training needed!
    """
    
    def segment_roof(self, image):
        """Simple segmentation using color and edge detection"""
        
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image
        
        # Convert to grayscale
        gray = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY)
        
        # Apply GaussianBlur
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # Edge detection
        edges = cv2.Canny(blurred, 50, 150)
        
        # Find contours
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Find largest contour (roof)
        if len(contours) == 0:
            return {
                'roof_mask': None,
                'roof_area_sqft': 0,
                'obstacles': [],
                'usable_area_sqft': 0
            }
        
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Create mask
        mask = np.zeros(gray.shape, dtype=np.uint8)
        cv2.drawContours(mask, [largest_contour], -1, 255, -1)
        
        # Calculate area
        roof_area_pixels = cv2.contourArea(largest_contour)
        pixel_to_sqm = 0.09
        sqm_to_sqft = 10.764
        roof_area_sqft = roof_area_pixels * pixel_to_sqm * sqm_to_sqft
        
        # Simple obstacle detection (smaller contours)
        obstacles = []
        for contour in contours[1:6]:
            area = cv2.contourArea(contour)
            if area > 100:
                x, y, w, h = cv2.boundingRect(contour)
                obstacles.append({
                    'area': area,
                    'bbox': [x, y, w, h]
                })
        
        obstacle_area = sum([obs['area'] for obs in obstacles])
        usable_area_sqft = (roof_area_pixels - obstacle_area) * pixel_to_sqm * sqm_to_sqft
        
        return {
            'roof_mask': mask > 0,
            'roof_area_sqft': int(roof_area_sqft),
            'obstacles': obstacles,
            'usable_area_sqft': int(usable_area_sqft),
            'obstacle_count': len(obstacles)
        }


# Usage example
if __name__ == "__main__":
    # Test the segmenter
    test_image = Image.open("data/sample_images/test_roof.jpg")
    
    # Option 1: Use SAM (better but heavier)
    try:
        segmenter = RoofSegmenter()
        result = segmenter.segment_roof(test_image)
        print("SAM Results:", result)
    except:
        print("SAM not available, using simplified version")
        
        # Option 2: Use simplified version (lighter)
        segmenter = SimplifiedRoofSegmenter()
        result = segmenter.segment_roof(test_image)
        print("Simplified Results:", result)