# SkyAid

> AI-powered disaster response and real-time situational awareness platform for emergency coordination, aerial intelligence, and predictive risk mapping.

---

## Overview

SkyAid centralizes fragmented disaster data into a single real-time command dashboard. It is designed for emergency responders, humanitarian teams, and crisis coordination systems to improve decision-making speed, accuracy, and safety during critical events.

---

## Key Features

### Real-Time Disaster Mapping
- Interactive live map dashboard
- Fire, flood, earthquake, and damage overlays
- GPS-based incident tracking

### Aerial Intelligence
- Drone / helicopter feed support
- Image-based damage detection
- Satellite layer compatibility

### AI Risk Prediction
- Disaster spread forecasting
- Risk zone detection
- Automated alert generation

### Emergency Resource Tracking
- Hospitals, shelters, evacuation routes
- Response unit positioning
- Route optimization for emergency vehicles

### Incident Reporting
- Fast structured reporting system
- Timestamped geolocation logging
- Field + civilian input support

---

## Tech Stack

**Frontend**
- Streamlit / React
- Leaflet / Folium / Mapbox

**Backend**
- Python

**Geospatial Processing**
- GeoPandas
- Shapely

**AI / ML**
- PyTorch or TensorFlow
- Computer vision models for damage detection

**Data**
- Pandas
- NumPy

**APIs (optional)**
- OpenStreetMap
- NASA Earth Data
- Weather APIs

---

## System Architecture
             +----------------------+
             |   Data Sources       |
             |----------------------|
             | Drones / Satellites  |
             | Sensors / Reports    |
             +----------+-----------+
                        |
                        v
             +----------------------+
             |  Ingestion Layer     |
             +----------+-----------+
                        |
                        v
             +----------------------+
             | Processing Layer     |
             | AI + Geospatial      |
             +----------+-----------+
                        |
                        v
             +----------------------+
             | Visualization Layer  |
             | Live Dashboard       |
             +----------+-----------+
                        |
                        v
             +----------------------+
             | Decision Support     |
             | Alerts + Routing     |
             +----------------------+

             
---

## Installation

```bash
git clone https://github.com/your-username/skyaid.git
cd skyaid

pip install -r requirements.txt
streamlit run app.py
