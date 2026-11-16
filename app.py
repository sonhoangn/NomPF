import streamlit as st

# --- CONFIGURABLE MEDIA ASSETS ---
P_ICON = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/icon.png"
BG_IMAGE_URL = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/wbg.gif"
IMG_MEDAL = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/md.png"

# Configure page settings
st.set_page_config(
    page_title="Synergy Star 2026 - Winners",
    page_icon=P_ICON,
    layout="centered"
)

# --- MULTI-LANGUAGE DICTIONARY ---
TRANSLATIONS = {
    "Tiếng Việt (Vietnamese)": {
        "congrats_title": "Vinh Danh Top 3 Ngôi Sao Synergy Star 2026",
        "congrats_subtitle": "Xin chúc mừng các cá nhân xuất sắc nhất đã đạt giải thưởng cao nhất trong mùa giải năm nay!",
        "admin_sec": "Quản Trị Viên (Xem & Tải Dữ Liệu)",
        "admin_pass_label": "Nhập mật khẩu quản trị",
        "admin_success": "Xác thực thành công!",
        "err_pass": "Mật khẩu không chính xác!"
    },
    "English": {
        "congrats_title": "Celebrating the Top 3 Synergy Star 2026 Winners",
        "congrats_subtitle": "Congratulations to our outstanding finalists for achieving the highest honors this season!",
        "admin_sec": "Administrator (View & Download Data)",
        "admin_pass_label": "Enter admin password",
        "admin_success": "Authentication successful!",
        "err_pass": "Incorrect password!"
    },
    "Deutsch (German)": {
        "congrats_title": "Feier der Top 3 Synergy Star 2026 Gewinner",
        "congrats_subtitle": "Herzlichen Glückwunsch an unsere herausragenden Finalisten für die höchsten Auszeichnungen in dieser Saison!",
        "admin_sec": "Administrator (Daten anzeigen & herunterladen)",
        "admin_pass_label": "Admin-Passwort eingeben",
        "admin_success": "Authentifizierung erfolgreich!",
        "err_pass": "Falsches Passwort!"
    }
}

# Sidebar Language Selector
selected_lang_key = st.sidebar.selectbox("🌐 Language / Ngôn ngữ / Sprache", list(TRANSLATIONS.keys()))
t = TRANSLATIONS[selected_lang_key]

# Determine bio suffix based on selected language
if selected_lang_key == "Tiếng Việt (Vietnamese)":
    bio_suffix = "_V"
elif selected_lang_key == "Deutsch (German)":
    bio_suffix = "_D"
else:
    bio_suffix = "_E"

# --- TOP 3 WINNERS CONFIGURATION FROM SECRETS ---
TOP_3_WINNERS = [
    {
        "name": st.secrets.get("P2_NAME_1"),
        "department": st.secrets.get("P2_DEPT_1"),
        "image": "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f1.png",
        "bio": st.secrets.get(f"P2_BIO_1{bio_suffix}")
    },
    {
        "name": st.secrets.get("P2_NAME_6"),
        "department": st.secrets.get("P2_DEPT_6"),
        "image": "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f6.png",
        "bio": st.secrets.get(f"P2_BIO_6{bio_suffix}")
    },
    {
        "name": st.secrets.get("P2_NAME_10"),
        "department": st.secrets.get("P2_DEPT_10"),
        "image": "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f10.png",
        "bio": st.secrets.get(f"P2_BIO_10{bio_suffix}")
    }
]

