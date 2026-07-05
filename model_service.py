import os
import base64
import logging
import numpy as np
from PIL import Image
import io
from flask import Blueprint, jsonify, request

logger = logging.getLogger("kisan_saathi")

model_bp = Blueprint("model", __name__)

MODEL_PATH = "crop_disease_model.h5"

# Lazy-loaded model global
_model = None

def get_model():
    global _model
    if _model is None:
        logger.info("Lazy-loading crop disease model...")
        try:
            if os.path.exists(MODEL_PATH):
                import tensorflow as tf
                _model = tf.keras.models.load_model(MODEL_PATH)
                logger.info(f"Crop disease model loaded successfully from {MODEL_PATH}.")
            else:
                logger.warning(f"Model file not found at {MODEL_PATH}. Leaf diagnosis will run in mock/fallback mode.")
        except Exception as e:
            logger.error(f"Error loading crop disease model: {e}")
    return _model

# Labels matching the model's indices 0-17 (16 PlantVillage + 2 Soybean classes)
class_labels = [
    'Pepper__bell___Bacterial_spot',
    'Pepper__bell___healthy',
    'PlantVillage',
    'Potato___Early_blight',
    'Potato___Late_blight',
    'Potato___healthy',
    'Tomato_Bacterial_spot',
    'Tomato_Early_blight',
    'Tomato_Late_blight',
    'Tomato_Leaf_Mold',
    'Tomato_Septoria_leaf_spot',
    'Tomato_Spider_mites_Two_spotted_spider_mite',
    'Tomato__Target_Spot',
    'Tomato__Tomato_YellowLeaf__Curl_Virus',
    'Tomato__Tomato_mosaic_virus',
    'Tomato_healthy',
    'Soybean_Bacterial_Pustule',   # index 16
    'Soybean_Healthy',             # index 17
]

