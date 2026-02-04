import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - V12 Final Fix",
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

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    .tip-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .question-box {
        background-color: #f8f9fa; border-radius: 10px; padding: 25px;
        border-left: 6px solid #007bff; margin-bottom: 20px;
    }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    
    /* Chống lệch hàng Radio */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] div[role="radiogroup"] { gap: 10px; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 15px 20px;
        border-radius: 8px;
        width: 100%;
        display: flex;
        align-items: center; 
        margin: 0;
        cursor: pointer;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #007bff;
        background-color: #f1f8ff;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

@st.cache_data
def load_tips_data(license_type):
    try:
        file_path = 'data.json' if "Ô tô" in license_type else 'tips_a1.json'
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return []

@st.cache_data
def load_600_questions():
    try:
        with open('dulieu_600_cau.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

def load_image_v12(image_name, is_exam, question_id=None):
    """
    Hàm load ảnh cưỡng bức để sửa lỗi câu 1
    """
    if not image_name: return None
    img_name = str(image_name).strip()
    
    # Ưu tiên folder theo chế độ
    if is_exam:
        # Nếu là câu 1 của phần thi, ép buộc tìm trong folder 'images' trước
        # và TUYỆT ĐỐI không nhìn vào folder 'images_a1' hay thư mục mẹo
        search_order = ["images", ""] 
        if question_id == 1:
            # Fix cứng cho câu 1: Nếu thấy file ở images thì lấy luôn, không tìm chỗ khác
            path = os.path.join("images", img_name)
            if os.path.exists(path):
                return ImageOps.exif_transpose(Image.open(path))
    else:
        # Nếu là học mẹo
        search_order = ["images_a1", "images", ""]
        
    for folder in search_order:
        full_path = os.path.join(folder, img_name) if folder else img_name
        if os.path.exists(full_path) and os.path.isfile(full_path):
            try:
                return ImageOps.exif_transpose(Image.open(full_path))
            except: continue
    return None

# --- 5. GIAO DIỆN: HỌC MẸO ---
def render_tips_page(data, is_oto):
    st.header(f"📖 Mẹo Thi Lý Thuyết {'Ô Tô' if is_oto else 'Xe Máy'}")
    if not data: return
    
    cats = sorted(list(set([i.get('category','Khác') for i in data])))
    sel = st.selectbox("Danh mục:", ["Tất cả"] + cats)
    items = data if sel == "Tất cả" else [d for d in data if d.get('category') == sel]

    for tip in items:
        st.markdown(f'<div class="tip-card"><h3>{tip.get("title", "Mẹo")}</h3>', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            for line in tip.get('content', []):
                if "=>" in line:
                    p = line.split("=>")
                    line = f"{p[0]} => <span class='highlight'>{p[1]}</span>"
                st.markdown(f"• {line}", unsafe_allow_html=True)
        with c2:
            if tip.get('image'):
                img = load_image_v12(tip['image'], is_exam=False)
                if img: st.image(img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. GIAO DIỆN: LUYỆN THI ---
def render_exam_page(is_oto):
    st.header("📝 Luyện Tập 600 Câu Hỏi")
    questions = load_600_questions()
    if not questions: return

    total = len(questions)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Trước"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.session_state.show_answer = False
            st.rerun()
    with c3:
        if st.button("Sau ➡️"):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.session_state.show_answer = False
            st.rerun()
    with c2:
        val = st.number_input("Câu số:", 1, total, st.session_state.current_q_index + 1)
        if val - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = val - 1
            st.session_state.show_answer = False
            st.rerun()

    q = questions[st.session_state.current_q_index]
    st.markdown(f'<div class="question-box"><h4>Câu {q["id"]}: {q["question"]}</h4></div>', unsafe_allow_html=True)

    if q.get('image'):
        # Truyền q['id'] vào để hàm load ảnh biết đây là câu số mấy
        img = load_image_v12(q['image'], is_exam=True, question_id=q['id'])
        if img:
            st.image(img, width=450)
        else:
            st.caption(f"Ảnh câu hỏi: {q['image']}")

    ans = st.radio("Lựa chọn", q['options'], index=None, key=f"ans_{st.session_state.current_q_index}")
    if st.button("Kiểm tra kết quả", type="primary"):
        st.session_state.show_answer = True

    if st.session_state.show_answer:
        st.divider()
        correct = q['correct_answer'].strip()
        if ans and ans.strip() == correct:
            st.success(f"✅ Chính xác! Đáp án: {correct}")
        else:
            st.error(f"❌ Sai rồi! Đáp án đúng: {correct}")

# --- 7. MAIN ---
def main():
    with st.sidebar:
        st.title("🚗 GPLX Pro V12")
        license = st.selectbox("Hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license != st.session_state.license_type:
            st.session_state.license_type = license
            st.session_state.current_q_index = 0
            st.rerun()
        mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])

    if mode == "📖 Học Mẹo":
        render_tips_page(load_tips_data(st.session_state.license_type), "Ô tô" in st.session_state.license_type)
    else:
        render_exam_page("Ô tô" in st.session_state.license_type)

if __name__ == "__main__":
    main()
