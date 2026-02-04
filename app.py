import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX - Chuẩn Layout",
    page_icon="🚗",
    layout="wide"
)

# --- 2. KHỞI TẠO STATE ---
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# --- 3. CSS GIAO DIỆN (ĐÃ FIX NGAY NGẮN & KHÔNG LỆCH) ---
st.markdown("""
<style>
    /* Box câu hỏi */
    .question-box {
        background-color: #ffffff; 
        border-radius: 10px; 
        padding: 20px;
        border-left: 6px solid #1a73e8; 
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    /* Fix đáp án thẳng hàng */
    div[data-testid="stRadio"] div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 12px 15px;
        border-radius: 8px;
        cursor: pointer;
        width: 100%;
        margin: 0;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #1a73e8;
        background-color: #e8f0fe;
    }

    /* Ảnh căn giữa đẹp */
    .stImage {
        display: flex;
        justify-content: center;
        padding: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM LOAD DỮ LIỆU ---
@st.cache_data
def load_600_questions(license_type):
    try:
        with open('dulieu_600_cau.json', 'r', encoding='utf-8') as f:
            full_data = json.load(f)
        
        # Nếu là xe máy, có thể lọc bớt câu hỏi nếu file JSON có trường phân loại
        if "Xe máy" in license_type:
            # Lọc các câu không thuộc về cấu tạo, sửa chữa ô tô (nếu data có category)
            return [q for q in full_data if "ô tô" not in q.get('category', '').lower()]
        return full_data
    except:
        return []

def load_image_strict(image_name, is_oto):
    """Tìm ảnh chính xác theo loại bằng để không bị dính ảnh lẫn nhau"""
    if not image_name: return None
    
    # Ưu tiên folder theo loại bằng
    folder = "images" if is_oto else "images_a1"
    path = os.path.join(folder, image_name)
    
    if os.path.exists(path):
        try:
            return ImageOps.exif_transpose(Image.open(path))
        except: return None
    
    # Nếu folder chính không có, mới tìm folder còn lại làm fallback
    other_folder = "images_a1" if is_oto else "images"
    path_fallback = os.path.join(other_folder, image_name)
    if os.path.exists(path_fallback):
        try:
            return ImageOps.exif_transpose(Image.open(path_fallback))
        except: return None
    return None

# --- 5. GIAO DIỆN LUYỆN THI ---
def render_exam_page(is_oto):
    st.subheader(f"📝 Luyện Tập Câu Hỏi {'Ô Tô' if is_oto else 'Xe Máy'}")
    
    questions = load_600_questions(st.session_state.license_type)
    if not questions:
        st.error("Không tìm thấy dữ liệu câu hỏi.")
        return

    total_q = len(questions)
    
    # Điều hướng
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Câu trước"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.session_state.show_answer = False
            st.rerun()
    with c3:
        if st.button("Câu tiếp ➡️"):
            st.session_state.current_q_index = min(total_q - 1, st.session_state.current_q_index + 1)
            st.session_state.show_answer = False
            st.rerun()
    with c2:
        val = st.number_input("Câu số:", 1, total_q, st.session_state.current_q_index + 1)
        if val - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = val - 1
            st.session_state.show_answer = False
            st.rerun()

    q = questions[st.session_state.current_q_index]
    
    # Hiển thị câu hỏi
    st.markdown(f"""
    <div class="question-box">
        <b style="color:#1a73e8">Câu {st.session_state.current_q_index + 1}:</b> {q['question']}
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị ảnh (Chỉ tìm đúng folder của loại bằng đó)
    if q.get('image'):
        img = load_image_strict(q['image'], is_oto)
        if img:
            st.image(img, width=450)

    # Đáp án
    user_choice = st.radio("Chọn đáp án:", q['options'], index=None, 
                           key=f"ex_{st.session_state.current_q_index}", 
                           label_visibility="collapsed")

    if st.button("Kiểm tra kết quả", type="primary"):
        st.session_state.show_answer = True

    if st.session_state.show_answer:
        correct = q['correct_answer'].strip()
        if user_choice and user_choice.strip() == correct:
            st.success(f"✅ Chính xác! Đáp án: {correct}")
        else:
            st.error(f"❌ Sai rồi! Đáp án đúng là: {correct}")

# --- 6. MAIN ---
def main():
    with st.sidebar:
        st.title("🗂️ ÔN THI GPLX")
        license = st.selectbox("Hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license != st.session_state.license_type:
            st.session_state.license_type = license
            st.session_state.current_q_index = 0
            st.rerun()
            
        mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi"])

    is_oto = "Ô tô" in st.session_state.license_type
    
    if mode == "📝 Luyện Thi":
        render_exam_page(is_oto)
    else:
        st.info("Chế độ Học Mẹo đang được cập nhật...")

if __name__ == "__main__":
    main()
