import os
import cv2
import numpy as np
from dotenv import load_dotenv
from utils import identify_plant_plantnet, identify_crop_health, get_perenual_care_info

load_dotenv()

def test_apis():
    # Create a dummy image (green leaf-ish)
    img = np.zeros((300, 300, 3), dtype=np.uint8)
    img[50:250, 50:250] = [0, 255, 0] # Green square
    
    print("--- Testing PlantNet API ---")
    p_res = identify_plant_plantnet(img)
    print(p_res)
    
    print("\n--- Testing Crop.Health API ---")
    c_res = identify_crop_health(img)
    print(c_res)
    
    variant = p_res.get('plant', 'Rose')
    print(f"\n--- Testing Perenual API with variant: {variant} ---")
    per_res = get_perenual_care_info(variant)
    print(per_res)

if __name__ == "__main__":
    test_apis()
