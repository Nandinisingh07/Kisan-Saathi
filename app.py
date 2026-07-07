from dotenv import load_dotenv
load_dotenv()
import os, time, glob, base64, io, requests, numpy as np, pandas as pd, datetime, json, random
from flask import Flask, request, jsonify, render_template, send_from_directory, session
from flask_session import Session
from PIL import Image
import cv2
from gtts import gTTS
import firebase_admin
from firebase_admin import credentials, firestore
import google.generativeai as genai
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = os.getenv("FLASK_SECRET_KEY", "kisan_saathi_secret")
Session(app)

os.makedirs("static/css", exist_ok=True)
os.makedirs("static/js", exist_ok=True)
os.makedirs("static/audio", exist_ok=True)
os.makedirs("templates", exist_ok=True)

if not firebase_admin._apps:
    try:
        firebase_json = os.getenv("FIREBASE_CREDENTIALS")
        if firebase_json:
            cred = credentials.Certificate(json.loads(firebase_json))
        else:
            cred = credentials.Certificate("firebase_key.json")
        firebase_admin.initialize_app(cred)
    except Exception as e:
        print("Firebase init warning:", e)

try:
    db = firestore.client()
except Exception as e:
    db = None
    print("Firestore client warning:", e)

# Crop disease model loading has been moved to model_service.py (lazy-loaded)

PESTICIDE_CSV = os.path.join(os.path.dirname(__file__), "Pesticides.csv")
try:
    pesticide_df = pd.read_csv(PESTICIDE_CSV)
    pesticide_df['Disease'] = pesticide_df['Disease'].str.strip()
    print("Pesticide dataset loaded.")
except Exception as e:
    pesticide_df = None
    print("Pesticide CSV missing:", e)

class_labels = [
    'Pepper__bell___Bacterial_spot','Pepper__bell___healthy','PlantVillage',
    'Potato___Early_blight','Potato___Late_blight','Potato___healthy',
    'Tomato_Bacterial_spot','Tomato_Early_blight','Tomato_Late_blight',
    'Tomato_Leaf_Mold','Tomato_Septoria_leaf_spot',
    'Tomato_Spider_mites_Two_spotted_spider_mite','Tomato__Target_Spot',
    'Tomato__Tomato_YellowLeaf__Curl_Virus','Tomato__Tomato_mosaic_virus','Tomato_healthy'
]

bilingual_classes = {
    'Pepper__bell___Bacterial_spot': {'crop':'Pepper Bell','crop_hi':'शिमला मिर्च','disease':'Bacterial Spot','disease_hi':'जीवाणु धब्बा','pesticide':'Streptocycline (0.1g/L) + Copper Oxychloride (2g/L)'},
    'Pepper__bell___healthy': {'crop':'Pepper Bell','crop_hi':'शिमला मिर्च','disease':'Healthy','disease_hi':'स्वस्थ','pesticide':'None'},
    'PlantVillage': {'crop':'Unknown','crop_hi':'अज्ञात','disease':'Unknown','disease_hi':'अज्ञात','pesticide':'None'},
    'Potato___Early_blight': {'crop':'Potato','crop_hi':'आलू','disease':'Early Blight','disease_hi':'अगेती झुलसा','pesticide':'Mancozeb (2g/L water)'},
    'Potato___Late_blight': {'crop':'Potato','crop_hi':'आलू','disease':'Late Blight','disease_hi':'पछैती झुलसा','pesticide':'Metalaxyl + Mancozeb'},
    'Potato___healthy': {'crop':'Potato','crop_hi':'आलू','disease':'Healthy','disease_hi':'स्वस्थ','pesticide':'None'},
    'Tomato_Bacterial_spot': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Bacterial Spot','disease_hi':'जीवाणु धब्बा','pesticide':'Streptocycline + Copper Oxychloride'},
    'Tomato_Early_blight': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Early Blight','disease_hi':'अगेती झुलसा','pesticide':'Mancozeb or Chlorothalonil'},
    'Tomato_Late_blight': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Late Blight','disease_hi':'पछैती झुलसा','pesticide':'Metalaxyl + Mancozeb'},
    'Tomato_Leaf_Mold': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Leaf Mold','disease_hi':'पत्ती मोल्ड','pesticide':'Carbendazim or Chlorothalonil'},
    'Tomato_Septoria_leaf_spot': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Septoria Leaf Spot','disease_hi':'सेप्टोरिया पत्ती धब्बा','pesticide':'Mancozeb or Propiconazole'},
    'Tomato_Spider_mites_Two_spotted_spider_mite': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Spider Mites','disease_hi':'मकड़ी घुन','pesticide':'Abamectin or Dicofol'},
    'Tomato__Target_Spot': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Target Spot','disease_hi':'लक्षित धब्बा','pesticide':'Chlorothalonil or Mancozeb'},
    'Tomato__Tomato_YellowLeaf__Curl_Virus': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Yellow Leaf Curl Virus','disease_hi':'पीला पत्ती मरोड़ वायरस','pesticide':'Imidacloprid'},
    'Tomato__Tomato_mosaic_virus': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Mosaic Virus','disease_hi':'मोज़ेक वायरस','pesticide':'Dimethoate'},
    'Tomato_healthy': {'crop':'Tomato','crop_hi':'टमाटर','disease':'Healthy','disease_hi':'स्वस्थ','pesticide':'None'}
}

