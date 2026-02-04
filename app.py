import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG (MOBILE FIRST) ---
st.set_page_config(
    page_title="GPLX Pro - Mobile V12",
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

# --- 3. CSS TỐI ƯU UI/UX ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .stApp { background-color: #f0f2f5; }
    
    /* Tinh chỉnh khoảng cách trên cùng cho điện thoại */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 5rem !important;
    }

    /* CARD CÂU HỎI (To, Rõ, Đẹp) */
    .content-card {
        background: white; 
        padding: 25px; 
        border-radius: 16px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid #e1e4e8; 
        margin-bottom: 20px;
    }
    
    .q-text { 
        font-size: 1.35rem; /* Chữ to ~21px */
        font-weight: 700; 
        color: #1a202c; 
        line-height: 1.5; 
        margin-top: 8px;
    }
    
    .badge {
        background: #e0f2fe; color: #0284c7; 
        padding: 4px 12px; border-radius: 20px; 
        font-weight: 700; font-size: 0.9rem;
    }

    /* ĐÁP ÁN (Dạng thẻ bấm lớn) */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 12px; display: flex; flex-direction: column; }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; 
        border: 2px solid #e2e8f0; 
        padding: 16px; /* Vùng bấm lớn */
        border-radius: 12px; 
        width: 100%; 
        cursor: pointer;
        display: flex; align-items: center; 
        color: #475569;
        font-size: 1.1rem; /* Chữ đáp án to */
        font-weight: 500;
        transition: all 0.15s;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #3b82f6; background: #eff6ff;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #2563eb !important; background: #eff6ff !important;
        color: #1e40af !important; font-weight: 700;
    }

    /* ẢNH MINH HỌA */
    div[data-testid="stImage"] {
        display: flex; justify-content: center;
        margin: 15px 0; background: #fff; padding: 10px; border-radius: 12px;
    }
    div[data-testid="stImage"] img { border-radius: 8px; max-height: 350px; object-fit: contain; }

    /* NÚT BẤM TO */
    div[data-testid="stButton"] button { width: 100%; border-radius: 8px; height: 3rem; }
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
    selected_cat = st.selectbox("Chọn chủ đề:", ["Tất cả"] + cats)
    
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    for tip in items:
        st.markdown(f"""
        <div class="content-card" style="border-left: 5px solid #d63384;">
            <div style="font-size:0.9rem; color:#d63384; font-weight:700;">{tip.get('category', 'Mẹo')}</div>
            <div style="font-weight:700; font-size:1.2rem; margin-top:5px;">📌 {tip.get('title', 'Mẹo')}</div>
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

# --- 6. GIAO DIỆN LUYỆN THI (LAYOUT MỚI) ---
def render_exam_page():
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: return

    cats = sorted(list(set([q.get('category', 'Khác') for q in all_qs])))
    
    # 1. BỘ LỌC (Nằm trên cùng, tách biệt)
    sel_cat = st.selectbox("📂 Chọn chủ đề ôn tập:", ["Tất cả"] + cats, label_visibility="collapsed")

    if sel_cat != st.session_state.exam_category:
        st.session_state.exam_category = sel_cat
        st.session_state.current_q_index = 0
        st.rerun()

    filtered = all_qs if sel_cat == "Tất cả" else [q for q in all_qs if q.get('category') == sel_cat]
    total = len(filtered)
    
    if st.session_state.current_q_index >= total: st.session_state.current_q_index = 0
    q = filtered[st.session_state.current_q_index]

    st.markdown("---") # Kẻ ngang tách biệt

    # 2. THANH ĐIỀU HƯỚNG TRÊN CÙNG (GIẢI QUYẾT VẤN ĐỀ CỦA BẠN)
    # Nút bấm nằm ngay trên câu hỏi, không cần cuộn
    col_t1, col_t2, col_t3 = st.columns([1, 2, 1])
    with col_t1:
        if st.button("⬅️", key="top_prev"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.rerun()
    with col_t2:
        st.markdown(f"<div style='text-align:center; font-weight:bold; padding-top:10px; font-size:1.1rem'>Câu {st.session_state.current_q_index + 1}/{total}</div>", unsafe_allow_html=True)
    with col_t3:
        if st.button("➡️", key="top_next", type="primary"):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.rerun()

    # 3. NỘI DUNG CÂU HỎI
    st.markdown(f"""
    <div class="content-card" style="border-left: 6px solid #2563eb;">
        <div style="font-size:0.85rem; color:#64748b; text-transform:uppercase; margin-bottom:5px;">{q.get('category','Chung')}</div>
        <div class="q-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Ảnh (Fix câu 1)
    if q['id'] == 1: q['image'] = None
    if q.get('image'):
        img = load_image_strict(q['image'], ['images'])
        if img: st.image(img, use_container_width=True)

    # Đáp án
    user_choice = st.radio("Lựa chọn:", q['options'], index=None, key=f"q_{q['id']}")

    if user_choice:
        correct = q['correct_answer'].strip()
        if user_choice.strip() == correct:
            st.success(f"✅ CHÍNH XÁC: {correct}")
        else:
            st.error(f"❌ SAI: Đáp án là {correct}")

    # 4. THANH ĐIỀU HƯỚNG DƯỚI CÙNG (Dự phòng)
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
        st.info("V12: Có nút điều hướng trên đầu trang.")

    if mode == "📖 Học Mẹo":
        render_tips_page(st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
