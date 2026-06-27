# Setup Guide — Kisan Saathi (किसान साथी)

Follow this guide to get the Kisan Saathi end-to-end integration running locally.

---

## 🛠️ Step 1: Install Dependencies
Run the following pip install command to download all required packages:
```bash
pip install -r requirements.txt
```

---

## 🔑 Step 2: Configure Environment Keys
1. Copy the `.env.example` file and rename it to `.env`:
   ```bash
   copy .env.example .env
   ```
2. Fill in the following credentials:
   - `OPENWEATHER_API_KEY`: Key from [OpenWeatherMap](https://openweathermap.org/).
   - `GEMINI_API_KEY`: Key from [Google AI Studio](https://aistudio.google.com/).
   - `FLASK_SECRET_KEY`: Set to a strong random sequence.

---

## 💾 Step 3: Seed the Databases

### 1. Firestore Database (For QR Authentications)
Verify `firebase_key.json` is present in the root folder, then execute the seed script:
```bash
python seed_firestore.py
```
This populates 10 sample verified products (ranging from Urea, bio-pesticides, to expired seed logs) directly into your Firestore project database.

### 2. SQLite Helpline database (For IVR Simulator logs)
The SQLite schema `ivr_logs.db` is initialized automatically when you boot the server for the first time, loading 3 baseline logs onto the call centre logs page.

---

## 🚜 Step 4: CLI Commands
To manually trigger the Mandi price update script and write the fluctuated rates into `mandi_prices.csv`:
```bash
flask fetch-mandi
```
*Note: Make sure your terminal session directory is in the workspace root.*

---

## 🏃 Step 5: Start the Server
Start the application factory runner:
```bash
python run.py
```

The application will start on:
👉 **`http://127.0.0.1:5000/`**

---

## 📂 Logs and Monitoring
Check the rotating logs at:
📁 **`logs/kisan_saathi.log`** for timestamps, inference timings, query details, and internal API exceptions.
