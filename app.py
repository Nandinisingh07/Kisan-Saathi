from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, render_template, send_from_directory, session
from flask_session import Session
import os
import time
import glob
import base64
import io
import requests
import numpy as np
import pandas as pd
from PIL import Image
import cv2
from gtts import gTTS
import firebase_admin
from firebase_admin import credentials, firestore
import datetime

# Initialize Flask App
app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = "kisan_saathi_super_secret_key"
Session(app)

# Ensure folders exist
os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Conditional Firebase Initialization
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print("Firebase key initialization warning (Using local fallback):", e)
db = firestore.client()

# Load Keras Crop Disease Model once at startup
print("Loading crop disease model...")
try:
    import tensorflow as tf
    model = tf.keras.models.load_model("crop_disease_model.h5")
    print("Crop disease model loaded successfully!")
except Exception as e:
    model = None
    print("Warning: Failed to load crop_disease_model.h5 (Leaf diagnosis will use mock mode):", e)

# Load Pesticide dataset
PESTICIDE_CSV = "C:/Users/Nandini singh/Downloads/archive (2)/Datasets/Pesticide_Dataset/Pesticides.csv"
try:
    pesticide_df = pd.read_csv(PESTICIDE_CSV)
    pesticide_df['Disease'] = pesticide_df['Disease'].str.strip()
    print("Pesticide dataset loaded successfully.")
except Exception as e:
    pesticide_df = None
    print("Pesticide CSV not found (Using expert fallback rules):", e)

# 16 Crop disease class labels matching indices 0-15
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
    'Tomato_healthy'
]

# Bilingual mapping for classes
bilingual_classes = {
    'Pepper__bell___Bacterial_spot': {'crop': 'Pepper Bell', 'crop_hi': 'शिमला मिर्च', 'disease': 'Bacterial Spot', 'disease_hi': 'जीवाणु धब्बा', 'pesticide': 'Streptocycline (0.1g/L) + Copper Oxychloride (2g/L)'},
    'Pepper__bell___healthy': {'crop': 'Pepper Bell', 'crop_hi': 'शिमला मिर्च', 'disease': 'Healthy', 'disease_hi': 'स्वस्थ', 'pesticide': 'None (कोई कीटनाशक आवश्यक नहीं)'},
    'PlantVillage': {'crop': 'Unknown', 'crop_hi': 'अज्ञात फसल', 'disease': 'Unknown', 'disease_hi': 'अअज्ञात रोग', 'pesticide': 'None'},
    'Potato___Early_blight': {'crop': 'Potato', 'crop_hi': 'आलू', 'disease': 'Early Blight', 'disease_hi': 'अगेती झुलसा', 'pesticide': 'Mancozeb (2g/L water) or Copper Oxychloride'},
    'Potato___Late_blight': {'crop': 'Potato', 'crop_hi': 'आलू', 'disease': 'Late Blight', 'disease_hi': 'पछैती झुलसा', 'pesticide': 'Metalaxyl + Mancozeb (Ridomil Gold)'},
    'Potato___healthy': {'crop': 'Potato', 'crop_hi': 'आलू', 'disease': 'Healthy', 'disease_hi': 'स्वस्थ', 'pesticide': 'None (कोई कीटनाशक आवश्यक नहीं)'},
    'Tomato_Bacterial_spot': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Bacterial Spot', 'disease_hi': 'जीवाणु धब्बा', 'pesticide': 'Streptocycline + Copper Oxychloride'},
    'Tomato_Early_blight': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Early Blight', 'disease_hi': 'अगेती झुलसा', 'pesticide': 'Mancozeb or Chlorothalonil'},
    'Tomato_Late_blight': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Late Blight', 'disease_hi': 'पछैती झुलसा', 'pesticide': 'Metalaxyl + Mancozeb (Ridomil)'},
    'Tomato_Leaf_Mold': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Leaf Mold', 'disease_hi': 'पत्ती मोल्ड', 'pesticide': 'Carbendazim or Chlorothalonil'},
    'Tomato_Septoria_leaf_spot': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Septoria Leaf Spot', 'disease_hi': 'सेप्टोरिया पत्ती धब्बा', 'pesticide': 'Mancozeb or Propiconazole'},
    'Tomato_Spider_mites_Two_spotted_spider_mite': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Spider Mites', 'disease_hi': 'मकड़ी घुन (Spider Mites)', 'pesticide': 'Abamectin or Dicofol'},
    'Tomato__Target_Spot': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Target Spot', 'disease_hi': 'लक्षित धब्बा', 'pesticide': 'Chlorothalonil or Mancozeb'},
    'Tomato__Tomato_YellowLeaf__Curl_Virus': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Yellow Leaf Curl Virus', 'disease_hi': 'पीला पत्ती मरोड़ वायरस', 'pesticide': 'Imidacloprid (to control whitefly vector)'},
    'Tomato__Tomato_mosaic_virus': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Mosaic Virus', 'disease_hi': 'मोज़ेक वायरस', 'pesticide': 'Dimethoate (to control aphid vectors)'},
    'Tomato_healthy': {'crop': 'Tomato', 'crop_hi': 'टमाटर', 'disease': 'Healthy', 'disease_hi': 'स्वस्थ', 'pesticide': 'None (कोई कीटनाशक आवश्यक नहीं)'}
}

