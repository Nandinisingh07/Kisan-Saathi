import os
import time
import uuid
import glob
import logging
import json
from flask import Blueprint, jsonify, request
import google.generativeai as genai
from gtts import gTTS
from langdetect import detect
from language_config import LANGUAGES

logger = logging.getLogger("kisan_saathi")

chat_bp = Blueprint("chat", __name__)

# Simple in-memory response cache to prevent API rate limiting on repeated demo runs (TTL = 10 minutes)
chat_cache = {}

# Configure Google Gemini API key
api_key = os.getenv("GEMINI_API_KEY", "")
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Startup check: list available models to verify API key validity
        available_models = [m.name for m in genai.list_models()]
        logger.info(f"Gemini AI API configured successfully. Available models: {available_models}")
    except Exception as e:
        logger.error(f"Gemini startup validation failed: {e}")
else:
    logger.warning("GEMINI_API_KEY missing in environment. Chatbot will run in fallback rule-based mode.")

SYSTEM_INSTRUCTION = (
    "You are Kisan Saathi, an expert Indian agricultural assistant serving farmers in Madhya Pradesh. "
    "Answer questions about: crop diseases and pest management, soil health and fertilizers, weather-based farming decisions, "
    "government schemes (PM-Kisan, crop insurance, subsidies), market/mandi prices and selling decisions, irrigation and water management, "
    "seed selection, and post-harvest storage. "
    "If a farmer describes symptoms (e.g. 'my wheat leaves are turning yellow'), ask ONE clarifying question if needed "
    "(e.g. crop stage, recent weather) rather than guessing, then give a specific, actionable answer — not a generic one. "
    "Reply in the same language the user writes in. Be concise and practical: 3-5 sentences, simple vocabulary suitable for a farmer with basic literacy. "
    "If the question is outside agriculture, politely redirect to what you can help with. "
    "Respond ONLY as a valid JSON object matching this structure: "
    "{\"answer\": \"<response in the user's language>\", \"answer_en\": \"<concise English translation of the same response>\"}. "
    "Do not include any markdown formatting, backticks, or extra text in your output."
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
            if detected in LANGUAGES:
                lang = detected
            else:
                lang = "hi"  # Default
        except Exception:
            lang = "hi"

    reply_target = ""
    reply_en = ""
    success = False
    query_key = f"{query.strip().lower()}_{lang}"

    # Check cache (10 mins = 600s TTL)
    if query_key in chat_cache:
        cached = chat_cache[query_key]
        if time.time() - cached["timestamp"] < 600:
            logger.info(f"Serving cached Gemini response for query: '{query}' in lang: {lang}")
            # Generate new audio file occasionally if required, or reuse the cached audio URL
            audio_url = cached["audio_url"]
            return jsonify({
                "success": True,
                "reply": cached["reply_target"],
                "reply_hi": cached["reply_target"],
                "reply_en": cached["reply_en"],
                "audio_url": audio_url
            })

    # 1. Use Gemini API if configured
    if api_key:
        lang_info = LANGUAGES.get(lang, LANGUAGES["hi"])
        lang_instruction = f"Reply ONLY in {lang_info['name']}, using {lang_info['script']} script. Keep it simple, farmer-friendly, max 3-5 sentences."
        dynamic_system_instruction = f"{SYSTEM_INSTRUCTION} {lang_instruction}"
        
        # Build conversation history
        contents = []
        for h in history:
            role = "user" if h.get("sender") == "user" else "model"
            contents.append({"role": role, "parts": [h.get("text", "")]})
        contents.append({"role": "user", "parts": [query]})

        retries = 2
        for attempt in range(retries):
            try:
                logger.info(f"Sending prompt to Gemini (attempt {attempt+1}): '{query}' in language: {lang_info['name']}")
                model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    system_instruction=dynamic_system_instruction
                )
                response = model.generate_content(contents)
                
                if response.text:
                    text = response.text.strip()
                    # Strip markdown block if model outputted it
                    if text.startswith("```json"):
                        text = text[7:]
                    if text.endswith("```"):
                        text = text[:-3]
                    text = text.strip()
                    
                    parsed = json.loads(text)
                    reply_target = parsed.get("answer", "").strip()
                    reply_en = parsed.get("answer_en", "").strip()
                    if reply_target:
                        success = True
                        break
            except Exception as e:
                err_msg = str(e).lower()
                is_rate_limit = "429" in err_msg or "quota" in err_msg or "exhausted" in err_msg
                wait_time = 2.5 if is_rate_limit else 1.0
                logger.warning(f"Gemini API attempt {attempt+1} failed: {e}. Backing off for {wait_time}s...")
                if attempt < retries - 1:
                    time.sleep(wait_time)

    # 2. Fallback rule-based system if Gemini key is missing or failed
    if not success:
        logger.warning("Executing local rule-based chatbot fallback...")
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

        # Translate or return defaults
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

    # 3. Synthesize Speech audio if reply length < 300 chars
    audio_url = None
    if len(reply_target) < 300:
        lang_info = LANGUAGES.get(lang, LANGUAGES["hi"])
        if lang_info.get("gtts_supported", False):
            try:
                filename = f"chat_reply_{uuid.uuid4().hex}.mp3"
                audio_dir = os.path.join("static", "audio")
                os.makedirs(audio_dir, exist_ok=True)
                audio_path = os.path.join(audio_dir, filename)
                
                tts = gTTS(text=reply_target, lang=lang_info["gtts_code"])
                tts.save(audio_path)
                audio_url = f"/static/audio/{filename}"
                logger.info(f"Synthesized chat audio for language locale '{lang}': {audio_url}")
            except Exception as e:
                logger.error(f"Failed to generate TTS audio: {e}")
        else:
            logger.warning(f"gTTS does not support language '{lang}'. Skipping TTS audio generation.")

    return jsonify({
        "success": True,
        "reply": reply_target,
        "reply_hi": reply_target,
        "reply_en": reply_en,
        "audio_url": audio_url
    })
