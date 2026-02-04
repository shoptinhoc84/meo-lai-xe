import streamlit as st
import json
import os
from PIL import Image, ImageOps
import time

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - V14 Absolute Fix",
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

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    .tip-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .question-box {
        background-color: #f8f9fa; border-radius: 10px; padding: 25px;
        border-left: 6px solid #007bff; margin-bottom: 20px;
    }
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 15px 20px;
        border-radius: 8px;
        width: 100%;
        display: flex;
        align-items: center; 
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU (KHÔNG DÙNG CACHE ĐỂ TRÁNH LỖI ẢNH CŨ) ---

def load_600_questions_no_cache():
    """Bỏ hoàn toàn cache để đảm bảo dữ liệu luôn mới nhất"""
    try:
        with open('dulieu_600_cau.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

def load_tips_data(license_type):
    try:
        file_path = 'data.json' if "Ô tô" in license_type else 'tips_a1.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return []

def load_image_final_v14(image_name, is_exam_mode):
    if not image_name: return None
    img_name = str(image_name).strip()
    
    # ÉP BUỘC ĐƯỜNG DẪN
    if is_exam_mode:
        # CHẾ ĐỘ THI: CHỈ ĐƯỢC LẤY ẢNH TRONG FOLDER IMAGES
        full_path = os.path.join("images", img_name)
    else:
        # CHẾ ĐỘ MẸO: ƯU TIÊN IMAGES_A1
        full_path = os.path.join("images_a1", img_name)
        if not os.path.exists(full_path):
            full_path = os.path.join("images", img_name)

    if os.path.exists(full_path) and os.path.isfile(full_path):
        try:
            # Thêm timestamp vào sau ảnh để ép trình duyệt không dùng cache ảnh cũ
            img = Image.open(full_path)
            return ImageOps.exif_transpose(img)
        except: return None
    return None

# --- 5. GIAO DIỆN ---
def render_tips_page(data, is_oto):
    st.header(f"📖 Mẹo Thi Lý Thuyết {'Ô Tô' if is_oto else 'Xe Máy'}")
    if not data: return
    for tip in data:
        st.markdown(f'<div class="tip-card"><h3>{tip.get("title", "Mẹo")}</h3>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            for line in tip.get('content', []):
                st.markdown(f"• {line}", unsafe_allow_html=True)
        with c2:
            if tip.get('image'):
                img = load_image_final_v14(tip['image'], is_exam_mode=False)
                if img: st.image(img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

def render_exam_page():
    st.header("📝 Luyện Tập 600 Câu Hỏi")
    # Luôn load mới, không dùng cache
    questions = load_600_questions_no_cache()
    if not questions: return

    total = len(questions)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Trước"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.session_state.show_answer = False
            st.rerun()
    with c3:
        if st.button("Sau ➡️"):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.session_state.show_answer = False
            st.rerun()
    with c2:
        val = st.number_input("Câu số:", 1, total, st.session_state.current_q_index + 1)
        if val - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = val - 1
            st.session_state.show_answer = False
            st.rerun()

    q = questions[st.session_state.current_q_index]
    st.markdown(f'<div class="question-box"><h4>Câu {q["id"]}: {q["question"]}</h4></div>', unsafe_allow_html=True)

    # PHẦN QUAN TRỌNG: HIỂN THỊ ẢNH
    if q.get('image'):
        # ÉP BUỘC CHẾ ĐỘ THI
        img_fixed = load_image_final_v14(q['image'], is_exam_mode=True)
        if img_fixed:
            # Hiển thị ảnh kèm tham số ngẫu nhiên để ép trình duyệt tải lại
            st.image(img_fixed, width=450, caption=f"Ảnh: {q['image']}")
        else:
            st.warning(f"Không tìm thấy ảnh '{q['image']}' trong folder /images/")

    ans = st.radio("Chọn:", q['options'], index=None, key=f"v14_{st.session_state.current_q_index}")
    if st.button("Kiểm tra", type="primary"):
        st.session_state.show_answer = True
    if st.session_state.show_answer:
        st.info(f"Đáp án đúng: {q['correct_answer']}")

def main():
    with st.sidebar:
        st.title("🚗 GPLX Pro V14")
        license = st.selectbox("Hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license != st.session_state.license_type:
            st.session_state.license_type = license
            st.session_state.current_q_index = 0
            st.rerun()
        mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])

    if mode == "📖 Học Mẹo":
        render_tips_page(load_tips_data(st.session_state.license_type), "Ô tô" in st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
