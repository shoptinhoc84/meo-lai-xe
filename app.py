import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Hệ Thống Ôn Thi GPLX Quốc Gia",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. KHỞI TẠO STATE ---
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'exam_category' not in st.session_state:
    st.session_state.exam_category = "Tất cả"

# --- 3. CSS GIAO DIỆN CAO CẤP ---
st.markdown("""
<style>
    /* Nền chung xám nhẹ dịu mắt */
    .stApp {
        background-color: #f0f2f5;
    }
    
    /* Box chứa câu hỏi: Bo tròn, đổ bóng, nền trắng */
    .question-card {
        background-color: #ffffff;
        border-radius: 15px;
        padding: 30px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-left: 8px solid #007bff; /* Điểm nhấn màu xanh bên trái */
    }
    
    /* Tiêu đề câu hỏi */
    .q-header {
        font-size: 0.9rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
        display: flex;
        justify-content: space-between;
    }
    
    .q-content {
        font-size: 1.3rem;
        font-weight: 600;
        color: #212529;
        line-height: 1.5;
        margin-bottom: 20px;
    }

    /* Tùy chỉnh Radio Button (Đáp án) */
    div[role="radiogroup"] {
        display: flex;
        flex-direction: column;
        gap: 12px;
    }
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #ffffff;
        border: 2px solid #e9ecef;
        padding: 15px 20px;
        border-radius: 10px;
        width: 100%;
        display: flex;
        align-items: center;
        transition: all 0.2s ease;
        font-size: 1rem;
    }
    /* Hiệu ứng khi di chuột vào đáp án */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #007bff;
        background-color: #f8fbff;
        transform: translateY(-2px);
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }

    /* Style cho thanh chọn chủ đề (Horizontal Radio) */
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] {
        background: white;
        padding: 10px;
        border-radius: 12px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        justify-content: center;
    }
    
    /* Căn giữa ảnh */
    div[data-testid="stImage"] { 
        display: flex; 
        justify-content: center; 
        margin: 15px 0;
        background: #fff;
        padding: 10px;
        border-radius: 10px;
    }
    
    /* Sidebar: Bảng lưới câu hỏi */
    .grid-btn {
        display: inline-block;
        width: 35px;
        height: 35px;
        line-height: 35px;
        text-align: center;
        margin: 2px;
        border-radius: 4px;
        font-size: 0.8rem;
        background-color: #e9ecef;
        color: #333;
        text-decoration: none;
    }
    .grid-btn.active {
        background-color: #007bff;
        color: white;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

@st.cache_data
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_data_by_license(license_type):
    is_oto = "Ô tô" in license_type
    files_oto = ['data.json', 'data (6).json']
    files_xe_may = ['tips_a1.json', 'tips_a1 (1).json']
    target_files = files_oto if is_oto else files_xe_may
    
    for fname in target_files:
        data = load_json_file(fname)
        if data: return data
    return []

def load_image_strict(image_name, folders_allowed):
    if not image_name: return None
    img_name = str(image_name).strip()
    
    for folder in folders_allowed:
        path = os.path.join(folder, img_name)
        if os.path.exists(path) and os.path.isfile(path):
            try:
                img = Image.open(path)
                return ImageOps.exif_transpose(img)
            except: continue
    return None

# --- 5. GIAO DIỆN HỌC MẸO ---
def render_tips_page(license_type):
    st.title(f"📖 Mẹo Thi Lý Thuyết {license_type}")
    data = load_data_by_license(license_type)
    if not data:
        st.error("Chưa tìm thấy dữ liệu mẹo.")
        return

    categories = sorted(list(set([i.get('category', 'Khác') for i in data])))
    
    st.write("---")
    selected_cat = st.radio("Chủ đề:", ["Tất cả"] + categories, horizontal=True)
    st.write("---")

    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    for tip in items:
        with st.container():
            st.markdown(f"""
            <div class="question-card" style="border-left: 6px solid #28a745;">
                <h3 style="margin-top:0;">📌 {tip.get("title", "Mẹo")}</h3>
            </div>
            """, unsafe_allow_html=True)
            
            c1, c2 = st.columns([1.5, 1])
            with c1:
                for line in tip.get('content', []):
                    line = line.replace("=>", "👉 <b style='color:#d63384'>")
                    if "👉" in line: line += "</b>"
                    st.markdown(f"• {line}", unsafe_allow_html=True)
            with c2:
                if tip.get('image'):
                    folders = ["images", "images_a1"] if "Ô tô" in license_type else ["images_a1", "images"]
                    img = load_image_strict(tip['image'], folders)
                    if img: st.image(img, use_container_width=True)

# --- 6. GIAO DIỆN LUYỆN THI ---
def render_exam_page():
    # Load dữ liệu
    all_questions = load_json_file('dulieu_600_cau.json')
    if not all_questions:
        st.error("⚠️ Lỗi file dữ liệu.")
        return

    categories = sorted(list(set([q.get('category', 'Khác') for q in all_questions])))

    # HEADER & FILTER
    st.markdown("### 📝 Luyện Tập Sát Hạch GPLX")
    
    # Thanh chọn chủ đề nằm ngang (được CSS làm đẹp)
    selected_cat = st.radio(
        "Filter", 
        ["Tất cả"] + categories, 
        horizontal=True, 
        label_visibility="collapsed"
    )

    # Logic lọc
    if selected_cat != st.session_state.exam_category:
        st.session_state.exam_category = selected_cat
        st.session_state.current_q_index = 0
        st.rerun()

    if selected_cat == "Tất cả":
        filtered_questions = all_questions
    else:
        filtered_questions = [q for q in all_questions if q.get('category') == selected_cat]

    total = len(filtered_questions)
    if st.session_state.current_q_index >= total: st.session_state.current_q_index = 0
    
    q = filtered_questions[st.session_state.current_q_index]

    # --- SIDEBAR: BẢNG LƯỚI CÂU HỎI ---
    with st.sidebar:
        st.divider()
        st.write(f"📊 **Danh sách câu hỏi ({selected_cat})**")
        st.caption("Nhập số thứ tự để nhảy nhanh:")
        
        # Nhập số để nhảy nhanh
        new_idx = st.number_input("Đi tới câu số:", 1, total, st.session_state.current_q_index + 1)
        if new_idx - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_idx - 1
            st.rerun()
            
        st.progress((st.session_state.current_q_index + 1) / total)
        st.caption(f"Tiến độ: {st.session_state.current_q_index + 1}/{total}")

    # --- MAIN CONTENT: KHUNG CÂU HỎI ---
    
    # Hiển thị thẻ câu hỏi (HTML/CSS)
    st.markdown(f"""
    <div class="question-card">
        <div class="q-header">
            <span>Câu hỏi {st.session_state.current_q_index + 1} / {total}</span>
            <span style="background:#e9ecef; color:#495057; padding:2px 10px; border-radius:12px; font-size:0.75rem;">
                {q.get('category','Chung')}
            </span>
        </div>
        <div class="q-content">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Xử lý ảnh (Fix cứng câu 1)
    if q['id'] == 1: q['image'] = None
    if q.get('image'):
        img = load_image_strict(q['image'], folders_allowed=['images'])
        if img: st.image(img, width=500)

    # Đáp án & Kết quả
    c1, c2 = st.columns([0.1, 0.9]) # Layout chỉnh lề
    
    # Radio Button
    user_choice = st.radio("Lựa chọn:", q['options'], index=None, key=f"q_{q['id']}")

    # Thông báo kết quả ngay lập tức
    if user_choice:
        correct = q['correct_answer'].strip()
        is_correct = user_choice.strip() == correct
        
        if is_correct:
            st.success(f"✅ CHÍNH XÁC! Đáp án: {correct}")
        else:
            st.error(f"❌ SAI RỒI! Đáp án đúng là: {correct}")

    st.write("---")

    # NÚT ĐIỀU HƯỚNG TO VÀ RÕ RÀNG
    col_prev, col_spacer, col_next = st.columns([1, 2, 1])
    with col_prev:
        if st.button("⬅️ Câu Trước", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.rerun()
    with col_next:
        if st.button("Câu Sau ➡️", use_container_width=True):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.rerun()

# --- 7. MAIN APP ---
def main():
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/3097/3097180.png", width=60)
        st.title("GPLX PRO")
        
        st.markdown("---")
        license = st.selectbox("Hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license != st.session_state.license_type:
            st.session_state.license_type = license
            st.session_state.current_q_index = 0
            st.cache_data.clear()
            st.rerun()

        mode = st.radio("Chế độ ôn tập:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        
    if mode == "📖 Học Mẹo":
        render_tips_page(st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
