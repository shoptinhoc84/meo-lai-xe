import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX",
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
        background-color: #f8f9fa; border-radius: 10px; padding: 20px;
        border-left: 5px solid #007bff; margin-bottom: 20px;
    }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    .stButton button { width: 100%; font-weight: 500; }
    /* Căn giữa ảnh và caption */
    div[data-testid="stImage"] {
        display: block;
        margin-left: auto;
        margin-right: auto;
    }
    div[data-testid="stImage"] > img {
        width: auto;
        max-width: 100%; 
        max-height: 500px;
        object-fit: contain;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU & ẢNH ---

@st.cache_data
def load_tips_data(license_type):
    try:
        file_path = 'data.json' if "Ô tô" in license_type else 'tips_a1.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return []

@st.cache_data
def load_600_questions():
    try:
        with open('dulieu_600_cau.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_image_smart(image_name, folder_priority=[]):
    """
    Hàm load ảnh thông minh:
    1. Tìm trong danh sách folder ưu tiên (images_a1, images...)
    2. Tự động xoay ảnh nếu bị ngược (ImageOps.exif_transpose)
    """
    if not image_name: return None
    
    # Duyệt qua các folder để tìm ảnh
    found_path = None
    for folder in folder_priority:
        path = os.path.join(folder, image_name)
        if os.path.exists(path):
            found_path = path
            break
            
    if found_path:
        try:
            image = Image.open(found_path)
            # Xoay ảnh đúng chiều
            image = ImageOps.exif_transpose(image)
            return image
        except:
            return None
    return None

# --- 5. GIAO DIỆN: HỌC MẸO ---
def render_tips_page(data, is_oto):
    st.header(f"📖 Mẹo Thi Lý Thuyết {'Ô Tô' if is_oto else 'Xe Máy'}")
    
    if not data:
        st.warning("Chưa có dữ liệu mẹo. Vui lòng kiểm tra file data.json hoặc tips_a1.json")
        return

    categories = list(set([item.get('category', 'Khác') for item in data]))
    if categories:
        selected_cat = st.selectbox("Chọn danh mục:", ["Tất cả"] + categories)
        filtered_data = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    else:
        filtered_data = data

    for tip in filtered_data:
        st.markdown(f"""<div class="tip-card"><h3>{tip.get('title', 'Mẹo')}</h3>""", unsafe_allow_html=True)
        
        # --- THAY ĐỔI BỐ CỤC ---
        # Thay vì chia cột 2:1 (bị dồn ảnh), ta chia 1:1 hoặc để ảnh phía dưới nếu màn hình nhỏ
        cols = st.columns([1, 1]) # Chia đều 50-50 để ảnh to hơn
        
        with cols[0]:
            st.write("**Nội dung:**")
            for line in tip.get('content', []):
                parts = line.split("=>")
                if len(parts) > 1:
                    line = f"{parts[0]} => <span class='highlight'>{parts[1]}</span>"
                st.markdown(f"• {line}", unsafe_allow_html=True)

        with cols[1]:
            if tip.get('image'):
                # Logic tìm ảnh: Nếu là xe máy, ưu tiên tìm trong 'images_a1', nếu không thấy thì tìm 'images'
                # Nếu là ô tô, ưu tiên 'images'
                folders = ["images", "images_a1"] if is_oto else ["images_a1", "images"]
                
                img_obj = load_image_smart(tip['image'], folder_priority=folders)
                if img_obj:
                    # use_container_width=True giúp ảnh tự giãn đầy cột (không bị bé tí)
                    st.image(img_obj, use_container_width=True)
                else:
                    # Ẩn cảnh báo nếu không thấy ảnh để giao diện đỡ rối, hoặc hiện mờ
                    st.caption(f"(Thiếu ảnh: {tip['image']})")
        
        st.markdown("</div>", unsafe_allow_html=True)


# --- 6. GIAO DIỆN: LUYỆN THI 600 CÂU ---
def render_exam_page():
    st.header("📝 Luyện Tập 600 Câu Hỏi")
    questions = load_600_questions()
    
    if not questions:
        st.error("⚠️ LỖI: Chưa tìm thấy file `dulieu_600_cau.json`.")
        return

    total_q = len(questions)
    
    # Điều hướng
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Trước"):
            if st.session_state.current_q_index > 0:
                st.session_state.current_q_index -= 1
                st.session_state.show_answer = False
                st.rerun()
    with c3:
        if st.button("Sau ➡️"):
            if st.session_state.current_q_index < total_q - 1:
                st.session_state.current_q_index += 1
                st.session_state.show_answer = False
                st.rerun()
    with c2:
        new_idx = st.number_input("Câu số:", 1, total_q, st.session_state.current_q_index + 1)
        if new_idx - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_idx - 1
            st.session_state.show_answer = False
            st.rerun()

    # Hiển thị câu hỏi
    q = questions[st.session_state.current_q_index]
    st.markdown(f"""
    <div class="question-box">
        <h4>Câu {q['id']}: {q['question']}</h4>
        <span style='color: #666; font-size: 0.9em;'>Phân loại: {q.get('category', 'Chung')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị ảnh (Căn giữa, không set cứng width=500 nữa)
    if q.get('image'):
        # Luôn tìm trong folder images cho phần 600 câu
        img_obj = load_image_smart(q['image'], folder_priority=["images"])
        if img_obj:
            # Không set width cố định, cho ảnh tự nhiên nhưng giới hạn bởi CSS max-height
            st.image(img_obj)
        elif "Sa hình" in q.get('category', '') or "Biển báo" in q.get('category', ''):
            st.warning(f"Chưa có ảnh: {q['image']}")

    # Chọn đáp án
    st.write("**Chọn đáp án:**")
    # CSS tùy chỉnh cho Radio button to hơn một chút
    st.markdown("""
    <style>
    div[role="radiogroup"] > label > div:first-child {
        background-color: #f0f2f6;
        border: 1px solid #d1d5db;
        padding: 10px;
        border-radius: 8px;
        width: 100%;
        margin-bottom: 5px;
    }
    div[role="radiogroup"] > label > div:first-child:hover {
        background-color: #e2e8f0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    user_choice = st.radio("Answers", q['options'], index=None, key=f"q_{q['id']}", label_visibility="collapsed")

    if st.button("Kiểm tra kết quả", type="primary"):
        st.session_state.show_answer = True

    if st.session_state.show_answer:
        st.divider()
        if user_choice:
            if user_choice.strip() == q['correct_answer'].strip():
                st.success("🎉 Chính xác!")
            else:
                st.error("Sai rồi!")
                st.info(f"👉 Đáp án đúng: **{q['correct_answer']}**")
        else:
            st.warning("Vui lòng chọn đáp án.")
            st.info(f"👉 Đáp án đúng: **{q['correct_answer']}**")

# --- 7. MAIN APP ---
def main():
    with st.sidebar:
        st.title("🗂️ ÔN THI GPLX")
        st.write("---")
        
        old_license = st.session_state.license_type
        current_license = st.selectbox("Chọn hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        
        if current_license != old_license:
            st.session_state.license_type = current_license
            st.cache_data.clear()
            st.rerun()

        mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        st.write("---")
        st.caption("Ver 5.0 - Giao diện Fix")

    is_oto = "Ô tô" in st.session_state.license_type

    if mode == "📖 Học Mẹo":
        data = load_tips_data(st.session_state.license_type)
        render_tips_page(data, is_oto)
    elif mode == "📝 Luyện Thi (600 câu)":
        render_exam_page()

if __name__ == "__main__":
    main()
