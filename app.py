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

# --- 2. KHỞI TẠO STATE (Lưu trữ trạng thái Đánh dấu) ---
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = set()

# --- 3. CSS CAO CẤP (Giao diện đẹp) ---
st.markdown("""
<style>
    /* Font chữ toàn hệ thống */
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    
    /* Giao diện thẻ bài (Card) */
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
        transition: all 0.2s ease-in-out;
    }
    div.tip-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 16px rgba(0,0,0,0.12);
        border-color: #d32f2f;
    }

    /* Tiêu đề mẹo */
    .tip-header {
        color: #b71c1c;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Nhãn phân loại (Badge) */
    .badge {
        font-size: 0.8rem;
        padding: 4px 8px;
        border-radius: 12px;
        color: white;
        font-weight: 600;
        text-transform: uppercase;
        margin-bottom: 8px;
        display: inline-block;
    }
    
    /* Đáp án/Từ khóa nổi bật */
    .highlight {
        background-color: #ffebee;
        color: #c62828;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid #ffcdd2;
    }
    
    /* Nút che đáp án */
    .hidden-answer {
        color: #999;
        font-style: italic;
        border: 1px dashed #ccc;
        padding: 0 8px;
        border-radius: 4px;
        cursor: help;
    }

    /* Nút Zoom ảnh */
    .stButton button {
        width: 100%;
        border-radius: 8px;
        font-weight: 600;
    }

    /* Ẩn khoảng trắng thừa mobile */
    .block-container { padding-top: 1.5rem !important; padding-bottom: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ MÀU SẮC DANH MỤC ---
def get_category_color(category):
    colors = {
        "Biển báo": "#1976D2",    # Xanh dương
        "Sa hình": "#F57C00",     # Cam
        "Khái niệm": "#388E3C",   # Xanh lá
        "Quy tắc": "#00796B",     # Xanh ngọc
        "Văn hóa": "#7B1FA2",     # Tím
        "Kỹ thuật": "#455A64",    # Xám xanh
        "Tốc độ": "#D32F2F",      # Đỏ
    }
    for key, color in colors.items():
        if key in category: return color
    return "#616161"

# --- 5. TẢI DỮ LIỆU ---
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

# --- 6. HÀM POPUP ZOOM ẢNH (New Feature) ---
@st.dialog("🔍 HÌNH MINH HỌA CHI TIẾT")
def show_large_image(image_obj, title):
    st.subheader(title)
    st.image(image_obj, use_container_width=True)
    st.caption("Mẹo: Bạn có thể xoay ngang điện thoại để xem rõ hơn.")

# --- 7. HÀM HIỂN THỊ THẺ (CARD) ---
def render_tip_card(tip, show_answer):
    cat_color = get_category_color(tip['category'])
    is_bookmarked = tip['id'] in st.session_state.bookmarks
    
    # HTML Card Container
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
    
    # --- XỬ LÝ ẢNH & ZOOM ---
    if tip.get('image'):
        image_path = os.path.join("images", tip['image'])
        if os.path.exists(image_path):
            img = Image.open(image_path)
            
            # Logic xoay ảnh (Giữ nguyên yêu cầu của bạn)
            cid = tip.get('id', 0)
            if 1 <= cid <= 36:
                img = img.rotate(-270, expand=True)
            elif 37 <= cid <= 51:
                img = img.rotate(-90, expand=True)
            
            # Hiển thị ảnh nhỏ
            st.image(img, use_container_width=True)
            
            # Nút bấm Zoom (Dùng key unique theo ID để không lỗi)
            if st.button("🔍 Bấm để phóng to", key=f"zoom_{tip['id']}"):
                show_large_image(img, tip['title'])
    
    # --- CHECKBOX LƯU ---
    col1, col2 = st.columns([0.75, 0.25])
    with col2:
        if st.checkbox("Lưu", value=is_bookmarked, key=f"bk_{tip['id']}"):
            st.session_state.bookmarks.add(tip['id'])
        else:
            st.session_state.bookmarks.discard(tip['id'])
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- 8. CHƯƠNG TRÌNH CHÍNH ---
def main():
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
