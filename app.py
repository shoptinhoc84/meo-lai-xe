import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX - 600 Câu",
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

# --- 3. CSS GIAO DIỆN (ĐÃ FIX LỖI LỆCH HÀNG) ---
st.markdown("""
<style>
    /* Tổng thể */
    .main { background-color: #f5f7f9; }
    
    /* Thẻ Mẹo */
    .tip-card {
        background-color: #ffffff; border-radius: 12px; padding: 25px;
        margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #eef2f6;
    }
    
    /* Box Câu Hỏi */
    .question-box {
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 25px;
        border-left: 8px solid #007bff; 
        margin-bottom: 25px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }
    .question-text {
        font-size: 1.2rem;
        font-weight: 600;
        color: #1e293b;
        line-height: 1.5;
    }
    
    /* Highlight cho mẹo */
    .highlight { 
        background-color: #fee2e2; 
        color: #dc2626; 
        font-weight: bold; 
        padding: 2px 8px; 
        border-radius: 4px; 
    }

    /* CSS FIX CHO RADIO BUTTONS (ĐÁP ÁN) */
    div[data-testid="stRadio"] > label {
        display: none; /* Ẩn cái label "Answers" mặc định */
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] {
        gap: 12px; /* Khoảng cách giữa các đáp án */
    }

    /* Tạo style cho từng dòng đáp án */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: white;
        border: 1px solid #e2e8f0;
        padding: 15px 20px;
        border-radius: 10px;
        width: 100%;
        transition: all 0.2s ease;
        cursor: pointer;
        display: flex;
        align-items: center;
    }

    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #3b82f6;
        background-color: #f8fafc;
    }

    /* Khi được chọn */
    div[data-testid="stRadio"] div[role="radiogroup"] [data-checked="true"] {
        background-color: #eff6ff !important;
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 1px #3b82f6;
    }

    /* Ảnh minh họa */
    .img-container {
        display: flex;
        justify-content: center;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU & ẢNH ---
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

def load_image_smart(image_name, folder_priority=[]):
    if not image_name: return None
    for folder in folder_priority:
        path = os.path.join(folder, image_name)
        if os.path.exists(path):
            try:
                img = Image.open(path)
                return ImageOps.exif_transpose(img)
            except: continue
    return None

# --- 5. GIAO DIỆN: HỌC MẸO ---
def render_tips_page(data, is_oto):
    st.subheader(f"📖 Mẹo Thi Lý Thuyết {'Ô Tô' if is_oto else 'Xe Máy'}")
    
    if not data:
        st.warning("Không tìm thấy dữ liệu mẹo.")
        return

    categories = sorted(list(set([item.get('category', 'Khác') for item in data])))
    selected_cat = st.selectbox("Lọc theo danh mục:", ["Tất cả"] + categories)
    filtered_data = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    for tip in filtered_data:
        with st.container():
            st.markdown(f"""<div class="tip-card"><h4>💡 {tip.get('title', 'Mẹo')}</h4>""", unsafe_allow_html=True)
            c1, c2 = st.columns([1.2, 1])
            with c1:
                for line in tip.get('content', []):
                    if "=>" in line:
                        parts = line.split("=>")
                        line = f"{parts[0]} <span class='highlight'>➔ {parts[1]}</span>"
                    st.markdown(f"• {line}", unsafe_allow_html=True)
            with c2:
                if tip.get('image'):
                    folders = ["images", "images_a1"] if is_oto else ["images_a1", "images"]
                    img_obj = load_image_smart(tip['image'], folders)
                    if img_obj: st.image(img_obj, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

# --- 6. GIAO DIỆN: LUYỆN THI 600 CÂU ---
def render_exam_page():
    st.subheader("📝 Luyện Tập 600 Câu Hỏi")
    questions = load_600_questions()
    if not questions:
        st.error("Lỗi: Không tìm thấy file `dulieu_600_cau.json`.")
        return

    total_q = len(questions)
    
    # Thanh điều hướng
    nav_cols = st.columns([1, 1, 1, 1])
    with nav_cols[0]:
        if st.button("⬅️ Câu trước"):
            if st.session_state.current_q_index > 0:
                st.session_state.current_q_index -= 1
                st.session_state.show_answer = False
                st.rerun()
    with nav_cols[1]:
        if st.button("Câu tiếp ➡️"):
            if st.session_state.current_q_index < total_q - 1:
                st.session_state.current_q_index += 1
                st.session_state.show_answer = False
                st.rerun()
    with nav_cols[2]:
        new_idx = st.number_input("Nhảy tới câu:", 1, total_q, st.session_state.current_q_index + 1)
        if new_idx - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_idx - 1
            st.session_state.show_answer = False
            st.rerun()

    # Hiển thị câu hỏi
    q = questions[st.session_state.current_q_index]
    st.markdown(f"""
    <div class="question-box">
        <div style="color: #64748b; margin-bottom: 8px;">Câu {st.session_state.current_q_index + 1} / {total_q} - [{q.get('category', 'Chung')}]</div>
        <div class="question-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị ảnh (nếu có)
    if q.get('image'):
        img_obj = load_image_smart(q['image'], ["images", "images_a1"])
        if img_obj:
            st.image(img_obj, width=500)

    # Đáp án
    user_choice = st.radio(
        "Chọn đáp án:", 
        q['options'], 
        index=None, 
        key=f"q_{st.session_state.current_q_index}",
        label_visibility="collapsed"
    )

    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("Kiểm tra", type="primary", use_container_width=True):
            st.session_state.show_answer = True

    if st.session_state.show_answer:
        st.markdown("---")
        correct = q['correct_answer'].strip()
        if user_choice:
            if user_choice.strip() == correct:
                st.success(f"✅ CHÍNH XÁC: {correct}")
            else:
                st.error(f"❌ SAI RỒI! Đáp án đúng là: **{correct}**")
        else:
            st.info(f"💡 Đáp án đúng là: **{correct}**")

# --- 7. MAIN APP ---
def main():
    with st.sidebar:
        st.title("🚗 GPLX PRO")
        st.divider()
        
        old_license = st.session_state.license_type
        current_license = st.selectbox("Chọn hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        
        if current_license != old_license:
            st.session_state.license_type = current_license
            st.session_state.current_q_index = 0
            st.cache_data.clear()
            st.rerun()

        mode = st.radio("Chế độ học:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        st.divider()
        st.caption("Phiên bản 5.2 - Đã sửa lỗi layout")

    if mode == "📖 Học Mẹo":
        data = load_tips_data(st.session_state.license_type)
        render_tips_page(data, "Ô tô" in st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
