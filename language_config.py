import logging
import gtts

logger = logging.getLogger("kisan_saathi")

LANGUAGES = {
    "hi": {"name": "Hindi", "gtts_code": "hi", "script": "Devanagari"},
    "en": {"name": "English", "gtts_code": "en", "script": "Latin"},
    "mr": {"name": "Marathi", "gtts_code": "mr", "script": "Devanagari"},
    "gu": {"name": "Gujarati", "gtts_code": "gu", "script": "Gujarati"},
    "bn": {"name": "Bengali", "gtts_code": "bn", "script": "Bengali"},
    "pa": {"name": "Punjabi", "gtts_code": "pa", "script": "Gurmukhi"},
    "ta": {"name": "Tamil", "gtts_code": "ta", "script": "Tamil"},
    "te": {"name": "Telugu", "gtts_code": "te", "script": "Telugu"},
    "kn": {"name": "Kannada", "gtts_code": "kn", "script": "Kannada"},
    "ml": {"name": "Malayalam", "gtts_code": "ml", "script": "Malayalam"},
    "or": {"name": "Odia", "gtts_code": "or", "script": "Odia"},
    "ur": {"name": "Urdu", "gtts_code": "ur", "script": "Arabic"},
    "as": {"name": "Assamese", "gtts_code": "as", "script": "Bengali"},
}

try:
    SUPPORTED_GTTS_LANGS = gtts.lang.tts_langs()
except Exception as e:
    logger.error(f"Error checking gTTS languages: {e}")
    SUPPORTED_GTTS_LANGS = {}

for lang_code, info in LANGUAGES.items():
    gtts_c = info["gtts_code"]
    if gtts_c not in SUPPORTED_GTTS_LANGS:
        logger.warning(f"gTTS does not support language code '{gtts_c}' ({info['name']}). TTS audio will be disabled for this language.")
        info["gtts_supported"] = False
    else:
        info["gtts_supported"] = True
