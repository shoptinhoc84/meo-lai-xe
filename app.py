import streamlit as st
import json
import os
import re
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX SHOPTINHOC",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. KHỞI TẠO STATE ---
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = set()
if 'zoomed_image_data' not in st.session_state:
    st.session_state.zoomed_image_data = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .question-header { color: #0d47a1; font-size: 1.3rem; font-weight: 700; margin-bottom: 15px; }
    .badge {
        font-size: 0.8rem; padding: 4px 8px; border-radius: 12px;
        color: white; font-weight: 600; text-transform: uppercase;
        margin-bottom: 8px; display: inline-block;
    }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    .hidden-answer { color: #999; font-style: italic; border: 1px dashed #ccc; padding: 0 8px; border-radius: 4px; }
    .explanation-box {
        background-color: #e8f5e9; border-left: 5px solid #4caf50;
        padding: 15px; margin-top: 15px; border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

def get_category_color(category):
    colors = {
        "Biển báo": "#1976D2", "Sa hình": "#F57C00", "Khái niệm": "#388E3C",
        "Quy tắc": "#00796B", "Văn hóa": "#7B1FA2", "Kỹ thuật": "#455A64", "Tốc độ": "#D32F2F"
    }
    for key, color in colors.items():
        if key in category: return color
    return "#616161"

# HÀM XỬ LÝ ẢNH (ĐÃ FIX LỖI XOAY ẢNH Ô TÔ)
def process_image(image_filename, tip_id=None, is_oto=True):
    if not image_filename: return None
    image_path = os.path.join("images", image_filename)
    if os.path.exists(image_path):
        img = Image.open(image_path)
        # Chỉ áp dụng xoay ảnh cho phần Mẹo của Ô tô theo logic code gốc của bạn
        if is_oto and tip_id is not None:
            if 1 <= tip_id <= 36: 
                img = img.rotate(-270, expand=True)
            elif 37 <= tip_id <= 51: 
                img = img.rotate(-90, expand=True)
        return img
    return None

@st.cache_data
def load_tips(license_mode):
    filename = 'data.json' if license_mode == "oto" else 'tips_a1.json'
    if not os.path.exists(filename): return []
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data
    except: return []

@st.cache_data
def load_questions_v6(license_mode):
    if license_mode == "oto":
        candidates = ['dulieu_web_chuan.json', 'data_600cau.json']
    else:
        candidates = ['dulieu_a1.json', 'questions_a1.json']
    
    file_path = None
    for f in candidates:
        if os.path.exists(f) and os.path.getsize(f) > 1024:
            file_path = f
            break
            
    if not file_path: return [], f"Chưa có dữ liệu câu hỏi cho {license_mode}", None

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Logic Deep Miner
    try:
        idx = content.find('"questions"')
        if idx != -1:
            array_start = content.find('[', idx)
            obj, _ = json.JSONDecoder().raw_decode(content, idx=array_start)
            return obj, "Đã tải dữ liệu thành công", None
        return json.loads(content), "Mode cơ bản", None
    except: return [], "Lỗi đọc file", None

# --- 5. GIAO DIỆN HỌC MẸO ---
def display_tips_list(tips_list, show_answer, is_oto):
    for tip in tips_list:
        cat_color = get_category_color(tip.get('category', 'Chung'))
        unique_key = f"{tip['id']}_{st.session_state.license_type}"
        
        st.markdown(f"""
        <div class="tip-card">
            <span class="badge" style="background-color: {cat_color}">{tip.get('category', 'Chung')}</span>
            <div class="tip-header"><b>{tip['title']}</b></div>
        """, unsafe_allow_html=True)
        
        for line in tip['content']:
            if "=>" in line:
                parts = line.split("=>")
                display_line = f"{parts[0]} <span class='highlight'>👉 {parts[1]}</span>" if show_answer else f"{parts[0]} <span class='hidden-answer'>???</span>"
            else: display_line = line
            st.markdown(f"• {display_line}", unsafe_allow_html=True)
        
        # Gọi hàm xử lý ảnh với Tip ID để xoay nếu là Ô tô
        if tip.get('image'):
            img_obj = process_image(tip['image'], tip_id=tip['id'], is_oto=is_oto)
            if img_obj:
                st.image(img_obj, use_container_width=True)
                if st.button("🔍 Phóng to", key=f"z_{unique_key}"):
                    st.session_state.zoomed_image_data = {"image": img_obj, "title": tip['title']}
                    st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)

def render_tips_page(tips_data, is_oto):
    st.header(f"💡 MẸO GIẢI NHANH ({st.session_state.license_type})")
    if not tips_data:
        st.info("Đang chờ file tips_a1.json...")
        return

    col1, col2 = st.columns([3, 1])
    with col1: search = st.text_input("", placeholder="🔍 Tìm kiếm mẹo...")
    with col2: study_mode = st.radio("Chế độ:", ["Xem đáp án", "Học thuộc"], horizontal=True, label_visibility="collapsed")
    
    show_answer = (study_mode == "Xem đáp án")
    filtered = [t for t in tips_data if search.lower() in t['title'].lower()] if search else tips_data
    
    display_tips_list(filtered, show_answer, is_oto)

# --- 6. GIAO DIỆN CÂU HỎI ---
def render_questions_page(questions_data, status):
    st.header(f"📝 LUYỆN THI ({st.session_state.license_type})")
    if not questions_data:
        st.warning(status)
        return

    q = questions_data[st.session_state.current_question_index]
    st.markdown(f"""<div class="tip-card">
        <div class="question-header">Câu {st.session_state.current_question_index + 1}</div>
        <div class="question-content">{q.get('question', '')}</div>
    </div>""", unsafe_allow_html=True)

    if q.get('image'):
        img = process_image(q['image'], is_oto=False) # Câu hỏi sa hình thường không cần xoay
        if img: st.image(img, width=500)

    # ... (Giữ nguyên logic Radio Button và Navigation cũ của bạn)

# --- 7. MAIN APP ---
def main():
    if st.session_state.zoomed_image_data:
        st.button("🔙 QUAY LẠI", on_click=lambda: st.session_state.update(zoomed_image_data=None))
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        return

    with st.sidebar:
        st.title("🗂️ Menu")
        app_mode = st.selectbox("Chọn hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if app_mode != st.session_state.license_type:
            st.session_state.license_type = app_mode
            st.rerun()
        page = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi"])

    is_oto = "Ô tô" in st.session_state.license_type
    mode_key = "oto" if is_oto else "xemay"

    if page == "📖 Học Mẹo":
        render_tips_page(load_tips(mode_key), is_oto)
    else:
        q_data, status, _ = load_questions_v6(mode_key)
        render_questions_page(q_data, status)

if __name__ == "__main__":
    main()
