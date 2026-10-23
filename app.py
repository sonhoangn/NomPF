import os
import json
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import io
import uuid

# --- REPORTLAB PDF GENERATION IMPORTS ---
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# --- CONFIGURABLE MEDIA ASSETS ---
LOGO_URL = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/icon.png"
P_ICON = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/icon.png"
BG_IMAGE_URL = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/bg.gif"
IMG_WELCOME = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/bg.png"
IMG_THANKYOU = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/ty.png"
IMG_COLLAB = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/cl1.png"
IMG_INNOV = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/in1.png"
IMG_CULTURE = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/cv1.png"
IMG_ACC = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/ac1.png"

# Configure page settings
st.set_page_config(
    page_title="Synergy Star 2026",
    page_icon=P_ICON,
    layout="centered"
)

# --- LOAD SECRETS FOR NOMINEE LIBRARY & ADMIN ---
AD_PASS = st.secrets.get("AD_PASS", "MO-LQN")
NOMINEE_LIBRARY = st.secrets.get("NOMINEE_LIST", ["Nguyen Van A", "John Doe", "Max Mustermann"])

# --- DEVICE TRACKING & PERSISTENCE FILES ---
DATA_FILE = "danh_sach_de_cu.csv"
DEVICE_REGISTRY_FILE = "device_registry.json"

