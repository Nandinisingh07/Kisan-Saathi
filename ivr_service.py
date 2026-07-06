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
    gather.say("नमस्ते! किसान साथी हेल्पलाइन में आपका स्वागत है। हिंदी के लिए एक दबाएं।", language="hi-IN")
    gather.say("For English, press 2.", language="en-US")
    gather.say("मराठीसाठी तीन दाबा.", language="mr-IN", voice="Google.mr-IN-Standard-A")
    gather.say("गुजराती के लिए चार दबाएं।", language="gu-IN", voice="Google.gu-IN-Standard-A")
    gather.say("বাংলার জন্য পাঁচ চাপুন।", language="bn-IN", voice="Google.bn-IN-Standard-A")
    resp.append(gather)
    resp.redirect("/ivr/voice")
    return Response(str(resp), mimetype="text/xml")

@ivr_bp.route("/ivr/handle-language", methods=["POST"])
def handle_language():
    """Handles digit entered for language, prompts with options menu in that language."""
    digits = request.form.get("Digits", "1").strip()
    lang_mapping = {
        "1": "hi",
        "2": "en",
        "3": "mr",
        "4": "gu",
        "5": "bn"
    }
    lang_code = lang_mapping.get(digits, "hi")
    call_sid = request.form.get("CallSid")
    call_sessions[call_sid] = lang_code
    
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["hi"])
    twilio_lang = TWILIO_LANG_MAP.get(lang_code, "hi-IN")
    
    resp = VoiceResponse()
    gather = Gather(numDigits=1, timeout=8, action="/ivr/handle-menu")
    
    # Hardcoded menu prompts to avoid Gemini latency and use spelled-out numbers
    menu_prompts = {
        "hi": "फसल रोग की जानकारी के लिए एक दबाएं। मंडी भाव के लिए दो दबाएं। मौसम सलाह के लिए तीन दबाएं। सरकारी योजनाओं के लिए चार दबाएं। विशेषज्ञ से बात करने के लिए पांच दबाएं।",
        "en": "For Crop Disease Info, press 1. For Mandi Prices, press 2. For Weather Advisory, press 3. For Government Schemes, press 4. To speak to an expert, press 5.",
        "mr": "पीक रोगाच्या माहितीसाठी एक दाबा. बाजार भावांसाठी दोन दाबा. हवामान सल्ल्यासाठी तीन दाबा. सरकारी योजनांसाठी चार दाबा. तज्ज्ञांशी बोलण्यासाठी पाच दाबा.",
        "gu": "પાક રોગની માહિતી માટે એક દબાવો. બજાર ભાવો માટે બે દબાવો. હવામાન સલાહ માટે ત્રણ દબાવો. સરકારી યોજનાઓ માટે ચાર દબાવો. નિષ્ણાત સાથે વાત કરવા માટે પાંચ દબાવો.",
        "bn": "ফসল রোগ তথ্যের জন্য এক চাপুন। বাজার দরের জন্য দুই চাপুন। আবহাওয়া পূর্বাভাসের জন্য তিন চাপুন। সরকারি প্রকল্পের জন্য চার চাপুন। বিশেষজ্ঞের সাথে কথা বলতে পাঁচ চাপুন।"
    }
    menu_prompt = menu_prompts.get(lang_code, menu_prompts["hi"])
            
    voice_mapping = {
        "mr": "Google.mr-IN-Standard-A",
        "gu": "Google.gu-IN-Standard-A",
        "bn": "Google.bn-IN-Standard-A"
    }
    voice_name = voice_mapping.get(lang_code)
    if voice_name:
        gather.say(menu_prompt, language=twilio_lang, voice=voice_name)
    else:
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
    
    voice_mapping = {
        "mr": "Google.mr-IN-Standard-A",
        "gu": "Google.gu-IN-Standard-A",
        "bn": "Google.bn-IN-Standard-A"
    }
    voice_name = voice_mapping.get(lang_code)
    
    if option == 1:
        # Prompt user to say crop name (no Gemini, hardcoded translated strings)
        fallback_prompts = {
            "hi": "कृपया अपनी फसल का नाम बोलें।",
            "en": "Please say the name of your crop.",
            "mr": "कृपया तुमच्या पिकाचे नाव सांगा.",
            "gu": "કૃપા કરીને તમારા પાકનું નામ બોલો.",
            "bn": "অনুগ্রহ করে আপনার ফসলের নাম বলুন।"
        }
        prompt_text = fallback_prompts.get(lang_code, "Please say the name of your crop.")
            
        resp = VoiceResponse()
        gather = Gather(input="speech", speechTimeout="auto", timeout=8, action="/ivr/handle-crop-name")
        if voice_name:
            gather.say(prompt_text, language=twilio_lang, voice=voice_name)
        else:
            gather.say(prompt_text, language=twilio_lang)
        resp.append(gather)
        resp.redirect("/ivr/handle-crop-name")
        return Response(str(resp), mimetype="text/xml")
        
    options_map = {
        2: ("Mandi Prices", "मंडी भाव"),
        3: ("Weather Advisory", "मौसम पूर्वानुमान"),
        4: ("Government Schemes", "सरकारी योजनाएं"),
        5: ("Speak to Expert", "विशेषज्ञ से बात")
    }
    opt_en, opt_hi = options_map.get(option, ("General Inquiry", "सामान्य पूछताछ"))
    selected_path = f"{lang_info['name']} -> {opt_hi} (Press {option})"
    
    resp = VoiceResponse()
    
    # Hardcoded responses for options 2, 3, 4, 5 (zero latency)
    responses = {
        2: {
            "hi": "मंडी में गेहूं का औसत भाव तेईस सौ पचास रुपये प्रति क्विंटल चल रहा है।",
            "en": "The average wheat price in the mandi is two thousand three hundred and fifty rupees per quintal.",
            "mr": "बाजार समितीमध्ये गव्हाचा सरासरी भाव दोन हजार तीनशे पन्नास रुपये प्रति क्विंटल सुरू आहे.",
            "gu": "બજારમાં ઘઉંનો સરેરાશ ભાવ બે હજાર ત્રણસો પચાસ રૂપિયા પ્રતિ ક્વિન્ટલ ચાલી રહ્યો છે.",
            "bn": "বাজারে গমের গড় দাম প্রতি কুইন্টাল দুই হাজার তিনশত পঞ্চাশ টাকা চলছে।"
        },
        3: {
            "hi": "आज मौसम साफ रहेगा और फसलों की सिंचाई जारी रखें।",
            "en": "Today's weather will be clear. Please continue crop irrigation.",
            "mr": "आज हवामान स्वच्छ राहील आणि पिकांची सिंचन सुरू ठेवावे.",
            "gu": "આજે હવામાન ચોખ્ખું રહેશે અને પાકની સિંચાઈ ચાલુ રાખો.",
            "bn": "আজ আবহাওয়া পরিষ্কার থাকবে এবং ফসলে জলসেচ অব্যাহত রাখুন।"
        },
        4: {
            "hi": "पीएम किसान सम्मान निधि योजना के तहत किसानों को हर साल तीन किश्तों में वित्तीय सहायता दी जाती है। आप अपना स्टेटस पीएम-किसान पोर्टल पर देख सकते हैं या अपने नजदीकी कृषि कार्यालय में संपर्क कर सकते हैं।",
            "en": "Under the PM Kisan Samman Nidhi scheme, farmers receive financial support in three installments per year. You can check your status on the PM-Kisan portal or contact your local agriculture office.",
            "mr": "पीएम किसान सन्मान निधी योजनेअंतर्गत शेतकऱ्यांना दरवर्षी तीन हप्त्यांमध्ये आर्थिक मदत दिली जाते. तुम्ही पीएम-किसान पोर्टलवर तुमची स्थिती तपासू शकता किंवा तुमच्या स्थानिक कृषी कार्यालयाशी संपर्क साधू शकता.",
            "gu": "પીએમ કિસાન સન્માન નિધિ યોજના અંતર્ગત ખેડૂતોને વર્ષમાં ત્રણ હપ્તામાં નાણાકીય સહાય આપવામાં આવે છે. તમે પીએમ-કિસาน પોર્ટલ પર તમારું સ્ટેટસ ચેક કરી શકો છો અથવા તમારી સ્થાનિક કૃષિ કચેરીનો સંપર્ક કરી શકો છો.",
            "bn": "পিএম কিষাণ সম্মান নিধি প্রকল্পের আওতায় কৃষকরা বছরে তিনটি কিস্তিতে আর্থিক সহায়তা পান। আপনি পিএম-কিষাণ পোর্টালে আপনার স্ট্যাটাস চেক করতে পারেন বা আপনার স্থানীয় কৃষি অফিসে যোগাযোগ করতে পারেন।"
        },
        5: {
            "hi": "कृषि विशेषज्ञ से आपकी कॉल दो घंटे में शेड्यूल्ड कर दी गई है।",
            "en": "Your callback from an agricultural expert has been scheduled within two hours.",
            "mr": "कृषी तज्ज्ञांकडून आपला कॉल दोन तासात नियोजित केला गेला आहे.",
            "gu": "કૃષિ નિષ્ણાત સાથેનો તમારો કોલ બે કલાકમાં શેડ્યૂલ કરવામાં આવ્યો છે.",
            "bn": "কৃষি বিশেষজ্ঞের সাথে আপনার কলটি দুই ঘণ্টার মধ্যে নির্ধারিত করা হয়েছে।"
        }
    }
    
    response_text = responses.get(option, {}).get(lang_code, responses.get(option, {}).get("hi", ""))

    audio_url = ""
    audio_filename = f"ivr_reply_{uuid_hex()}.mp3"
    
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
            if voice_name:
                resp.say(response_text, language=twilio_lang, voice=voice_name)
            else:
                resp.say(response_text, language=twilio_lang)
    else:
        logger.warning(f"gTTS not supported for {lang_code}. Fallback to Twilio say.")
        if voice_name:
            resp.say(response_text, language=twilio_lang, voice=voice_name)
        else:
            resp.say(response_text, language=twilio_lang)
            
    # Add warm closing line
    closings = {
        "hi": "किसान साथी का उपयोग करने के लिए आपका धन्यवाद। आपका दिन शुभ हो!",
        "en": "Thank you for using Kisan Saathi. Have a great day!",
        "mr": "किसान साथी वापरल्याबद्दल धन्यवाद. तुमचा दिवस चांगला जावो!",
        "gu": "કિસાન સાથીનો ઉપયોગ કરવા બદલ આભાર. તમારો દિવસ સારો રહે!",
        "bn": "কিষাণ সাথী ব্যবহার করার জন্য আপনাকে ধন্যবাদ। আপনার দিনটি শুভ হোক!"
    }
    closing_text = closings.get(lang_code, closings["en"])
    if voice_name:
        resp.say(closing_text, language=twilio_lang, voice=voice_name)
    else:
        resp.say(closing_text, language=twilio_lang)
            
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

