import os
import time
import uuid
import glob
import logging
from flask import Blueprint, jsonify, request
import google.generativeai as genai
from gtts import gTTS
from langdetect import detect

logger = logging.getLogger("kisan_saathi")

chat_bp = Blueprint("chat", __name__)

# Configure Google Gemini API key
api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    genai.configure(api_key=api_key)
    logger.info("Gemini AI API configured successfully.")
else:
    logger.warning("GEMINI_API_KEY missing in environment. Chatbot will run in fallback rule-based mode.")

SYSTEM_INSTRUCTION = (
    "You are Kisan Saathi, an expert Indian agricultural assistant. "
    "Answer only about farming, crops, soil, weather, pests, government schemes, and market prices. "
    "Reply in the same language the user writes in (Hindi, English, Marathi, Gujarati, or Bengali). "
    "Be concise, practical, and use simple language suitable for farmers. Limit answers to 3-4 sentences."
)

def clean_old_audio_files():
    """Deletes cached audio files older than 1 hour in static/audio/."""
    try:
        now = time.time()
        audio_dir = os.path.join("static", "audio")
        os.makedirs(audio_dir, exist_ok=True)
        files = glob.glob(os.path.join(audio_dir, "chat_reply_*.mp3"))
        deleted_count = 0
        for f in files:
            # 1 hour = 3600 seconds
            if os.stat(f).st_mtime < now - 3600:
                os.remove(f)
                deleted_count += 1
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} cached audio files older than 1 hour.")
    except Exception as e:
        logger.error(f"Error during audio file cleanup: {e}")

# Register scheduler job for cleanup
def start_cleanup_scheduler(scheduler):
    scheduler.add_job(func=clean_old_audio_files, trigger="interval", hours=1)
    logger.info("Audio cleanup job registered.")

@chat_bp.route("/api/chat", methods=["POST"])
def chat_response():
    # Run cleanup checks occasionally
    clean_old_audio_files()
    
    req_data = request.get_json()
    if not req_data or "message" not in req_data:
        return jsonify({"success": False, "error": "No query message sent"})

    query = req_data["message"]
    # Handle both 'lang' and 'language' request keys
    lang = req_data.get("lang", req_data.get("language", "")).strip()
    history = req_data.get("history", [])

    # Language detection fallback using langdetect
    if not lang:
        try:
            detected = detect(query)
            # Map standard codes to supported ones
            if detected in ["hi", "mr", "gu", "bn", "en"]:
                lang = detected
            else:
                lang = "hi"  # Default
        except Exception:
            lang = "hi"

    # Define language maps for translation fallback
    lang_names = {
        "hi": "Hindi",
        "mr": "Marathi",
        "gu": "Gujarati",
        "bn": "Bengali",
        "en": "English"
    }

    reply_target = ""
    reply_en = ""
    success = False

    # 1. Use Gemini API if configured
    if api_key:
        try:
            # Build conversation history
            contents = []
            for h in history:
                role = "user" if h.get("sender") == "user" else "model"
                contents.append({"role": role, "parts": [h.get("text", "")]})
            contents.append({"role": "user", "parts": [query]})

            model = genai.GenerativeModel(
                model_name="gemini-1.5-flash",
                system_instruction=SYSTEM_INSTRUCTION
            )
            
            logger.info(f"Sending prompt to Gemini: '{query}' in language: {lang_names.get(lang, lang)}")
            response = model.generate_content(contents)
            
            if response.text:
                reply_target = response.text.strip()
                success = True
                
                # Fetch English translation for comparison panel
                trans_model = genai.GenerativeModel("gemini-1.5-flash")
                en_response = trans_model.generate_content(
                    f"Translate the following agricultural text to English concisely: {reply_target}"
                )
                reply_en = en_response.text.strip() if en_response.text else reply_target
                
        except Exception as e:
            logger.error(f"Gemini API generation failed: {e}")

    # 2. Fallback rule-based system if Gemini key is missing or failed
    if not success:
        logger.info("Executing local rule-based chatbot fallback...")
        query_lower = query.lower()
        if "weather" in query_lower or "मौसम" in query_lower or "बारिश" in query_lower:
            reply_hi = "इंदौर क्षेत्र में आज मौसम सुहाना है। तापमान 32 डिग्री सेल्सियस के आसपास रहेगा, बारिश की कोई संभावना नहीं है।"
            reply_en = "Indore region weather is pleasant today. Temperature is around 32°C, with 0% chance of precipitation."
        elif "mandi" in query_lower or "भाव" in query_lower or "कीमत" in query_lower or "गेहूं" in query_lower:
            reply_hi = "इंदौर मंडी में सोयाबीन का औसत भाव ₹4650 प्रति क्विंटल और गेहूं का भाव ₹2350 प्रति क्विंटल चल रहा है।"
            reply_en = "Indore Mandi rate of Soyabean is ₹4,650/quintal and Wheat is ₹2,350/quintal."
        elif "disease" in query_lower or "रोग" in query_lower or "पत्ती" in query_lower:
            reply_hi = "यदि आपकी फसल की पत्तियों पर काले धब्बे दिख रहे हैं, तो यह अर्ली ब्लाइट हो सकता है। नियंत्रण के लिए मैन्कोजेब (Mancozeb) का छिड़काव करें।"
            reply_en = "If leaves display black concentric spots, it could be Early Blight. Spray Mancozeb pesticide to treat it."
        elif "hello" in query_lower or "hi" in query_lower or "नमस्ते" in query_lower:
            reply_hi = "नमस्ते किसान भाई! मैं किसान साथी ए.आई. सहायक हूँ। मैं आपकी क्या मदद कर सकता हूँ?"
            reply_en = "Hello! I am your Kisan Saathi AI assistant. How can I help you today?"
        else:
            reply_hi = "मंडी भाव जानने के लिए 'मंडी', मौसम के लिए 'मौसम' या फसल रोगों के उपचार के लिए 'रोग' लिखकर पूछें।"
            reply_en = "Ask about market prices by saying 'mandi', weather forecast by saying 'weather', or crop leaf infections by saying 'disease'."

        # Translate using googletrans or return defaults
        if lang == "en":
            reply_target = reply_en
        elif lang == "hi":
            reply_target = reply_hi
        else:
            try:
                from googletrans import Translator
                translator = Translator()
                reply_target = translator.translate(reply_en, src='en', dest=lang).text
            except Exception:
                reply_target = reply_hi
        reply_en = reply_en
        success = True

    # 3. Synthesize Speech audio if reply length < 300 chars
    audio_url = None
    if len(reply_target) < 300:
        try:
            filename = f"chat_reply_{uuid.uuid4().hex}.mp3"
            audio_dir = os.path.join("static", "audio")
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = os.path.join(audio_dir, filename)
            
            # gTTS synthesis
            tts = gTTS(text=reply_target, lang=lang)
            tts.save(audio_path)
            audio_url = f"/static/audio/{filename}"
            logger.info(f"Synthesized chat audio for language locale '{lang}': {audio_url}")
        except Exception as e:
            logger.error(f"Failed to generate TTS audio: {e}")

    return jsonify({
        "success": True,
        "reply": reply_target,          # For API task specifications
        "reply_hi": reply_target,       # For scan.js / chat.js frontend display
        "reply_en": reply_en,           # For bilingual side-by-side translation
        "audio_url": audio_url
    })
