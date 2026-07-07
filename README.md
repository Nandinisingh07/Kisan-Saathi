<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:0F172A,100:1E3A8A&height=200&section=header&text=Kisan%20Saathi&fontSize=60&fontColor=38BDF8&fontAlignY=40&desc=AI-Powered%20Agricultural%20Intelligence%20for%20Farmers%20of%20Madhya%20Pradesh&descAlignY=60&descSize=18&descColor=E2E8F0" width="100%"/>

<br/>

<img src="https://img.shields.io/badge/AgriScan-Crop%20Disease%20AI-2E7D32?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Chatbot-Gemini%202.5%20Flash-4285F4?style=for-the-badge"/>
<img src="https://img.shields.io/badge/13%20Languages-Multilingual-FF6F00?style=for-the-badge"/>
<img src="https://img.shields.io/badge/IVR-Twilio%20Live-F22F46?style=for-the-badge"/>
<img src="https://img.shields.io/badge/Status-Hackathon%20Ready-16A34A?style=for-the-badge"/>

<br/><br/>

### 🌾 ए.आई. संचालित फसल सुरक्षा, सटीक लाइव मंडी भाव, मौसम पूर्वानुमान और कॉल सेंटर का एक ही स्थान पर समन्वय। 🌾
### AI-powered crop protection, live mandi prices, weather forecasts, and call center dashboard integration.

<br/>

<a href="https://github.com/Nandinisingh07/Kisan-Saathi"><img src="https://img.shields.io/badge/GitHub-Repo-181717?style=for-the-badge&logo=github&logoColor=white"/></a>
<a href="https://kisan-saathi-backend.onrender.com/"><img src="https://img.shields.io/badge/Live-Demo-46E3B7?style=for-the-badge&logo=render&logoColor=white"/></a>
<a href="#"><img src="https://img.shields.io/badge/Demo-Video-FF0000?style=for-the-badge&logo=youtube&logoColor=white"/></a>

</div>

<br/>

<hr/>

Indian farmers face significant barriers to agricultural growth — language barriers across regional scripts, lack of smartphones/internet access, crop disease outbreaks, fluctuating market prices, and counterfeit pesticides. **Kisan Saathi** addresses this with a unified web dashboard for smartphone-enabled farmers and an offline voice helpline (IVR) that answers queries over a basic phone call, ensuring critical agricultural intelligence is accessible to every farmer.

**Target users/region:** Madhya Pradesh farmers, specifically the Malwa region, with full UI/chatbot translation support across 13 major Indian languages.

<hr/>

<br/>

<img src="https://img.shields.io/badge/CORE%20FEATURES-000000?style=for-the-badge&logoColor=white&labelColor=EA580C"/>

<br/><br/>

<img src="https://img.shields.io/badge/🩺_AgriScan-Crop%20Disease%20Detection-2E7D32?style=flat-square"/>

TFLite model, 18 disease/health classes across Tomato, Potato, Bell Pepper, and Soybean — light enough to run on free-tier hosting.

Runs a local **7.4 MB** `crop_disease_model.tflite` model via `ai_edge_litert.Interpreter` on the backend to classify 18 distinct plant leaf/disease states.

<img src="https://img.shields.io/badge/💬_Multilingual-AI%20Chatbot-4285F4?style=flat-square"/>

Gemini 2.5 Flash-powered (`gemini-2.5-flash`), 13 Indian languages (Hindi, English, Marathi, Gujarati, Bengali, Telugu, Tamil, Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu), spoken replies via gTTS.

<img src="https://img.shields.io/badge/☎️_Real_IVR-Twilio%20Helpline-F22F46?style=flat-square"/>

No app, no internet — real Twilio webhook (`/voice`, `/gather`) accepts incoming calls and uses Gemini-based operator scripts to read out mandi prices, weather forecasts, and crop disease remedies in the farmer's language.

<img src="https://img.shields.io/badge/📈_Mandi_Prices-Live%20Tracking-CA8A04?style=flat-square"/>

Real district-level commodity prices via Agmarknet (data.gov.in), with a local `mandi_prices.csv` fallback that simulates daily market price changes when the API is unreachable.

<img src="https://img.shields.io/badge/🌦️_Weather-Forecast%20%26%20Alerts-0EA5E9?style=flat-square"/>

Live conditions and 3-day forecasts via OpenWeatherMap, translated into the farmer's language, with proactive safety alerts (e.g. advising against pesticide sprays during rainfall warnings).

<img src="https://img.shields.io/badge/🔍_QR_Verification-Pesticide%20Authenticity-7C3AED?style=flat-square"/>

Compares scanned product details (via OpenCV) against `cibrc_registered_db.py` — a local reference list of CIBRC-registered pesticides — to verify combinations and flag unverified listings.

<br/>
<hr/>
<br/>

<img src="https://img.shields.io/badge/TECH%20STACK-000000?style=for-the-badge&logoColor=white&labelColor=7C3AED"/>

<br/><br/>

