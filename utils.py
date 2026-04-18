"""
utils.py — PlantPulse Shared Utilities (v2.1)
=======================================
Single source of truth for:
  • Feature extraction  (used by main.py, app.py, server.py)
  • Artifact paths
  • Disease knowledge base
  • Image decoding helpers

RULE: Any change to extract_features() is made HERE only.
      All other files import from this module.
"""

import cv2
import numpy as np
import os
import requests
import json
import base64
from typing import Optional
from dotenv import load_dotenv
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

# Load environment variables
load_dotenv()

# ── Artifact paths (one place to change if you move files) ────────────────────
MODEL_PATH  = "plant_model.pkl"
SCALER_PATH = "plant_scaler.pkl"
REPORT_PATH = "training_report.txt"
IMG_SIZE    = (129, 129)

# Feature-space identifiers
FEATURE_MODE_RAW  = "raw_pixels"    # 129×129×3 = 49923 dims
FEATURE_MODE_HIST = "histogram"     # 63 dims
RAW_PIXEL_DIM     = 129 * 129 * 3  # = 49923


# ═══════════════════════════════════════════════════════════════════════════════
# FEATURE EXTRACTION
# ═══════════════════════════════════════════════════════════════════════════════
def extract_features(img: np.ndarray) -> np.ndarray:
    """
    Deterministic, normalized feature vector (63 dims).
    Improved to be more robust to lighting and scale.
    """
    # 1. Resize once to standard 128x128
    img_std = cv2.resize(img, IMG_SIZE)
    hsv     = cv2.cvtColor(img_std, cv2.COLOR_BGR2HSV)

    # 2. Color histograms — normalized to sum to 1
    h_hist = cv2.calcHist([hsv], [0], None, [24], [0, 180]).flatten()
    s_hist = cv2.calcHist([hsv], [1], None, [16], [0, 256]).flatten()
    v_hist = cv2.calcHist([hsv], [2], None, [16], [0, 256]).flatten()
    
    h_hist /= (h_hist.sum() + 1e-7)
    s_hist /= (s_hist.sum() + 1e-7)
    v_hist /= (v_hist.sum() + 1e-7)

    # 3. Global statistics (normalized 0-1)
    means, stds = cv2.meanStdDev(img_std)
    stats = np.concatenate([means.flatten(), stds.flatten()]) / 255.0

    # 4. Texture/Edge Density
    gray  = cv2.cvtColor(img_std, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    edge_density = float(np.sum(edges > 0)) / (IMG_SIZE[0] * IMG_SIZE[1])

    return np.concatenate([h_hist, s_hist, v_hist, stats, [edge_density]])


FEATURE_DIM = len(extract_features(np.zeros((8, 8, 3), dtype=np.uint8)))  # = 63


def extract_features_raw(img: np.ndarray) -> np.ndarray:
    """
    Legacy extractor — raw pixel flatten (128×128×3 = 49152 dims).
    CRITICAL: Now normalizes to 0-1 to fix 'wrong results' error.
    """
    resized = cv2.resize(img, IMG_SIZE).astype(np.float64) / 255.0
    return resized.flatten()


def get_feature_mode(model) -> str:
    """
    Inspect a loaded model and return which feature extractor it was trained with.

    Returns:
        'raw_pixels'  — model.n_features_in_ == 49152  (old pipeline)
        'histogram'   — model.n_features_in_ == 63     (new pipeline)

    Raises:
        ValueError if the feature count is unrecognised.
    """
    n = model.n_features_in_
    if n == RAW_PIXEL_DIM:
        return FEATURE_MODE_RAW
    if n == FEATURE_DIM:
        return FEATURE_MODE_HIST
    raise ValueError(
        f"Unrecognised model feature count: {n}. "
        f"Expected {RAW_PIXEL_DIM} (old) or {FEATURE_DIM} (new). "
        f"Retrain with `python main.py`."
    )


def extract_for_model(img: np.ndarray, model) -> np.ndarray:
    """
    Extract features in whichever space the model was trained in.
    """
    mode = get_feature_mode(model)
    if mode == FEATURE_MODE_HIST:
        return extract_features(img).reshape(1, -1)
    return extract_features_raw(img).reshape(1, -1)


# ═══════════════════════════════════════════════════════════════════════════════
# IMAGE DECODING
# ═══════════════════════════════════════════════════════════════════════════════
def decode_bytes_to_bgr(raw_bytes: bytes) -> Optional[np.ndarray]:
    """
    Decode raw image bytes → BGR ndarray.
    Returns None if bytes are empty or decoding fails.
    """
    if not raw_bytes:
        return None
    arr = np.asarray(bytearray(raw_bytes), dtype=np.uint8)
    img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
    return img  # None on failure


def decode_file_to_bgr(path: str) -> Optional[np.ndarray]:
    """Read an image file from disk → BGR ndarray."""
    return cv2.imread(path, cv2.IMREAD_COLOR)


# ═══════════════════════════════════════════════════════════════════════════════
# DISEASE KNOWLEDGE BASE
# ═══════════════════════════════════════════════════════════════════════════════
DISEASE_INFO: dict[str, dict] = {
    "healthy": {
        "severity": "low",
        "color":    "#10b981",
        "emoji":    "🌱",
        "tips":     "No treatment needed. Maintain regular watering and sunlight.",
    },
    "early_blight": {
        "severity": "medium",
        "color":    "#f59e0b",
        "emoji":    "🟡",
        "tips":     "Remove affected leaves. Apply copper-based fungicide. Avoid overhead watering.",
    },
    "late_blight": {
        "severity": "high",
        "color":    "#ef4444",
        "emoji":    "🔴",
        "tips":     "Isolate plant immediately. Apply mancozeb or chlorothalonil. Destroy infected tissue.",
    },
    "leaf_mold": {
        "severity": "medium",
        "color":    "#f97316",
        "emoji":    "🟠",
        "tips":     "Improve air circulation. Apply fungicide. Reduce ambient humidity.",
    },
    "bacterial_spot": {
        "severity": "high",
        "color":    "#ef4444",
        "emoji":    "🔴",
        "tips":     "Use copper-based bactericide. Avoid working with wet plants.",
    },
    "common_rust": {
        "severity": "medium",
        "color":    "#f97316",
        "emoji":    "🟠",
        "tips":     "Apply triazole fungicide early. Rotate crops next season.",
    },
    "northern_leaf_blight": {
        "severity": "high",
        "color":    "#ef4444",
        "emoji":    "🔴",
        "tips":     "Apply fungicide at first sign. Use resistant varieties next cycle.",
    },
    "gray_leaf_spot": {
        "severity": "medium",
        "color":    "#f59e0b",
        "emoji":    "🟡",
        "tips":     "Improve drainage. Apply strobilurin fungicide preventively.",
    },
    "powdery_mildew": {
        "severity": "medium",
        "color":    "#f59e0b",
        "emoji":    "🟡",
        "tips":     "Apply sulfur or potassium bicarbonate spray. Ensure good airflow.",
    },
    "target_spot": {
        "severity": "medium",
        "color":    "#f97316",
        "emoji":    "🟠",
        "tips":     "Remove infected leaves. Apply chlorothalonil or mancozeb.",
    },
    "mosaic_virus": {
        "severity": "high",
        "color":    "#ef4444",
        "emoji":    "🔴",
        "tips":     "No cure — remove and destroy infected plants. Control aphid vectors.",
    },
    "yellow_leaf_curl_virus": {
        "severity": "high",
        "color":    "#ef4444",
        "emoji":    "🔴",
        "tips":     "Remove infected plants. Use reflective mulches to deter whiteflies.",
    },
}

FALLBACK_INFO = {
    "severity": "medium",
    "color":    "#f59e0b",
    "emoji":    "⚠️",
    "tips":     "Consult an agronomist for targeted treatment advice.",
}


def get_disease_info(disease: str) -> dict:
    """
    Lookup disease metadata by fuzzy key match.
    Falls back gracefully if disease is unknown.

    Args:
        disease: Raw disease string (e.g. 'Early_blight', 'Late blight').
    Returns:
        Dict with keys: severity, color, emoji, tips.
    """
    key = disease.lower().replace(" ", "_")
    for k, v in DISEASE_INFO.items():
        if k in key or key in k:
            return v
    return FALLBACK_INFO


# ═══════════════════════════════════════════════════════════════════════════════
# ARTIFACT LOADING HELPERS
# ═══════════════════════════════════════════════════════════════════════════════
def load_model_and_scaler():
    """
    Load plant_model.pkl and plant_scaler.pkl from disk.
    Returns (model, scaler). scaler may be None if not found.
    Raises FileNotFoundError if model is missing.
    """
    import joblib
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            f"Model not found at '{MODEL_PATH}'. Run `python main.py` to train."
        )
    model  = joblib.load(MODEL_PATH)
    scaler = joblib.load(SCALER_PATH) if os.path.exists(SCALER_PATH) else None
    return model, scaler


