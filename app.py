import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go
import hashlib
from datetime import datetime
import firebase_admin
from firebase_admin import credentials, firestore

# ---------------------------------------------------------
# AZURE ML CONFIG
# ---------------------------------------------------------
ENDPOINT_URL = "https://hemosense-hb-jzzks.southindia.inference.ml.azure.com/score"
API_KEY = st.secrets.get("AZURE_API_KEY", "")

# ---------------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------------
st.set_page_config(page_title="HemoSense AI", page_icon="🩸", layout="wide")

# ---------------------------------------------------------
# COLOR PALETTE (UNCHANGED)
# ---------------------------------------------------------
PALETTE = {
    "bg_light": "#1e3a8a",
    "card": "#3b82f6",
    "accent": "#1e40af",
    "text": "#FFFFFF",
    "dark_bg": "#071226",
    "dark_card": "#0b2a3c",
    "dark_text": "#FFFFFF",
    "dark_accent": "#20b2aa"
}

# ---------------------------------------------------------
# FIREBASE INIT (STREAMLIT CLOUD SAFE)
# ---------------------------------------------------------
@st.cache_resource
def init_firebase():
    if not firebase_admin._apps:
        cred = credentials.Certificate(dict(st.secrets["FIREBASE_KEY"]))
        firebase_admin.initialize_app(cred)
    return firestore.client()

db = init_firebase()

# ---------------------------------------------------------
# SECURITY
# ---------------------------------------------------------
def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()

# ---------------------------------------------------------
# FIRESTORE HELPERS
# ---------------------------------------------------------
def save_user(email, name, password_hash):
    db.collection("users").document(email).set({
        "email": email,
        "name": name,
        "password_hash": password_hash,
        "created_at": datetime.utcnow()
    })

def authenticate(email, password):
    doc = db.collection("users").document(email).get()
    return doc.exists and doc.to_dict()["password_hash"] == hash_password(password)

def append_prediction(email, hb, green, red, ir, skin):
    db.collection("predictions").add({
        "email": email,
        "hb_value": hb,
        "green": green,
        "red": red,
        "ir": ir,
        "skin_type": skin,
        "timestamp": datetime.utcnow()
    })

def load_user_history(email):
    docs = (
        db.collection("predictions")
        .where("email", "==", email)
        .order_by("timestamp")
        .stream()
    )
    return pd.DataFrame([d.to_dict() for d in docs])

# ---------------------------------------------------------
# GLOBAL LANGUAGE SUPPORT
# ---------------------------------------------------------
LANGUAGE_NAMES = {
    "en": "English", "es": "Español", "fr": "Français", "de": "Deutsch",
    "it": "Italiano", "pt": "Português", "ru": "Русский", "zh": "中文",
    "ja": "日本語", "ko": "한국어", "ar": "العربية", "hi": "हिन्दी",
    "bn": "বাংলা", "ta": "தமிழ்", "te": "తెలుగు", "ml": "മലയാളം",
    "mr": "मराठी", "gu": "ગુજરાતી", "ur": "اردو", "fa": "فارسی",
    "tr": "Türkçe", "vi": "Tiếng Việt", "th": "ไทย", "id": "Bahasa Indonesia",
    "sw": "Kiswahili", "nl": "Nederlands", "sv": "Svenska",
    "no": "Norsk", "da": "Dansk", "fi": "Suomi", "pl": "Polski",
    "cs": "Čeština", "el": "Ελληνικά", "he": "עברית"
}

TRANSLATIONS = {
    "en": {
        "title": "HemoSense AI",
        "subtitle": "Non-Invasive Hemoglobin Estimation System",
        "email": "Email",
        "name": "Full name",
        "password": "Password",
        "confirm_password": "Confirm Password",
        "register": "Register",
        "login": "Login",
        "logout": "Logout",
        "run": "Run Diagnostic Scan",
        "history": "Your Recent Readings"
    }
}

def t(key):
    lang = st.session_state.get("lang", "en")
    return TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))

# ---------------------------------------------------------
# SESSION STATE
# ---------------------------------------------------------
for k, v in {"theme": "light", "lang": "en", "user": None}.items():
    st.session_state.setdefault(k, v)

