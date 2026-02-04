import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - V22 Mobile Fixed",
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

# --- 3. CSS TỐI ƯU (FIX LỖI DỌC & MẤT ĐÁP ÁN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f3f4f6; }
    
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 6rem !important;
    }

    /* ================================================================= */
    /* PHẦN 1: ÉP BUỘC THANH CHỦ ĐỀ NẰM NGANG (HORIZONTAL SCROLL)      */
    /* ================================================================= */
    
    /* Target vào Radio Group có thuộc tính horizontal */
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important; /* QUAN TRỌNG: Cấm xuống dòng */
        overflow-x: auto !important;  /* Cho phép cuộn ngang */
        width: 100% !important;
        gap: 8px !important;
        padding-bottom: 8px !important;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none; /* Ẩn thanh cuộn Firefox */
    }
    
    /* Ẩn thanh cuộn Chrome/Safari */
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"]::-webkit-scrollbar {
        display: none; 
    }

    /* Style cho từng nút bấm chủ đề */
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] label {
        flex: 0 0 auto !important; /* QUAN TRỌNG: Không co giãn */
        background-color: white !important;
        border: 1px solid #cbd5e1 !important;
        padding: 8px 16px !important;
        border-radius: 50px !important;
        white-space: nowrap !important; /* Chữ luôn thẳng hàng */
        font-weight: 600 !important;
        color: #64748b !important;
        font-size: 0.85rem !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02) !important;
        margin: 0 !important;
        min-width: 80px !important; /* Chiều rộng tối thiểu */
        text-align: center !important;
        justify-content: center !important;
    }

    /* Hiệu ứng khi chọn chủ đề (Active) */
    div[data-testid="stRadio"] div[role="radiogroup"][aria-orientation="horizontal"] label[data-checked="true"] {
        background-color: #2563eb !important;
        color: white !important;
        border-color: #2563eb !important;
        box-shadow: 0 4px 10px rgba(37, 99, 235, 0.3) !important;
    }

    /* ================================================================= */
    /* PHẦN 2: ĐÁP ÁN CÂU HỎI (VERTICAL - DỌC)                         */
    /* ================================================================= */
    
    /* Target vào Radio Group KHÔNG có thuộc tính horizontal */
    div[data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) {
        display: flex !important;
        flex-direction: column !important;
        gap: 12px !important;
        flex-wrap: wrap !important; /* Cho phép xuống dòng nội dung bên trong */
    }

    /* Style cho từng nút đáp án */
    div[data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) label {
        display: flex !important;
        width: 100% !important;
        background-color: white !important;
        border: 2px solid #e2e8f0 !important;
        padding: 16px !important;
        border-radius: 12px !important;
        align-items: center !important;
        white-space: normal !important; /* Cho phép text dài xuống dòng */
        height: auto !important;
        cursor: pointer !important;
    }
    
    /* Hiệu ứng chọn đáp án */
    div[data-testid="stRadio"] div[role="radiogroup"]:not([aria-orientation="horizontal"]) label[data-checked="true"] {
        border-color: #2563eb !important;
        background-color: #eff6ff !important;
        color: #1e40af !important;
        font-weight: 700 !important;
    }

    /* Ẩn tiêu đề mặc định của Radio để tự custom */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }

    /* ================================================================= */
    /* CÁC THÀNH PHẦN KHÁC */
    /* ================================================================= */
    .top-nav-container {
        background: white; padding: 10px; border-radius: 12px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-bottom: 10px;
        border: 1px solid #e5e7eb;
    }
    .filter-label {
        font-size: 0.75rem; font-weight: 800; color: #94a3b8; text-transform: uppercase; margin-bottom: 5px; letter-spacing: 0.5px;
    }
    .content-card {
        background: white; padding: 25px; border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.03);
        border: 1px solid #e2e8f0; margin-bottom: 15px;
    }
    .q-text { 
        font-size: 1.35rem; font-weight: 700; color: #1e293b; 
        line-height: 1.5; margin-top: 5px; 
    }
    div[data-testid="stImage"] { display: flex; justify-content: center; margin: 10px 0; }
    div[data-testid="stImage"] img { border-radius: 8px; max-height: 350px; object-fit: contain; }
    div[data-testid="stButton"] button { width: 100%; border-radius: 8px; font-weight: 600; height: 3rem; }

</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

def load_data_by_license(license_type):
    is_oto = "Ô tô" in license_type
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

