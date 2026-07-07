<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:14532D,50:15803D,100:65A30D&height=220&section=header&text=Kisan%20Saathi&fontSize=62&fontColor=FEF9C3&fontAlignY=38&desc=AI-Powered%20Agricultural%20Intelligence%20for%20Farmers%20of%20Madhya%20Pradesh&descAlignY=58&descSize=18&descColor=ECFCCB" width="100%"/>

<br/>

<img src="https://img.shields.io/badge/🩺_AgriScan-Crop%20Disease%20AI-9DC183?style=for-the-badge"/>
<img src="https://img.shields.io/badge/💬_Chatbot-Gemini%202.5%20Flash-F5F5DC?style=for-the-badge"/>
<img src="https://img.shields.io/badge/🗣️_13%20Languages-Multilingual-6B7280?style=for-the-badge"/>
<img src="https://img.shields.io/badge/☎️_IVR-Twilio%20Live-9DC183?style=for-the-badge"/>

<br/><br/>

### 🌾 ए.आई. संचालित फसल सुरक्षा, सटीक लाइव मंडी भाव, मौसम पूर्वानुमान और कॉल सेंटर का एक ही स्थान पर समन्वय। 🌾
### AI-powered crop protection, live mandi prices, weather forecasts, and call center dashboard integration.

<br/>

<a href="https://github.com/Nandinisingh07/Kisan-Saathi"><img src="https://img.shields.io/badge/GitHub-Repo-F5F5DC?style=for-the-badge&logo=github&logoColor=black"/></a>
<a href="https://kisan-saathi-backend.onrender.com/"><img src="https://img.shields.io/badge/Live-Demo-6B7280?style=for-the-badge&logo=render&logoColor=white"/></a>

</div>

<br/>

<p align="center">🌱 ────────────────────────────────────────────── 🌱</p>

<br/>

Indian farmers face significant barriers to agricultural growth — language barriers across regional scripts, lack of smartphones/internet access, crop disease outbreaks, fluctuating market prices, and counterfeit pesticides. **Kisan Saathi** addresses this with a unified web dashboard for smartphone-enabled farmers and an offline voice helpline (IVR) that answers queries over a basic phone call, ensuring critical agricultural intelligence is accessible to every farmer.

**Target users/region:** Madhya Pradesh farmers, specifically the Malwa region, with full UI/chatbot translation support across 13 major Indian languages.

<p align="center">🌱 ────────────────────────────────────────────── 🌱</p>

<br/>

<div align="center">
<img src="https://img.shields.io/badge/🌿%20CORE%20FEATURES%20🌿-1F2937?style=for-the-badge&logoColor=black&labelColor=9DC183&color=9DC183"/>
</div>

<br/>

<img src="https://img.shields.io/badge/🩺_AgriScan-Crop%20Disease%20Detection-F5F5DC?style=flat-square"/>

TFLite model, 18 disease/health classes across Tomato, Potato, Bell Pepper, and Soybean — light enough to run on free-tier hosting.

Runs a local **7.4 MB** `crop_disease_model.tflite` model via `ai_edge_litert.Interpreter` on the backend to classify 18 distinct plant leaf/disease states.

<img src="https://img.shields.io/badge/💬_Multilingual-AI%20Chatbot-6B7280?style=flat-square"/>

Gemini 2.5 Flash-powered (`gemini-2.5-flash`), 13 Indian languages (Hindi, English, Marathi, Gujarati, Bengali, Telugu, Tamil, Kannada, Malayalam, Punjabi, Odia, Assamese, Urdu), spoken replies via gTTS.

<img src="https://img.shields.io/badge/☎️_Real_IVR-Twilio%20Helpline-9DC183?style=flat-square"/>

No app, no internet — real Twilio webhook (`/voice`, `/gather`) accepts incoming calls and uses Gemini-based operator scripts to read out mandi prices, weather forecasts, and crop disease remedies in the farmer's language.

<img src="https://img.shields.io/badge/📈_Mandi_Prices-Live%20Tracking-F5F5DC?style=flat-square"/>

Real district-level commodity prices via Agmarknet (data.gov.in), with a local `mandi_prices.csv` fallback that simulates daily market price changes when the API is unreachable.

<img src="https://img.shields.io/badge/🌦️_Weather-Forecast%20%26%20Alerts-6B7280?style=flat-square"/>

Live conditions and 3-day forecasts via OpenWeatherMap, translated into the farmer's language, with proactive safety alerts (e.g. advising against pesticide sprays during rainfall warnings).

<img src="https://img.shields.io/badge/🔍_QR_Verification-Pesticide%20Authenticity-9DC183?style=flat-square"/>

Compares scanned product details (via OpenCV) against `cibrc_registered_db.py` — a local reference list of CIBRC-registered pesticides — to verify combinations and flag unverified listings.

<br/>
<p align="center">🌱 ────────────────────────────────────────────── 🌱</p>
<br/>

<div align="center">
<img src="https://img.shields.io/badge/🚜%20TECH%20STACK%20🚜-1F2937?style=for-the-badge&logoColor=black&labelColor=F5F5DC&color=F5F5DC"/>
</div>

<br/>

<div align="center">