weather_translations = {
    'clear sky':'साफ आसमान','few clouds':'आंशिक बादल','scattered clouds':'बिखरे बादल',
    'broken clouds':'घने बादल','shower rain':'तेज बौछारें','rain':'बारिश',
    'thunderstorm':'आंधी तूफान','snow':'बर्फबारी','mist':'कोहरा','haze':'धुंध',
    'overcast clouds':'पूरी तरह से बादलमय','light rain':'हल्की बारिश',
    'moderate rain':'मध्यम बारिश','heavy intensity rain':'भारी बारिश'
}

multilingual_weather = {
    "hi": {
        'clear sky': 'साफ आसमान', 'few clouds': 'आंशिक बादल', 'scattered clouds': 'बिखरे बादल',
        'broken clouds': 'घने बादल', 'shower rain': 'तेज बौछारें', 'rain': 'बारिश',
        'thunderstorm': 'आंधी तूफान', 'snow': 'बर्फबारी', 'mist': 'कोहरा', 'haze': 'धुंध',
        'overcast clouds': 'पूरी तरह से बादलमय', 'light rain': 'हल्की बारिश',
        'moderate rain': 'मध्यम बारिश', 'heavy intensity rain': 'भारी बारिश'
    },
    "mr": {
        'clear sky': 'स्वच्छ आकाश', 'few clouds': 'अंशतः ढगाळ', 'scattered clouds': 'विखुरलेले ढग',
        'broken clouds': 'ढगाळ वातावरण', 'shower rain': 'पावसाच्या सरी', 'rain': 'पाऊस',
        'thunderstorm': 'वादळी पाऊस', 'snow': 'बर्फवृष्टी', 'mist': 'धुके', 'haze': 'धुके',
        'overcast clouds': 'पूर्णपणे ढगाळ', 'light rain': 'हलका पाऊस',
        'moderate rain': 'मध्यम पाऊस', 'heavy intensity rain': 'मुसळधार पाऊस'
    }
}

ivr_logs = [
    {"caller":"+91 99999 XXX99","path":"Hindi -> Mandi (Press 2)","duration":"1m 24s","time":"15:10","audio_url":"/static/audio/mandi_hi.mp3","transcript":"इंदौर मंडी में गेहूं का औसत भाव तेईस सौ पचास रुपये प्रति क्विंटल चल रहा है।"},
    {"caller":"+91 94250 XXX41","path":"Hindi -> Weather (Press 3)","duration":"0m 45s","time":"14:42","audio_url":"/static/audio/weather_hi.mp3","transcript":"इंदौर क्षेत्र में आज मौसम साफ रहेगा।"},
    {"caller":"+91 88710 XXX12","path":"English -> Crop Help (Press 4)","duration":"2m 10s","time":"12:15","audio_url":"/static/audio/crop_en.mp3","transcript":"For wheat Early Blight, spray Mancozeb 2g per litre water."}
]

def build_ivr_mock_audio():
    try:
        if not os.path.exists("static/audio/mandi_hi.mp3"):
            gTTS("गेहूं का औसत मंडी भाव 2350 रुपये प्रति क्विंटल है।", lang='hi').save("static/audio/mandi_hi.mp3")
        if not os.path.exists("static/audio/weather_hi.mp3"):
            gTTS("आज मौसम साफ रहेगा।", lang='hi').save("static/audio/weather_hi.mp3")
        if not os.path.exists("static/audio/crop_en.mp3"):
            gTTS("For crop disease help, spray Mancozeb.", lang='en').save("static/audio/crop_en.mp3")
    except Exception as e:
        print("Audio build warning:", e)

build_ivr_mock_audio()

def clean_old_audio():
    try:
        now = time.time()
        for f in glob.glob("static/audio/chat_reply_*.mp3") + glob.glob("static/audio/ivr_*.mp3"):
            if os.stat(f).st_mtime < now - 600:
                os.remove(f)
    except: pass

