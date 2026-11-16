import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import io
import uuid
import altair as alt

# --- REPORTLAB PDF GENERATION IMPORTS ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- CONFIGURABLE MEDIA ASSETS ---
LOGO_URL = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/icon.png"
P_ICON = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/icon.png"
BG_IMAGE_URL = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/bg.gif"
IMG_WELCOME = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/wbg.gif"
IMG_THANKYOU = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/wbg.gif"
IMG_COLLAB = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/cl1.png"
IMG_INNOV = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/in1.png"
IMG_CULTURE = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/cv1.png"
IMG_ACC = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/ac1.png"
IMG_MEDAL = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/md.png"
IMG_F1 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f1.png"
IMG_F2 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f2.png"
IMG_F3 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f3.png"
IMG_F4 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f4.png"
IMG_F5 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f5.png"
IMG_F6 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f6.png"
IMG_F7 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f7.png"
IMG_F8 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f8.png"
IMG_F9 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f9.png"
IMG_F10 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f10.png"
IMG_F11 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f11.png"
IMG_F12 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f12.png"
IMG_F13 = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/f13.png"

# Configure page settings
st.set_page_config(
    page_title="Synergy Star 2026",
    page_icon=P_ICON,
    layout="centered"
)

# --- LOAD ADMIN PASSWORD ---
AD_PASS = st.secrets.get("AD_PASS", "MO-LQN")


# --- HELPER FUNCTION TO PARSE SECRETS INTO LISTS ---
def parse_secret_list(secret_val):
    if not secret_val or secret_val == "---":
        return []
    if isinstance(secret_val, list):
        return [str(item).strip() for item in secret_val if str(item).strip()]
    return [name.strip() for name in str(secret_val).split(",") if name.strip()]


# --- LOAD DEPT NAME LISTs FROM SECRETS ---
EN = parse_secret_list(st.secrets.get("EN", ""))
PB = parse_secret_list(st.secrets.get("PB", ""))
PEDC = parse_secret_list(st.secrets.get("PEDC", ""))
PBP = parse_secret_list(st.secrets.get("PBP", ""))
LG = parse_secret_list(st.secrets.get("LG", ""))
PA = parse_secret_list(st.secrets.get("PA", ""))
PP = parse_secret_list(st.secrets.get("PP", ""))
QM = parse_secret_list(st.secrets.get("QM", ""))

# --- DEPARTMENT & PLACEHOLDER NAMES MAPPING ---
DEPARTMENT_NAMES = {
    "Engineering": EN,
    "Production - Bodyshop": PB,
    "Production - ED Coating": PEDC,
    "Production - Bodyshop & Paintshop": PBP,
    "Logistics": LG,
    "Production - Assembly": PA,
    "Production - Paintshop": PP,
    "Quality Management": QM
}

