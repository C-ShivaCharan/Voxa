import requests

API_KEY = "0e2097df482562304186b80a8644343f"
city = "Bangalore"

url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
response = requests.get(url)
data = response.json()

if response.status_code == 200:
    temp = data["main"]["temp"]
    desc = data["weather"][0]["description"]
    print(f"Weather in {city}: {temp}°C, {desc}")
else:
    print(f"Failed to fetch weather data: {data.get('message', 'Unknown error')}")
