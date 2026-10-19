import os
import pandas as pd
import streamlit as st
from datetime import datetime

# Configure page settings
st.set_page_config(
    page_title="Hệ Thống Đề Cử Khen Thưởng",
    page_icon="🏆",
    layout="centered"
)

# File path to save data
DATA_FILE = "danh_sach_de_cu.csv"


# Function to initialize the CSV file if it doesn't exist
def init_data_file():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "Thời Gian",
            "Tên Người Được Đề Cử",
            "Mã Số Nhân Viên",
            "Phòng Ban",
            "Điểm Hợp Tác", "Minh Chứng Hợp Tác",
            "Điểm Đổi Mới", "Minh Chứng Đổi Mới",
            "Điểm Văn Hóa & Giá Trị", "Minh Chứng Văn Hóa & Giá Trị",
            "Điểm Trách Nhiệm", "Minh Chứng Trách Nhiệm"
        ])
        df.to_csv(DATA_FILE, index=False, encoding='utf-8-sig')


init_data_file()

# Header Section
st.title("🏆 Cổng Đề Cử Khen Thưởng")
st.markdown("Vui lòng điền đầy đủ thông tin đề cử cá nhân/tập thể xuất sắc theo các tiêu chí bên dưới.")
st.divider()

# Form Definition
with st.form(key="nomination_form", clear_on_submit=True):
    st.subheader("1. Thông tin chung")

    col1, col2, col3 = st.columns([2, 1, 2])

    with col1:
        nominee_name = st.text_input("Tên người/tập thể được đề cử *", placeholder="Nguyễn Văn A")

    with col2:
        employee_id = st.text_input("Mã số NV *", placeholder="NV12345")

    with col3:
        department = st.text_input("Phòng ban / Bộ phận *", placeholder="Kinh doanh / CNTT")

    st.divider()
    st.subheader("2. Đánh giá theo tiêu chí (Thang điểm 0 - 10)")

    # 1. Collaboration (Hợp tác)
    st.markdown("### 🤝 1. Hợp Tác (Collaboration)")
    st.caption("Mô tả: Làm việc nhóm hiệu quả, sẵn sàng hỗ trợ đồng nghiệp và phối hợp tốt giữa các phòng ban.")
    score_collab = st.slider("Điểm Hợp Tác", min_value=0, max_value=5, value=5, key="collab_score")
    evidence_collab = st.text_area("Minh chứng / Ví dụ cụ thể cho tiêu chí Hợp Tác *",
                                   placeholder="Nêu rõ tình huống hoặc dự án phối hợp thành công...")

    st.markdown("---")

    # 2. Innovation (Đổi mới sáng tạo)
    st.markdown("### 💡 2. Đổi Mới Sáng Tạo (Innovation)")
    st.caption("Mô tả: Đưa ra ý tưởng mới, cải tiến quy trình làm việc giúp nâng cao năng suất hoặc tiết kiệm chi phí.")
    score_innov = st.slider("Điểm Đổi Mới", min_value=0, max_value=5, value=5, key="innov_score")
    evidence_innov = st.text_area("Minh chứng / Ví dụ cụ thể cho tiêu chí Đổi Mới *",
                                  placeholder="Mô tả ý tưởng hoặc cải tiến đã được áp dụng...")

    st.markdown("---")

    # 3. Culture & Value (Văn hóa & Giá trị)
    st.markdown("### 🌟 3. Văn Hóa & Giá Trị (Culture & Value)")
    st.caption(
        "Mô tả: Thể hiện rõ các giá trị cốt lõi của công ty, lan tỏa năng lượng tích cực và xây dựng môi trường làm việc tốt.")
    score_culture = st.slider("Điểm Văn Hóa & Giá Trị", min_value=0, max_value=5, value=5, key="culture_score")
    evidence_culture = st.text_area("Minh chứng / Ví dụ cụ thể cho tiêu chí Văn Hóa & Giá Trị *",
                                    placeholder="Nêu ví dụ về hành động thể hiện giá trị văn hóa...")

    st.markdown("---")

    # 4. Accountability (Trách nhiệm)
    st.markdown("### 🎯 4. Trách Nhiệm (Accountability)")
    st.caption("Mô tả: Làm chủ công việc, cam kết hoàn thành mục tiêu đúng hạn và chịu trách nhiệm về kết quả.")
    score_acc = st.slider("Điểm Trách Nhiệm", min_value=0, max_value=5, value=5, key="acc_score")
    evidence_acc = st.text_area("Minh chứng / Ví dụ cụ thể cho tiêu chí Trách Nhiệm *",
                                placeholder="Nêu ví dụ về tinh thần trách nhiệm trong công việc...")

    st.markdown("---")

    # Form Submit Button
    submit_button = st.form_submit_button(label="🚀 Gửi Đề Cử")

# Form handling logic
if submit_button:
    # Validation
    if not nominee_name.strip() or not employee_id.strip() or not department.strip():
        st.error("⚠️ Vui lòng điền đầy đủ Tên người được đề cử, Mã số NV và Phòng ban!")
    elif not evidence_collab.strip() or not evidence_innov.strip() or not evidence_culture.strip() or not evidence_acc.strip():
        st.error("⚠️ Vui lòng điền minh chứng cho tất cả 4 tiêu chí đánh giá!")
    else:
        # Prepare new data record
        new_entry = {
            "Thời Gian": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "Tên Người Được Đề Cử": nominee_name,
            "Mã Số Nhân Viên": employee_id,
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

        st.success("✅ Gửi đề cử thành công! Cảm ơn bạn đã đóng góp.")

# Admin Section for Viewing and Exporting Data
st.divider()
with st.expander("🔒 Quản Trị Viên (Xem & Tải Dữ Liệu)"):
    admin_password = st.text_input("Nhập mật khẩu quản trị", type="password")

    # Simple security check (replace 'admin123' with your preferred password)
    if admin_password == "MO-LQN":
        st.success("Xác thực thành công!")
        if os.path.exists(DATA_FILE):
            df_data = pd.read_csv(DATA_FILE)
            st.write(f"**Tổng số lượt đề cử:** {len(df_data)}")
            st.dataframe(df_data)

            # Export CSV Button
            csv_data = df_data.to_csv(index=False, encoding='utf-8-sig').encode('utf-8-sig')
            st.download_button(
                label="📥 Tải Bảng Dữ Liệu (CSV)",
                data=csv_data,
                file_name=f"danh_sach_de_cu_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
    elif admin_password != "":
        st.error("Mật khẩu không chính xác!")