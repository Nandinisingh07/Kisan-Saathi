<div align="center">

<img width="100%" src="https://capsule-render.vercel.app/api?type=waving&height=300&color=0:14532D,25:2E7D32,50:4CAF50,75:84CC16,100:C7F9CC&text=🌾%20Kisan%20Saathi&fontColor=FFFFFF&fontSize=64&fontAlignY=35&desc=AI-Powered%20Agricultural%20Intelligence%20Platform&descAlignY=57&descSize=22&descColor=F8FAFC"/>

# 🌱 Empowering Every Farmer with AI

<br>

<img src="https://img.shields.io/badge/_Crop_Disease_&_Pesticide_AI-1B5E20?style=for-the-badge"/>
<img src="https://img.shields.io/badge/_Product_Verification_(CIB%26RC)-FFE082?style=for-the-badge"/>
<img src="https://img.shields.io/badge/_Multilingual_(13_Languages)-1976D2?style=for-the-badge"/>
<img src="https://img.shields.io/badge/_AI_Chatbot-7C3AED?style=for-the-badge"/>
<img src="https://img.shields.io/badge/_Live_Market_Prices-F59E0B?style=for-the-badge"/>
<img src="https://img.shields.io/badge/_Weather_Alerts-0288D1?style=for-the-badge"/>
<img src="https://img.shields.io/badge/_IVR_Voice_Support-D81B60?style=for-the-badge"/>

<br><br>

<a href="https://kisan-saathi-backend.onrender.com/">
<img src="https://img.shields.io/badge/_Live_Demo-16A34A?style=for-the-badge&logo=render&logoColor=white"/>
</a>
<a href="https://github.com/Nandinisingh07/Kisan-Saathi">
<img src="https://img.shields.io/badge/_GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/>
</a>

<br><br>

<img src="https://readme-typing-svg.herokuapp.com?font=Poppins&weight=600&size=22&duration=3000&pause=800&center=true&vCenter=true&width=850&color=F5F5DC&lines=AI+Crop+Disease+Detection;CIB%26RC+Product+Verification;Live+Market+Prices;Real-Time+Weather+Alerts;13+Indian+Languages;IVR+Voice+Support"/>

</div>

<div align="center">

### 🌱 ए.आई. संचालित फसल सुरक्षा, सटीक लाइव मंडी भाव, मौसम पूर्वानुमान और कॉल सेंटर का एक ही स्थान पर समन्वय। 
### 🌱AI-powered crop protection, live mandi prices, weather forecasts, and call center dashboard integration.

<br/>

</div>
Indian farmers face significant barriers to agricultural growth — language barriers across regional scripts, lack of smartphone/internet access, crop disease outbreaks, fluctuating market prices, and counterfeit pesticides. **Kisan Saathi** addresses this with a unified web dashboard for smartphone-enabled farmers and an offline voice helpline (IVR) that answers queries over a basic phone call, ensuring critical agricultural intelligence is accessible to every farmer.

**Target users/region:** Madhya Pradesh farmers, specifically the Malwa region, with full UI/chatbot translation support across 13 major Indian languages.

<div align="center">
<img src="https://img.shields.io/badge/CORE%20FEATURES-1976D2?style=for-the-badge&color=1976D2&labelColor=1976D2&logoColor=white"/>
</div>

<br/>

<img src="https://img.shields.io/badge/🩺_AgriScan-Crop%20Disease%20Detection-F5F5DC?style=flat-square"/>

Runs a local **7.4 MB** `crop_disease_model.tflite` model via `ai_edge_litert.Interpreter` on the backend to classify 18 distinct plant leaf/disease states across Tomato, Potato, Bell Pepper, and Soybean crops — light enough to run on free-tier hosting.

<img src="https://img.shields.io/badge/💬_Multilingual-AI%20Chatbot-6B7280?style=flat-square"/>

Gemini 2.5 Flash–powered (`gemini-2.5-flash`) chatbot supporting 13 Indian languages — Hindi, English, Marathi, Gujarati, Bengali, Telugu, Tamil, Kannada, Malayalam, Punjabi, Odia, Assamese, and Urdu — with spoken replies via gTTS.

<img src="https://img.shields.io/badge/☎️_Real_IVR-Twilio%20Helpline-9DC183?style=flat-square"/>

No app, no internet — a real Twilio webhook (`/voice`, `/gather`) accepts incoming calls and uses Gemini-based operator scripts to read out mandi prices, weather forecasts, and crop disease remedies in the farmer's language.

<img src="https://img.shields.io/badge/📈_Mandi_Prices-Live%20Tracking-F5F5DC?style=flat-square"/>

Real district-level commodity prices via Agmarknet (data.gov.in), with a local `mandi_prices.csv` fallback that simulates daily market price changes when the API is unreachable.

<img src="https://img.shields.io/badge/🌦️_Weather-Forecast%20%26%20Alerts-6B7280?style=flat-square"/>

Live conditions and 3-day forecasts via OpenWeatherMap, translated into the farmer's language, with proactive safety alerts (e.g. advising against pesticide sprays during rainfall warnings).

<img src="https://img.shields.io/badge/🔍_QR_Verification-Pesticide%20Authenticity-9DC183?style=flat-square"/>