# --- 5. GIAO DIỆN HỌC MẸO ---
def render_tips_page(license_type):
    st.markdown(f"### 📖 Mẹo: {license_type}")
    data = load_data_by_license(license_type)
    if not data:
        st.error("Thiếu dữ liệu mẹo.")
        return

    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    
    st.markdown('<div class="filter-label">👉 CHỌN CHỦ ĐỀ (VUỐT NGANG):</div>', unsafe_allow_html=True)
    selected_cat = st.radio("Chủ đề:", ["Tất cả"] + cats, horizontal=True, label_visibility="collapsed", key="tips_key")
    
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    st.write("---")
    for tip in items:
        st.markdown(f"""
        <div class="content-card" style="border-left: 5px solid #d63384;">
            <div style="font-size:0.85rem; color:#d63384; font-weight:700;">{tip.get('category', 'Mẹo')}</div>
            <div style="font-weight:700; font-size:1.1rem; margin-top:5px;">📌 {tip.get('title', 'Mẹo')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        for line in tip.get('content', []):
            line = line.replace("=>", "👉 <b>").replace("(", "<br><span style='color:#718096; font-size:0.9rem'>(")
            if "<b>" in line: line += "</b>"
            if "<span" in line: line += "</span>"
            st.markdown(f"• {line}", unsafe_allow_html=True)
            
        if tip.get('image'):
            folders = ["images", "images_a1"] if "Ô tô" in license_type else ["images_a1", "images"]
            img = load_image_strict(tip['image'], folders)
            if img: st.image(img, use_container_width=True)
        st.write("---")

# --- 6. GIAO DIỆN LUYỆN THI (V22) ---
def render_exam_page():
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: return

    cats = sorted(list(set([q.get('category', 'Khác') for q in all_qs])))
    
    current_cat = st.session_state.exam_category
    filtered = all_qs if current_cat == "Tất cả" else [q for q in all_qs if q.get('category') == current_cat]
    total = len(filtered)
    
    if st.session_state.current_q_index >= total: st.session_state.current_q_index = 0
    q = filtered[st.session_state.current_q_index]

    # 1. THANH ĐIỀU HƯỚNG TRÊN
    with st.container():
        st.markdown('<div class="top-nav-container">', unsafe_allow_html=True)
        c1, c2, c3 = st.columns([1, 2, 1])
        with c1:
            if st.button("⬅️", key="top_prev"):
                st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
                st.rerun()
        with c2:
            st.markdown(f"<div style='text-align:center; font-weight:800; padding-top:10px; font-size:1.1rem; color:#1e293b'>Câu {st.session_state.current_q_index + 1}/{total}</div>", unsafe_allow_html=True)
        with c3:
            if st.button("➡️", key="top_next", type="primary"):
                st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. KHUNG CHỌN CHỦ ĐỀ (PILLS SCROLL)
    st.markdown('<div class="filter-label">📂 CHỦ ĐỀ (VUỐT NGANG ↔️):</div>', unsafe_allow_html=True)
    
    sel_cat = st.radio(
        "Bộ lọc chủ đề", 
        ["Tất cả"] + cats, 
        horizontal=True, 
        label_visibility="collapsed",
        key="exam_cat_radio",
        index=0 if current_cat == "Tất cả" else (cats.index(current_cat) + 1 if current_cat in cats else 0)
    )

    if sel_cat != st.session_state.exam_category:
        st.session_state.exam_category = sel_cat
        st.session_state.current_q_index = 0
        st.rerun()

    st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)

    # 3. NỘI DUNG CÂU HỎI
    st.markdown(f"""
    <div class="content-card" style="border-left: 6px solid #2563eb;">
        <div style="font-size:0.8rem; color:#64748b; text-transform:uppercase; margin-bottom:5px;">{q.get('category','Chung')}</div>
        <div class="q-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    if q['id'] == 1: q['image'] = None
    if q.get('image'):
        img = load_image_strict(q['image'], ['images'])
        if img: st.image(img, use_container_width=True)

    # 4. ĐÁP ÁN (DỌC)
    user_choice = st.radio(
        "Lựa chọn:", 
        q['options'], 
        index=None, 
        key=f"q_radio_{q['id']}"
    )

    if user_choice:
        correct = q['correct_answer'].strip()
        if user_choice.strip() == correct:
            st.success(f"✅ CHÍNH XÁC: {correct}")
        else:
            st.error(f"❌ SAI: Đáp án là {correct}")

    # 5. THANH ĐIỀU HƯỚNG DƯỚI
    st.markdown("---")
    st.markdown('<div style="height:30px"></div>', unsafe_allow_html=True)
    
    col_b1, col_b2, col_b3 = st.columns([1, 1, 1])
    with col_b1:
        if st.button("⬅️ Trước", key="bot_prev", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.rerun()
    with col_b3:
        if st.button("Tiếp theo ➡️", key="bot_next", type="primary", use_container_width=True):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.rerun()
    with col_b2:
         new_idx = st.number_input("Nhảy tới câu:", 1, total, st.session_state.current_q_index + 1, label_visibility="collapsed")
         if new_idx - 1 != st.session_state.current_q_index:
             st.session_state.current_q_index = new_idx - 1
             st.rerun()

# --- MAIN ---
def main():
    with st.sidebar:
        st.header("Cài Đặt")
        lc = st.selectbox("Hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if lc != st.session_state.license_type:
            st.session_state.license_type = lc
            st.session_state.current_q_index = 0
            st.cache_data.clear()
            st.rerun()
        
        mode = st.radio("Chế độ:", ["📝 Luyện Thi", "📖 Học Mẹo"])
        st.divider()
        if st.button("🔄 Xóa Cache CSS"):
            st.cache_data.clear()
            st.rerun()

    if mode == "📖 Học Mẹo":
        render_tips_page(st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
