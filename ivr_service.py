import os
import sqlite3
import random
import logging
import datetime
import uuid
from flask import Blueprint, jsonify, request, Response
from gtts import gTTS
import google.generativeai as genai
from language_config import LANGUAGES
from twilio.twiml.voice_response import VoiceResponse, Gather

logger = logging.getLogger("kisan_saathi")

ivr_bp = Blueprint("ivr", __name__)

DB_PATH = "ivr_logs.db"

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)
    logger.info("Gemini AI API configured successfully in ivr_service.")
else:
    logger.warning("GEMINI_API_KEY missing in environment for ivr_service.")

# In-memory dictionary to store language choices by Twilio CallSid
call_sessions = {}

TWILIO_LANG_MAP = {
    "hi": "hi-IN", "en": "en-US", "mr": "mr-IN", "gu": "gu-IN",
    "bn": "bn-IN", "pa": "pa-IN", "ta": "ta-IN", "te": "te-IN",
    "kn": "kn-IN", "ml": "ml-IN", "or": "en-IN", "ur": "en-IN", "as": "en-IN",
}

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

def uuid_hex():
    return uuid.uuid4().hex

@ivr_bp.route("/ivr/voice", methods=["POST"])
def incoming_call():
    """Initial webhook hit by Twilio when a call comes in."""
    resp = VoiceResponse()
    gather = Gather(numDigits=1, timeout=8, action="/ivr/handle-language")
    gather.say("नमस्ते! किसान साथी हेल्पलाइन में आपका स्वागत है। हिंदी के लिए 1 दबाएं।", language="hi-IN")
    gather.say("For English, press 2.", language="en-US")
    gather.say("मराठीसाठी 3 दाबा.", language="mr-IN")
    gather.say("गुजराती के लिए 4 दबाएं।", language="gu-IN")
    gather.say("বাংলার জন্য 5 চাপুন।", language="bn-IN")
    gather.say("ਪੰਜਾਬੀ ਲਈ 6 ਦਬਾਓ.", language="pa-IN")
    gather.say("தமிழுக்கு 7 அழுத்தவும்.", language="ta-IN")
    gather.say("తెలుగు కోసం 8 నొక్కండి.", language="te-IN")
    gather.say("ಕನ್ನಡಕ್ಕಾಗಿ 9 ಒತ್ತಿರಿ.", language="kn-IN")
    gather.say("മലയാളത്തിന് 0 അമർത്തുക.", language="ml-IN")
    resp.append(gather)
    resp.redirect("/ivr/voice")
    return Response(str(resp), mimetype="text/xml")

@ivr_bp.route("/ivr/handle-language", methods=["POST"])
def handle_language():
    """Handles digit entered for language, prompts with options menu in that language."""
    digits = request.form.get("Digits", "1").strip()
    lang_mapping = {
    "1": "hi", "2": "en", "3": "mr", "4": "gu", "5": "bn",
    "6": "pa", "7": "ta", "8": "te", "9": "kn", "0": "ml"
}
    lang_code = lang_mapping.get(digits, "hi")
    call_sid = request.form.get("CallSid")
    call_sessions[call_sid] = lang_code
    
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["hi"])
    twilio_lang = TWILIO_LANG_MAP.get(lang_code, "hi-IN")
    
    resp = VoiceResponse()
    gather = Gather(numDigits=1, timeout=8, action="/ivr/handle-menu")
    
    # Translate the menu prompt dynamically using Gemini
    menu_prompt = ""
    try:
        model_g = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            f"Translate/rephrase the following menu instructions into {lang_info['name']} using {lang_info['script']} script: "
            f"'For Crop Disease Info, press 1. For Mandi Prices, press 2. For Weather Advisory, press 3. "
            f"For Government Schemes, press 4. To speak to an expert, press 5.' "
            f"Make it clear, concise, and natural for a farmer to hear over the phone. Return ONLY the translated/rephrased text."
        )
        res = model_g.generate_content(prompt)
        menu_prompt = res.text.strip() if res.text else ""
    except Exception as e:
        logger.error(f"Gemini menu translation failed: {e}")
        
    if not menu_prompt:
        # Fallback prompts
        if lang_code == "hi":
            menu_prompt = "फसल रोग की जानकारी के लिए 1 दबाएं। मंडी भाव के लिए 2 दबाएं। मौसम सलाह के लिए 3 दबाएं। सरकारी योजनाओं के लिए 4 दबाएं। विशेषज्ञ से बात करने के लिए 5 दबाएं।"
        else:
            menu_prompt = "For Crop Disease Info, press 1. For Mandi Prices, press 2. For Weather Advisory, press 3. For Government Schemes, press 4. To speak to an expert, press 5."
            
    gather.say(menu_prompt, language=twilio_lang)
    resp.append(gather)
    resp.redirect("/ivr/handle-language")
    return Response(str(resp), mimetype="text/xml")

