import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - V26 Big Font",
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

# --- 3. HÀM MÀU SẮC (GIỮ NGUYÊN TÍNH NĂNG CHAMELEON) ---
def get_category_color(category):
    colors = {
        "Tất cả": "#f1f5f9",
        "Khái niệm và quy tắc": "#dbeafe", 
        "Văn hóa, đạo đức nghề nghiệp": "#fce7f3",
        "Kỹ thuật lái xe": "#dcfce7",
        "Cấu tạo và sửa chữa": "#ffedd5",
        "Biển báo đường bộ": "#fee2e2",
        "Sa hình": "#fff7ed",
        "Nghiệp vụ vận tải": "#ede9fe"
    }
    return colors.get(category, "#f1f5f9")

def get_category_border(category):
    borders = {
        "Tất cả": "#cbd5e1",
        "Khái niệm và quy tắc": "#2563eb",
        "Văn hóa, đạo đức nghề nghiệp": "#db2777",
        "Kỹ thuật lái xe": "#16a34a",
        "Cấu tạo và sửa chữa": "#ea580c",
        "Biển báo đường bộ": "#dc2626",
        "Sa hình": "#ca8a04",
        "Nghiệp vụ vận tải": "#7c3aed"
    }
    return borders.get(category, "#94a3b8")

# --- 4. CSS TỐI ƯU (FONT TO RÕ) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    .block-container {
        padding-top: 0.5rem !important;
        padding-bottom: 6rem !important;
    }

    /* --- THANH ĐIỀU HƯỚNG TRÊN --- */
    .top-nav-container {
        background: white; padding: 10px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 15px;
        border: 1px solid #e2e8f0;
    }

    /* --- CÂU HỎI (FONT CỰC TO) --- */
    .content-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9; margin-bottom: 20px;
    }
    .q-text { 
        font-size: 1.5rem !important; /* ~24px: Cực rõ */
        font-weight: 700 !important; 
        color: #0f172a !important; 
        line-height: 1.5 !important; 
        margin-top: 10px !important;
    }

    /* --- ĐÁP ÁN (FONT TO & DỄ BẤM) --- */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 15px; display: flex; flex-direction: column; }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; 
        border: 2px solid #e2e8f0; 
        padding: 20px !important; /* Tăng vùng bấm */
        border-radius: 16px; 
        width: 100%; 
        cursor: pointer;
        display: flex; 
        align-items: center; 
        color: #334155; 
        
        /* CẤU HÌNH FONT CHỮ ĐÁP ÁN */
        font-size: 1.25rem !important; /* ~20px: To rõ */
        font-weight: 500 !important;
        line-height: 1.6 !important;
        transition: all 0.2s ease;
    }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.25rem !important; /* Ép cả thẻ p bên trong */
    }

    /* Hiệu ứng chọn */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #6366f1; background: #eef2ff;
        transform: translateY(-2px);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #4f46e5 !important; background: #eef2ff !important;
        color: #4338ca !important; font-weight: 700 !important;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2);
    }

    /* Tùy chỉnh Selectbox */
    div[data-testid="stSelectbox"] > div > div {
        border-radius: 12px !important;
        height: 50px !important; /* Cao hơn dễ bấm */
        display: flex; align-items: center;
    }
    div[data-testid="stSelectbox"] label {
        font-size: 1.2rem !important;
    }

    div[data-testid="stImage"] { display: flex; justify-content: center; margin: 15px 0; }
    div[data-testid="stImage"] img { border-radius: 12px; max-height: 400px; object-fit: contain; }
    div[data-testid="stButton"] button { width: 100%; border-radius: 12px; font-weight: 700; height: 3.5rem; font-size: 1.1rem !important; }
    
