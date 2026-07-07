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
from language_config import LANGUAGES, FALLBACK_RESPONSES

logger = logging.getLogger("kisan_saathi")

chat_bp = Blueprint("chat", __name__)

# Simple in-memory response cache to prevent API rate limiting on repeated demo runs (TTL = 10 minutes)
chat_cache = {}

# Configure Google Gemini API keys (supports rotation on rate-limit)
_gemini_key_1 = os.getenv("GEMINI_API_KEY", "")
_gemini_key_2 = os.getenv("GEMINI_API_KEY_2", "")
GEMINI_KEYS = [k for k in [_gemini_key_1, _gemini_key_2] if k]
_current_key_idx = 0
api_key = GEMINI_KEYS[0] if GEMINI_KEYS else ""

def get_next_gemini_key():
    """Rotate to the next available Gemini API key and reconfigure genai."""
    global _current_key_idx
    if len(GEMINI_KEYS) <= 1:
        return api_key
    _current_key_idx = (_current_key_idx + 1) % len(GEMINI_KEYS)
    new_key = GEMINI_KEYS[_current_key_idx]
    genai.configure(api_key=new_key)
    logger.info(f"Rotated to Gemini API key index {_current_key_idx}")
    return new_key

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
    "When explaining government schemes like PM-Kisan or PMFBY, state eligibility criteria factually and briefly, and remind the farmer to verify details on the official portal pmkisan.gov.in. "
    "If a farmer describes symptoms (e.g. 'my wheat leaves are turning yellow'), ask ONE clarifying question if needed "
    "(e.g. crop stage, recent weather) rather than guessing, then give a specific, actionable answer — not a generic one. "
    "Reply ONLY in the same language the user writes in. Be concise and practical: 3-5 sentences, simple vocabulary suitable for a farmer with basic literacy. "
    "If the question is outside agriculture, politely redirect to what you can help with. "
    "Respond ONLY as a valid JSON object matching this structure: "
    "{\"answer\": \"<response in the user's language>\", \"answer_en\": \"<concise English translation of the same response>\"}. "
    "Do not include any markdown formatting, backticks, or extra text in your output."
)

SEASON_MAP = {
    "kharif": "kharif", "rabi": "rabi", "zaid": "zaid",
    "खरीफ": "kharif", "रबी": "rabi", "जायद": "zaid",
    "sauni": "kharif", "hari": "rabi", "zaad": "zaid",
    "সাউণী": "kharif", "হাੜੀ": "rabi", "ਜਾਇਦ": "zaid",
    "ఖరీఫ్": "kharif", "రబీ": "rabi", "జాయద్": "zaid",
    "ಕಾರ್ತಿ": "kharif", "ರಬಿ": "rabi", "ಜಾಯಿದ್": "zaid"
}

MONTH_MAP = {
    "june": "kharif", "july": "kharif", "august": "kharif", "september": "kharif", "october": "kharif",
    "november": "rabi", "december": "rabi", "january": "rabi", "february": "rabi", "march": "zaid",
    "april": "zaid", "may": "zaid",
    "जून": "kharif", "जुलाई": "kharif", "अगस्त": "kharif", "सितंबर": "kharif", "अक्टूबर": "kharif",
    "नवंबर": "rabi", "दिसंबर": "rabi", "जनवरी": "rabi", "फरवरी": "rabi", "मार्च": "zaid",
    "अप्रैल": "zaid", "मई": "zaid",
}

KVK_CONTACTS = {
    "indore": "KVK Indore (College of Agriculture): +91-731-2710384",
    "bhopal": "KVK Bhopal (CIAE Campus, Nabi Bagh): +91-755-2733274",
    "jabalpur": "KVK Jabalpur (JNKVV Campus): +91-761-2681236",
    "gwalior": "KVK Gwalior (RVSKVV): +91-751-2460075",
    "ujjain": "KVK Ujjain: +91-734-2521505",
    "dhar": "KVK Dhar: +91-7292-234204",
    "dewas": "KVK Dewas: +91-7272-260261",
    "sehore": "KVK Sehore: +91-7562-227546",
    "raisen": "KVK Raisen: +91-7482-223450",
    "sagar": "KVK Sagar: +91-7582-281350",
    "shivpuri": "KVK Shivpuri: +91-7492-223405",
}

