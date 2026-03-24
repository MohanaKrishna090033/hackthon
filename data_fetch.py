import requests

# Chennai coordinates
lat = 13.0827
lon = 80.2707

url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"

response = requests.get(url)
data = response.json()

print("🌡 Temperature:", data['current_weather']['temperature'])
print("🌬 Wind Speed:", data['current_weather']['windspeed'])