# Bilingual mappings and expert recommendations
disease_details = {
    'Pepper__bell___Bacterial_spot': {
        'pesticides': ['Streptocycline (0.1g/L)', 'Copper Oxychloride (2g/L)'],
        'organic': ['Neem oil spray (1%)', 'Baking soda solution (10g/L)'],
        'schedule': 'Spray weekly in the early morning for 3 consecutive weeks.',
        'translations': {
            'en': {'crop': 'Pepper Bell', 'disease': 'Bacterial Spot', 'pesticide': 'Streptocycline (0.1g/L) + Copper Oxychloride (2g/L)'},
            'hi': {'crop': 'शिमला मिर्च', 'disease': 'जीवाणु धब्बा', 'pesticide': 'स्ट्रेप्टोसाइक्लिन (0.1 ग्राम/लीटर) + कॉपर ऑक्सीक्लोराइड (2 ग्राम/लीटर)'}
        }
    },
    'Pepper__bell___healthy': {
        'pesticides': [], 'organic': [], 'schedule': 'No treatment required.',
        'translations': {
            'en': {'crop': 'Pepper Bell', 'disease': 'Healthy', 'pesticide': 'None'},
            'hi': {'crop': 'शिमला मिर्च', 'disease': 'स्वस्थ', 'pesticide': 'None'}
        }
    },
    'PlantVillage': {
        'pesticides': [], 'organic': [], 'schedule': 'Monitor crop health.',
        'translations': {
            'en': {'crop': 'Unknown Crop', 'disease': 'Unknown Issue', 'pesticide': 'None'},
            'hi': {'crop': 'अज्ञात फसल', 'disease': 'अद्यात समस्या', 'pesticide': 'None'},
            'ta': {'crop': 'அறியப்படாத பயிர்', 'disease': 'அறியப்படாத பிரச்சனை', 'pesticide': 'ஏதுமில்லை'},
            'te': {'crop': 'తెలియని పంట', 'disease': 'తెలియని సమస్య', 'pesticide': 'ఏమీ లేదు'},
            'ur': {'crop': 'نامعلوم فصل', 'disease': 'نامعلوم مسئلہ', 'pesticide': 'کوئی نہیں'}
        }
    },
    'Potato___Early_blight': {
        'pesticides': ['Mancozeb (2g/L water)', 'Chlorothalonil'],
        'organic': ['Neem seed kernel extract (5%)', 'Copper hydroxide sprays'],
        'schedule': 'Apply at first sign of symptoms, repeat at 7-10 day intervals.',
        'translations': {
            'en': {'crop': 'Potato', 'disease': 'Early Blight', 'pesticide': 'Mancozeb (2g/L water), Chlorothalonil'},
            'hi': {'crop': 'आलू', 'disease': 'अगेती झुलसा', 'pesticide': 'मैनकोजेब (2 ग्राम/लीटर पानी) या क्लोरोथालोनिल'},
            'ta': {'crop': 'உருளைக்கிழங்கு', 'disease': 'ஆரம்பகால வெப்புநோய்', 'pesticide': 'மேன்கோசெப் அல்லது குளோரோதலோனில்'},
            'te': {'crop': 'బంగాళాదుంప', 'disease': 'అర్లీ బ్లైట్', 'pesticide': 'మాంకోజెబ్ లేదా క్లోరోథలోనిల్'},
            'ur': {'crop': 'آلو', 'disease': 'अगेتی झुलसा / Early Blight', 'pesticide': 'مینکوزیب یا کلوروتھالونل'}
        }
    },
    'Potato___Late_blight': {
        'pesticides': ['Metalaxyl + Mancozeb (Ridomil Gold)', 'Cymoxanil'],
        'organic': ['Bordeaux mixture (1%)', 'Trichoderma viride culture (5g/L)'],
        'schedule': 'Apply immediately under cool, cloudy conditions. Re-apply every 7 days.',
        'translations': {
            'en': {'crop': 'Potato', 'disease': 'Late Blight', 'pesticide': 'Metalaxyl + Mancozeb (Ridomil Gold), Cymoxanil'},
            'hi': {'crop': 'आलू', 'disease': 'पछैती झुलसा', 'pesticide': 'मेटालेक्सिल + मैनकोजेब या साइमोक्सानिल'}
        }
    },
    'Potato___healthy': {
        'pesticides': [], 'organic': [], 'schedule': 'No treatment required.',
        'translations': {
            'en': {'crop': 'Potato', 'disease': 'Healthy', 'pesticide': 'None'},
            'hi': {'crop': 'आलू', 'disease': 'स्वस्थ', 'pesticide': 'None'}
        }
    },
    'Tomato_Bacterial_spot': {
        'pesticides': ['Copper Oxychloride', 'Streptomycin sulfate'],
        'organic': ['Serenade ASO (Bacillus subtilis)', 'Compost tea sprays'],
        'schedule': 'Spray every 7-10 days during warm, humid conditions.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Bacterial Spot', 'pesticide': 'Copper Oxychloride, Streptomycin sulfate'},
            'hi': {'crop': 'टमाटर', 'disease': 'जीवाणु धब्बा', 'pesticide': 'कॉपर ऑक्सीक्लोराइड या स्ट्रेप्टोमाइसिन सल्फेट'}
        }
    },
    'Tomato_Early_blight': {
        'pesticides': ['Mancozeb', 'Chlorothalonil (Daconil)'],
        'organic': ['Baking soda spray', 'Potassium bicarbonate (5g/L)'],
        'schedule': 'Spray starting at leaf canopy closure, repeat every 10-14 days.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Early Blight', 'pesticide': 'Mancozeb, Chlorothalonil (Daconil)'},
            'hi': {'crop': 'टमाटर', 'disease': 'अगेती झुलसा', 'pesticide': 'मैनकोजेब या क्लोरोथालोनिल'},
            'ta': {'crop': 'தக்காளி', 'disease': 'ஆரம்பகால வெப்புநோய்', 'pesticide': 'மேன்கோசெப் அல்லது குளோரோதலோனில்'},
            'te': {'crop': 'టమోటా', 'disease': 'అర్లీ బ్లైట్', 'pesticide': 'మాంకోజెబ్ లేదా క్లోరోథలోనిల్'},
            'ur': {'crop': 'ٹماٹر', 'disease': 'अगेتی झुलसा / Early Blight', 'pesticide': 'مینکوزیب یا کلوروتھالونل'}
        }
    },
    'Tomato_Late_blight': {
        'pesticides': ['Metalaxyl + Mancozeb', 'Famoxadone'],
        'organic': ['Copper fungicides', 'Garlic extract spray'],
        'schedule': 'Apply immediately upon detection. Prune infected lower branches.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Late Blight', 'pesticide': 'Metalaxyl + Mancozeb, Famoxadone'},
            'hi': {'crop': 'टमाटर', 'disease': 'पछैती झुलसा', 'pesticide': 'मेटालेक्सिल + मैनकोजेब या फेमोक्साडोन'}
        }
    },
    'Tomato_Leaf_Mold': {
        'pesticides': ['Carbendazim', 'Chlorothalonil'],
        'organic': ['Improve greenhouse ventilation', 'Neem oil sprays'],
        'schedule': 'Spray lower and upper leaf surfaces thoroughly every 7 days.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Leaf Mold', 'pesticide': 'Carbendazim, Chlorothalonil'},
            'hi': {'crop': 'टमाटर', 'disease': 'पत्ती मोल्ड', 'pesticide': 'कार्बेन्डाजिम या क्लोरोथालोनिल'}
        }
    },
    'Tomato_Septoria_leaf_spot': {
        'pesticides': ['Mancozeb', 'Propiconazole'],
        'organic': ['Mulching soil to prevent spore splash', 'Copper soaps'],
        'schedule': 'Apply fungicide at first spot detection, repeat every 7-10 days.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Septoria Leaf Spot', 'pesticide': 'Mancozeb, Propiconazole'},
            'hi': {'crop': 'टमाटर', 'disease': 'सेप्टोरिया पत्ती धब्बा', 'pesticide': 'मैनकोजेब या प्रोपिकोनाज़ोल'}
        }
    },
    'Tomato_Spider_mites_Two_spotted_spider_mite': {
        'pesticides': ['Abamectin', 'Dicofol'],
        'organic': ['Spynosaad', 'Insecticidal soap wash', 'Neem oil (1.5%)'],
        'schedule': 'Apply miticides/soap wash focusing on underside of leaves.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Spider Mites', 'pesticide': 'Abamectin, Dicofol'},
            'hi': {'crop': 'टमाटर', 'disease': 'मकड़ी घुन', 'pesticide': 'एबामेक्टिन या डिकोफोल'}
        }
    },
    'Tomato__Target_Spot': {
        'pesticides': ['Chlorothalonil', 'Mancozeb'],
        'organic': ['Prune lower leaves', 'Bacillus subtilis bio-fungicide'],
        'schedule': 'Apply fungicides at 10-day intervals during wet weather.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Target Spot', 'pesticide': 'Chlorothalonil, Mancozeb'},
            'hi': {'crop': 'टमाटर', 'disease': 'लक्षित धब्बा', 'pesticide': 'क्लोरोथालोनिल या मैनकोजेब'}
        }
    },
    'Tomato__Tomato_YellowLeaf__Curl_Virus': {
        'pesticides': ['Imidacloprid (for whiteflies)', 'Acetamiprid'],
        'organic': ['Yellow sticky cards', 'Neem oil to deter whiteflies'],
        'schedule': 'Control whitefly vector populations early in the morning.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Yellow Leaf Curl Virus', 'pesticide': 'Imidacloprid (for whiteflies), Acetamiprid'},
            'hi': {'crop': 'टमाटर', 'disease': 'पीला पत्ती मरोड़ वायरस', 'pesticide': 'इमिडाक्लोप्रिड या एसिटामिप्रिड'}
        }
    },
    'Tomato__Tomato_mosaic_virus': {
        'pesticides': ['Dimethoate (for aphid vector)'],
        'organic': ['Remove infected plants immediately', 'Sanitize tools in milk'],
        'schedule': 'Practice vector control and plant resistant varieties.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Mosaic Virus', 'pesticide': 'Dimethoate (for aphid vector)'},
            'hi': {'crop': 'टमाटर', 'disease': 'मोज़ेक वायरस', 'pesticide': 'डाइमेथोएट'}
        }
    },
    'Tomato_healthy': {
        'pesticides': [], 'organic': [], 'schedule': 'No treatment required.',
        'translations': {
            'en': {'crop': 'Tomato', 'disease': 'Healthy', 'pesticide': 'None'},
            'hi': {'crop': 'टमाटर', 'disease': 'स्वस्थ', 'pesticide': 'None'}
        }
    },
    'Soybean_Bacterial_Pustule': {
        'pesticides': ['Copper Oxychloride (2g/L)', 'Mancozeb (2g/L)'],
        'organic': ['Neem oil spray (1%)', 'Trichoderma-based bio-fungicide'],
        'schedule': 'Spray at first signs of pustule formation, repeat every 10 days.',
        'translations': {
            'en': {'crop': 'Soybean', 'disease': 'Bacterial Pustule', 'pesticide': 'Copper Oxychloride (2g/L), Mancozeb (2g/L)'},
            'hi': {'crop': 'सोयाबीन', 'disease': 'जीवाणु फुंसी', 'pesticide': 'कॉपर ऑक्सीक्लोराइड (2 ग्राम/लीटर) या मैनकोजेब (2 ग्राम/लीटर)'}
        }
    },
    'Soybean_Healthy': {
        'pesticides': [], 'organic': [], 'schedule': 'No treatment required.',
        'translations': {
            'en': {'crop': 'Soybean', 'disease': 'Healthy', 'pesticide': 'None'},
            'hi': {'crop': 'सोयाबीन', 'disease': 'स्वस्थ', 'pesticide': 'कोई आवश्यकता नहीं'}
        }
    },
}

