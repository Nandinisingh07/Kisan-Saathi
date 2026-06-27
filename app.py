from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, render_template, send_from_directory, session
from flask_session import Session
import os, time, glob, base64, io, requests, numpy as np, pandas as pd, datetime, json, random
from PIL import Image
import cv2
from gtts import gTTS
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
app.config['SESSION_TYPE'] = 'filesystem'
app.secret_key = os.getenv("FLASK_SECRET_KEY", "kisan_saathi_secret")
from flask_session import Session
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

print("Loading crop disease model...")
try:
    import tensorflow as tf
    model = tf.keras.models.load_model("crop_disease_model.h5")
    print("Model loaded!")
except Exception as e:
    model = None
    print("Model load failed (mock mode):", e)

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
    'PlantVillage': {'crop':'Unknown','crop_hi':'अज्ञात फसल','disease':'Unknown','disease_hi':'अज्ञात रोग','pesticide':'None'},
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
    'clear sky':'साफ आकाश','few clouds':'कम बादल','scattered clouds':'बिखरे बादल',
    'broken clouds':'टूटे बादल','shower rain':'बोछारें','rain':'बारिश',
    'thunderstorm':'आंधी-तूफान','snow':'बर्फबारी','mist':'कोहरा','haze':'धुंध',
    'overcast clouds':'घने बादल','light rain':'हल्की बारिश',
    'moderate rain':'सामान्य बारिश','heavy intensity rain':'भारी वर्षा'
}

ivr_logs = [
    {"caller":"+91 99999 XXX99","path":"Hindi -> Mandi (Press 2)","duration":"1m 24s","time":"15:10","audio_url":"/static/audio/mandi_hi.mp3"},
    {"caller":"+91 94250 XXX41","path":"Hindi -> Weather (Press 3)","duration":"0m 45s","time":"14:42","audio_url":"/static/audio/weather_hi.mp3"},
    {"caller":"+91 88710 XXX12","path":"English -> Crop Input (Press 4)","duration":"2m 10s","time":"12:15","audio_url":"/static/audio/crop_en.mp3"}
]

def build_ivr_mock_audio():
    try:
        if not os.path.exists("static/audio/mandi_hi.mp3"):
            gTTS("गेहूं का औसत मंडी भाव 2350 रुपये प्रति क्विंटल है।", lang='hi').save("static/audio/mandi_hi.mp3")
        if not os.path.exists("static/audio/weather_hi.mp3"):
            gTTS("आज मौसम साफ रहेगा।", lang='hi').save("static/audio/weather_hi.mp3")
        if not os.path.exists("static/audio/crop_en.mp3"):
            gTTS("You selected Potato.", lang='en').save("static/audio/crop_en.mp3")
    except Exception as e:
        print("Audio build warning:", e)

build_ivr_mock_audio()

def clean_old_audio():
    try:
        now = time.time()
        for f in glob.glob("static/audio/chat_reply_*.mp3"):
            if os.stat(f).st_mtime < now - 300:
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
            wd = data["weather"][0]["description"]
            desc_hi = weather_translations.get(wd.lower(), wd).capitalize() if lang == "hi" else wd.capitalize()
            return jsonify({"success":True,"temp":data["main"]["temp"],"desc":wd.capitalize(),"desc_hi":desc_hi,"main_desc":data["weather"][0]["main"],"humidity":data["main"]["humidity"],"wind":data["wind"]["speed"]})
        return jsonify({"success":False,"error":data.get("message","City not found")})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)})

@app.route("/api/market")
def get_market_data():
    state = request.args.get("state","Madhya Pradesh")
    district = request.args.get("district","Indore")
    land_type = request.args.get("land_type","other")
    try:
        df = pd.read_csv("mandi_prices.csv")
        filtered = df[(df["state"].str.lower()==state.lower())&(df["district"].str.lower()==district.lower())]
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

