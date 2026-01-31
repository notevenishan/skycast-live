from flask import Flask, render_template, request
import requests

app = Flask(__name__)

API_KEY = "7278a08a4648f4ee1e2441acf90e991b" 
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

@app.route("/", methods=["GET", "POST"])
def home():
    weather_data = None
    if request.method == "POST":
        city = request.form.get("city")
        lat = request.form.get("lat")
        lon = request.form.get("lon")
        
        url = ""
        
        if city:
            url = f"{BASE_URL}?q={city}&appid={API_KEY}&units=metric"
        elif lat and lon:
            url = f"{BASE_URL}?lat={lat}&lon={lon}&appid={API_KEY}&units=metric"
            
        if url:
            response = requests.get(url)
            data = response.json()
            if data.get("cod") == 200:
                # Get coordinates for AQI
                coord_lat = data["coord"]["lat"]
                coord_lon = data["coord"]["lon"]
                
                # Fetch AQI
                aqi_url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={coord_lat}&lon={coord_lon}&appid={API_KEY}"
                aqi_response = requests.get(aqi_url)
                aqi_data = aqi_response.json()
                
                aqi_val = 0
                aqi_desc = "Unknown"
                
                if "list" in aqi_data and len(aqi_data["list"]) > 0:
                    # simplistic conversion from PM2.5 to US AQI (approximate)
                    # Real formula is complex, this is a rough estimation for demo purposes
                    pm2_5 = aqi_data["list"][0]["components"]["pm2_5"]
                    
                    if pm2_5 <= 12.0:
                        aqi_val = round((50 - 0) / (12.0 - 0) * (pm2_5 - 0) + 0)
                        aqi_desc = "Good"
                    elif pm2_5 <= 35.4:
                        aqi_val = round((100 - 51) / (35.4 - 12.1) * (pm2_5 - 12.1) + 51)
                        aqi_desc = "Moderate"
                    elif pm2_5 <= 55.4:
                        aqi_val = round((150 - 101) / (55.4 - 35.5) * (pm2_5 - 35.5) + 101)
                        aqi_desc = "Unhealthy for Sensitive Groups"
                    elif pm2_5 <= 150.4:
                        aqi_val = round((200 - 151) / (150.4 - 55.5) * (pm2_5 - 55.5) + 151)
                        aqi_desc = "Unhealthy"
                    elif pm2_5 <= 250.4:
                        aqi_val = round((300 - 201) / (250.4 - 150.5) * (pm2_5 - 150.5) + 201)
                        aqi_desc = "Very Unhealthy"
                    else:
                        aqi_val = round((500 - 301) / (500.4 - 250.5) * (pm2_5 - 250.5) + 301)
                        aqi_desc = "Hazardous"

                # Outfit Logic
                temp = data["main"]["temp"]
                weather_main = data["weather"][0]["main"].lower()
                weather_id = data["weather"][0]["id"]
                outfit = "Comfortable casual wear."
                
                # Emojis Mappings
                emojis = {
                    "Clear": "☀️",
                    "Clouds": "☁️",
                    "Rain": "🌧️",
                    "Drizzle": "🌦️",
                    "Thunderstorm": "⛈️",
                    "Snow": "❄️",
                    "Mist": "🌫️",
                    "Smoke": "💨",
                    "Haze": "😶‍🌫️",
                    "Dust": "🌪️",
                    "Fog": "🌁",
                    "Sand": "🏜️",
                    "Ash": "🌋",
                    "Squall": "🌬️",
                    "Tornado": "🌪️"
                }
                
                main_cond = data["weather"][0]["main"]
                weather_emoji = emojis.get(main_cond, "🌡️")

                if "rain" in weather_main or "drizzle" in weather_main:
                    outfit = "Raincoat and umbrella essential. Waterproof shoes recommended."
                elif "snow" in weather_main:
                    outfit = "Heavy coat, scarf, gloves, and warm boots."
                elif temp < 10:
                    outfit = "Winter coat, thermal layers, and a beanie."
                elif temp < 18:
                    outfit = "Light jacket, hoodie, or sweater."
                elif temp < 25:
                    outfit = "T-shirt and jeans. Maybe a light cardigan for evening."
                elif temp >= 25:
                    outfit = "Shorts, linen shirt, sunglasses, and sunscreen."

                weather_data = {
                    "city": data["name"],
                    "temp": round(data["main"]["temp"]), 
                    "desc": f"{data['weather'][0]['description'].title()} {weather_emoji}",
                    "main": data["weather"][0]["main"], # Passed for background logic
                    "humidity": data["main"]["humidity"],
                    "wind": data["wind"]["speed"],
                    "icon": data["weather"][0]["icon"],
                    "aqi": aqi_val,
                    "aqi_desc": aqi_desc,
                    "outfit": outfit
                }
            else:
                weather_data = {"error": data.get("message", "Location not found")}
                
    return render_template("index.html", weather=weather_data)

if __name__ == "__main__":
    app.run(debug=True)
