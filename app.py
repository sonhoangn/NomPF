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
PB = parse_secret_list(st.secrets.get("PB", ""))
PEDC = parse_secret_list(st.secrets.get("PEDC", ""))
PBP = parse_secret_list(st.secrets.get("PBP", ""))
LG = parse_secret_list(st.secrets.get("LG", ""))
PA = parse_secret_list(st.secrets.get("PA", ""))
PP = parse_secret_list(st.secrets.get("PP", ""))
QM = parse_secret_list(st.secrets.get("QM", ""))

# --- DEPARTMENT & PLACEHOLDER NAMES MAPPING ---
DEPARTMENT_NAMES = {
    "Production - Bodyshop": PB,
    "Production - ED Coating": PEDC,
    "Production - Bodyshop & Paintshop": PBP,
    "Logistics": LG,
    "Production - Assembly": PA,
    "Production - Paintshop": PP,
    "Quality Management": QM
}

# --- PHASE 2 TOP 10 FINALISTS CONFIGURATION ---
TOP_10_FINALISTS = [
    {
        "name": st.secrets.get("P2_NAME_1", "Finalist 1"),
        "department": st.secrets.get("P2_DEPT_1", "Production"),
        "bio": st.secrets.get("P2_BIO_1", "Outstanding contribution to cross-departmental synergy and process innovation."),
        "image": st.secrets.get("P2_IMG_1", IMG_COLLAB)
    },
    {
        "name": st.secrets.get("P2_NAME_2", "Finalist 2"),
        "department": st.secrets.get("P2_DEPT_2", "Logistics"),
        "bio": st.secrets.get("P2_BIO_2", "Exemplary commitment and leadership in supply chain optimization."),
        "image": st.secrets.get("P2_IMG_2", IMG_INNOV)
    },
    {
        "name": st.secrets.get("P2_NAME_3", "Finalist 3"),
        "department": st.secrets.get("P2_DEPT_3", "Quality Management"),
        "bio": st.secrets.get("P2_BIO_3", "Dedicated to maintaining rigorous standards and fostering collaborative culture."),
        "image": st.secrets.get("P2_IMG_3", IMG_CULTURE)
    },
    {
        "name": st.secrets.get("P2_NAME_4", "Finalist 4"),
        "department": st.secrets.get("P2_DEPT_4", "Engineering"),
        "bio": st.secrets.get("P2_BIO_4", "Pioneered automated tracking systems saving substantial operational hours."),
        "image": st.secrets.get("P2_IMG_4", IMG_ACC)
    },
    {
        "name": st.secrets.get("P2_NAME_5", "Finalist 5"),
        "department": st.secrets.get("P2_DEPT_5", "Production - Assembly"),
        "bio": st.secrets.get("P2_BIO_5", "Consistently demonstrates high accountability and team-first support."),
        "image": st.secrets.get("P2_IMG_5", IMG_WELCOME)
    },
    {
        "name": st.secrets.get("P2_NAME_6", "Finalist 6"),
        "department": st.secrets.get("P2_DEPT_6", "Logistics"),
        "bio": st.secrets.get("P2_BIO_6", "Streamlined material flow and resolved bottlenecks efficiently."),
        "image": st.secrets.get("P2_IMG_6", IMG_COLLAB)
    },
    {
        "name": st.secrets.get("P2_NAME_7", "Finalist 7"),
        "department": st.secrets.get("P2_DEPT_7", "Quality Management"),
        "bio": st.secrets.get("P2_BIO_7", "Championed continuous improvement initiatives across shifts."),
        "image": st.secrets.get("P2_IMG_7", IMG_INNOV)
    },
    {
        "name": st.secrets.get("P2_NAME_8", "Finalist 8"),
        "department": st.secrets.get("P2_DEPT_8", "Production - Paintshop"),
        "bio": st.secrets.get("P2_BIO_8", "Exceptional problem solver with a strong drive for technological innovation."),
        "image": st.secrets.get("P2_IMG_8", IMG_CULTURE)
    },
    {
        "name": st.secrets.get("P2_NAME_9", "Finalist 9"),
        "department": st.secrets.get("P2_DEPT_9", "Engineering PSI"),
        "bio": st.secrets.get("P2_BIO_9", "Trusted technical lead bridging IT and shopfloor operations seamlessly."),
        "image": st.secrets.get("P2_IMG_9", IMG_ACC)
    },
    {
        "name": st.secrets.get("P2_NAME_10", "Finalist 10"),
        "department": st.secrets.get("P2_DEPT_10", "Production - Bodyshop"),
        "bio": st.secrets.get("P2_BIO_10", "Exemplifies core corporate values and mentor-like support to junior staff."),
        "image": st.secrets.get("P2_IMG_10", IMG_WELCOME)
    }
]