# --- MULTI-LANGUAGE DICTIONARY ---
TRANSLATIONS = {
    "Tiếng Việt (Vietnamese)": {
        "p2_title": "Vòng Bình Chọn Chung Kết (Phase 2)",
        "p2_welcome_heading": "Chào Mừng Đến Vòng Bình Chọn Top 3",
        "p2_welcome_desc": "Hãy cuộn xuống bên dưới để xem thông tin chi tiết và lựa chọn đúng **3 ứng viên** xuất sắc nhất mà bạn muốn bình chọn.",
        "p2_instruction_banner": "Vui lòng cuộn xuống để xem hồ sơ các ứng viên và chọn đúng 3 ứng viên bạn muốn bình chọn.",
        "p2_start_btn": "Bắt Đầu Bình Chọn",
        "p2_selected_count": "Đã chọn: {} / 3 ứng viên",
        "p2_submit_btn": "Xác Nhận & Gửi Bình Chọn (3 Ứng Viên)",
        "p2_thank_you_title": "Cảm Ơn Bạn Đã Bình Chọn!",
        "p2_thank_you_msg": "Lựa chọn của bạn cho vòng chung kết đã được ghi nhận thành công.",
        "p2_locked_title": "Bạn Đã Hoàn Thành Bình Chọn",
        "p2_locked_msg": "Thiết bị này đã tham gia bình chọn vòng chung kết trước đó. Xin cảm ơn sự tham gia của bạn!",
        "p2_selection": "Chọn ứng viên này",
        "p2_selected": "Ứng viên đã được chọn!",
        "p2_confirm_nomination": "Bạn đã bình chọn các ứng viên sau",
        "highlights_title": "Những điểm sáng",

        "portal_closed_title": "Cổng Đề Cử Hiện Đang Tạm Đóng",
        "portal_closed_msg": "Cổng tiếp nhận đề cử và bình chọn hiện đang tạm thời đóng bởi Quản trị viên. Vui lòng quay lại sau!",

        "admin_sec": "Quản Trị Viên (Xem & Tải Dữ Liệu)",
        "admin_pass_label": "Nhập mật khẩu quản trị",
        "admin_success": "Xác thực thành công!",
        "download_btn": "Tải Bảng Dữ Liệu Gốc (CSV)",
        "download_pdf_btn": "Tải Báo Cáo PDF Dashboard",
        "download_html_btn": "Tải Báo Cáo Phase 1 HTML Comprehensive",
        "summary_table_title": "Bảng Tổng Hợp Số Lượt Đề Cử & Điểm Trung Bình:",
        "raw_table_title": "Bảng Dữ Liệu Gốc Các Đề Cử:",
        "chart_votes_title": "Top 10 Đề Cử Nhiều Nhất (Nhiều Lượt Bình Chọn Nhất)",
        "leaderboard_title": "Bảng Xếp Hạng (Top 10 Đề Cử Hàng Đầu)",
        "err_pass": "Mật khẩu không chính xác!"
    },
    "English": {
        "p2_title": "Finals Voting Portal (Phase 2)",
        "p2_welcome_heading": "Welcome to the Finals Voting",
        "p2_welcome_desc": "Please scroll down the page to explore the profiles and select exactly **3 finalists** you wish to nominate.",
        "p2_instruction_banner": "Please scroll down to review finalist profiles and select exactly 3 candidates for your final vote.",
        "p2_start_btn": "Start Voting",
        "p2_selected_count": "Selected: {} / 3 candidates",
        "p2_submit_btn": "Confirm & Submit Vote (3 Candidates)",
        "p2_thank_you_title": "Thank You for Voting!",
        "p2_thank_you_msg": "Your final vote has been successfully recorded.",
        "p2_locked_title": "Vote Already Submitted",
        "p2_locked_msg": "A vote has already been submitted from this device for Phase 2. Thank you for your participation!",
        "p2_selection": "Select this candidate",
        "p2_selected": "This candidate has been selected!",
        "p2_confirm_nomination": "You have selected the following candidates",
        "highlights_title": "Highlights",

        "portal_closed_title": "Nomination Portal Temporarily Closed",
        "portal_closed_msg": "The nomination and voting portal is currently closed by the administrator. Please check back later!",

        "admin_sec": "Administrator (View & Download Data)",
        "admin_pass_label": "Enter admin password",
        "admin_success": "Authentication successful!",
        "download_btn": "Download Raw Data (CSV)",
        "download_pdf_btn": "Download Dashboard PDF Report",
        "download_html_btn": "Download Phase 1 HTML Comprehensive Report",
        "summary_table_title": "Summary Table of Total Votes & Average Scores:",
        "raw_table_title": "Raw Nominations Table:",
        "chart_votes_title": "Most Voted Nominees",
        "leaderboard_title": "Leaderboard (Nominees)",
        "err_pass": "Incorrect password!"
    },
    "Deutsch (German)": {
        "p2_title": "Finalabstimmungsportal (Phase 2)",
        "p2_welcome_heading": "Willkommen zur Finalabstimmung",
        "p2_welcome_desc": "Bitte scrollen Sie nach unten, um die Profile zu erkunden und genau **3 Finalisten** für Ihre Stimme auszuwählen.",
        "p2_instruction_banner": "Bitte scrollen Sie nach unten, um die Finalisten-Profile zu überprüfen und genau 3 Kandidaten auszuwählen.",
        "p2_start_btn": "Abstimmung Starten",
        "p2_selected_count": "Ausgewählt: {} / 3 Kandidaten",
        "p2_submit_btn": "Stimme Bestätigen & Absenden (3 Kandidaten)",
        "p2_thank_you_title": "Vielen Dank für Ihre Stimme!",
        "p2_thank_you_msg": "Ihre Finalstimme wurde erfolgreich erfasst.",
        "p2_locked_title": "Stimme Bereits Abgeschlossen",
        "p2_locked_msg": "Von diesem Gerät wurde bereits eine Stimme für Phase 2 abgegeben.",
        "p2_selection": "Diesen Kandidaten auswählen?",
        "p2_selected": "Dieser/-e Kandidat/-in wurde ausgewählt!",
        "p2_confirm_nomination": "Sie haben diese Kandidaten ausgewählt",
        "highlights_title": "Höhepunkte",

        "portal_closed_title": "Nominierungsportal Vorübergehend Geschlossen",
        "portal_closed_msg": "Das Nominierungs- und Abstimmungsportal wurde vom Administrator vorübergehend geschlossen. Bitte versuchen Sie es später noch einmal!",

        "admin_sec": "Administrator (Daten anzeigen & herunterladen)",
        "admin_pass_label": "Admin-Passwort eingeben",
        "admin_success": "Authentifizierung erfolgreich!",
        "download_btn": "Rohdaten herunterladen (CSV)",
        "download_pdf_btn": "Dashboard PDF-Bericht herunterladen",
        "download_html_btn": "Phase 1 HTML-Bericht herunterladen",
        "summary_table_title": "Zusammenfassung der Stimmen & Durchschnittswerte:",
        "raw_table_title": "Rohdaten-Tabelle der Nominierungen:",
        "chart_votes_title": "Nominierte nach Stimmen",
        "leaderboard_title": "Bestenliste",
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

# --- PHASE 2 FINALISTS CONFIGURATION WITH MULTI-LANGUAGE BIOS ---
TOP_10_FINALISTS = [
    {
        "name": st.secrets.get("P2_NAME_1"),
        "department": st.secrets.get("P2_DEPT_1"),
        "bio": st.secrets.get(f"P2_BIO_1{bio_suffix}", st.secrets.get("P2_BIO_1", "")),
        "image": IMG_F1
    },
    {
        "name": st.secrets.get("P2_NAME_2"),
        "department": st.secrets.get("P2_DEPT_2"),
        "bio": st.secrets.get(f"P2_BIO_2{bio_suffix}", st.secrets.get("P2_BIO_2", "")),
        "image": IMG_F2
    },
    {
        "name": st.secrets.get("P2_NAME_3"),
        "department": st.secrets.get("P2_DEPT_3"),
        "bio": st.secrets.get(f"P2_BIO_3{bio_suffix}", st.secrets.get("P2_BIO_3", "")),
        "image": IMG_F3
    },
    {
        "name": st.secrets.get("P2_NAME_4"),
        "department": st.secrets.get("P2_DEPT_4"),
        "bio": st.secrets.get(f"P2_BIO_4{bio_suffix}", st.secrets.get("P2_BIO_4", "")),
        "image": IMG_F4
    },
    {
        "name": st.secrets.get("P2_NAME_5"),
        "department": st.secrets.get("P2_DEPT_5"),
        "bio": st.secrets.get(f"P2_BIO_5{bio_suffix}", st.secrets.get("P2_BIO_5", "")),
        "image": IMG_F5
    },
    {
        "name": st.secrets.get("P2_NAME_6"),
        "department": st.secrets.get("P2_DEPT_6"),
        "bio": st.secrets.get(f"P2_BIO_6{bio_suffix}", st.secrets.get("P2_BIO_6", "")),
        "image": IMG_F6
    },
    {
        "name": st.secrets.get("P2_NAME_7"),
        "department": st.secrets.get("P2_DEPT_7"),
        "bio": st.secrets.get(f"P2_BIO_7{bio_suffix}", st.secrets.get("P2_BIO_7", "")),
        "image": IMG_F7
    },
    {
        "name": st.secrets.get("P2_NAME_8"),
        "department": st.secrets.get("P2_DEPT_8"),
        "bio": st.secrets.get(f"P2_BIO_8{bio_suffix}", st.secrets.get("P2_BIO_8", "")),
        "image": IMG_F8
    },
    {
        "name": st.secrets.get("P2_NAME_9"),
        "department": st.secrets.get("P2_DEPT_9"),
        "bio": st.secrets.get(f"P2_BIO_9{bio_suffix}", st.secrets.get("P2_BIO_9", "")),
        "image": IMG_F9
    },
    {
        "name": st.secrets.get("P2_NAME_10"),
        "department": st.secrets.get("P2_DEPT_10"),
        "bio": st.secrets.get(f"P2_BIO_10{bio_suffix}", st.secrets.get("P2_BIO_10", "")),
        "image": IMG_F10
    },
    {
        "name": st.secrets.get("P2_NAME_11"),
        "department": st.secrets.get("P2_DEPT_11"),
        "bio": st.secrets.get(f"P2_BIO_11{bio_suffix}", st.secrets.get("P2_BIO_11", "")),
        "image": IMG_F11
    },
    {
        "name": st.secrets.get("P2_NAME_12"),
        "department": st.secrets.get("P2_DEPT_12"),
        "bio": st.secrets.get(f"P2_BIO_12{bio_suffix}", st.secrets.get("P2_BIO_12", "")),
        "image": IMG_F12
    },
    {
        "name": st.secrets.get("P2_NAME_13"),
        "department": st.secrets.get("P2_DEPT_13"),
        "bio": st.secrets.get(f"P2_BIO_13{bio_suffix}", st.secrets.get("P2_BIO_13", "")),
        "image": IMG_F13
    }
]

# Filter out unconfigured finalists
TOP_10_FINALISTS = [f for f in TOP_10_FINALISTS if f["name"]]

# --- DEVICE TRACKING & PERSISTENCE FILES ---
DATA_FILE = "danh_sach_de_cu.csv"
DEVICE_REGISTRY_FILE = "device_registry.json"

# Phase 2 Persistence files
DATA_FILE_P2 = "danh_sach_de_cu_phase2.csv"
DEVICE_REGISTRY_FILE_P2 = "device_registry_phase2.json"
PORTAL_STATE_FILE = "portal_state.json"


def load_json_state(filename, default_val):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_val
    return default_val


def save_json_state(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


# Portal Closed state from persistent files
portal_data = load_json_state(PORTAL_STATE_FILE, {"portal_closed": False})
PORTAL_CLOSED = portal_data.get("portal_closed", False)


def load_device_registry(registry_file):
    if os.path.exists(registry_file):
        try:
            with open(registry_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_device_registry(registry_file, registry_list):
    with open(registry_file, "w", encoding="utf-8") as f:
        json.dump(registry_list, f, ensure_ascii=False, indent=4)


# Assign or retrieve unique device token via URL query params & session state
if "device_token" not in st.session_state:
    query_params = st.query_params
    if "did" in query_params:
        st.session_state["device_token"] = query_params["did"]
    else:
        new_token = str(uuid.uuid4())
        st.session_state["device_token"] = new_token
        st.query_params["did"] = new_token

DEVICE_ID = st.session_state["device_token"]

# --- SESSION STATE INITIALIZATION (PHASE 2 LOCKED) ---
if "p2_step" not in st.session_state:
    st.session_state["p2_step"] = 0

if "p2_selected_nominees" not in st.session_state:
    st.session_state["p2_selected_nominees"] = []

# Check device submission lock for Phase 2
registered_devices_p2 = load_device_registry(DEVICE_REGISTRY_FILE_P2)
if DEVICE_ID in registered_devices_p2 and st.session_state["p2_step"] not in [2]:
    st.session_state["p2_step"] = 2


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

        div[data-testid="stForm"] button:hover, 
        button[data-testid="baseButton-secondary"]:hover,
        button[data-testid="baseButton-primary"]:hover {{
            background-color: rgba(28, 24, 15, 0.75) !important;
            border-color: rgba(219, 159, 22, 0.2) !important;
            box-shadow: 0 4px 16px 0 rgba(245, 158, 11, 0.30) !important;
            color: #db9f16 !important;
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


def init_data_files():
    expected_columns_p2 = [
        "Thời Gian",
        "Tên Ứng Viên",
        "Phòng Ban",
        "Device_ID"
    ]
    if not os.path.exists(DATA_FILE_P2):
        df_p2 = pd.DataFrame(columns=expected_columns_p2)
        df_p2.to_csv(DATA_FILE_P2, index=False, encoding='utf-8-sig')


init_data_files()


def generate_pdf_report(summary_df, leaderboard_df, raw_df):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=25, leftMargin=25, topMargin=30, bottomMargin=30)
    story = []

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ReportTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=colors.HexColor('#B45309'),
        alignment=1,
        spaceAfter=10
    )
    heading_style = ParagraphStyle(
        'ReportHeading',
        parent=styles['Heading2'],
        fontSize=11,
        textColor=colors.HexColor('#92400E'),
        spaceBefore=10,
        spaceAfter=4
    )
    normal_style = ParagraphStyle(
        'ReportNormal',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#1F2937')
    )
    cell_style = ParagraphStyle(
        'ReportCell',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        textColor=colors.HexColor('#1F2937')
    )
    header_cell_style = ParagraphStyle(
        'ReportHeaderCell',
        parent=styles['Normal'],
        fontSize=7,
        leading=9,
        fontName='Helvetica-Bold',
        textColor=colors.whitesmoke
    )

    story.append(Paragraph("Synergy Star 2026 - Admin Dashboard Report", title_style))
    story.append(
        Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Submissions: {len(raw_df)}",
                  normal_style))
    story.append(Spacer(1, 8))

    def create_wrapped_table(df_subset, col_widths=None):
        headers = list(df_subset.columns)
        table_data = [[Paragraph(str(h), header_cell_style) for h in headers]]

        for _, row in df_subset.iterrows():
            row_cells = [Paragraph(str(val), cell_style) for val in row.values]
            table_data.append(row_cells)

        t = Table(table_data, colWidths=col_widths, hAlign='LEFT')
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#F59E0B')),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#FEF3C7')),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#D97706'))
        ]))
        return t

    story.append(Paragraph("Top 10 Leaderboard (Votes & Average Scores)", heading_style))
    lb_pdf = leaderboard_df.rename(columns={
        "Tên Người Được Đề Cử": "Nominee Name",
        "Số_Lượt_Đề_Cử": "Total Votes",
        "Điểm_Trung_Bình_Tổng_Thể": "Overall Avg Score"
    }).copy()
    story.append(create_wrapped_table(lb_pdf, col_widths=[250, 150, 160]))
    story.append(Spacer(1, 8))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def generate_phase1_html_report(raw_df, achievement_summaries=None):
    if achievement_summaries is None:
        achievement_summaries = {}

    if raw_df.empty or "Tên Người Được Đề Cử" not in raw_df.columns:
        return "<html><body><h1>No Data Available to Generate Report</h1></body></html>"

    group_cols = ["Tên Người Được Đề Cử", "Phòng Ban"]
    numeric_cols = ["Điểm Trung Bình", "Điểm Hợp Tác", "Điểm Đổi Mới", "Điểm Văn Hóa & Giá Trị", "Điểm Trách Nhiệm"]

    for col in numeric_cols:
        if col in raw_df.columns:
            raw_df[col] = pd.to_numeric(raw_df[col], errors='coerce')

    aggregated = raw_df.groupby(group_cols).agg(
        Total_Votes=("Điểm Trung Bình", "count"),
        Avg_Overall=("Điểm Trung Bình", "mean"),
        Avg_Collab=("Điểm Hợp Tác", "mean"),
        Avg_Innov=("Điểm Đổi Mới", "mean"),
        Avg_Culture=("Điểm Văn Hóa & Giá Trị", "mean"),
        Avg_Acc=("Điểm Trách Nhiệm", "mean")
    ).reset_index()

    aggregated = aggregated.sort_values(by=["Total_Votes", "Avg_Overall"], ascending=[False, False])
    top_10 = aggregated.head(10).copy()

    vote_distribution = raw_df["Tên Người Được Đề Cử"].value_counts()
    chart_labels = json.dumps(list(vote_distribution.index.astype(str)))
    chart_data = json.dumps(list(vote_distribution.values.astype(int)))

    infocards_html = ""
    for idx, row in top_10.reset_index(drop=True).iterrows():
        name = str(row["Tên Người Được Đề Cử"])
        dept = str(row["Phòng Ban"])
        votes = int(row["Total_Votes"])
        avg_overall = round(float(row["Avg_Overall"]), 2) if pd.notnull(row["Avg_Overall"]) else 0.0
        avg_collab = round(float(row["Avg_Collab"]), 2) if pd.notnull(row["Avg_Collab"]) else 0.0
        avg_innov = round(float(row["Avg_Innov"]), 2) if pd.notnull(row["Avg_Innov"]) else 0.0
        avg_culture = round(float(row["Avg_Culture"]), 2) if pd.notnull(row["Avg_Culture"]) else 0.0
        avg_acc = round(float(row["Avg_Acc"]), 2) if pd.notnull(row["Avg_Acc"]) else 0.0

        summary_text = achievement_summaries.get(name,
                                                 "Consistently demonstrated exceptional commitment, cross-departmental collaboration, and leadership excellence during Phase 1.")

        infocards_html += f"""
        <div class="infocard">
            <div class="card-header">
                <div class="rank-badge">#{idx + 1}</div>
                <div class="nominee-info">
                    <h3 class="nominee-name">{name}</h3>
                    <span class="department-tag">{dept}</span>
                </div>
                <div class="score-pill">
                    <span class="score-val">{avg_overall}</span>
                    <span class="score-lbl">Avg Point</span>
                </div>
            </div>

            <div class="votes-banner">
                <i class="fas fa-vote-yea"></i> Total Nominations: <strong>{votes} votes</strong>
            </div>

            <div class="scores-grid">
                <div class="score-item">
                    <span class="cat-name">Collaboration</span>
                    <div class="bar-bg"><div class="bar-fill collab" style="width: {(avg_collab / 5.0) * 100}%;"></div></div>
                    <span class="cat-score">{avg_collab} / 5</span>
                </div>
                <div class="score-item">
                    <span class="cat-name">Innovation</span>
                    <div class="bar-bg"><div class="bar-fill innov" style="width: {(avg_innov / 5.0) * 100}%;"></div></div>
                    <span class="cat-score">{avg_innov} / 5</span>
                </div>
                <div class="score-item">
                    <span class="cat-name">Culture & Value</span>
                    <div class="bar-bg"><div class="bar-fill culture" style="width: {(avg_culture / 5.0) * 100}%;"></div></div>
                    <span class="cat-score">{avg_culture} / 5</span>
                </div>
                <div class="score-item">
                    <span class="cat-name">Accountability</span>
                    <div class="bar-bg"><div class="bar-fill acc" style="width: {(avg_acc / 5.0) * 100}%;"></div></div>
                    <span class="cat-score">{avg_acc} / 5</span>
                </div>
            </div>

            <div class="achievement-section">
                <h4><i class="fas fa-award"></i> Achievement Summary</h4>
                <div class="achievement-body" contenteditable="true" title="Click to edit manually">{summary_text}</div>
            </div>
        </div>
        """

    html_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Synergy Star 2026 - Phase 1 Comprehensive Report</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        :root {{
            --bg-gradient: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #172554 100%);
            --card-bg: rgba(30, 41, 59, 0.75);
            --card-border: rgba(245, 158, 11, 0.3);
            --accent-gold: #f59e0b;
            --accent-yellow: #fde047;
            --text-main: #f8fafc;
            --text-muted: #94a3b8;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', sans-serif; }}
        body {{ background: var(--bg-gradient); color: var(--text-main); min-height: 100vh; padding: 2rem; }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .report-header {{ text-align: center; padding: 2.5rem 1rem; background: rgba(15, 23, 42, 0.6); border: 1px solid var(--card-border); border-radius: 20px; backdrop-filter: blur(10px); margin-bottom: 2rem; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }}
        .report-header h1 {{ font-size: 2.5rem; color: var(--accent-yellow); text-transform: uppercase; letter-spacing: 2px; text-shadow: 0 0 15px rgba(245, 158, 11, 0.5); margin-bottom: 0.5rem; }}
        .report-header p {{ color: var(--text-muted); font-size: 1.1rem; }}
        .section-title {{ font-size: 1.6rem; color: var(--accent-gold); margin-bottom: 1.5rem; display: flex; align-items: center; gap: 0.5rem; border-bottom: 2px solid var(--card-border); padding-bottom: 0.5rem; }}
        .chart-card {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 2rem; margin-bottom: 3rem; backdrop-filter: blur(10px); box-shadow: 0 8px 25px rgba(0,0,0,0.3); display: flex; flex-direction: column; align-items: center; }}
        .chart-container {{ position: relative; width: 100%; max-width: 550px; height: 380px; }}
        .grid-cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(340px, 1fr)); gap: 1.5rem; }}
        .infocard {{ background: var(--card-bg); border: 1px solid var(--card-border); border-radius: 16px; padding: 1.5rem; backdrop-filter: blur(8px); box-shadow: 0 6px 20px rgba(0,0,0,0.25); display: flex; flex-direction: column; }}
        .card-header {{ display: flex; align-items: center; gap: 1rem; margin-bottom: 1rem; }}
        .rank-badge {{ background: linear-gradient(135deg, #f59e0b, #b45309); color: #fff; font-weight: bold; font-size: 1.1rem; width: 42px; height: 42px; border-radius: 50%; display: flex; align-items: center; justify-content: center; }}
        .nominee-info {{ flex: 1; }}
        .nominee-name {{ font-size: 1.25rem; color: var(--accent-yellow); margin-bottom: 0.2rem; }}
        .department-tag {{ font-size: 0.85rem; color: var(--text-muted); background: rgba(255,255,255,0.08); padding: 0.2rem 0.6rem; border-radius: 12px; }}
        .score-pill {{ text-align: right; background: rgba(245, 158, 11, 0.15); border: 1px solid rgba(245, 158, 11, 0.4); padding: 0.4rem 0.8rem; border-radius: 12px; }}
        .score-val {{ display: block; font-size: 1.3rem; font-weight: bold; color: var(--accent-yellow); }}
        .score-lbl {{ font-size: 0.7rem; color: var(--text-muted); text-transform: uppercase; }}
        .votes-banner {{ background: rgba(59, 130, 246, 0.15); border: 1px solid rgba(59, 130, 246, 0.3); color: #93c5fd; padding: 0.5rem 0.8rem; border-radius: 8px; font-size: 0.9rem; margin-bottom: 1.2rem; }}
        .scores-grid {{ display: flex; flex-direction: column; gap: 0.6rem; margin-bottom: 1.2rem; }}
        .score-item {{ display: grid; grid-template-columns: 110px 1fr 45px; align-items: center; gap: 0.5rem; font-size: 0.85rem; }}
        .cat-name {{ color: var(--text-muted); }}
        .bar-bg {{ background: rgba(255, 255, 255, 0.1); height: 8px; border-radius: 4px; overflow: hidden; }}
        .bar-fill {{ height: 100%; border-radius: 4px; }}
        .bar-fill.collab {{ background: #3b82f6; }}
        .bar-fill.innov {{ background: #10b981; }}
        .bar-fill.culture {{ background: #ec4899; }}
        .bar-fill.acc {{ background: #f59e0b; }}
        .cat-score {{ text-align: right; font-weight: bold; color: var(--text-main); }}
        .achievement-section {{ margin-top: auto; border-top: 1px solid rgba(255, 255, 255, 0.1); padding-top: 0.8rem; }}
        .achievement-section h4 {{ font-size: 0.9rem; color: var(--accent-gold); margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.4rem; }}
        .achievement-body {{ font-size: 0.9rem; color: var(--text-main); line-height: 1.4; background: rgba(15, 23, 42, 0.4); padding: 0.6rem 0.8rem; border-radius: 8px; border: 1px dashed rgba(255, 255, 255, 0.15); outline: none; }}
        footer {{ text-align: center; margin-top: 3rem; padding: 1.5rem; color: var(--text-muted); font-size: 0.9rem; }}
    </style>
</head>
<body>
    <div class="container">
        <header class="report-header">
            <h1><i class="fas fa-star"></i> Phase 1 Comprehensive Report</h1>
            <p>Synergy Star 2026 - Official Nomination & Evaluation Analysis</p>
        </header>
        <section>
            <h2 class="section-title"><i class="fas fa-chart-pie"></i> Vote Distribution Percentage</h2>
            <div class="chart-card"><div class="chart-container"><canvas id="votePieChart"></canvas></div></div>
        </section>
        <section>
            <h2 class="section-title"><i class="fas fa-trophy"></i> Nominees (Most Votes & Highest Points)</h2>
            <div class="grid-cards">{infocards_html}</div>
        </section>
        <footer><p>Generated automatically on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Synergy Star 2026 System</p></footer>
    </div>
    <script>
        const ctx = document.getElementById('votePieChart').getContext('2d');
        const votePieChart = new Chart(ctx, {{
            type: 'pie',
            data: {{
                labels: {chart_labels},
                datasets: [{{
                    data: {chart_data},
                    backgroundColor: ['#f59e0b', '#3b82f6', '#10b981', '#ec4899', '#8b5cf6', '#06b6d4', '#f97316', '#84cc16', '#e11d48', '#6366f1'],
                    borderColor: '#1e293b',
                    borderWidth: 2
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{ position: 'right', labels: {{ color: '#f8fafc', font: {{ size: 12 }} }} }}
                }}
            }}
        }});
    </script>
</body>
</html>
"""
    return html_template


# Header display banner (Phase 2 Finals Title)
header_title_text = t['p2_title']
st.markdown(f"""
    <div style="display: flex; justify-content: center; align-items: center; margin-bottom: 1.5rem;">
        <img src="{LOGO_URL}" alt="Logo" style="
            max-height: 200px; 
            width: auto; 
            display: block; 
            background: transparent !important; 
            filter: drop-shadow(0 0 12px rgba(245, 158, 11, 0.9)) drop-shadow(0 0 22px rgba(217, 119, 6, 0.7));
        " />
    </div>
    <div class="golden-title-card">
        <h1 class="golden-glow-text" style="font-family: 'TitleCondOfcVI' !important; width: 100%; text-align: center; margin: 0 auto; white-space: pre-line;">{header_title_text}</h1>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# PORTAL CLOSED CHECK OR ACTIVE PHASE 2 FLOW
# ==========================================
if PORTAL_CLOSED:
    with st.form(key="portal_closed_form"):
        if IMG_THANKYOU:
            st.image(IMG_THANKYOU, use_container_width=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 2rem 0;">
                <h2 style="color: #F87171; font-size: 2.2rem; margin-bottom: 1rem;">{t['portal_closed_title']}</h2>
                <p style="font-size: 1.2rem; line-height: 1.6; margin-bottom: 1.5rem;">{t['portal_closed_msg']}</p>
            </div>
        """, unsafe_allow_html=True)
else:
    # ==========================================
    # PHASE 2: FINALIST VOTING & SCORING FLOW (PHASE 1 PERMANENTLY DISABLED)
    # ==========================================
    if st.session_state["p2_step"] == 0:
        with st.form(key="p2_welcome_form"):
            if IMG_WELCOME:
                st.image(IMG_WELCOME, use_container_width=True)
            st.markdown(f"""
                <div style="text-align: center; padding: 1rem 0;">
                    <h2 style="font-family: 'TitleCondOfcVI' !important; font-size: 1.8rem; margin-bottom: 1rem;">{t['p2_welcome_heading']}</h2>
                    <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem; width: 100%; text-align: center; white-space: pre-line; font-family: 'TitleCondOfcVI' !important;">{t['p2_welcome_desc']}</p>
                </div>
            """, unsafe_allow_html=True)

            p2_start_clicked = st.form_submit_button(t["p2_start_btn"], use_container_width=True)
            if p2_start_clicked:
                st.session_state["p2_step"] = 1
                st.rerun()

    elif st.session_state["p2_step"] == 1:
        st.subheader(t["p2_title"])

        # Instruction banner guiding the user to scroll down and select 3 finalists
        st.markdown(f"""
            <div style="background: rgba(60, 45, 15, 0.85); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 10px; padding: 1rem; margin-bottom: 1.5rem; text-align: center;">
                <p style="color: #FDE047; font-size: 1.1rem; margin: 0; font-weight: bold;">{t['p2_instruction_banner']}</p>
            </div>
        """, unsafe_allow_html=True)

        selected_list = st.session_state["p2_selected_nominees"]

        # Display counter status
        st.markdown(f"### {t['p2_selected_count'].format(len(selected_list))}")

        # Display all finalist infocards using single-line HTML concatenation to prevent code-block rendering
        for idx, finalist in enumerate(TOP_10_FINALISTS):
            name = finalist["name"]
            dept = finalist["department"]
            bio = finalist["bio"]
            img = finalist["image"]

            is_selected = name in selected_list

            card_bg = "rgba(60, 45, 15, 0.85)" if is_selected else "rgba(42, 35, 15, 0.7)"
            card_border = "2px solid #FDE047" if is_selected else "1px solid rgba(245, 158, 11, 0.4)"
            card_shadow = "0 0 25px rgba(245, 158, 11, 0.7)" if is_selected else "0 4px 12px rgba(0, 0, 0, 0.3)"

            medal_html = (
                f'<img src="{IMG_MEDAL}" style="position: absolute; top: 15px; right: 15px; width: 60px; height: 60px; '
                f'filter: drop-shadow(0 0 8px rgba(245, 158, 11, 0.9)); z-index: 10;" />'
                if is_selected else ""
            )

            card_html = (
                f'<div style="position: relative; background: {card_bg}; border: {card_border}; border-radius: 14px; padding: 1.5rem; margin-bottom: 1.2rem; box-shadow: {card_shadow}; transition: all 0.3s ease;">'
                f'{medal_html}'
                f'<div style="display: flex; gap: 1.5rem; align-items: flex-start; flex-wrap: wrap;">'
                f'<div style="flex: 0 0 160px; text-align: center;">'
                f'<img src="{img}" alt="Nominee Photo" style="width: 160px; height: 200px; aspect-ratio: 4 / 5; border-radius: 8px; object-fit: cover; border: 2px solid #F59E0B; box-shadow: 0 4px 12px rgba(245, 158, 11, 0.3);" />'
                f'<div style="margin-top: 0.5rem; font-weight: bold; color: #FDE047; font-size: 0.95rem;">{name}</div>'
                f'<div style="color: #F7C657; font-size: 0.85rem; font-style: italic;">{dept}</div>'
                f'</div>'
                f'<div style="flex: 1; min-width: 220px;">'
                f'<h3 style="color: #FDE047; margin-bottom: 0.2rem; font-size: 1.5rem;">{name}</h3>'
                f'<p style="color: #F7C657; font-size: 1rem; font-style: italic; margin-bottom: 0.8rem;">{dept}</p>'
                f'<h4 style="color: #FDE047; font-size: 1.15rem; margin-bottom: 0.4rem; border-bottom: 1px solid rgba(245, 158, 11, 0.3); padding-bottom: 0.2rem;">{t["highlights_title"]}</h4>'
                f'<p style="color: #FFF; font-size: 1.05rem; line-height: 1.6;">{bio}</p>'
                f'</div>'
                f'</div>'
                f'</div>'
            )

            st.markdown(card_html, unsafe_allow_html=True)

            # Selection button below each card
            btn_label = f"✅ {t['p2_selected']}" if is_selected else f"⭐ {t['p2_selection']}"
            if st.button(btn_label, key=f"select_btn_{idx}", use_container_width=True):
                if is_selected:
                    st.session_state["p2_selected_nominees"].remove(name)
                else:
                    if len(st.session_state["p2_selected_nominees"]) < 3:
                        st.session_state["p2_selected_nominees"].append(name)
                    else:
                        st.warning("You can only select a maximum of 3 finalists! Please deselect one first.")
                st.rerun()

        # Show submission button ONLY when exactly 3 finalists are selected
        if len(st.session_state["p2_selected_nominees"]) == 3:
            st.markdown("---")
            with st.form(key="p2_voting_form"):
                st.success(f"{t['p2_confirm_nomination']}: {', '.join(st.session_state['p2_selected_nominees'])}")
                p2_submit_clicked = st.form_submit_button(t["p2_submit_btn"], use_container_width=True, type="primary")

            if p2_submit_clicked:
                for nom in st.session_state["p2_selected_nominees"]:
                    selected_record = {
                        "Thời Gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "Tên Ứng Viên": nom,
                        "Phòng Ban": next((f["department"] for f in TOP_10_FINALISTS if f["name"] == nom), ""),
                        "Device_ID": DEVICE_ID
                    }
                    df_p2_new = pd.DataFrame([selected_record])
                    df_p2_new.to_csv(DATA_FILE_P2, mode='a', header=False, index=False, encoding='utf-8-sig')

                current_reg_p2 = load_device_registry(DEVICE_REGISTRY_FILE_P2)
                if DEVICE_ID not in current_reg_p2:
                    current_reg_p2.append(DEVICE_ID)
                    save_device_registry(DEVICE_REGISTRY_FILE_P2, current_reg_p2)

                st.session_state["p2_step"] = 2
                st.rerun()

    elif st.session_state["p2_step"] == 2:
        if IMG_THANKYOU:
            st.image(IMG_THANKYOU, use_container_width=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0;">
                <h2 style="color: #4ADE80; font-size: 2rem; margin-bottom: 1rem;">{t['p2_thank_you_title']}</h2>
                <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem;">{t['p2_thank_you_msg']}</p>
            </div>
        """, unsafe_allow_html=True)

# ==========================================
# ANCHORED ADMINISTRATOR LOGIN PANEL
# ==========================================
st.divider()
with st.expander(t["admin_sec"]):
    admin_password = st.text_input(t["admin_pass_label"], type="password", key="admin_pass_input")
    if admin_password == AD_PASS:
        st.success(t["admin_success"])

        # --- PORTAL & DEVICE MANAGEMENT CONTROLS ---
        st.markdown("---")
        st.subheader("Portal Management Control")

        new_portal_closed_toggle = st.toggle("🛑 Close Portal (Pause Submissions & Voting)", value=PORTAL_CLOSED)
        if new_portal_closed_toggle != PORTAL_CLOSED:
            save_json_state(PORTAL_STATE_FILE, {"portal_closed": new_portal_closed_toggle})
            st.success(f"Portal Closed Status updated to: {new_portal_closed_toggle}. Reloading...")
            st.rerun()

        if st.button("Reset Phase 2 Devices"):
            save_device_registry(DEVICE_REGISTRY_FILE_P2, [])
            st.success("Phase 2 device registry reset!")

        # --- PHASE 2 ADMIN DASHBOARD SECTION ---
        if os.path.exists(DATA_FILE_P2):
            try:
                df_p2_raw = pd.read_csv(DATA_FILE_P2, on_bad_lines='skip')
                st.markdown(f"### Phase 2 Finals Dashboard (Total Votes: {len(df_p2_raw)})")

                if not df_p2_raw.empty and "Tên Ứng Viên" in df_p2_raw.columns:
                    summary_p2 = df_p2_raw.groupby("Tên Ứng Viên").agg(
                        Số_Lượt_Bình_Chọn=("Phòng Ban", "count")
                    ).reset_index()

                    st.markdown("#### Vote Allocation Percentage (Top Finalists)")
                    total_p2_votes = summary_p2["Số_Lượt_Bình_Chọn"].sum()
                    summary_p2["Phần_Trăm"] = (summary_p2["Số_Lượt_Bình_Chọn"] / total_p2_votes) * 100 if total_p2_votes > 0 else 0

                    pie_chart_p2 = alt.Chart(summary_p2).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="Số_Lượt_Bình_Chọn", type="quantitative"),
                        color=alt.Color(field="Tên Ứng Viên", type="nominal", legend=alt.Legend(title="Finalist")),
                        tooltip=["Tên Ứng Viên", "Số_Lượt_Bình_Chọn", alt.Tooltip("Phần_Trăm:Q", format=".1f", title="Percentage (%)")]
                    ).properties(width=400, height=350)
                    st.altair_chart(pie_chart_p2, use_container_width=True)

                    st.markdown("#### Top Finalists with Most Votes")
                    top_votes_p2 = summary_p2.sort_values(by="Số_Lượt_Bình_Chọn", ascending=False).head(10)
                    st.bar_chart(top_votes_p2.set_index("Tên Ứng Viên")["Số_Lượt_Bình_Chọn"])

                    st.markdown("#### Phase 2 Raw Nomination Data")
                    st.dataframe(df_p2_raw, use_container_width=True)

                    csv_p2_data = df_p2_raw.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                    st.download_button(
                        label="Download Phase 2 CSV Data",
                        data=csv_p2_data,
                        file_name=f"phase2_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            except Exception as e:
                st.info(f"Phase 2 data log empty or unreadable: {e}")

        # --- PHASE 1 ARCHIVE DATA SECTION ---
        if os.path.exists(DATA_FILE):
            try:
                df_raw = pd.read_csv(DATA_FILE, on_bad_lines='skip')
                st.markdown(f"### Phase 1 Nominations Archive (Total: {len(df_raw)})")
                st.dataframe(df_raw, use_container_width=True)
            except Exception:
                pass
    elif admin_password != "":
        st.error(t["err_pass"])