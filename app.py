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
# State cho phần Luyện Thi 600 câu
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
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    .hidden-answer { color: #999; font-style: italic; border: 1px dashed #ccc; padding: 0 8px; border-radius: 4px; }
    .stButton button { width: 100%; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

@st.cache_data
def load_tips_data(license_type):
    """Load dữ liệu Mẹo thi (Code cũ)"""
    try:
        if "Ô tô" in license_type:
            file_path = 'data.json'
        else:
            file_path = 'tips_a1.json'
            
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"Không tìm thấy file {file_path}. Vui lòng kiểm tra lại.")
        return []

@st.cache_data
def load_600_questions():
    """Load dữ liệu 600 câu (Code mới)"""
    try:
        # Nhớ đổi tên file 600 câu thành dulieu_600_cau.json
        with open('dulieu_600_cau.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def get_image_path_string(image_name, is_oto_mode=True, is_exam_mode=False):
    """
    Hàm xử lý ảnh KHÔNG DÙNG PIL để tránh bị lật ngược.
    Trả về đường dẫn file (string) để Streamlit tự xử lý.
    """
    if not image_name: return None
    
    # Xác định thư mục ảnh
    if is_exam_mode:
        # Chế độ thi 600 câu: dùng chung thư mục images
        folder = "images" 
    else:
        # Chế độ học mẹo: giữ logic cũ (images cho Oto, images_a1 cho Xe máy)
        folder = "images" if is_oto_mode else "images_a1"
    
    # Tạo đường dẫn
    img_path = os.path.join(folder, image_name)
    
    # Kiểm tra file có tồn tại không
    if os.path.exists(img_path):
        return img_path
    
    return None

# --- 5. GIAO DIỆN: HỌC MẸO (Code từ file cũ) ---
def render_tips_page(data, is_oto):
    st.header(f"📖 Mẹo Thi Lý Thuyết {'Ô Tô' if is_oto else 'Xe Máy'}")
    
    if not data: return

    # Filter danh mục
    categories = list(set([item.get('category', 'Khác') for item in data]))
    if categories:
        selected_cat = st.selectbox("Chọn danh mục:", ["Tất cả"] + categories)
        filtered_data = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    else:
        filtered_data = data

    for tip in filtered_data:
        # Tạo Card cho mỗi mẹo
        st.markdown(f"""<div class="tip-card"><h3>{tip.get('title', 'Mẹo')}</h3>""", unsafe_allow_html=True)
        
        cols = st.columns([2, 1])
        
        # Cột nội dung text
        with cols[0]:
            content = tip.get('content', [])
            for line in content:
                # Xử lý highlight text (giữ logic cũ)
                parts = line.split("=>")
                if len(parts) > 1:
                    display_line = f"{parts[0]} => <span class='highlight'>{parts[1]}</span>"
                else:
                    display_line = line
                st.markdown(f"• {display_line}", unsafe_allow_html=True)

        # Cột hình ảnh (SỬA LỖI LẬT ẢNH)
        with cols[1]:
            if tip.get('image'):
                # Gọi hàm lấy đường dẫn String
                img_path = get_image_path_string(tip['image'], is_oto_mode=is_oto, is_exam_mode=False)
                if img_path:
                    st.image(img_path, use_container_width=True)
        
        st.markdown("</div>", unsafe_allow_html=True)


# --- 6. GIAO DIỆN: LUYỆN THI 600 CÂU (Code mới thêm) ---
def render_exam_page():
    st.header("📝 Luyện Tập 600 Câu Hỏi")
    
    questions = load_600_questions()
    
    if not questions:
        st.error("⚠️ LỖI: Chưa tìm thấy file `dulieu_600_cau.json`.")
        st.info("Hãy tải file JSON 600 câu về, đổi tên thành 'dulieu_600_cau.json' và đặt cạnh file app.py")
        return

    total_q = len(questions)
    
    # --- Thanh điều hướng ---
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Câu trước"):
            if st.session_state.current_q_index > 0:
                st.session_state.current_q_index -= 1
                st.session_state.show_answer = False
                st.rerun()
    with c3:
        if st.button("Câu sau ➡️"):
            if st.session_state.current_q_index < total_q - 1:
                st.session_state.current_q_index += 1
                st.session_state.show_answer = False
                st.rerun()
    with c2:
        new_idx = st.number_input("Đi đến câu số:", 1, total_q, st.session_state.current_q_index + 1)
        if new_idx - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_idx - 1
            st.session_state.show_answer = False
            st.rerun()

    # --- Hiển thị câu hỏi ---
    q = questions[st.session_state.current_q_index]
    
    st.markdown(f"""
    <div class="question-box">
        <h4>Câu {q['id']}: {q['question']}</h4>
        <span style='color: #666; font-size: 0.9em;'>Phân loại: {q.get('category', 'Chung')}</span>
    </div>
    """, unsafe_allow_html=True)

    # --- Hiển thị ảnh (SỬA LỖI LẬT ẢNH) ---
    if q.get('image'):
        # Mode thi = True để luôn tìm trong folder 'images'
        img_path = get_image_path_string(q['image'], is_oto_mode=True, is_exam_mode=True)
        if img_path:
            st.image(img_path, caption=f"Hình minh họa câu {q['id']}", width=500)
        else:
            # Chỉ báo lỗi nếu là câu hỏi hình ảnh
            if "Sa hình" in q.get('category', '') or "Biển báo" in q.get('category', ''):
                st.warning(f"⚠️ Không tìm thấy ảnh: {q['image']} trong thư mục images/")

    # --- Chọn đáp án ---
    st.write("**Chọn đáp án:**")
    user_choice = st.radio(
        "Answers", 
        q['options'], 
        index=None, 
        key=f"q_{q['id']}", 
        label_visibility="collapsed"
    )

    if st.button("Kiểm tra đáp án", type="primary"):
        st.session_state.show_answer = True

    if st.session_state.show_answer:
        st.divider()
        if user_choice:
            if user_choice.strip() == q['correct_answer'].strip():
                st.success("🎉 Chính xác!")
            else:
                st.error("Sai rồi!")
                st.info(f"👉 Đáp án đúng: **{q['correct_answer']}**")
        else:
            st.warning("Vui lòng chọn một đáp án.")
            st.info(f"👉 Đáp án đúng: **{q['correct_answer']}**")


# --- 7. MAIN APP (Sidebar & Routing) ---
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
        
        # Reset khi đổi loại bằng
        if current_license != old_license:
            st.session_state.license_type = current_license
            st.cache_data.clear()
            st.rerun()

        # Menu điều hướng
        mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        
        st.write("---")
        st.caption("Phiên bản: 3.0 (Fixed Image Flip)")

    is_oto = "Ô tô" in st.session_state.license_type

    if mode == "📖 Học Mẹo":
        data = load_tips_data(st.session_state.license_type)
        render_tips_page(data, is_oto)
        
    elif mode == "📝 Luyện Thi (600 câu)":
        render_exam_page()

if __name__ == "__main__":
    main()
