import streamlit as st
import json
import os
import random
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi 600 Câu PRO",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. KHỞI TẠO STATE ---
# Lưu trữ bookmark
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = set()
# Lưu trữ ảnh đang phóng to (Để sửa lỗi Chrome)
if 'zoomed_image_data' not in st.session_state:
    st.session_state.zoomed_image_data = None

# --- 3. CSS CAO CẤP ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    
    /* Giao diện thẻ bài */
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    
    /* Tiêu đề */
    .tip-header {
        color: #b71c1c;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 10px;
    }

    /* Nhãn category */
    .badge {
        font-size: 0.8rem; padding: 4px 8px; border-radius: 12px;
        color: white; font-weight: 600; text-transform: uppercase;
        margin-bottom: 8px; display: inline-block;
    }
    
    /* Đáp án nổi bật */
    .highlight {
        background-color: #ffebee; color: #c62828; font-weight: bold;
        padding: 2px 6px; border-radius: 4px; border: 1px solid #ffcdd2;
    }
    
    /* Nút che đáp án */
    .hidden-answer {
        color: #999; font-style: italic; border: 1px dashed #ccc;
        padding: 0 8px; border-radius: 4px;
    }

    /* Nút Zoom to hơn, nổi bật hơn */
    .zoom-btn { width: 100%; border-radius: 8px; }

    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. CÁC HÀM HỖ TRỢ ---
def get_category_color(category):
    colors = {
        "Biển báo": "#1976D2", "Sa hình": "#F57C00", "Khái niệm": "#388E3C",
        "Quy tắc": "#00796B", "Văn hóa": "#7B1FA2", "Kỹ thuật": "#455A64", "Tốc độ": "#D32F2F"
    }
    for key, color in colors.items():
        if key in category: return color
    return "#616161"

@st.cache_data
def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'category' not in item: item['category'] = "Chung"
            return data
    except FileNotFoundError:
        return []

# Hàm xử lý xoay ảnh chuẩn (Logic của bạn)
def process_image(image_filename, tip_id):
    image_path = os.path.join("images", image_filename)
    if os.path.exists(image_path):
        img = Image.open(image_path)
        # Logic xoay: 1-36 xoay 270, 37-51 xoay 90
        if 1 <= tip_id <= 36:
            img = img.rotate(-270, expand=True)
        elif 37 <= tip_id <= 51:
            img = img.rotate(-90, expand=True)
        return img
    return None

# --- 5. HÀM HIỂN THỊ THẺ (CARD) ---
def render_tip_card(tip, show_answer):
    cat_color = get_category_color(tip['category'])
    is_bookmarked = tip['id'] in st.session_state.bookmarks
    
    # HTML Card
    st.markdown(f"""
    <div class="tip-card">
        <span class="badge" style="background-color: {cat_color}">{tip['category']}</span>
        <div class="tip-header"><span>{tip['title']}</span></div>
        <div class="tip-content">
    """, unsafe_allow_html=True)
    
    # Nội dung Text
    for line in tip['content']:
        if "=>" in line:
            parts = line.split("=>")
            q_text, a_text = parts[0], parts[1]
            if show_answer:
                display_line = f"{q_text} <span class='highlight'>👉 {a_text}</span>"
            else:
                display_line = f"{q_text} <span class='hidden-answer'>???</span>"
        else:
            display_line = line
        st.markdown(f"• {display_line}", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # --- XỬ LÝ ẢNH & NÚT ZOOM (SỬA LỖI CHROME) ---
    if tip.get('image'):
        # Xử lý ảnh nhỏ để hiển thị trước
        img_obj = process_image(tip['image'], tip.get('id', 0))
        
        if img_obj:
            st.image(img_obj, use_container_width=True)
            
            # Nút bấm Zoom: Thay vì mở Dialog, ta lưu vào Session State để mở trang riêng
            if st.button("🔍 Phóng to ảnh", key=f"zoom_{tip['id']}", use_container_width=True):
                st.session_state.zoomed_image_data = {
                    "image": img_obj,
                    "title": tip['title']
                }
                st.rerun() # Tải lại trang để vào chế độ xem ảnh
    
    # --- CHECKBOX LƯU ---
    col1, col2 = st.columns([0.75, 0.25])
    with col2:
        if st.checkbox("Lưu", value=is_bookmarked, key=f"bk_{tip['id']}"):
            st.session_state.bookmarks.add(tip['id'])
        else:
            st.session_state.bookmarks.discard(tip['id'])
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. CHƯƠNG TRÌNH CHÍNH ---
def main():
    # === CHẾ ĐỘ XEM ẢNH PHÓNG TO (FULLSCREEN) ===
    # Nếu đang có ảnh cần phóng to, chỉ hiện ảnh đó thôi
    if st.session_state.zoomed_image_data:
        st.button("🔙 QUAY LẠI DANH SÁCH", on_click=lambda: st.session_state.update(zoomed_image_data=None), type="primary", use_container_width=True)
        st.header(st.session_state.zoomed_image_data["title"])
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        st.caption("Mẹo: Xoay ngang điện thoại để xem rõ nhất.")
        return # Dừng không chạy phần bên dưới nữa
    # ============================================

    data = load_data()
    if not data:
        st.error("⚠️ Lỗi: Không tìm thấy file data.json")
        return

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("⚙️ Bộ Lọc & Công Cụ")
        study_mode = st.radio("Chế độ hiển thị:", ["📖 Xem đáp án", "🫣 Học thuộc (Che đi)"])
        show_result = (study_mode == "📖 Xem đáp án")
        st.divider()
        st.subheader("🎯 Lọc theo")
        filter_bookmark = st.checkbox("❤️ Chỉ hiện mẹo đã Lưu")
        st.divider()
        st.subheader("🎲 Thử thách")
        if st.button("Bốc thăm 1 câu ngẫu nhiên"):
            st.session_state['random_tip'] = random.choice(data)
        if st.button("Xóa bốc thăm"):
            if 'random_tip' in st.session_state: del st.session_state['random_tip']

    # --- MAIN CONTENT ---
    if 'random_tip' in st.session_state:
        st.info("🎲 **Mẹo ngẫu nhiên dành cho bạn:**")
        render_tip_card(st.session_state['random_tip'], show_result)
        st.divider()

    st.title("🚗 ÔN THI LÝ THUYẾT 600 CÂU")
    search = st.text_input("", placeholder="🔍 Nhập từ khóa để tìm (vd: độ tuổi, 18 tuổi, cấm dừng...)...")

    filtered_data = data
    if search:
        filtered_data = [t for t in filtered_data if search.lower() in t['title'].lower() or any(search.lower() in x.lower() for x in t['content'])]
    if filter_bookmark:
        filtered_data = [t for t in filtered_data if t['id'] in st.session_state.bookmarks]

    if not filtered_data:
        st.warning("Không tìm thấy mẹo nào phù hợp!")
    else:
        if search or filter_bookmark:
            st.caption(f"Tìm thấy {len(filtered_data)} mẹo:")
            for tip in filtered_data:
                render_tip_card(tip, show_result)
        else:
            categories = ["Tất cả"] + sorted(list(set([t['category'] for t in data])))
            tabs = st.tabs(categories)
            for i, category in enumerate(categories):
                with tabs[i]:
                    current_tips = data if category == "Tất cả" else [t for t in data if t['category'] == category]
                    for tip in current_tips:
                        render_tip_card(tip, show_result)

if __name__ == "__main__":
    main()