@app.route("/")
def index(): return render_template("index.html", active_page="dashboard")
@app.route("/scan")
def scan_page(): return render_template("scan.html", active_page="scan")
@app.route("/market")
def market_page(): return render_template("market.html", active_page="market")
@app.route("/chat")
def chat_page(): return render_template("chat.html", active_page="chat")
@app.route("/ivr")
def ivr_page(): return render_template("ivr.html", active_page="ivr")
@app.route("/settings")
def settings_page(): return render_template("settings.html", active_page="settings")
@app.route("/product_qr/<path:filename>")
def serve_qr(filename): return send_from_directory(".", filename)

def translate_weather(desc, lang):
    desc_lower = desc.lower()
    if lang == "en":
        return desc.capitalize()
    
    # Try local dictionary lookup first for zero-latency, rate-limit-proof delivery
    if lang in multilingual_weather and desc_lower in multilingual_weather[lang]:
        return multilingual_weather[lang][desc_lower].capitalize()
    
    if lang == "hi" or lang not in multilingual_weather:
        if desc_lower in weather_translations:
            return weather_translations[desc_lower].capitalize()
            
    try:
        from language_config import LANGUAGES
        lang_info = LANGUAGES.get(lang, LANGUAGES["hi"])
        lang_name = lang_info["name"]
        
        api_key = os.getenv("GEMINI_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = f"Translate the weather description term '{desc}' into the language {lang_name}. Return ONLY the direct translation, nothing else."
            response = model.generate_content(prompt)
            if response and response.text:
                return response.text.strip().capitalize()
    except Exception as e:
        print(f"Gemini weather translation failed: {e}")
        
    return weather_translations.get(desc_lower, desc).capitalize()

@app.route("/api/weather")
def get_weather_api():
    city = request.args.get("city", "Indore")
    lang = request.args.get("lang", "hi")
    api_key = os.getenv("OPENWEATHER_API_KEY")
    
    # Base fallback values (simulated dynamic Indore weather if key missing or unreachable)
    fallback_data = {
        "success": True,
        "temp": 32.0,
        "desc": "scattered clouds",
        "desc_hi": "बिखरे बादल",
        "main_desc": "Clouds",
        "humidity": 45.0,
        "wind": 3.5
    }

    if not api_key:
        localized_fallback = fallback_data.copy()
        localized_fallback["desc_hi"] = translate_weather(fallback_data["desc"], lang)
        return jsonify(localized_fallback)

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    try:
        res = requests.get(url, timeout=5)
        data = res.json()
        if res.status_code == 200:
            wd = data["weather"][0]["description"]
            desc_hi = translate_weather(wd, lang)
            return jsonify({
                "success": True,
                "temp": data["main"]["temp"],
                "desc": wd.capitalize(),
                "desc_hi": desc_hi,
                "main_desc": data["weather"][0]["main"],
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"]
            })
        
        localized_fallback = fallback_data.copy()
        localized_fallback["desc_hi"] = translate_weather(fallback_data["desc"], lang)
        return jsonify(localized_fallback)
    except Exception as e:
        localized_fallback = fallback_data.copy()
        localized_fallback["desc_hi"] = translate_weather(fallback_data["desc"], lang)
        return jsonify(localized_fallback)

@app.route("/api/market")
def get_market_data():
    state = request.args.get("state","Madhya Pradesh")
    district = request.args.get("district","Indore")
    land_type = request.args.get("land_type","other")
    try:
        csv_path = os.path.join(os.path.dirname(__file__), "mandi_prices.csv")
        df = pd.read_csv(csv_path)
        filtered = df[(df["state"].str.lower()==state.lower())&(df["district"].str.lower()==district.lower())].copy()
        filtered["modal_price"] = pd.to_numeric(filtered["modal_price"],errors="coerce")
        avg_prices = filtered.groupby("commodity")["modal_price"].mean().to_dict()
        profitable = filtered.groupby("commodity")["modal_price"].mean().sort_values(ascending=False)
        dry_crops = ["Bajra","Moong","Urad","Chana","Masoor","Soyabean"]
        wet_crops = ["Rice","Wheat","Sugarcane","Maize","Barley"]
        if land_type.lower()=="dry": recommended=[c for c in profitable.index if c in dry_crops]
        elif land_type.lower()=="wet": recommended=[c for c in profitable.index if c in wet_crops]
        else: recommended=profitable.index.tolist()
        recommended=recommended[:3]
        popular=filtered["commodity"].value_counts().head(3).index.tolist() if "commodity" in filtered.columns else []
        return jsonify({"success":True,"records":filtered.to_dict(orient="records")[:100],"recommended_crops":recommended,"popular_crops":popular,"avg_prices":{c:avg_prices.get(c,0) for c in list(set(recommended+popular))}})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)})

