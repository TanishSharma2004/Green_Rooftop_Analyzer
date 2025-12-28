# models/download_models.py
# Download pre-trained models - NO TRAINING NEEDED!

import os
import torch
from segment_anything import sam_model_registry, SamPredictor
import urllib.request
from tqdm import tqdm

def download_file(url, filename):
    """Download file with progress bar"""
    print(f"Downloading {filename}...")
    
    def reporthook(count, block_size, total_size):
        if total_size > 0:
            percent = int(count * block_size * 100 / total_size)
            print(f"\rProgress: {percent}%", end='')
    
    urllib.request.urlretrieve(url, filename, reporthook)
    print("\nDownload complete!")

def setup_models():
    """Download all required pre-trained models"""
    
    os.makedirs('models/pretrained', exist_ok=True)
    
    print("="*60)
    print("DOWNLOADING PRE-TRAINED MODELS")
    print("="*60)
    
    # 1. Segment Anything Model (SAM) - Meta's model for segmentation
    # This is PERFECT for roof segmentation - no training needed!
    print("\n[1/2] Segment Anything Model (SAM)")
    sam_url = "https://dl.fbaipublicfiles.com/segment_anything/sam_vit_b_01ec64.pth"
    sam_path = "models/pretrained/sam_vit_b.pth"
    
    if not os.path.exists(sam_path):
        download_file(sam_url, sam_path)
    else:
        print("✓ SAM model already exists")
    
    # 2. ResNet for feature extraction (pre-trained on ImageNet)
    print("\n[2/2] ResNet50 for feature extraction")
    print("Downloading via PyTorch...")
    
    from torchvision import models
    resnet = models.resnet50(pretrained=True)
    torch.save(resnet.state_dict(), 'models/pretrained/resnet50.pth')
    print("✓ ResNet50 downloaded")
    
    print("\n" + "="*60)
    print("✅ ALL MODELS READY!")
    print("="*60)
    print("\nYou now have:")
    print("1. SAM for roof segmentation (no training needed)")
    print("2. ResNet50 for feature extraction (pre-trained)")
    print("\nNo training required! These work out of the box.")

if __name__ == "__main__":
    setup_models()
    
    # Test if models work
    print("\n" + "="*60)
    print("TESTING MODELS...")
    print("="*60)
    
    try:
        # Test SAM
        sam_checkpoint = "models/pretrained/sam_vit_b.pth"
        model_type = "vit_b"
        sam = sam_model_registry[model_type](checkpoint=sam_checkpoint)
        print("✓ SAM model loaded successfully")
        
        # Test ResNet
        resnet = models.resnet50()
        resnet.load_state_dict(torch.load('models/pretrained/resnet50.pth'))
        print("✓ ResNet50 loaded successfully")
        
        print("\n🎉 All models working perfectly!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Please run: pip install segment-anything torch torchvision")