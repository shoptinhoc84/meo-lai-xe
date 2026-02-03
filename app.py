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
# State cho phần Luyện Thi
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
    .correct-answer { color: #28a745; font-weight: bold; }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def load_tips(license_type):
    """Load dữ liệu Mẹo thi (file cũ của bạn)"""
    try:
        if "Ô tô" in license_type:
            with open('data.json', 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            with open('tips_a1.json', 'r', encoding='utf-8') as f:
                return json.load(f)
    except FileNotFoundError:
        st.error("Không tìm thấy file dữ liệu mẹo (data.json hoặc tips_a1.json)!")
        return []

@st.cache_data
def load_600_questions():
    """Load dữ liệu 600 câu hỏi (file mới)"""
    try:
        # Bạn nhớ đổi tên file json 600 câu thành 'dulieu_600_cau.json'
        with open('dulieu_600_cau.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def process_image(image_name, folder="images"):
    """Xử lý đường dẫn ảnh"""
    if not image_name: return None
    # Giả sử bạn bỏ tất cả ảnh vào thư mục 'images'
    img_path = os.path.join(folder, image_name)
    if os.path.exists(img_path):
        return Image.open(img_path)
    return None

# --- 5. GIAO DIỆN: HỌC MẸO (Code cũ của bạn) ---
def render_tips_page(data, is_oto):
    st.header(f"📖 Mẹo Thi Lý Thuyết {'Ô Tô' if is_oto else 'Xe Máy'}")
    
    # Filter
    categories = list(set([item['category'] for item in data]))
    selected_cat = st.selectbox("Chọn danh mục:", ["Tất cả"] + categories)
    
    filtered_data = data if selected_cat == "Tất cả" else [d for d in data if d['category'] == selected_cat]
    
    for tip in filtered_data:
        with st.container():
            st.markdown(f"""
            <div class="tip-card">
                <h3>{tip['title']}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            cols = st.columns([2, 1])
            with cols[0]:
                for line in tip['content']:
                    st.markdown(f"• {line}")
            with cols[1]:
                if tip.get('image'):
                    img = process_image(tip['image'])
                    if img: st.image(img, use_container_width=True)

# --- 6. GIAO DIỆN: LUYỆN THI (Mới thêm vào) ---
def render_exam_page():
    st.header("📝 Luyện Tập 600 Câu Hỏi")
    
    questions = load_600_questions()
    
    if not questions:
        st.error("⚠️ Chưa tìm thấy file `dulieu_600_cau.json`. Hãy copy file json tôi đã tạo và đổi tên lại.")
        return

    total_q = len(questions)
    
    # Thanh điều hướng câu hỏi
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        if st.button("⬅️ Câu trước"):
            if st.session_state.current_q_index > 0:
                st.session_state.current_q_index -= 1
                st.session_state.show_answer = False
                st.rerun()
    with col3:
        if st.button("Câu sau ➡️"):
            if st.session_state.current_q_index < total_q - 1:
                st.session_state.current_q_index += 1
                st.session_state.show_answer = False
                st.rerun()
    with col2:
        # Nhập số để nhảy câu
        new_index = st.number_input("Đi đến câu số:", min_value=1, max_value=total_q, value=st.session_state.current_q_index + 1)
        if new_index - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_index - 1
            st.session_state.show_answer = False
            st.rerun()

    # Lấy câu hỏi hiện tại
    q = questions[st.session_state.current_q_index]
    
    # Hiển thị nội dung câu hỏi
    st.markdown(f"""
    <div class="question-box">
        <h4>Câu {q['id']}: {q['question']}</h4>
        <span style='color: #666; font-size: 0.9em;'>Phân loại: {q.get('category', 'Chung')}</span>
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị ảnh (nếu có)
    if q.get('image'):
        # Lưu ý: File json mới ảnh tên là "ID.jpg", cần đảm bảo thư mục images có ảnh này
        img = process_image(q['image']) 
        if img:
            st.image(img, caption=f"Hình câu {q['id']}", width=400) # Giới hạn chiều rộng cho đẹp

    # Hiển thị lựa chọn đáp án
    st.write("---")
    st.write("**Lựa chọn đáp án:**")
    
    # Sử dụng radio để chọn (nhưng cần key unique để không bị lỗi duplicate widget)
    selected_option = st.radio(
        "Chọn đáp án:", 
        q['options'], 
        index=None, 
        key=f"radio_{q['id']}",
        label_visibility="collapsed"
    )

    # Nút kiểm tra kết quả
    if st.button("🔍 Kiểm tra đáp án", type="primary"):
        st.session_state.show_answer = True

    # Hiển thị kết quả
    if st.session_state.show_answer:
        st.divider()
        if selected_option:
            # So sánh chuỗi (cần xử lý cẩn thận vì text có thể khác nhau chút ít về khoảng trắng)
            is_correct = selected_option.strip() == q['correct_answer'].strip()
            
            if is_correct:
                st.success("🎉 Chính xác! Bạn giỏi quá.")
            else:
                st.error("Rất tiếc, chưa đúng rồi.")
                st.info(f"👉 Đáp án đúng là: **{q['correct_answer']}**")
        else:
            st.warning("Bạn chưa chọn đáp án nào cả!")
            st.info(f"👉 Đáp án đúng là: **{q['correct_answer']}**")


# --- 7. MAIN APP ---
def main():
    with st.sidebar:
        st.title("🗂️ HỆ THỐNG ÔN THI")
        
        # Chọn hạng bằng
        old_license = st.session_state.license_type
        current_license = st.selectbox(
            "Chọn hạng bằng:", 
            ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"]
        )
        
        if current_license != old_license:
            st.session_state.license_type = current_license
            st.cache_data.clear()
            st.rerun()

        # MENU CHÍNH
        page = st.radio("Menu chính:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        
        st.write("---")
        st.info("Ứng dụng hỗ trợ ôn thi GPLX\nPhiên bản: 2.0")

    is_oto = "Ô tô" in st.session_state.license_type

    if page == "📖 Học Mẹo":
        data = load_tips(st.session_state.license_type)
        if data:
            render_tips_page(data, is_oto)
            
    elif page == "📝 Luyện Thi (600 câu)":
        render_exam_page()

if __name__ == "__main__":
    main()
