import streamlit as st
import json
import os
from PIL import Image

# --- 1. CẤU HÌNH TRANG & GIAO DIỆN ---
st.set_page_config(
    page_title="Ôn Thi 600 Câu",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed" # Thu gọn menu để rộng chỗ trên điện thoại
)

# --- 2. CSS TỐI ƯU CHO ĐIỆN THOẠI & PC ---
st.markdown("""
<style>
    /* Chỉnh font chữ toàn bộ web to hơn */
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
    }
    
    /* Giao diện thẻ bài (Card) */
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.08); /* Đổ bóng nhẹ */
        border-left: 5px solid #d32f2f; /* Viền đỏ bên trái làm điểm nhấn */
        transition: transform 0.2s;
    }
    div.tip-card:hover {
        transform: translateY(-2px); /* Hiệu ứng nổi khi di chuột */
        box-shadow: 0 6px 15px rgba(0,0,0,0.12);
    }

    /* Tiêu đề của Mẹo */
    .tip-header {
        color: #b71c1c;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 12px;
        border-bottom: 1px dashed #eee;
        padding-bottom: 8px;
    }

    /* Phần nội dung chữ */
    .tip-content {
        font-size: 1.1rem; /* Chữ to dễ đọc trên đt */
        line-height: 1.6;
        color: #333;
    }
    
    /* Highlight đáp án/từ khóa */
    .highlight {
        background-color: #ffebee;
        color: #c62828;
        font-weight: bold;
        padding: 2px 6px;
        border-radius: 4px;
        border: 1px solid #ffcdd2;
    }

    /* Ảnh minh họa */
    .tip-image {
        margin-top: 15px;
        border-radius: 8px;
        border: 1px solid #ddd;
    }

    /* Ẩn bớt khoảng trắng thừa của Streamlit trên Mobile */
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def load_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Tự động gán category mặc định nếu thiếu
            for item in data:
                if 'category' not in item:
                    item['category'] = "Chung"
            return data
    except FileNotFoundError:
        return []

# --- 4. HÀM HIỂN THỊ MỘT THẺ MẸO ---
def render_tip_card(tip, show_answer):
    # Container HTML cho thẻ
    html_content = f"""
    <div class="tip-card">
        <div class="tip-header">{tip['title']}</div>
        <div class="tip-content">
    """
    
    # Xử lý từng dòng nội dung
    for line in tip['content']:
        if "=>" in line:
            parts = line.split("=>")
            question_part = parts[0]
            answer_part = parts[1]
            
            # Logic Che/Hiện đáp án
            if show_answer:
                # Hiện đáp án đẹp
                display_line = f"{question_part} <span class='highlight'>👉 {answer_part}</span>"
            else:
                # Che đáp án (hiện dấu ???)
                display_line = f"{question_part} <span style='color:#bbb; border:1px dashed #ccc; padding:0 5px'>??? (Bấm hiện để xem)</span>"
        else:
            display_line = line
            
        html_content += f"<div>• {display_line}</div>"
    
    html_content += "</div></div>"
    st.markdown(html_content, unsafe_allow_html=True)

    # Xử lý ảnh (Dùng st.image của Streamlit để tận dụng tính năng zoom/full width)
    if tip.get('image'):
        image_path = os.path.join("images", tip['image'])
        if os.path.exists(image_path):
            img = Image.open(image_path)
            
            # --- LOGIC XOAY ẢNH CHUẨN CỦA BẠN ---
            current_id = tip.get('id', 0)
            if 1 <= current_id <= 36:
                img = img.rotate(-270, expand=True)
            elif 37 <= current_id <= 51:
                img = img.rotate(-90, expand=True)
            # ------------------------------------
            
            st.image(img, use_container_width=True)


# --- 5. CHƯƠNG TRÌNH CHÍNH ---
def main():
    data = load_data()
    if not data:
        st.error("⚠️ Lỗi: Không tìm thấy file data.json")
        return

    # --- MENU BÊN TRÁI ---
    with st.sidebar:
        st.header("⚙️ Cài đặt học tập")
        
        # 1. Chế độ học (Tính năng mới!)
        mode = st.radio("Chế độ:", ["📖 Xem đáp án", "🫣 Học thuộc (Che đáp án)"])
        show_result = True if mode == "📖 Xem đáp án" else False
        
        st.divider()
        st.info("💡 **Mẹo:** Chọn chế độ **'Học thuộc'** để tự kiểm tra trí nhớ, sau đó chuyển sang **'Xem đáp án'** để đối chiếu.")

    # --- GIAO DIỆN CHÍNH ---
    st.title("🚗 MẸO 600 CÂU LÝ THUYẾT by SHOPTINHOC")
    
    # 1. Thanh tìm kiếm
    search = st.text_input("", placeholder="🔍 Tìm kiếm nhanh (vd: nồng độ cồn, cao tốc, 18 tuổi...)...")

    # 2. Phân loại Category (Tạo Tabs)
    # Lấy danh sách các danh mục duy nhất từ dữ liệu
    categories = ["Tất cả"] + sorted(list(set([t['category'] for t in data])))
    
    # Nếu đang tìm kiếm thì không hiện Tabs (để tránh rối)
    if search:
        st.subheader(f"Kết quả tìm kiếm cho: '{search}'")
        filtered_data = [t for t in data if search.lower() in t['title'].lower() or any(search.lower() in x.lower() for x in t['content'])]
        if not filtered_data:
            st.warning("Không tìm thấy kết quả nào.")
        else:
            for tip in filtered_data:
                render_tip_card(tip, show_result)
    else:
        # Tạo giao diện Tabs cực tiện cho điện thoại
        tabs = st.tabs(categories)
        
        for i, category in enumerate(categories):
            with tabs[i]:
                # Lọc dữ liệu theo tab
                if category == "Tất cả":
                    current_tips = data
                else:
                    current_tips = [t for t in data if t['category'] == category]
                
                # Hiển thị
                for tip in current_tips:
                    render_tip_card(tip, show_result)

if __name__ == "__main__":
    main()

