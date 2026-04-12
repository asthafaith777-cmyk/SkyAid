import os
import requests
import streamlit as st
import folium
from streamlit.components.v1 import html
from geopy.geocoders import Nominatim
import math
import heapq
import random

st.set_page_config(
    page_title="SkyAid Navigator: Emergency Air Response System",
    layout="wide",
    page_icon="airplane",
)

PAGE_STYLE = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: #ffffff;
        font-family: 'Orbitron', monospace;
    }
    .block-container {
        padding: 2rem 2rem 2.5rem;
        border-radius: 24px;
        background-color: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border: 2px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 24px 60px rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(10px);
    }
    .stSidebar .sidebar-content {
        background: rgba(255, 255, 255, 0.1);
        color: #ffffff;
        border-radius: 20px;
        padding: 1rem 1rem 1.25rem;
        border: 2px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    .stButton>button {
        background: linear-gradient(135deg, #ff6b6b, #4ecdc4);
        color: white;
        border-radius: 12px;
        padding: 0.85rem 1.35rem;
        border: none;
        font-weight: 700;
        font-size: 1rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        box-shadow: 0 10px 25px rgba(255, 107, 107, 0.3);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #ff5252, #45b7aa);
        transform: translateY(-2px);
        box-shadow: 0 15px 35px rgba(255, 107, 107, 0.4);
    }
    .stTextInput>div>div>input {
        background: rgba(255, 255, 255, 0.9);
        color: #000000;
        border-radius: 12px;
        border: 2px solid rgba(255, 255, 255, 0.3);
        padding: 0.85rem 1rem;
        font-size: 1rem;
        font-weight: 500;
    }
    .stTextInput>div>div>input:focus {
        border-color: #ff6b6b;
        box-shadow: 0 0 10px rgba(255, 107, 107, 0.5);
    }
    .stTextInput label, .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown p {
        color: #ffffff;
        font-family: 'Orbitron', monospace;
        font-weight: 400;
    }
    .stMarkdown h1 {
        font-size: 3rem;
        font-weight: 900;
        text-shadow: 0 0 20px rgba(255, 107, 107, 0.5);
        margin-bottom: 0.5rem;
        text-align: center;
    }
    .stMarkdown h2 {
        font-size: 1.5rem;
        font-weight: 700;
        margin-top: 0;
        margin-bottom: 1.5rem;
        text-align: center;
        color: #f8f9fa;
    }
    .stMarkdown h3 {
        font-weight: 700;
        font-size: 1.2rem;
        color: #f1f3f4;
    }
    .stMetric {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 18px;
        padding: 0.85rem;
        border: 1px solid rgba(255, 255, 255, 0.2);
    }
    .dashboard-card {
        border-radius: 20px;
        background: rgba(255, 255, 255, 0.1);
        padding: 1.25rem;
        border: 2px solid rgba(255, 255, 255, 0.2);
        backdrop-filter: blur(10px);
    }
    .animation-row {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        margin-top: 1rem;
        font-size: 1rem;
        color: #ffffff;
        font-weight: 500;
    }
    .pulse-dot {
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        animation: pulse 1.5s ease-in-out infinite;
        box-shadow: 0 0 10px rgba(255, 107, 107, 0.6);
    }
    @keyframes pulse {
        0% { transform: scale(0.8); opacity: 0.7; }
        50% { transform: scale(1.5); opacity: 0.3; }
        100% { transform: scale(0.8); opacity: 0.7; }
    }
    .route-line {
        animation: dash 3s linear infinite;
    }
    @keyframes dash {
        to {
            stroke-dashoffset: -20;
        }
    }
    .stSelectbox, .stRadio {
        color: #ffffff;
    }
    .stSelectbox label, .stRadio label {
        color: #ffffff;
        font-weight: 600;
    }
    .stars-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        pointer-events: none;
        z-index: 999999;
        overflow: hidden;
    }
    .star {
        position: absolute;
        width: 3px;
        height: 3px;
        background: #ffffff;
        border-radius: 50%;
        box-shadow: 0 0 4px rgba(255, 255, 255, 1);
    }
    .star-twinkle {
        animation: twinkle 3s infinite;
    }
    .star-move {
        animation: moveStars 20s linear infinite;
    }
    @keyframes twinkle {
        0%, 100% { opacity: 0.4; }
        50% { opacity: 1; }
    }
    @keyframes moveStars {
        0% { transform: translateY(0px) translateX(0px); }
        25% { transform: translateY(-20px) translateX(10px); }
        50% { transform: translateY(-40px) translateX(-10px); }
        75% { transform: translateY(-20px) translateX(10px); }
        100% { transform: translateY(0px) translateX(0px); }
    }
</style>
"""
st.markdown(PAGE_STYLE, unsafe_allow_html=True)

# Add moving stars effect
STARS_HTML = """
<div class="stars-container" id="starsContainer"></div>
<script>
    // Create stars dynamically
    const container = document.getElementById('starsContainer');
    const starCount = 100;
    
    for (let i = 0; i < starCount; i++) {
        const star = document.createElement('div');
        star.className = 'star star-twinkle star-move';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animationDelay = (Math.random() * 3) + 's';
        star.style.animationDuration = (15 + Math.random() * 10) + 's';
        container.appendChild(star);
    }
</script>
"""
st.markdown(STARS_HTML, unsafe_allow_html=True)

st.markdown(
    """
    <div class='dashboard-card'>
        <h1>SkyAid Navigator</h1>
        <h2>Emergency Air Response System</h2>
        <p>Navigate emergency response with AI-powered route optimization and real-time hazard analysis.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

st.sidebar.header("Mission Control")
st.sidebar.write(
    """
    - Compare drone and helicopter routing across emergency scenarios.
    - Visualize restricted airspace and hazard zones.
    - Explore AI-driven mission data for emergency response planning.
    """
)
st.sidebar.info("Enter both locations and generate a route to view the map and mission summary.")

GRID_SIZE = 30
random.seed(42)

no_fly_center = (GRID_SIZE // 2, GRID_SIZE // 2)
no_fly_radius = 6

SCENARIO_CONFIG = {
    "Wildfire": {"hazard_bias": 0.18, "no_fly_scale": 1.4, "color": "#e63946", "label": "Wildfire"},
    "Earthquake": {"hazard_bias": 0.12, "no_fly_scale": 1.2, "color": "#fb923c", "label": "Earthquake"},
    "Flood": {"hazard_bias": 0.10, "no_fly_scale": 1.0, "color": "#0ea5e9", "label": "Flood"},
}

min_lat = None
max_lat = None
min_lon = None
max_lon = None


def to_grid(lat, lon):
    x = int((lat - min_lat) / (max_lat - min_lat) * (GRID_SIZE - 1))
    y = int((lon - min_lon) / (max_lon - min_lon) * (GRID_SIZE - 1))
    return (x, y)


def disaster_zone(cell, scenario_bias=0.0):
    x, y = cell
    probability = 0.06 + scenario_bias
    threshold = int(min(max(probability, 0.02), 0.28) * 100)
    return ((x * 17 + y * 13 + 7) % 100) < threshold


def in_no_fly(cell, no_fly_scale=1.0):
    return math.dist(cell, no_fly_center) < no_fly_radius * no_fly_scale


def heuristic(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def get_neighbors(node, vehicle="drone", scenario_bias=0.0, no_fly_scale=1.0):
    x, y = node
    moves = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    results = []

    for dx, dy in moves:
        nx, ny = x + dx, y + dy

        if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE:
            if vehicle == "drone":
                if in_no_fly((nx, ny), no_fly_scale):
                    continue

            if vehicle == "helicopter":
                if disaster_zone((nx, ny), scenario_bias) and ((nx + ny) % 3 == 0):
                    continue

            results.append((nx, ny))

    return results


def astar(start, goal, vehicle="drone", scenario_bias=0.0, no_fly_scale=1.0):
    open_set = []
    heapq.heappush(open_set, (0, start))

    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            break

        for neighbor in get_neighbors(current, vehicle, scenario_bias, no_fly_scale):
            tentative_g = g_score[current] + 1

            if neighbor not in g_score or tentative_g < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f, neighbor))

    path = []
    cur = goal

    while cur in came_from:
        path.append(cur)
        cur = came_from[cur]

    path.append(start)
    return path[::-1]


def fetch_weather(lat, lon):
    api_key = os.getenv("OPENWEATHER_API_KEY")
    fallback = {
        "source": "fallback",
        "wind_mph": 8.0,
        "description": "Moderate conditions",
        "weather": "Moderate conditions",
        "wind_risk": "Low",
    }
    if not api_key:
        return fallback

    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": api_key, "units": "imperial"}
    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        wind_mph = float(data.get("wind", {}).get("speed", 0.0))
        description = data.get("weather", [{}])[0].get("description", "Clear").title()
        wind_risk = "Low" if wind_mph < 10 else "Moderate" if wind_mph < 20 else "High"
        return {
            "source": "OpenWeather",
            "wind_mph": wind_mph,
            "description": description,
            "weather": description,
            "wind_risk": wind_risk,
        }
    except Exception:
        return fallback


def calculate_scores(distance, hazard_count, wind_mph):
    wind_penalty = max(0, wind_mph - 8) * 2.0
    drone_score = 90 - hazard_count * 7 - wind_penalty - distance * 0.55
    helicopter_score = 74 + min(wind_penalty, 18) * 0.5 - hazard_count * 4 + min(distance, 28) * 0.6
    return {
        "drone_score": max(0, min(100, drone_score)),
        "helicopter_score": max(0, min(100, helicopter_score)),
    }


def recommend_vehicle(drone_score, helicopter_score, wind_mph, hazard_count, distance):
    reasons = []
    if wind_mph >= 15:
        reasons.append("Wind conditions favor helicopter stability.")
    if hazard_count >= 3:
        reasons.append("High hazard density increases drone risk.")
    if distance > 20:
        reasons.append("Long-distance missions are better suited for helicopter range.")
    if distance <= 12 and hazard_count < 2 and wind_mph < 12:
        reasons.append("Short mission with low hazards favors drone efficiency.")

    if abs(drone_score - helicopter_score) < 6:
        recommendation = "Hybrid"
        reasons.insert(0, "Both options are viable; use hybrid operational planning.")
    elif helicopter_score > drone_score:
        recommendation = "Helicopter"
        if "Wind conditions favor helicopter stability." not in reasons:
            reasons.append("Helicopter is more stable for current conditions.")
    else:
        recommendation = "Drone"
        if "Short mission with low hazards favors drone efficiency." not in reasons:
            reasons.append("Drone is more efficient for this route.")

    return recommendation, reasons


def grid_to_latlon(cell):
    x, y = cell
    lat = min_lat + (x / GRID_SIZE) * (max_lat - min_lat)
    lon = min_lon + (y / GRID_SIZE) * (max_lon - min_lon)
    return (lat, lon)


def haversine(a, b):
    R = 6371
    dlat = math.radians(b[0] - a[0])
    dlon = math.radians(b[1] - a[1])
    x = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(a[0]))
        * math.cos(math.radians(b[0]))
        * math.sin(dlon / 2) ** 2
    )
    return 2 * R * math.asin(math.sqrt(x))


