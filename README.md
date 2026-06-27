# 🌾 Kisan Saathi (किसान साथी)

Kisan Saathi is an AI-powered agricultural intelligence platform designed to support farmers with crop disease diagnosis, real-time Mandi market rates, weather forecasting, interactive AI chatbot assistance, and simulated IVR call center integration. 

The platform supports multiple regional languages, voice synthesis, and preserves farmer privacy.

---

## 📁 Project Structure

```text
skill development for farmers/
├── app.py                      # Main Flask Backend (APIs and Routing)
├── crop_disease_model.h5       # Keras Deep Learning Model (Leaf disease classification)
├── firebase_key.json           # Firebase credentials file (Firestore verification)
├── mandi_prices.csv            # Mandi market prices database (MP district rates)
├── static/
│   ├── css/
│   │   └── theme.css           # Design system (glassmorphism, light/dark themes)
│   ├── js/
│   │   ├── translations.js     # Client-side translation engine (5 languages)
│   │   ├── toast.js            # Global toast notifications
│   │   ├── nav.js              # Navigation and dynamic weather widget
│   │   ├── scan.js             # Camera client, cropping, and API sender
│   │   ├── market.js           # Datatable filters, search, and Chart.js graphics
│   │   ├── chat.js             # Voice/Text chatbot interface with auto audio response
│   │   └── ivr.js              # Metrics updater and Helpline call simulator
│   └── audio/                  # Cached synthesized chat speech files (MP3s)
└── templates/
    ├── base.html               # Shared layout (Header, Nav, language switcher, marquee)
    ├── index.html              # Farmer Dashboard (status overview & advisory widgets)
    ├── scan.html               # Crop leaf scanner & QR authentication page
    ├── market.html             # Mandi tracking and land type crop recommendations
    ├── chat.html               # Voice-enabled conversational AI chatbot page
    ├── ivr.html                # Helpline Call Flow & Simulator
    └── settings.html           # Farmer Profile, city defaults, and system thresholds
```

---

## 🚀 Key Features

1. **Aesthetic Unified Layout**: Custom styles using deep agricultural greens, warm golds, and glassmorphic card designs responsive from desktop down to 375px mobile screens. Fully supports dark mode toggling.
2. **Multilingual translation engine**: Client-side dictionary translating all page content on the fly into **Hindi, English, Marathi, Gujarati, and Bengali**, while keeping dual English/regional subtitles readable.
3. **AI Speech Assistant**: Voice-enabled chatbot that accepts voice input and responds with translated text and auto-generated spoken voice prompts in the selected language using **gTTS (Google Text-to-Speech)**.
4. **AgriScan AI Leaf diagnosis**: Uses `crop_disease_model.h5` globally at startup to diagnose 16 classes of potato, tomato, and pepper bell leaf infections, offering local expert pesticide recommendations.
5. **QR Code Verification**: Scans product QR codes and queries Firebase Firestore to authenticate genuine fertilizers and pesticides from registered manufacturers.
6. **Helpline & Privacy Protection**: Masked logs to protect user contact information while displaying active IVR helpline tracking logs.
7. **Interactive Mandi Rates & Exporter**: Employs Chart.js to display trending commodity price curves, recommends optimal crops based on land properties (dry/wet), and exports custom data tables to CSV reports.

---

## 🛠️ Setup & Installation

### Prerequisites
Make sure you have **Python 3.8+** installed.

### 1. Install Dependencies
Install all required libraries for the Flask app and AI model running:
```bash
pip install flask flask-session numpy pandas pillow opencv-python gtts firebase-admin requests tensorflow
```

### 2. Prepare Data Files
Verify the following files are present in the root folder:
* `crop_disease_model.h5` (TensorFlow model)
* `mandi_prices.json` or `mandi_prices.csv` (For market API)
* `firebase_key.json` (For QR code authentication API)

---

## 🏃 Running the Application

To start the Flask development server:

```bash
python app.py
```

The application will start in the background and can be accessed at:
👉 **`http://127.0.0.1:5000/`**

---

## 📄 License
This project is developed for farmer empowerment and skill development.