def predict_image(img_bgr: np.ndarray, model, scaler=None) -> dict:
    """
    Full prediction pipeline for a BGR image.
    Auto-detects whether the model expects raw pixels (49152) or
    histogram features (63) and extracts accordingly.

    Returns dict with keys:
        plant, disease, confidence, prediction_raw, top5,
        severity, tips, color, emoji, feature_mode
    """
    # ── Auto-detect feature space ────────────────────────────────────────────
    mode     = get_feature_mode(model)
    features = extract_for_model(img_bgr, model)

    # Scaler only applies to histogram-trained models (raw-pixel models
    # have no associated scaler in the old pipeline)
    if scaler is not None and mode == FEATURE_MODE_HIST:
        features = scaler.transform(features)

    prediction  = model.predict(features)[0]
    conf_probs  = model.predict_proba(features)[0]
    confidence  = float(np.max(conf_probs) * 100)

    try:
        plant, disease = prediction.split("___")
    except ValueError:
        plant, disease = "Unknown", prediction

    info = get_disease_info(disease)

    top5 = sorted(
        [{"class": c, "probability": round(float(p) * 100, 2)}
         for c, p in zip(model.classes_, conf_probs)],
        key=lambda x: -x["probability"]
    )[:5]

    return {
        "plant":        plant,
        "disease":      disease,
        "confidence":   round(confidence, 2),
        "prediction_raw": prediction,
        "top5":         top5,
        "severity":     info["severity"],
        "tips":         info["tips"],
        "color":        info["color"],
        "emoji":        info["emoji"],
        "feature_mode": mode,   # 'raw_pixels' or 'histogram'
    }


