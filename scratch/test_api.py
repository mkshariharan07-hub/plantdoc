import os
import requests
from dotenv import load_dotenv

load_dotenv()

def test_keys():
    pk = os.getenv("PLANTNET_API_KEY")
    ck = os.getenv("CROP_HEALTH_API_KEY")
    
    print(f"PlantNet Key: {pk[:5]}...{pk[-5:] if pk else 'NONE'}")
    print(f"Kindwise Key: {ck[:5]}...{ck[-5:] if ck else 'NONE'}")
    
    # Test PlantNet
    p_url = f"https://my-api.plantnet.org/v2/identify/all?api-key={pk}"
    try:
        r = requests.get(p_url.replace("identify/all", "identify"), timeout=5) # Simple ping
        print(f"PlantNet Status: {r.status_code}")
    except Exception as e:
        print(f"PlantNet Error: {e}")
        
    # Test Kindwise
    c_url = "https://crop.kindwise.com/api/v1/identification"
    try:
        r = requests.get(c_url.replace("identification", ""), headers={"Api-Key": ck}, timeout=5)
        print(f"Kindwise Status: {r.status_code}")
    except Exception as e:
        print(f"Kindwise Error: {e}")

if __name__ == "__main__":
    test_keys()
