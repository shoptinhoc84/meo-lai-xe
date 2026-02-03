import streamlit as st
import json
import os

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX SHOPTINHOC",
    page_icon="🚗",
    layout="wide"
)

# --- 2. KHỞI TẠO STATE (Lưu trạng thái) ---
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# --- 3. CSS GIAO DIỆN (Làm đẹp) ---
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
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

@st.cache_data
def load_tips(license_type):
    """Load dữ liệu Mẹo thi"""
    try:
        if "Ô tô" in license_type:
            file_path = 'data.json'
        else:
            file_path = 'tips_a1.json'
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Không tìm thấy file {file_path}. Hãy kiểm tra lại thư mục.")
        return []

@st.cache_data
def load_600_questions():
    """Load dữ liệu 600 câu hỏi"""
    try:
        # File JSON 600 câu bạn đã đổi tên
        with open('dulieu_600_cau.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_image_path(image_name, folder="images"):
    """
    Trả về đường dẫn ảnh (String) để Streamlit tự xử lý.
    Khắc phục lỗi ảnh bị xoay/lật ngược do thư viện PIL cũ.
    """
    if not image_name: return None
    
    # Tạo đường dẫn
    img_path = os.path.join(folder, image_name)
    
    # Kiểm tra file có tồn tại không
    if os.path.exists(img_path):
        return img_path
    return None

# --- 5. GIAO DIỆN: HỌC MẸO ---
def render_tips_page(data, is_oto):
    st.header(f"📖 Mẹo Thi Lý Thuyết {'Ô Tô' if is_oto else 'Xe Máy'}")
    
    # Bộ lọc danh mục
    if data:
        categories = list(set([item.get('category', 'Khác') for item in data]))
        selected_cat = st.selectbox("Chọn danh mục:", ["Tất cả"] + categories)
        
        filtered_data = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
        
        for tip in filtered_data:
            with st.container():
                st.markdown(f"""
                <div class="tip-card">
                    <h3>{tip.get('title', 'Mẹo')}</h3>
                </div>
                """, unsafe_allow_html=True)
                
                cols = st.columns([2, 1])
                with cols[0]:
                    content = tip.get('content', [])
                    for line in content:
                        st.markdown(f"• {line}")
                with cols[1]:
                    if tip.get('image'):
                        # Gửi đường dẫn trực tiếp cho st.image
                        img_path = get_image_path(tip['image'])
                        if img_path: 
                            st.image(img_path, use_container_width=True)
    else:
        st.info("Chưa có dữ liệu mẹo.")

# --- 6. GIAO DIỆN: LUYỆN THI 600 CÂU ---
def render_exam_page():
    st.header("📝 Luyện Tập 600 Câu Hỏi")
    
    questions = load_600_questions()
    
    if not questions:
        st.error("⚠️ LỖI: Chưa tìm thấy file `dulieu_600_cau.json`.")
        st.info("Vui lòng tải file JSON về, đổi tên thành 'dulieu_600_cau.json' và để cùng thư mục với app.py")
        return

    total_q = len(questions)
    
    # --- THANH ĐIỀU HƯỚNG ---
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Nút lùi
    with col1:
        if st.button("⬅️ Câu trước"):
            if st.session_state.current_q_index > 0:
                st.session_state.current_q_index -= 1
                st.session_state.show_answer = False
                st.rerun()
                
    # Nút tiến
    with col3:
        if st.button("Câu sau ➡️"):
            if st.session_state.current_q_index < total_q - 1:
                st.session_state.current_q_index += 1
                st.session_state.show_answer = False
                st.rerun()
                
    # Ô nhập số nhảy câu
    with col2:
        new_index = st.number_input(
            "Đi đến câu số:", 
            min_value=1, 
            max_value=total_q, 
            value=st.session_state.current_q_index + 1
        )
        if new_index - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_index - 1
            st.session_state.show_answer = False
            st.rerun()

    # --- HIỂN THỊ CÂU HỎI ---
    q = questions[st.session_state.current_q_index]
    
    st.markdown(f"""
    <div class="question-box">
        <h4>Câu {q['id']}: {q['question']}</h4>
        <p style='color: #666; font-size: 0.9em; margin-top: 5px;'>Phân loại: {q.get('category', 'Chung')}</p>
    </div>
    """, unsafe_allow_html=True)

    # --- HIỂN THỊ ẢNH (FIX LỖI LẬT) ---
    if q.get('image'):
        # Gọi hàm lấy đường dẫn (string) thay vì mở bằng PIL
        img_path = get_image_path(q['image']) 
        if img_path:
            # width=500 giúp ảnh không bị quá to tràn màn hình
            st.image(img_path, caption=f"Hình minh họa câu {q['id']}", width=500)
        else:
            # Chỉ hiện cảnh báo nếu câu hỏi thuộc loại Sa hình/Biển báo mà thiếu ảnh
            cat = q.get('category', '')
            if "Sa hình" in cat or "Biển báo" in cat:
                st.warning(f"⚠️ Không tìm thấy ảnh: {q['image']} trong thư mục images/")

    # --- LỰA CHỌN ĐÁP ÁN ---
    st.write("---")
    st.write("**Chọn đáp án:**")
    
    # Key unique để reset radio khi đổi câu hỏi
    selected_option = st.radio(
        "Lựa chọn:", 
        q['options'], 
        index=None, 
        key=f"radio_q{q['id']}", 
        label_visibility="collapsed"
    )

    # Nút kiểm tra
    if st.button("🔍 Kiểm tra kết quả", type="primary"):
        st.session_state.show_answer = True

    # Hiển thị kết quả
    if st.session_state.show_answer:
        st.divider()
        if selected_option:
            # So sánh chuỗi (strip để xóa khoảng trắng thừa nếu có)
            if selected_option.strip() == q['correct_answer'].strip():
                st.success("🎉 CHÍNH XÁC! Chúc mừng bạn.")
            else:
                st.error("Rất tiếc, câu trả lời chưa đúng.")
                st.info(f"👉 Đáp án đúng là: **{q['correct_answer']}**")
        else:
            st.warning("Bạn hãy chọn một đáp án trước khi kiểm tra nhé!")
            st.info(f"👉 Đáp án đúng là: **{q['correct_answer']}**")

# --- 7. CHẠY ỨNG DỤNG ---
def main():
    with st.sidebar:
        st.title("🗂️ ÔN THI GPLX")
        st.write("---")
        
        # Chọn loại bằng
        old_license = st.session_state.license_type
        current_license = st.selectbox(
            "Chọn hạng bằng:", 
            ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"]
        )
        
        if current_license != old_license:
            st.session_state.license_type = current_license
            st.cache_data.clear()
            st.rerun()

        # Menu
        page = st.radio("Chế độ học:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        
        st.write("---")
        st.caption("Phiên bản 2.1 (Fix Image Rotation)")

    is_oto = "Ô tô" in st.session_state.license_type

    if page == "📖 Học Mẹo":
        data = load_tips(st.session_state.license_type)
        render_tips_page(data, is_oto)
            
    elif page == "📝 Luyện Thi (600 câu)":
        render_exam_page()

if __name__ == "__main__":
    main()
