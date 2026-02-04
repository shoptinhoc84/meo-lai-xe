import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX - Full Tính Năng",
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

# --- 3. CSS GIAO DIỆN (FIX LỆCH HÀNG & GIAO DIỆN CHUẨN) ---
st.markdown("""
<style>
    .tip-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .question-box {
        background-color: #f8f9fa; border-radius: 10px; padding: 20px;
        border-left: 5px solid #007bff; margin-bottom: 20px;
    }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    
    /* Fix đáp án Radio bị lệch hàng */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] div[role="radiogroup"] { gap: 8px; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 12px 15px;
        border-radius: 8px;
        width: 100%;
        display: flex;
        align-items: center;
        margin: 0;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #007bff;
        background-color: #f1f8ff;
    }
    
    /* Căn giữa ảnh */
    div[data-testid="stImage"] { display: flex; justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU & ẢNH ---

@st.cache_data
def load_tips_data(license_type):
    try:
        file_path = 'data.json' if "Ô tô" in license_type else 'tips_a1.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return []

@st.cache_data
def load_600_questions():
    try:
        with open('dulieu_600_cau.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

def load_image_strict(image_name, is_oto):
    """Tìm ảnh đúng thư mục để không bị dính ảnh lẫn nhau"""
    if not image_name: return None
    # Xác định thư mục ưu tiên dựa trên hạng bằng
    primary_folder = "images" if is_oto else "images_a1"
    path = os.path.join(primary_folder, image_name)
    
    if os.path.exists(path):
        try:
            return ImageOps.exif_transpose(Image.open(path))
        except: return None
    return None

# --- 5. GIAO DIỆN: HỌC MẸO (ĐÃ KHÔI PHỤC) ---
def render_tips_page(data, is_oto):
    st.header(f"📖 Mẹo Thi Lý Thuyết {'Ô Tô' if is_oto else 'Xe Máy'}")
    
    if not data:
        st.warning("Chưa có dữ liệu mẹo. Vui lòng kiểm tra file .json")
        return

    categories = list(set([item.get('category', 'Khác') for item in data]))
    selected_cat = st.selectbox("Chọn danh mục:", ["Tất cả"] + categories)
    filtered_data = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    for tip in filtered_data:
        st.markdown(f"""<div class="tip-card"><h3>{tip.get('title', 'Mẹo')}</h3>""", unsafe_allow_html=True)
        cols = st.columns([1, 1]) 
        with cols[0]:
            st.write("**Nội dung:**")
            for line in tip.get('content', []):
                if "=>" in line:
                    parts = line.split("=>")
                    line = f"{parts[0]} => <span class='highlight'>{parts[1]}</span>"
                st.markdown(f"• {line}", unsafe_allow_html=True)
        with cols[1]:
            if tip.get('image'):
                img_obj = load_image_strict(tip['image'], is_oto)
                if img_obj: st.image(img_obj, use_container_width=True)
                else: st.caption(f"(Thiếu ảnh: {tip['image']})")
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. GIAO DIỆN: LUYỆN THI (ĐÃ FIX LỆCH HÀNG) ---
def render_exam_page(is_oto):
    st.header(f"📝 Luyện Tập 600 Câu - {'Hạng Ô Tô' if is_oto else 'Hạng Xe Máy'}")
    questions = load_600_questions()
    if not questions:
        st.error("Lỗi: Không tìm thấy file dữ liệu 600 câu.")
        return

    total_q = len(questions)
    
    # Điều hướng
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Trước"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.session_state.show_answer = False
            st.rerun()
    with c3:
        if st.button("Sau ➡️"):
            st.session_state.current_q_index = min(total_q - 1, st.session_state.current_q_index + 1)
            st.session_state.show_answer = False
            st.rerun()
    with c2:
        new_idx = st.number_input("Câu số:", 1, total_q, st.session_state.current_q_index + 1)
        if new_idx - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_idx - 1
            st.session_state.show_answer = False
            st.rerun()

    q = questions[st.session_state.current_q_index]
    st.markdown(f"""<div class="question-box"><h4>Câu {q['id']}: {q['question']}</h4></div>""", unsafe_allow_html=True)

    if q.get('image'):
        img_obj = load_image_strict(q['image'], is_oto)
        if img_obj: st.image(img_obj, width=500)

    user_choice = st.radio("Answers", q['options'], index=None, key=f"q_{st.session_state.current_q_index}")

    if st.button("Kiểm tra kết quả", type="primary"):
        st.session_state.show_answer = True

    if st.session_state.show_answer:
        st.divider()
        correct = q['correct_answer'].strip()
        if user_choice and user_choice.strip() == correct:
            st.success(f"✅ Chính xác! Đáp án: {correct}")
        else:
            st.error(f"❌ Sai rồi! Đáp án đúng là: {correct}")

# --- 7. MAIN APP ---
def main():
    with st.sidebar:
        st.title("🗂️ ÔN THI GPLX")
        license_choice = st.selectbox("Chọn hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license_choice != st.session_state.license_type:
            st.session_state.license_type = license_choice
            st.session_state.current_q_index = 0
            st.rerun()

        mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        st.caption("Phiên bản 8.0 - Full & Fix")

    is_oto = "Ô tô" in st.session_state.license_type
    if mode == "📖 Học Mẹo":
        data = load_tips_data(st.session_state.license_type)
        render_tips_page(data, is_oto)
    else:
        render_exam_page(is_oto)

if __name__ == "__main__":
    main()
