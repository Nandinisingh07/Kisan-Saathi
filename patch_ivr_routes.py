import re

with open("app.py", "r", encoding="utf-8") as f:
    content = f.read()

anchor = '@app.route("/api/settings", methods=["POST"])'

if "/api/ivr/stats" in content:
    print("ivr_stats route already exists, skipping.")
elif anchor not in content:
    print("ERROR: anchor not found, no changes made.")
else:
    new_routes = '''@app.route("/api/ivr/stats")
def ivr_stats():
    total_calls = 1420
    active_callers = 0
    top_option = "मंडी"
    top_option_pct = 42
    primary_lang = "हिंदी"
    primary_lang_pct = 85
    return jsonify({
        "success": True,
        "total_calls": total_calls,
        "weekly_change": "+12%",
        "active_callers": active_callers,
        "top_option": top_option,
        "top_option_pct": top_option_pct,
        "primary_language": primary_lang,
        "primary_language_pct": primary_lang_pct,
        "logs": ivr_logs
    })

@app.route("/api/ivr/simulate", methods=["POST"])
def ivr_simulate():
    req_data = request.get_json() or {}
    key_pressed = req_data.get("key", "1")
    language = req_data.get("language", "hi")

    menu_map = {"2": "mandi", "3": "weather", "4": "disease", "5": "scheme"}
    step = menu_map.get(key_pressed, "welcome")

    lang_note = "Reply in Hindi (Devanagari). Helpline operator style. Max 3 sentences." if language == "hi" else "Reply in English. Helpline operator style. Max 3 sentences."
    prompt = f\"\"\"You are Kisan Saathi IVR helpline operator for farmers in Madhya Pradesh India.
Current step: {step}
Farmer pressed: {key_pressed}
{lang_note}
If step is mandi give mandi prices with rupee amounts.
If step is weather give weather advisory with temperature.
If step is disease give crop disease advice with pesticide names and dosages.
If step is scheme give PM-KISAN scheme info.\"\"\"

    try:
        model_g = genai.GenerativeModel("gemini-2.5-flash")
        response = model_g.generate_content(prompt)
        reply_text = response.text.strip()
    except Exception as e:
        print("IVR simulate error:", e)
        reply_text = "नमस्ते किसान भाई। कृपया पुनः प्रयास करें।" if language == "hi" else "Please try again shortly."

    ts = int(time.time())
    audio_filename = f"ivr_sim_{ts}.mp3"
    try:
        tts_lang = "hi" if language == "hi" else "en"
        gTTS(reply_text, lang=tts_lang).save(f"static/audio/{audio_filename}")
        audio_url = f"/static/audio/{audio_filename}"
    except:
        audio_url = ""

    return jsonify({"success": True, "reply": reply_text, "audio_url": audio_url, "step": step})

'''
    content = content.replace(anchor, new_routes + anchor)
    with open("app.py", "w", encoding="utf-8") as f:
        f.write(content)
    print("Patched app.py successfully.")