@app.route("/api/scan", methods=["POST"])
def scan_api():
    req_data = request.get_json()
    if not req_data or "image" not in req_data:
        return jsonify({"success":False,"error":"No image"})
    mode = req_data.get("mode","disease")
    b64 = req_data["image"]
    lang = req_data.get("lang","hi")
    try:
        if "," in b64: b64 = b64.split(",")[1]
        frame = cv2.imdecode(np.frombuffer(base64.b64decode(b64),dtype=np.uint8),cv2.IMREAD_COLOR)
        if mode=="qrcode":
            pid,_,_ = cv2.QRCodeDetector().detectAndDecode(frame)
            if pid and db:
                doc = db.collection("products").document(pid).get()
                if doc.exists:
                    p=doc.to_dict()
                    return jsonify({"success":True,"product_id":pid,"verified":p.get("verified",False),"manufacturer":p.get("manufacturer","Unknown"),"name":p.get("name","Item")})
            return jsonify({"success":True,"product_id":pid or "","verified":False,"manufacturer":"Unregistered","name":"Unknown"})
        if model is None:
            return jsonify({"success":True,"crop":"Tomato","crop_hi":"टमाटर","disease":"Early Blight","disease_hi":"अगेती झुलसा","pesticide":"Mancozeb (2g/L water)"})
        img = np.expand_dims(np.array(Image.fromarray(cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)).resize((128,128)))/255.0,axis=0)
        pred_class = class_labels[np.argmax(model.predict(img)[0])]
        meta = bilingual_classes.get(pred_class,{'crop':'Unknown','crop_hi':'अज्ञात','disease':'Unknown','disease_hi':'अज्ञात','pesticide':'None'})
        pesticide = meta['pesticide']
        if pesticide_df is not None:
            f=pesticide_df[pesticide_df["Disease"].str.lower()==meta['disease'].lower()]
            if not f.empty: pesticide=f["Pesticide"].values[0]
        return jsonify({"success":True,"crop":meta['crop'],"crop_hi":meta['crop_hi'] if lang!="en" else meta['crop'],"disease":meta['disease'],"disease_hi":meta['disease_hi'] if lang!="en" else meta['disease'],"pesticide":pesticide})
    except Exception as e:
        return jsonify({"success":False,"error":str(e)})

@app.route("/api/ivr/stats")
def get_ivr_stats():
    return jsonify({"success":True,"active_calls":0,"logs":ivr_logs})

@app.route("/api/ivr/simulate", methods=["POST"])
def simulate_ivr():
    paths=["Hindi -> Mandi (Press 2)","Hindi -> Weather (Press 3)","Hindi -> Crop Selection (Press 4)","English -> Weather (Press 3)","English -> Mandi (Press 2)"]
    path=random.choice(paths)
    audio="/static/audio/weather_hi.mp3" if "Weather" in path else "/static/audio/crop_en.mp3" if "English" in path else "/static/audio/mandi_hi.mp3"
    ivr_logs.insert(0,{"caller":f"+91 {random.randint(70000,99999)} XXX{random.randint(10,99)}","path":path,"duration":f"{random.randint(0,2)}m {random.randint(10,59)}s","time":datetime.datetime.now().strftime("%H:%M"),"audio_url":audio})
    if len(ivr_logs)>20: ivr_logs.pop()
    return jsonify({"success":True,"audio_url":audio})

@app.route("/api/chat", methods=["POST"])
def chat_api():
    clean_old_audio()
    req_data = request.get_json()
    if not req_data or "message" not in req_data:
        return jsonify({"success":False,"error":"No message"})
    query=req_data["message"].lower()
    lang=req_data.get("lang","hi")
    if "weather" in query or "मौसम" in query:
        hi="इंदौर में आज मौसम सुहाना है। तापमान 32°C रहेगा।"; en="Indore weather is pleasant. Temp ~32C."
    elif "mandi" in query or "भाव" in query or "गेहूं" in query:
        hi="सोयाबीन ₹4650/क्विंटल, गेहूं ₹2350/क्विंटल।"; en="Soyabean ₹4650/q, Wheat ₹2350/q."
    elif "disease" in query or "रोग" in query or "झुलसा" in query:
        hi="पत्तियों पर काले धब्बे हों तो Mancozeb छिड़कें।"; en="Black spots on leaves? Spray Mancozeb."
    elif "hello" in query or "नमस्ते" in query:
        hi="नमस्ते किसान भाई!"; en="Hello farmer friend!"
    else:
        hi="मंडी भाव के लिए 'मंडी', मौसम के लिए 'मौसम' लिखें।"; en="Say 'mandi' for prices, 'weather' for forecast."
    reply = en if lang=="en" else hi
    ts=int(time.time())
    afile=f"static/audio/chat_reply_{ts}.mp3"
    try: gTTS(reply,lang=lang).save(afile); aurl=f"/static/audio/chat_reply_{ts}.mp3"
    except: aurl=""
    return jsonify({"success":True,"reply_hi":reply,"reply_en":en,"audio_url":aurl})

@app.route("/api/settings", methods=["POST"])
def save_settings():
    data=request.get_json()
    if data:
        session["farmer_name"]=data.get("name")
        session["farmer_city"]=data.get("city")
    return jsonify({"success":True})

if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
