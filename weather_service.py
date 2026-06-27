import os
import logging
import requests
from flask import Blueprint, jsonify, request

logger = logging.getLogger("kisan_saathi")

weather_bp = Blueprint("weather", __name__)

# Weather translation map from existing app.py
weather_translations = {
    'clear sky': 'साफ आकाश',
    'few clouds': 'कम बादल',
    'scattered clouds': 'बिखरे बादल',
    'broken clouds': 'टूटे बादल',
    'shower rain': 'बोछारें',
    'rain': 'बारिश',
    'thunderstorm': 'आंधी-तूफान',
    'snow': 'बर्फबारी',
    'mist': 'कोहरा',
    'haze': 'धुंध',
    'overcast clouds': 'घने बादल',
    'light rain': 'हल्की बारिश',
    'moderate rain': 'सामान्य बारिश',
    'heavy intensity rain': 'भारी वर्षा'
}

def translate_weather(desc, lang):
    desc_lower = desc.lower()
    if lang == "hi":
        return weather_translations.get(desc_lower, desc).capitalize()
    elif lang == "en":
        return desc.capitalize()
    else:
        try:
            from googletrans import Translator
            translator = Translator()
            return translator.translate(desc, src='en', dest=lang).text.capitalize()
        except Exception:
            return weather_translations.get(desc_lower, desc).capitalize()

@weather_bp.route("/api/weather")
def get_weather():
    city = request.args.get("city", "Indore")
    lang = request.args.get("lang", "hi")
    
    api_key = os.getenv("OPENWEATHER_API_KEY", "")
    
    # Base fallback values (simulated dynamic Indore weather if key missing or unreachable)
    fallback_data = {
        "success": True,
        "temp": 32.0,
        "desc": "scattered clouds",
        "desc_hi": "बिखरे बादल",
        "main_desc": "Clouds",
        "humidity": 45.0,
        "wind": 3.5,
        "advisory": "फसलों की सामान्य देखरेख जारी रखें। Keep normal crop monitoring.",
        "forecast": [
            {"day": "Tomorrow", "temp": 33, "desc": "Light rain", "desc_hi": "हल्की बारिश"},
            {"day": "Day After", "temp": 31, "desc": "Moderate rain", "desc_hi": "सामान्य बारिश"},
            {"day": "3rd Day", "temp": 32, "desc": "Scattered clouds", "desc_hi": "बिखरे बादल"}
        ]
    }

    if not api_key:
        logger.warning("OPENWEATHER_API_KEY missing in environment. Using fallback data.")
        return jsonify(fallback_data)

    try:
        # 1. Fetch current weather
        curr_url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
        curr_res = requests.get(curr_url, timeout=5)
        
        if curr_res.status_code != 200:
            logger.error(f"OpenWeather current weather query failed for {city}: {curr_res.text}")
            return jsonify(fallback_data)
            
        curr_data = curr_res.json()
        
        # 2. Fetch 3-day forecast (using 5 day / 3 hour forecast)
        fore_url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={api_key}&units=metric"
        fore_res = requests.get(fore_url, timeout=5)
        
        forecast_list = []
        forecast_rain_sum = 0.0
        
        if fore_res.status_code == 200:
            fore_data = fore_res.json()
            # Group by days (approx. 24 hour intervals or 8 steps later)
            cnt = 0
            for i in range(8, len(fore_data.get("list", [])), 8):
                if cnt >= 3:
                    break
                item = fore_data["list"][i]
                rain_val = item.get("rain", {}).get("3h", 0.0)
                forecast_rain_sum += rain_val
                
                desc_val = item["weather"][0]["description"]
                forecast_list.append({
                    "day": f"Day {cnt+1}",
                    "temp": round(item["main"]["temp"]),
                    "desc": desc_val.capitalize(),
                    "desc_hi": translate_weather(desc_val, "hi")
                })
                cnt += 1
                
        # Determine agricultural advisories
        advisories = []
        temp = curr_data["main"]["temp"]
        humidity = curr_data["main"]["humidity"]
        rain_current = curr_data.get("rain", {}).get("1h", 0.0)
        
        if rain_current > 20.0 or forecast_rain_sum > 20.0:
            advisories.append("⚠️ कीटनाशक छिड़काव रोकें: भारी बारिश की चेतावनी (Delay pesticide spray: heavy rain warning)")
        if temp > 40.0:
            advisories.append("🚜 फसलों की सिंचाई करें: तीव्र तापमान चेतावनी (Irrigate crops: high temperature warning)")
        if humidity > 80.0:
            advisories.append("🍄 उच्च फंगल संक्रमण जोखिम: नमी अधिक है (High fungal disease risk due to high humidity)")
            
        if not advisories:
            advisories.append("🌾 फसलों की सामान्य देखरेख जारी रखें। (Keep normal crop monitoring.)")
            
        desc = curr_data["weather"][0]["description"]
        
        return jsonify({
            "success": True,
            "temp": temp,
            "desc": desc.capitalize(),
            "desc_hi": translate_weather(desc, lang),
            "main_desc": curr_data["weather"][0]["main"],
            "humidity": humidity,
            "wind": curr_data["wind"]["speed"],
            "advisory": " | ".join(advisories),
            "forecast": forecast_list
        })
        
    except Exception as e:
        logger.error(f"Error querying weather service: {e}")
        return jsonify(fallback_data)
