"""
╔══════════════════════════════════════════════════════════════════╗
║          AgriSmart AI Pro — Precision Farming Intelligence       ║
║          College Project · Built with Streamlit + Gemini AI      ║
║                                                                  ║
║  SETUP:                                                          ║
║  1. pip install streamlit google-generativeai plotly             ║
║         pandas pillow requests                                   ║
║  2. Create .streamlit/secrets.toml:                              ║
║         GEMINI_API_KEY    = "your-gemini-key"                    ║
║         OPENWEATHER_KEY   = "your-openweather-key"  (free)       ║
║  3. streamlit run agrismart_final.py                             ║
╚══════════════════════════════════════════════════════════════════╝
"""
 
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import google.generativeai as genai
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import hashlib, json, requests
from datetime import datetime
from PIL import Image
 
# ─────────────────────────────────────────────────────────────────
# 0 · PAGE CONFIG  (must be first Streamlit call)
# ─────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Smart Agriculture Farming",
    page_icon="🌾",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ─────────────────────────────────────────────────────────────────
# 1 · GLOBAL CSS  — Earthy-Luxe dark theme
# ─────────────────────────────────────────────────────────────────
st.markdown(r"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;600;700&family=Outfit:wght@300;400;500;600&family=JetBrains+Mono:wght@400&display=swap');
 
/* ── Tokens ── */
:root {
    --bg:       #080f09;
    --surf:     #0e1a10;
    --card:     #121e14;
    --border:   #1c3320;
    --green:    #52e07c;
    --green2:   #2ecc5a;
    --gold:     #c9953a;
    --amber:    #e8a020;
    --red:      #e05252;
    --blue:     #52abe0;
    --sky:      #7ecfea;
    --txt:      #ddeedd;
    --muted:    #5a8060;
    --hi:       #ffffff;
}
 
/* ── Base ── */
html, body, .stApp          { background: var(--bg) !important; }
.stApp                      { font-family: 'Outfit', sans-serif; color: var(--txt); }

/* Kill ALL top padding/margin that creates the gap above the hero */
.block-container,
[data-testid="stMainBlockContainer"] {
    padding-top: 0 !important;
    margin-top:  0 !important;
    max-width: 1440px;
}

/* ── Header: transparent, no border — toggle renders natively inside it ── */
header[data-testid="stHeader"] {
    background:    transparent !important;
    border-bottom: none !important;
}
/* Hide only explicitly-labelled toolbar chrome */
[data-testid="stToolbar"],
[data-testid="stDecoration"],
[data-testid="stStatusWidget"],
#MainMenu, footer { display: none !important; }

/* Hero breathing room */
.hero { margin-top: 0.5rem; }

/* Collapse the GPS iframe gap */
iframe[height="0"] { display: block !important; line-height: 0; margin: 0 !important; padding: 0 !important; }
.stApp::before {
    content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 1;
    background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='300' height='300'%3E%3Cfilter id='g'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.75' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='300' height='300' filter='url(%23g)' opacity='0.04'/%3E%3C/svg%3E");
    opacity: .55;
}

/* Ambient glow blobs — z-index BELOW the toggle */
.stApp::after {
    content: ''; position: fixed; inset: 0; pointer-events: none; z-index: 1;
    background:
        radial-gradient(ellipse 55% 35% at 10% 20%, #1a4d2222, transparent),
        radial-gradient(ellipse 40% 50% at 90% 80%, #0d2e1422, transparent),
        radial-gradient(ellipse 30% 30% at 50% 50%, #0a1e0c11, transparent);
}
 
/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #090f0a 0%, #050c06 100%) !important;
    border-right: 1px solid var(--border) !important;
}
section[data-testid="stSidebar"] * { color: var(--txt) !important; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stNumberInput > div > div > input {
    background: #0e1a10 !important;
    border: 1px solid var(--border) !important;
    color: var(--txt) !important;
}
 
/* ── Buttons ── */
.stButton > button {
    background: linear-gradient(135deg, #1a6b35 0%, #0f4a22 100%) !important;
    color: #ffffff !important; border: 1px solid #2a8845 !important;
    border-radius: 10px !important; font-family: 'Outfit', sans-serif !important;
    font-weight: 600 !important; letter-spacing: .03em !important;
    padding: .55rem 1.5rem !important; transition: all .2s !important;
    box-shadow: 0 2px 16px #1a6b3533 !important;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #22883f 0%, #1a6b35 100%) !important;
    box-shadow: 0 4px 28px #22883f55 !important; transform: translateY(-2px) !important;
}
 
/* ── Inputs / sliders ── */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stTextArea > div > textarea {
    background: var(--surf) !important; border: 1px solid var(--border) !important;
    border-radius: 10px !important; color: var(--txt) !important;
    font-family: 'Outfit', sans-serif !important;
}
.stSelectbox > div > div { background: var(--surf) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; color: var(--txt) !important; }
div[data-baseweb="select"] * { background: var(--surf) !important; color: var(--txt) !important; }
.stSlider [data-baseweb="slider"] [role="slider"] { background: var(--green) !important; }
.stSlider > div > div > div { color: var(--txt) !important; }
.stRadio > div { color: var(--txt) !important; }
 
/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {
    background: var(--surf) !important; border: 1px solid var(--border) !important;
    border-radius: 14px !important; padding: 5px !important; gap: 4px;
}
.stTabs [data-baseweb="tab"] {
    background: transparent !important; color: var(--muted) !important;
    border-radius: 10px !important; font-family: 'Outfit', sans-serif !important;
    font-size: .85rem !important; padding: .45rem 1rem !important;
}
.stTabs [aria-selected="true"] {
    background: var(--card) !important; color: var(--green) !important;
    border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab-panel"] { background: transparent !important; padding-top: 1.2rem !important; }
 
/* ── Metrics ── */
div[data-testid="metric-container"] {
    background: var(--card); border: 1px solid var(--border); border-radius: 14px;
    padding: .9rem 1.1rem; box-shadow: 0 4px 20px #00000040;
}
div[data-testid="metric-container"] label { color: var(--muted) !important; font-size: .72rem !important; text-transform: uppercase; letter-spacing: .08em; }
div[data-testid="metric-container"] div[data-testid="stMetricValue"] { color: var(--green) !important; font-size: 1.55rem !important; font-family: 'Cormorant Garamond', serif !important; font-weight: 700 !important; }
div[data-testid="stMetricDelta"] { font-size: .72rem !important; }
 
/* ── Alerts ── */
.stAlert { border-radius: 12px !important; border: none !important; }
 
/* ── Expander ── */
.streamlit-expanderHeader { background: var(--surf) !important; border: 1px solid var(--border) !important; border-radius: 10px !important; }
.streamlit-expanderContent { background: var(--card) !important; border: 1px solid var(--border) !important; border-bottom-left-radius: 10px !important; border-bottom-right-radius: 10px !important; }
 
/* ── Dataframe ── */
.stDataFrame { border: 1px solid var(--border) !important; border-radius: 12px !important; overflow: hidden; }
 
/* ── Progress ── */
div[data-testid="stProgressBar"] > div { background: var(--green) !important; }
 
/* ── Custom components ── */
.hero {
    background: linear-gradient(135deg, #0a1f0c 0%, #071408 40%, #0e1f10 100%);
    border: 1px solid var(--border); border-radius: 22px; padding: 2rem 2.5rem;
    margin-bottom: 1.8rem; position: relative; overflow: hidden;
}
.hero::before {
    content: ''; position: absolute; right: -40px; top: -40px; width: 300px; height: 300px;
    background: radial-gradient(circle, #52e07c0a, transparent 70%);
    border-radius: 50%;
}
.hero-emoji { position: absolute; right: 2.5rem; top: 50%; transform: translateY(-50%); font-size: 6rem; opacity: .08; pointer-events: none; }
 
.sec-head {
    font-family: 'Cormorant Garamond', serif; font-size: 1.35rem; font-weight: 600;
    color: var(--txt); border-left: 3px solid var(--green); padding-left: .75rem; margin-bottom: 1rem;
}
.glass {
    background: linear-gradient(135deg, #12201466, #0a140b66);
    border: 1px solid var(--border); border-radius: 16px; padding: 1.4rem;
    backdrop-filter: blur(8px);
}
.result-box {
    background: linear-gradient(135deg, #061a09ee, #0d2e12ee);
    border: 1px solid #2a8845aa; border-radius: 18px; padding: 2rem;
    margin-top: 1.2rem; box-shadow: 0 0 60px #52e07c0d;
}
.pill {
    display: inline-block; background: var(--surf); border: 1px solid var(--border);
    border-radius: 20px; padding: .22rem .75rem; font-size: .75rem; color: var(--muted); margin: 2px;
}
.green-pill { background: #1a4d2255; border-color: #2a8845; color: var(--green); }
.amber-pill { background: #3d280055; border-color: #c9953a; color: var(--gold); }
.red-pill   { background: #3d000055; border-color: #a03030; color: var(--red); }
.weather-card {
    background: linear-gradient(135deg, #0a1e2a, #071218);
    border: 1px solid #1c3344; border-radius: 16px; padding: 1.2rem 1.5rem;
}
.login-wrap { max-width: 440px; margin: 2.5rem auto; }
.login-card {
    background: var(--card); border: 1px solid var(--border); border-radius: 22px;
    padding: 2.5rem; box-shadow: 0 24px 80px #00000080;
}
 
/* Scrollbar */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
 
/* File uploader */
[data-testid="stFileUploader"] { background: var(--surf) !important; border: 1px dashed var(--border) !important; border-radius: 12px !important; }
</style>
""", unsafe_allow_html=True)
 
# ─────────────────────────────────────────────────────────────────
# 2 · SESSION STATE DEFAULTS
# ─────────────────────────────────────────────────────────────────
def make_hash(pw): return hashlib.sha256(pw.encode()).hexdigest()
def check_hash(pw, h): return make_hash(pw) == h
 
_defaults = {
    "logged_in": False, "user": None, "history": [],
    "disease_log": [],
    "last_advisory": None, "advisory_inputs": {},
    "sb_disease_result": "", "sb_last_img_name": "",
    "user_db": pd.DataFrame([
        {"username": "jafar",  "password": make_hash("1234"),     "role": "farmer",  "region": "Singarayakonda, AP"},
        {"username": "admin",  "password": make_hash("admin123"), "role": "admin",   "region": "All India"},
        {"username": "demo",   "password": make_hash("demo123"),  "role": "farmer",  "region": "Guntur, AP"},
    ]),
}
for k, v in _defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v
 
# ─────────────────────────────────────────────────────────────────
# 3 · KNOWLEDGE BASE
# ─────────────────────────────────────────────────────────────────
CROPS = {
    "Rice":       {"N":(80,120),"P":(40,60),"K":(40,60),"pH":(5.5,7.0),"T":(20,35),"R":(150,300)},
    "Wheat":      {"N":(60,120),"P":(30,60),"K":(30,60),"pH":(6.0,7.5),"T":(12,25),"R":(50,100)},
    "Maize":      {"N":(80,120),"P":(40,60),"K":(40,60),"pH":(5.5,7.5),"T":(18,35),"R":(50,100)},
    "Cotton":     {"N":(60,100),"P":(30,50),"K":(30,60),"pH":(5.8,7.5),"T":(21,35),"R":(50,150)},
    "Groundnut":  {"N":(15,25), "P":(40,60),"K":(40,60),"pH":(6.0,7.0),"T":(25,35),"R":(50,150)},
    "Chilli":     {"N":(80,120),"P":(40,60),"K":(60,80),"pH":(6.0,7.0),"T":(20,30),"R":(60,120)},
    "Tomato":     {"N":(100,150),"P":(60,80),"K":(80,100),"pH":(6.0,7.0),"T":(18,30),"R":(40,80)},
    "Sugarcane":  {"N":(100,150),"P":(40,60),"K":(80,120),"pH":(6.0,7.5),"T":(20,38),"R":(100,200)},
    "Soybean":    {"N":(20,30), "P":(40,60),"K":(40,60),"pH":(6.0,7.0),"T":(20,30),"R":(60,150)},
    "Turmeric":   {"N":(60,80), "P":(40,60),"K":(80,100),"pH":(5.5,7.0),"T":(20,30),"R":(100,250)},
    "Banana":     {"N":(100,140),"P":(40,60),"K":(100,140),"pH":(5.5,7.0),"T":(20,35),"R":(100,200)},
    "Papaya":     {"N":(80,120),"P":(40,60),"K":(60,100),"pH":(6.0,7.0),"T":(22,35),"R":(80,150)},
}
 
MARKET = {
    "Rice":2183,"Wheat":2275,"Maize":1870,"Cotton":6620,"Groundnut":6377,
    "Chilli":8000,"Tomato":1500,"Sugarcane":315,"Soybean":4600,"Turmeric":13000,
    "Banana":1800,"Papaya":1200,
}
 
SEASON_MAP = {
    "Kharif (Jun–Oct)": ["Rice","Cotton","Maize","Soybean","Groundnut","Turmeric","Banana"],
    "Rabi (Nov–Mar)":   ["Wheat","Tomato","Chilli","Sugarcane","Papaya"],
    "Zaid (Mar–May)":   ["Maize","Tomato","Groundnut","Papaya","Banana"],
}
 
DISEASE_QUICK = {
    "Yellow leaves":          "Likely N deficiency or Iron chlorosis → foliar spray 2% urea or 0.5% FeSO₄",
    "Brown leaf spots":       "Fungal (Alternaria/Cercospora) → Mancozeb 2 g/L or Copper Oxychloride 3 g/L",
    "White powdery coating":  "Powdery mildew → Wettable Sulphur 80WP 2 g/L or Hexaconazole 1 ml/L",
    "Wilting / root rot":     "Pythium/Phytophthora → drench Metalaxyl-M 2 g/L; improve drainage",
    "Holes / eaten leaves":   "Insect pest → identify first; Chlorpyrifos 2 ml/L or Neem oil 5 ml/L",
    "Orange rust pustules":   "Rust disease → Propiconazole 1 ml/L or Tebuconazole 1 ml/L",
    "Curled / distorted":     "Viral (Thrips vector) → remove infected plants; Imidacloprid 0.5 ml/L",
    "Black sooty mould":      "Sooty mould on honeydew → control whitefly; spray starch solution + Neem",
}
 
FERT_GUIDE = {
    "Urea (46% N)":           "Split: 1/3 basal + 1/3 tillering + 1/3 panicle. Use neem-coated in flooded fields.",
    "DAP (18N-46P)":          "Excellent basal dose. Apply before sowing/transplanting. 50 kg/acre typical.",
    "MOP (60% K)":            "Apply in 2 splits on sandy soils. Avoid excess on saline soils.",
    "SSP (16P-11S)":          "Good for sulphur-deficient Andhra soils. Apply at sowing.",
    "Vermicompost":           "2-3 t/ha improves structure, water retention, and microbial diversity.",
    "Bio-NPK Consortium":     "Rhizobium + PSB + KMB — reduces chemical inputs by ~25%. Apply at transplanting.",
    "Zinc Sulphate":          "5 kg/acre if Zn-deficient (whitish middle leaves). Critical for AP red soils.",
    "Neem Cake":              "200 kg/ha — controls nematodes, adds slow-release N, repels soil insects.",
}
 
REGIONS = [
    "Singarayakonda, AP", "Guntur, AP", "Kurnool, AP", "Vijayawada, AP",
    "Warangal, Telangana", "Hyderabad, Telangana", "Nashik, Maharashtra",
    "Ludhiana, Punjab", "Mysuru, Karnataka", "Coimbatore, Tamil Nadu",
    "Chennai, Tamil Nadu", "Bengaluru, Karnataka", "Pune, Maharashtra",
    "All India", "Other",
]
 
# ─────────────────────────────────────────────────────────────────
# 4 · AI HELPERS
# ─────────────────────────────────────────────────────────────────
@st.cache_resource
def get_model():
    # ── 1. Read API key safely ────────────────────────────────────
    try:
        key = st.secrets["GEMINI_API_KEY"]
    except Exception:
        key = ""
    key = (key or "").strip()

    if not key or "your-gemini" in key.lower():
        return None, ""          # (model, error_msg)

    # ── 2. Configure SDK ──────────────────────────────────────────
    try:
        genai.configure(api_key=key)
    except Exception as e:
        return None, f"⚠️ Gemini configure failed: {e}"

    # ── 3. Try stable free-tier models in order ───────────────────
    PREFERRED = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-1.5-flash",
        "gemini-1.5-flash-latest",
    ]
    for model_name in PREFERRED:
        try:
            return genai.GenerativeModel(model_name), ""
        except Exception:
            continue

    # ── 4. Auto-discover from what the key actually has access to ─
    try:
        available = [
            m.name.replace("models/", "")
            for m in genai.list_models()
            if "generateContent" in m.supported_generation_methods
        ]
        for m_name in available:
            if any(x in m_name for x in ["flash", "lite", "pro"]) and "preview" not in m_name:
                try:
                    return genai.GenerativeModel(m_name), ""
                except Exception:
                    continue
        names = "\n".join(f"• `{n}`" for n in available[:10])
        return None, f"⚠️ No preferred model worked.\n\nYour key can access:\n{names}"
    except Exception as list_err:
        return None, f"⚠️ API key rejected — {list_err}"
 
 
def score_crops(n, p, k, ph, temp, rain):
    results = []
    for crop, r in CROPS.items():
        s = 0
        for val, key, w in [(n,"N",2),(p,"P",2),(k,"K",2),(temp,"T",2),(rain,"R",1)]:
            if r[key][0] <= val <= r[key][1]: s += w
            elif abs(val - sum(r[key])/2) < (r[key][1]-r[key][0])*0.4: s += w//2
        if r["pH"][0] <= ph <= r["pH"][1]: s += 3
        elif abs(ph - sum(r["pH"])/2) < 0.5: s += 1
        results.append((crop, s, 0))   # pct recalculated at return
    results.sort(key=lambda x: x[1], reverse=True)
    # Max possible score: N(2)+P(2)+K(2)+T(2)+R(1)+pH(3) = 12
    return [(crop, s, min(round(s / 12 * 100), 100)) for crop, s, _ in results[:6]]
 
 
def advisory_prompt(n, p, k, ph, temp, rain, hum, soil, season, lang, weather_ctx=""):
    top = score_crops(n, p, k, ph, temp, rain)
    top_names = ", ".join(f"{c}({pct}%)" for c,_,pct in top[:3])
    n_status = "DEFICIENT (<60)" if n<60 else "EXCESS (>120)" if n>120 else "OPTIMAL"
    p_status = "DEFICIENT (<30)" if p<30 else "EXCESS (>80)" if p>80 else "OPTIMAL"
    k_status = "DEFICIENT (<30)" if k<30 else "EXCESS (>120)" if k>120 else "OPTIMAL"
    ph_status = "ACIDIC — needs lime" if ph<5.5 else "ALKALINE — needs sulphur" if ph>7.8 else "OPTIMAL"
 
    lang_note = "Write entirely in Telugu script (తెలుగు) except numbers/chemical names." if lang == "తెలుగు" else ""
 
    return f"""You are Dr. Arjun Reddy, a Senior Agronomist with 28 years specializing in Andhra Pradesh and Telangana agriculture. You are precise, data-driven, and care deeply about farmer profitability.
 
FARM DATA:
- NPK: N={n} kg/ha ({n_status}), P={p} kg/ha ({p_status}), K={k} kg/ha ({k_status})
- Soil pH: {ph} ({ph_status}) | Temp: {temp}°C | Rainfall: {rain}mm | Humidity: {hum}%
- Soil type: {soil} | Season: {season}
{f"- Live weather: {weather_ctx}" if weather_ctx else ""}
 
REFERENCE DATA (use as ground truth — do not contradict):
Rule-based crop match scores: {top_names}
AP Market Prices (₹/quintal): {json.dumps({crop_name:price for crop_name,price in MARKET.items() if crop_name in [c for c,_,_ in top[:5]]})}
Fertilizer guide: {json.dumps(FERT_GUIDE)}
 
TASK — Produce a structured advisory report with EXACTLY these sections:
 
## 🧪 Soil Health Report
Table showing each parameter (N, P, K, pH, Temp, Rainfall), its value, status (✅ Optimal / ⚠️ Adjust / ❌ Critical), and one-line action.
 
## 🏆 Top 3 Recommended Crops
For each crop:
**[Crop Name]** — Suitability: X%
- Why it matches this soil & climate (2 sentences, specific)
- Expected yield: X–Y quintals/acre
- Gross income: ₹X (yield × market price)
- Net profit estimate: ₹X (after ~₹9,000/acre input cost)
 
## 💊 Precision Fertilizer Schedule
Markdown table: | Fertilizer | Quantity/acre | Timing | Method |
Include 1 organic alternative row.
 
## ⚠️ Top 3 Risks This Season
For each: Risk name, Why it applies to THIS farm data, Prevention (specific product + dose).
 
## 📅 4-Week Kick-off Action Plan
| Week | Key Tasks | Materials Needed |
 
## 💡 3 Precision Farming Upgrades
Practical, low-cost tech suggestions (e.g., soil moisture sensors, drip kits) with estimated ROI.
 
{lang_note}
Be specific. Use this farmer's actual numbers. No generic advice."""
 
 
def disease_prompt(crop):
    return f"""You are Dr. Priya Sharma, a Plant Pathologist with expertise in Indian crop diseases.
Analyze this {crop} plant image and provide:
 
## 🔬 Diagnosis
- Disease/condition name (confidence %)
- Visual symptoms detected in the image
 
## 🧬 Cause & Spread
- Pathogen or environmental trigger
- How it spreads (weather, contact, soil)
 
## 💊 Treatment Plan
| Option | Product | Dose | Frequency |
Include: chemical treatment, organic alternative, cost estimate (₹/acre).
 
## ⏱️ Urgency & Yield Impact
- Severity: Minor / Moderate / Severe
- Estimated yield loss if untreated: X%
- Act within: X days
 
## 🛡️ Prevention Next Season
3 specific actions to prevent recurrence.
 
Be direct. Farmer needs to act today."""
 
# ─────────────────────────────────────────────────────────────────
# 5 · GEOLOCATION + WEATHER
# ─────────────────────────────────────────────────────────────────
# How it works — zero manual input required:
#
#   Layer 1 · Browser GPS   — JS asks the device for coordinates.
#                             Stored in ?geo=lat,lon query param.
#                             Page reloads once; Python reads the param.
#                             Guard prevents reload loops.
#   Layer 2 · IP geolocation — ip-api.com free lookup, no API key.
#                              Works silently even if GPS is denied.
#   Layer 3 · Dropdown      — sidebar Location selector as last resort.
#
# "📍 Reset GPS" button clears the query param → JS re-fires on next load.
# ─────────────────────────────────────────────────────────────────

def inject_geolocation_js():
    """
    Single components.html call that:
      1. Injects GPS geolocation (window.parent navigation)
      2. Creates a custom floating sidebar toggle button injected
         directly into window.parent.document — completely bypasses
         Streamlit's header CSS so it's always visible and always works.
    """
    components.html(
        """
<script>
(function () {
    // ── 1. GPS ───────────────────────────────────────────────────
    var params = new URLSearchParams(window.parent.location.search);
    if (!params.has('geo')) {
        function pushGeo(value) {
            var p = new URLSearchParams(window.parent.location.search);
            p.set('geo', value);
            window.parent.location.search = p.toString();
        }
        if (!navigator.geolocation) { pushGeo('denied'); }
        else {
            navigator.geolocation.getCurrentPosition(
                function(pos) {
                    pushGeo(pos.coords.latitude.toFixed(5) + ',' + pos.coords.longitude.toFixed(5));
                },
                function() { pushGeo('denied'); },
                { enableHighAccuracy: true, timeout: 10000, maximumAge: 300000 }
            );
        }
    }

    // ── 2. Custom sidebar toggle ─────────────────────────────────
    // Inject a floating button into the parent Streamlit document.
    // It detects sidebar state and clicks the native Streamlit button,
    // so Streamlit's own state machine stays in sync.
    var doc = window.parent.document;

    // Avoid duplicate injection
    if (doc.getElementById('agri-sidebar-toggle')) return;

    var btn = doc.createElement('button');
    btn.id = 'agri-sidebar-toggle';
    btn.innerHTML = '&#9776;';
    btn.title = 'Toggle sidebar';
    btn.style.cssText = [
        'position:fixed',
        'top:50%',
        'left:0',
        'transform:translateY(-50%)',
        'z-index:999999',
        'width:28px',
        'height:52px',
        'background:#121e14',
        'border:1px solid #52e07c',
        'border-left:none',
        'border-radius:0 10px 10px 0',
        'color:#52e07c',
        'font-size:16px',
        'cursor:pointer',
        'padding:0',
        'line-height:1',
        'box-shadow:2px 0 12px rgba(82,224,124,0.15)',
        'transition:background 0.2s',
    ].join(';');

    btn.onmouseenter = function() { btn.style.background = '#1a3d1e'; };
    btn.onmouseleave = function() { btn.style.background = '#121e14'; };

    btn.onclick = function() {
        // Try to click Streamlit's native collapse/expand buttons
        var collapseBtn = doc.querySelector('[data-testid="stSidebarCollapseButton"] button');
        var expandBtn   = doc.querySelector('[data-testid="collapsedControl"] button');
        if (collapseBtn) { collapseBtn.click(); }
        else if (expandBtn) { expandBtn.click(); }
    };

    doc.body.appendChild(btn);
})();
</script>
        """,
        height=0,
        scrolling=False,
    )


def get_device_coords():
    """Return (lat, lon) from ?geo= query param, or (None, None)."""
    try:
        geo = st.query_params.get("geo", "")
    except Exception:
        return None, None
    if not geo or geo == "denied":
        return None, None
    try:
        lat_s, lon_s = geo.split(",")
        return float(lat_s), float(lon_s)
    except Exception:
        return None, None


@st.cache_data(ttl=600)
def _ip_geolocation():
    """Free IP-based geolocation via ip-api.com — no key required."""
    try:
        r = requests.get(
            "https://ip-api.com/json/?fields=status,lat,lon,city",
            timeout=5,
        )
        if r.status_code == 200:
            d = r.json()
            if d.get("status") == "success":
                return float(d["lat"]), float(d["lon"]), d.get("city", "")
    except Exception:
        pass
    return None, None, ""


@st.cache_data(ttl=1800)
def _owm_by_coords(lat: float, lon: float):
    """OpenWeatherMap fetch by coordinates (most accurate)."""
    try:
        key = st.secrets["OPENWEATHER_KEY"] if "OPENWEATHER_KEY" in st.secrets else ""
        if not key or "your-openweather" in key.lower():
            return None
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?lat={lat}&lon={lon}&appid={key}&units=metric",
            timeout=6,
        )
        if r.status_code == 200:
            d = r.json()
            return {
                "temp":     round(d["main"]["temp"]),
                "feels":    round(d["main"]["feels_like"]),
                "humidity": d["main"]["humidity"],
                "desc":     d["weather"][0]["description"].title(),
                "icon":     d["weather"][0]["main"],
                "wind":     round(d["wind"]["speed"], 1),
                "rain":     d.get("rain", {}).get("1h", 0),
                "city":     d["name"],
            }
    except Exception:
        pass
    return None


@st.cache_data(ttl=1800)
def _owm_by_city(city: str):
    """OpenWeatherMap fetch by city name — India assumed."""
    try:
        key = st.secrets["OPENWEATHER_KEY"] if "OPENWEATHER_KEY" in st.secrets else ""
        if not key or "your-openweather" in key.lower():
            return None
        r = requests.get(
            f"https://api.openweathermap.org/data/2.5/weather"
            f"?q={city},IN&appid={key}&units=metric",
            timeout=6,
        )
        if r.status_code == 200:
            d = r.json()
            return {
                "temp":     round(d["main"]["temp"]),
                "feels":    round(d["main"]["feels_like"]),
                "humidity": d["main"]["humidity"],
                "desc":     d["weather"][0]["description"].title(),
                "icon":     d["weather"][0]["main"],
                "wind":     round(d["wind"]["speed"], 1),
                "rain":     d.get("rain", {}).get("1h", 0),
                "city":     d["name"],
            }
    except Exception:
        pass
    return None


def get_weather(fallback_city: str = ""):
    """
    Resolve weather through 3 layers — returns dict with 'source' key.
      source = 'gps'  → real device GPS
      source = 'ip'   → IP geolocation
      source = 'city' → sidebar dropdown
    """
    # Layer 1 — device GPS (coordinates from ?geo= query param)
    lat, lon = get_device_coords()
    if lat is not None:
        wx = _owm_by_coords(lat, lon)
        if wx:
            wx["source"] = "gps"
            return wx

    # Layer 2 — IP geolocation (silent, automatic)
    ip_lat, ip_lon, _ = _ip_geolocation()
    if ip_lat is not None:
        wx = _owm_by_coords(ip_lat, ip_lon)
        if wx:
            wx["source"] = "ip"
            return wx

    # Layer 3 — sidebar location dropdown
    if fallback_city:
        wx = _owm_by_city(fallback_city)
        if wx:
            wx["source"] = "city"
            return wx

    return None


def weather_icon(icon_key):
    return {
        "Clear": "☀️", "Clouds": "⛅", "Rain": "🌧️", "Drizzle": "🌦️",
        "Thunderstorm": "⛈️", "Snow": "❄️", "Mist": "🌫️",
        "Haze": "🌫️", "Smoke": "🌫️",
    }.get(icon_key, "🌡️")


def weather_source_badge(source: str):
    """Tiny coloured pill showing which layer resolved the weather."""
    cfg = {
        "gps":  ("📍", "GPS",     "#52e07c", "#061a09"),
        "ip":   ("🌐", "Network", "#52abe0", "#06121a"),
        "city": ("🏙️", "Region",  "#e8a020", "#1a0e00"),
    }
    ico, label, fg, bg = cfg.get(source, ("❓", "Unknown", "#888", "#111"))
    return (f"<span style='font-size:.68rem;background:{bg};color:{fg};"
            f"border:1px solid {fg}55;border-radius:20px;"
            f"padding:.15rem .55rem'>{ico} {label}</span>")

# 6 · PLOTLY CHARTS
# ─────────────────────────────────────────────────────────────────
LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(18,30,20,.6)",
              font=dict(color="#ddeedd", family="Outfit"), margin=dict(l=30,r=20,t=45,b=30))
 
def npk_radar(n, p, k):
    fig = go.Figure(go.Scatterpolar(
        r=[n, p, k, n], theta=["Nitrogen", "Phosphorus", "Potassium", "Nitrogen"],
        fill="toself", fillcolor="rgba(82,224,124,.15)",
        line=dict(color="#52e07c", width=2.5), marker=dict(size=9, color="#52e07c"),
    ))
    fig.update_layout(polar=dict(
        bgcolor="rgba(18,30,20,.5)",
        radialaxis=dict(range=[0,150], gridcolor="#1c3320", color="#5a8060", tickfont=dict(size=9)),
        angularaxis=dict(gridcolor="#1c3320", tickfont=dict(size=10)),
    ), **LAYOUT, title=dict(text="NPK Balance", font=dict(size=13)), height=280)
    return fig
 
def ph_gauge(ph):
    clr = "#52e07c" if 6<=ph<=7.5 else "#e8a020" if 5<=ph<6 or 7.5<ph<=8.5 else "#e05252"
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=ph,
        title={"text":"Soil pH", "font":{"color":"#ddeedd","size":13}},
        number={"font":{"color":clr,"size":30,"family":"Cormorant Garamond"}},
        gauge={
            "axis":{"range":[4,9],"tickcolor":"#5a8060","tickfont":{"size":9}},
            "bar":{"color":clr,"thickness":.28},
            "bgcolor":"#0e1a10","bordercolor":"#1c3320","borderwidth":1,
            "steps":[{"range":[4,5.5],"color":"rgba(61,0,0,0.2)"},
                     {"range":[5.5,7.5],"color":"rgba(26,77,34,0.2)"},
                     {"range":[7.5,9], "color":"rgba(61,40,0,0.2)"}],
        }
    ))
    fig.update_layout(**LAYOUT, height=240)
    return fig
 
def profit_waterfall(area, yield_q, price, seed, fert, labor, other):
    gross   = yield_q * area * price
    costs   = [(seed, "Seed"), (fert, "Fertilizer"), (labor, "Labour"), (other, "Other")]
    xs      = ["Gross Income"] + [c[1] for c in costs] + ["Net Profit"]
    ys      = [gross] + [-c[0]*area for c in costs] + [0]
    measure = ["absolute"] + ["relative"]*len(costs) + ["total"]
    fig = go.Figure(go.Waterfall(
        x=xs, y=ys, measure=measure,
        connector={"line":{"color":"#1c3320"}},
        increasing={"marker":{"color":"#52e07c"}},
        decreasing={"marker":{"color":"#e05252"}},
        totals={"marker":{"color":"#e8a020"}},
    ))
    fig.update_layout(**LAYOUT, title="Cost–Profit Waterfall (₹)", height=310)
    return fig
 
def crop_comparison_bar(scored):
    crops = [c for c,_,_ in scored[:6]]
    pcts  = [p for _,_,p in scored[:6]]
    clrs  = ["#52e07c" if p>=70 else "#e8a020" if p>=50 else "#e05252" for p in pcts]
    fig = go.Figure(go.Bar(
        x=pcts, y=crops, orientation="h",
        marker_color=clrs, marker_line_width=0, text=[f"{p}%" for p in pcts],
        textposition="outside", textfont=dict(color="#ddeedd", size=11),
    ))
    fig.update_layout(**LAYOUT, title="Crop Suitability Scores", height=300,
                      xaxis=dict(range=[0,115], gridcolor="#1c3320", showgrid=True),
                      yaxis=dict(gridcolor="#1c3320"))
    return fig
 
def trend_chart():
    months = pd.date_range("2024-01-01", periods=12, freq="ME")
    np.random.seed(42)
    df = pd.DataFrame({
        "Month": months,
        "Rice (q/ac)":     np.random.normal(17, 1.5, 12).clip(12, 22),
        "Chilli (q/ac)":   np.random.normal(8, 1,   12).clip(5, 12),
        "Rainfall (mm)":   np.random.normal(85, 35,  12).clip(0, 220),
    })
    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                        subplot_titles=("Yield Trends", "Monthly Rainfall"),
                        vertical_spacing=.12)
    for col, clr in [("Rice (q/ac)","#52e07c"),("Chilli (q/ac)","#e8a020")]:
        fig.add_trace(go.Scatter(x=df["Month"], y=df[col], name=col,
                                 mode="lines+markers", line=dict(color=clr, width=2.2),
                                 marker=dict(size=5)), row=1, col=1)
    fig.add_trace(go.Bar(x=df["Month"], y=df["Rainfall (mm)"], name="Rainfall",
                         marker_color="rgba(82,171,224,0.33)"), row=2, col=1)
    fig.update_layout(**LAYOUT, height=420, legend=dict(bgcolor="rgba(0,0,0,0)"))
    fig.update_xaxes(gridcolor="#1c3320"); fig.update_yaxes(gridcolor="#1c3320")
    return fig
 
def season_dot_chart():
    rows = [{"Season":s,"Crop":c} for s,cs in SEASON_MAP.items() for c in cs]
    df   = pd.DataFrame(rows)
    cmap = {"Kharif (Jun–Oct)":"#52e07c","Rabi (Nov–Mar)":"#52abe0","Zaid (Mar–May)":"#e8a020"}
    fig  = px.scatter(df, x="Season", y="Crop", color="Season", color_discrete_map=cmap)
    fig.update_traces(marker=dict(size=20, symbol="square", opacity=.85))
    fig.update_layout(**LAYOUT, title="AP Seasonal Crop Calendar", height=420,
                      showlegend=False, xaxis=dict(gridcolor="#1c3320"),
                      yaxis=dict(gridcolor="#1c3320"))
    return fig
 
# ─────────────────────────────────────────────────────────────────
# 7 · AUTH PAGE
# ─────────────────────────────────────────────────────────────────
def auth_page():
    st.markdown("""
    <div style='text-align:center;padding:2.5rem 0 1.5rem;'>
        <div style='font-size:4rem;margin-bottom:.5rem'>🌾</div>
        <div style='font-family:Cormorant Garamond,serif;font-size:2.8rem;font-weight:700;
            background:linear-gradient(135deg,#52e07c,#c9953a);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.1'>
            AgriSmart AI Pro
        </div>
        <div style='color:#5a8060;font-size:.95rem;margin-top:.6rem;letter-spacing:.04em'>
            Precision Farming Intelligence · Andhra Pradesh & Telangana
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    _, col, _ = st.columns([1, 1.8, 1])
    with col:
        choice = st.radio("", ["🔑 Login", "✨ Create Account"], horizontal=True, label_visibility="collapsed")
 
        if "Login" in choice:
            with st.form("lf"):
                u = st.text_input("Username", placeholder="Enter username")
                p = st.text_input("Password", type="password", placeholder="Enter password")
                if st.form_submit_button("Login →", use_container_width=True):
                    rec = st.session_state.user_db[st.session_state.user_db.username == u]
                    if not rec.empty and check_hash(p, rec.iloc[0].password):
                        st.session_state.logged_in = True
                        st.session_state.user = u
                        st.rerun()
                    else:
                        st.error("Invalid username or password.")
 
        else:  # signup
            with st.form("sf"):
                nu = st.text_input("Choose Username", placeholder="e.g. farmer_ravi")
                np_ = st.text_input("Choose Password (min 6 chars)", type="password")
                nr = st.selectbox("Your Region", REGIONS)
                if st.form_submit_button("Create Account →", use_container_width=True):
                    if not nu or len(np_) < 6:
                        st.warning("Username required and password ≥ 6 characters.")
                    elif nu in st.session_state.user_db.username.values:
                        st.warning("Username already taken.")
                    else:
                        row = pd.DataFrame([{"username":nu,"password":make_hash(np_),"role":"farmer","region":nr}])
                        st.session_state.user_db = pd.concat([st.session_state.user_db, row], ignore_index=True)
                        st.success("Account created! Please login.")
 
        st.markdown("""
        <div style='text-align:center;margin-top:1.2rem;padding:.9rem;
            background:#0e1a10;border-radius:10px;border:1px solid #1c3320;font-size:.77rem;color:#5a8060;'>
            Demo accounts — <b style='color:#52e07c'>jafar</b>/<b style='color:#52e07c'>1234</b> &nbsp;·&nbsp;
            <b style='color:#52e07c'>demo</b>/<b style='color:#52e07c'>demo123</b>
        </div>
        """, unsafe_allow_html=True)
 
# ─────────────────────────────────────────────────────────────────
# 8 · MAIN APP
# ─────────────────────────────────────────────────────────────────
def main_app():
    u    = st.session_state.user
    rec  = st.session_state.user_db[st.session_state.user_db.username == u].iloc[0]
    reg  = rec.get("region", "Andhra Pradesh")
    model, model_err = get_model()

    wx = None   # safe default — assigned inside sidebar, read in hero banner

    # ── Sidebar ──────────────────────────────────────────────────
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center;padding:.8rem 0 .4rem'>
            <div style='font-size:2.8rem'>👨‍🌾</div>
            <div style='font-family:Cormorant Garamond,serif;font-size:1.2rem;color:#52e07c'>{u.title()}</div>
        </div>
        """, unsafe_allow_html=True)
        st.divider()
 
        st.markdown("**⚙️ Farm Profile**")
        farm_area  = st.number_input("Farm Area (acres)", 0.5, 500.0, 5.0, 0.5)
        soil_type  = st.selectbox("Soil Type", ["Red Sandy Loam","Black Cotton","Alluvial","Laterite","Clay Loam"])
        irrigation = st.selectbox("Irrigation", ["Drip","Sprinkler","Flood / Furrow","Rainfed"])

        # Location drives weather — changing this instantly updates the weather card below
        default_idx = REGIONS.index(reg) if reg in REGIONS else 0
        selected_location = st.selectbox("📍 Location", REGIONS, index=default_idx,
                                         help="Change location to update live weather automatically")
        language   = st.radio("Advisory Language", ["English","తెలుగు"], horizontal=True)

        st.divider()

        # ── Weather: auto GPS → IP → dropdown fallback ────────────
        gps_lat, _ = get_device_coords()
        ip_lat, _, _ = _ip_geolocation()

        # Source label shown in weather card
        if gps_lat is not None:
            wx_source_label = "📍 GPS location"
        elif ip_lat is not None:
            wx_source_label = "🌐 Network location"
        else:
            wx_source_label = "🏙️ Region"

        # Show which detection layer is active + reset GPS button
        c_src, c_btn = st.columns([2, 1])
        with c_src:
            st.markdown(
                f"<div style='font-size:.7rem;color:#5a8060;padding-top:.4rem'>"
                f"{wx_source_label}</div>",
                unsafe_allow_html=True,
            )
        with c_btn:
            if st.button("📍 Reset GPS", use_container_width=True, key="reset_geo",
                         help="Re-request your device GPS location"):
                # Clear the geo param so JS re-runs on next load
                st.query_params.clear()
                st.rerun()

        city_for_weather = selected_location.split(",")[0].strip()
        # "Other" is not a real city — skip the city fallback and rely on GPS/IP only
        wx = get_weather(fallback_city="" if city_for_weather.lower() == "other" else city_for_weather)
        if wx:
            ico = weather_icon(wx["icon"])
            badge = weather_source_badge(wx.get("source", ""))
            st.markdown(f"""
            <div class='weather-card'>
                <div style='font-size:.7rem;color:#5a8060;text-transform:uppercase;
                    letter-spacing:.1em;display:flex;align-items:center;gap:.4rem;flex-wrap:wrap'>
                    Live Weather · {wx['city']} {badge}
                </div>
                <div style='display:flex;align-items:center;gap:.6rem;margin-top:.4rem'>
                    <span style='font-size:2rem'>{ico}</span>
                    <span style='font-family:Cormorant Garamond,serif;font-size:2rem;
                        color:#52e07c'>{wx['temp']}°C</span>
                </div>
                <div style='font-size:.8rem;color:#7ecfea;margin-bottom:.4rem'>{wx['desc']}</div>
                <div style='font-size:.75rem;color:#5a8060;
                    display:grid;grid-template-columns:1fr 1fr;gap:.2rem'>
                    <span>💧 Humidity</span><span style='color:#ddeedd'>{wx['humidity']}%</span>
                    <span>💨 Wind</span><span style='color:#ddeedd'>{wx['wind']} m/s</span>
                    <span>🌧️ Rain/hr</span><span style='color:#ddeedd'>{wx['rain']} mm</span>
                    <span>🌡️ Feels</span><span style='color:#ddeedd'>{wx['feels']}°C</span>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # Farm alerts — all in one st.markdown to avoid ghost-box from split divs
            alerts = []
            if wx["humidity"] > 80:
                alerts.append(("⚠️", "High humidity — fungal risk", "#e8a020"))
            if wx["temp"] > 38:
                alerts.append(("🌡️", "Heat stress — irrigate early", "#e05252"))
            if wx["temp"] < 15:
                alerts.append(("❄️", "Cold — delay N top-dressing", "#52abe0"))
            if wx["wind"] > 5:
                alerts.append(("💨", "High wind — avoid spraying", "#e8a020"))
            if not alerts:
                alerts.append(("✅", "Conditions suitable for farm ops", "#52e07c"))
            alert_html = "<div style='margin-top:.5rem'>" + "".join(
                f"<div style='font-size:.73rem;background:{c}15;border-left:3px solid {c};"
                f"border-radius:6px;padding:.4rem .6rem;margin-bottom:.3rem;color:#ddeedd'>"
                f"{i} {m}</div>"
                for i, m, c in alerts
            ) + "</div>"
            st.markdown(alert_html, unsafe_allow_html=True)
        else:
            st.info("Add OPENWEATHER_KEY in secrets.toml for live weather.", icon="🌦️")
 
        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.logged_in = False
            st.session_state.user = None
            st.rerun()
 
    # ── Hero banner ──────────────────────────────────────────────
    season_now = "Kharif" if 6 <= datetime.now().month <= 10 else "Rabi"
    wx_inline  = f"Live: {wx['temp']}°C, {wx['humidity']}% humidity" if wx else "Add weather API key"
 
    st.markdown(f"""
    <div class='hero'>
        <div class='hero-emoji'>🌾</div>
        <div style='font-family:Cormorant Garamond,serif;font-size:2.1rem;font-weight:700;
            color:#52e07c;margin-bottom:.3rem'>AgriSmart AI Pro</div>
        <div style='color:#7a9e7e;font-size:.9rem'>
            {selected_location} &nbsp;·&nbsp; {datetime.now().strftime("%B %d, %Y")} &nbsp;·&nbsp; Season: {season_now}
        </div>
        <div style='margin-top:.9rem'>
            <span class='pill'>🌱 {farm_area} acres</span>
            <span class='pill'>🪨 {soil_type}</span>
            <span class='pill'>💧 {irrigation}</span>
            <span class='pill'>🌡️ {wx_inline}</span>
            <span class='pill'>📊 {len(st.session_state.history)} Advisories</span>
            <span class='pill'>🔬 {len(st.session_state.disease_log)} Diagnoses</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
 
    if model is None:
        if model_err:
            st.sidebar.error(model_err)
        st.warning("⚠️  **Gemini API key not configured** — AI features will show rule-based results only. Add `GEMINI_API_KEY` to `.streamlit/secrets.toml`.")
 
    # ── 5 Main Tabs ───────────────────────────────────────────────
    tab1, tab2, tab3 = st.tabs([
        "🎯 AI Crop Advisor",
        "💰 Profit Calculator",
        "📊 Analytics & KB",
    ])
 
    # ════════════════════════════════════════════════════════════
    # TAB 1 — AI CROP ADVISOR
    # ════════════════════════════════════════════════════════════
    with tab1:
        left, right = st.columns([1.3, 1], gap="large")

        with left:
            st.markdown('<div class="sec-head">Soil & Climate Parameters</div>', unsafe_allow_html=True)

            # ── Inputs OUTSIDE st.form so every change triggers a rerun
            # and the NPK radar + pH gauge update live ──────────────
            c1, c2, c3 = st.columns(3)
            with c1:
                n   = st.number_input("Nitrogen N (kg/ha)",    0, 200, 90,  key="adv_n")
                hum = st.slider("Humidity %",                  20, 100, 65, key="adv_hum")
            with c2:
                p   = st.number_input("Phosphorus P (kg/ha)", 0, 200, 42,  key="adv_p")
                temp= st.slider("Temperature °C",              5,  50, 28,  key="adv_temp")
            with c3:
                k   = st.number_input("Potassium K (kg/ha)",  0, 200, 38,  key="adv_k")
                rain= st.slider("Rainfall mm",                 0, 600, 95,  key="adv_rain")

            ph     = st.slider("Soil pH", 4.0, 9.5, 6.4, 0.1,
                               help="Ideal: 6.0–7.5 for most AP crops", key="adv_ph")
            season = st.selectbox("Sowing Season", list(SEASON_MAP.keys()), key="adv_season")

            if wx:
                st.caption(f"💡 Live: {wx['temp']}°C, {wx['humidity']}% humidity — consider using these values.")

            go = st.button("🚀 Generate AI Advisory", use_container_width=True, key="adv_go")

        with right:
            st.markdown('<div class="sec-head">Live Diagnostics</div>', unsafe_allow_html=True)
            # Charts now read the live input values directly — update on every keystroke
            st.plotly_chart(npk_radar(n, p, k),  use_container_width=True)
            st.plotly_chart(ph_gauge(ph),         use_container_width=True)

        # ── Run advisory ──────────────────────────────────────────
        if go:
            st.session_state.advisory_inputs = {"n": n, "p": p, "k": k, "ph": ph}
            scored = score_crops(n, p, k, ph, temp, rain)

            best = scored[0][0]
            m1, m2, m3, m4, m5 = st.columns(5)
            m1.metric("Best Crop",   best)
            m2.metric("Market Rate", f"₹{MARKET.get(best,0):,}/q")
            m3.metric("pH Status",   "✅ Good" if 6<=ph<=7.5 else "⚠️ Adjust")
            m4.metric("N Status",    "✅ Good" if 60<=n<=120 else "⬆️ Low" if n<60 else "⬇️ High")
            m5.metric("Season Fit",  f"{scored[0][2]}%")

            st.plotly_chart(crop_comparison_bar(scored), use_container_width=True)

            wx_ctx = f"{wx['temp']}°C, {wx['humidity']}% humidity, {wx['desc']}" if wx else ""
            prompt = advisory_prompt(n, p, k, ph, temp, rain, hum, soil_type, season, language, wx_ctx)

            if model:
                with st.spinner("🧠 Dr. Arjun Reddy is analysing your farm conditions..."):
                    try:
                        resp = model.generate_content(prompt)
                        text = resp.text
                        st.session_state.last_advisory = text
                        st.session_state.history.append({
                            "Date":      datetime.now().strftime("%d %b %Y %H:%M"),
                            "N/P/K":     f"{n}/{p}/{k}",
                            "pH":        ph,
                            "Best Crop": best,
                            "Score":     f"{scored[0][2]}%",
                        })
                        # Fix: single st.markdown call — open tag, content, close tag
                        # all in one call so Streamlit renders them as one element
                        st.markdown(
                            f"<div class='result-box'>\n\n{text}\n\n</div>",
                            unsafe_allow_html=True,
                        )
                    except Exception as e:
                        st.error(f"AI error: {e}")
            else:
                # Fallback: rule-based output
                lines_out = ["### 🏆 Rule-Based Crop Recommendations\n"]
                for crop, sc, pct in scored[:3]:
                    bar   = "█" * int(pct // 10) + "░" * (10 - int(pct // 10))
                    price = MARKET.get(crop, 0)
                    profit_est = round(15 * price - 9000)
                    lines_out.append(
                        f"**{crop}** — `{bar}` {pct}%\n"
                        f"- Market Price: ₹{price:,}/quintal\n"
                        f"- Est. Net Profit: ₹{profit_est:,}/acre (15 q yield)\n"
                    )
                st.markdown(
                    "<div class='result-box'>\n\n" + "\n".join(lines_out) + "\n\n</div>",
                    unsafe_allow_html=True,
                )
 
    # ════════════════════════════════════════════════════════════
    # TAB 2 — PROFIT CALCULATOR
    # ════════════════════════════════════════════════════════════
    with tab2:
        st.markdown('<div class="sec-head">💰 Crop Profit & ROI Calculator</div>', unsafe_allow_html=True)
 
        p1, p2 = st.columns(2, gap="large")
 
        with p1:
            p_crop   = st.selectbox("Select Crop", list(CROPS.keys()), key="pc")
            p_area   = st.number_input("Farm Area (acres)", .5, 200., farm_area, .5)
            p_yield  = st.number_input("Expected Yield (quintals/acre)", 1., 100., 15., .5)
            p_price  = st.number_input("Market Price (₹/quintal)", 100, 60000, MARKET.get(p_crop,2000))
            st.caption("Input Costs (₹ per acre)")
            c_seed   = st.number_input("Seed Cost",       0, 15000, 1500)
            c_fert   = st.number_input("Fertilizer Cost", 0, 25000, 3800)
            c_labor  = st.number_input("Labour Cost",     0, 25000, 4200)
            c_other  = st.number_input("Other Costs",     0, 15000, 900)
 
        with p2:
            total_in = (c_seed + c_fert + c_labor + c_other) * p_area
            gross    = p_yield * p_area * p_price
            net      = gross - total_in
            roi      = (net/total_in*100) if total_in else 0
            bcr      = (gross/total_in) if total_in else 0
            break_q  = total_in / (p_price * p_area) if p_price and p_area else 0
 
            profit_color = "#52e07c" if net > 0 else "#e05252"
            verdict = "✅ Excellent" if bcr > 2 else "✅ Profitable" if bcr > 1 else "⚠️ Break-even risk"
 
            st.markdown(f"""
            <div class='glass' style='margin-bottom:1rem'>
                <div style='font-family:Cormorant Garamond,serif;font-size:1.3rem;color:#52e07c;margin-bottom:1rem'>
                    {p_crop} · {p_area} acres · Profit Summary
                </div>
                <table style='width:100%;border-collapse:collapse;font-size:.88rem'>
                    <tr><td style='color:#5a8060;padding:5px 0'>Total Yield</td>
                        <td style='text-align:right;color:#ddeedd'><b>{p_yield*p_area:.1f} quintals</b></td></tr>
                    <tr><td style='color:#5a8060;padding:5px 0'>Gross Income</td>
                        <td style='text-align:right;color:#52e07c'><b>₹{gross:,.0f}</b></td></tr>
                    <tr><td style='color:#5a8060;padding:5px 0'>Total Input Cost</td>
                        <td style='text-align:right;color:#e05252'><b>₹{total_in:,.0f}</b></td></tr>
                    <tr style='border-top:1px solid #1c3320'>
                        <td style='padding:8px 0;font-size:1rem'><b>Net Profit</b></td>
                        <td style='text-align:right;font-size:1.3rem;font-family:Cormorant Garamond,serif;
                            color:{profit_color}'><b>₹{net:,.0f}</b></td></tr>
                    <tr><td style='color:#5a8060;padding:5px 0'>ROI</td>
                        <td style='text-align:right;color:#e8a020'><b>{roi:.1f}%</b></td></tr>
                    <tr><td style='color:#5a8060;padding:5px 0'>Benefit-Cost Ratio</td>
                        <td style='text-align:right;color:#52abe0'><b>{bcr:.2f}</b></td></tr>
                    <tr><td style='color:#5a8060;padding:5px 0'>Break-even Yield</td>
                        <td style='text-align:right;color:#ddeedd'><b>{break_q:.1f} q/acre</b></td></tr>
                </table>
                <div style='margin-top:.9rem;padding:.7rem;background:{"rgba(10,46,20,0.33)" if net>0 else "rgba(46,10,10,0.33)"};
                    border-radius:8px;font-size:.82rem;color:{profit_color}'>
                    {verdict} — BCR of {bcr:.2f} means every ₹1 invested returns ₹{bcr:.2f}
                </div>
            </div>
            """, unsafe_allow_html=True)
 
            # Compare top 3 crops
            st.markdown("**Compare with other crops (same area & yield)**")
            comp = []
            for cn, cp in sorted(MARKET.items(), key=lambda x: x[1], reverse=True)[:8]:
                g = p_yield * p_area * cp
                n2= g - total_in
                comp.append({"Crop": cn, "Price/q": f"₹{cp:,}", "Gross": f"₹{g:,.0f}", "Net": f"₹{n2:,.0f}", "BCR": f"{g/total_in:.2f}" if total_in else "-"})
            st.dataframe(pd.DataFrame(comp), use_container_width=True, hide_index=True)
 
        st.plotly_chart(profit_waterfall(p_area, p_yield, p_price, c_seed, c_fert, c_labor, c_other), use_container_width=True)
 
    # ════════════════════════════════════════════════════════════
    # TAB 3 — ANALYTICS + KB
    # ════════════════════════════════════════════════════════════
    with tab3:
        a1, a2 = st.tabs(["📊 Farm Analytics", "📚 Knowledge Base"])

        with a1:
            mm1, mm2, mm3, mm4, mm5 = st.columns(5)
            mm1.metric("Farm Area",   f"{farm_area} ac")
            mm2.metric("Season",      season_now)
            mm3.metric("Advisories",  len(st.session_state.history))
            mm4.metric("Diagnoses",   len(st.session_state.disease_log))
            mm5.metric("Soil Type",   soil_type[:8]+"…" if len(soil_type) > 8 else soil_type)

            st.plotly_chart(trend_chart(), use_container_width=True)

            # Side-by-side advisory + disease history
            st.markdown('<div class="sec-head">Crop Activity Log</div>', unsafe_allow_html=True)
            col_h, col_d = st.columns(2, gap="large")
            with col_h:
                st.caption("📋 Advisory History")
                if st.session_state.history:
                    st.dataframe(pd.DataFrame(st.session_state.history),
                                 use_container_width=True, hide_index=True)
                else:
                    st.info("No advisories yet.")
            with col_d:
                st.caption("🔬 Disease Diagnoses")
                if st.session_state.disease_log:
                    st.dataframe(pd.DataFrame(st.session_state.disease_log),
                                 use_container_width=True, hide_index=True)
                else:
                    st.info("No diagnoses yet — use Disease Log tab.")

        with a2:
            kb1, kb2, kb3, kb4, kb5 = st.tabs([
                "🌾 Crop Requirements",
                "💊 Fertilizer Guide",
                "🧾 Market Prices",
                "📅 Season Calendar",
                "🔬 Disease Log",
            ])

            with kb1:
                rows = []
                for cn, r in CROPS.items():
                    rows.append({
                        "Crop": cn,
                        "N (kg/ha)": f"{r['N'][0]}–{r['N'][1]}",
                        "P (kg/ha)": f"{r['P'][0]}–{r['P'][1]}",
                        "K (kg/ha)": f"{r['K'][0]}–{r['K'][1]}",
                        "pH":        f"{r['pH'][0]}–{r['pH'][1]}",
                        "Temp °C":   f"{r['T'][0]}–{r['T'][1]}",
                        "Rain mm":   f"{r['R'][0]}–{r['R'][1]}",
                        "Price ₹/q": f"₹{MARKET.get(cn,0):,}",
                    })
                st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            with kb2:
                for fn, fd in FERT_GUIDE.items():
                    with st.expander(f"🧪 {fn}"):
                        st.write(fd)

            with kb3:
                mdf = pd.DataFrame([
                    {"Crop": c, "Market Price (₹/quintal)": f"₹{p:,}",
                     "Type": "MSP/Indicative", "Updated": "2024–25"}
                    for c, p in sorted(MARKET.items(), key=lambda x: x[1], reverse=True)
                ])
                st.dataframe(mdf, use_container_width=True, hide_index=True)
                st.caption("Prices are indicative AP market rates. Always check your local mandi before selling.")
                fig = px.bar(
                    pd.DataFrame(list(MARKET.items()), columns=["Crop","Price"]).sort_values("Price", ascending=True),
                    x="Price", y="Crop", orientation="h",
                    color="Price", color_continuous_scale=["#1a4d22","#52e07c"],
                    title="AP Market Prices (₹/quintal)",
                )
                fig.update_layout(**LAYOUT, height=380, coloraxis_showscale=False)
                st.plotly_chart(fig, use_container_width=True)

            with kb4:
                st.plotly_chart(season_dot_chart(), use_container_width=True)
                st.markdown('<div class="sec-head">Crops by Season</div>', unsafe_allow_html=True)
                for season_name, crops in SEASON_MAP.items():
                    badges = " ".join([f"<span class='green-pill pill'>{c}</span>" for c in crops])
                    st.markdown(f"**{season_name}**", unsafe_allow_html=False)
                    st.markdown(badges, unsafe_allow_html=True)
                    st.markdown("")

            # ── Disease Log ─────────────────────────────────────────
            with kb5:
                st.markdown('<div class="sec-head">🔬 Crop Disease Detector & Log</div>', unsafe_allow_html=True)
                st.caption("Upload a leaf photo for AI diagnosis. Every result is saved and cross-referenced with your advisory history.")

                det_l, det_r = st.columns([1, 1.2], gap="large")

                with det_l:
                    dis_crop = st.selectbox("Crop", list(CROPS.keys()), key="kb_dis_crop")
                    dis_img  = st.file_uploader("📸 Upload Leaf / Plant Image",
                                                type=["jpg","jpeg","png","webp"],
                                                key="kb_dis_img")
                    if dis_img:
                        if dis_img.name != st.session_state.get("sb_last_img_name", ""):
                            st.session_state["sb_disease_result"] = ""
                            st.session_state["sb_last_img_name"] = dis_img.name
                        st.image(Image.open(dis_img), caption="Uploaded image", use_container_width=True)

                    diagnose_btn = st.button("🔬 Diagnose Disease", use_container_width=True,
                                             disabled=not dis_img, key="kb_diag_btn")

                with det_r:
                    st.markdown('<div class="sec-head">Quick Symptom Lookup</div>', unsafe_allow_html=True)
                    st.caption("No image? Pick a symptom for instant guidance.")
                    sym = st.selectbox("What do you observe?",
                                       ["— Select —"] + list(DISEASE_QUICK.keys()),
                                       key="kb_sym_sel")
                    if sym != "— Select —":
                        st.markdown(f"""
                        <div class='glass' style='border-color:#1c4422;margin-top:.5rem'>
                            <div style='font-size:.75rem;color:#5a8060;margin-bottom:.4rem'>RECOMMENDED ACTION</div>
                            <div style='font-size:.9rem;color:#ddeedd'>{DISEASE_QUICK[sym]}</div>
                        </div>""", unsafe_allow_html=True)
                    st.divider()
                    st.markdown("**📋 Quick Reference**")
                    for s, d in DISEASE_QUICK.items():
                        with st.expander(s):
                            st.write(d)

                # Run diagnosis and log
                if diagnose_btn and dis_img:
                    if model:
                        with st.spinner("🔬 Plant pathologist AI is scanning..."):
                            try:
                                dis_img.seek(0)
                                ipart = {"mime_type": dis_img.type, "data": dis_img.getvalue()}
                                resp  = model.generate_content([disease_prompt(dis_crop), ipart])
                                st.session_state["sb_disease_result"] = resp.text
                                last_crop = (st.session_state.history[-1]["Best Crop"]
                                             if st.session_state.history else "—")
                                st.session_state.disease_log.append({
                                    "Date":               datetime.now().strftime("%d %b %Y %H:%M"),
                                    "Crop":               dis_crop,
                                    "Image":              dis_img.name,
                                    "Last Advisory Crop": last_crop,
                                    "Status":             "Diagnosed ✅",
                                })
                            except Exception as e:
                                st.error(f"Analysis error: {e}")
                    else:
                        st.warning("Configure Gemini API key to enable image analysis.")

                if st.session_state.get("sb_disease_result"):
                    st.markdown(
                        f"<div class='result-box'>\n\n{st.session_state['sb_disease_result']}\n\n</div>",
                        unsafe_allow_html=True,
                    )

                # Disease history log table
                st.divider()
                st.markdown('<div class="sec-head">Disease History Log</div>', unsafe_allow_html=True)
                if st.session_state.disease_log:
                    st.dataframe(pd.DataFrame(st.session_state.disease_log),
                                 use_container_width=True, hide_index=True)

                    # Cross-reference alert
                    adv_crops = {h["Best Crop"] for h in st.session_state.history}
                    dis_crops = {d["Crop"] for d in st.session_state.disease_log}
                    overlap   = adv_crops & dis_crops
                    if overlap:
                        badges = " ".join(f"<span class='amber-pill pill'>{c}</span>" for c in sorted(overlap))
                        st.markdown(
                            f"<div style='background:#1a1a0a;border:1px solid #c9953a;border-radius:10px;"
                            f"padding:.8rem 1rem;font-size:.82rem;color:#ddeedd;margin-top:.6rem'>"
                            f"⚠️ <b>Crops appearing in both advisories and disease log:</b><br>"
                            f"{badges}<br>"
                            f"<span style='color:#5a8060;font-size:.75rem'>Review fertilizer and disease management for these crops.</span>"
                            f"</div>",
                            unsafe_allow_html=True,
                        )

                    c1, _ = st.columns([1, 4])
                    with c1:
                        if st.button("🗑️ Clear Log", key="clear_dis_log"):
                            st.session_state.disease_log = []
                            st.session_state["sb_disease_result"] = ""
                            st.rerun()
                else:
                    st.info("No diagnoses yet — upload a leaf photo above to start tracking.")
 
 
    # ── Fire GPS detection — placed at bottom so its iframe renders
    # after all content and never creates a gap before the hero ────
    inject_geolocation_js()

# ─────────────────────────────────────────────────────────────────
# 9 · ENTRY POINT
# ─────────────────────────────────────────────────────────────────
if st.session_state.logged_in:
    main_app()
else:
    auth_page()