def load_device_registry():
    if os.path.exists(DEVICE_REGISTRY_FILE):
        try:
            with open(DEVICE_REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_device_registry(registry_list):
    with open(DEVICE_REGISTRY_FILE, "w", encoding="utf-8") as f:
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

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state["step"] = 0  # 0: Welcome, 1: Nominee Info, 2: Collab, 3: Innov, 4: Culture, 5: Acc, 6: Thank You, 7: Locked Out

# Check if device has already submitted
registered_devices = load_device_registry()
if DEVICE_ID in registered_devices and st.session_state["step"] not in [6, 7]:
    st.session_state["step"] = 7

# Form data storage in session state
default_keys = {
    "nominee_name": "",
    "department": "Others",
    "score_collab": 5,
    "evidence_collab": "",
    "score_innov": 5,
    "evidence_innov": "",
    "score_culture": 5,
    "evidence_culture": "",
    "score_acc": 5,
    "evidence_acc": ""
}
for key, default_val in default_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default_val


# --- ADVANCED NAME MATCHING & NORMALIZATION ENGINE ---
def normalize_tokens(name_str):
    """Removes commas, extra whitespace, and splits into lowercase tokens."""
    cleaned = name_str.replace(",", " ").strip()
    return [token.lower() for token in cleaned.split() if token]


def get_canonical_name(input_name, library_list):
    """
    Matches input name against the library considering comma placement and token variations.
    Strictly preserves token sequence orders (e.g., 'Nguyen Van A' != 'Nguyen A Van').
    """
    if not input_name:
        return input_name

    input_tokens = normalize_tokens(input_name)
    if not input_tokens:
        return input_name

    for lib_name in library_list:
        lib_tokens = normalize_tokens(lib_name)

        # 1. Direct strict token match
        if input_tokens == lib_tokens:
            return lib_name

        # 2. Check comma-shifted variations (e.g., "Nguyen, Van A" or "A, Nguyen Van")
        raw_parts = [p.strip() for p in input_name.split(",")]
        if len(raw_parts) > 1:
            reconstructed_tokens = []
            for part in raw_parts:
                reconstructed_tokens.extend([t.lower() for t in part.split() if t])

            if reconstructed_tokens == lib_tokens:
                return lib_name

    # If no library match is found, return the original input capitalized cleanly
    return " ".join([t.capitalize() for t in normalize_tokens(input_name)])


# Helper function to generate safe dynamic glow style based on slider value
def get_slider_glow_style(score):
    if score >= 4:
        return """
        <style>
        div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] {
            background-color: #FDE047 !important;
            box-shadow: 0 0 12px rgba(245, 158, 11, 0.9), 0 0 20px rgba(217, 119, 6, 0.7) !important;
            border-color: #F59E0B !important;
        }
        div[data-testid="stSlider"] div[data-baseweb="slider"] > div:nth-child(2) div {
            background: linear-gradient(90deg, #F59E0B, #FDE047) !important;
        }
        </style>
        """
    elif score == 1:
        return """
        <style>
        div[data-testid="stSlider"] div[data-baseweb="slider"] div[role="slider"] {
            background-color: #F87171 !important;
            box-shadow: 0 0 12px rgba(239, 68, 68, 0.9), 0 0 20px rgba(220, 38, 38, 0.7) !important;
            border-color: #EF4444 !important;
        }
        div[data-testid="stSlider"] div[data-baseweb="slider"] > div:nth-child(2) div {
            background: linear-gradient(90deg, #DC2626, #F87171) !important;
        }
        </style>
        """
    else:
        return ""


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

        @font-face {{
            font-family: 'TextOfcVI-Bold';
            src: url('app/static/MBCorpoSTextOfcVI-Bold 2.ttf') format('truetype');
            font-weight: 700;
            font-style: normal;
        }}

        @font-face {{
            font-family: 'TextOfcVI-Light';
            src: url('app/static/MBCorpoSTextOfcVI-Light 2.ttf') format('truetype');
            font-weight: 100;
            font-style: normal;
        }}

        @font-face {{
            font-family: 'TextOfcVI-Regular';
            src: url('app/static/MBCorpoSTextOfcVI-Regular 2.ttf') format('truetype');
            font-weight: 400;
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

        .stProgress > div > div > div > div {{
            background-color: #4ADE80 !important;
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

# --- MULTI-LANGUAGE DICTIONARY ---
TRANSLATIONS = {
    "Tiếng Việt (Vietnamese)": {
        "title": "Cổng Đề Cử\nNgôi Sao\nTạo Động Lực",
        "welcome_heading": "Chào Mừng Đến Cổng Đề Cử",
        "welcome_desc": "Vinh danh 3 đồng nghiệp xuất sắc nhất,\nnhững người kết nối các động lực liên phòng ban,\ntạo ra giá trị vượt xa các mục tiêu công việc thông thường trong toàn tổ chức.",
        "start_btn": "Bắt Đầu Đề Cử",

        "step_indicator": "Bước {} / 5",
        "sec1": "1. Thông tin người được đề cử",
        "nominee_label": "Nhập tên *",
        "nominee_placeholder": "Nhập họ tên đầy đủ...",
        "dept_label": "Phòng ban / Bộ phận *",

        "collab_title": "1. Hợp Tác (Collaboration)",
        "collab_desc": "Mô tả: Thể hiện tinh thần làm việc nhóm vượt ra ngoài phạm vi công việc được xác định; phối hợp hiệu quả với người khác thông qua chia sẻ kiến thức, hỗ trợ đồng đội, chủ động tiếp nhận phản hồi và giải quyết xung đột mang tính xây dựng.",
        "collab_slider": "Điểm Hợp Tác",
        "collab_evidence": "Minh chứng / Ví dụ cụ thể cho tiêu chí Hợp Tác *",
        "collab_ph": "Nêu rõ tình huống hoặc dự án phối hợp thành công...",

        "innov_title": "2. Đổi Mới Sáng Tạo (Innovation)",
        "innov_desc": "Mô tả: Có khả năng đưa ra các ý tưởng có giá trị, thách thức lối mòn và giải quyết vấn đề một cách sáng tạo.",
        "innov_slider": "Điểm Đổi Mới",
        "innov_evidence": "Minh chứng / Ví dụ cụ thể cho tiêu chí Đổi Mới *",
        "innov_ph": "Mô tả ý tưởng hoặc cải tiến đã được áp dụng...",

        "culture_title": "3. Văn Hóa & Giá Trị (Culture & Value)",
        "culture_desc": "Mô tả: Thể hiện các giá trị của công ty thông qua sự chính trực, tôn trọng và tuân thủ các chuẩn mực đạo đức.",
        "culture_slider": "Điểm Văn Hóa & Giá Trị",
        "culture_evidence": "Minh chứng / Ví dụ cụ thể cho tiêu chí Văn Hóa & Giá Trị *",
        "culture_ph": "Nêu ví dụ về hành động thể hiện giá trị văn hóa...",

        "acc_title": "4. Trách Nhiệm (Accountability)",
        "acc_desc": "Mô tả: Thực hiện đúng cam kết, tuân thủ kỷ luật thời gian, chuẩn bị công việc chu đáo và thực hiện đúng quy trình; đồng thời không ngừng cải thiện để cùng nhau tạo nên sự khác biệt.",
        "acc_slider": "Điểm Trách Nhiệm",
        "acc_evidence": "Minh chứng / Ví dụ cụ thể cho tiêu chí Trách Nhiệm *",
        "acc_ph": "Nêu ví dụ về tinh thần trách nhiệm trong công việc...",

        "next_btn": "Tiếp theo ➔",
        "prev_btn": "⬅️ Quay lại",
        "submit_btn": "Hoàn Tất & Gửi Đề Cử",
        "err_fields": "⚠️ Vui lòng nhập tên người được đề cử!",
        "err_evidence": "⚠️ Vui lòng điền minh chứng cho tiêu chí này!",

        "thank_you_title": "Cảm Ơn Bạn Đã Đề Cử!",
        "thank_you_msg": "Thông tin đề cử của bạn đã được ghi nhận thành công từ thiết bị này. Mỗi thiết bị chỉ được thực hiện đề cử 1 lần duy nhất.",
        "locked_title": "Thiết Bị Đã Thực Hiện Đề Cử",
        "locked_msg": "Thiết bị này đã hoàn tất việc gửi đề cử trước đó. Cảm ơn sự tham gia đóng góp của bạn vào chương trình!",

        "admin_sec": "🔒 Quản Trị Viên (Xem & Tải Dữ Liệu)",
        "admin_pass_label": "Nhập mật khẩu quản trị",
        "admin_success": "Xác thực thành công!",
        "total_nominations": "Tổng số lượt đề cử:",
        "reset_devices_btn": "🔄 Đặt Lại Danh Sách Thiết Bị (Cho phép đề cử lại)",
        "reset_devices_success": "Đã reset thiết bị thành công! Các thiết bị có thể làm mới trang để đề cử lại.",
        "download_btn": "📥 Tải Bảng Dữ Liệu Gốc (CSV)",
        "download_pdf_btn": "📥 Tải Báo Cáo PDF Dashboard",
        "summary_table_title": "📊 Bảng Tổng Hợp Số Lượt Đề Cử & Điểm Trung Bình:",
        "raw_table_title": "📋 Bảng Dữ Liệu Gốc Các Đề Cử:",
        "chart_votes_title": "📈 Top 10 Đề Cử Nhiều Nhất (Nhiều Lượt Bình Chọn Nhất)",
        "chart_scores_title": "⭐ Top 10 Đề Cử Điểm Trung Bình Cao Nhất",
        "chart_pie_title": "🥧 Tỷ Lệ Phân Bổ Bình Chọn (Phần Trăm Lượt Đề Cử)",
        "leaderboard_title": "🏆 Bảng Xếp Hạng (Top 10 Đề Cử Hàng Đầu)",
        "err_pass": "Mật khẩu không chính xác!"
    },
    "English": {
        "title": "Synergy Star \nNomination Portal",
        "welcome_heading": "Welcome to the Award Nomination Portal",
        "welcome_desc": "Recognizing top 3 teammates,\nwho connect our synergies,\nthat bring beyond the regular working objectives across organizations",
        "start_btn": "Start Nomination",

        "step_indicator": "Step {} of 5",
        "sec1": "1. Nominee Information",
        "nominee_label": "Type name manually *",
        "nominee_placeholder": "Type full name...",
        "dept_label": "Department *",

        "collab_title": "1. Collaboration",
        "collab_desc": "Description: Demonstrate a teamwork spirit that goes beyond the defined scope of work; coordinate effectively with others through knowledge sharing, teammate support, proactive feedback, and constructive conflict resolution.",
        "collab_slider": "Collaboration Score",
        "collab_evidence": "Evidence / Specific example for Collaboration *",
        "collab_ph": "Describe the successful collaboration scenario or project...",

        "innov_title": "2. Innovation",
        "innov_desc": "Description: Capable of coming up with valuable ideas, challenging the rut, and solving problems creatively.",
        "innov_slider": "Innovation Score",
        "innov_evidence": "Evidence / Specific example for Innovation *",
        "innov_ph": "Describe the idea or workflow improvement implemented...",

        "culture_title": "3. Culture & Value",
        "culture_desc": "Description: Demonstrate company values through integrity, respect, and adherence to ethical standards.",
        "culture_slider": "Culture & Value Score",
        "culture_evidence": "Evidence / Specific example for Culture & Value *",
        "culture_ph": "Provide examples of actions reflecting cultural values...",

        "acc_title": "4. Accountability",
        "acc_desc": "Description: Fulfilling commitments, complying with time discipline, preparing work thoughtfully and implementing the right process; at the same time, constantly improving to make a difference together.",
        "acc_slider": "Accountability Score",
        "acc_evidence": "Evidence / Specific example for Accountability *",
        "acc_ph": "Provide examples of strong responsibility in work...",

        "next_btn": "Next ➔",
        "prev_btn": "⬅️ Back",
        "submit_btn": "Submit Nomination",
        "err_fields": "⚠️ Please type the nominee name!",
        "err_evidence": "⚠️ Please provide evidence for this criterion!",

        "thank_you_title": "Thank You for Your Nomination!",
        "thank_you_msg": "Your nomination has been recorded successfully from this device. Each device is permitted one submission only.",
        "locked_title": "Nomination Already Submitted",
        "locked_msg": "A nomination has already been submitted from this device. Thank you for your participation!",

        "admin_sec": "🔒 Administrator (View & Download Data)",
        "admin_pass_label": "Enter admin password",
        "admin_success": "Authentication successful!",
        "total_nominations": "Total nominations:",
        "reset_devices_btn": "🔄 Reset Device Registry (Allow Re-nomination)",
        "reset_devices_success": "Device registry successfully reset! Devices can now reload and submit again.",
        "download_btn": "📥 Download Raw Data (CSV)",
        "download_pdf_btn": "📥 Download Dashboard PDF Report",
        "summary_table_title": "📊 Summary Table of Total Votes & Average Scores:",
        "raw_table_title": "📋 Raw Nominations Table:",
        "chart_votes_title": "📈 Top 10 Most Voted Nominees",
        "chart_scores_title": "⭐ Top 10 Highest Average Scores",
        "chart_pie_title": "🥧 Vote Allocation Percentage (Pie Chart)",
        "leaderboard_title": "🏆 Leaderboard (Top 10 Nominees)",
        "err_pass": "Incorrect password!"
    },
    "Deutsch (German)": {
        "title": "Mitarbeiter-Nominierungsportal",
        "welcome_heading": "Willkommen beim Nominierungsportal",
        "welcome_desc": "Dieses Programm ehrt herausragende Einzelpersonen mit außergewöhnlichen Beiträgen.\nReichen Sie jetzt Ihre Nominierung ein!",
        "start_btn": "Nominierung Starten",

        "step_indicator": "Schritt {} von 5",
        "sec1": "1. Informationen zum Nominierten",
        "nominee_label": "Namen manuell eingeben *",
        "nominee_placeholder": "Vollständigen Namen eingeben...",
        "dept_label": "Abteilung *",

        "collab_title": "1. Zusammenarbeit (Collaboration)",
        "collab_desc": "Beschreibung: Einen Teamgeist zeigen, der über den definierten Arbeitsbereich hinausgeht; effektive Koordination mit anderen durch Wissensaustausch, Unterstützung von Teamkollegen, proaktives Feedback und konstruktive Konfliktlösung.",
        "collab_slider": "Bewertung der Zusammenarbeit",
        "collab_evidence": "Nachweis / Konkretes Beispiel für das Kriterium Zusammenarbeit *",
        "collab_ph": "Beschreiben Sie das erfolgreiche Kooperationsszenario oder Projekt...",

        "innov_title": "2. Innovation",
        "innov_desc": "Beschreibung: Fähigkeit, wertvolle Ideen einzubringen, eingefahrene Wege zu hinterfragen und Probleme kreativ zu lösen.",
        "innov_slider": "Bewertung für Innovation",
        "innov_evidence": "Nachweis / Konkretes Beispiel für das Kriterium Innovation *",
        "innov_ph": "Beschreiben Sie die umgesetzte Idee oder Prozessverbesserung...",

        "culture_title": "3. Kultur & Werte (Culture & Value)",
        "culture_desc": "Beschreibung: Demonstration der Unternehmenswerte durch Integrität, Respekt und die Einhaltung ethischer Standards.",
        "culture_slider": "Bewertung für Kultur & Werte",
        "culture_evidence": "Nachweis / Konkretes Beispiel für das Kriterium Kultur & Werte *",
        "culture_ph": "Geben Sie Beispiele für Handlungen an, die kulturelle Werte widerspiegeln...",

        "acc_title": "4. Verantwortlichkeit (Accountability)",
        "acc_desc": "Beschreibung: Erfüllung von Verpflichtungen, Einhaltung der Zeitdisziplin, sorgfältige Vorbereitung der Arbeit und Umsetzung des richtigen Prozesses; gleichzeitig ständige Verbesserung, um gemeinsam etwas zu bewegen.",
        "acc_slider": "Bewertung der Verantwortlichkeit",
        "acc_evidence": "Nachweis / Konkretes Beispiel für das Kriterium Verantwortlichkeit *",
        "acc_ph": "Geben Sie Beispiele für starkes Verantwortungsbewusstsein bei der Arbeit an...",

        "next_btn": "Weiter ➔",
        "prev_btn": "⬅️ Zurück",
        "submit_btn": "Nominierung Absenden",
        "err_fields": "⚠️ Bitte geben Sie den Namen ein!",
        "err_evidence": "⚠️ Bitte geben Sie für dieses Kriterium Nachweise an!",

        "thank_you_title": "Vielen Dank für Ihre Nominierung!",
        "thank_you_msg": "Ihre Nominierung wurde erfolgreich von diesem Gerät erfasst. Jedes Gerät darf nur einmal einreichen.",
        "locked_title": "Nominierung Bereits Abgeschlossen",
        "locked_msg": "Von diesem Gerät wurde bereits eine Nominierung eingereicht. Vielen Dank für Ihre Teilnahme!",

        "admin_sec": "🔒 Administrator (Daten anzeigen & herunterladen)",
        "admin_pass_label": "Admin-Passwort eingeben",
        "admin_success": "Authentifizierung erfolgreich!",
        "total_nominations": "Gesamtzahl der Nominierungen:",
        "reset_devices_btn": "🔄 Geräteliste zurücksetzen (Erneut nominieren erlauben)",
        "reset_devices_success": "Geräteliste erfolgreich zurückgesetzt! Geräte können die Seite neu laden, um erneut zu nominieren.",
        "download_btn": "📥 Rohdaten herunterladen (CSV)",
        "download_pdf_btn": "📥 Dashboard PDF-Bericht herunterladen",
        "summary_table_title": "📊 Zusammenfassung der Stimmen & Durchschnittswerte:",
        "raw_table_title": "📋 Rohdaten-Tabelle der Nominierungen:",
        "chart_votes_title": "📈 Top 10 Nominierte nach Stimmen",
        "chart_scores_title": "⭐ Top 10 Höchste Durchschnittswerte",
        "chart_pie_title": "🥧 Stimmverteilung (Prozentdiagramm)",
        "leaderboard_title": "🏆 Bestenliste (Top 10 Nominierte)",
        "err_pass": "Falsches Passwort!"
    }
}

# Sidebar Language Selector
selected_lang_key = st.sidebar.selectbox("🌐 Language / Ngôn ngữ / Sprache", list(TRANSLATIONS.keys()))
t = TRANSLATIONS[selected_lang_key]


def init_data_file():
    expected_columns = [
        "Thời Gian",
        "Tên Người Được Đề Cử",
        "Phòng Ban",
        "Điểm Trung Bình",
        "Điểm Hợp Tác", "Minh Chứng Hợp Tác",
        "Điểm Đổi Mới", "Minh Chứng Đổi Mới",
        "Điểm Văn Hóa & Giá Trị", "Minh Chứng Văn Hóa & Giá Trị",
        "Điểm Trách Nhiệm", "Minh Chứng Trách Nhiệm"
    ]

    if os.path.exists(DATA_FILE):
        try:
            df_existing = pd.read_csv(DATA_FILE, nrows=0)
            if list(df_existing.columns) != expected_columns:
                os.remove(DATA_FILE)
        except Exception:
            os.remove(DATA_FILE)

    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=expected_columns)
        df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')


init_data_file()


# Helper function to generate clean ASCII/English PDF report with text wrapping
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

    # Title & Metadata
    story.append(Paragraph("Synergy Star 2026 - Admin Dashboard Report", title_style))
    story.append(
        Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Total Submissions: {len(raw_df)}",
                  normal_style))
    story.append(Spacer(1, 8))

    # Helper function to format DataFrame into wrapped Paragraph tables with explicit column widths
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

    # 1. Leaderboard Section (English headers for PDF compatibility)
    story.append(Paragraph("Top 10 Leaderboard (Votes & Average Scores)", heading_style))
    lb_pdf = leaderboard_df.rename(columns={
        "Tên Người Được Đề Cử": "Nominee Name",
        "Số_Lượt_Đề_Cử": "Total Votes",
        "Điểm_Trung_Bình_Tổng_Thể": "Overall Avg Score"
    }).copy()
    story.append(create_wrapped_table(lb_pdf, col_widths=[250, 150, 160]))
    story.append(Spacer(1, 8))

    # 2. Summary Table Section
    story.append(Paragraph("Aggregated Summary Table", heading_style))
    sum_pdf = summary_df.rename(columns={
        "Tên Người Được Đề Cử": "Nominee Name",
        "Số_Lượt_Đề_Cử": "Total Votes",
        "Điểm_Trung_Bình_Tổng_Thể": "Overall Avg Score"
    }).copy()
    story.append(create_wrapped_table(sum_pdf, col_widths=[250, 150, 160]))
    story.append(Spacer(1, 8))

    # 3. Raw Submissions Table Section
    story.append(Paragraph("Raw Nominations Log", heading_style))
    raw_pdf = raw_df.rename(columns={
        "Thời Gian": "Timestamp",
        "Tên Người Được Đề Cử": "Nominee",
        "Phòng Ban": "Department",
        "Điểm Trung Bình": "Avg",
        "Điểm Hợp Tác": "Collab",
        "Minh Chứng Hợp Tác": "Collab Evidence",
        "Điểm Đổi Mới": "Innov",
        "Minh Chứng Đổi Mới": "Innov Evidence",
        "Điểm Văn Hóa & Giá Trị": "Culture",
        "Minh Chứng Văn Hóa & Giá Trị": "Culture Evidence",
        "Điểm Trách Nhiệm": "Acc",
        "Minh Chứng Trách Nhiệm": "Acc Evidence"
    }).copy()
    raw_widths = [55, 65, 55, 30, 35, 65, 35, 65, 35, 65, 30, 60]
    story.append(create_wrapped_table(raw_pdf, col_widths=raw_widths))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# Header Section with Golden Glow Title Effect
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
        <h1 class="golden-glow-text" style="font-family: 'TitleCondOfcVI' !important; width: 100%; text-align: center; margin: 0 auto; white-space: pre-line;">{t['title']}</h1>
    </div>
""", unsafe_allow_html=True)

# ==========================================
# SCREEN 0: WELCOME SCREEN
# ==========================================
if st.session_state["step"] == 0:
    with st.form(key="welcome_form"):
        if IMG_WELCOME:
            st.image(IMG_WELCOME, use_container_width=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0;">
                <h2 style="font-family: 'TitleCondOfcVI' !important; font-size: 1.8rem; margin-bottom: 1rem;">{t['welcome_heading']}</h2>
                <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem; width: 100%; text-align: center; white-space: pre-line; font-family: 'TitleCondOfcVI' !important;">{t['welcome_desc']}</p>
            </div>
        """, unsafe_allow_html=True)

        start_clicked = st.form_submit_button(t["start_btn"], use_container_width=True)
        if start_clicked:
            st.session_state["step"] = 1
            st.rerun()

# ==========================================
# SCREEN 1: NOMINEE DETAILS
# ==========================================
elif st.session_state["step"] == 1:
    with st.form(key="step1_form"):
        st.subheader(t["sec1"])

        typed_custom_name = st.text_input(
            t["nominee_label"],
            value=st.session_state["nominee_name"],
            placeholder=t["nominee_placeholder"]
        )

        dept_options = ["Engineering PSI", "Engineering Facility", "Production - Bodyshop", "Production - EDC",
                        "Production - Paintshop", "Production - Assembly", "Production - EoL/Finish",
                        "Logistics", "Quality Management", "Others"]
        try:
            default_dept_index = dept_options.index(st.session_state["department"])
        except ValueError:
            default_dept_index = 0

        department = st.selectbox(t["dept_label"], options=dept_options, index=default_dept_index)

        st.write("")
        col_back, col_next = st.columns([1, 1])
        with col_next:
            next_clicked = st.form_submit_button(t["next_btn"], type="primary")

    if next_clicked:
        raw_name = typed_custom_name.strip()
        if not raw_name:
            st.error(t["err_fields"])
        else:
            canonical_name = get_canonical_name(raw_name, NOMINEE_LIBRARY)
            st.session_state["nominee_name"] = canonical_name
            st.session_state["department"] = department
            st.session_state["step"] = 2
            st.rerun()

# ==========================================
# SCREEN 2: COLLABORATION
# ==========================================
elif st.session_state["step"] == 2:
    with st.form(key="step2_form"):
        if IMG_COLLAB:
            st.image(IMG_COLLAB, use_container_width=True)
        st.markdown(f"### {t['collab_title']}")
        st.caption(t["collab_desc"])
        score_collab = st.slider(t["collab_slider"], min_value=0, max_value=5, value=st.session_state["score_collab"])
        st.markdown(get_slider_glow_style(score_collab), unsafe_allow_html=True)
        evidence_collab = st.text_area(t["collab_evidence"], value=st.session_state["evidence_collab"],
                                       placeholder=t["collab_ph"])

        st.write("")
        col_back, col_next = st.columns([1, 1])
        with col_back:
            prev_clicked = st.form_submit_button(t["prev_btn"], use_container_width=True)
        with col_next:
            next_clicked = st.form_submit_button(t["next_btn"], use_container_width=True)

    if prev_clicked:
        st.session_state["step"] = 1
        st.rerun()
    elif next_clicked:
        if not evidence_collab.strip():
            st.error(t["err_evidence"])
        else:
            st.session_state["score_collab"] = score_collab
            st.session_state["evidence_collab"] = evidence_collab
            st.session_state["step"] = 3
            st.rerun()

# ==========================================
# SCREEN 3: INNOVATION
# ==========================================
elif st.session_state["step"] == 3:
    with st.form(key="step3_form"):
        if IMG_INNOV:
            st.image(IMG_INNOV, use_container_width=True)
        st.markdown(f"### {t['innov_title']}")
        st.caption(t["innov_desc"])
        score_innov = st.slider(t["innov_slider"], min_value=0, max_value=5, value=st.session_state["score_innov"])
        st.markdown(get_slider_glow_style(score_innov), unsafe_allow_html=True)
        evidence_innov = st.text_area(t["innov_evidence"], value=st.session_state["evidence_innov"],
                                      placeholder=t["innov_ph"])

        st.write("")
        col_back, col_next = st.columns([1, 1])
        with col_back:
            prev_clicked = st.form_submit_button(t["prev_btn"], use_container_width=True)
        with col_next:
            next_clicked = st.form_submit_button(t["next_btn"], use_container_width=True)

    if prev_clicked:
        st.session_state["step"] = 2
        st.rerun()
    elif next_clicked:
        if not evidence_innov.strip():
            st.error(t["err_evidence"])
        else:
            st.session_state["score_innov"] = score_innov
            st.session_state["evidence_innov"] = evidence_innov
            st.session_state["step"] = 4
            st.rerun()

# ==========================================
# SCREEN 4: CULTURE & VALUE
# ==========================================
elif st.session_state["step"] == 4:
    with st.form(key="step4_form"):
        if IMG_CULTURE:
            st.image(IMG_CULTURE, use_container_width=True)
        st.markdown(f"### {t['culture_title']}")
        st.caption(t["culture_desc"])
        score_culture = st.slider(t["culture_slider"], min_value=0, max_value=5,
                                  value=st.session_state["score_culture"])
        st.markdown(get_slider_glow_style(score_culture), unsafe_allow_html=True)
        evidence_culture = st.text_area(t["culture_evidence"], value=st.session_state["evidence_culture"],
                                        placeholder=t["culture_ph"])

        st.write("")
        col_back, col_next = st.columns([1, 1])
        with col_back:
            prev_clicked = st.form_submit_button(t["prev_btn"], use_container_width=True)
        with col_next:
            next_clicked = st.form_submit_button(t["next_btn"], use_container_width=True)

    if prev_clicked:
        st.session_state["step"] = 3
        st.rerun()
    elif next_clicked:
        if not evidence_culture.strip():
            st.error(t["err_evidence"])
        else:
            st.session_state["score_culture"] = score_culture
            st.session_state["evidence_culture"] = evidence_culture
            st.session_state["step"] = 5
            st.rerun()

# ==========================================
# SCREEN 5: ACCOUNTABILITY & FINAL SUBMIT
# ==========================================
elif st.session_state["step"] == 5:
    with st.form(key="step5_form"):
        if IMG_ACC:
            st.image(IMG_ACC, use_container_width=True)
        st.markdown(f"### {t['acc_title']}")
        st.caption(t["acc_desc"])
        score_acc = st.slider(t["acc_slider"], min_value=0, max_value=5, value=st.session_state["score_acc"])
        st.markdown(get_slider_glow_style(score_acc), unsafe_allow_html=True)
        evidence_acc = st.text_area(t["acc_evidence"], value=st.session_state["evidence_acc"], placeholder=t["acc_ph"])

        st.write("")
        col_back, col_next = st.columns([1, 1])
        with col_back:
            prev_clicked = st.form_submit_button(t["prev_btn"], use_container_width=True)
        with col_next:
            submit_clicked = st.form_submit_button(t["submit_btn"], use_container_width=True)

    if prev_clicked:
        st.session_state["step"] = 4
        st.rerun()
    elif submit_clicked:
        if not evidence_acc.strip():
            st.error(t["err_evidence"])
        else:
            st.session_state["score_acc"] = score_acc
            st.session_state["evidence_acc"] = evidence_acc

            avg_score = round((
                                      st.session_state["score_collab"] +
                                      st.session_state["score_innov"] +
                                      st.session_state["score_culture"] +
                                      st.session_state["score_acc"]
                              ) / 4.0, 2)

            new_entry = {
                "Thời Gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "Tên Người Được Đề Cử": st.session_state["nominee_name"],
                "Phòng Ban": st.session_state["department"],
                "Điểm Trung Bình": avg_score,
                "Điểm Hợp Tác": st.session_state["score_collab"],
                "Minh Chứng Hợp Tác": st.session_state["evidence_collab"],
                "Điểm Đổi Mới": st.session_state["score_innov"],
                "Minh Chứng Đổi Mới": st.session_state["evidence_innov"],
                "Điểm Văn Hóa & Giá Trị": st.session_state["score_culture"],
                "Minh Chứng Văn Hóa & Giá Trị": st.session_state["evidence_culture"],
                "Điểm Trách Nhiệm": st.session_state["score_acc"],
                "Minh Chứng Trách Nhiệm": st.session_state["evidence_acc"]
            }

            df_new = pd.DataFrame([new_entry])
            df_new.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')

            # Record device token in registry so it cannot submit again
            current_registry = load_device_registry()
            if DEVICE_ID not in current_registry:
                current_registry.append(DEVICE_ID)
                save_device_registry(current_registry)

            st.session_state["step"] = 6
            st.rerun()

# ==========================================
# SCREEN 6: THANK YOU SCREEN
# ==========================================
elif st.session_state["step"] == 6:
    if IMG_THANKYOU:
        st.image(IMG_THANKYOU, use_container_width=True)
    st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #4ADE80; font-size: 2rem; margin-bottom: 1rem;">{t['thank_you_title']}</h2>
            <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem;">{t['thank_you_msg']}</p>
        </div>
    """, unsafe_allow_html=True)

# ==========================================
# SCREEN 7: LOCKED OUT SCREEN (Already Submitted)
# ==========================================
elif st.session_state["step"] == 7:
    if IMG_THANKYOU:
        st.image(IMG_THANKYOU, use_container_width=True)
    st.markdown(f"""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #F87171; font-size: 2rem; margin-bottom: 1rem;">{t['locked_title']}</h2>
            <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem;">{t['locked_msg']}</p>
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

        # Admin option to reset device registry tokens
        if st.button(t["reset_devices_btn"]):
            save_device_registry([])
            st.success(t["reset_devices_success"])

        if os.path.exists(DATA_FILE):
            try:
                # 1. Original Raw Data Table
                df_raw = pd.read_csv(DATA_FILE, on_bad_lines='skip')
                st.write(f"**{t['total_nominations']}** {len(df_raw)}")

                if not df_raw.empty and "Tên Người Được Đề Cử" in df_raw.columns and "Điểm Trung Bình" in df_raw.columns:
                    # 2. Aggregated Summary Calculation Table
                    summary_df = df_raw.groupby("Tên Người Được Đề Cử").agg(
                        Số_Lượt_Đề_Cử=("Điểm Trung Bình", "count"),
                        Điểm_Trung_Bình_Tổng_Thể=("Điểm Trung Bình", "mean")
                    ).reset_index()

                    summary_df["Điểm_Trung_Bình_Tổng_Thể"] = summary_df["Điểm_Trung_Bình_Tổng_Thể"].round(2)
                    summary_df = summary_df.sort_values(by=["Số_Lượt_Đề_Cử", "Điểm_Trung_Bình_Tổng_Thể"],
                                                        ascending=False)

                    st.markdown(f"### {t['summary_table_title']}")
                    st.dataframe(summary_df, use_container_width=True)

                    # --- CHARTS & LEADERBOARD ---
                    st.markdown("---")

                    # Bar Chart 1: Top 10 Most Voted Nominees
                    st.markdown(f"### {t['chart_votes_title']}")
                    top_votes = summary_df.sort_values(by="Số_Lượt_Đề_Cử", ascending=False).head(10)
                    chart_votes_data = top_votes.set_index("Tên Người Được Đề Cử")["Số_Lượt_Đề_Cử"]
                    st.bar_chart(chart_votes_data)

                    # Bar Chart 2: Top 10 Highest Average Scores
                    st.markdown(f"### {t['chart_scores_title']}")
                    top_scores = summary_df.sort_values(by="Điểm_Trung_Bình_Tổng_Thể", ascending=False).head(10)
                    chart_scores_data = top_scores.set_index("Tên Người Được Đề Cử")["Điểm_Trung_Bình_Tổng_Thể"]
                    st.bar_chart(chart_scores_data)

                    # Pie Chart: Vote Percentage Allocation
                    st.markdown(f"### {t['chart_pie_title']}")
                    import altair as alt

                    pie_data = summary_df.copy()
                    total_votes_sum = pie_data["Số_Lượt_Đề_Cử"].sum()
                    pie_data["Phần_Trăm"] = (pie_data[
                                                 "Số_Lượt_Đề_Cử"] / total_votes_sum) * 100 if total_votes_sum > 0 else 0

                    pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="Số_Lượt_Đề_Cử", type="quantitative"),
                        color=alt.Color(field="Tên Người Được Đề Cử", type="nominal",
                                        legend=alt.Legend(title="Nominee")),
                        tooltip=["Tên Người Được Đề Cử", "Số_Lượt_Đề_Cử",
                                 alt.Tooltip("Phần_Trăm:Q", format=".1f", title="Percentage (%)")]
                    ).properties(width=400, height=350)
                    st.altair_chart(pie_chart, use_container_width=True)

                    # Leaderboard: Top 10 Nominees combining votes + highest average scores
                    st.markdown(f"### {t['leaderboard_title']}")
                    leaderboard_df = summary_df.sort_values(by=["Số_Lượt_Đề_Cử", "Điểm_Trung_Bình_Tổng_Thể"],
                                                            ascending=[False, False]).head(10).reset_index(drop=True)
                    leaderboard_df.index += 1  # 1-based rank
                    st.dataframe(leaderboard_df, use_container_width=True)

                # Render the original raw nomination data table separately below
                st.markdown(f"### {t['raw_table_title']}")
                st.dataframe(df_raw, use_container_width=True)

                col_dl1, col_dl2 = st.columns(2)
                with col_dl1:
                    csv_data = df_raw.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                    st.download_button(
                        label=t["download_btn"],
                        data=csv_data,
                        file_name=f"danh_sach_de_cu_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
                with col_dl2:
                    pdf_bytes = generate_pdf_report(summary_df, leaderboard_df, df_raw)
                    st.download_button(
                        label=t["download_pdf_btn"],
                        data=pdf_bytes,
                        file_name=f"synergy_star_report_{datetime.now().strftime('%Y%m%d')}.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"⚠️ Lỗi đọc file dữ liệu: {e}")
                st.info("💡 Bạn có thể xóa file `danh_sach_de_cu.csv` để ứng dụng khởi tạo lại bảng dữ liệu mới.")
    elif admin_password != "":
        st.error(t["err_pass"])