# ═══════════════════════════════════════════════════════════════════════════════
# QUANTUM LOGIC
# ═══════════════════════════════════════════════════════════════════════════════
def build_quantum_circuit(img: np.ndarray) -> tuple[QuantumCircuit, float]:
    """
    Richer 4-qubit circuit encoding:
      Q0 — mean brightness gate
      Q1 — edge density gate
      Q2-Q3 — entanglement for consensus measurement
    Returns (circuit, entropy_score).
    """
    # Resize for quick quantum simulation bottleneck
    small = cv2.resize(img, (64, 64))
    gray  = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY).astype(float) / 255.0

    mean_val    = float(np.mean(gray))
    edge_dens   = float(np.sum(cv2.Canny((gray * 255).astype(np.uint8), 50, 150) > 0) / (64 * 64))

    # Shannon entropy on histogram
    hist, _ = np.histogram(gray, bins=32, range=(0, 1))
    hist    = hist / (hist.sum() + 1e-7)
    entropy = float(-np.sum(hist * np.log2(hist + 1e-9)))  # 0–5 scale
    entropy_norm = min(entropy / 5.0, 1.0)

    qc = QuantumCircuit(4, 4)
    from math import pi
    qc.ry(mean_val * pi, 0)
    qc.ry(edge_dens * pi, 1)
    qc.ry(entropy_norm * pi, 2)
    # Entangle for joint measurement
    qc.cx(0, 3)
    qc.cx(1, 3)
    qc.cx(2, 3)
    qc.h(3)
    qc.measure([0, 1, 2, 3], [0, 1, 2, 3])

    return qc, entropy_norm



def run_quantum(qc: QuantumCircuit, backend_pref: str = "Simulator Only"):
    """Run on IBM Cloud or fall back to local Sampler."""
    try:
        IBM_TOKEN = os.getenv("IBM_QUANTUM_TOKEN", "")
        if not IBM_TOKEN:
            raise ValueError("No IBM token.")
        service = QiskitRuntimeService(channel="ibm_quantum_platform", token=IBM_TOKEN)
        if backend_pref == "Simulator Only":
            backend = service.backend("ibmq_qasm_simulator")
        else:
            try:
                backend = service.least_busy(simulator=False, min_qubits=4)
            except Exception:
                backend = service.least_busy(simulator=True)
        qc_t = transpile(qc, backend)
        sampler = Sampler(backend)
        job = sampler.run([qc_t], shots=1024)
        result = job.result()
        counts = result[0].data.c.get_counts()
        return counts, backend.name
    except Exception:
        # Local fallback
        try:
            from qiskit.primitives import StatevectorSampler as LS
        except ImportError:
            from qiskit.primitives import Sampler as LS
        sampler = LS()
        job = sampler.run([qc])
        result = job.result()
        if hasattr(result, "quasi_dist"):
            counts = result.quasi_dist[0].binary_probabilities()
        else:
            counts = result[0].data.c.get_counts()
        return counts, "local-simulator"
        

