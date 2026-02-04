import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX - Giao Diện Mới",
    page_icon="🚗",
    layout="wide"
)

# --- 2. KHỞI TẠO STATE ---
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'exam_category' not in st.session_state:
    st.session_state.exam_category = "Tất cả"

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    .tip-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    .question-box {
        background-color: #f8f9fa; border-radius: 10px; padding: 25px;
        border-left: 6px solid #007bff; margin-bottom: 20px;
    }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    
    /* Tùy chỉnh Radio Button cho ĐÁP ÁN (Dạng dọc) */
    div[data-testid="stRadio"] > label { display: none; }
    /* Class riêng cho radio đáp án (được bọc trong st.container hoặc div cụ thể nếu cần, 
       nhưng ở đây ta chỉnh chung rồi override cho phần chủ đề sau) */
    
    div[role="radiogroup"] { gap: 10px; }
    
    /* Style chung cho radio label */
    div[role="radiogroup"] > label {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 10px 15px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.2s;
    }
    div[role="radiogroup"] > label:hover {
        border-color: #007bff;
        background-color: #f0f7ff;
    }
    
    /* CSS RIÊNG CHO RADIO CHỦ ĐỀ (HÀNG NGANG) 
       Streamlit không có class riêng dễ bắt, nên ta dùng mẹo:
       Radio hàng ngang thường có flex-direction: row.
    */
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] {
        flex-wrap: wrap; /* Cho phép xuống dòng nếu màn hình nhỏ */
        gap: 8px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] > label {
        background-color: #e9ecef; /* Màu nền xám nhạt cho nút chủ đề */
        border: none;
        padding: 8px 12px;
        font-weight: 500;
        font-size: 0.9rem;
    }
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] > label:hover {
        background-color: #dee2e6;
    }
    /* Khi được chọn (checked) */
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] label[data-checked="true"] {
        background-color: #007bff !important;
        color: white !important;
    }

    div[data-testid="stImage"] { display: flex; justify-content: center; }
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
    st.header(f"📖 Mẹo Thi Lý Thuyết {license_type}")
    data = load_data_by_license(license_type)
    if not data:
        st.warning("Chưa tìm thấy dữ liệu mẹo.")
        return

    categories = sorted(list(set([i.get('category', 'Khác') for i in data])))
    
    # CHỌN CHỦ ĐỀ MẸO (Cũng chuyển sang ngang cho đồng bộ)
    st.write("📂 **Chọn chủ đề mẹo:**")
    selected_cat = st.radio(
        "Chủ đề mẹo", 
        ["Tất cả"] + categories,
        horizontal=True,
        label_visibility="collapsed"
    )

    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    for tip in items:
        st.markdown(f'<div class="tip-card"><h3>📌 {tip.get("title", "Mẹo")}</h3>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.5, 1])
        with c1:
            for line in tip.get('content', []):
                if "=>" in line:
                    p = line.split("=>")
                    line = f"{p[0]} => <span class='highlight'>{p[1]}</span>"
                st.markdown(f"• {line}", unsafe_allow_html=True)
        with c2:
            if tip.get('image'):
                folders = ["images", "images_a1"] if "Ô tô" in license_type else ["images_a1", "images"]
                img = load_image_strict(tip['image'], folders)
                if img: st.image(img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. GIAO DIỆN LUYỆN THI (GIAO DIỆN HÀNG NGANG) ---
def render_exam_page():
    st.header("📝 Luyện Tập 600 Câu Hỏi")
    all_questions = load_json_file('dulieu_600_cau.json')
    if not all_questions:
        st.error("Lỗi file dữ liệu 600 câu.")
        return

    # Lấy danh sách chủ đề
    categories = sorted(list(set([q.get('category', 'Khác') for q in all_questions])))
    
    # --- THANH CHỌN CHỦ ĐỀ NẰM NGANG ---
    st.write("📂 **Chọn chủ đề ôn tập:**")
    selected_cat = st.radio(
        "Chọn chủ đề:", 
        ["Tất cả"] + categories,
        horizontal=True, # QUAN TRỌNG: Làm cho nó nằm ngang
        label_visibility="collapsed",
        key="cat_selection"
    )
    
    # Reset khi đổi chủ đề
    if selected_cat != st.session_state.exam_category:
        st.session_state.exam_category = selected_cat
        st.session_state.current_q_index = 0
        st.rerun()

    # Lọc câu hỏi
    if selected_cat == "Tất cả":
        filtered_questions = all_questions
    else:
        filtered_questions = [q for q in all_questions if q.get('category') == selected_cat]

    if not filtered_questions:
        st.warning(f"Không có câu hỏi nào trong chủ đề '{selected_cat}'")
        return

    total = len(filtered_questions)
    
    # Hiển thị số lượng câu hỏi của chủ đề
    st.caption(f"Đang hiển thị: {total} câu hỏi thuộc phần **{selected_cat}**")

    # Đảm bảo index hợp lệ
    if st.session_state.current_q_index >= total:
        st.session_state.current_q_index = 0

    # Điều hướng
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Câu trước", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.rerun()
    with c3:
        if st.button("Câu sau ➡️", use_container_width=True):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.rerun()
    with c2:
        val = st.number_input("Câu số:", 1, total, st.session_state.current_q_index + 1)
        if val - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = val - 1
            st.rerun()

    q = filtered_questions[st.session_state.current_q_index]
    
    st.markdown(f"""
    <div class="question-box">
        <div style="color:#666; font-size: 0.9em;">Câu {st.session_state.current_q_index + 1} / {total} - ({q.get('category','Chung')})</div>
        <div style="font-size: 1.15em; font-weight: 600; margin-top: 5px;">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # FIX ẢNH CÂU 1
    if q['id'] == 1: q['image'] = None

    if q.get('image'):
        img = load_image_strict(q['image'], folders_allowed=['images'])
        if img: st.image(img, width=500)

    st.write("---")
    
    # ĐÁP ÁN (DỌC) - Kết quả hiện ngay
    user_choice = st.radio("Chọn đáp án:", q['options'], index=None, key=f"q_{q['id']}")

    if user_choice:
        st.write("") 
        correct = q['correct_answer'].strip()
        if user_choice.strip() == correct:
            st.success(f"🎉 CHÍNH XÁC! Đáp án: {correct}")
        else:
            st.error(f"❌ SAI RỒI! Đáp án đúng là: {correct}")

# --- 7. MAIN APP ---
def main():
    with st.sidebar:
        st.title("🚗 MENU ÔN TẬP")
        st.divider()
        license = st.selectbox("Chọn hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license != st.session_state.license_type:
            st.session_state.license_type = license
            st.session_state.current_q_index = 0
            st.cache_data.clear()
            st.rerun()

        mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        st.divider()
        if st.button("🔄 Làm mới"):
            st.cache_data.clear()
            st.rerun()

    if mode == "📖 Học Mẹo":
        render_tips_page(st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