</style>
""", unsafe_allow_html=True)

# --- 5. HÀM XỬ LÝ DỮ LIỆU ---
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

# --- 6. GIAO DIỆN HỌC MẸO ---
def render_tips_page(license_type):
    st.markdown(f"### 📖 Mẹo: {license_type}")
    data = load_data_by_license(license_type)
    if not data:
        st.error("Thiếu dữ liệu mẹo.")
        return

    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    
    st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#64748b; margin-bottom:5px;">CHỌN CHỦ ĐỀ MẸO:</div>', unsafe_allow_html=True)
    selected_cat = st.selectbox("Mẹo:", ["Tất cả"] + cats, label_visibility="collapsed")
    
    # Màu động
    bg = get_category_color(selected_cat)
    border = get_category_border(selected_cat)
    
    # Inject CSS
    st.markdown(f"""<style>div[data-testid="stSelectbox"] > div > div {{ background-color: {bg} !important; border: 2px solid {border} !important; color: #1e293b !important; font-weight: 700 !important; }}</style>""", unsafe_allow_html=True)
    
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    st.write("---")
    for tip in items:
        st.markdown(f"""
        <div style="background:white; padding:25px; border-radius:16px; border-left:8px solid {border}; box-shadow:0 4px 10px rgba(0,0,0,0.05); margin-bottom:20px;">
            <div style="font-size:0.9rem; color:{border}; font-weight:800;">{tip.get('category', 'Mẹo')}</div>
            <div style="font-weight:800; font-size:1.3rem; margin-top:8px; line-height:1.4;">📌 {tip.get('title', 'Mẹo')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        for line in tip.get('content', []):
            line = line.replace("=>", "👉 <b>").replace("(", "<br><span style='color:#718096; font-size:1rem'>(")
            if "<b>" in line: line += "</b>"
            if "<span" in line: line += "</span>"
            st.markdown(f"<div style='font-size:1.15rem; margin-bottom:8px; line-height:1.6;'>• {line}</div>", unsafe_allow_html=True)
            
        if tip.get('image'):
            folders = ["images", "images_a1"] if "Ô tô" in license_type else ["images_a1", "images"]
            img = load_image_strict(tip['image'], folders)
            if img: st.image(img, use_container_width=True)
        st.write("---")

# --- 7. GIAO DIỆN LUYỆN THI (BIG FONT) ---
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
            st.markdown(f"<div style='text-align:center; font-weight:800; font-size:1.2rem; color:#334155; padding-top:10px;'>Câu {st.session_state.current_q_index + 1}/{total}</div>", unsafe_allow_html=True)
        with c3:
            if st.button("➡️", key="top_next", type="primary"):
                st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # 2. KHUNG CHỌN CHỦ ĐỀ (MÀU ĐỘNG)
    bg = get_category_color(current_cat)
    border = get_category_border(current_cat)
    
    st.markdown(f"""
    <style>
        div[data-testid="stSelectbox"] > div > div {{
            background-color: {bg} !important; border: 2px solid {border} !important;
            color: #0f172a !important; font-weight: 700 !important;
            box-shadow: 0 4px 6px -1px {bg} !important;
        }}
        div[data-testid="stSelectbox"] svg {{ fill: {border} !important; }}
    </style>
    """, unsafe_allow_html=True)

    st.markdown(f'<div style="font-size:0.9rem; font-weight:800; color:{border}; margin-bottom:5px; text-transform:uppercase;">📂 CHỌN CHỦ ĐỀ:</div>', unsafe_allow_html=True)
    
    idx = 0
    if current_cat == "Tất cả": idx = 0
    elif current_cat in cats: idx = cats.index(current_cat) + 1

    sel_cat = st.selectbox("Filter", ["Tất cả"] + cats, index=idx, label_visibility="collapsed")

    if sel_cat != st.session_state.exam_category:
        st.session_state.exam_category = sel_cat
        st.session_state.current_q_index = 0
        st.rerun()

    st.markdown('<div style="margin-bottom: 20px;"></div>', unsafe_allow_html=True)

    # 3. NỘI DUNG CÂU HỎI
    st.markdown(f"""
    <div class="content-card" style="border-left: 8px solid {border};">
        <div style="font-size:0.9rem; color:{border}; text-transform:uppercase; margin-bottom:5px; font-weight:700;">{q.get('category','Chung')}</div>
        <div class="q-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    if q['id'] == 1: q['image'] = None
    if q.get('image'):
        img = load_image_strict(q['image'], ['images'])
        if img: st.image(img, use_container_width=True)

    # 4. ĐÁP ÁN (FONT TO)
    user_choice = st.radio("Lựa chọn:", q['options'], index=None, key=f"q_{q['id']}")

    if user_choice:
        correct = q['correct_answer'].strip()
        if user_choice.strip() == correct:
            st.success(f"✅ CHÍNH XÁC: {correct}")
        else:
            st.error(f"❌ SAI: Đáp án là {correct}")

    # 5. THANH ĐIỀU HƯỚNG DƯỚI
    st.markdown("---")
    st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
    
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
        if st.button("🔄 Làm mới"):
            st.cache_data.clear()
            st.rerun()

    if mode == "📖 Học Mẹo":
        render_tips_page(st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
