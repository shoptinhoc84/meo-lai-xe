import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Master - Ôn Thi App",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. KHỞI TẠO STATE ---
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'exam_category' not in st.session_state:
    st.session_state.exam_category = "Tất cả"

# --- 3. CSS UI/UX (MOBILE FIRST) ---
st.markdown("""
<style>
    /* Tổng thể */
    .stApp { background-color: #f8f9fa; }
    
    /* Sticky Footer (Thanh điều hướng dính đáy) */
    .sticky-nav {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: white; padding: 10px;
        box-shadow: 0 -2px 10px rgba(0,0,0,0.1); z-index: 999;
    }
    .block-container { padding-bottom: 80px !important; }

    /* Card (Khung nội dung) */
    .content-card {
        background: white; padding: 20px; border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #edf2f7; margin-bottom: 20px;
    }
    
    /* Badges */
    .badge {
        background: #e3f2fd; color: #1565c0; padding: 4px 12px;
        border-radius: 20px; font-size: 0.85rem; font-weight: 700;
        display: inline-block; margin-bottom: 8px;
    }
    
    /* Text Styles */
    .q-text { font-size: 1.3rem; font-weight: 600; color: #2d3748; line-height: 1.5; }
    .tip-highlight { color: #d63384; font-weight: bold; background: #fff0f6; padding: 0 4px; border-radius: 4px; }

    /* Radio Button (Đáp án dạng thẻ bấm) */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 10px; display: flex; flex-direction: column; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #e2e8f0; padding: 15px;
        border-radius: 12px; width: 100%; cursor: pointer;
        display: flex; align-items: center; color: #4a5568;
        transition: all 0.2s;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #3182ce; background: #ebf8ff;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #3182ce !important; background: #ebf8ff !important;
        color: #2b6cb0 !important; font-weight: 600;
    }

    /* Ảnh */
    div[data-testid="stImage"] {
        display: flex; justify-content: center;
        background: #fff; padding: 10px; border-radius: 12px; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

@st.cache_data
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

def load_data_by_license(license_type):
    """Load dữ liệu mẹo dựa trên loại bằng"""
    is_oto = "Ô tô" in license_type
    # Danh sách tên file có thể có (bao gồm cả tên file gốc và tên file bạn up lên)
    files_oto = ['data.json', 'data (6).json']
    files_xm = ['tips_a1.json', 'tips_a1 (1).json']
    
    target = files_oto if is_oto else files_xm
    for f in target:
        d = load_json_file(f)
        if d: return d
    return []

def load_image_strict(image_name, folders_allowed):
    if not image_name: return None
    img_name = str(image_name).strip()
    for folder in folders_allowed:
        path = os.path.join(folder, img_name)
        if os.path.exists(path) and os.path.isfile(path):
            try: return ImageOps.exif_transpose(Image.open(path))
            except: continue
    return None

# --- 5. GIAO DIỆN HỌC MẸO (ĐÃ KHÔI PHỤC & NÂNG CẤP) ---
def render_tips_page(license_type):
    st.markdown(f"### 📖 Mẹo Thi: {license_type}")
    data = load_data_by_license(license_type)
    
    if not data:
        st.error("⚠️ Không tìm thấy file dữ liệu mẹo (data.json hoặc tips_a1.json).")
        return

    # Filter Chủ đề (Dạng ngang)
    categories = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Chọn chủ đề mẹo:", ["Tất cả"] + categories)
    
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    for tip in items:
        # Sử dụng Card giao diện mới
        st.markdown(f"""
        <div class="content-card" style="border-left: 5px solid #e83e8c;">
            <div class="badge">{tip.get('category', 'Mẹo')}</div>
            <h3 style="margin:0; color:#2d3748;">📌 {tip.get('title', 'Mẹo ghi nhớ')}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            for line in tip.get('content', []):
                # Highlight từ khóa
                line = line.replace("=>", "👉 <span class='tip-highlight'>")
                if "👉" in line: line += "</span>"
                st.markdown(f"• {line}", unsafe_allow_html=True)
        with c2:
            if tip.get('image'):
                # Mẹo thì tìm cả 2 folder cho chắc
                folders = ["images", "images_a1"] if "Ô tô" in license_type else ["images_a1", "images"]
                img = load_image_strict(tip['image'], folders)
                if img: st.image(img, use_container_width=True)

# --- 6. GIAO DIỆN LUYỆN THI (GIỮ NGUYÊN V9) ---
def render_exam_page():
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs:
        st.error("Lỗi dữ liệu 600 câu.")
        return

    # Filter
    cats = sorted(list(set([q.get('category', 'Khác') for q in all_qs])))
    
    c1, c2 = st.columns([2, 1])
    with c1: st.markdown("### 📝 Luyện Thi 600 Câu")
    with c2: sel_cat = st.selectbox("Lọc chủ đề:", ["Tất cả"] + cats, label_visibility="collapsed")

    if sel_cat != st.session_state.exam_category:
        st.session_state.exam_category = sel_cat
        st.session_state.current_q_index = 0
        st.rerun()

    filtered = all_qs if sel_cat == "Tất cả" else [q for q in all_qs if q.get('category') == sel_cat]
    total = len(filtered)
    
    if st.session_state.current_q_index >= total: st.session_state.current_q_index = 0
    q = filtered[st.session_state.current_q_index]

    # --- CARD CÂU HỎI ---
    st.markdown(f"""
    <div class="content-card" style="border-left: 5px solid #3182ce;">
        <div style="display:flex; justify-content:space-between;">
            <span class="badge">Câu {st.session_state.current_q_index + 1}/{total}</span>
            <span style="color:#718096; font-size:0.8rem;">{q.get('category','Chung')}</span>
        </div>
        <div class="q-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Ảnh (Fix câu 1)
    if q['id'] == 1: q['image'] = None
    if q.get('image'):
        img = load_image_strict(q['image'], ['images'])
        if img: st.image(img, use_container_width=True)

    # Đáp án
    user_choice = st.radio("Chọn:", q['options'], index=None, key=f"q_{q['id']}")

    if user_choice:
        correct = q['correct_answer'].strip()
        if user_choice.strip() == correct:
            st.success(f"✅ CHÍNH XÁC: {correct}")
        else:
            st.error(f"❌ SAI: Đáp án đúng là {correct}")

    # --- THANH ĐIỀU HƯỚNG ---
    st.markdown("---")
    st.markdown('<div style="height:50px"></div>', unsafe_allow_html=True)
    
    c_prev, c_txt, c_next = st.columns([1, 1, 1])
    with c_prev:
        if st.button("⬅️ Trước", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.rerun()
    with c_next:
        if st.button("Tiếp theo ➡️", type="primary", use_container_width=True):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.rerun()
    with c_txt:
        st.markdown(f"<div style='text-align:center; padding-top:10px; color:#888'>Câu {st.session_state.current_q_index + 1}</div>", unsafe_allow_html=True)

# --- MAIN ---
def main():
    with st.sidebar:
        st.header("⚙️ Cài Đặt")
        lc = st.selectbox("Hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if lc != st.session_state.license_type:
            st.session_state.license_type = lc
            st.session_state.current_q_index = 0
            st.cache_data.clear()
            st.rerun()
        
        mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi"])
        st.divider()
        st.info("Phiên bản V10: Full tính năng & Giao diện App")

    if mode == "📖 Học Mẹo":
        render_tips_page(st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
