import streamlit as st
import json
import os

# Cấu hình trang
st.set_page_config(
    page_title="Mẹo 600 Câu Lý Thuyết",
    page_icon="🚗",
    layout="wide"
)

# CSS tùy chỉnh để làm đẹp (Tô đỏ tiêu đề và mũi tên)
st.markdown("""
<style>
    .tip-title { color: #d32f2f; font-weight: bold; font-size: 1.2rem; margin-bottom: 10px; }
    .highlight { color: #d32f2f; font-weight: 900; background-color: #ffebee; padding: 0 5px; border-radius: 4px; }
    .card { background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border: 1px solid #f0f0f0; }
</style>
""", unsafe_allow_html=True)

# Đọc dữ liệu
@st.cache_data
def load_data():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def main():
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
        # Chia lưới 3 cột (responsive)
        cols = st.columns(3)
        
        for i, tip in enumerate(results):
            with cols[i % 3]: # Phân phối thẻ vào 3 cột
                # Bắt đầu thẻ Card
                with st.container():
                    st.markdown(f'<div class="card">', unsafe_allow_html=True)
                    
                    # Tiêu đề
                    st.markdown(f'<div class="tip-title">{tip["title"]}</div>', unsafe_allow_html=True)
                    
                    # Nội dung
                    for line in tip['content']:
                        # Xử lý tô màu mũi tên
                        formatted_line = line.replace("=>", "<span class='highlight'>=></span>")
                        st.markdown(f"- {formatted_line}", unsafe_allow_html=True)
                    
                    # Hình ảnh
                    if tip.get('image'):
                        image_path = os.path.join("images", tip['image'])
                        if os.path.exists(image_path):
                            st.image(image_path, caption="Hình minh họa", use_column_width=True)
                    
                    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()