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
from typing import Optional
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, Sampler

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
    
    if risk_score > 70:
        level = "CRITICAL"
    elif risk_score > 40:
        level = "MODERATE"
    else:
        level = "LOW"
        
    return round(risk_score, 1), level


# ═══════════════════════════════════════════════════════════════════════════════
# EXTERNAL API INTEGRATIONS
# ═══════════════════════════════════════════════════════════════════════════════
def identify_plant_plantnet(img_bgr: np.ndarray) -> dict:
    """
    Call Pl@ntNet API for professional species identification.
    Requires PLANTNET_API_KEY in .env.
    """
    import requests
    import json

    api_key = os.getenv("PLANTNET_API_KEY", "")
    if not api_key:
        return {"error": "No PlantNet API key found in .env"}

    # Encode to JPEG
    _, buf = cv2.imencode(".jpg", img_bgr)
    files = {"images": ("image.jpg", buf.tobytes())}

    url = f"https://my-api.plantnet.org/v2/identify/all?api-key={api_key}"
    
    try:
        response = requests.post(url, files=files)
        response.raise_for_status()
        data = response.json()
        
        # Parse top result
        if data.get("results"):
            best = data["results"][0]
            return {
                "plant": best["species"]["commonNames"][0] if best["species"]["commonNames"] else best["species"]["scientificName"],
                "score": round(best["score"] * 100, 1),
                "scientific_name": best["species"]["scientificName"],
                "family": best["species"]["family"]["scientificNameWithoutAuthor"],
            }
        return {"error": "No plant identified by PlantNet."}
    except Exception as e:
        return {"error": f"PlantNet API error: {str(e)}"}


def identify_crop_health(img_bgr: np.ndarray) -> dict:
    """
    Call Kindwise Crop.Health API for advanced disease & pest diagnostics.
    Requires CROP_HEALTH_API_KEY in .env.
    """
    import requests
    import base64
    import json

    api_key = os.getenv("CROP_HEALTH_API_KEY", "")
    if not api_key:
        return {"error": "No Crop.Health API key found in .env"}

    # Encode to JPEG and then Base64
    _, buf = cv2.imencode(".jpg", img_bgr)
    img_base64 = base64.b64encode(buf.tobytes()).decode("ascii")

    url = "https://crop.kindwise.com/api/v1/identification"
    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }
    payload = {
        "images": [img_base64],
        "details": "taxonomy,description,treatment,common_names"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()

        # Parse result
        result = data.get("result", {})
        crop_suggestions = result.get("crop", {}).get("suggestions", [])
        disease_suggestions = result.get("disease", {}).get("suggestions", [])

        if not crop_suggestions and not disease_suggestions:
            return {"error": "No diagnosis from Crop.Health."}

        # Best crop and best disease
        best_crop = crop_suggestions[0]["name"] if crop_suggestions else "Unknown"
        best_disease = disease_suggestions[0]["name"] if disease_suggestions else "Healthy"
        confidence = disease_suggestions[0]["probability"] * 100 if disease_suggestions else (crop_suggestions[0]["probability"] * 100 if crop_suggestions else 0)

        # Get treatment if available
        details = disease_suggestions[0].get("details", {}) if disease_suggestions else {}
        treatment = details.get("treatment", {}).get("biological", []) + \
                    details.get("treatment", {}).get("chemical", []) + \
                    details.get("treatment", {}).get("prevention", [])
        
        treatment_str = " | ".join(treatment[:3]) if treatment else "No specific treatment info found."

        return {
            "plant": best_crop,
            "disease": best_disease,
            "confidence": round(confidence, 1),
            "treatment": treatment_str,
            "suggestions": disease_suggestions[:3]  # Return top 3 for UI
        }
    except Exception as e:
        return {"error": f"Crop.Health API error: {str(e)}"}