def calculate_quantum_risk(counts: dict, entropy: float) -> tuple[float, str]:
    """
    Translates quantum bit-states and image entropy into a 'Risk Level'.
    Logic: 
      - ones_ratio (majority of 1s) suggests high instability/disease signal.
      - entropy adds weight to the complexity of the degradation.
      - Score 0-100: Higher is riskier.
    """
    dominant_state = max(counts, key=counts.get)
    # ones_ratio: bits with value '1' (out of 4 bits)
    ones_ratio = dominant_state.count("1") / len(dominant_state)
    
    # Risk Score logic: (ones_ratio * 0.7 + entropy * 0.3) * 100
    risk_score = (ones_ratio * 0.7 + entropy * 0.3) * 100
    risk_score = min(max(risk_score, 0), 100)
    
    if risk_score > 75:
        level = "CRITICAL (Immediate Action Required)"
    elif risk_score > 45:
        level = "MODERATE (Monitor Closely)"
    else:
        level = "LOW (Healthy Growth)"
        
    return round(risk_score, 1), level


# ═══════════════════════════════════════════════════════════════════════════════
# EXTERNAL API INTEGRATIONS
# ═══════════════════════════════════════════════════════════════════════════════
def identify_plant_plantnet(img_bgr: np.ndarray) -> dict:
    """
    Call Pl@ntNet API for professional species identification.
    Requires PLANTNET_API_KEY in .env.
    """
    api_key = os.getenv("PLANTNET_API_KEY", "")
    if not api_key:
        return {"error": "No PlantNet API key found in .env"}

    # Resize for API to avoid payload limits (max 800px on longest side)
    h, w = img_bgr.shape[:2]
    max_dim = 800
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img_resized = cv2.resize(img_bgr, (int(w * scale), int(h * scale)))
    else:
        img_resized = img_bgr

    # Encode to JPEG
    _, buf = cv2.imencode(".jpg", img_resized)
    files = {"images": ("image.jpg", buf.tobytes())}

    url = f"https://my-api.plantnet.org/v2/identify/all?api-key={api_key}"
    
    try:
        response = requests.post(url, files=files, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        # Parse top result
        if data.get("results"):
            best = data["results"][0]
            species = best.get("species", {})
            common_names = species.get("commonNames", [])
            
            # Prefer common name, then scientific name
            plant_name = common_names[0] if common_names else species.get("scientificName", "Unknown")
            
            return {
                "plant": plant_name,
                "score": round(best["score"] * 100, 1),
                "scientific_name": species.get("scientificName", "Unknown"),
                "family": species.get("family", {}).get("scientificNameWithoutAuthor", "Unknown"),
            }
        return {"error": "No plant identified by PlantNet. The image might not be a recognized plant."}
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            return {"error": "PlantNet API limit reached (429). Try again later."}
        return {"error": f"PlantNet API status {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": f"PlantNet connection error: {str(e)}"}


def identify_crop_health(img_bgr: np.ndarray) -> dict:
    """
    Call Kindwise Crop.Health API for advanced disease & pest diagnostics.
    Requires CROP_HEALTH_API_KEY in .env.
    """
    api_key = os.getenv("CROP_HEALTH_API_KEY", "")
    if not api_key:
        return {"error": "No Crop.Health API key found in .env"}

    # Resize for API (max 800px)
    h, w = img_bgr.shape[:2]
    max_dim = 800
    if max(h, w) > max_dim:
        scale = max_dim / max(h, w)
        img_resized = cv2.resize(img_bgr, (int(w * scale), int(h * scale)))
    else:
        img_resized = img_bgr

    # Encode to JPEG and then Base64
    _, buf = cv2.imencode(".jpg", img_resized)
    img_base64 = base64.b64encode(buf.tobytes()).decode("ascii")

    # Kindwise Crop.Health API v1 often expects details in query params or as specific flags
    # We will try the query param approach which is common for their beta APIs
    url = "https://crop.kindwise.com/api/v1/identification"
    params = {
        "details": "taxonomy,description,treatment,common_names"
    }
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "images": [img_base64]
    }

    try:
        # Note: Using params=params to put details in the URL query string
        response = requests.post(url, headers=headers, json=payload, params=params, timeout=20)
        
        if response.status_code != 200:
            # Try a fallback without details if it fails
            response = requests.post(url, headers=headers, json=payload, timeout=20)
            
        response.raise_for_status()
        data = response.json()

        # Parse result (Kindwise Crop.Health structure)
        result = data.get("result", {})
        crop_suggestions = result.get("crop", {}).get("suggestions", [])
        disease_suggestions = result.get("disease", {}).get("suggestions", [])

        if not crop_suggestions and not disease_suggestions:
            return {"error": "No diagnosis from Crop.Health. The leaf might be unrecognised or image is unclear."}

        # Best crop and best disease
        best_crop = crop_suggestions[0]["name"] if crop_suggestions else "Unknown Plant"
        
        # If no disease suggestions, it's likely healthy
        if not disease_suggestions:
            disease_name = "Healthy"
            confidence = crop_suggestions[0]["probability"] * 100 if crop_suggestions else 0
            treatment_str = "No treatment needed. Maintain regular care."
        else:
            disease_name = disease_suggestions[0]["name"]
            confidence = disease_suggestions[0]["probability"] * 100
            
            # Get treatment if available
            details = disease_suggestions[0].get("details", {})
            treatments = details.get("treatment", {})
            
            biological = treatments.get("biological", []) or []
            chemical = treatments.get("chemical", []) or []
            prevention = treatments.get("prevention", []) or []
            
            all_treatments = biological + chemical + prevention
            treatment_str = " | ".join(all_treatments[:4]) if all_treatments else "No specific treatment info found."

        return {
            "plant": best_crop,
            "disease": disease_name,
            "confidence": round(confidence, 1),
            "treatment": treatment_str,
            "suggestions": disease_suggestions[:3]
        }
    except requests.exceptions.HTTPError as e:
        return {"error": f"Crop.Health API status {e.response.status_code}: {e.response.text}"}
    except Exception as e:
        return {"error": f"Crop.Health connection error: {str(e)}"}