# ---------------------------------------------------------
# THEME CSS (YOUR ORIGINAL STYLE)
# ---------------------------------------------------------
def set_theme_css():
    if st.session_state["theme"] == "dark":
        bg, text, card, accent = (
            PALETTE["dark_bg"], PALETTE["dark_text"],
            PALETTE["dark_card"], PALETTE["dark_accent"]
        )
    else:
        bg, text, card, accent = (
            PALETTE["bg_light"], PALETTE["text"],
            PALETTE["card"], PALETTE["accent"]
        )

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
    .reportview-container {{background:{bg}; color:{text}; font-family:Poppins}}
    .stButton>button {{background:{accent}; color:white; border-radius:10px; font-weight:700}}
    .stApp .block-container {{background:{card}; padding:20px; border-radius:12px}}
    section[data-testid="stSidebar"] {{background:#2d2d2d; color:white}}
    </style>
    """, unsafe_allow_html=True)

set_theme_css()

# ---------------------------------------------------------
# SIDEBAR
# ---------------------------------------------------------
with st.sidebar:
    st.radio("Theme", ["light", "dark"], key="theme", on_change=set_theme_css)
    st.selectbox("Language", list(LANGUAGE_NAMES.keys()),
                 format_func=lambda x: LANGUAGE_NAMES[x], key="lang")
    if st.session_state["user"] and st.button(t("logout")):
        st.session_state["user"] = None
        st.rerun()

# ---------------------------------------------------------
# HEADER
# ---------------------------------------------------------
st.title(f"🩸 {t('title')}")
st.markdown(f"### {t('subtitle')}")

# ---------------------------------------------------------
# AUTH
# ---------------------------------------------------------
if not st.session_state["user"]:
    mode = st.radio("Account", ["Login", "Register"], horizontal=True)
    email = st.text_input(t("email"))
    password = st.text_input(t("password"), type="password")

    if mode == "Register":
        name = st.text_input(t("name"))
        confirm = st.text_input(t("confirm_password"), type="password")
        if st.button(t("register")) and password == confirm:
            save_user(email, name, hash_password(password))
            st.success("Registered successfully. Please login.")
    else:
        if st.button(t("login")) and authenticate(email, password):
            st.session_state["user"] = email
            st.rerun()

    st.stop()

# ---------------------------------------------------------
# SENSOR INPUT
# ---------------------------------------------------------
st.subheader("1. Sensor Input")
c1, c2 = st.columns(2)

with c1:
    green = st.slider("Green Light Absorption (535nm)", 0.0, 25.0, 10.0, 0.1)
    red = st.slider("Red Light Absorption (660nm)", 700.0, 1300.0, 1000.0, 10.0)
    ir = st.slider("Infrared Absorption (940nm)", 5400.0, 6300.0, 5850.0, 50.0)

with c2:
    skin = st.selectbox("Fitzpatrick Skin Type", [1, 2, 3, 4, 5, 6])

# ---------------------------------------------------------
# RUN ML
# ---------------------------------------------------------
if st.button(t("login")):
    auth_result = authenticate(email, password)

    if auth_result == "NO_USER":
        st.error("❌ Account does not exist. Please register first.")

    elif auth_result == "WRONG_PASSWORD":
        st.error("❌ Incorrect password. Please try again.")

    elif auth_result == "SUCCESS":
        st.session_state['user'] = email
        st.session_state['page'] = 'dashboard'
        st.success("✅ Login successful")
        st.rerun()

if st.button(t("run")):
    payload = {
        "input_data": {
            "columns": [
                "Green_535nm", "Red_660nm", "IR_940nm",
                "Ratio_Red_IR", "Ratio_Green_IR", "Fitzpatrick_Scale"
            ],
            "index": [0],
            "data": [[green, red, ir, red/ir, green/ir, skin]]
        }
    }

    r = requests.post(
        ENDPOINT_URL,
        headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
        json=payload
    )

    if r.status_code == 200:
        hb = float(list(r.json().values())[0][0])
        append_prediction(st.session_state["user"], hb, green, red, ir, skin)

        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=hb,
            title={"text": "Hemoglobin (g/dL)"},
            gauge={"axis": {"range": [0, 20]}, "bar": {"color": PALETTE["accent"]}}
        ))
        st.plotly_chart(fig, use_container_width=True)

# ---------------------------------------------------------
# HISTORY
# ---------------------------------------------------------
st.markdown("---")
st.subheader(t("history"))

df = load_user_history(st.session_state["user"])
if not df.empty:
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    st.dataframe(df.sort_values("timestamp", ascending=False))
else:
    st.info("No readings yet")