def get_severity(confidence):
    if confidence < 0.4:
        return "Low"
    elif confidence < 0.7:
        return "Medium"
    else:
        return "High"

def get_translation(best_meta, lang):
    if 'translations' not in best_meta:
        return {
            'crop': best_meta.get('crop', 'Unknown'),
            'disease': best_meta.get('disease', 'Unknown'),
            'pesticide': ", ".join(best_meta.get('pesticides', [])) if best_meta.get('pesticides') else "None"
        }
    if lang in best_meta['translations']:
        return best_meta['translations'][lang]
        
    # Translate using Gemini once and cache
    import google.generativeai as genai
    from language_config import LANGUAGES
    lang_info = LANGUAGES.get(lang, LANGUAGES["hi"])
    lang_name = lang_info["name"]
    
    translations = {}
    for key, english_text in best_meta['translations']['en'].items():
        if not english_text or english_text.lower() in ["none", "unknown", "healthy", "need not / none", "आवश्यकता नहीं / none"]:
            translations[key] = english_text
            continue
        try:
            model_g = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"Translate the agricultural term '{english_text}' into {lang_name}. Return ONLY the direct translation, nothing else."
            response = model_g.generate_content(prompt)
            if response and response.text:
                translations[key] = response.text.strip()
            else:
                translations[key] = english_text
        except Exception as e:
            logger.error(f"Gemini translation error for '{english_text}' to {lang_name}: {e}")
            translations[key] = english_text
            
    best_meta['translations'][lang] = translations
    return translations

