import os
import requests
import streamlit as st
import folium
from streamlit.components.v1 import html
from geopy.geocoders import Nominatim
import math
import heapq
import random
import time
from folium.plugins import AntPath

st.set_page_config(
    page_title="SkyAid Navigator: Emergency Air Response System",
    layout="wide",
    page_icon="🚁",
)

# ================= DRONE SYSTEM =================
DRONE_MAX_RANGE_KM = 25
DRONE_BATTERY_MIN = 30

# ================= METEOR SKY =================
PAGE_STYLE = """
<style>
.stApp {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    font-family: Orbitron;
}

.star {
    position: absolute;
    width: 2px;
    height: 90px;
    background: linear-gradient(white, transparent);
    transform: rotate(45deg);
    filter: drop-shadow(0 0 8px white);
}

@keyframes fall {
    0% { transform: translateY(-10vh) rotate(45deg); opacity: 1; }
    100% { transform: translateY(120vh) translateX(-100px) rotate(45deg); opacity: 0; }
}
</style>
"""
st.markdown(PAGE_STYLE, unsafe_allow_html=True)

STARS = """
<div id="sky"></div>
<script>
const sky = document.getElementById("sky");

function star() {
    const s = document.createElement("div");
    s.className = "star";
    s.style.left = Math.random()*100 + "vw";
    s.style.top = "-10vh";
    let t = 1.5 + Math.random()*3;
    s.style.animation = `fall ${t}s linear`;
    sky.appendChild(s);
    setTimeout(()=>s.remove(), t*1000);
}
setInterval(star, 80);
</script>
"""
html(STARS, height=0)

# ================= AI SYSTEM =================
def mission_success(distance, hazards, wind, vehicle):
    score = 100
    score -= distance * 1.3
    score -= hazards * 10

    if vehicle == "drone":
        score -= max(0, wind - 10) * 4
    else:
        score -= max(0, wind - 15) * 2

    return max(5, min(99, score))


def battery_drain(distance, wind):
    return (distance * 3) + max(0, wind - 8) * 2


def hazard_map(grid_size=20):
    return {(random.randint(0, grid_size-1), random.randint(0, grid_size-1)) for _ in range(25)}

HAZARDS = hazard_map()

# ================= UI =================
st.title("SkyAid Navigator - AI Emergency Command System")
st.caption("Live disaster response + autonomous aerial routing")

start_place = st.text_input("Start Location")
end_place = st.text_input("Destination")

mode = st.selectbox("Vehicle Mode", ["Drone", "Helicopter", "Both"])

if st.button("Launch Mission"):

    geo = Nominatim(user_agent="sky")
    start_loc = geo.geocode(start_place)
    end_loc = geo.geocode(end_place)

    if not start_loc or not end_loc:
        st.error("Invalid location")
        st.stop()

    start = (start_loc.latitude, start_loc.longitude)
    end = (end_loc.latitude, end_loc.longitude)

    st.success("Mission initialized")

    # ================= SIMULATION VALUES =================
    distance = random.uniform(5, 25)
    wind = random.uniform(5, 20)
    hazards = random.randint(1, 6)

    time_est = distance * 2

    # ================= DRONE PHYSICS =================
    battery = battery_drain(distance, wind)
    range_used = (distance / DRONE_MAX_RANGE_KM) * 100

    st.subheader("Live Telemetry")
    st.write(f"Wind: {wind:.1f} mph")
    st.write(f"Hazards detected: {hazards}")
    st.write(f"Distance: {distance:.1f} km")

    st.metric("Battery Drain", f"{battery:.1f}%")
    st.metric("Range Usage", f"{range_used:.0f}%")

    # ================= AUTO SWITCH =================
    vehicle = mode.lower()

    if vehicle == "drone" and (battery > 100 or distance > DRONE_MAX_RANGE_KM):
        st.error("Drone failure predicted → switching to Helicopter")
        vehicle = "helicopter"

    # ================= AI SCORE =================
    success = mission_success(distance, hazards, wind, vehicle)

    st.metric("Mission Success Probability", f"{success:.0f}%")

    if success > 80:
        st.success("🟢 Optimal Mission Conditions")
    elif success > 50:
        st.warning("🟡 Moderate Risk")
    else:
        st.error("🔴 High Failure Risk")

    # ================= MAP =================
    m = folium.Map(location=start, zoom_start=10)

    folium.Marker(start, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)
    folium.Marker(end, tooltip="End", icon=folium.Icon(color="red")).add_to(m)

    route = [start, end]

    # Animated route
    AntPath(route, color="blue", delay=600).add_to(m)

    # ================= MOVING VEHICLE SIM =================
    marker = folium.Marker(start, icon=folium.Icon(color="blue"))
    marker.add_to(m)

    for i in range(10):
        lat = start[0] + (end[0]-start[0])*(i/10)
        lon = start[1] + (end[1]-start[1])*(i/10)
        marker.location = (lat, lon)

    st.components.v1.html(m._repr_html_(), height=500)

    # ================= MISSION FEED =================
    st.subheader("Mission Control Feed")

    feed = [
        "Scanning airspace...",
        "Analyzing hazards...",
        "Calculating optimal route...",
        "Evaluating vehicle performance...",
        "Finalizing mission plan..."
    ]

    for f in feed:
        st.write("✔ " + f)
        time.sleep(0.2)

    st.success("Mission complete simulation executed")