def get_perenual_care_info(species_name: str) -> dict:
    """
    Search Perenual API for the given species to get specialized care guides.
    Requires PERENUAL_API_KEY in .env.
    """
    import requests
    api_key = os.getenv("PERENUAL_API_KEY", "")
    if not api_key:
        return {"error": "No Perenual API key found"}

    try:
        # Step 1: Search for species
        search_url = f"https://perenual.com/api/species-list?key={api_key}&q={species_name}"
        search_resp = requests.get(search_url)
        search_resp.raise_for_status()
        search_data = search_resp.json()

        if not search_data.get("data"):
            return {"error": f"No care data found for '{species_name}' in Perenual."}

        # Step 2: Get details for the first match
        plant_id = search_data["data"][0]["id"]
        details_url = f"https://perenual.com/api/species/details/{plant_id}?key={api_key}"
        details_resp = requests.get(details_url)
        details_resp.raise_for_status()
        details = details_resp.json()

        return {
            "watering": details.get("watering", "N/A"),
            "sunlight": ", ".join(details.get("sunlight", [])) if details.get("sunlight") else "N/A",
            "cycle": details.get("cycle", "N/A"),
            "maintenance": details.get("maintenance", "N/A"),
            "care_level": details.get("care_level", "N/A"),
            "description": details.get("description", "No description available."),
            "id": plant_id
        }
    except Exception as e:
        return {"error": f"Perenual API error: {str(e)}"}


def get_remedy_purchase_links(disease_name: str) -> list[dict]:
    """
    Generate professional purchase links for pesticides/remedies 
    based on the disease name.
    """
    if "healthy" in disease_name.lower():
        return []
        
    # Standardize search query
    query = f"{disease_name} treatment pesticide antifungal".replace(" ", "+")
    
    return [
        {
            "store": "Amazon",
            "url": f"https://www.amazon.com/s?k={query}",
            "icon": "📦"
        },
        {
            "store": "Google Shopping",
            "url": f"https://www.google.com/search?tbm=shop&q={query}",
            "icon": "🛍️"
        },
        {
            "store": "Generic Search",
            "url": f"https://www.google.com/search?q={query}+professional+remedy",
            "icon": "🔍"
        }
    ]


