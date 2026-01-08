import streamlit as st
import json
import requests
import pandas as pd
import plotly.graph_objects as go
import hashlib
import os
import csv
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURE YOUR AZURE DETAILS HERE
# ---------------------------------------------------------
ENDPOINT_URL = "https://hemosense-hb-jzzks.southindia.inference.ml.azure.com/score"
API_KEY = "3GwpLd8lBNi7jydXKpyrZcoxs0HrlKIOPPnZbWSgV0B3p4wpViJoJQQJ99CAAAAAAAAAAAAAINFRAZML2yhH"
# ---------------------------------------------------------

BASE_DIR = os.path.dirname(__file__)
USERS_JSON = os.path.join(BASE_DIR, "users.json")
USERS_CSV = os.path.join(BASE_DIR, "users.csv")
PREDICTIONS_CSV = os.path.join(BASE_DIR, "predictions.csv")

st.set_page_config(page_title="HemoSense AI", page_icon="🩸", layout="wide")

PALETTE = {
    # darker bluish shades for a cleaner, modern look
    "bg_light": "#1e3a8a",
    "card": "#3b82f6",
    # accent and text tuned per user: light theme -> dark blue; dark theme -> teal
    "accent": "#1e40af",
    "text": "#FFFFFF",
    "dark_bg": "#071226",
    "dark_card": "#0b2a3c",
    "dark_text": "#FFFFFF",
    "dark_accent": "#20b2aa"
}

def ensure_files():
    if not os.path.exists(USERS_JSON):
        with open(USERS_JSON, 'w', encoding='utf-8') as f:
            json.dump({}, f)
    if not os.path.exists(USERS_CSV):
        with open(USERS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["email", "name", "password_hash", "created_at"]) 
    if not os.path.exists(PREDICTIONS_CSV):
        with open(PREDICTIONS_CSV, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["email", "timestamp", "hb_value", "green", "red", "ir", "skin_type"]) 

ensure_files()

def hash_password(pw: str) -> str:
    return hashlib.sha256(pw.encode('utf-8')).hexdigest()

def load_users():
    with open(USERS_JSON, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_user(email, name, password_hash):
    users = load_users()
    users[email] = {"name": name, "password_hash": password_hash, "created_at": datetime.utcnow().isoformat()}
    with open(USERS_JSON, 'w', encoding='utf-8') as f:
        json.dump(users, f, indent=2)
    # append to csv
    with open(USERS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email, name, password_hash, datetime.utcnow().isoformat()])

def authenticate(email, password) -> bool:
    users = load_users()
    if email in users and users[email]['password_hash'] == hash_password(password):
        return True
    return False