# --- DEVICE TRACKING & PERSISTENCE FILES ---
DATA_FILE = "danh_sach_de_cu.csv"
DEVICE_REGISTRY_FILE = "device_registry.json"

# Phase 2 Persistence files
DATA_FILE_P2 = "danh_sach_de_cu_phase2.csv"
DEVICE_REGISTRY_FILE_P2 = "device_registry_phase2.json"
PHASE2_STATE_FILE = "phase2_state.json"
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


# Load Phase 2 active toggle state & Portal Closed state from persistent files
phase2_data = load_json_state(PHASE2_STATE_FILE, {"phase2_active": False})
PHASE_2_ACTIVE = phase2_data.get("phase2_active", False)

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

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state["step"] = 0

if "p2_step" not in st.session_state:
    st.session_state["p2_step"] = 0

if "p2_score_collab" not in st.session_state:
    st.session_state["p2_score_collab"] = 5
if "p2_score_innov" not in st.session_state:
    st.session_state["p2_score_innov"] = 5
if "p2_score_culture" not in st.session_state:
    st.session_state["p2_score_culture"] = 5
if "p2_score_acc" not in st.session_state:
    st.session_state["p2_score_acc"] = 5

# Check device submission lock based on active phase
if PHASE_2_ACTIVE:
    registered_devices_p2 = load_device_registry(DEVICE_REGISTRY_FILE_P2)
    if DEVICE_ID in registered_devices_p2 and st.session_state["p2_step"] not in [2]:
        st.session_state["p2_step"] = 2
else:
    registered_devices = load_device_registry(DEVICE_REGISTRY_FILE)
    if DEVICE_ID in registered_devices and st.session_state["step"] not in [6, 7]:
        st.session_state["step"] = 7