@model_bp.route("/api/scan", methods=["POST"])
def scan_crop():
    # 1. Parse Input: JSON base64 or Multipart image upload
    img_bytes = None
    mode = "disease"
    lang = "hi"
    
    # Check if request has multipart files
    if 'image' in request.files:
        file = request.files['image']
        # Input validation: reject non-image files, files < 50KB
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.webp')):
            return jsonify({"success": False, "error": "Invalid file format. Upload an image.", "verified": False})
        
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        
        if size < 50 * 1024:
            return jsonify({"success": False, "error": "Image file too small (must be > 50KB for proper leaf scan).", "verified": False})
            
        img_bytes = file.read()
        mode = request.form.get("mode", "disease")
        lang = request.form.get("lang", "hi")
        
    else:
        # JSON base64 parser
        req_data = request.get_json()
        if not req_data or "image" not in req_data:
            return jsonify({"success": False, "error": "No image payload provided", "verified": False})
            
        base64_img = req_data["image"]
        mode = req_data.get("mode", "disease")
        lang = req_data.get("lang", "hi")
        
        # Decode base64
        try:
            if "," in base64_img:
                base64_img = base64_img.split(",")[1]
            img_bytes = base64.b64decode(base64_img)
        except Exception as e:
            return jsonify({"success": False, "error": f"Invalid base64 encoding: {e}", "verified": False})
            
        if len(img_bytes) < 50 * 1024:
            return jsonify({"success": False, "error": "Captured frame contains insufficient details (<50KB). Please hold leaf closer.", "verified": False})

    # Redirect to QR code validation route if mode is 'qrcode'
    if mode == "qrcode":
        try:
            import cv2
            nparr = np.frombuffer(img_bytes, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            detector = cv2.QRCodeDetector()
            product_id, bbox, _ = detector.detectAndDecode(frame)
            if product_id:
                # Import verification logic locally or forward
                from firebase_service import verify_qr
                # Call local Firestore verify handler internally
                # Mock a request-like JSON context
                class DummyRequest:
                    def get_json(self):
                        return {"qr_data": product_id}
                # Simulate endpoint call
                import flask
                from flask import Response
                with flask.current_app.test_request_context(json={"qr_data": product_id}):
                    from firebase_service import verify_qr
                    return verify_qr()
            else:
                return jsonify({"success": False, "error": "No QR Code detected in image. Ensure clean lighting.", "message_hi": "छवि में कोई क्यूआर कोड नहीं मिला"})
        except Exception as e:
            logger.error(f"Error executing QR scanning logic: {e}")
            return jsonify({"success": False, "error": str(e)})

    # 2. Run Disease Classification
    try:
        # Load image via PIL
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        
        # Preprocess to 224x224 RGB as requested by Task 4
        img_224 = img.resize((224, 224))
        
        model = get_model()
        if model is None:
            return jsonify({
                "success": False,
                "error": "The TensorFlow crop disease classification model is currently unavailable on the backend. Verification could not be run.",
                "verified": False
            }), 503
            
        # Model expects 128x128 input shape. Resize from 224x224 to 128x128
        img_128 = img_224.resize((128, 128))
        img_arr = np.array(img_128) / 255.0
        img_expanded = np.expand_dims(img_arr, axis=0)
        
        # Run inference
        predictions = model.predict(img_expanded)[0]
        top_indices = np.argsort(predictions)[::-1][:3]
        
        top_predictions = []
        for idx in top_indices:
            label = class_labels[idx]
            conf = float(predictions[idx])
            meta = disease_details.get(label, {
                'disease': label, 'crop': 'Unknown'
            })
            crop_name = meta['translations']['en']['crop'] if 'translations' in meta else meta.get('crop', 'Unknown')
            disease_name = meta['translations']['en']['disease'] if 'translations' in meta else meta.get('disease', 'Unknown')
            top_predictions.append({
                "disease_name": f"{crop_name} - {disease_name}",
                "confidence": round(conf, 4),
                "severity": get_severity(conf)
            })
            
        # Get top-1 prediction meta
        best_label = class_labels[top_indices[0]]
        best_meta = disease_details[best_label]
        best_conf = float(predictions[top_indices[0]])
        
        trans = get_translation(best_meta, lang)
        
        return jsonify({
            "success": True,
            "crop": best_meta['translations']['en']['crop'],
            "crop_hi": trans['crop'],
            "disease": best_meta['translations']['en']['disease'],
            "disease_hi": trans['disease'],
            "pesticide": trans['pesticide'],
            "severity": get_severity(best_conf),
            "recommended_pesticides": best_meta['pesticides'],
            "organic_alternatives": best_meta['organic'],
            "application_schedule": best_meta['schedule'],
            "predictions": top_predictions
        })
        
    except Exception as e:
        logger.error(f"Error during leaf scan inference: {e}")
        return jsonify({"success": False, "error": str(e), "verified": False})

