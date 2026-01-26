import streamlit as st
import json
import os
from PIL import Image

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
    # --- CẤU HÌNH TỰ ĐỘNG ---
    MOC_CHUYEN_DOI = 36 
    
    st.sidebar.title("⚙️ Cài đặt hiển thị")
    view_mode = st.sidebar.radio("Chọn bố cục:", ["Danh sách (1 cột)", "Lưới (3 cột)"], index=0)
    
    # Hiển thị thông báo trạng thái
    st.sidebar.success(
        f"✅ Đang tự động xử lý:\n"
        f"- Câu 1-{MOC_CHUYEN_DOI}: Giữ nguyên (0°)\n"
        f"- Câu {MOC_CHUYEN_DOI+1}+: Xoay 270°"
    )

    st.title("🚗 MẸO GIẢI NHANH 600 CÂU LÝ THUYẾT")
    st.caption("Tra cứu nhanh các mẹo học lý thuyết lái xe ô tô")

    search_query = st.text_input("", placeholder="🔍 Nhập từ khóa (ví dụ: tốc độ, độ tuổi, biển báo...)...")

    try:
        data = load_data()
    except FileNotFoundError:
        st.error("Lỗi: Không tìm thấy file data.json")
        return

    # Lọc dữ liệu
    if search_query:
        results = [tip for tip in data if search_query.lower() in tip['title'].lower() or any(search_query.lower() in line.lower() for line in tip['content'])]
    else:
        results = data

    if not results:
        st.warning(f"Không tìm thấy mẹo nào cho từ khóa: '{search_query}'")
    else:
        # Xử lý hiển thị
        if "3 cột" in view_mode:
            cols = st.columns(3)
        else:
            cols = [st.container() for _ in range(len(results))]

        for i, tip in enumerate(results):
            col = cols[i % 3] if "3 cột" in view_mode else cols[i]

            with col:
                st.markdown(f'<div class="card">', unsafe_allow_html=True)
                st.markdown(f'<div class="tip-title">{tip["title"]}</div>', unsafe_allow_html=True)
                
                # Nội dung chữ
                for line in tip['content']:
                    formatted_line = line.replace("=>", "<span class='highlight'>=></span>")
                    st.markdown(f"- {formatted_line}", unsafe_allow_html=True)
                
                # Hình ảnh
                if tip.get('image'):
                    image_path = os.path.join("images", tip['image'])
                    if os.path.exists(image_path):
                        img = Image.open(image_path)
                        
                        # --- LOGIC XOAY ẢNH CHUẨN ---
                        current_id = tip.get('id', 0)
                        
                        if current_id <= MOC_CHUYEN_DOI:
                            # Từ câu 1 đến 36: Giữ nguyên (0 độ)
                            pass 
                        else:
                            # Từ câu 37 trở đi: Xoay 270 độ
                            img = img.rotate(-270, expand=True)
                        # ----------------------------
                            
                        st.image(img, caption=f"Hình minh họa", use_container_width=True)
                
                st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()
