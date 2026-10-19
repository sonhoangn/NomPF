import os
import pandas as pd
import streamlit as st
from datetime import datetime

# --- CONFIGURABLE MEDIA ASSETS ---
BG_IMAGE_URL = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/bg.png"
IMG_WELCOME = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/bg.png"
IMG_THANKYOU = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/ty.png"
IMG_COLLAB = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/cl.png"
IMG_INNOV = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/in.png"
IMG_CULTURE = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/cv.png"
IMG_ACC = "https://raw.githubusercontent.com/sonhoangn/NomPF/refs/heads/main/ac.png"

# Configure page settings
st.set_page_config(
    page_title="Đề Cử Khen Thưởng - Employee Award 2026",
    page_icon="🏆",
    layout="centered"
)

# --- SESSION STATE INITIALIZATION ---
if "step" not in st.session_state:
    st.session_state["step"] = 0  # 0: Welcome, 1: Nominee Info, 2: Collab, 3: Innov, 4: Culture, 5: Acc, 6: Thank You

# Form data storage in session state
default_keys = {
    "nominee_name": "",
    "department": "",
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

# --- GLASSMORPHISM & BACKGROUND STYLING ---
if BG_IMAGE_URL:
    st.markdown(f"""
        <style>
        /* Anchor background wallpaper */
        .stApp {{
            background-image: url("{BG_IMAGE_URL}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
        }}

        /* Remove default background from main page padding container */
        .main .block-container {{
            background: rgba(30, 30, 30, 0.35) !important;
            backdrop-filter: blur(16px);
            padding: 2.5rem;
        }}

        /* Unified Glassmorphism Card Style for containers */
        [data-testid="stVerticalBlock"] > div:has(div.element-container) {{
            /* Target wrapper blocks if needed */
        }}

        .glass-container {{
            background: rgba(30, 30, 30, 0.35) !important;
            -webkit-backdrop-filter: blur(16px);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.1) !important;
            border-radius: 16px !important;
            box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2) !important;
            padding: 2rem !important;
            margin-bottom: 1.5rem;
        }}

        /* Input text fields styling inside glass container */
        .stTextInput > div > div > input, 
        .stTextArea > div > div > textarea {{
            background-color: rgba(255, 255, 255, 0.25) !important;
            color: rgba(255, 255, 255, 0.95) !important;
            border-radius: 8px !important;
            border: 1px solid rgba(255, 255, 255, 0.15) !important;
        }}

        /* Custom styling to make the progress bar highly visible */
        .stProgress > div > div > div > div {{
            background-color: #4ADE80 !important;
        }}

        /* Text readability fixes */
        label, .stSubheader, h1, h2, h3 {{
            color: rgba(255, 255, 255, 0.95) !important;
        }}
        .stCaption, p {{
            color: rgba(255, 255, 255, 0.8) !important;
        }}
        </style>
        """, unsafe_allow_html=True)

# --- MULTI-LANGUAGE DICTIONARY ---
TRANSLATIONS = {
    "Tiếng Việt (Vietnamese)": {
        "title": "🏆 Cổng Đề Cử Khen Thưởng",
        "subtitle": "Vui lòng điền đầy đủ thông tin đề cử cá nhân xuất sắc theo các tiêu chí bên dưới.",
        "welcome_heading": "Chào Mừng Đến Với Cổng Đề Cử",
        "welcome_desc": "Chương trình vinh danh các cá nhân xuất sắc đã có những đóng góp nổi bật. Hãy cùng gửi đề cử của bạn!",
        "start_btn": "🚀 Bắt Đầu Đề Cử",

        "step_indicator": "Bước {} / 5",
        "sec1": "1. Thông tin người được đề cử",
        "nominee_label": "Tên người được đề cử *",
        "nominee_placeholder": "Nguyễn Văn A",
        "dept_label": "Phòng ban / Bộ phận *",
        "dept_placeholder": "Kinh doanh / CNTT",

        "collab_title": "🤝 1. Hợp Tác (Collaboration)",
        "collab_desc": "Mô tả: Làm việc nhóm hiệu quả, sẵn sàng hỗ trợ đồng nghiệp và phối hợp tốt giữa các phòng ban.",
        "collab_slider": "Điểm Hợp Tác",
        "collab_evidence": "Minh chứng / Ví dụ cụ thể cho tiêu chí Hợp Tác *",
        "collab_ph": "Nêu rõ tình huống hoặc dự án phối hợp thành công...",

        "innov_title": "💡 2. Đổi Mới Sáng Tạo (Innovation)",
        "innov_desc": "Mô tả: Đưa ra ý tưởng mới, cải tiến quy trình làm việc giúp nâng cao năng suất hoặc tiết kiệm chi phí.",
        "innov_slider": "Điểm Đổi Mới",
        "innov_evidence": "Minh chứng / Ví dụ cụ thể cho tiêu chí Đổi Mới *",
        "innov_ph": "Mô tả ý tưởng hoặc cải tiến đã được áp dụng...",

        "culture_title": "🌟 3. Văn Hóa & Giá Trị (Culture & Value)",
        "culture_desc": "Mô tả: Thể hiện rõ các giá trị cốt lõi của công ty, lan tỏa năng lượng tích cực và xây dựng môi trường làm việc tốt.",
        "culture_slider": "Điểm Văn Hóa & Giá Trị",
        "culture_evidence": "Minh chứng / Ví dụ cụ thể cho tiêu chí Văn Hóa & Giá Trị *",
        "culture_ph": "Nêu ví dụ về hành động thể hiện giá trị văn hóa...",

        "acc_title": "🎯 4. Trách Nhiệm (Accountability)",
        "acc_desc": "Mô tả: Làm chủ công việc, cam kết hoàn thành mục tiêu đúng hạn và chịu trách nhiệm về kết quả.",
        "acc_slider": "Điểm Trách Nhiệm",
        "acc_evidence": "Minh chứng / Ví dụ cụ thể cho tiêu chí Trách Nhiệm *",
        "acc_ph": "Nêu ví dụ về tinh thần trách nhiệm trong công việc...",

        "next_btn": "Tiếp theo ➔",
        "prev_btn": "⬅️ Quay lại",
        "submit_btn": "🚀 Hoàn Tất & Gửi Đề Cử",
        "err_fields": "⚠️ Vui lòng điền đầy đủ Tên người được đề cử và Phòng ban!",
        "err_evidence": "⚠️ Vui lòng điền minh chứng cho tiêu chí này!",

        "thank_you_title": "🎉 Cảm Ơn Bạn Đã Đề Cử!",
        "thank_you_msg": "Thông tin đề cử của bạn đã được ghi nhận thành công. Đóng góp của bạn giúp tôn vinh những cá nhân xuất sắc!",
        "submit_another": "➕ Đề Cử Thêm Cá Nhân Khác",

        "admin_sec": "🔒 Quản Trị Viên (Xem & Tải Dữ Liệu)",
        "admin_pass_label": "Nhập mật khẩu quản trị",
        "admin_success": "Xác thực thành công!",
        "total_nominations": "Tổng số lượt đề cử:",
        "download_btn": "📥 Tải Bảng Dữ Liệu (CSV)",
        "err_pass": "Mật khẩu không chính xác!"
    },
    "English": {
        "title": "🏆 Employee Award Nomination Portal",
        "subtitle": "Please fill in the nomination details for outstanding individuals based on the criteria below.",
        "welcome_heading": "Welcome to the Award Nomination Portal",
        "welcome_desc": "This program honors outstanding individuals with exceptional contributions. Start submitting your nominations now!",
        "start_btn": "🚀 Start Nomination",

        "step_indicator": "Step {} of 5",
        "sec1": "1. Nominee Information",
        "nominee_label": "Nominee Name *",
        "nominee_placeholder": "John Doe",
        "dept_label": "Department *",
        "dept_placeholder": "Sales / IT",

        "collab_title": "🤝 1. Collaboration",
        "collab_desc": "Description: Effective teamwork, willingness to support colleagues, and good cross-departmental coordination.",
        "collab_slider": "Collaboration Score",
        "collab_evidence": "Evidence / Specific example for Collaboration *",
        "collab_ph": "Describe the successful collaboration scenario or project...",

        "innov_title": "💡 2. Innovation",
        "innov_desc": "Description: Proposing new ideas, improving workflows to increase productivity or save costs.",
        "innov_slider": "Innovation Score",
        "innov_evidence": "Evidence / Specific example for Innovation *",
        "innov_ph": "Describe the idea or workflow improvement implemented...",

        "culture_title": "🌟 3. Culture & Value",
        "culture_desc": "Description: Clearly demonstrating core company values, spreading positive energy, and building a great work environment.",
        "culture_slider": "Culture & Value Score",
        "culture_evidence": "Evidence / Specific example for Culture & Value *",
        "culture_ph": "Provide examples of actions reflecting cultural values...",

        "acc_title": "🎯 4. Accountability",
        "acc_desc": "Description: Taking ownership of work, committing to meeting goals on time, and taking responsibility for outcomes.",
        "acc_slider": "Accountability Score",
        "acc_evidence": "Evidence / Specific example for Accountability *",
        "acc_ph": "Provide examples of strong responsibility in work...",

        "next_btn": "Next ➔",
        "prev_btn": "⬅️ Back",
        "submit_btn": "🚀 Submit Nomination",
        "err_fields": "⚠️ Please fill in the Nominee Name and Department!",
        "err_evidence": "⚠️ Please provide evidence for this criterion!",

        "thank_you_title": "🎉 Thank You for Your Nomination!",
        "thank_you_msg": "Your nomination has been recorded successfully. Your contribution helps recognize outstanding individuals and teams!",
        "submit_another": "➕ Submit Another Nomination",

        "admin_sec": "🔒 Administrator (View & Download Data)",
        "admin_pass_label": "Enter admin password",
        "admin_success": "Authentication successful!",
        "total_nominations": "Total nominations:",
        "download_btn": "📥 Download Data (CSV)",
        "err_pass": "Incorrect password!"
    },
    "Deutsch (German)": {
        "title": "🏆 Mitarbeiter-Nominierungsportal",
        "subtitle": "Bitte füllen Sie die Nominierungsdetails cho herausragende Einzelpersonen basierend auf den folgenden Kriterien aus.",
        "welcome_heading": "Willkommen beim Nominierungsportal",
        "welcome_desc": "Dieses Programm ehrt herausragende Einzelpersonen mit außergewöhnlichen Beiträgen. Reichen Sie jetzt Ihre Nominierung ein!",
        "start_btn": "🚀 Nominierung Starten",

        "step_indicator": "Schritt {} von 5",
        "sec1": "1. Informationen zum Nominierten",
        "nominee_label": "Name des Nominierten *",
        "nominee_placeholder": "Max Mustermann",
        "dept_label": "Abteilung *",
        "dept_placeholder": "Vertrieb / IT",

        "collab_title": "🤝 1. Zusammenarbeit (Collaboration)",
        "collab_desc": "Beschreibung: Effektive Teamarbeit, Bereitschaft zur Unterstützung von Kollegen und gute abteilungsübergreifende Koordination.",
        "collab_slider": "Zusammenarbeit Bewertung",
        "collab_evidence": "Nachweis / Konkretes Beispiel für Zusammenarbeit *",
        "collab_ph": "Beschreiben Sie das erfolgreiche Kooperationsszenario hoặc Projekt...",

        "innov_title": "💡 2. Innovation",
        "innov_desc": "Beschreibung: Vorschlagen neuer Ideen, Verbesserung von Arbeitsabläufen zur Steigerung der Produktivität hoặc Kosteneinsparung.",
        "innov_slider": "Innovation Bewertung",
        "innov_evidence": "Nachweis / Konkretes Beispiel für Innovation *",
        "innov_ph": "Beschreiben Sie die umgesetzte Idee hoặc Prozessverbesserung...",

        "culture_title": "🌟 3. Kultur & Werte (Culture & Value)",
        "culture_desc": "Beschreibung: Deutliche Demonstration der Unternehmenswerte, Verbreitung positiver Energie và Aufbau eines großartigen Arbeitsumfelds.",
        "culture_slider": "Kultur & Werte Bewertung",
        "culture_evidence": "Nachweis / Konkretes Beispiel für Kultur & Werte *",
        "culture_ph": "Geben Sie Beispiele für Handlungen an, die kulturelle Werte widerspiegeln...",

        "acc_title": "🎯 4. Verantwortlichkeit (Accountability)",
        "acc_desc": "Beschreibung: Übernahme der Verantwortung cho die Arbeit, Verpflichtung zur termingerechten Erreichung von Zielen và Verantwortung cho Ergebnisse.",
        "acc_slider": "Verantwortlichkeit Bewertung",
        "acc_evidence": "Nachweis / Konkretes Beispiel für Verantwortlichkeit *",
        "acc_ph": "Geben Sie Beispiele cho starkes Verantwortungsbewusstsein bei der Arbeit an...",

        "next_btn": "Weiter ➔",
        "prev_btn": "⬅️ Zurück",
        "submit_btn": "🚀 Nominierung Absenden",
        "err_fields": "⚠️ Bitte füllen Sie den Namen des Nominierten und die Abteilung aus!",
        "err_evidence": "⚠️ Bitte geben Sie cho dieses Kriterium Nachweise an!",

        "thank_you_title": "🎉 Vielen Dank für Ihre Nominierung!",
        "thank_you_msg": "Ihre Nominierung wurde erfolgreich erfasst. Ihr Beitrag hilft dabei, herausragende Einzelpersonen und Teams zu würdigen!",
        "submit_another": "➕ Weitere Nominierung einreichen",

        "admin_sec": "🔒 Administrator (Daten anzeigen & herunterladen)",
        "admin_pass_label": "Admin-Passwort eingeben",
        "admin_success": "Authentifizierung erfolgreich!",
        "total_nominations": "Gesamtzahl der Nominierungen:",
        "download_btn": "📥 Daten herunterladen (CSV)",
        "err_pass": "Falsches Passwort!"
    }
}

# Sidebar Language Selector
selected_lang_key = st.sidebar.selectbox("🌐 Language / Ngôn ngữ / Sprache", list(TRANSLATIONS.keys()))
t = TRANSLATIONS[selected_lang_key]

# Data File Setup
DATA_FILE = "danh_sach_de_cu.csv"

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

# Header Section with Glassmorphism Card
st.markdown(f"""
    <div style="
        background: rgba(30, 30, 30, 0.35);
        -webkit-backdrop-filter: blur(16px);
        backdrop-filter: blur(16px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        text-align: center;
    ">
        <h1 style="color: rgba(255, 255, 255, 1.0); margin-bottom: 0.5rem; font-size: 2.2rem;">{t['title']}</h1>
        <p style="color: rgba(255, 255, 255, 0.8); font-size: 1.05rem; margin: 0;">{t['subtitle']}</p>
    </div>
""", unsafe_allow_html=True)

# Helper function for navigation buttons & progress bar using Streamlit containers
def render_nav_buttons(show_back=True, next_label=None, is_submit=False):
    current_step = st.session_state["step"]
    progress_val = min(max(current_step / 5.0, 0.0), 1.0)
    st.progress(progress_val)
    st.caption(t["step_indicator"].format(current_step))
    st.write("")

    col_back, col_next = st.columns([1, 1])
    with col_back:
        if show_back:
            if st.button(t["prev_btn"], key=f"prev_{st.session_state['step']}"):
                st.session_state["step"] -= 1
                st.rerun()
    with col_next:
        label = next_label if next_label else (t["submit_btn"] if is_submit else t["next_btn"])
        return st.button(label, key=f"next_{st.session_state['step']}", type="primary")

# ==========================================
# SCREEN 0: WELCOME SCREEN
# ==========================================
if st.session_state["step"] == 0:
    with st.container(border=True):
        if IMG_WELCOME:
            st.image(IMG_WELCOME, use_container_width=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0;">
                <h2 style="font-size: 1.8rem; margin-bottom: 1rem;">{t['welcome_heading']}</h2>
                <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem;">{t['welcome_desc']}</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button(t["start_btn"], use_container_width=True, type="primary"):
            st.session_state["step"] = 1
            st.rerun()

# ==========================================
# SCREEN 1: NOMINEE DETAILS
# ==========================================
elif st.session_state["step"] == 1:
    with st.container(border=True):
        st.subheader(t["sec1"])
        nominee_name = st.text_input(t["nominee_label"], value=st.session_state["nominee_name"], placeholder=t["nominee_placeholder"])
        department = st.text_input(t["dept_label"], value=st.session_state["department"], placeholder=t["dept_placeholder"])

    if render_nav_buttons(show_back=False):
        if not nominee_name.strip() or not department.strip():
            st.error(t["err_fields"])
        else:
            st.session_state["nominee_name"] = nominee_name
            st.session_state["department"] = department
            st.session_state["step"] = 2
            st.rerun()

# ==========================================
# SCREEN 2: COLLABORATION
# ==========================================
elif st.session_state["step"] == 2:
    with st.container(border=True):
        if IMG_COLLAB:
            st.image(IMG_COLLAB, use_container_width=True)
        st.markdown(f"### {t['collab_title']}")
        st.caption(t["collab_desc"])
        score_collab = st.slider(t["collab_slider"], min_value=0, max_value=5, value=st.session_state["score_collab"])
        evidence_collab = st.text_area(t["collab_evidence"], value=st.session_state["evidence_collab"], placeholder=t["collab_ph"])

    if render_nav_buttons():
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
    with st.container(border=True):
        if IMG_INNOV:
            st.image(IMG_INNOV, use_container_width=True)
        st.markdown(f"### {t['innov_title']}")
        st.caption(t["innov_desc"])
        score_innov = st.slider(t["innov_slider"], min_value=0, max_value=5, value=st.session_state["score_innov"])
        evidence_innov = st.text_area(t["innov_evidence"], value=st.session_state["evidence_innov"], placeholder=t["innov_ph"])

    if render_nav_buttons():
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
    with st.container(border=True):
        if IMG_CULTURE:
            st.image(IMG_CULTURE, use_container_width=True)
        st.markdown(f"### {t['culture_title']}")
        st.caption(t["culture_desc"])
        score_culture = st.slider(t["culture_slider"], min_value=0, max_value=5, value=st.session_state["score_culture"])
        evidence_culture = st.text_area(t["culture_evidence"], value=st.session_state["evidence_culture"], placeholder=t["culture_ph"])

    if render_nav_buttons():
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
    with st.container(border=True):
        if IMG_ACC:
            st.image(IMG_ACC, use_container_width=True)
        st.markdown(f"### {t['acc_title']}")
        st.caption(t["acc_desc"])
        score_acc = st.slider(t["acc_slider"], min_value=0, max_value=5, value=st.session_state["score_acc"])
        evidence_acc = st.text_area(t["acc_evidence"], value=st.session_state["evidence_acc"], placeholder=t["acc_ph"])

    if render_nav_buttons(is_submit=True):
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

            st.session_state["step"] = 6
            st.rerun()

# ==========================================
# SCREEN 6: THANK YOU SCREEN
# ==========================================
elif st.session_state["step"] == 6:
    with st.container(border=True):
        if IMG_THANKYOU:
            st.image(IMG_THANKYOU, use_container_width=True)
        st.markdown(f"""
            <div style="text-align: center; padding: 1rem 0;">
                <h2 style="color: #4ADE80; font-size: 2rem; margin-bottom: 1rem;">{t['thank_you_title']}</h2>
                <p style="font-size: 1.1rem; line-height: 1.6; margin-bottom: 1.5rem;">{t['thank_you_msg']}</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button(t["submit_another"], use_container_width=True, type="primary"):
            for key, default_val in default_keys.items():
                st.session_state[key] = default_val
            st.session_state["step"] = 0
            st.rerun()

# ==========================================
# ANCHORED ADMINISTRATOR LOGIN PANEL
# ==========================================
st.divider()
with st.expander(t["admin_sec"]):
    admin_password = st.text_input(t["admin_pass_label"], type="password", key="admin_pass_input")

    if admin_password == "MO-LQN":
        st.success(t["admin_success"])
        if os.path.exists(DATA_FILE):
            try:
                df_data = pd.read_csv(DATA_FILE, on_bad_lines='skip')
                st.write(f"**{t['total_nominations']}** {len(df_data)}")
                st.dataframe(df_data)

                csv_data = df_data.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
                st.download_button(
                    label=t["download_btn"],
                    data=csv_data,
                    file_name=f"danh_sach_de_cu_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            except Exception as e:
                st.error(f"⚠️ Lỗi đọc file dữ liệu: {e}")
                st.info("💡 Bạn có thể xóa file `danh_sach_de_cu.csv` để ứng dụng khởi tạo lại bảng dữ liệu mới.")
    elif admin_password != "":
        st.error(t["err_pass"])