import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hệ Thống Ôn Thi GPLX",
    page_icon="🚗",
    layout="wide"
)

# --- 2. KHỞI TẠO STATE ---
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# --- 3. CSS GIAO DIỆN (CHỐNG LỆCH HÀNG & XÉO) ---
st.markdown("""
<style>
    .question-box {
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 25px;
        border-left: 8px solid #1a73e8; 
        margin-bottom: 25px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .question-text {
        font-size: 1.25rem;
        font-weight: 600;
        color: #1e293b;
        line-height: 1.6;
    }
    
    /* Fix Radio Button - Đáp án thẳng hàng */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] div[role="radiogroup"] { gap: 10px; }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 15px 20px;
        border-radius: 10px;
        width: 100%;
        display: flex;
        align-items: center; /* Căn giữa nội dung theo chiều dọc */
        transition: all 0.2s;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #1a73e8;
        background-color: #f8fafc;
    }
    
    /* Căn giữa ảnh */
    div[data-testid="stImage"] {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM LOAD DỮ LIỆU ---
@st.cache_data
def load_600_questions():
    try:
        # Load file gốc, không lọc để tránh lỗi "không chạy được"
        with open('dulieu_600_cau.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"⚠️ Không tìm thấy file dulieu_600_cau.json: {e}")
        return []

def load_image_strict(image_name, is_oto):
    if not image_name: return None
    
    # Ép buộc tìm trong folder tương ứng
    folder = "images" if is_oto else "images_a1"
    path = os.path.join(folder, image_name)
    
    if os.path.exists(path):
        try:
            return ImageOps.exif_transpose(Image.open(path))
        except: return None
    return None

# --- 5. GIAO DIỆN LUYỆN THI ---
def render_exam_page(is_oto):
    st.header(f"📝 Luyện Tập: {'Hạng Ô Tô' if is_oto else 'Hạng Xe Máy'}")
    
    questions = load_600_questions()
    if not questions: return

    total_q = len(questions)
    
    # Thanh điều hướng (Navigation)
    col_nav = st.columns([1, 1, 1, 1])
    with col_nav[0]:
        if st.button("⬅️ Câu trước"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.session_state.show_answer = False
            st.rerun()
    with col_nav[1]:
        if st.button("Câu tiếp ➡️"):
            st.session_state.current_q_index = min(total_q - 1, st.session_state.current_q_index + 1)
            st.session_state.show_answer = False
            st.rerun()
    with col_nav[2]:
        val = st.number_input("Tới câu số:", 1, total_q, st.session_state.current_q_index + 1)
        if val - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = val - 1
            st.session_state.show_answer = False
            st.rerun()

    # Lấy câu hỏi hiện tại
    q = questions[st.session_state.current_q_index]
    
    # Hiển thị
    st.markdown(f"""
    <div class="question-box">
        <div style="color:#64748b; font-weight:500;">Câu hỏi {st.session_state.current_q_index + 1} / {total_q}</div>
        <div class="question-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Ảnh (Tìm theo logic strict)
    if q.get('image'):
        img = load_image_strict(q['image'], is_oto)
        if img:
            st.image(img, width=500)
        else:
            st.caption(f"(Không tìm thấy ảnh {q['image']} trong thư mục {'images' if is_oto else 'images_a1'})")

    # Đáp án
    user_choice = st.radio(
        "Label ẩn", 
        q['options'], 
        index=None, 
        key=f"radio_{st.session_state.current_q_index}"
    )

    if st.button("Kiểm tra đáp án", type="primary"):
        st.session_state.show_answer = True

    if st.session_state.show_answer:
        st.divider()
        correct = q['correct_answer'].strip()
        if user_choice:
            if user_choice.strip() == correct:
                st.success(f"🎉 CHÍNH XÁC! Đáp án: {correct}")
            else:
                st.error(f"❌ SAI RỒI! Đáp án đúng là: {correct}")
        else:
            st.warning(f"💡 Đáp án đúng của câu này là: {correct}")

# --- 6. MAIN ---
def main():
    with st.sidebar:
        st.title("🚗 GPLX OFFLINE")
        st.divider()
        
        license = st.selectbox("Chọn loại bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license != st.session_state.license_type:
            st.session_state.license_type = license
            st.session_state.current_q_index = 0
            st.session_state.show_answer = False
            st.rerun()
            
        mode = st.radio("Chế độ:", ["📝 Luyện Thi 600 Câu", "📖 Xem Mẹo Thi"])
        st.divider()
        st.info("Lưu ý: Đảm bảo các file .json và folder images đặt đúng chỗ.")

    is_oto = "Ô tô" in st.session_state.license_type
    
    if mode == "📝 Luyện Thi 600 Câu":
        render_exam_page(is_oto)
    else:
        st.write("Chế độ xem mẹo đang được đồng bộ...")

if __name__ == "__main__":
    main()