<img src="https://img.shields.io/badge/Flask-000000?style=flat-square&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/Python%203.11-3776AB?style=flat-square&logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask--Session-000000?style=flat-square"/>
<img src="https://img.shields.io/badge/Google%20Gemini%202.5%20Flash-8E75B2?style=flat-square&logo=googlegemini&logoColor=white"/>
<img src="https://img.shields.io/badge/TFLite%20(ai__edge__litert)-FF6F00?style=flat-square&logo=tensorflow&logoColor=white"/>
<img src="https://img.shields.io/badge/Firebase%20Firestore-FFCA28?style=flat-square&logo=firebase&logoColor=black"/>
<img src="https://img.shields.io/badge/Twilio-F22F46?style=flat-square&logo=twilio&logoColor=white"/>
<img src="https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=flat-square&logo=opencv&logoColor=white"/>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=flat-square&logo=html5&logoColor=white"/>
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=flat-square&logo=javascript&logoColor=black"/>

<br/>
<hr/>
<br/>

<img src="https://img.shields.io/badge/ARCHITECTURE-000000?style=for-the-badge&logoColor=white&labelColor=0EA5E9"/>

<br/><br/>

```
                        ┌─────────────────────────┐
                        │   Flask Backend (app.py) │
                        └────────────┬─────────────┘
                                     │
              ┌──────────────────────┼──────────────────────┐
              │                      │                      │
     🌐 Web Dashboard         ☎️ Twilio IVR Call      🧠 Gemini 2.5 Flash
   (scan, chat, market,       (/voice, /gather          (chat, translation,
    weather, QR)               webhooks)                 TTS text)
```

| File | Responsibility |
|---|---|
| `app.py` | Main Flask application lifecycle, router, database triggers, and Twilio `/voice`/`/gather` webhooks |
| `chatbot_service.py` | Chatbot API endpoint, conversation history management, multi-key Gemini rate-limit rotation |
| `model_service.py` | Lazy-loaded TFLite inference pipeline for crop leaf classification |
| `weather_service.py` | Offline weather lookup & Gemini-based weather translation helper |
| `firebase_service.py` | Firestore integration and pesticide validation |
| `cibrc_registered_db.py` | Local fallback database registry for chemical/pesticide lookup |
| `data_fetcher.py` | Government dataset (Agmarknet) fetch routines |

<br/>
<hr/>
<br/>

<img src="https://img.shields.io/badge/GETTING%20STARTED-000000?style=for-the-badge&logoColor=white&labelColor=16A34A"/>

<br/><br/>

```powershell
git clone https://github.com/Nandinisingh07/Kisan-Saathi.git
cd Kisan-Saathi
pip install -r requirements.txt
cp .env.example .env   # fill in the values below
python seed_firestore.py   # optional: seed Firestore product registry
python run.py          # → http://127.0.0.1:5000
```

**Environment variables required:**

| Variable | Purpose |
|---|---|
| `GEMINI_API_KEY` / `GEMINI_API_KEY_2` | Primary/secondary keys for chatbot translation, auto-rotate on rate-limit |
| `OPENWEATHER_API_KEY` | Key to fetch current forecast metrics |
| `DATAGOV_API_KEY` | Key to fetch government Agmarknet mandi prices |
| `TWILIO_ACCOUNT_SID` / `TWILIO_AUTH_TOKEN` | Credentials to trigger the Twilio IVR helpline |
| `MY_PHONE_NUMBER` | Phone number configuration for Twilio script calls |
| `FLASK_SECRET_KEY` | Security signature for sessions |

**Python version:** 3.11

<br/>
<hr/>
<br/>

<img src="https://img.shields.io/badge/WHY%20THIS%20MATTERS-000000?style=for-the-badge&logoColor=white&labelColor=DC2626"/>

<br/><br/>

- **Zero-internet fallbacks** — the real Twilio IVR hotline lets farmers with feature phones (no internet) access crop diagnosis and mandi data
- **Offline TFLite integration** — disease diagnosis runs on a compressed, low-memory 7.4 MB TFLite interpreter instead of a resource-heavy deep learning runtime, keeping backend deployment cheap and fast
- **True multilingual sync** — handles both static UI labels and dynamic feeds (weather descriptions, crop advisory headings, scan details) across 13 native Indian languages
- **Anti-fail key rotation** — automatically rotates Gemini keys on API errors to prevent standard rate-limit blocks

**Known limitations (kept honest, not hidden):**
- gTTS does not support voice synthesis for Odia (`or`) and Assamese (`as`) — chatbot defaults to visual text output for these
- Free-tier Gemini API is limited to 20 requests/minute; mitigated with dictionary caches, but not eliminated

<br/>
<hr/>
<br/>

<br/>
<hr/>
<br/>

<img src="https://img.shields.io/badge/SCREENSHOTS-000000?style=for-the-badge&logoColor=white&labelColor=0891B2"/>

<br/><br/>

1. **Interactive Farmer Dashboard** — Weather Card, Mandi Trends, and Crop Scan Alerts
2. **AgriScan AI leaf diagnosis** — identified disease and recommendations
3. **Pesticide QR verification** — genuine vs. unverified product badges
4. **Bilingual AI Chatbot interface** — voice input and audio playback
5. **Call center Helpline Log page** — Twilio simulator registers and interactive charts

<br/>
<hr/>
<br/>

<div align="center">

<img src="https://img.shields.io/badge/Built%20Solo%20By-Nandini%20Singh-1E3A8A?style=for-the-badge"/>
<br/><br/>
B.Tech AI/ML · Indore Institute of Science and Technology
<br/>
Submitted to: **Flipkart GRiD 8.0 · Hack2Skill / GDG Hackathon**

<br/><br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:1E3A8A,100:0F172A&height=100&section=footer" width="100%"/>

</div>