def build_map(center):
    m = folium.Map(
        location=center,
        zoom_start=12,
        tiles="OpenStreetMap",
        control_scale=True,
        prefer_canvas=True,
    )
    folium.LayerControl(position="topright", collapsed=True).add_to(m)
    return m


def draw_simulation_layers(m, scenario_bias=0.0, no_fly_scale=1.0, scenario_color="#e63946"):
    for x in range(GRID_SIZE):
        for y in range(GRID_SIZE):
            if disaster_zone((x, y), scenario_bias):
                folium.Circle(
                    location=grid_to_latlon((x, y)),
                    radius=400,
                    color=scenario_color,
                    fill=True,
                    fill_color=scenario_color,
                    fill_opacity=0.18,
                    weight=0,
                ).add_to(m)

    folium.Circle(
        location=grid_to_latlon(no_fly_center),
        radius=no_fly_radius * no_fly_scale * 450,
        color="#d00000",
        weight=2,
        fill=False,
        dash_array="10",
        tooltip="Restricted no-fly zone",
    ).add_to(m)


def calculate_risk(route, distance):
    hazards = sum(1 for node in route if disaster_zone(node))
    if hazards >= 3 or distance > 28:
        return "Critical"
    if hazards >= 1 or distance > 16:
        return "High"
    return "Low"