def clean_old_audio_files():
    """Deletes cached audio files older than 1 hour in static/audio/."""
    try:
        now = time.time()
        audio_dir = os.path.join("static", "audio")
        os.makedirs(audio_dir, exist_ok=True)
        files = glob.glob(os.path.join(audio_dir, "chat_reply_*.mp3"))
        deleted_count = 0
        for f in files:
            if os.stat(f).st_mtime < now - 3600:
                os.remove(f)
                deleted_count += 1
        if deleted_count > 0:
            logger.info(f"Cleaned up {deleted_count} cached audio files older than 1 hour.")
    except Exception as e:
        logger.error(f"Error during audio file cleanup: {e}")

def start_cleanup_scheduler(scheduler):
    scheduler.add_job(func=clean_old_audio_files, trigger="interval", hours=1)
    logger.info("Audio cleanup job registered.")

@chat_bp.route("/api/chat", methods=["POST"])
def chat_response():
    clean_old_audio_files()
    
    req_data = request.get_json()
    if not req_data or "message" not in req_data:
        return jsonify({"success": False, "error": "No query message sent"})

    query = req_data["message"]
    lang = req_data.get("lang", req_data.get("language", "")).strip()
    history = req_data.get("history", [])

    if not lang:
        try:
            detected = detect(query)
            if detected in LANGUAGES:
                lang = detected
            else:
                lang = "hi"
        except Exception:
            lang = "hi"

    reply_target = ""
    reply_en = ""
    success = False
    used_path = "fallback_rule_based"
    query_key = f"{query.strip().lower()}_{lang}"

    # Check cache (10 mins TTL)
    if query_key in chat_cache:
        cached = chat_cache[query_key]
        if time.time() - cached["timestamp"] < 600:
            logger.info(f"Serving cached response for query: '{query}' in lang: {lang}")
            return jsonify({
                "success": True,
                "reply": cached["reply_target"],
                "reply_hi": cached["reply_target"],
                "reply_en": cached["reply_en"],
                "audio_url": cached["audio_url"]
            })

    # 1. Primary and Secondary Gemini Try-Loops
    if api_key:
        lang_info = LANGUAGES.get(lang, LANGUAGES["hi"])
        lang_instruction = f"Reply ONLY in {lang_info['name']}, using {lang_info['script']} script. Keep it simple, farmer-friendly, max 3-5 sentences."
        dynamic_system_instruction = f"{SYSTEM_INSTRUCTION} {lang_instruction}"
        
        contents = []
        for h in history:
            role = "user" if h.get("sender") == "user" else "model"
            contents.append({"role": role, "parts": [h.get("text", "")]})
        contents.append({"role": "user", "parts": [query]})

        # Models to try sequentially
        models_to_try = [
            ("gemini-2.5-flash", "gemini_primary"),
            ("gemini-1.5-flash", "gemini_secondary_model")
        ]

        for model_name, model_label in models_to_try:
            if success:
                break
                
            retries = 4
            for attempt in range(retries):
                try:
                    logger.info(f"Sending prompt to {model_name} (attempt {attempt+1}): '{query}'")
                    model = genai.GenerativeModel(
                        model_name=model_name,
                        system_instruction=dynamic_system_instruction
                    )
                    response = model.generate_content(contents)
                    
                    if response.text:
                        text = response.text.strip()
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
                            used_path = model_label
                            break
                except Exception as e:
                    err_msg = str(e).lower()
                    is_rate_limit = "429" in err_msg or "quota" in err_msg or "exhausted" in err_msg
                    logger.warning(f"Model {model_name} attempt {attempt+1} failed: {e}")
                    
                    if attempt < retries - 1:
                        if is_rate_limit:
                            if len(GEMINI_KEYS) > 1:
                                logger.info("Rate limit hit. Rotating to next Gemini API key...")
                                get_next_gemini_key()
                                time.sleep(0.5)
                            else:
                                wait_time = [1.0, 3.0, 6.0][attempt]
                                logger.info(f"Rate limit / quota error. Backing off for {wait_time}s...")
                                time.sleep(wait_time)
                        else:
                            time.sleep(0.1)
            
            if success:
                break

    # 2. Local rule-based fallback system if Gemini fails
    if not success:
        logger.warning("Executing local rule-based chatbot fallback...")
        used_path = "fallback_rule_based"
        query_lower = query.lower()
        
        # Check if last bot response asked for timing clarification
        pending_clarification = False
        last_bot_text = ""
        for h in reversed(history):
            if h.get("sender") in ["bot", "assistant"] or h.get("role") in ["model", "assistant"]:
                last_bot_text = h.get("text", "").lower()
                break
                
        if last_bot_text:
            timing_keywords = ["month", "season", "when", "time", "sow", "plant", "महीना", "मौसम", "समय", "ऋतु", "बोने", "बुवाई", "बुআই", "बोना", "kharif", "rabi", "zaid", "खरीफ", "रबी", "जायद"]
            if any(k in last_bot_text for k in timing_keywords):
                pending_clarification = True

        intent = None
        
        # Colloquial and regional intent classification
        weather_keywords = ["weather", "मौसम", "बारिश", "rain", "वर्षा", "pani kab", "monsoon", "climate", "হাওয়া", "વરસાદ", "বৃষ্টি", "ਮੀਂਹ", "மழை", "వర్షం", "ಮಳೆ", "മഴ", "ବର୍ଷା", "بارش"]
        mandi_keywords = ["mandi", "भाव", "कीमत", "गेहूं", "rate", "price", "मन्डी", "बाजार दर", "ભાવ", "দর", "ਭਾਅ", "விலை", "ధర", "ದರ", "വില", "ଦର", "بھاؤ"]
        disease_keywords = ["disease", "রোগ", "পত্তি", "कीड़ा", "kida", "kitak", "spots", "धब्बे", "बीमारी", "इलाज", "उपचार", "ब्लाइट", "રોગ", "ਰੋਗ", "நோய்", "తెగులు", "ರೋಗ", "രോഗം", "ବିମାରୀ"]
        greeting_keywords = ["hello", "hi", "नमस्ते", "hey", "सश्रीकाल", "नमस्कार", "سلام", "வணக்கம்", "నమస్కారం", "ನಮಸ್ಕಾರ"]
        scheme_keywords = ["scheme", "योजना", "yojana", "pm kisan", "status", "बीमा", "beema", "subsidy", "pmfby", "सरकारी मदद", "योजने", "લાભ", "বীমা", "ਬੀਮਾ", "காப்பீடு", "భీమా", "ವಿಮೆ", "ഇൻഷുറൻസ്", "ବୀମା", "اسکیم"]
        expert_keywords = ["expert", "talk", "speak", "person", "help", "call", "phone", "number", "officer", "kvk", "seva kendra", "अधिकारी", "विज्ञान केंद्र", "बात करना", "संपर्क", "મદદ", "সহায়তা", "ਸੰਪਰਕ", "உதவி", "ಸಂಪರ್ಕ", "സഹായം", "ସହଯୋଗ", "رابطہ"]
        irrigation_keywords = ["irrigation", "water", "paani", "pani", "sinchai", "field", "dry", "wet", "सिंचाई", "सिंचन", "পিয়ত", "जलसेच", "ਸਿੰਚਾਈ", "பாசனம்", "తడులు", "ನೀರಾವರಿ", "നനയ്ക്കുക", "ଜଳସେଚନ", "آبپاشی"]

        if any(w in query_lower for w in weather_keywords):
            intent = "weather"
        elif any(w in query_lower for w in mandi_keywords):
            intent = "mandi"
        elif any(w in query_lower for w in disease_keywords):
            intent = "disease"
        elif any(w in query_lower for w in greeting_keywords):
            intent = "greeting"
        elif any(w in query_lower for w in scheme_keywords):
            intent = "schemes"
        elif any(w in query_lower for w in expert_keywords):
            intent = "expert"
        elif any(w in query_lower for w in irrigation_keywords):
            intent = "irrigation"

        if intent:
            reply_target = FALLBACK_RESPONSES[lang][intent]
            reply_en = FALLBACK_RESPONSES["en"][intent]
            
            # For expert escalation, perform district-based KVK details injection
            if intent == "expert":
                matched_district = None
                # Check query and history for district name
                combined_history_text = " ".join([h.get("text", "").lower() for h in history]) + " " + query_lower
                for d in KVK_CONTACTS:
                    if d in combined_history_text:
                        matched_district = d
                        break
                if matched_district:
                    kvk_info = KVK_CONTACTS[matched_district]
                    if lang == "hi":
                        reply_target += f" {matched_district.title()} जिले के लिए: {kvk_info}."
                    else:
                        reply_target += f" For {matched_district.title()} district: {kvk_info}."
                    reply_en += f" For {matched_district.title()} district: {kvk_info}."
        else:
            if pending_clarification:
                detected_season = None
                for word, season in SEASON_MAP.items():
                    if word in query_lower:
                        detected_season = season
                        break
                if not detected_season:
                    for word, season in MONTH_MAP.items():
                        if word in query_lower:
                            detected_season = season
                            break
                
                if detected_season:
                    rec_key = f"crop-recommendation-{detected_season}"
                    reply_target = FALLBACK_RESPONSES[lang][rec_key]
                    reply_en = FALLBACK_RESPONSES["en"][rec_key]
                else:
                    reply_target = FALLBACK_RESPONSES[lang]["month-clarification-needed"]
                    reply_en = FALLBACK_RESPONSES["en"]["month-clarification-needed"]
            else:
                reply_target = FALLBACK_RESPONSES[lang]["generic-redirect"]
                reply_en = FALLBACK_RESPONSES["en"]["generic-redirect"]

    logger.info(f"Response served via path: {used_path}")

    # 3. Synthesize Speech audio if reply length < 300 chars (consistent across both primary & fallback paths)
    audio_url = None
    if len(reply_target) < 300:
        lang_info = LANGUAGES[lang]
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

    # Cache the response
    chat_cache[query_key] = {
        "reply_target": reply_target,
        "reply_en": reply_en,
        "audio_url": audio_url,
        "timestamp": time.time(),
        "used_path": used_path
    }

    return jsonify({
        "success": True,
        "reply": reply_target,
        "reply_hi": reply_target,
        "reply_en": reply_en,
        "audio_url": audio_url
    })