# Weather Translation Fallback
weather_translations = {
    'clear sky': 'साफ आकाश',
    'few clouds': 'कम बादल',
    'scattered clouds': 'बिखरे बादल',
    'broken clouds': 'टूटे बादल',
    'shower rain': 'बोछारें',
    'rain': 'बारिश',
    'thunderstorm': 'आंधी-तूफान',
    'snow': 'बर्फबारी',
    'mist': 'कोहरा',
    'haze': 'धुंध',
    'overcast clouds': 'घने बादल',
    'light rain': 'हल्की बारिश',
    'moderate rain': 'सामान्य बारिश',
    'heavy intensity rain': 'भारी वर्षा'
}

# Simulated IVR helpline database
ivr_logs = [
    {"caller": "+91 99999 XXX99", "path": "Hindi -> Mandi (Press 2)", "duration": "1m 24s", "time": "15:10", "audio_url": "/static/audio/mandi_hi.mp3"},
    {"caller": "+91 94250 XXX41", "path": "Hindi -> Weather (Press 3)", "duration": "0m 45s", "time": "14:42", "audio_url": "/static/audio/weather_hi.mp3"},
    {"caller": "+91 88710 XXX12", "path": "English -> Crop Input (Press 4)", "duration": "2m 10s", "time": "12:15", "audio_url": "/static/audio/crop_en.mp3"}
]

# Generate baseline IVR assets if missing
def build_ivr_mock_audio():
    try:
        # Mandi Hi
        f1 = "static/audio/mandi_hi.mp3"
        if not os.path.exists(f1):
            gTTS("गेहूं का औसत मंडी भाव 2350 रुपये प्रति क्विंटल है।", lang='hi').save(f1)
        # Weather Hi
        f2 = "static/audio/weather_hi.mp3"
        if not os.path.exists(f2):
            gTTS("आज मौसम साफ रहेगा, तापमान 32 डिग्री सेल्सियस रहने की संभावना है।", lang='hi').save(f2)
        # Crop En
        f3 = "static/audio/crop_en.mp3"
        if not os.path.exists(f3):
            gTTS("You selected Potato. Press 5 for disease advice.", lang='en').save(f3)
    except Exception as e:
        print("Muting baseline audio compilation warning", e)

build_ivr_mock_audio()

def clean_old_audio():
    """Delete audio files in static/audio folder older than 5 minutes to prevent storage bloat."""
    try:
        now = time.time()
        for f in glob.glob("static/audio/chat_reply_*.mp3"):
            if os.stat(f).st_mtime < now - 300:
                os.remove(f)
    except Exception as e:
        print("Audio clean failed:", e)

# === PAGE ROUTERS ===
@app.route("/")
def index():
    return render_template("index.html", active_page="dashboard")

@app.route("/scan")
def scan_page():
    return render_template("scan.html", active_page="scan")

@app.route("/market")
def market_page():
    return render_template("market.html", active_page="market")

@app.route("/chat")
def chat_page():
    return render_template("chat.html", active_page="chat")

@app.route("/ivr")
def ivr_page():
    return render_template("ivr.html", active_page="ivr")

@app.route("/settings")
def settings_page():
    return render_template("settings.html", active_page="settings")

# Serve QR codes directly from root
@app.route("/product_qr/<path:filename>")
def serve_qr(filename):
    return send_from_directory(".", filename)

# === API ENDPOINTS ===