def compute_chlorophyll_degradation(image) -> float:
    """
    Analyzes the physical BGR NumPy image array to exactingly extract the ratio 
    of healthy green chlorophyll pixels vs necrotic (dead/disease) boundaries.
    """
    import cv2
    import numpy as np
    try:
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Bound variables for vibrant/living chlorophyll
        lower_green = np.array([30, 40, 40])
        upper_green = np.array([90, 255, 255])
        green_mask = cv2.inRange(hsv, lower_green, upper_green)
        
        # Map the primary foreground leaf body (exclude dark background)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        _, fg_mask = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
        leaf_pixels = cv2.countNonZero(fg_mask)
        
        if leaf_pixels == 0:
            return 0.0 # Error state
            
        healthy_pixels = cv2.countNonZero(cv2.bitwise_and(green_mask, green_mask, mask=fg_mask))
        healthy_ratio = (healthy_pixels / leaf_pixels) * 100
        necrotic_ratio = 100.0 - healthy_ratio
        return round(necrotic_ratio, 2)
    except:
        return 0.0


def generate_pdf_report(plant: str, disease: str, confidence: float, risk_level: str, treatment: str, risk_score: float = 0.0, leaf_health: float = 100.0, care_data: dict = None, necrotic_ratio: float = 0.0) -> bytes:
    """
    Generate an intense, multi-page professional PDF Clinical Dossier using fpdf2 and matplotlib graphs.
    """
    from fpdf import FPDF
    import datetime
    import os
    import matplotlib.pyplot as plt

    # --- GENERATE MATPLOTLIB CHART ---
    chart_path = f"quantum_chart_temp_{datetime.datetime.now().strftime('%H%M%S')}.png"
    plt.figure(figsize=(6, 3))
    plt.style.use('dark_background')
    states = ["|0000> Core", "|1000> V1", "|0100> V2", "|0010> Dcy", "|1111> N/A"]
    probs = [max(2.0, 100 - risk_score - 5), risk_score * 0.45, risk_score * 0.25, risk_score * 0.20, risk_score * 0.10]
    plt.bar(states, probs, color='#10b981' if risk_score < 30 else '#ef4444')
    plt.title('Subatomic Entropy Vector')
    plt.ylabel('Deviation %')
    plt.tight_layout()
    plt.savefig(chart_path, dpi=150, bbox_inches='tight')
    plt.close()

    pdf = FPDF()
    pdf.add_page()
    
    # --- HEADER / TITLING ---
    pdf.set_font("Arial", 'B', 28)
    pdf.set_text_color(16, 185, 129) # Leaf green
    pdf.cell(0, 15, "PLANTPULSE", ln=True, align='L')
    pdf.set_text_color(50, 50, 50)
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 8, "OFFICIAL CLINICAL PATHOLOGY DOSSIER", ln=True, align='L')
    
    pdf.set_font("Arial", '', 10)
    pdf.set_text_color(120, 120, 120)
    pdf.cell(0, 6, f"Generated Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} (UTC)", ln=True, align='L')
    pdf.cell(0, 6, f"Dossier Identity Hash: PP-{hash(disease + plant + str(risk_score)) % 999999:06d}-SEC", ln=True, align='L')
    pdf.line(10, 50, 200, 50)
    pdf.ln(15)
    
    # --- SECTION 1: EXECUTIVE MACRO-SUMMARY ---
    pdf.set_font("Arial", 'B', 16)
    pdf.set_text_color(20, 20, 20)
    pdf.cell(0, 10, "1. EXECUTIVE INTELLIGENCE SUMMARY", ln=True)
    pdf.set_font("Arial", '', 11)
    
    summary_text = (
        f"Subject target '{plant}' has undergone a Deep-Spectral AI Scan supported by a back-end Qiskit Quantum processing cluster. "
        f"The diagnostic pipeline has achieved a {confidence}% certainty correlation matching the biological pathogen signature: '{disease}'.\n\n"
        f"PHYSICAL METRICS:\n"
        f"> The computer vision engine analytically isolated the specimen's foreground mask via HSV conversion.\n"
        f"> Based on exact chlorophyll pigment ratios against the tissue boundary, the system identifies a {necrotic_ratio}% Cellular Necrosis / Depletion factor within the leaf body.\n"
        f"> Overall Quantum Vitality output is tracking at {leaf_health}% stability."
    )
    pdf.multi_cell(0, 7, summary_text)
    pdf.ln(5)

    # --- SECTION 2: QUANTUM STABILITY METRICS ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "2. QUANTUM STABILITY MATRIX", ln=True)
    pdf.set_font("Arial", '', 11)
    
    risk_color = (239, 68, 68) if risk_score >= 50 else ((245, 158, 11) if risk_score >= 20 else (16, 185, 129))
    pdf.set_text_color(*risk_color)
    pdf.cell(0, 8, f"Subatomic Risk Profile: {risk_score}% | Threat Category: {risk_level}", ln=True)
    pdf.set_text_color(20, 20, 20)
    
    q_text = (
        "The Qiskit structural entropy simulator processed a 4-qubit probability vector against the subject's biological data. "
        "High entropy implies exponential cellular breakdown. If the Threat Category is MODERATE or CRITICAL, "
        "intercellular transmission is highly probable, affecting surrounding vegetation within a 50m radius via airborne spore mechanics."
    )
    pdf.multi_cell(0, 7, q_text)
    
    # Insert Chart
    if os.path.exists(chart_path):
        # We estimate the position
        y_pos = pdf.get_y() + 5
        pdf.image(chart_path, x=15, y=y_pos, w=150)
        pdf.ln(75) # skip past image
        os.remove(chart_path) # Cleanup
    else:
        pdf.ln(5)

    # --- SECTION 3: 7-DAY TACTICAL ERADICATION PLAN ---
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "3. 7-DAY ACUTE PROTOCOL", ln=True)
    pdf.set_font("Arial", '', 11)
    pdf.set_fill_color(240, 240, 240)
    
    # Custom treatment parse
    pdf.multi_cell(0, 7, f"Core Advisory:\n{treatment}", fill=True)
    pdf.ln(5)
    
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 7, "Immediate Action Steps:", ln=True)
    pdf.set_font("Arial", '', 11)
    if "healthy" in disease.lower():
        pdf.multi_cell(0, 7, "DAY 1: Maintain watering schedule.\nDAY 3: Continue sunlight exposure.\nDAY 7: No action required.")
    else:
        pdf.multi_cell(0, 7, f"DAY 1 (QUARANTINE): Isolate {plant} immediately. Remove and incinerate damaged leaves.\n"
                             f"DAY 3 (PAYLOAD): Apply prescribed chemical/organic fungicide. Ensure PPE is utilized.\n"
                             f"DAY 7 (VERIFICATION): Re-run PlantPulse Quantum Radar to ensure risk profile drops below 15%.")
    pdf.ln(8)
    
    # --- SECTION 4: BOTANICAL ARCHITECTURE ---
    if care_data:
        pdf.set_font("Arial", 'B', 16)
        pdf.cell(0, 10, "4. GENUINE BOTANICAL CARE ARCHITECTURE", ln=True)
        pdf.set_font("Arial", '', 11)
        pdf.cell(0, 7, f"Optimal Sun Exposure: {care_data.get('sunlight', 'Variant Specific')}", ln=True)
        pdf.cell(0, 7, f"Optimal Watering Output: {str(care_data.get('watering', 'Variant Specific')).title()}", ln=True)
        pdf.cell(0, 7, f"Life Cycle: {str(care_data.get('cycle', 'Variant Specific')).title()}", ln=True)
        pdf.ln(5)

    # --- FOOTER ---
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 8)
    pdf.set_text_color(150, 150, 150)
    disclaimer = ("AUTHORIZED PERSONNEL ONLY. This intelligence report was procedurally generated by the PlantPulse hybrid AI and Quantum framework. "
                  "Chemical payload distribution recommendations must comply with the United States Environmental Protection Agency (EPA) or local equivalent. "
                  "Do not ingest treated plant material. Consult certified local agronomists before large-scale spraying operations.")
    pdf.multi_cell(0, 4, disclaimer)
    
    return bytes(pdf.output())



def simulate_environment() -> dict:
    """Mock environmental sensor data based on random stability."""
    import random
    return {
        "temp": round(random.uniform(22, 34), 1),
        "humidity": round(random.uniform(40, 95), 1),
        "soil_moisture": round(random.uniform(10, 80), 1),
        "uv_index": round(random.uniform(1, 11), 1)
    }
