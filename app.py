import os
import pandas as pd
import streamlit as st
from datetime import datetime

# --- CONFIGURABLE MEDIA ASSETS ---
# Replace these URLs/paths with your custom image links or local file paths
BG_IMAGE_URL = "bg.png"  # e.g., "https://images.unsplash.com/photo-..." or "background.jpg"
IMG_COLLAB = "https://via.placeholder.com/600x150?text=Collaboration"
IMG_INNOV = "https://via.placeholder.com/600x150?text=Innovation"
IMG_CULTURE = "https://via.placeholder.com/600x150?text=Culture+and+Values"
IMG_ACC = "https://via.placeholder.com/600x150?text=Accountability"

# Configure page settings
st.set_page_config(
    page_title="Đề Cử Khen Thưởng - Employee Award 2026",
    page_icon="🏆",
    layout="centered"
)

# Apply Background Image CSS if provided
if BG_IMAGE_URL:
    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("{BG_IMAGE_URL}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed; /* <-- This keeps the wallpaper fixed while scrolling */
        }}
        .main .block-container {{
            background-color: rgba(255, 255, 255, 0.92);
            padding: 2.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }}
        </style>
        """, unsafe_allow_html=True)

# --- MULTI-LANGUAGE DICTIONARY ---
TRANSLATIONS = {
    "Tiếng Việt (Vietnamese)": {
        "sidebar_lang": "🌐 Ngôn ngữ / Language",
        "title": "🏆 Cổng Đề Cử Khen Thưởng",
        "subtitle": "Vui lòng điền đầy đủ thông tin đề cử cá nhân/tập thể xuất sắc theo các tiêu chí bên dưới.",
        "sec1": "1. Thông tin chung",
        "nominee_label": "Tên người/tập thể được đề cử *",
        "nominee_placeholder": "Nguyễn Văn A",
        "dept_label": "Phòng ban / Bộ phận *",
        "dept_placeholder": "Kinh doanh / CNTT",
        "sec2": "2. Đánh giá theo tiêu chí (Thang điểm 0 - 5)",

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

        "submit_btn": "🚀 Gửi Đề Cử",
        "err_fields": "⚠️ Vui lòng điền đầy đủ Tên người được đề cử và Phòng ban!",
        "err_evidence": "⚠️ Vui lòng điền minh chứng cho tất cả 4 tiêu chí đánh giá!",
        "success_msg": "✅ Gửi đề cử thành công! Cảm ơn bạn đã đóng góp.",

        "admin_sec": "🔒 Quản Trị Viên (Xem & Tải Dữ Liệu)",
        "admin_pass_label": "Nhập mật khẩu quản trị",
        "admin_success": "Xác thực thành công!",
        "total_nominations": "Tổng số lượt đề cử:",
        "download_btn": "📥 Tải Bảng Dữ Liệu (CSV)",
        "err_pass": "Mật khẩu không chính xác!"
    },
    "English": {
        "sidebar_lang": "🌐 Language",
        "title": "🏆 Employee Award Nomination Portal",
        "subtitle": "Please fill in the nomination details for outstanding individuals or teams based on the criteria below.",
        "sec1": "1. General Information",
        "nominee_label": "Nominee Name / Team Name *",
        "nominee_placeholder": "John Doe",
        "dept_label": "Department *",
        "dept_placeholder": "Sales / IT",
        "sec2": "2. Criteria Evaluation (Score 0 - 5)",

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

        "submit_btn": "🚀 Submit Nomination",
        "err_fields": "⚠️ Please fill in the Nominee Name and Department!",
        "err_evidence": "⚠️ Please provide evidence for all 4 criteria!",
        "success_msg": "✅ Nomination submitted successfully! Thank you for your contribution.",

        "admin_sec": "🔒 Administrator (View & Download Data)",
        "admin_pass_label": "Enter admin password",
        "admin_success": "Authentication successful!",
        "total_nominations": "Total nominations:",
        "download_btn": "📥 Download Data (CSV)",
        "err_pass": "Incorrect password!"
    },
    "Deutsch (German)": {
        "sidebar_lang": "🌐 Sprache / Language",
        "title": "🏆 Mitarbeiter-Nominierungsportal",
        "subtitle": "Bitte füllen Sie die Nominierungsdetails für herausragende Einzelpersonen oder Teams basierend auf den folgenden Kriterien aus.",
        "sec1": "1. Allgemeine Informationen",
        "nominee_label": "Name des Nominierten / Teamname *",
        "nominee_placeholder": "Max Mustermann",
        "dept_label": "Abteilung *",
        "dept_placeholder": "Vertrieb / IT",
        "sec2": "2. Kriterienbewertung (Skala 0 - 5)",

        "collab_title": "🤝 1. Zusammenarbeit (Collaboration)",
        "collab_desc": "Beschreibung: Effektive Teamarbeit, Bereitschaft zur Unterstützung von Kollegen und gute abteilungsübergreifende Koordination.",
        "collab_slider": "Zusammenarbeit Bewertung",
        "collab_evidence": "Nachweis / Konkretes Beispiel für Zusammenarbeit *",
        "collab_ph": "Beschreiben Sie das erfolgreiche Kooperationsszenario oder Projekt...",

        "innov_title": "💡 2. Innovation",
        "innov_desc": "Beschreibung: Vorschlagen neuer Ideen, Verbesserung von Arbeitsabläufen zur Steigerung der Produktivität oder Kosteneinsparung.",
        "innov_slider": "Innovation Bewertung",
        "innov_evidence": "Nachweis / Konkretes Beispiel für Innovation *",
        "innov_ph": "Beschreiben Sie die umgesetzte Idee oder Prozessverbesserung...",

        "culture_title": "🌟 3. Kultur & Werte (Culture & Value)",
        "culture_desc": "Beschreibung: Deutliche Demonstration der Unternehmenswerte, Verbreitung positiver Energie und Aufbau eines großartigen Arbeitsumfelds.",
        "culture_slider": "Kultur & Werte Bewertung",
        "culture_evidence": "Nachweis / Konkretes Beispiel für Kultur & Werte *",
        "culture_ph": "Geben Sie Beispiele für Handlungen an, die kulturelle Werte widerspiegeln...",

        "acc_title": "🎯 4. Verantwortlichkeit (Accountability)",
        "acc_desc": "Beschreibung: Übernahme der Verantwortung für die Arbeit, Verpflichtung zur termingerechten Erreichung von Zielen und Verantwortung für Ergebnisse.",
        "acc_slider": "Verantwortlichkeit Bewertung",
        "acc_evidence": "Nachweis / Konkretes Beispiel für Verantwortlichkeit *",
        "acc_ph": "Geben Sie Beispiele für starkes Verantwortungsbewusstsein bei der Arbeit an...",

        "submit_btn": "🚀 Nominierung absenden",
        "err_fields": "⚠️ Bitte füllen Sie den Namen des Nominierten und die Abteilung aus!",
        "err_evidence": "⚠️ Bitte geben Sie für alle 4 Kriterien Nachweise an!",
        "success_msg": "✅ Nominierung erfolgreich eingereicht! Vielen Dank für Ihren Beitrag.",

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

# File path to save data
DATA_FILE = "danh_sach_de_cu.csv"


# Function to initialize the CSV file if it doesn't exist
def init_data_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "Thời Gian",
            "Tên Người Được Đề Cử",
            "Phòng Ban",
            "Điểm Hợp Tác", "Minh Chứng Hợp Tác",
            "Điểm Đổi Mới", "Minh Chứng Đổi Mới",
            "Điểm Văn Hóa & Giá Trị", "Minh Chứng Văn Hóa & Giá Trị",
            "Điểm Trách Nhiệm", "Minh Chứng Trách Nhiệm"
        ])
        df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')


init_data_file()

# Header Section
st.title(t["title"])
st.markdown(t["subtitle"])
st.divider()

# Form Definition
with st.form(key="nomination_form", clear_on_submit=True):
    st.subheader(t["sec1"])

    col1, col2 = st.columns(2)

    with col1:
        nominee_name = st.text_input(t["nominee_label"], placeholder=t["nominee_placeholder"])

    with col2:
        department = st.text_input(t["dept_label"], placeholder=t["dept_placeholder"])

    st.divider()
    st.subheader(t["sec2"])

    # 1. Collaboration (Hợp tác)
    st.image(IMG_COLLAB, use_container_width=True)
    st.markdown(f"### {t['collab_title']}")
    st.caption(t["collab_desc"])
    score_collab = st.slider(t["collab_slider"], min_value=0, max_value=5, value=5, key="collab_score")
    evidence_collab = st.text_area(t["collab_evidence"], placeholder=t["collab_ph"])

    st.markdown("---")

    # 2. Innovation (Đổi mới sáng tạo)
    st.image(IMG_INNOV, use_container_width=True)
    st.markdown(f"### {t['innov_title']}")
    st.caption(t["innov_desc"])
    score_innov = st.slider(t["innov_slider"], min_value=0, max_value=5, value=5, key="innov_score")
    evidence_innov = st.text_area(t["innov_evidence"], placeholder=t["innov_ph"])

    st.markdown("---")

    # 3. Culture & Value (Văn hóa & Giá trị)
    st.image(IMG_CULTURE, use_container_width=True)
    st.markdown(f"### {t['culture_title']}")
    st.caption(t["culture_desc"])
    score_culture = st.slider(t["culture_slider"], min_value=0, max_value=5, value=5, key="culture_score")
    evidence_culture = st.text_area(t["culture_evidence"], placeholder=t["culture_ph"])

    st.markdown("---")

    # 4. Accountability (Trách nhiệm)
    st.image(IMG_ACC, use_container_width=True)
    st.markdown(f"### {t['acc_title']}")
    st.caption(t["acc_desc"])
    score_acc = st.slider(t["acc_slider"], min_value=0, max_value=5, value=5, key="acc_score")
    evidence_acc = st.text_area(t["acc_evidence"], placeholder=t["acc_ph"])

    st.markdown("---")

    # Form Submit Button
    submit_button = st.form_submit_button(label=t["submit_btn"])

# Form handling logic
if submit_button:
    # Validation
    if not nominee_name.strip() or not department.strip():
        st.error(t["err_fields"])
    elif not evidence_collab.strip() or not evidence_innov.strip() or not evidence_culture.strip() or not evidence_acc.strip():
        st.error(t["err_evidence"])
    else:
        # Prepare new data record
        new_entry = {
            "Thời Gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Tên Người Được Đề Cử": nominee_name,
            "Phòng Ban": department,
            "Điểm Hợp Tác": score_collab,
            "Minh Chứng Hợp Tác": evidence_collab,
            "Điểm Đổi Mới": score_innov,
            "Minh Chứng Đổi Mới": evidence_innov,
            "Điểm Văn Hóa & Giá Trị": score_culture,
            "Minh Chứng Văn Hóa & Giá Trị": evidence_culture,
            "Điểm Trách Nhiệm": score_acc,
            "Minh Chứng Trách Nhiệm": evidence_acc
        }

        # Append to CSV file
        df_new = pd.DataFrame([new_entry])
        df_new.to_csv(DATA_FILE, mode='a', header=False, index=False, encoding='utf-8-sig')

        st.success(t["success_msg"])

# Admin Section for Viewing and Exporting Data
st.divider()
with st.expander(t["admin_sec"]):
    admin_password = st.text_input(t["admin_pass_label"], type="password")

    if admin_password == "MO-LQN":
        st.success(t["admin_success"])
        if os.path.exists(DATA_FILE):
            df_data = pd.read_csv(DATA_FILE)
            st.write(f"**{t['total_nominations']}** {len(df_data)}")
            st.dataframe(df_data)

            # Export CSV Button
            csv_data = df_data.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label=t["download_btn"],
                data=csv_data,
                file_name=f"danh_sach_de_cu_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    elif admin_password != "":
        st.error(t["err_pass"])