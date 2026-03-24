import requests
import pandas as pd

# --- STEP 1: Base dataset ---
data = [
    ["Chennai","TNagar",13.0418,80.2341,36.7,6.8,25,75,850],
    ["Delhi","ConnaughtPlace",28.6139,77.2090,39.2,4.8,12,88,650],
    ["Mumbai","Bandra",19.0596,72.8295,36.4,1.9,19,81,2100],
    ["Bengaluru","Whitefield",12.9698,77.7499,34.8,8.4,28,72,900]
]

df = pd.DataFrame(data, columns=[
    "city","ward","lat","lon","temp","groundwater","vegetation","builtup","rainfall"
])

# --- STEP 2: Fetch REAL-TIME temperature ---
def get_live_temp(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        res = requests.get(url).json()
        return res["current_weather"]["temperature"]
    except:
        return None

# --- STEP 3: Update dataset dynamically ---
live_temps = []

for index, row in df.iterrows():
    live_temp = get_live_temp(row["lat"], row["lon"])
    
    if live_temp:
        df.at[index, "temp"] = live_temp
    
    live_temps.append(live_temp)

# --- STEP 4: Print updated data ---
print("\n🌍 LIVE DATASET\n")
print(df)

def simulate(temp, water, veg, built, rain):
    new_temp = temp + (built * 0.02) - (veg * 0.03)
    new_water = water + (rain * 0.005) - (new_temp * 0.02)
    return round(new_temp,2), round(new_water,2)

print("\n🔮 SIMULATION OUTPUT\n")

for index, row in df.iterrows():
    new_temp, new_water = simulate(
        row["temp"],
        row["groundwater"],
        row["vegetation"],
        row["builtup"],
        row["rainfall"]
    )
    
    print(f"{row['city']} → Temp: {new_temp}, Water: {new_water}")