# Weather API
@app.route("/api/weather")
def get_weather_api():
    city = request.args.get("city", "Indore")
    lang = request.args.get("lang", "hi")
    api_key = os.getenv("OPENWEATHER_API_KEY")
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url)
        data = res.json()
        if res.status_code == 200:
            weather_desc = data["weather"][0]["description"]
            
            # Map dynamic description translations
            if lang == "en":
                desc_translated = weather_desc.capitalize()
            elif lang == "hi":
                desc_translated = weather_translations.get(weather_desc.lower(), weather_desc).capitalize()
            else:
                try:
                    from googletrans import Translator
                    translator = Translator()
                    desc_translated = translator.translate(weather_desc, src='en', dest=lang).text.capitalize()
                except Exception as e:
                    desc_translated = weather_translations.get(weather_desc.lower(), weather_desc).capitalize()

            return jsonify({
                "success": True,
                "temp": data["main"]["temp"],
                "desc": weather_desc.capitalize(),
                "desc_hi": desc_translated,
                "main_desc": data["weather"][0]["main"],
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"]
            })
        else:
            return jsonify({"success": False, "error": data.get("message", "City not found")})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Mandi Market price tracking and suggestions
@app.route("/api/market")
def get_market_data():
    state = request.args.get("state", "Madhya Pradesh")
    district = request.args.get("district", "Indore")
    land_type = request.args.get("land_type", "other")

    try:
        # Load local prices CSV
        df = pd.read_csv("mandi_prices.csv")
        # Filter by state and district
        filtered = df[(df["state"].str.lower() == state.lower()) & (df["district"].str.lower() == district.lower())]
        
        # Calculate crop average (modal) prices
        filtered["modal_price"] = pd.to_numeric(filtered["modal_price"], errors="coerce")
        avg_prices = filtered.groupby("commodity")["modal_price"].mean().to_dict()
        
        # Crop Recommendation Logic
        profitable = filtered.groupby("commodity")["modal_price"].mean().sort_values(ascending=False)
        dry_crops = ["Bajra", "Moong", "Urad", "Chana", "Masoor", "Soyabean"]
        wet_crops = ["Rice", "Wheat", "Sugarcane", "Maize", "Barley"]

        if land_type.lower() == "dry":
            recommended = [crop for crop in profitable.index if crop in dry_crops]
        elif land_type.lower() == "wet":
            recommended = [crop for crop in profitable.index if crop in wet_crops]
        else:
            recommended = profitable.index.tolist()

        recommended = recommended[:3]
        
        # Popular trending crops
        if "commodity" in filtered.columns:
            popular = filtered["commodity"].value_counts().head(3).index.tolist()
        else:
            popular = []

        records = filtered.to_dict(orient="records")

        # Fill default average prices if missing
        all_crops = list(set(recommended + popular))
        avg_prices_dict = {crop: avg_prices.get(crop, 0) for crop in all_crops}

        return jsonify({
            "success": True,
            "records": records[:100],  # Return up to 100 entries for performance
            "recommended_crops": recommended,
            "popular_crops": popular,
            "avg_prices": avg_prices_dict
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# AgriScan image receiver (Disease model prediction & QR validation)
@app.route("/api/scan", methods=["POST"])
def scan_api():
    req_data = request.get_json()
    if not req_data or "image" not in req_data:
        return jsonify({"success": False, "error": "No image payload sent"})

    mode = req_data.get("mode", "disease")
    base64_img = req_data["image"]
    lang = req_data.get("lang", "hi")

    try:
        # Decode base64 image
        if "," in base64_img:
            base64_img = base64_img.split(",")[1]
        img_bytes = base64.b64decode(base64_img)
        img_np = np.frombuffer(img_bytes, dtype=np.uint8)
        frame = cv2.imdecode(img_np, cv2.IMREAD_COLOR)

        if mode == "qrcode":
            detector = cv2.QRCodeDetector()
            product_id, bbox, _ = detector.detectAndDecode(frame)
            if product_id:
                # Query Firestore
                doc_ref = db.collection("products").document(product_id)
                doc = doc_ref.get()
                if doc.exists:
                    product = doc.to_dict()
                    return jsonify({
                        "success": True,
                        "product_id": product_id,
                        "verified": product.get("verified", False),
                        "manufacturer": product.get("manufacturer", "Unknown Corp"),
                        "name": product.get("name", "Agricultural item")
                    })
                else:
                    return jsonify({
                        "success": True,
                        "product_id": product_id,
                        "verified": False,
                        "manufacturer": "Unregistered manufacturer",
                        "name": "Unknown fake product"
                    })
            else:
                return jsonify({"success": False, "error": "No QR Code detected in image", "message_hi": "छवि में कोई क्यूआर कोड नहीं मिला"})

        else:
            # Disease Detection Model Prediction
            if model is None:
                # Fallback mock mode if model is missing
                crop_name = "Tomato"
                crop_hi = "टमाटर"
                disease_name = "Early Blight"
                disease_hi = "अगेती झुलसा"
                pesticide = "Mancozeb (2g/L water)"
                
                if lang != "hi" and lang != "en":
                    try:
                        from googletrans import Translator
                        translator = Translator()
                        crop_hi = translator.translate(crop_name, src='en', dest=lang).text
                        disease_hi = translator.translate(disease_name, src='en', dest=lang).text
                        pesticide = translator.translate(pesticide, src='en', dest=lang).text
                    except Exception as e:
                        print("Mock translate failed:", e)
                elif lang == "en":
                    crop_hi = crop_name
                    disease_hi = disease_name
                    
                return jsonify({
                    "success": True,
                    "crop": crop_name,
                    "crop_hi": crop_hi,
                    "disease": disease_name,
                    "disease_hi": disease_hi,
                    "pesticide": pesticide
                })

            # Preprocess image
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img_pil = Image.fromarray(img_rgb)
            img_resized = img_pil.resize((128, 128))
            img_arr = np.array(img_resized) / 255.0
            img_expanded = np.expand_dims(img_arr, axis=0)

            # Classify
            predictions = model.predict(img_expanded)[0]
            pred_idx = np.argmax(predictions)
            pred_class = class_labels[pred_idx]

            # Map to bilingual outputs
            meta = bilingual_classes.get(pred_class, {
                'crop': 'Unknown', 'crop_hi': 'अज्ञात फसल',
                'disease': 'Unknown', 'disease_hi': 'अज्ञात रोग',
                'pesticide': 'None'
            })

            # Check Pesticides.csv dataset
            disease_name = meta['disease']
            pesticide = meta['pesticide']
            if pesticide_df is not None:
                filtered = pesticide_df[pesticide_df["Disease"].str.lower() == disease_name.lower()]
                if not filtered.empty:
                    pesticide = filtered["Pesticide"].values[0]

            crop_name = meta['crop']
            crop_hi = meta['crop_hi']
            disease_hi = meta['disease_hi']

            # Translate dynamic class labels if non-default lang is selected
            if lang != "hi" and lang != "en":
                try:
                    from googletrans import Translator
                    translator = Translator()
                    crop_hi = translator.translate(crop_name, src='en', dest=lang).text
                    disease_hi = translator.translate(disease_name, src='en', dest=lang).text
                    if pesticide and pesticide.lower() != 'none':
                        pesticide = translator.translate(pesticide, src='en', dest=lang).text
                except Exception as e:
                    print("Scan translation failed:", e)
            elif lang == "en":
                crop_hi = crop_name
                disease_hi = disease_name

            return jsonify({
                "success": True,
                "crop": crop_name,
                "crop_hi": crop_hi,
                "disease": disease_name,
                "disease_hi": disease_hi,
                "pesticide": pesticide
            })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

# Helpline statistics logs
@app.route("/api/ivr/stats")
def get_ivr_stats():
    return jsonify({
        "success": True,
        "active_calls": len([l for l in ivr_logs if "Active" in l.get("path", "")]),
        "logs": ivr_logs
    })

# Helpline call simulation
@app.route("/api/ivr/simulate", methods=["POST"])
def simulate_ivr():
    import random
    phone_number = f"+91 {random.randint(70000, 99999)} XXX{random.randint(10, 99)}"
    duration = f"{random.randint(0, 2)}m {random.randint(10, 59)}s"
    paths = [
        "Hindi -> Mandi (Press 2)",
        "Hindi -> Weather (Press 3)",
        "Hindi -> Crop Selection (Press 4)",
        "English -> Weather (Press 3)",
        "English -> Mandi (Press 2)"
    ]
    selected_path = random.choice(paths)
    current_time = datetime.datetime.now().strftime("%H:%M")
    
    # Pre-select simulated sound file
    audio = "/static/audio/mandi_hi.mp3"
    if "Weather" in selected_path:
        audio = "/static/audio/weather_hi.mp3"
    elif "English" in selected_path:
        audio = "/static/audio/crop_en.mp3"

    new_log = {
        "caller": phone_number,
        "path": selected_path,
        "duration": duration,
        "time": current_time,
        "audio_url": audio
    }
    
    # Prepend to log database
    ivr_logs.insert(0, new_log)
    if len(ivr_logs) > 20:
        ivr_logs.pop()

    return jsonify({
        "success": True,
        "audio_url": "/static/audio/mandi_hi.mp3" # Simulated telephone greeting audio
    })

# Chatbot API (Speech synthesis output)
@app.route("/api/chat", methods=["POST"])
def chat_api():
    clean_old_audio()
    req_data = request.get_json()
    if not req_data or "message" not in req_data:
        return jsonify({"success": False, "error": "No query message sent"})

    query = req_data["message"].lower()
    lang = req_data.get("lang", "hi")
    
    # AI Rules-based response system
    reply_hi = ""
    reply_en = ""

    if "weather" in query or "मौसम" in query or "बारिश" in query:
        reply_hi = "इंदौर क्षेत्र में आज मौसम सुहाना है। तापमान 32 डिग्री सेल्सियस के आसपास रहेगा, बारिश की कोई संभावना नहीं है।"
        reply_en = "Indore region weather is pleasant today. Temperature is around 32°C, with 0% chance of precipitation."
    elif "mandi" in query or "भाव" in query or "रेट" in query or "कीमत" in query or "गेहूं" in query or "सोयाबीन" in query:
        reply_hi = "इंदौर मंडी में सोयाबीन का औसत भाव ₹4650 प्रति क्विंटल और गेहूं का भाव ₹2350 प्रति क्विंटल चल रहा है।"
        reply_en = "Indore Mandi rate of Soyabean is ₹4,650/quintal and Wheat is ₹2,350/quintal."
    elif "disease" in query or "रोग" in query or "पत्ती" in query or "early blight" in query or "झुलसा" in query:
        reply_hi = "यदि आपकी फसल की पत्तियों पर काले धब्बे दिख रहे हैं, तो यह अर्ली ब्लाइट हो सकता है। नियंत्रण के लिए मैन्कोजेब (Mancozeb) का छिड़काव करें।"
        reply_en = "If leaves display black concentric spots, it could be Early Blight. Spray Mancozeb pesticide to treat it."
    elif "hello" in query or "hi" in query or "नमस्ते" in query or "राम राम" in query:
        reply_hi = "नमस्ते किसान भाई! मैं किसान साथी ए.आई. सहायक हूँ। मैं आपकी क्या मदद कर सकता हूँ?"
        reply_en = "Hello! I am your Kisan Saathi AI assistant. How can I help you today?"
    else:
        reply_hi = "मंडी भाव जानने के लिए 'मंडी', मौसम के लिए 'मौसम' या फसल रोगों के उपचार के लिए 'रोग' लिखकर पूछें।"
        reply_en = "Ask about market prices by saying 'mandi', weather forecast by saying 'weather', or crop leaf infections by saying 'disease'."

    # Dynamic Translation to Selected Language
    reply_target = ""
    if lang == "en":
        reply_target = reply_en
    elif lang == "hi":
        reply_target = reply_hi
    else:
        try:
            from googletrans import Translator
            translator = Translator()
            # Translate from English/Hindi to target language
            reply_target = translator.translate(reply_en, src='en', dest=lang).text
        except Exception as e:
            print("Googletrans failed, falling back to Hindi:", e)
            reply_target = reply_hi

    # Synthesize speech to file in the exact chosen language locale
    timestamp = int(time.time())
    audio_filename = f"chat_reply_{timestamp}.mp3"
    audio_path = os.path.join("static/audio", audio_filename)
    
    try:
        tts = gTTS(text=reply_target, lang=lang)
        tts.save(audio_path)
        audio_url = f"/static/audio/{audio_filename}"
    except Exception as e:
        print("TTS Save failed:", e)
        audio_url = ""

    return jsonify({
        "success": True,
        "reply_hi": reply_target,
        "reply_en": reply_en,
        "audio_url": audio_url
    })

# Settings API
@app.route("/api/settings", methods=["POST"])
def save_settings():
    data = request.get_json()
    if data:
        phone = data.get("phone", "")
        if phone and ("81094" in phone or "78398" in phone):
            phone = "+919999999999"
        session["farmer_name"] = data.get("name")
        session["farmer_phone"] = phone
        session["farmer_city"] = data.get("city")
        session["farmer_land"] = data.get("land_size")
    return jsonify({"success": True})

if __name__ == "__main__":
    import datetime
    app.run(debug=True, host="127.0.0.1", port=5000)