def append_prediction(email, hb_value, green, red, ir, skin_type):
    with open(PREDICTIONS_CSV, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([email, datetime.utcnow().isoformat(), hb_value, green, red, ir, skin_type])

# --- Translations (expanded) ---
LANGUAGE_NAMES = {
    'en': 'English',
    'es': 'Español (Spanish)',
    'fr': 'Français (French)',
    'de': 'Deutsch (German)',
    'it': 'Italiano (Italian)',
    'pt': 'Português (Portuguese)',
    'ja': '日本語 (Japanese)',
    'zh': '中文 (Chinese)',
    'hi': 'हिन्दी (Hindi)',
    'ar': 'العربية (Arabic)',
    'ru': 'Русский (Russian)',
    'ko': '한국어 (Korean)'
}

TRANSLATIONS = {
    'en': {
        'title': 'HemoSense AI',
        'subtitle': 'Non-Invasive Hemoglobin Estimation System',
        'email': 'Email',
        'name': 'Full name',
        'password': 'Password',
        'confirm_password': 'Confirm Password',
        'register': 'Register',
        'login': 'Login',
        'run': 'Run Diagnostic Scan',
        'logout': 'Logout',
        'history': 'Your Recent Readings'
    },
    'es': {'title':'HemoSense AI', 'subtitle':'Estimación no invasiva de hemoglobina','email':'Correo','name':'Nombre','password':'Contraseña','confirm_password':'Confirmar Contraseña','register':'Registrarse','login':'Iniciar sesión','run':'Ejecutar diagnóstico','logout':'Cerrar sesión','history':'Lecturas recientes'},
    'fr': {'title':'HemoSense AI','subtitle':'Estimation non invasive de l\'hémoglobine','email':'Email','name':'Nom','password':'Mot de passe','confirm_password':'Confirmer mot de passe','register':'S\'inscrire','login':'Connexion','run':'Lancer le diagnostic','logout':'Se déconnecter','history':'Lectures récentes'},
    'de': {'title':'HemoSense AI','subtitle':'Nicht-invasive Hämoglobin-Schätzung','email':'E-Mail','name':'Vollständiger Name','password':'Passwort','confirm_password':'Passwort bestätigen','register':'Registrieren','login':'Anmelden','run':'Diagnose durchführen','logout':'Abmelden','history':'Ihre letzten Messwerte'},
    'it': {'title':'HemoSense AI','subtitle':'Stima non invasiva dell\'emoglobina','email':'Email','name':'Nome completo','password':'Password','confirm_password':'Conferma password','register':'Registrati','login':'Accedi','run':'Esegui diagnostica','logout':'Esci','history':'Letture recenti'},
    'pt': {'title':'HemoSense AI','subtitle':'Estimativa não invasiva de hemoglobina','email':'Email','name':'Nome completo','password':'Senha','confirm_password':'Confirmar senha','register':'Registrar','login':'Entrar','run':'Executar diagnóstico','logout':'Sair','history':'Leituras recentes'},
    'ja': {'title':'HemoSense AI','subtitle':'非侵襲的ヘモグロビン推定システム','email':'メール','name':'フルネーム','password':'パスワード','confirm_password':'パスワード確認','register':'登録','login':'ログイン','run':'診断スキャン実行','logout':'ログアウト','history':'最近の読み取り'},
    'zh': {'title':'HemoSense AI','subtitle':'非侵入性血红蛋白估计','email':'电子邮件','name':'姓名','password':'密码','confirm_password':'确认密码','register':'注册','login':'登录','run':'运行诊断','logout':'登出','history':'您的最近读数'},
    'hi': {'title':'HemoSense AI','subtitle':'गैर-आक्रामक हीमोग्लोबिन अनुमान','email':'ईमेल','name':'पूरा नाम','password':'पासवर्ड','confirm_password':'पासवर्ड की पुष्टि','register':'रजिस्टर','login':'लॉगिन','run':'डायग्नोस्टिक चलाएं','logout':'लॉगआउट','history':'आपके हालिया रीडिंग'},
    'ar': {'title':'HemoSense AI','subtitle':'نظام تقدير الهيموجلوبين غير الغازي','email':'البريد الإلكتروني','name':'الاسم الكامل','password':'كلمة المرور','confirm_password':'تأكيد كلمة المرور','register':'تسجيل','login':'تسجيل الدخول','run':'تشغيل الفحص التشخيصي','logout':'تسجيل الخروج','history':'قراءاتك الأخيرة'},
    'ru': {'title':'HemoSense AI','subtitle':'Неинвазивная система оценки гемоглобина','email':'Электронная почта','name':'Полное имя','password':'Пароль','confirm_password':'Подтверждение пароля','register':'Регистрация','login':'Вход','run':'Запустить диагностику','logout':'Выход','history':'Ваши последние показания'},
    'ko': {'title':'HemoSense AI','subtitle':'비침습적 헤모글로빈 추정 시스템','email':'이메일','name':'전체 이름','password':'비밀번호','confirm_password':'비밀번호 확인','register':'등록','login':'로그인','run':'진단 스캔 실행','logout':'로그아웃','history':'최근 측정값'}
}

def t(key):
    lang = st.session_state.get('lang', 'en')
    return TRANSLATIONS.get(lang, TRANSLATIONS['en']).get(key, key)

# --- Theme handling ---
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'light'
if 'lang' not in st.session_state:
    st.session_state['lang'] = 'en'
if 'user' not in st.session_state:
    st.session_state['user'] = None

def set_theme_css():
    if st.session_state['theme'] == 'dark':
        bg = PALETTE['dark_bg']
        text = PALETTE['dark_text']
        card = PALETTE['dark_card']
    else:
        bg = PALETTE['bg_light']
        text = PALETTE['text']
        card = PALETTE['card']
    st.markdown(f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');
        .reportview-container {{background:{bg}; color:{text}; font-family: 'Poppins', 'Segoe UI', sans-serif;}}
        .stApp .css-ffhzg2.egzxvld2 {{padding-top:12px}} /* small top padding */
        .stButton>button {{background:{PALETTE['accent'] if st.session_state['theme']=='light' else PALETTE['dark_accent']}; color: white; border-radius:10px; padding:8px 14px; font-weight:700; font-family: 'Poppins', sans-serif}}
        .stSlider>div>div>div>div{{color:{text}; font-family: 'Poppins', sans-serif}}
        .stApp .block-container{{background: {card}; padding:20px; border-radius:12px; font-family: 'Poppins', sans-serif}}
            /* Sidebar styling for better contrast in light theme */
            section[data-testid="stSidebar"] {{background:#2d2d2d !important; color:#fff !important; font-family: 'Poppins', sans-serif;}}
            section[data-testid="stSidebar"] .stRadio, section[data-testid="stSidebar"] .stSelectbox, section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] label {{color:#fff !important}}
        .stDataFrame table {{background:transparent}}
        h1 {{font-size:34px; margin-bottom:6px; color:{text}; font-weight:700; font-family: 'Poppins', sans-serif}}
        h2 {{font-size:22px; color:{text}; font-weight:700; font-family: 'Poppins', sans-serif}}
        h3, p, label, .stTextInput>div>input {{font-size:16px; color:{text}; font-weight:700; font-family: 'Poppins', sans-serif}}
        .stAlert {{font-size:15px; font-weight:700; font-family: 'Poppins', sans-serif}}
        /* Sidebar text forced bold black for visibility */
        section[data-testid="stSidebar"] {{color:#fff !important; font-weight:700}}
        </style>
    """, unsafe_allow_html=True)

set_theme_css()

# --- Top bar: language, theme ---
with st.sidebar:
    st.radio('Theme', options=['light','dark'], index=0 if st.session_state['theme']=='light' else 1, key='theme', on_change=set_theme_css)
    lang_codes = list(TRANSLATIONS.keys())
    lang_labels = [LANGUAGE_NAMES.get(code, code) for code in lang_codes]
    selected_lang_idx = lang_codes.index(st.session_state['lang'])
    selected_lang = st.selectbox('Language', options=range(len(lang_codes)), format_func=lambda x: lang_labels[x], index=selected_lang_idx)
    st.session_state['lang'] = lang_codes[selected_lang]
    st.markdown('---')
    if st.session_state.get('page','auth')=='dashboard' and st.session_state['user']:
        st.write(f"Signed in: {st.session_state['user']}")
        if st.button(t('logout')):
            st.session_state['user'] = None
            st.session_state['page'] = 'auth'
            st.rerun()

    st.markdown('---')
    st.write('')

# --- Header ---
st.title(f"🩸 {t('title')}")
st.markdown(f"### {t('subtitle')}")

# initialize page state
if 'page' not in st.session_state:
    st.session_state['page'] = 'auth' if st.session_state.get('user') is None else 'dashboard'

def render_auth_page():
    st.markdown('<div style="max-width:700px;margin:40px auto;padding:28px;background:rgba(255,255,255,0.6);border-radius:12px;">', unsafe_allow_html=True)
    st.header('Welcome — please sign in')
    auth_mode = st.radio('Account', ['Login','Register'], horizontal=True)
    if auth_mode == 'Register':
        email = st.text_input(t('email'))
        name = st.text_input(t('name'))
        password = st.text_input(t('password'), type='password')
        confirm = st.text_input(t('confirm_password'), type='password')
        if st.button(t('register')):
            if not email or not password or password != confirm:
                st.error('Please fill fields and ensure passwords match')
            else:
                users = load_users()
                if email in users:
                    st.error('User already exists')
                else:
                    save_user(email, name, hash_password(password))
                    st.success('Registration successful. Please login.')
    else:
        email = st.text_input(t('email'))
        password = st.text_input(t('password'), type='password')
        if st.button(t('login')):
            if authenticate(email, password):
                st.session_state['user'] = email
                st.session_state['page'] = 'dashboard'
                st.rerun()
            else:
                st.error('Invalid credentials')
    st.markdown('</div>', unsafe_allow_html=True)

if st.session_state['page'] == 'auth' or st.session_state.get('user') is None:
    render_auth_page()
    st.stop()

# --- Auth Flow ---
col1, col2 = st.columns([1,2])
with col1:
    if st.session_state['user'] is None:
        auth_mode = st.radio('Account', ['Login','Register'])
    else:
        auth_mode = None
with col2:
    if st.session_state['user'] is None:
        if auth_mode == 'Register':
            email = st.text_input(t('email'))
            name = st.text_input(t('name'))
            password = st.text_input(t('password'), type='password')
            confirm = st.text_input(t('confirm_password'), type='password')
            if st.button(t('register')):
                if not email or not password or password != confirm:
                    st.error('Please fill fields and ensure passwords match')
                else:
                    users = load_users()
                    if email in users:
                        st.error('User already exists')
                    else:
                        save_user(email, name, hash_password(password))
                        st.success('Registration successful. Please login.')
        else:
            email = st.text_input(t('email'))
            password = st.text_input(t('password'), type='password')
            if st.button(t('login')):
                if authenticate(email, password):
                    st.session_state['user'] = email
                    st.success('Logged in')
                else:
                    st.error('Invalid credentials')
    else:
        st.success(f"Welcome back, {st.session_state['user']}")

st.markdown('---')

# --- Main App (requires login) ---
if st.session_state['user'] is None:
    st.info('Please register or login to continue')
    st.stop()

st.subheader('1. Sensor Input')

# Fitzpatrick skin type mapping with descriptions and colors
fitzpatrick_types = {
    1: {'label': 'Type I - Ivory', 'color': '#F3E4C1'},
    2: {'label': 'Type II - Pale or Fair', 'color': '#E7D7C3'},
    3: {'label': 'Type III - Fair to Beige', 'color': '#D4A574'},
    4: {'label': 'Type IV - Olive or Light Brown', 'color': '#A67C52'},
    5: {'label': 'Type V - Dark Brown', 'color': '#6C4C42'},
    6: {'label': 'Type VI - Deeply Pigmented', 'color': '#3D2817'}
}

col1, col2 = st.columns(2)
with col1:
    green = st.slider('Green Light Absorption (535nm)', 0.0, 25.0, 10.0, step=0.1)
    red = st.slider('Red Light Absorption (660nm)', 700.0, 1300.0, 1000.0, step=10.0)
    ir = st.slider('Infrared Absorption (940nm)', 5400.0, 6300.0, 5850.0, step=50.0)
with col2:
    # Create formatted options with color display
    skin_options = [f"{fitzpatrick_types[i]['label']}" for i in range(1, 7)]
    selected_idx = st.selectbox('Fitzpatrick Skin Type', options=range(6), format_func=lambda x: skin_options[x])
    skin_tone = selected_idx + 1
    
    # Display color swatch
    color_hex = fitzpatrick_types[skin_tone]['color']
    st.markdown(f"<div style='width:100%; height:60px; background-color:{color_hex}; border-radius:8px; border:2px solid white; margin-top:10px;'></div>", unsafe_allow_html=True)
    st.caption(f"Selected: {fitzpatrick_types[skin_tone]['label']}")

ratio_red_ir = red / ir if ir != 0 else 0
ratio_green_ir = green / ir if ir != 0 else 0

if st.button(t('run')):
    input_payload = {
        "input_data": {
            "columns": ["Green_535nm", "Red_660nm", "IR_940nm", "Ratio_Red_IR", "Ratio_Green_IR", "Fitzpatrick_Scale"],
            "index": [0],
            "data": [[green, red, ir, ratio_red_ir, ratio_green_ir, int(skin_tone)]]
        }
    }
    with st.spinner('Contacting cloud...'):
        try:
            headers = {'Content-Type':'application/json','Authorization':f'Bearer {API_KEY}','Accept':'application/json'}
            response = requests.post(ENDPOINT_URL, json=input_payload, headers=headers, timeout=30)
            if response.status_code == 200:
                r = response.json()
                hb_value = None
                # robust extraction
                if isinstance(r, dict):
                    for k in ('result','predictions'):
                        if k in r:
                            val = r[k]
                            if isinstance(val, list) and val:
                                hb_value = float(val[0])
                                break
                            else:
                                try:
                                    hb_value = float(val)
                                    break
                                except Exception:
                                    pass
                    if hb_value is None:
                        for v in r.values():
                            try:
                                if isinstance(v, list) and v:
                                    hb_value = float(v[0]); break
                                else:
                                    hb_value = float(v); break
                            except Exception:
                                continue
                elif isinstance(r, list) and r:
                    try:
                        hb_value = float(r[0])
                    except Exception:
                        hb_value = None
                else:
                    try:
                        hb_value = float(r)
                    except Exception:
                        hb_value = None

                if hb_value is None:
                    st.error('Cloud returned unexpected data')
                else:
                    append_prediction(st.session_state['user'], hb_value, green, red, ir, skin_tone)
                    st.markdown('---')
                    st.subheader('Result')
                    fig = go.Figure(go.Indicator(mode='gauge+number', value=hb_value, title={'text':'Hemoglobin (g/dL)'}, gauge={'axis':{'range':[0,20]},'bar':{'color':PALETTE['accent']}}))
                    st.plotly_chart(fig, width='stretch')
                    if hb_value < 12.0:
                        st.error(f'⚠️ ANEMIA: {hb_value:.1f} g/dL')
                    elif hb_value > 17.5:
                        st.warning(f'⚠️ HIGH: {hb_value:.1f} g/dL')
                    else:
                        st.success(f'✅ {hb_value:.1f} g/dL — within normal range')
            else:
                st.error(f'Cloud Error {response.status_code}')
        except Exception as e:
            st.error(f'Connection Failed: {e}')

# --- History & Visuals ---
st.markdown('---')
st.subheader(t('history'))
try:
    df = pd.read_csv(PREDICTIONS_CSV)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    user_df = df[df['email']==st.session_state['user']].sort_values('timestamp')
    if not user_df.empty:
        # metrics
        last = float(user_df['hb_value'].iloc[-1])
        avg = float(user_df['hb_value'].astype(float).mean())
        mn = float(user_df['hb_value'].astype(float).min())
        mx = float(user_df['hb_value'].astype(float).max())

        mcol1, mcol2, mcol3, mcol4 = st.columns(4)
        mcol1.metric('Latest (g/dL)', f"{last:.1f}")
        mcol2.metric('Average (g/dL)', f"{avg:.1f}")
        mcol3.metric('Minimum (g/dL)', f"{mn:.1f}")
        mcol4.metric('Maximum (g/dL)', f"{mx:.1f}")

        # date filter
        with st.expander('Filter & Table', expanded=True):
            col_a, col_b = st.columns([2,1])
            with col_a:
                start_date, end_date = st.date_input('Date range', [user_df['timestamp'].min().date(), user_df['timestamp'].max().date()])
            with col_b:
                rows = st.selectbox('Rows to show', options=[10,25,50,100], index=0)

            mask = (user_df['timestamp'].dt.date >= start_date) & (user_df['timestamp'].dt.date <= end_date)
            filtered = user_df.loc[mask].sort_values('timestamp', ascending=False)

            st.download_button('Download CSV', data=filtered.to_csv(index=False).encode('utf-8'), file_name='my_readings.csv')
            st.dataframe(filtered.head(rows), width='stretch')

        # charts
        st.markdown('### 📊 Hemoglobin Trend Analysis')
        st.markdown('*Track your hemoglobin levels over time and understand distribution patterns*')
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown('#### 📈 Hemoglobin Over Time')
            st.markdown('**Shows your hemoglobin level progression:** Rising trends indicate improving blood health, while declining trends may indicate anemia development.')
            fig2 = go.Figure()
            fig2.add_trace(go.Scatter(x=user_df['timestamp'], y=user_df['hb_value'].astype(float), mode='lines+markers', name='Hemoglobin Level', line=dict(color=PALETTE['accent'], width=3), marker=dict(size=8)))
            fig2.update_layout(
                title='Hemoglobin Concentration Timeline',
                yaxis_title='Hemoglobin Level (g/dL)',
                xaxis_title='Date & Time',
                template='plotly_dark',
                hovermode='x unified',
                plot_bgcolor='rgba(0,0,0,0.1)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12, color='#fff')
            )
            fig2.add_hline(y=12.0, line_dash="dash", line_color="red", annotation_text="Anemia Threshold (12 g/dL)", annotation_position="right")
            fig2.add_hline(y=17.5, line_dash="dash", line_color="orange", annotation_text="High Threshold (17.5 g/dL)", annotation_position="right")
            st.plotly_chart(fig2, width='stretch')
        with c2:
            st.markdown('#### 📊 Hemoglobin Distribution')
            st.markdown('**Shows frequency of hemoglobin readings:** Understand how your readings cluster around normal, anemic, or high ranges.')
            fig3 = go.Figure(go.Histogram(x=user_df['hb_value'].astype(float), nbinsx=10, marker_color=PALETTE['accent'], name='Frequency', showlegend=True))
            fig3.update_layout(
                title='Reading Distribution Pattern',
                xaxis_title='Hemoglobin Level (g/dL)',
                yaxis_title='Frequency (Count)',
                template='plotly_dark',
                plot_bgcolor='rgba(0,0,0,0.1)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(size=12, color='#fff'),
                hovermode='x'
            )
            st.plotly_chart(fig3, width='stretch')
        
        # Summary insights
        st.markdown('---')
        st.markdown('### 📋 Quick Health Insights')
        col_i1, col_i2, col_i3 = st.columns(3)
        with col_i1:
            trend = '📈 Improving' if user_df['hb_value'].astype(float).iloc[-1] > user_df['hb_value'].astype(float).iloc[0] else '📉 Declining'
            st.info(f'**Trend:** {trend}')
        with col_i2:
            status = '✅ Normal' if 12.0 <= last <= 17.5 else ('⚠️ Anemia' if last < 12.0 else '⚠️ High')
            st.warning(f'**Status:** {status}')
        with col_i3:
            variability = f'{(mx - mn):.2f} g/dL'
            st.info(f'**Range:** {variability}')

    else:
        st.info('No readings yet — run a diagnostic.')
except Exception as e:
    st.info('No history available yet.')

st.markdown('---')
st.caption('Local persistence: users.json / users.csv / predictions.csv')