<img src="https://img.shields.io/badge/Flask-6B7280?style=flat-square&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/Python%203.11-9DC183?style=flat-square&logo=python&logoColor=black"/>
<img src="https://img.shields.io/badge/Flask--Session-F5F5DC?style=flat-square&logoColor=black"/>
<img src="https://img.shields.io/badge/Google%20Gemini%202.5%20Flash-6B7280?style=flat-square&logo=googlegemini&logoColor=white"/>
<img src="https://img.shields.io/badge/TFLite%20(ai__edge__litert)-9DC183?style=flat-square&logo=tensorflow&logoColor=black"/>
<img src="https://img.shields.io/badge/Firebase%20Firestore-F5F5DC?style=flat-square&logo=firebase&logoColor=black"/>
<img src="https://img.shields.io/badge/Twilio-6B7280?style=flat-square&logo=twilio&logoColor=white"/>
<img src="https://img.shields.io/badge/Render-9DC183?style=flat-square&logo=render&logoColor=black"/>
<img src="https://img.shields.io/badge/OpenCV-F5F5DC?style=flat-square&logo=opencv&logoColor=black"/>
<img src="https://img.shields.io/badge/HTML5-6B7280?style=flat-square&logo=html5&logoColor=white"/>
<img src="https://img.shields.io/badge/JavaScript-9DC183?style=flat-square&logo=javascript&logoColor=black"/>

</div>

<br/>
<p align="center">🌱 ────────────────────────────────────────────── 🌱</p>
<br/>

<div align="center">
<img src="https://img.shields.io/badge/🗺️%20ARCHITECTURE%20🗺️-1F2937?style=for-the-badge&logoColor=black&labelColor=F5F5DC&color=F5F5DC"/>
</div>

<br/>

<div align="center">

<table>
<tr>
<td align="center" bgcolor="#166534" width="480">
<font color="#F5F5DC"><b>🌾 Flask Backend (app.py)</b><br/><sub>main router · lifecycle · DB triggers</sub></font>
</td>
</tr>
</table>

<table>
<tr>
<td align="center" width="160">│</td>
<td align="center" width="160">│</td>
<td align="center" width="160">│</td>
</tr>
<tr>
<td align="center">⬇️</td>
<td align="center">⬇️</td>
<td align="center">⬇️</td>
</tr>
</table>

<table>
<tr>
<td align="center" bgcolor="#9DC183" width="220" valign="top">
<b>🌐 Web Dashboard</b><br/><br/>
<sub>scan · chat · market<br/>weather · QR</sub>
</td>
<td align="center" bgcolor="#F5F5DC" width="220" valign="top">
<b>☎️ Twilio IVR Call</b><br/><br/>
<sub>/voice · /gather<br/>webhooks</sub>
</td>
<td align="center" bgcolor="#6B7280" width="220" valign="top">
<font color="#F5F5DC"><b>🧠 Gemini 2.5 Flash</b><br/><br/>
<sub>chat · translation<br/>TTS text</sub></font>
</td>
</tr>
</table>

<sub>Web Dashboard and Twilio IVR both route language/voice requests through Gemini 2.5 Flash for translation and TTS generation.</sub>

</div>

<br/>

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
<p align="center">🌱 ────────────────────────────────────────────── 🌱</p>
<br/>

<div align="center">
<img src="https://img.shields.io/badge/🌾%20GETTING%20STARTED%20🌾-1F2937?style=for-the-badge&logoColor=black&labelColor=6B7280&color=6B7280"/>
</div>

<br/>

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
<p align="center">🌱 ────────────────────────────────────────────── 🌱</p>
<br/>

<div align="center">
<img src="https://img.shields.io/badge/🌻%20WHY%20THIS%20MATTERS%20🌻-1F2937?style=for-the-badge&logoColor=black&labelColor=9DC183&color=9DC183"/>
</div>

<br/>

- **Zero-internet fallbacks** — the real Twilio IVR hotline lets farmers with feature phones (no internet) access crop diagnosis and mandi data
- **Offline TFLite integration** — disease diagnosis runs on a compressed, low-memory 7.4 MB TFLite interpreter instead of a resource-heavy deep learning runtime, keeping backend deployment cheap and fast
- **True multilingual sync** — handles both static UI labels and dynamic feeds (weather descriptions, crop advisory headings, scan details) across 13 native Indian languages
- **Anti-fail key rotation** — automatically rotates Gemini keys on API errors to prevent standard rate-limit blocks

**Known limitations (kept honest, not hidden):**
- gTTS does not support voice synthesis for Odia (`or`) and Assamese (`as`) — chatbot defaults to visual text output for these
- Free-tier Gemini API is limited to 20 requests/minute; mitigated with dictionary caches, but not eliminated

<br/>
<p align="center">🌱 ────────────────────────────────────────────── 🌱</p>
<br/>

<div align="center">
<img src="https://img.shields.io/badge/📸%20SCREENSHOTS%20📸-1F2937?style=for-the-badge&logoColor=black&labelColor=F5F5DC&color=F5F5DC"/>
</div>

<br/>

<div align="center">

<table>
<tr>
<td align="center" width="33%">
<b>🖥️ Main Dashboard</b><br/><br/>
<img src="./screenshots/dashboard.png" width="100%"/><br/>
<sub>Weather card, mandi price trends, and crop scan alerts at a glance</sub>
</td>
<td align="center" width="33%">
<b>☎️ IVR Support Page</b><br/><br/>
<img src="./screenshots/ivr.png" width="100%"/><br/>
<sub>Twilio call simulator with live support logs and interaction charts</sub>
</td>
<td align="center" width="33%">
<b>🩺 AgriScan · Diagnosis & Verification</b><br/><br/>
<img src="./screenshots/agriscan.png" width="100%"/><br/>
<sub>Crop disease detection, treatment recommendations, and pesticide QR verification</sub>
</td>
</tr>
</table>

</div>

<br/>
<p align="center">🌱 ────────────────────────────────────────────── 🌱</p>
<br/>

<div align="center">

<img src="https://img.shields.io/badge/🌾%20Built%20Solo%20By-Nandini%20Singh-6B7280?style=for-the-badge"/>
<br/><br/>
B.Tech AI/ML · Indore Institute of Science and Technology

<br/><br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:65A30D,50:15803D,100:14532D&height=100&section=footer" width="100%"/>

</div>
