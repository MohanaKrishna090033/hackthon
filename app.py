import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
from io import StringIO   # ← this is already correct

st.set_page_config(page_title="HydroHeat AI", layout="wide", page_icon="🌡️💧")

st.title("🇮🇳 HydroHeat AI - India Climate Sandbox")
st.markdown("**Real-time urban heat + groundwater simulator (IMD + CGWB + Open-Meteo)**")

# ==================== DATASET ====================
@st.cache_data
def load_data():
    data = """city,ward,lat,lon,temp,groundwater,vegetation,builtup,rainfall
Delhi,Connaught Place,28.6139,77.2090,39.2,4.8,12,88,650
Delhi,Rohini,28.7495,77.0565,37.8,6.2,18,82,650
Mumbai,Colaba,18.9067,72.8147,35.1,2.3,22,78,2100
Mumbai,Bandra,19.0596,72.8295,36.4,1.9,19,81,2100
Chennai,T.Nagar,13.0418,80.2341,36.7,6.8,25,75,850
Chennai,Anna Nagar,13.0850,80.2101,35.9,8.1,35,65,850
Chennai,Velachery,12.9750,80.2212,37.4,5.9,18,82,850
Bengaluru,Whitefield,12.9698,77.7499,34.8,8.4,28,72,900
Bengaluru,Koramangala,12.9279,77.6271,36.1,7.2,24,76,900
Hyderabad,Hitech City,17.4435,78.3772,39.6,6.1,16,84,800
"""
    return pd.read_csv(StringIO(data))

df = load_data()

# ==================== LIVE API ====================
def get_live_temp(lat, lon):
    url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
    try:
        res = requests.get(url).json()
        return res["current_weather"]["temperature"]
    except:
        return None

# Update with live temperature (real-time!)
for idx, row in df.iterrows():
    live_temp = get_live_temp(row["lat"], row["lon"])
    if live_temp is not None:
        df.at[idx, "temp"] = live_temp

# ==================== SIDEBAR ====================
st.sidebar.header("🎮 Controls")

selected_city = st.sidebar.selectbox("City", df["city"].unique())
filtered = df[df["city"] == selected_city]
selected_ward = st.sidebar.selectbox("Ward", filtered["ward"].unique())

ward_row = df[(df["city"] == selected_city) & (df["ward"] == selected_ward)].iloc[0]

veg_change = st.sidebar.slider("🌳 Vegetation Change %", -50, 50, 0)
built_change = st.sidebar.slider("🏢 Built-up Change %", -30, 50, 0)
rain_change = st.sidebar.slider("🌧 Rainfall Change %", -40, 20, 0)

col1, col2 = st.sidebar.columns(2)
if col1.button("🌳 Green City", use_container_width=True):
    veg_change = 30; built_change = -15; rain_change = 10
if col2.button("🏭 Urban Boom", use_container_width=True):
    veg_change = -20; built_change = 25; rain_change = -5

# ==================== SIMULATION ====================
def simulate(base_temp, base_gw, veg_c, built_c, rain_c):
    new_temp = base_temp + (built_c * 0.035) - (veg_c * 0.04)
    new_gw = max(0, base_gw + (rain_c * 0.005) - (new_temp * 0.02))
    return round(new_temp, 1), round(new_gw, 1)

new_temp, new_gw = simulate(ward_row["temp"], ward_row["groundwater"], veg_change, built_change, rain_change)

# ==================== MAIN DASHBOARD ====================
col1, col2, col3 = st.columns(3)
col1.metric("🌡️ Temperature", f"{new_temp}°C", f"{new_temp - ward_row['temp']:.1f}")
col2.metric("💧 Groundwater", f"{new_gw}m", f"{new_gw - ward_row['groundwater']:.1f}")
col3.metric("⚠️ Risk Score", f"{new_temp*0.6 + (10-new_gw)*0.4:.1f}")

st.subheader("🤖 AI Climate Insight")
if new_temp > 38:
    st.error("🚨 CRITICAL HEAT RISK — Add 30%+ green cover immediately")
elif new_gw < 5:
    st.warning("⚠️ GROUNDWATER EMERGENCY — Build recharge structures")
else:
    st.success("✅ Balanced conditions")

# India Map
st.subheader("🇮🇳 India Climate Risk Map")
df["risk_score"] = df["temp"] * 0.6 + (10 - df["groundwater"]) * 0.4
fig_map = px.scatter_geo(df, lat="lat", lon="lon", hover_name="ward",
                         size="risk_score", color="risk_score",
                         color_continuous_scale="Reds", size_max=30,
                         title="Urban Heat + Groundwater Risk")
st.plotly_chart(fig_map, use_container_width=True)

# Prediction Chart
st.subheader("📈 Future Prediction (2026–2040)")
years = list(range(2026, 2041))
temps = [new_temp + (y-2026)*0.15 for y in years]
gws = [new_gw - (y-2026)*0.25 for y in years]
fig_time = go.Figure()
fig_time.add_trace(go.Scatter(x=years, y=temps, name="Temperature (°C)", line=dict(color="red")))
fig_time.add_trace(go.Scatter(x=years, y=gws, name="Groundwater (m)", line=dict(color="blue"), yaxis="y2"))
fig_time.update_layout(yaxis2=dict(overlaying="y", side="right"), height=400)
st.plotly_chart(fig_time, use_container_width=True)

st.dataframe(df, use_container_width=True)