# --- GLASSMORPHISM & SOLID BACKGROUND STYLING ---
if BG_IMAGE_URL:
    st.markdown(f"""
        <style>        
        @font-face {{
            font-family: 'TitleCondOfcVI';
            src: url('app/static/MBCorpoATitleCondOfcVI-Regular 2.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}

        @font-face {{
            font-family: 'TitleOfcVI';
            src: url('app/static/MBCorpoATitleOfcVI-Regular 2.ttf') format('truetype');
            font-weight: normal;
            font-style: normal;
        }}

        html, body, [class*="css"] {{
            font-family: 'TitleCondOfcVI' !important;
        }}

        h1, h2, h3 {{
            font-family: 'TitleCondOfcVI' !important;
            font-weight: normal;
        }}
        .stApp {{
            background-image: url("{BG_IMAGE_URL}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        .main .block-container {{
            background: transparent !important;
            padding: 2.5rem;
        }}

        .golden-title-card {{
            background: rgba(42, 35, 15, 0.6);
            -webkit-backdrop-filter: blur(5px);
            backdrop-filter: blur(5px);
            border: 1px solid rgba(245, 158, 11, 0.2) !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 32px 0 rgba(245, 158, 11, 0.5) !important;
            padding: 1.5rem 2rem;
            margin-bottom: 2rem;
            text-align: center;
        }}

        .golden-glow-text {{
            color: #FDE047 !important;
            text-shadow: 0 0 10px rgba(245, 158, 11, 0.8), 
                         0 0 20px rgba(217, 119, 6, 0.6), 
                         0 0 30px rgba(180, 83, 9, 0.4);
            margin-bottom: 0.5rem;
            font-family: 'TitleCondOfcVI' !important;
            font-size: 1.8rem !important;
            font-weight: 650;
        }}

        div[data-testid="stExpander"], 
        div[data-testid="stForm"] {{
            background-color: rgba(42, 35, 15, 0.6) !important;
            -webkit-backdrop-filter: blur(5px) !important;
            backdrop-filter: blur(5px) !important;
            border: 1px solid rgba(245, 158, 11, 0.3) !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 32px 0 rgba(245, 158, 11, 0.5) !important;
            padding: 2rem !important;
            margin-bottom: 1.5rem !important;
            font-family: 'TitleCondOfcVI' !important;
            font-weight: normal;
        }}

        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea,
        div[data-testid="stSelectbox"] div[data-baseweb="select"] > div {{
            background-color: rgba(42, 35, 15, 0.6) !important;
            color: rgba(245, 158, 11, 0.95) !important;
            border-radius: 8px !important;
            border: 1px solid rgba(245, 158, 11, 0.2) !important;
            font-family: 'TitleCondOfcVI' !important;
            font-weight: normal;
            font-size: 1.2rem !important;
        }}

        div[data-testid="stForm"] button, 
        button[data-testid="baseButton-secondary"],
        button[data-testid="baseButton-primary"] {{
            background-color: rgba(28, 24, 15, 0.75) !important;
            color: #db9f16 !important;
            border: 1px solid rgba(219, 159, 22, 0.15) !important;
            border-radius: 8px !important;
            box-shadow: 0 2px 8px 0 rgba(245, 158, 11, 0.15) !important;
            font-family: 'TitleCondOfcVI' !important;
            font-weight: normal;
            font-size: 1.2rem !important;
        }}

        label, .stSubheader, h1, h2, h3 {{
            color: rgba(247, 198, 87, 1) !important;
        }}
        .stCaption, p {{
            color: rgba(247, 198, 87, 0.95) !important;
            font-size: 1.2rem !important;
        }}
        </style>
        """, unsafe_allow_html=True)

# Header display banner (Winners Celebration Title)
header_title_text = t['congrats_title']
st.markdown(f"""
    <div class="golden-title-card">
        <h1 class="golden-glow-text" style="font-family: 'TitleCondOfcVI' !important; width: 100%; text-align: center; margin: 0 auto; white-space: pre-line;">{header_title_text}</h1>
        <p style="color: #F7C657; font-size: 1.15rem; margin-top: 0.5rem; text-align: center;">{t['congrats_subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# CONGRATULATIONS PAGE FOR Synergy Star WinnerS
# ==========================================
for idx, winner in enumerate(TOP_3_WINNERS):
    name = winner["name"]
    dept = winner["department"]
    img = winner["image"]
    bio = winner["bio"]

    card_bg = "rgba(60, 45, 15, 0.85)"
    card_border = "2px solid #FDE047"
    card_shadow = "0 0 25px rgba(245, 158, 11, 0.7)"

    medal_html = f'<img src="{IMG_MEDAL}" style="position: absolute; top: 15px; right: 15px; width: 60px; height: 60px; filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.9)); z-index: 10;" />'

    winner_card_html = (
        f'<div style="position: relative; background: {card_bg}; border: {card_border}; border-radius: 14px; padding: 1.5rem; margin-bottom: 1.5rem; box-shadow: {card_shadow};">'
        f'{medal_html}'
        f'<div style="display: flex; gap: 1.5rem; align-items: flex-start; flex-wrap: wrap;">'
        f'<div style="flex: 0 0 160px; text-align: center;">'
        f'<img src="{img}" alt="Winner Photo" style="width: 160px; height: 200px; aspect-ratio: 4 / 5; border-radius: 8px; object-fit: cover; border: 2px solid #F59E0B; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);" />'
        f'<div style="margin-top: 0.5rem; font-weight: bold; color: #FDE047; font-size: 1rem;">Synergy Star #{idx + 1}</div>'
        f'</div>'
        f'<div style="flex: 1; min-width: 220px;">'
        f'<h3 style="color: #FDE047; margin-bottom: 0.2rem; font-size: 1.6rem;">{name}</h3>'
        f'<p style="color: #F7C657; font-size: 1.05rem; font-style: italic; margin-bottom: 0.8rem;">{dept}</p>'
        f'<h4 style="color: #FDE047; font-size: 1.15rem; margin-bottom: 0.4rem; border-bottom: 1px solid rgba(245, 158, 11, 0.3); padding-bottom: 0.2rem;">Achievement Summary</h4>'
        f'<p style="color: #FFF; font-size: 1.05rem; line-height: 1.6;">{bio}</p>'
        f'</div>'
        f'</div>'
        f'</div>'
    )

    st.markdown(winner_card_html, unsafe_allow_html=True)