# Form data storage in session state
default_keys = {
    "nominee_name": "",
    "department": list(DEPARTMENT_NAMES.keys())[0],
    "score_collab": 5,
    "evidence_collab": "",
    "score_innov": 5,
    "evidence_innov": "",
    "score_culture": 5,
    "evidence_culture": "",
    "score_acc": 5,
    "evidence_acc": "",
    "p2_selected_nominee": TOP_10_FINALISTS[0]["name"]
}
for key, default_val in default_keys.items():
    if key not in st.session_state:
        st.session_state[key] = default_val


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

        "p2_title": "Vòng Bình Chọn Chung Kết (Phase 2)",
        "p2_welcome_heading": "Chào Mừng Đến Vòng Bình Chọn Top 10",
        "p2_welcome_desc": "Hãy xem qua hồ sơ của các ứng viên xuất sắc nhất lọt vào vòng chung kết và lựa chọn ứng viên xứng đáng nhất cùng với điểm số đánh giá.",
        "p2_start_btn": "Bắt Đầu Bình Chọn",
        "p2_select_label": "Chọn ứng viên chung kết *",
        "p2_submit_btn": "Xác Nhận & Gửi Bình Chọn",
        "p2_thank_you_title": "Cảm Ơn Bạn Đã Bình Chọn!",
        "p2_thank_you_msg": "Lựa chọn và điểm số của bạn cho vòng chung kết đã được ghi nhận thành công.",
        "p2_locked_title": "Bạn Đã Hoàn Thành Bình Chọn",
        "p2_locked_msg": "Thiết bị này đã tham gia bình chọn vòng chung kết trước đó. Xin cảm ơn sự tham gia của bạn!",

        "portal_closed_title": "Cổng Đề Cử Hiện Đang Tạm Đóng",
        "portal_closed_msg": "Cổng tiếp nhận đề cử và bình chọn hiện đang tạm thời đóng bởi Quản trị viên. Vui lòng quay lại sau!",

        "step_indicator": "Bước {} / 5",
        "sec1": "1. Thông tin người được đề cử",
        "dept_label": "Phòng ban / Bộ phận *",
        "nominee_label": "Chọn tên nhân sự *",
        "nominee_placeholder": "Chọn tên từ danh sách...",

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
        "prev_btn": "Quay lại",
        "submit_btn": "Hoàn Tất & Gửi Đề Cử",
        "err_fields": "Vui lòng chọn đầy đủ phòng ban và tên người được đề cử!",
        "err_no_names": "Phòng ban này chưa có tên nhân sự trong danh sách cấu hình!",
        "err_evidence": "Vui lòng điền minh chứng cho tiêu chí này!",

        "thank_you_title": "Cảm Ơn Bạn Đã Đề Cử!",
        "thank_you_msg": "Thông tin đề cử của bạn đã được ghi nhận thành công từ thiết bị này. Mỗi thiết bị chỉ được thực hiện đề cử 1 lần duy nhất.",
        "locked_title": "Thiết Bị Đã Thực Hiện Đề Cử",
        "locked_msg": "Thiết bị này đã hoàn tất việc gửi đề cử trước đó. Cảm ơn sự tham gia đóng góp của bạn vào chương trình!",

        "admin_sec": "Quản Trị Viên (Xem & Tải Dữ Liệu)",
        "admin_pass_label": "Nhập mật khẩu quản trị",
        "admin_success": "Xác thực thành công!",
        "total_nominations": "Tổng số lượt đề cử:",
        "reset_devices_btn": "Đặt Lại Danh Sách Thiết Bị (Cho phép đề cử lại)",
        "reset_devices_success": "Đã reset thiết bị thành công! Các thiết bị có thể làm mới trang để đề cử lại.",
        "download_btn": "Tải Bảng Dữ Liệu Gốc (CSV)",
        "download_pdf_btn": "Tải Báo Cáo PDF Dashboard",
        "summary_table_title": "Bảng Tổng Hợp Số Lượt Đề Cử & Điểm Trung Bình:",
        "raw_table_title": "Bảng Dữ Liệu Gốc Các Đề Cử:",
        "chart_votes_title": "Top 10 Đề Cử Nhiều Nhất (Nhiều Lượt Bình Chọn Nhất)",
        "chart_scores_title": "Top 10 Đề Cử Điểm Trung Bình Cao Nhất",
        "chart_pie_title": "Tỷ Lệ Phân Bổ Bình Chọn (Phần Trăm Lượt Đề Cử)",
        "leaderboard_title": "Bảng Xếp Hạng (Top 10 Đề Cử Hàng Đầu)",
        "err_pass": "Mật khẩu không chính xác!"
    },
    "English": {
        "title": "Synergy Star \nNomination Portal",
        "welcome_heading": "Welcome to the Award Nomination Portal",
        "welcome_desc": "Recognizing top 3 teammates,\nwho connect our synergies,\nthat bring beyond the regular working objectives across organizations",
        "start_btn": "Start Nomination",

        "p2_title": "Finals Voting Portal (Phase 2)",
        "p2_welcome_heading": "Welcome to the Top 10 Finals Voting",
        "p2_welcome_desc": "Explore the profiles of our top 10 finalists and cast your final vote and scores to celebrate excellence.",
        "p2_start_btn": "Start Voting",
        "p2_select_label": "Select Finalist Nominee *",
        "p2_submit_btn": "Confirm & Submit Vote",
        "p2_thank_you_title": "Thank You for Voting!",
        "p2_thank_you_msg": "Your final vote and scoring have been successfully recorded.",
        "p2_locked_title": "Vote Already Submitted",
        "p2_locked_msg": "A vote has already been submitted from this device for Phase 2. Thank you for your participation!",

        "portal_closed_title": "Nomination Portal Temporarily Closed",
        "portal_closed_msg": "The nomination and voting portal is currently closed by the administrator. Please check back later!",

        "step_indicator": "Step {} of 5",
        "sec1": "1. Nominee Information",
        "dept_label": "Department *",
        "nominee_label": "Select Nominee Name *",
        "nominee_placeholder": "Select name from list...",

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
        "prev_btn": "Back",
        "submit_btn": "Submit Nomination",
        "err_fields": "Please select both a department and a nominee name!",
        "err_no_names": "This department does not have any names listed in the configuration yet!",
        "err_evidence": "Please provide evidence for this criterion!",

        "thank_you_title": "Thank You for Your Nomination!",
        "thank_you_msg": "Your nomination has been recorded successfully from this device. Each device is permitted one submission only.",
        "locked_title": "Nomination Already Submitted",
        "locked_msg": "A nomination has already been submitted from this device. Thank you for your participation!",

        "admin_sec": "Administrator (View & Download Data)",
        "admin_pass_label": "Enter admin password",
        "admin_success": "Authentication successful!",
        "total_nominations": "Total nominations:",
        "reset_devices_btn": "Reset Device Registry (Allow Re-nomination)",
        "reset_devices_success": "Device registry successfully reset! Devices can now reload and submit again.",
        "download_btn": "Download Raw Data (CSV)",
        "download_pdf_btn": "Download Dashboard PDF Report",
        "summary_table_title": "Summary Table of Total Votes & Average Scores:",
        "raw_table_title": "Raw Nominations Table:",
        "chart_votes_title": "Top 10 Most Voted Nominees",
        "chart_scores_title": "Top 10 Highest Average Scores",
        "chart_pie_title": "Vote Allocation Percentage (Pie Chart)",
        "leaderboard_title": "Leaderboard (Top 10 Nominees)",
        "err_pass": "Incorrect password!"
    },
    "Deutsch (German)": {
        "title": "Mitarbeiter-Nominierungsportal",
        "welcome_heading": "Willkommen beim Nominierungsportal",
        "welcome_desc": "Dieses Programm ehrt herausragende Einzelpersonen mit außergewöhnlichen Beiträgen.\nReichen Sie jetzt Ihre Nominierung ein!",
        "start_btn": "Nominierung Starten",

        "p2_title": "Finalabstimmungsportal (Phase 2)",
        "p2_welcome_heading": "Willkommen zur Top-10-Finalabstimmung",
        "p2_welcome_desc": "Entdecken Sie die Profile unserer Top-10-Finalisten und geben Sie Ihre Stimme und Bewertung ab.",
        "p2_start_btn": "Abstimmung Starten",
        "p2_select_label": "Finalisten auswählen *",
        "p2_submit_btn": "Stimme Bestätigen & Absenden",
        "p2_thank_you_title": "Vielen Dank für Ihre Stimme!",
        "p2_thank_you_msg": "Ihre Finalstimme und Bewertung wurden erfolgreich erfasst.",
        "p2_locked_title": "Stimme Bereits Abgeschlossen",
        "p2_locked_msg": "Von diesem Gerät wurde bereits eine Stimme für Phase 2 abgegeben.",

        "portal_closed_title": "Nominierungsportal Vorübergehend Geschlossen",
        "portal_closed_msg": "Das Nominierungs- und Abstimmungsportal wurde vom Administrator vorübergehend geschlossen. Bitte versuchen Sie es später noch einmal!",

        "step_indicator": "Schritt {} von 5",
        "sec1": "1. Informationen zum Nominierten",
        "dept_label": "Abteilung *",
        "nominee_label": "Namen des Nominierten auswählen *",
        "nominee_placeholder": "Namen aus der Liste auswählen...",

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
        "prev_btn": "Zurück",
        "submit_btn": "Nominierung Absenden",
        "err_fields": "Bitte wählen Sie sowohl eine Abteilung als auch einen Namen aus!",
        "err_no_names": "Diese Abteilung hat noch keine Namen in der Konfiguration!",
        "err_evidence": "Bitte geben Sie für dieses Kriterium Nachweise an!",

        "thank_you_title": "Vielen Dank für Ihre Nominierung!",
        "thank_you_msg": "Ihre Nominierung wurde erfolgreich von diesem Gerät erfasst. Jedes Gerät darf nur einmal einreichen.",
        "locked_title": "Nominierung Bereits Abgeschlossen",
        "locked_msg": "Von diesem Gerät wurde bereits eine Nominierung eingereicht. Vielen Dank für Ihre Teilnahme!",

        "admin_sec": "Administrator (Daten anzeigen & herunterladen)",
        "admin_pass_label": "Admin-Passwort eingeben",
        "admin_success": "Authentifizierung erfolgreich!",
        "total_nominations": "Gesamtzahl der Nominierungen:",
        "reset_devices_btn": "Geräteliste zurücksetzen (Erneut nominieren erlauben)",
        "reset_devices_success": "Geräteliste erfolgreich zurückgesetzt! Geräte können die Seite neu laden, um erneut zu nominieren.",
        "download_btn": "Rohdaten herunterladen (CSV)",
        "download_pdf_btn": "Dashboard PDF-Bericht herunterladen",
        "summary_table_title": "Zusammenfassung der Stimmen & Durchschnittswerte:",
        "raw_table_title": "Rohdaten-Tabelle der Nominierungen:",
        "chart_votes_title": "Top 10 Nominierte nach Stimmen",
        "chart_scores_title": "Top 10 Höchste Durchschnittswerte",
        "chart_pie_title": "Stimmverteilung (Prozentdiagramm)",
        "leaderboard_title": "Bestenliste (Top 10 Nominierte)",
        "err_pass": "Falsches Passwort!"
    }
}

