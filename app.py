from flask import Flask, render_template, request
import requests
import re 
import pyttsx3
import threading


from openai import OpenAI
client = OpenAI(api_key="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")

app = Flask(__name__)

API_KEY = "b38b1c72b88aa4669b8281f20950ad40"
import pyttsx3


def speak(text):
    engine = pyttsx3.init()
    engine.setProperty('rate', 160)
    engine.setProperty('volume', 1.0)
    engine.say(text)
    engine.runAndWait()
    engine.stop()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/weather", methods=["POST"])
def weather():
    city = request.form.get("city")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()

    if str(response.get("cod")) != "200":   # 👈 FIXED LINE
        weather_info = "City not found ❌"
    else:
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        weather_info = f"{city.title()} 🌡️ {temp}°C | {desc}"

    return render_template("index.html", weather=weather_info)

@app.route("/chat", methods=["GET", "POST"])
def chat():
    if request.method == "GET":
        # Agar koi direct /chat open kare to home page dikhao
        return render_template("index.html")

    user_msg = request.form.get("message")

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a helpful weather assistant."},
            {"role": "user", "content": user_msg}
        ]
    )

    reply = response.choices[0].message.content
    return render_template("index.html", reply=reply)
@app.route("/ask", methods=["POST"])
def ask():
    question = request.form.get("question").lower()

    city_map = {
        "delhi": ["delhi", "दिल्ली"],
        "mumbai": ["mumbai", "मुंबई"],
        "kolkata": ["kolkata", "कोलकाता"],
        "chennai": ["chennai", "चेन्नई"],
        "bangalore": ["bangalore", "बेंगलुरु"],
        "pune": ["pune", "पुणे"]
    }

    city = None
    for eng, variants in city_map.items():
        for v in variants:
            if v in question:
                city = eng
                break
        if city:
            break

    if not city:
        return render_template("index.html", reply="City samajh nahi aayi ❌")

    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url).json()

    if str(response.get("cod")) != "200":
        reply = "Weather data nahi mila ❌"
    else:
        temp = response["main"]["temp"]
        desc = response["weather"][0]["description"]
        reply = f"{city.title()} ka temperature {temp}°C hai aur weather {desc} hai 🌦️"
    # 🔊 SPEAK
    threading.Thread(target=speak, args=(reply,), daemon=True).start()
    return render_template("index.html", reply=reply)


if __name__ == "__main__":
    app.run(debug=False)