@chat_bp.route("/api/voice-transcribe", methods=["POST"])
def voice_transcribe():
    if "audio" not in request.files:
        return jsonify({"success": False, "error": "No audio file uploaded"})
        
    audio_file = request.files["audio"]
    lang = request.form.get("lang", "hi").strip()
    if lang not in LANGUAGES:
        lang = "hi"
    lang_info = LANGUAGES[lang]
    
    # Save the file temporarily
    temp_dir = os.path.join("static", "audio")
    os.makedirs(temp_dir, exist_ok=True)
    temp_filename = f"transcribe_{uuid.uuid4().hex}.webm"
    temp_filepath = os.path.join(temp_dir, temp_filename)
    audio_file.save(temp_filepath)
    
    transcript = ""
    try:
        if api_key:
            uploaded_file = genai.upload_file(path=temp_filepath, mime_type="audio/webm")
            model = genai.GenerativeModel("gemini-2.5-flash")
            prompt = (
                f"You are a helpful speech-to-text transcriber. Transcribe this audio recording into "
                f"written text in {lang_info['name']}. Only output the transcribed text, nothing else. "
                f"If the audio is completely silent or unrecognizable, output nothing."
            )
            response = model.generate_content([uploaded_file, prompt])
            transcript = response.text.strip() if response.text else ""
            
            try:
                genai.delete_file(uploaded_file.name)
            except Exception as e:
                logger.warning(f"Failed to delete uploaded File API file: {e}")
    except Exception as e:
        logger.error(f"Gemini transcription failed: {e}")
        
    try:
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
    except Exception as e:
        logger.warning(f"Failed to delete local temp audio file: {e}")
        
    if transcript:
        return jsonify({"success": True, "transcript": transcript})
    else:
        return jsonify({"success": False, "error": "Could not transcribe audio. Please try typing."})