# Sidebar Language Selector
selected_lang_key = st.sidebar.selectbox("🌐 Language / Ngôn ngữ / Sprache", list(TRANSLATIONS.keys()))
t = TRANSLATIONS[selected_lang_key]


def init_data_files():
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
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=expected_columns)
        df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')

    expected_columns_p2 = [
        "Thời Gian",
        "Tên Ứng Viên",
        "Phòng Ban",
        "Điểm Trung Bình",
        "Điểm Hợp Tác",
        "Điểm Đổi Mới",
        "Điểm Văn Hóa & Giá Trị",
        "Điểm Trách Nhiệm",
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


header_title_text = t['p2_title'] if PHASE_2_ACTIVE else t['title']
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
# PORTAL CLOSED CHECK OR ACTIVE FLOW
# ==========================================
if PORTAL_CLOSED:
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
    # PHASE 2: FINALIST VOTING & SCORING FLOW
    # ==========================================
    if PHASE_2_ACTIVE:
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

            finalist_names = [f["name"] for f in TOP_10_FINALISTS]


            def update_p2_selection():
                st.session_state["p2_selected_nominee"] = st.session_state["p2_selectbox"]


            selected_finalist_name = st.selectbox(
                t["p2_select_label"],
                options=finalist_names,
                index=finalist_names.index(st.session_state["p2_selected_nominee"]) if st.session_state[
                                                                                           "p2_selected_nominee"] in finalist_names else 0,
                key="p2_selectbox",
                on_change=update_p2_selection
            )

            current_finalist = next((f for f in TOP_10_FINALISTS if f["name"] == st.session_state["p2_selected_nominee"]),
                                    TOP_10_FINALISTS[0])

            # Render Info Card (Profile Picture & Biography)
            st.markdown(f"""
                <div style="background: rgba(42, 35, 15, 0.7); border: 1px solid rgba(245, 158, 11, 0.4); border-radius: 12px; padding: 1.5rem; margin-top: 1rem; margin-bottom: 1.5rem;">
                    <div style="display: flex; gap: 1.5rem; align-items: center; flex-wrap: wrap;">
                        <div style="flex: 0 0 120px; text-align: center;">
                            <img src="{current_finalist['image']}" alt="Nominee Photo" style="width: 110px; height: 110px; border-radius: 50%; object-fit: cover; border: 2px solid #F59E0B;" />
                        </div>
                        <div style="flex: 1; min-width: 200px;">
                            <h3 style="color: #FDE047; margin-bottom: 0.2rem;">{current_finalist['name']}</h3>
                            <p style="color: #F7C657; font-size: 0.95rem; font-style: italic; margin-bottom: 0.5rem;">{current_finalist['department']}</p>
                            <p style="color: #FFF; font-size: 1.05rem; line-height: 1.5;">{current_finalist['bio']}</p>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            # 4 Criteria Sliders for Phase 2 (without evidence text fields)
            with st.form(key="p2_scoring_form"):
                st.markdown(f"### {t['collab_title']}")
                st.caption(t["collab_desc"])
                p2_score_collab = st.slider(t["collab_slider"], min_value=0, max_value=5,
                                            value=st.session_state["p2_score_collab"])
                st.markdown(get_slider_glow_style(p2_score_collab), unsafe_allow_html=True)

                st.markdown("---")
                st.markdown(f"### {t['innov_title']}")
                st.caption(t["innov_desc"])
                p2_score_innov = st.slider(t["innov_slider"], min_value=0, max_value=5,
                                           value=st.session_state["p2_score_innov"])
                st.markdown(get_slider_glow_style(p2_score_innov), unsafe_allow_html=True)

                st.markdown("---")
                st.markdown(f"### {t['culture_title']}")
                st.caption(t["culture_desc"])
                p2_score_culture = st.slider(t["culture_slider"], min_value=0, max_value=5,
                                             value=st.session_state["p2_score_culture"])
                st.markdown(get_slider_glow_style(p2_score_culture), unsafe_allow_html=True)

                st.markdown("---")
                st.markdown(f"### {t['acc_title']}")
                st.caption(t["acc_desc"])
                p2_score_acc = st.slider(t["acc_slider"], min_value=0, max_value=5, value=st.session_state["p2_score_acc"])
                st.markdown(get_slider_glow_style(p2_score_acc), unsafe_allow_html=True)

                st.write("")
                p2_submit_clicked = st.form_submit_button(t["p2_submit_btn"], use_container_width=True, type="primary")

            if p2_submit_clicked:
                avg_score_p2 = round((p2_score_collab + p2_score_innov + p2_score_culture + p2_score_acc) / 4.0, 2)

                selected_record = {
                    "Thời Gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Tên Ứng Viên": current_finalist['name'],
                    "Phòng Ban": current_finalist['department'],
                    "Điểm Trung Bình": avg_score_p2,
                    "Điểm Hợp Tác": p2_score_collab,
                    "Điểm Đổi Mới": p2_score_innov,
                    "Điểm Văn Hóa & Giá Trị": p2_score_culture,
                    "Điểm Trách Nhiệm": p2_score_acc,
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
    # PHASE 1: STANDARD NOMINATION FLOW
    # ==========================================
    else:
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

        elif st.session_state["step"] == 1:
            st.subheader(t["sec1"])

            dept_options = list(DEPARTMENT_NAMES.keys())


            def update_department_selection():
                st.session_state["department"] = st.session_state["dept_selectbox"]
                st.session_state["nominee_name"] = ""


            selected_dept = st.selectbox(
                t["dept_label"],
                options=dept_options,
                index=dept_options.index(st.session_state["department"]) if st.session_state[
                                                                                "department"] in dept_options else 0,
                key="dept_selectbox",
                on_change=update_department_selection
            )

            current_dept = st.session_state["department"]
            available_names = DEPARTMENT_NAMES.get(current_dept, [])

            with st.form(key="step1_form"):
                if available_names:
                    try:
                        default_name_index = available_names.index(st.session_state["nominee_name"]) if st.session_state[
                                                                                                            "nominee_name"] in available_names else 0
                    except ValueError:
                        default_name_index = 0

                    nominee_name = st.selectbox(
                        t["nominee_label"],
                        options=available_names,
                        index=default_name_index
                    )
                else:
                    st.warning(t["err_no_names"])
                    nominee_name = ""

                st.write("")
                col_back, col_next = st.columns([1, 1])
                with col_next:
                    next_clicked = st.form_submit_button(t["next_btn"], type="primary")

            if next_clicked:
                if not current_dept or not nominee_name:
                    st.error(t["err_fields"])
                elif not available_names:
                    st.warning(t["err_no_names"])
                else:
                    st.session_state["department"] = current_dept
                    st.session_state["nominee_name"] = nominee_name
                    st.session_state["step"] = 2
                    st.rerun()

        elif st.session_state["step"] == 2:
            with st.form(key="step2_form"):
                if IMG_COLLAB:
                    st.image(IMG_COLLAB, use_container_width=True)
                st.markdown(f"### {t['collab_title']}")
                st.caption(t["collab_desc"])
                score_collab = st.slider(t["collab_slider"], min_value=0, max_value=5,
                                         value=st.session_state["score_collab"])
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

        elif st.session_state["step"] == 5:
            with st.form(key="step5_form"):
                if IMG_ACC:
                    st.image(IMG_ACC, use_container_width=True)
                st.markdown(f"### {t['acc_title']}")
                st.caption(t["acc_desc"])
                score_acc = st.slider(t["acc_slider"], min_value=0, max_value=5, value=st.session_state["score_acc"])
                st.markdown(get_slider_glow_style(score_acc), unsafe_allow_html=True)
                evidence_acc = st.text_area(t["acc_evidence"], value=st.session_state["evidence_acc"],
                                            placeholder=t["acc_ph"])

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

                    current_registry = load_device_registry(DEVICE_REGISTRY_FILE)
                    if DEVICE_ID not in current_registry:
                        current_registry.append(DEVICE_ID)
                        save_device_registry(DEVICE_REGISTRY_FILE, current_registry)

                    st.session_state["step"] = 6
                    st.rerun()

        elif st.session_state["step"] == 6:
            if IMG_THANKYOU:
                st.image(IMG_THANKYOU, use_container_width=True)
            st.markdown(f"""
                <div style="text-align: center; padding: 1rem 0;">
                    <h2 style="color: #4ADE80; font-size: 2rem; margin-bottom: 1rem;">{t['thank_you_title']}</h2>
                    <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem;">{t['thank_you_msg']}</p>
                </div>
            """, unsafe_allow_html=True)

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

        # --- PHASE & PORTAL MANAGEMENT CONTROLS ---
        st.markdown("---")
        st.subheader("Phase Management Control")

        # Portal Close / Open Toggle Switch
        new_portal_closed_toggle = st.toggle("🛑 Close Portal (Pause Submissions & Voting)", value=PORTAL_CLOSED)
        if new_portal_closed_toggle != PORTAL_CLOSED:
            save_json_state(PORTAL_STATE_FILE, {"portal_closed": new_portal_closed_toggle})
            st.success(f"Portal Closed Status updated to: {new_portal_closed_toggle}. Reloading...")
            st.rerun()

        new_phase2_toggle = st.toggle("Enable Phase 2 Finals Voting Mode", value=PHASE_2_ACTIVE)
        if new_phase2_toggle != PHASE_2_ACTIVE:
            save_json_state(PHASE2_STATE_FILE, {"phase2_active": new_phase2_toggle})
            st.success(f"Phase 2 status updated to: {new_phase2_toggle}. Reloading...")
            st.rerun()

        col_r1, col_r2 = st.columns(2)
        with col_r1:
            if st.button("Reset Phase 1 Devices"):
                save_device_registry(DEVICE_REGISTRY_FILE, [])
                st.success("Phase 1 device registry reset!")
        with col_r2:
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
                        Số_Lượt_Bình_Chọn=("Phòng Ban", "count"),
                        Điểm_Trung_Bình=("Điểm Trung Bình", "mean")
                    ).reset_index()
                    summary_p2["Điểm_Trung_Bình"] = summary_p2["Điểm_Trung_Bình"].round(2)

                    # 1. Pie Chart showing vote allocation between the 10 finalists
                    st.markdown("#### Vote Allocation Percentage (Top 10 Finalists)")
                    total_p2_votes = summary_p2["Số_Lượt_Bình_Chọn"].sum()
                    summary_p2["Phần_Trăm"] = (summary_p2["Số_Lượt_Bình_Chọn"] / total_p2_votes) * 100 if total_p2_votes > 0 else 0

                    pie_chart_p2 = alt.Chart(summary_p2).mark_arc(innerRadius=50).encode(
                        theta=alt.Theta(field="Số_Lượt_Bình_Chọn", type="quantitative"),
                        color=alt.Color(field="Tên Ứng Viên", type="nominal", legend=alt.Legend(title="Finalist")),
                        tooltip=["Tên Ứng Viên", "Số_Lượt_Bình_Chọn", alt.Tooltip("Phần_Trăm:Q", format=".1f", title="Percentage (%)")]
                    ).properties(width=400, height=350)
                    st.altair_chart(pie_chart_p2, use_container_width=True)

                    # 2. Bar Chart showing top 3 finalists with the most votes
                    st.markdown("#### Top 3 Finalists with Most Votes")
                    top3_votes = summary_p2.sort_values(by="Số_Lượt_Bình_Chọn", ascending=False).head(3)
                    st.bar_chart(top3_votes.set_index("Tên Ứng Viên")["Số_Lượt_Bình_Chọn"])

                    # 3. Bar Chart showing top 3 finalists with the most average score
                    st.markdown("#### Top 3 Finalists with Highest Average Scores")
                    top3_scores = summary_p2.sort_values(by="Điểm_Trung_Bình", ascending=False).head(3)
                    st.bar_chart(top3_scores.set_index("Tên Ứng Viên")["Điểm_Trung_Bình"])

                    # 4. Bar Chart showing top 3 finalists with both most votes and highest average score combined ranking
                    st.markdown("#### Top 3 Finalists (Most Votes & Highest Average Score Combined)")
                    top3_combined = summary_p2.sort_values(by=["Số_Lượt_Bình_Chọn", "Điểm_Trung_Bình"], ascending=[False, False]).head(3)
                    st.bar_chart(top3_combined.set_index("Tên Ứng Viên")[["Số_Lượt_Bình_Chọn", "Điểm_Trung_Bình"]])

                    # 5. Raw Nomination Data Table for Phase 2
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

        # --- PHASE 1 ADMIN DATA SECTION ---
        if os.path.exists(DATA_FILE):
            try:
                df_raw = pd.read_csv(DATA_FILE, on_bad_lines='skip')
                st.markdown(f"### Phase 1 Nominations Summary (Total: {len(df_raw)})")

                if not df_raw.empty and "Tên Người Được Đề Cử" in df_raw.columns and "Điểm Trung Bình" in df_raw.columns:
                    summary_df = df_raw.groupby("Tên Người Được Đề Cử").agg(
                        Số_Lượt_Đề_Cử=("Điểm Trung Bình", "count"),
                        Điểm_Trung_Bình_Tổng_Thể=("Điểm Trung Bình", "mean")
                    ).reset_index()

                    summary_df["Điểm_Trung_Bình_Tổng_Thể"] = summary_df["Điểm_Trung_Bình_Tổng_Thể"].round(2)
                    summary_df = summary_df.sort_values(by=["Số_Lượt_Đề_Cử", "Điểm_Trung_Bình_Tổng_Thể"], ascending=False)

                    st.markdown(f"### {t['summary_table_title']}")
                    st.dataframe(summary_df, use_container_width=True)

                    st.markdown("---")
                    st.markdown(f"### {t['chart_votes_title']}")
                    top_votes = summary_df.sort_values(by="Số_Lượt_Đề_Cử", ascending=False).head(10)
                    st.bar_chart(top_votes.set_index("Tên Người Được Đề Cử")["Số_Lượt_Đề_Cử"])

                    st.markdown(f"### {t['leaderboard_title']}")
                    leaderboard_df = summary_df.sort_values(by=["Số_Lượt_Đề_Cử", "Điểm_Trung_Bình_Tổng_Thể"], ascending=[False, False]).head(10).reset_index(drop=True)
                    leaderboard_df.index += 1
                    st.dataframe(leaderboard_df, use_container_width=True)

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
                st.error(f"Lỗi đọc file dữ liệu: {e}")
    elif admin_password != "":
        st.error(t["err_pass"])