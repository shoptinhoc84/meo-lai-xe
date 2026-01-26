import streamlit as st
import json
import os
from PIL import Image  # Thư viện xử lý ảnh

# Cấu hình trang
st.set_page_config(
    page_title="Mẹo 600 Câu Lý Thuyết",
    page_icon="🚗",
    layout="wide"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .tip-title { color: #d32f2f; font-weight: bold; font-size: 1.4rem; margin-bottom: 10px; }
    .highlight { color: #d32f2f; font-weight: 900; background-color: #ffebee; padding: 0 5px; border-radius: 4px; }
    .card { background-color: white; padding: 25px; border-radius: 12px; box-shadow: 0 4px 8px rgba(0,0,0,0.08); margin-bottom: 25px; border: 1px solid #eee; }
    img { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# Đọc dữ liệu
@st.cache_data
def load_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
    # --- THANH CÔNG CỤ BÊN TRÁI (SIDEBAR) ---
    st.sidebar.title("⚙️ Cài đặt hiển thị")
    
    # 1. Chọn chế độ xem (Giải quyết vấn đề ảnh bị dọc/nhỏ)
    view_mode = st.sidebar.radio(
        "Chọn bố cục:",
        ["Danh sách (1 cột) - Ảnh to", "Lưới (3 cột) - Nhìn bao quát"],
        index=0 # Mặc định chọn 1 cột để ảnh nằm ngang
    )
    
    # 2. Xoay ảnh (Giải quyết nếu ảnh bị nghiêng)
    rotate_option = st.sidebar.select_slider(
        "Xoay chiều ảnh (nếu ảnh bị ngược):",
        options=[0, 90, 180, 270],
        value=0
    )

    st.title("🚗 MẸO GIẢI NHANH 600 CÂU LÝ THUYẾT")
    st.caption("Tra cứu nhanh các mẹo học lý thuyết lái xe ô tô")

    # Thanh tìm kiếm
    search_query = st.text_input("", placeholder="🔍 Nhập từ khóa (ví dụ: tốc độ, độ tuổi, biển báo...)...")

    try:
        data = load_data()
    except FileNotFoundError:
        st.error("Lỗi: Không tìm thấy file data.json")
        return

    # Lọc dữ liệu
    if search_query:
        results = [
            tip for tip in data 
            if search_query.lower() in tip['title'].lower() 
            or any(search_query.lower() in line.lower() for line in tip['content'])
        ]
    else:
        results = data

    # Hiển thị kết quả
    if not results:
        st.warning(f"Không tìm thấy mẹo nào cho từ khóa: '{search_query}'")
    else:
        # Xử lý hiển thị theo chế độ đã chọn
        if "3 cột" in view_mode:
            cols = st.columns(3)
        else:
            cols = [st.container() for _ in range(len(results))] # Tạo danh sách container ảo

        for i, tip in enumerate(results):
            # Chọn vị trí hiển thị (Nếu 3 cột thì chia, nếu 1 cột thì xếp dọc)
            if "3 cột" in view_mode:
                col = cols[i % 3]
            else:
                col = cols[i] # 1 cột thì cứ lấy container tiếp theo

            with col:
                st.markdown(f'<div class="card">', unsafe_allow_html=True)
                
                # Tiêu đề
                st.markdown(f'<div class="tip-title">{tip["title"]}</div>', unsafe_allow_html=True)
                
                # Nội dung chữ
                for line in tip['content']:
                    formatted_line = line.replace("=>", "<span class='highlight'>=></span>")
                    st.markdown(f"- {formatted_line}", unsafe_allow_html=True)
                
                # Hình ảnh
                if tip.get('image'):
                    image_path = os.path.join("images", tip['image'])
                    if os.path.exists(image_path):
                        # Mở ảnh bằng PIL để xử lý xoay
                        img = Image.open(image_path)
                        
                        # Xoay ảnh nếu người dùng chọn trong Sidebar
                        if rotate_option != 0:
                            img = img.rotate(-rotate_option, expand=True)
                            
                        st.image(img, caption="Hình minh họa", use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