Compares scanned product details (via OpenCV) against `cibrc_registered_db.py` — a local reference list of CIB&RC-registered pesticides — to verify combinations and flag unverified listings.
<br>
<br>
<div align="center">
<div align="center">
<img src="https://img.shields.io/badge/TECH%20STACK-E67E22?style=for-the-badge&labelColor=E67E22&color=E67E22&logoColor=white"/>
</div>
<br/>
<div align="center">
<img src="https://img.shields.io/badge/Python_3.11-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B"/>
<img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/Flask_Session-4B5563?style=for-the-badge&logo=flask&logoColor=white"/>
<img src="https://img.shields.io/badge/Gunicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white"/>
<br>
<img src="https://img.shields.io/badge/Google_Gemini_2.5_Flash-4285F4?style=for-the-badge&logo=googlegemini&logoColor=white"/>
<img src="https://img.shields.io/badge/TFLite_(ai_edge_litert)-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenCV-5C3EE8?style=for-the-badge&logo=opencv&logoColor=white"/>
<br>
<img src="https://img.shields.io/badge/Firebase_Firestore-FFCA28?style=for-the-badge&logo=firebase&logoColor=black"/>
<img src="https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
<br>
<img src="https://img.shields.io/badge/Twilio-F22F46?style=for-the-badge&logo=twilio&logoColor=white"/>
<img src="https://img.shields.io/badge/gTTS-4285F4?style=for-the-badge&logo=google&logoColor=white"/>
<img src="https://img.shields.io/badge/OpenWeatherMap-EB6E4B?style=for-the-badge&logo=openweathermap&logoColor=white"/>
<br>
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white"/>
<img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white"/>
<img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black"/>
<br>
<img src="https://img.shields.io/badge/Render-46E3B7?style=for-the-badge&logo=render&logoColor=000000"/>
</div>

<br><br>


<div align="center">
<img src="https://img.shields.io/badge/%20ARCHITECTURE%20-1F2937?style=for-the-badge&logoColor=black&labelColor=F5F5DC&color=F5F5DC"/>
</div>
<br/>

<div align="center">

<table>
<tr>
<td align="center" bgcolor="#166534" width="700">
<font color="#F5F5DC"><b>🌾 Flask Backend (app.py)</b><br/><sub>main router · lifecycle · DB triggers</sub></font>
</td>
</tr>
</table>

<sub>▼&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;▼</sub>

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

<br><br>

<div align="center">

<img src="https://img.shields.io/badge/GETTING%20STARTED-2563EB?style=for-the-badge&labelColor=2563EB&color=2563EB&logoColor=white"/>

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
<br><br>
<br>
<br>
<div align="center">
<img src="https://img.shields.io/badge/SCREENSHOTS-8E24AA?style=for-the-badge&labelColor=8E24AA&color=8E24AA&logoColor=white"/>
</div>
<br/>

<div align="center">

<table>
<tr>
<td align="center" width="50%">
<b>🌐 Multilingual Dashboard</b><br/><br/>
<img src="assets/screenshots/dashboard.png" width="100%"/>
</td>
<td align="center" width="50%">
<b>🩺 Crop Disease Detection & Pesticide Recommendation</b><br/><br/>
<img src="assets/screenshots/crop-disease-detection.png" width="100%"/>
</td>
</tr>
<tr>
<td align="center" width="50%">
<b>☎️ IVR Helpline — English</b><br/><br/>
<img src="assets/screenshots/ivr-english.png" width="100%"/>
</td>
<td align="center" width="50%">
<b>☎️ IVR Helpline — Hindi</b><br/><br/>
<img src="assets/screenshots/ivr-hindi.png" width="100%"/>
</td>
</tr>
<tr>
<td align="center" colspan="2">
<b>🔍 Pesticide Product Verification (CIB&RC)</b><br/><br/>
<img src="assets/screenshots/product-verification.png" width="60%"/>
</td>
</tr>
</table>
<br>

</div>
<div align="center">

<img src="https://img.shields.io/badge/WHY%20THIS%20MATTERS-2E7D32?style=for-the-badge&labelColor=2E7D32&color=2E7D32&logoColor=white"/>

</div>

<br/>

- **Zero-internet fallbacks** — the real Twilio IVR hotline lets farmers with feature phones (no internet) access crop diagnosis and mandi data
- **Offline TFLite integration** — disease diagnosis runs on a compressed, low-memory 7.4 MB TFLite interpreter instead of a resource-heavy deep learning runtime, keeping backend deployment cheap and fast
- **True multilingual sync** — handles both static UI labels and dynamic feeds (weather descriptions, crop advisory headings, scan details) across 13 native Indian languages
- **Anti-fail key rotation** — automatically rotates Gemini keys on API errors to prevent standard rate-limit blocks

**Known limitations:**
- gTTS does not support voice synthesis for Odia (`or`) and Assamese (`as`) — chatbot defaults to visual text output for these
- Free-tier Gemini API is limited to 20 requests/minute; mitigated with dictionary caches, but not eliminated

<br><br>


<br>

<div align="center">

<div align="center">

<img src="https://img.shields.io/badge/BUILT%20BY-Nandini%20Singh-2E7D32?style=for-the-badge&labelColor=14532D&color=2E7D32"/>

<br><br>

<b>Pre Final-Year B.Tech Student in Artificial Intelligence & Machine Learning</b><br>
Indore Institute of Science and Technology, Indore

<br><br>

<a href="www.linkedin.com/in/nandinisingh10">
<img src="https://img.shields.io/badge/LinkedIn-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white"/>
</a>

<a href="https://github.com/Nandinisingh07">
<img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white"/>
</a>

<a href="mailto:nandinii.singh07@gmail.com">
<img src="https://img.shields.io/badge/Email-EA4335?style=for-the-badge&logo=gmail&logoColor=white"/>
</a>

</div>
<br/><br/>

<img src="https://capsule-render.vercel.app/api?type=waving&color=0:65A30D,50:15803D,100:14532D&height=100&section=footer" width="100%"/>

</div>