with st.form("route_form"):
    header_col, controls_col = st.columns([3, 1])
    with header_col:
        start_place = st.text_input(
            "Hospital / Start Location",
            placeholder="e.g. Boston General Hospital",
            key="start_place",
        )
        end_place = st.text_input(
            "Emergency / Destination",
            placeholder="e.g. 1600 Amphitheatre Parkway, Mountain View",
            key="end_place",
        )
    with controls_col:
        route_mode = st.radio(
            "Route mode",
            options=["Drone", "Helicopter", "Both"],
            index=2,
            horizontal=False,
            key="route_mode",
        )
        scenario = st.selectbox(
            "Disaster scenario",
            options=["Wildfire", "Earthquake", "Flood"],
            index=0,
            key="scenario",
        )
        st.caption("Choose the emergency scenario to adjust hazard density.")
    submitted = st.form_submit_button("Generate Emergency Route")

if st.button("Reset Map"):
    for key in ["start_place", "end_place", "route_mode"]:
        if key in st.session_state:
            del st.session_state[key]
    st.rerun()

if submitted:
    try:
        if not st.session_state.get("start_place") or not st.session_state.get("end_place"):
            st.warning("Please enter both locations.")
        else:
            start_place = st.session_state["start_place"]
            end_place = st.session_state["end_place"]
            route_mode = st.session_state["route_mode"]

            geolocator = Nominatim(user_agent="air_response_system")
            try:
                start_loc = geolocator.geocode(start_place, timeout=10)
                end_loc = geolocator.geocode(end_place, timeout=10)
            except Exception as exc:
                st.error(f"Geocoding failed: {exc}")
                start_loc = end_loc = None

            if not start_loc or not end_loc:
                st.error("Location not found. Try different text.")
            else:
                start = (start_loc.latitude, start_loc.longitude)
                end = (end_loc.latitude, end_loc.longitude)

                min_lat = min(start[0], end[0]) - 0.02
                max_lat = max(start[0], end[0]) + 0.02
                min_lon = min(start[1], end[1]) - 0.02
                max_lon = max(start[1], end[1]) + 0.02

                start_g = to_grid(*start)
                end_g = to_grid(*end)
                center = [(start[0] + end[0]) / 2, (start[1] + end[1]) / 2]
                scenario = st.session_state.get("scenario", "Wildfire")
                scenario_info = SCENARIO_CONFIG.get(scenario, SCENARIO_CONFIG["Wildfire"])
                scenario_bias = scenario_info["hazard_bias"]
                scenario_color = scenario_info["color"]
                no_fly_scale = scenario_info["no_fly_scale"]
                weather = fetch_weather(end[0], end[1])
                wind_mph = weather["wind_mph"]
                weather_desc = weather["weather"]

                m = build_map(center)
                draw_simulation_layers(
                    m,
                    scenario_bias=scenario_bias,
                    no_fly_scale=no_fly_scale,
                    scenario_color=scenario_color,
                )

                folium.Marker(
                    start,
                    tooltip="Hospital",
                    popup="Hospital / Start",
                    icon=folium.Icon(color="green", icon="plus-sign"),
                ).add_to(m)
                folium.Marker(
                    end,
                    tooltip="Emergency",
                    popup="Emergency / Destination",
                    icon=folium.Icon(color="red", icon="warning-sign"),
                ).add_to(m)

                progress_bar = st.progress(0)
                st.text("Calculating routes...")
                progress_bar.progress(25)

                drone_path = astar(start_g, end_g, "drone", scenario_bias, no_fly_scale)
                progress_bar.progress(50)
                heli_path = astar(start_g, end_g, "helicopter", scenario_bias, no_fly_scale)
                progress_bar.progress(75)

                drone_route = [grid_to_latlon(p) for p in drone_path] if drone_path else []
                heli_route = [grid_to_latlon(p) for p in heli_path] if heli_path else []
                progress_bar.progress(100)
                progress_bar.empty()
                st.success("Routes calculated successfully!")

                if not drone_route and route_mode in ["Drone", "Both"]:
                    st.warning("No viable drone route found due to obstacles. Consider helicopter or adjust scenario.")
                if not heli_route and route_mode in ["Helicopter", "Both"]:
                    st.warning("No viable helicopter route found due to obstacles. Consider drone or adjust scenario.")

                if route_mode in ["Drone", "Both"] and drone_route:
                    folium.PolyLine(
                        drone_route,
                        color="#3b82f6",
                        weight=6,
                        opacity=0.9,
                        tooltip="Drone route",
                        dash_array="10, 10",
                        animate=True,
                    ).add_to(m)

                if route_mode in ["Helicopter", "Both"] and heli_route:
                    folium.PolyLine(
                        heli_route,
                        color="#8b5cf6",
                        weight=6,
                        opacity=0.8,
                        tooltip="Helicopter route",
                        dash_array="5, 5",
                        animate=True,
                    ).add_to(m)

                distance_drone = sum(
                    haversine(drone_route[i], drone_route[i + 1])
                    for i in range(len(drone_route) - 1)
                )
                distance_heli = sum(
                    haversine(heli_route[i], heli_route[i + 1])
                    for i in range(len(heli_route) - 1)
                )
                hazard_drone = sum(
                    1 for node in drone_path if disaster_zone(node, scenario_bias)
                )
                hazard_heli = sum(
                    1 for node in heli_path if disaster_zone(node, scenario_bias)
                )
                scores_drone = calculate_scores(distance_drone, hazard_drone, wind_mph)
                scores_heli = calculate_scores(distance_heli, hazard_heli, wind_mph)
                recommendation, reasons = recommend_vehicle(
                    scores_drone["drone_score"],
                    scores_heli["helicopter_score"],
                    wind_mph,
                    min(hazard_drone, hazard_heli),
                    min(distance_drone, distance_heli),
                )
                selected_path = (
                    heli_route if route_mode == "Helicopter" else drone_route
                )
                selected_nodes = heli_path if route_mode == "Helicopter" else drone_path
                selected_distance = (
                    distance_heli if route_mode == "Helicopter" else distance_drone
                )
                selected_hazard = hazard_heli if route_mode == "Helicopter" else hazard_drone
                time_min = max(selected_distance * 2, 5)
                risk_level = calculate_risk(selected_nodes, selected_distance)
                best_vehicle = recommendation if route_mode == "Both" else route_mode

                col1, col2 = st.columns([2.4, 1])
                with col1:
                    st.subheader("Route Map")
                    map_html = m._repr_html_()
                    html(map_html, height=620, scrolling=True)

                with col2:
                    st.subheader("Mission Summary")
                    st.markdown(f"**Scenario:** {scenario}")
                    st.markdown(f"**Weather:** {weather_desc} — {wind_mph:.1f} mph wind")
                    st.markdown(f"**Start:** {start_place}")
                    st.markdown(f"**Destination:** {end_place}")
                    st.metric(label="Distance", value=f"{selected_distance:.2f} km")
                    st.metric(label="Estimated Time", value=f"{time_min:.1f} min")
                    st.markdown(f"**Risk Level:** {risk_level}")
                    st.markdown(f"**Recommended Vehicle:** {recommendation}")
                    st.markdown("---")
                    st.markdown(
                        f"**Drone Score:** {scores_drone['drone_score']:.0f} | **Helicopter Score:** {scores_heli['helicopter_score']:.0f}"
                    )
                    st.markdown("**Recommendation rationale:**")
                    for reason in reasons:
                        st.markdown(f"- {reason}")
                    st.markdown("---")
                    st.markdown(
                        "**Simulation layer:** Red areas indicate hazard zones and the dashed ring marks restricted airspace."
                    )
                    st.markdown(
                        "<div class='animation-row'><div class='pulse-dot'></div><strong>Vehicle in transit:</strong> analyzing route efficiency.</div>",
                        unsafe_allow_html=True,
                    )
                    if st.button("Recalculate Route"):
                        st.rerun()
                    if st.button("Switch Vehicle Mode"):
                        modes = ["Drone", "Helicopter", "Both"]
                        current = st.session_state.get("route_mode", "Both")
                        next_mode = modes[(modes.index(current) + 1) % len(modes)]
                        st.session_state["route_mode"] = next_mode
                        st.rerun()

                st.markdown(
                    "---\n"
                    "**Legend:** Green = Hospital | Red = Emergency | Blue = Drone route | Purple = Helicopter route"
                )
                st.info(
                    "Simulated emergency conditions affecting air travel routes. Use vehicle mode toggles to compare options."
                )

                st.markdown(
                    "<div class='dashboard-card'>"
                    "<h3>Mission Complete Report</h3>"
                    "<ul>"
                    "<li>Route optimized through hazards</li>"
                    "<li>Hazard zones analyzed and avoided</li>"
                    "<li>Vehicle selection based on performance</li>"
                    "<li>ETA calculated using advanced algorithms</li>"
                    "</ul>"
                    "</div>",
                    unsafe_allow_html=True,
                )
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
