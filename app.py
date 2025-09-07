from flask import Flask, render_template, request, jsonify
import wikipedia
import datetime
import requests
import pyjokes
import os
import subprocess
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

app = Flask(__name__)

# API keys from environment
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

# ---------------- Utility Functions ----------------

def clean_command(command: str) -> str:
    """Remove emojis and non-ASCII characters from input."""
    return re.sub(r'[^\x00-\x7F]+', '', command).strip()

def wiki_search(query: str) -> str:
    try:
        return wikipedia.summary(query, sentences=2)
    except Exception:
        return "I could not find any information on Wikipedia."

def weather(city: str) -> str:
    """
    Fetch weather for a given city from OpenWeather API.
    """
    if not city:
        return "Please tell me a city name."

    try:
        url = (
            f"http://api.openweathermap.org/data/2.5/weather"
            f"?q={city}&appid={WEATHER_API_KEY}&units=metric"
        )
        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            return f"Error fetching weather: {data.get('message', 'Unknown error')}"

        main = data.get("main")
        weather_list = data.get("weather")

        if main and weather_list:
            temp = main.get("temp")
            desc = weather_list[0].get("description").capitalize()
            humidity = main.get("humidity")
            return f"The temperature in {city} is {temp}°C with {desc}. Humidity: {humidity}%"
        else:
            return "City not found or API returned incomplete data."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to the weather API: {e}"

def get_time() -> str:
    return datetime.datetime.now().strftime("The current time is %I:%M %p")

def get_date() -> str:
    return datetime.datetime.now().strftime("Today is %B %d, %Y")

def open_website(site: str) -> dict:
    """Return a dict with message and URL for frontend to open."""
    sites = {
        "youtube": "https://www.youtube.com",
        "facebook": "https://www.facebook.com",
        "linkedin": "https://www.linkedin.com",
        "twitter": "https://twitter.com",
        "gmail": "https://mail.google.com",
        "google": "https://www.google.com",
        "reddit": "https://www.reddit.com",
    }
    site_key = site.lower().strip()
    url = sites.get(site_key, f"https://{site_key}.com")
    return {"message": f"Opening {site_key}", "url": url}

def tell_joke() -> str:
    return pyjokes.get_joke()

def get_news() -> str:
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=us&apiKey={NEWS_API_KEY}"
        response = requests.get(url).json()
        articles = response.get("articles")
        if articles:
            headlines = [f"{i+1}. {article['title']}" for i, article in enumerate(articles[:5])]
            return "Here are the top 5 news headlines:\n" + "\n".join(headlines)
        else:
            return "Sorry, I could not fetch news right now."
    except requests.exceptions.RequestException:
        return "Error connecting to the news API."

def save_note(note: str, filename="notes.txt") -> str:
    with open(filename, "a") as f:
        f.write(note + "\n")
    return "Note saved."

def read_notes(filename="notes.txt") -> str:
    if os.path.exists(filename):
        with open(filename, "r") as f:
            notes = f.read()
        return f"Here are your notes:\n{notes}"
    else:
        return "No notes found."

def install_package(package: str) -> str:
    try:
        subprocess.check_call([os.sys.executable, "-m", "pip", "install", package])
        return f"{package} installed successfully."
    except Exception:
        return f"Failed to install {package}."

# ---------------- Command Processing ----------------

def process_command(command: str) -> dict:
    """Process user command and return a consistent JSON response."""
    c = clean_command(command.lower())

    # Greetings
    greetings = ["hi", "hello", "hey", "good morning", "good afternoon", "good evening"]
    if any(word in c for word in greetings):
        return {"type": "text", "message": "Hello! I'm Voxa. How can I help you today?"}

    # Stop command
    if c in ["stop", "exit", "quit", "bye"]:
        return {"type": "text", "message": "Goodbye!"}

    # Wikipedia
    if "wikipedia" in c:
        return {"type": "text", "message": wiki_search(c.replace("wikipedia", "").strip())}

    # ✅ Weather (improved city extraction)
    if "weather" in c:
        if " in " in c:
            city = c.split(" in ", 1)[1].strip()
        else:
            city = c.replace("weather", "").strip()
        return {"type": "text", "message": weather(city)}

    # Time
    if "time" in c:
        return {"type": "text", "message": get_time()}

    # Date
    if "date" in c:
        return {"type": "text", "message": get_date()}

    # Open website
    if c.startswith("open "):
        site_name = c[len("open "):].strip()
        return {"type": "url", **open_website(site_name)}

    # Joke
    if "joke" in c:
        return {"type": "text", "message": tell_joke()}

    # News
    if "news" in c:
        return {"type": "text", "message": get_news()}

    # Notes
    if "note" in c and "save" in c:
        return {"type": "text", "message": save_note(c.replace("save note", "").strip())}
    if "read notes" in c:
        return {"type": "text", "message": read_notes()}

    # Install package
    if c.startswith("install "):
        return {"type": "text", "message": install_package(c[len("install "):].strip())}

    return {"type": "text", "message": "Sorry, I cannot perform this command yet."}

# ---------------- Flask Routes ----------------

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/command", methods=["POST"])
def command_route():
    data = request.get_json()
    user_command = data.get("command", "")
    response = process_command(user_command)
    return jsonify(response)

if __name__ == "__main__":
    app.run(debug=True)