def run_startup_self_test():
    """Performs startup checks on fallback response scripts and configurations."""
    logger.info("Starting Kisan Saathi Chatbot startup self-test...")
    all_passed = True
    
    # 1. Check gTTS support
    try:
        from gtts.lang import tts_langs
        supported_gtts = tts_langs()
    except Exception as e:
        logger.error(f"Startup test: Could not retrieve supported gTTS languages: {e}")
        supported_gtts = {}

    # Expected ranges mapping
    ranges = {
        "hi": (0x0900, 0x097F),
        "mr": (0x0900, 0x097F),
        "gu": (0x0A80, 0x0AFF),
        "bn": (0x0980, 0x09FF),
        "as": (0x0980, 0x09FF),
        "pa": (0x0A00, 0x0A7F),
        "ta": (0x0B80, 0x0BFF),
        "te": (0x0C00, 0x0C7F),
        "kn": (0x0C80, 0x0CFF),
        "ml": (0x0D00, 0x0D7F),
        "or": (0x0B00, 0x0B7F),
        "ur": (0x0600, 0x06FF),
        "en": (0x0000, 0x007F),
    }
    
    allowed_punc = set(" \t\n\r,.:;?!'\"()[]{}<>+-*/=%$₹0123456789_°।\u200c")
    required_keys = [
        "weather", "mandi", "disease", "greeting", 
        "generic-redirect", "month-clarification-needed",
        "crop-recommendation-kharif", "crop-recommendation-rabi", 
        "crop-recommendation-zaid"
    ]
    
    for lang_code, lang_info in LANGUAGES.items():
        lang_passed = True
        gtts_code = lang_info.get("gtts_code")
        
        # Check gTTS code warning
        if gtts_code not in supported_gtts:
            logger.warning(f"Startup test WARNING: Lang '{lang_code}' uses gtts_code '{gtts_code}' which is not in gtts.lang.tts_langs().")
        
        # Verify fallback responses exist and have correct script
        if lang_code not in FALLBACK_RESPONSES:
            logger.error(f"Startup test FAIL: Lang '{lang_code}' is missing from FALLBACK_RESPONSES.")
            all_passed = False
            continue
            
        responses = FALLBACK_RESPONSES[lang_code]
        for key in required_keys:
            if key not in responses:
                logger.error(f"Startup test FAIL: Lang '{lang_code}' is missing required key '{key}' in FALLBACK_RESPONSES.")
                lang_passed = False
                all_passed = False
                continue
                
            text = responses[key]
            if not text:
                logger.error(f"Startup test FAIL: Lang '{lang_code}' key '{key}' is empty.")
                lang_passed = False
                all_passed = False
                continue
                
            # Verify script
            start, end = ranges.get(lang_code, (0, 0))
            violations = []
            for ch in text:
                code = ord(ch)
                if ch in allowed_punc:
                    continue
                if (0x0041 <= code <= 0x005A) or (0x0061 <= code <= 0x007A):
                    continue
                if start and not (start <= code <= end):
                    violations.append(f"\\u{code:04x}")
            if violations:
                logger.error(f"Startup test FAIL: Lang '{lang_code}' key '{key}' has script violations: {violations}")
                lang_passed = False
                all_passed = False
                
        if lang_passed:
            logger.info(f"Startup test PASS: Language config and fallbacks for '{lang_code}' are valid.")
            
    if all_passed:
        logger.info("Startup self-test status: ALL PASSED")
    else:
        logger.error("Startup self-test status: FAILED")

# Execute self-test on load
run_startup_self_test()

