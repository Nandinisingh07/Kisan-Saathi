import os
import sqlite3
import random
import logging
import datetime
from flask import Blueprint, jsonify, request
from gtts import gTTS

logger = logging.getLogger("kisan_saathi")

ivr_bp = Blueprint("ivr", __name__)

DB_PATH = "ivr_logs.db"

def init_db():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ivr_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                caller TEXT NOT NULL,
                path TEXT NOT NULL,
                duration TEXT NOT NULL,
                time TEXT NOT NULL,
                date TEXT NOT NULL,
                audio_url TEXT NOT NULL,
                option_chosen INTEGER
            )
        """)
        conn.commit()
        
        # Seed initial records if empty to ensure dashboard and stats page look premium
        cursor.execute("SELECT COUNT(*) FROM ivr_calls")
        if cursor.fetchone()[0] == 0:
            initial_records = [
                ("+91 XXXXX XX399", "Hindi -> Mandi (Press 2)", "1m 24s", "15:10", "2026-06-27", "/static/audio/mandi_hi.mp3", 2),
                ("+91 XXXXX XX841", "Hindi -> Weather (Press 3)", "0m 45s", "14:42", "2026-06-27", "/static/audio/weather_hi.mp3", 3),
                ("+91 XXXXX XX012", "English -> Crop Disease (Press 1)", "2m 10s", "12:15", "2026-06-27", "/static/audio/crop_en.mp3", 1)
            ]
            cursor.executemany("""
                INSERT INTO ivr_calls (caller, path, duration, time, date, audio_url, option_chosen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, initial_records)
            conn.commit()
            logger.info("SQLite database seeded with initial IVR logs.")
        conn.close()
    except Exception as e:
        logger.error(f"Error initializing SQLite ivr_logs.db database: {e}")

# Call init_db on import
init_db()

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@ivr_bp.route("/api/ivr/simulate", methods=["POST"])
def simulate_call():
    req_data = request.get_json(silent=True) or {}
    
    # If parameters aren't supplied, simulate an incoming random caller
    phone = req_data.get("phone", "")
    language = req_data.get("language", "Hindi")
    option = req_data.get("option", None)
    
    if not phone:
        # Generate random masked caller phone
        phone_raw = f"+91 {random.randint(70000, 99999)} XXX{random.randint(10, 99)}"
        # Store masked phone: +91 XXXXX XX{last 4 digits}
        phone = f"+91 XXXXX XX{phone_raw[-2:]}"
        
    duration = f"{random.randint(0, 2)}m {random.randint(10, 59)}s"
    current_time = datetime.datetime.now().strftime("%H:%M")
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    
    if option is None:
        option = random.choice([1, 2, 3, 4, 5])
        
    # Option mappings
    options_map = {
        1: ("Crop Disease Info", "फसल रोग सूचना"),
        2: ("Mandi Prices", "मंडी भाव"),
        3: ("Weather Advisory", "मौसम पूर्वानुमान"),
        4: ("Government Schemes", "सरकारी योजनाएं"),
        5: ("Speak to Expert", "विशेषज्ञ से बात")
    }
    
    opt_en, opt_hi = options_map.get(option, ("General Inquiry", "सामान्य पूछताछ"))
    selected_path = f"{language} -> {opt_hi} (Press {option})"
    
    # Generate realistic response text based on options
    response_text = ""
    audio_filename = f"ivr_reply_{uuid_hex()}.mp3"
    
    if option == 1:
        response_text = "आलू में अगेती झुलसा रोग के उपचार हेतु मैन्कोजेब (Mancozeb 2g/L) का छिड़काव करें। (For Potato Early Blight, spray Mancozeb.)"
    elif option == 2:
        response_text = "इंदौर मंडी में गेहूं का औसत भाव तेईस सौ पचास रुपये प्रति क्विंटल चल रहा है। (Wheat modal price is 2,350 Rs/quintal.)"
    elif option == 3:
        response_text = "इंदौर क्षेत्र में आज मौसम साफ रहेगा और फसलों की सिंचाई जारी रखें। (Weather is clear in Indore today, irrigate crops.)"
    elif option == 4:
        response_text = "प्रधान मंत्री किसान सम्मान निधि योजना के तहत अगली किस्त की राशि जल्द जारी होगी। (Next PM-Kisan installation is coming soon.)"
    elif option == 5:
        response_text = "कृषि विशेषज्ञ से आपकी कॉल दो घंटे में शेड्यूल्ड कर दी गई है। (An expert callback is scheduled for you in 2 hours.)"
        
    # Generate the spoken audio for the caller response
    audio_url = "/static/audio/mandi_hi.mp3"
    try:
        audio_dir = os.path.join("static", "audio")
        os.makedirs(audio_dir, exist_ok=True)
        audio_path = os.path.join(audio_dir, audio_filename)
        lang_code = "en" if language.lower() == "english" else "hi"
        tts = gTTS(text=response_text, lang=lang_code)
        tts.save(audio_path)
        audio_url = f"/static/audio/{audio_filename}"
    except Exception as e:
        logger.error(f"Failed to generate IVR speech audio: {e}")

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ivr_calls (caller, path, duration, time, date, audio_url, option_chosen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (phone, selected_path, duration, current_time, current_date, audio_url, option))
        conn.commit()
        conn.close()
        
        logger.info(f"Log registered in SQLite ivr_logs.db: {phone} | Option: {option}")
        return jsonify({
            "success": True,
            "message": response_text,
            "audio_url": audio_url
        })
    except Exception as e:
        logger.error(f"Error logging simulated call: {e}")
        return jsonify({"success": False, "error": str(e)})

@ivr_bp.route("/api/ivr/stats")
def get_stats():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 1. Total call counts
        cursor.execute("SELECT COUNT(*) FROM ivr_calls")
        total_calls = cursor.fetchone()[0]
        
        # 2. Call volume by option
        cursor.execute("SELECT option_chosen, COUNT(*) FROM ivr_calls GROUP BY option_chosen")
        volume_by_option = {row[0]: row[1] for row in cursor.fetchall() if row[0] is not None}
        
        # 3. Weekly trend (calls in last 7 days)
        cursor.execute("""
            SELECT date, COUNT(*) FROM ivr_calls 
            WHERE date >= date('now', '-7 days') 
            GROUP BY date 
            ORDER BY date ASC
        """)
        weekly_trend = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 4. Fetch the log list to populate caller grid
        cursor.execute("SELECT caller, path, duration, time, date, audio_url FROM ivr_calls ORDER BY id DESC LIMIT 20")
        rows = cursor.fetchall()
        logs_list = []
        for r in rows:
            logs_list.append({
                "caller": r["caller"],
                "path": r["path"],
                "duration": r["duration"],
                "time": r["time"],
                "audio_url": r["audio_url"]
            })
            
        conn.close()
        
        return jsonify({
            "success": True,
            "active_calls": random.randint(1, 3), # Dynamic simulation metric
            "total_calls": total_calls,
            "volume_by_option": volume_by_option,
            "weekly_trend": weekly_trend,
            "logs": logs_list
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch stats from sqlite database: {e}")
        return jsonify({"success": False, "error": str(e)})

def uuid_hex():
    return uuid.uuid4().hex

import uuid