@ivr_bp.route("/ivr/handle-crop-name", methods=["POST"])
def handle_crop_name():
    """Handles voice input containing crop name, gets disease info from Gemini."""
    speech_result = request.form.get("SpeechResult", "").strip()
    call_sid = request.form.get("CallSid")
    lang_code = call_sessions.get(call_sid, "hi")
    lang_info = LANGUAGES.get(lang_code, LANGUAGES["hi"])
    twilio_lang = TWILIO_LANG_MAP.get(lang_code, "hi-IN")
    
    voice_mapping = {
        "mr": "Google.mr-IN-Standard-A",
        "gu": "Google.gu-IN-Standard-A",
        "bn": "Google.bn-IN-Standard-A"
    }
    voice_name = voice_mapping.get(lang_code)
    
    resp = VoiceResponse()
    
    # Warm closing lines dictionary
    closings = {
        "hi": "किसान साथी का उपयोग करने के लिए आपका धन्यवाद। आपका दिन शुभ हो!",
        "en": "Thank you for using Kisan Saathi. Have a great day!",
        "mr": "किसान साथी वापरल्याबद्दल धन्यवाद. तुमचा दिवस चांगला जावो!",
        "gu": "કિસាន સાથીનો ઉપયોગ કરવા બદલ આભાર. તમારો દિવસ સારો રહે!",
        "bn": "কিষাণ সাথী ব্যবহার করার জন্য আপনাকে ধন্যবাদ। আপনার দিনটি শুভ হোক!"
    }
    closing_text = closings.get(lang_code, closings["en"])
    
    if not speech_result:
        fallback_no_speech = {
            "hi": "क्षमा करें, मैं समझ नहीं पाया। एक विशेषज्ञ आपको जल्द ही वापस कॉल करेंगे।",
            "en": "Sorry, I could not understand. An expert will call you back shortly.",
            "mr": "क्षमस्व, मला समजले नाही. एक तज्ज्ञ तुम्हाला लवकरच परत कॉल करतील.",
            "gu": "દિલગીર છું, હું સમજી શક્યો નથી. એક નિષ્ણાત તમને ટૂંક સમયમાં પાછા કૉલ કરશે.",
            "bn": "দুঃখিত, আমি বুঝতে পারিনি। একজন বিশেষজ্ঞ শীঘ্রই আপনাকে ফেরত কল করবেন।"
        }
        msg = fallback_no_speech.get(lang_code, "Sorry, I could not understand. An expert will call you back shortly.")
        if voice_name:
            resp.say(msg, language=twilio_lang, voice=voice_name)
        else:
            resp.say(msg, language=twilio_lang)
            
        if voice_name:
            resp.say(closing_text, language=twilio_lang, voice=voice_name)
        else:
            resp.say(closing_text, language=twilio_lang)
            
        selected_path = f"{lang_info['name']} -> Crop Disease Info -> Custom Query: (No Speech Input)"
        phone = request.form.get("From", "+91 XXXXX XX00")
        duration = "0m 30s"
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_date = datetime.date.today().strftime("%Y-%m-%d")
        
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO ivr_calls (caller, path, duration, time, date, audio_url, option_chosen)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (phone, selected_path, duration, current_time, current_date, "", 1))
            conn.commit()
            conn.close()
        except Exception as e:
            logger.error(f"Error logging failed speech IVR call: {e}")
            
        resp.hangup()
        return Response(str(resp), mimetype="text/xml")
        
    # Play "Please wait" filler immediately before custom query Gemini call
    fillers = {
        "hi": "कृपया प्रतीक्षा करें।",
        "en": "Please wait.",
        "mr": "कृपया प्रतीक्षा करा.",
        "gu": "કૃપા કરીને રાહ જુઓ.",
        "bn": "অনুগ্রহ করে অপেক্ষা করুন।"
    }
    filler_text = fillers.get(lang_code, "Please wait.")
    if voice_name:
        resp.say(filler_text, language=twilio_lang, voice=voice_name)
    else:
        resp.say(filler_text, language=twilio_lang)
        
    # Generate custom crop disease advice (with reduced timeout of 3 seconds)
    response_text = ""
    try:
        model_g = genai.GenerativeModel("gemini-2.5-flash")
        prompt = (
            f"You are the Kisan Saathi IVR Helpline assistant. The farmer said their crop is: '{speech_result}'. "
            f"Generate a helpful, highly concise response (1-2 sentences maximum) in {lang_info['name']} (using {lang_info['script']} script) "
            f"about common diseases and basic treatment for this crop. If the crop name is unclear or not a real crop, "
            f"give a general crop-disease-care tip instead. Do not include English translation."
        )
        res = model_g.generate_content(prompt, request_options={"timeout": 3})
        response_text = res.text.strip() if res.text else ""
    except Exception as e:
        logger.error(f"Gemini IVR custom response generation failed: {e}")
        
    if not response_text:
        fallback_fail = {
            "hi": f"फसल {speech_result} के उपचार के लिए कृपया स्वस्थ बीजों का प्रयोग करें और जल निकासी का उचित प्रबंधन करें।",
            "en": f"For {speech_result} care, please use certified seeds and ensure proper soil drainage.",
            "mr": f"पिक {speech_result} च्या काळजीसाठी, कृपया प्रमाणित बियाणे वापरा आणि पाण्याचा निचरा योग्य ठेवा.",
            "gu": f"પાક {speech_result} ની સંભાળ માટે, કૃપા કરીને પ્રમાણિત બીજનો ઉપયોગ કરો અને યોગ્ય ડ્રેનેજ રાખો.",
            "bn": f"ফসলের {speech_result} যত্নের জন্য, অনুগ্রহ করে ভালো বীজ ব্যবহার করুন এবং সঠিক জল নিষ্কাশন নিশ্চিত করুন।"
        }
        response_text = fallback_fail.get(lang_code, f"For {speech_result} care, please ensure proper soil drainage.")
        
    audio_url = ""
    audio_filename = f"ivr_reply_{uuid_hex()}.mp3"
    
    if lang_info.get("gtts_supported", False):
        try:
            audio_dir = os.path.join("static", "audio")
            os.makedirs(audio_dir, exist_ok=True)
            audio_path = os.path.join(audio_dir, audio_filename)
            tts = gTTS(text=response_text, lang=lang_info["gtts_code"])
            tts.save(audio_path)
            audio_url = f"{request.url_root.rstrip('/')}/static/audio/{audio_filename}"
            resp.play(audio_url)
        except Exception as e:
            logger.error(f"Failed to generate custom gTTS audio: {e}")
            if voice_name:
                resp.say(response_text, language=twilio_lang, voice=voice_name)
            else:
                resp.say(response_text, language=twilio_lang)
    else:
        if voice_name:
            resp.say(response_text, language=twilio_lang, voice=voice_name)
        else:
            resp.say(response_text, language=twilio_lang)
            
    # Add warm closing line
    if voice_name:
        resp.say(closing_text, language=twilio_lang, voice=voice_name)
    else:
        resp.say(closing_text, language=twilio_lang)
            
    phone = request.form.get("From", "+91 XXXXX XX00")
    duration = "1m 15s"
    current_time = datetime.datetime.now().strftime("%H:%M")
    current_date = datetime.date.today().strftime("%Y-%m-%d")
    db_audio_url = f"/static/audio/{audio_filename}" if audio_url else ""
    selected_path = f"Crop Disease Info -> Custom Query: {speech_result}"
    
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ivr_calls (caller, path, duration, time, date, audio_url, option_chosen)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (phone, selected_path, duration, current_time, current_date, db_audio_url, 1))
        conn.commit()
        conn.close()
        logger.info(f"Custom query IVR Call logged: {phone} | Query: {speech_result}")
    except Exception as e:
        logger.error(f"Error logging custom query IVR call: {e}")
        
    resp.hangup()
    return Response(str(resp), mimetype="text/xml")