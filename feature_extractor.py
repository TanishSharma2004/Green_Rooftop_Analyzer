# models/feature_extractor.py
# Extract roof features using CV + simple ML

import cv2
import numpy as np
from PIL import Image
import torch
import torchvision.transforms as transforms
from torchvision import models

class RoofFeatureExtractor:
    """
    Extract key features from rooftop images
    Uses pre-trained models + computer vision
    """
    
    def __init__(self):
        # Load pre-trained ResNet for deep features (optional)
        self.use_deep_features = False
        try:
            self.resnet = models.resnet50(pretrained=True)
            self.resnet.eval()
            self.use_deep_features = True
            print("✓ ResNet50 loaded for deep features")
        except:
            print("⚠ ResNet not available, using CV features only")
        
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.485, 0.456, 0.406], 
                               std=[0.229, 0.224, 0.225])
        ])
    
    def extract_all_features(self, image, roof_mask=None):
        """
        Extract comprehensive features from rooftop image
        
        Returns:
            dict: All extracted features
        """
        
        if isinstance(image, Image.Image):
            image_np = np.array(image)
        else:
            image_np = image
        
        features = {}
        
        # 1. Orientation Detection
        features['orientation'] = self.detect_orientation(image_np)
        
        # 2. Shading Analysis
        features['shading_percent'] = self.analyze_shading(image_np)
        
        # 3. Roof Material (texture analysis)
        features['roof_material'] = self.detect_roof_material(image_np)
        
        # 4. Slope Detection
        features['roof_slope'] = self.estimate_slope(image_np)
        
        # 5. Complexity Score
        features['complexity_score'] = self.calculate_complexity(image_np)
        
        return features
    
    def detect_orientation(self, image):
        """
        Detect roof orientation using edge analysis
        Returns: N, NE, E, SE, S, SW, W, NW
        """
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, 200)
        
        if lines is None:
            return "Unknown"
        
        # Calculate dominant angle
        angles = []
        for line in lines[:10]:  # Top 10 lines
            rho, theta = line[0]
            angle = np.degrees(theta)
            angles.append(angle)
        
        avg_angle = np.mean(angles)
        
        # Convert to compass direction
        # Assuming image is oriented North-up
        if 0 <= avg_angle < 22.5 or 157.5 <= avg_angle < 180:
            return "South"
        elif 22.5 <= avg_angle < 67.5:
            return "South-West"
        elif 67.5 <= avg_angle < 112.5:
            return "West"
        elif 112.5 <= avg_angle < 157.5:
            return "North-West"
        else:
            return "South"  # Default to best for solar
    
    def analyze_shading(self, image):
        """
        Analyze shading percentage using brightness
        """
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate histogram
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        
        # Dark pixels (likely shadows) are in lower range
        total_pixels = image.shape[0] * image.shape[1]
        dark_pixels = np.sum(hist[:80])  # Pixels with intensity < 80
        
        shading_percent = (dark_pixels / total_pixels) * 100
        
        return min(shading_percent, 100)  # Cap at 100%
    
    def detect_roof_material(self, image):
        """
        Detect roof material based on texture
        Options: Asphalt, Metal, Tile, Concrete
        """
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Calculate texture features
        # 1. Standard deviation (roughness)
        std_dev = np.std(gray)
        
        # 2. Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Simple classification based on features
        if std_dev > 50 and edge_density > 0.15:
            return "Tile"  # Rough texture, many edges
        elif std_dev < 30:
            return "Metal"  # Smooth, uniform
        elif edge_density < 0.1:
            return "Concrete"  # Smooth but matte
        else:
            return "Asphalt"  # Most common
    
    def estimate_slope(self, image):
        """
        Estimate roof slope/pitch
        Returns: Flat, Low (<15°), Medium (15-30°), Steep (>30°)
        """
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # Detect lines
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, 
                               minLineLength=100, maxLineGap=10)
        
        if lines is None:
            return "Flat"
        
        # Calculate average line angle
        angles = []
        for line in lines[:20]:
            x1, y1, x2, y2 = line[0]
            angle = np.abs(np.degrees(np.arctan2(y2 - y1, x2 - x1)))
            angles.append(angle)
        
        avg_angle = np.mean(angles)
        
        # Classify slope
        if avg_angle < 5:
            return "Flat"
        elif avg_angle < 15:
            return "Low"
        elif avg_angle < 30:
            return "Medium"
        else:
            return "Steep"
    
    def calculate_complexity(self, image):
        """
        Calculate roof complexity score (1-10)
        Based on: edges, contours, texture variation
        """
        
        gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
        
        # 1. Edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_score = np.sum(edges > 0) / edges.size * 100
        
        # 2. Number of contours
        contours, _ = cv2.findContours(edges, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        contour_score = min(len(contours) / 10, 10)  # Normalize to 10
        
        # 3. Texture variation
        std_score = min(np.std(gray) / 10, 10)
        
        # Combined score
        complexity = (edge_score * 0.4 + contour_score * 0.3 + std_score * 0.3)
        
        return min(round(complexity, 1), 10)
    
    def get_deep_features(self, image):
        """
        Extract deep features using pre-trained ResNet
        (Optional - for more advanced analysis)
        """
        
        if not self.use_deep_features:
            return None
        
        # Convert to PIL
        if isinstance(image, np.ndarray):
            image_pil = Image.fromarray(image)
        else:
            image_pil = image
        
        # Transform and extract features
        image_tensor = self.transform(image_pil).unsqueeze(0)
        
        with torch.no_grad():
            features = self.resnet(image_tensor)
        
        return features.numpy()


# Usage example
if __name__ == "__main__":
    extractor = RoofFeatureExtractor()
    
    # Test with sample image
    test_image = Image.open("data/sample_images/test_roof.jpg")
    features = extractor.extract_all_features(test_image)
    
    print("\n📊 Extracted Features:")
    print("="*50)
    for key, value in features.items():
        print(f"{key}: {value}")
    print("="*50)