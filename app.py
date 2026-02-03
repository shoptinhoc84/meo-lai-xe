import streamlit as st
import json
import os
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX SHOPTINHOC",
    page_icon="🚗",
    layout="wide"
)

# --- 2. KHỞI TẠO STATE ---
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = set()
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    .tip-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    .hidden-answer { color: #999; font-style: italic; border: 1px dashed #ccc; padding: 0 8px; border-radius: 4px; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

# Xử lý xoay ảnh cho Ô tô và giữ nguyên cho Xe máy
def process_image(image_filename, tip_id, is_oto):
    if not image_filename: return None
    image_path = os.path.join("images", image_filename)
    if os.path.exists(image_path):
        try:
            img = Image.open(image_path)
            # Chỉ xoay ảnh nếu là hạng Ô tô (dựa trên code gốc của bạn)
            if is_oto:
                if 1 <= tip_id <= 36: 
                    img = img.rotate(-270, expand=True)
                elif 37 <= tip_id <= 51: 
                    img = img.rotate(-90, expand=True)
            return img
        except: return None
    return None

@st.cache_data(show_spinner=False)
def load_tips_data(mode):
    # Buộc load đúng file theo mode
    file_path = 'data.json' if mode == "oto" else 'tips_a1.json'
    if not os.path.exists(file_path):
        return []
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

# --- 5. GIAO DIỆN HIỂN THỊ MẸO ---
def render_tips_page(tips_list, is_oto):
    st.header(f"💡 MẸO GIẢI NHANH - HẠNG {st.session_state.license_type.upper()}")
    
    if not tips_list:
        st.warning("Không tìm thấy dữ liệu mẹo. Vui lòng kiểm tra file JSON.")
        return

    col1, col2 = st.columns([3, 1])
    with col1: search = st.text_input("🔍 Tìm kiếm mẹo...", key="search_bar")
    with col2: study_mode = st.radio("Chế độ:", ["Xem đáp án", "Học thuộc"], horizontal=True)

    show_answer = (study_mode == "Xem đáp án")
    
    for tip in tips_list:
        # Nếu có tìm kiếm, bỏ qua các mẹo không khớp
        if search and search.lower() not in tip['title'].lower():
            continue
            
        unique_key = f"tip_{tip['id']}_{'oto' if is_oto else 'a1'}"
        
        st.markdown(f"""
        <div class="tip-card">
            <div style="color:#0d47a1; font-weight:bold; font-size:1.2rem; margin-bottom:10px;">{tip['title']}</div>
        """, unsafe_allow_html=True)
        
        for line in tip['content']:
            if "=>" in line:
                parts = line.split("=>")
                display_line = f"{parts[0]} <span class='highlight'>👉 {parts[1]}</span>" if show_answer else f"{parts[0]} <span class='hidden-answer'>???</span>"
            else:
                display_line = line
            st.markdown(f"• {display_line}", unsafe_allow_html=True)
            
        # Hiển thị ảnh
        if tip.get('image'):
            img_obj = process_image(tip['image'], tip['id'], is_oto)
            if img_obj:
                # Dùng use_container_width để ảnh tự co dãn
                st.image(img_obj, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. MAIN APP ---
def main():
    with st.sidebar:
        st.title("🗂️ HỆ THỐNG ÔN THI")
        
        # Chọn hạng bằng
        old_license = st.session_state.license_type
        current_license = st.selectbox(
            "Chọn hạng bằng:", 
            ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"]
        )
        
        # Nếu đổi hạng bằng, xóa cache để load lại file mới hoàn toàn
        if current_license != old_license:
            st.session_state.license_type = current_license
            st.cache_data.clear() # Xóa toàn bộ cache
            st.rerun()

        page = st.radio("Menu chính:", ["📖 Học Mẹo", "📝 Luyện Thi"])

    is_oto = "Ô tô" in st.session_state.license_type
    mode_key = "oto" if is_oto else "xemay"

    if page == "📖 Học Mẹo":
        tips_data = load_tips_data(mode_key)
        render_tips_page(tips_data, is_oto)
    else:
        st.info("Chức năng Luyện Thi đang được cập nhật dữ liệu...")

if __name__ == "__main__":
    main()