@app.route("/api/ivr/call", methods=["POST"])
def ivr_interactive_call():
    req_data = request.get_json() or {}
    user_input = req_data.get("input", "")
    language = req_data.get("language", "hi")
    step = req_data.get("step", "welcome")
    crop = req_data.get("crop", "wheat")

    lang_note = "Reply in Hindi (Devanagari). Helpline operator style. Max 3 sentences." if language == "hi" else "Reply in English. Helpline operator style. Max 3 sentences."

    try:
        prompt = f"""You are Kisan Saathi IVR helpline operator for farmers in Madhya Pradesh India.
Current step: {step}
Farmer input: {user_input}
Crop context: {crop}
{lang_note}
If user pressed 2 give mandi prices with rupee amounts.
If user pressed 3 give weather advisory with temperature.
If user pressed 4 give crop disease advice with pesticide names and dosages.
If user pressed 5 give PM-KISAN scheme info.
If user typed a question give specific expert farming advice."""

        model_g = genai.GenerativeModel("gemini-2.5-flash")
        response = model_g.generate_content(prompt)
        reply_text = response.text.strip()
    except Exception as e:
        print("IVR call error:", e)
        reply_text = "नमस्ते किसान भाई। कृपया पुनः प्रयास करें।" if language == "hi" else "Please try again shortly."

    ts = int(time.time())
    audio_filename = f"ivr_interactive_{ts}.mp3"
    try:
        tts_lang = "hi" if language == "hi" else "en"
        gTTS(reply_text, lang=tts_lang).save(f"static/audio/{audio_filename}")
        audio_url = f"/static/audio/{audio_filename}"
    except:
        audio_url = ""

    return jsonify({"success":True,"reply":reply_text,"audio_url":audio_url})

@app.route("/api/ivr/stats")
def ivr_stats():
    total_calls = 1420
    active_callers = 0
    top_option = "मंडी"
    top_option_pct = 42
    primary_lang = "हिंदी"
    primary_lang_pct = 85
    return jsonify({
        "success": True,
        "total_calls": total_calls,
        "weekly_change": "+12%",
        "active_callers": active_callers,
        "top_option": top_option,
        "top_option_pct": top_option_pct,
        "primary_language": primary_lang,
        "primary_language_pct": primary_lang_pct,
        "logs": ivr_logs
    })

@app.route("/api/ivr/simulate", methods=["POST"])
def ivr_simulate():
    req_data = request.get_json() or {}
    key_pressed = req_data.get("key", "1")
    language = req_data.get("language", "hi")

    menu_map = {"2": "mandi", "3": "weather", "4": "disease", "5": "scheme"}
    step = menu_map.get(key_pressed, "welcome")

    lang_note = "Reply in Hindi (Devanagari). Helpline operator style. Max 3 sentences." if language == "hi" else "Reply in English. Helpline operator style. Max 3 sentences."
    prompt = f"""You are Kisan Saathi IVR helpline operator for farmers in Madhya Pradesh India.
Current step: {step}
Farmer pressed: {key_pressed}
{lang_note}
If step is mandi give mandi prices with rupee amounts.
If step is weather give weather advisory with temperature.
If step is disease give crop disease advice with pesticide names and dosages.
If step is scheme give PM-KISAN scheme info."""

    try:
        model_g = genai.GenerativeModel("gemini-2.5-flash")
        response = model_g.generate_content(prompt)
        reply_text = response.text.strip()
    except Exception as e:
        print("IVR simulate error:", e)
        reply_text = "नमस्ते किसान भाई। कृपया पुनः प्रयास करें।" if language == "hi" else "Please try again shortly."

    ts = int(time.time())
    audio_filename = f"ivr_sim_{ts}.mp3"
    try:
        tts_lang = "hi" if language == "hi" else "en"
        gTTS(reply_text, lang=tts_lang).save(f"static/audio/{audio_filename}")
        audio_url = f"/static/audio/{audio_filename}"
    except:
        audio_url = ""

    return jsonify({"success": True, "reply": reply_text, "audio_url": audio_url, "step": step})

@app.route("/api/settings", methods=["POST"])
def save_settings():
    data = request.get_json()
    if data:
        session["farmer_name"] = data.get("name")
        session["farmer_city"] = data.get("city")
    return jsonify({"success":True})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