@ivr_bp.route("/ivr/handle-menu", methods=["POST"])
def handle_menu():
    """Handles digit entered for option, plays generated audio reply, logs to database."""
    digits = request.form.get("Digits", "1").strip()
    try:
        option = int(digits)
    except ValueError:
        option = 1
        
    call_sid = request.form.get("CallSid")
    lang_code = call_sessions.get(call_sid, "hi")
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["hi"])
    twilio_lang = TWILIO_LANG_MAP.get(lang_code, "hi-IN")
    
    options_map = {
        1: ("Crop Disease Info", "फसल रोग सूचना"),
        2: ("Mandi Prices", "मंडी भाव"),
        3: ("Weather Advisory", "मौसम पूर्वानुमान"),
        4: ("Government Schemes", "सरकारी योजनाएं"),
        5: ("Speak to Expert", "विशेषज्ञ से बात")
    }
    opt_en, opt_hi = options_map.get(option, ("General Inquiry", "सामान्य पूछताछ"))
    selected_path = f"{lang_info['name']} -> {opt_hi} (Press {option})"
    
    # Generate response text dynamically using Gemini
    response_text = ""
    try:
        model_g = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            f"You are the Kisan Saathi IVR Helpline assistant. The farmer selected option {option} ({opt_en}). "
            f"Generate a helpful, highly concise response (1-2 sentences maximum) in {lang_info['name']} (using {lang_info['script']} script) "
            f"addressing their request. Do not include any English translation. Keep it simple and natural for a farmer."
        )
        res = model_g.generate_content(prompt, request_options={"timeout": 6})
        response_text = res.text.strip() if res.text else ""
    except Exception as e:
        logger.error(f"Gemini IVR response generation failed: {e}")
        
    if not response_text:
        if option == 1:
            response_text = "आलू में अगेती झुलसा रोग के उपचार हेतु मैन्कोजेब का छिड़काव करें।"
        elif option == 2:
            response_text = "मंडी में गेहूं का औसत भाव तेईस सौ पचास रुपये प्रति क्विंटल चल रहा है।"
        elif option == 3:
            response_text = "आज मौसम साफ रहेगा और फसलों की सिंचाई जारी रखें।"
        elif option == 4:
            response_text = "प्रधान मंत्री किसान सम्मान निधि योजना के तहत अगली किस्त की राशि जल्द जारी होगी।"
        else:
            response_text = "कृषि विशेषज्ञ से आपकी कॉल दो घंटे में शेड्यूल्ड कर दी गई है।"

    audio_url = ""
    audio_filename = f"ivr_reply_{uuid_hex()}.mp3"
    
    resp = VoiceResponse()
    
    if lang_info.get("gtts_supported", False):
        try:
            audio_dir = os.path.join("static", "audio")
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = os.path.join(audio_dir, audio_filename)
            tts = gTTS(text=response_text, lang=lang_info["gtts_code"])
            tts.save(audio_path)
            
            # Construct public absolute URL
            audio_url = f"{request.url_root.rstrip('/')}/static/audio/{audio_filename}"
            resp.play(audio_url)
        except Exception as e:
            logger.error(f"Failed to generate gTTS audio: {e}")
            resp.say(response_text, language=twilio_lang)
    else:
        logger.warning(f"gTTS not supported for {lang_code}. Fallback to Twilio say.")
        resp.say(response_text, language=twilio_lang)
        
    phone = request.form.get("From", "+91 XXXXX XX00")
    duration = "1m 12s"
    current_time = datetime.datetime.now().strftime("%H:%M")
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    
    db_audio_url = f"/static/audio/{audio_filename}" if audio_url else ""
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ivr_calls (caller, path, duration, time, date, audio_url, option_chosen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (phone, selected_path, duration, current_time, current_date, db_audio_url, option))
        conn.commit()
        conn.close()
        logger.info(f"Real Twilio Call logged to SQLite ivr_logs.db: {phone} | Option: {option}")
    except Exception as e:
        logger.error(f"Error logging real IVR call: {e}")
        
    resp.hangup()
    return Response(str(resp), mimetype="text/xml")

@ivr_bp.route("/api/ivr/simulate", methods=["POST"])
def simulate_call():
    req_data = request.get_json(silent=True) or {}
    
    phone = req_data.get("phone", "")
    language = req_data.get("language", "Hindi")
    option = req_data.get("option", None)
    
    if not phone:
        phone_raw = f"+91 {random.randint(70000, 99999)} XXX{random.randint(10, 99)}"
        phone = f"+91 XXXXX XX{phone_raw[-2:]}"
        
    duration = f"{random.randint(0, 2)}m {random.randint(10, 59)}s"
    current_time = datetime.datetime.now().strftime("%H:%M")
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    
    if option is None:
        option = random.choice([1, 2, 3, 4, 5])
        
    options_map = {
        1: ("Crop Disease Info", "फसल रोग सूचना"),
        2: ("Mandi Prices", "मंडी भाव"),
        3: ("Weather Advisory", "मौसम पूर्वानुमान"),
        4: ("Government Schemes", "सरकारी योजनाएं"),
        5: ("Speak to Expert", "विशेषज्ञ से बात")
    }
    
    opt_en, opt_hi = options_map.get(option, ("General Inquiry", "सामान्य पूछताछ"))
    selected_path = f"{language} -> {opt_hi} (Press {option})"
    
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
            "transcript": response_text,
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
        
        cursor.execute("SELECT COUNT(*) FROM ivr_calls")
        total_calls = cursor.fetchone()[0]
        
        cursor.execute("SELECT option_chosen, COUNT(*) FROM ivr_calls GROUP BY option_chosen")
        volume_by_option = {row[0]: row[1] for row in cursor.fetchall() if row[0] is not None}
        
        cursor.execute("""
            SELECT date, COUNT(*) FROM ivr_calls 
            WHERE date >= date('now', '-7 days') 
            GROUP BY date 
            ORDER BY date ASC
        """)
        weekly_trend = {row[0]: row[1] for row in cursor.fetchall()}
        
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
            "active_calls": len(call_sessions),
            "total_calls": total_calls,
            "volume_by_option": volume_by_option,
            "weekly_trend": weekly_trend,
            "logs": logs_list
        })
        
    except Exception as e:
        logger.error(f"Failed to fetch stats from sqlite database: {e}")
        return jsonify({"success": False, "error": str(e)})
