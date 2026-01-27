import streamlit as st
import json
import os
import random
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX Pro",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. KHỞI TẠO STATE ---
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = set()
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
# State để lưu lựa chọn tạm thời khi chuyển câu
if 'user_choice' not in st.session_state:
    st.session_state.user_choice = None

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    
    /* Giao diện thẻ Mẹo */
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .tip-header { color: #b71c1c; font-size: 1.2rem; font-weight: 700; margin-bottom: 10px; }
    
    /* Giao diện Câu hỏi 600 câu */
    .question-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #0d47a1;
        margin-bottom: 20px;
    }
    .question-text {
        font-size: 1.3rem;
        font-weight: 600;
        color: #333;
        margin-bottom: 15px;
    }
    
    /* Button điều hướng */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def load_tips():
    # Giả lập load file data.json nếu không có file thật
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return []

@st.cache_data
def load_questions():
    try:
        with open('dulieu_web_chuan.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Xử lý nếu dữ liệu nằm trong key 'questions' hoặc là list trực tiếp
            if isinstance(data, dict) and 'questions' in data:
                return data['questions']
            return data
    except FileNotFoundError:
        return []

# --- 5. LOGIC GIAO DIỆN MẸO (Tab cũ) ---
def render_tips_page(tips_data):
    st.header("💡 MẸO GIẢI NHANH")
    if not tips_data:
        st.info("Chưa có dữ liệu mẹo.")
        return
        
    for tip in tips_data:
        st.markdown(f"""
        <div class="tip-card">
            <div class="tip-header">{tip.get('title', 'Mẹo')}</div>
            <div>{tip.get('content', '')}</div>
        </div>
        """, unsafe_allow_html=True)

# --- 6. LOGIC GIAO DIỆN 600 CÂU (Tab mới) ---
def render_practice_page(questions):
    st.header("📝 LUYỆN THI 600 CÂU")
    
    if not questions:
        st.error("⚠️ Không tìm thấy dữ liệu câu hỏi! Hãy kiểm tra file 'dulieu_web_chuan.json'.")
        return

    # Lấy chỉ số câu hỏi hiện tại
    q_idx = st.session_state.current_question_index
    total_q = len(questions)
    
    # Đảm bảo index hợp lệ
    if q_idx < 0: q_idx = 0
    if q_idx >= total_q: q_idx = total_q - 1

    question = questions[q_idx]

    # --- Sidebar điều hướng ---
    with st.sidebar:
        st.markdown("---")
        st.subheader("🔢 Điều hướng câu hỏi")
        
        # Nhập số câu để nhảy nhanh
        new_idx = st.number_input("Đến câu số:", min_value=1, max_value=total_q, value=q_idx+1)
        if new_idx - 1 != q_idx:
            st.session_state.current_question_index = new_idx - 1
            st.rerun()
            
        st.progress((q_idx + 1) / total_q)
        st.caption(f"Tiến độ: {q_idx + 1}/{total_q}")

    # --- Hiển thị câu hỏi ---
    st.markdown(f"""
    <div class="question-card">
        <div style="color: #666; margin-bottom: 5px;">Câu {question.get('id', q_idx+1)} ({question.get('category', 'Chung')})</div>
        <div class="question-text">{question['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị ảnh nếu có
    if question.get('image'):
        # Giả sử ảnh nằm trong thư mục images/
        img_path = os.path.join("images", question['image'])
        if os.path.exists(img_path):
            st.image(img_path, caption="Hình ảnh minh họa")
        else:
            # Nếu không tìm thấy file ảnh thực tế, hiện tên ảnh để debug
            st.warning(f"Không tìm thấy ảnh: {question['image']}")

    # --- Hiển thị đáp án ---
    options = question.get('options', [])
    
    # Form chọn đáp án
    with st.form(key=f"form_q_{q_idx}"):
        user_choice = st.radio(
            "Chọn đáp án đúng:", 
            options, 
            index=None
        )
        
        col_check, col_empty = st.columns([1, 4])
        with col_check:
            submitted = st.form_submit_button("✅ Kiểm tra")

        if submitted:
            if not user_choice:
                st.warning("Vui lòng chọn một đáp án!")
            else:
                # Xử lý so sánh đáp án
                # Giả sử correct_answer trong JSON là "1", "2" hoặc nội dung text
                correct_ans = str(question.get('correct_answer', '')).strip()
                
                # Lấy số thứ tự từ lựa chọn của người dùng (VD: "1. Nội dung" -> "1")
                try:
                    user_ans_idx = str(user_choice).split('.')[0].strip()
                except:
                    user_ans_idx = user_choice

                if not correct_ans:
                    st.warning("⚠️ Dữ liệu câu hỏi này chưa có đáp án đúng (correct_answer trống).")
                elif user_ans_idx == correct_ans:
                    st.success(f"🎉 Chính xác! Đáp án là: {user_choice}")
                else:
                    st.error(f"❌ Sai rồi! Đáp án đúng là: {correct_ans}")
                    # Gợi ý đáp án đúng đầy đủ
                    for opt in options:
                        if str(opt).startswith(correct_ans + "."):
                            st.info(f"👉 Đáp án đúng: **{opt}**")

    # --- Nút chuyển câu (Prev / Next) ---
    col1, col2, col3 = st.columns([1, 4, 1])
    with col1:
        if st.button("⬅️ Câu trước", disabled=(q_idx == 0)):
            st.session_state.current_question_index -= 1
            st.rerun()
    with col3:
        if st.button("Câu sau ➡️", disabled=(q_idx == total_q - 1)):
            st.session_state.current_question_index += 1
            st.rerun()

# --- 7. CHẠY ỨNG DỤNG ---
def main():
    # Load dữ liệu
    tips_data = load_tips()
    questions_data = load_questions()

    # Menu Sidebar
    with st.sidebar:
        st.title("🗂️ Menu Chức Năng")
        page = st.radio("Chọn chế độ học:", ["📖 Học Mẹo", "📝 Luyện 600 Câu"], index=1) # Mặc định chọn 600 câu để test
        st.divider()

    # Điều hướng trang
    if page == "📖 Học Mẹo":
        render_tips_page(tips_data)
        
    elif page == "📝 Luyện 600 Câu":
        render_practice_page(questions_data)

if __name__ == "__main__":
    main()
