import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Font Chuẩn",
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

# --- 3. CSS UI/UX (FONT CHỮ TO & RÕ) ---
st.markdown("""
<style>
    /* NHÚNG FONT GOOGLE (Tùy chọn, nếu muốn đẹp hơn nữa) */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* TỔNG THỂ */
    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; /* Font hiện đại */
    }
    .stApp { background-color: #f4f6f8; }
    
    /* CARD CÂU HỎI (To và Rõ) */
    .content-card {
        background: white; 
        padding: 30px; /* Tăng padding */
        border-radius: 20px;
        box-shadow: 0 8px 30px rgba(0,0,0,0.08);
        border: 1px solid #e1e4e8; 
        margin-bottom: 25px;
    }
    
    /* CÂU HỎI: Chữ to, đậm, dễ đọc */
    .q-text { 
        font-size: 1.4rem; /* ~22px */
        font-weight: 700; 
        color: #1a202c; 
        line-height: 1.6; /* Giãn dòng thoáng */
        margin-top: 10px;
        letter-spacing: -0.01em;
    }
    
    /* BADGE (Số thứ tự câu) */
    .badge {
        background: #e0f2fe; color: #0284c7; 
        padding: 6px 14px;
        border-radius: 30px; 
        font-size: 0.95rem; 
        font-weight: 700;
        display: inline-block;
        border: 1px solid #bae6fd;
    }

    /* ĐÁP ÁN (Dạng thẻ bấm lớn) */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 15px; display: flex; flex-direction: column; }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; 
        border: 2px solid #e2e8f0; 
        padding: 18px 22px; /* Vùng bấm cực rộng */
        border-radius: 14px; 
        width: 100%; 
        cursor: pointer;
        display: flex; 
        align-items: center; 
        color: #475569;
        font-size: 1.15rem; /* ~18px (Chữ đáp án to) */
        font-weight: 500;
        line-height: 1.5;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    
    /* Hiệu ứng khi di chuột */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #3b82f6; 
        background: #eff6ff;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.15);
    }
    
    /* Khi được chọn (Active) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #2563eb !important; 
        background: #eff6ff !important;
        color: #1e40af !important; 
        font-weight: 700;
        box-shadow: 0 0 0 4px rgba(37, 99, 235, 0.2);
    }

    /* ẢNH MINH HỌA */
    div[data-testid="stImage"] {
        background: #fff; 
        padding: 12px; 
        border-radius: 16px; 
        border: 1px solid #f1f5f9;
        margin: 20px 0;
        display: flex; justify-content: center;
    }
    div[data-testid="stImage"] img {
        border-radius: 10px;
        max-width: 100%;
        height: auto;
    }

    /* THANH ĐIỀU HƯỚNG DƯỚI CÙNG */
    .sticky-nav {
        position: fixed; bottom: 0; left: 0; width: 100%;
        background: rgba(255, 255, 255, 0.95); 
        backdrop-filter: blur(10px);
        padding: 15px;
        border-top: 1px solid #e2e8f0;
        box-shadow: 0 -4px 20px rgba(0,0,0,0.06); 
        z-index: 9999;
    }
    .block-container { padding-bottom: 100px !important; }

    /* Nút bấm điều hướng */
    .btn-nav { font-size: 1.1rem; font-weight: 600; padding: 0.5rem 1rem; }
    
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
    st.markdown(f"### 📖 Mẹo Thi: {license_type}")
    data = load_data_by_license(license_type)
    
    if not data:
        st.error("⚠️ Không tìm thấy file dữ liệu mẹo.")
        return

    categories = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Chọn chủ đề mẹo:", ["Tất cả"] + categories)
    
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    for tip in items:
        st.markdown(f"""
        <div class="content-card" style="border-left: 6px solid #e83e8c;">
            <div class="badge" style="background:#fce7f3; color:#db2777; border-color:#fbcfe8;">{tip.get('category', 'Mẹo')}</div>
            <div class="q-text" style="font-size:1.2rem; margin-top:5px;">📌 {tip.get('title', 'Mẹo ghi nhớ')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        c1, c2 = st.columns([1.5, 1])
        with c1:
            for line in tip.get('content', []):
                line = line.replace("=>", "👉 <span style='color:#d63384; font-weight:800; background:#fff1f2; padding:2px 6px; border-radius:4px;'>")
                if "👉" in line: line += "</span>"
                st.markdown(f"<div style='font-size:1.1rem; line-height:1.6; margin-bottom:8px;'>• {line}</div>", unsafe_allow_html=True)
        with c2:
            if tip.get('image'):
                folders = ["images", "images_a1"] if "Ô tô" in license_type else ["images_a1", "images"]
                img = load_image_strict(tip['image'], folders)
                if img: st.image(img, use_container_width=True)

# --- 6. GIAO DIỆN LUYỆN THI (FONT TO) ---
def render_exam_page():
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: return

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
    <div class="content-card" style="border-left: 6px solid #2563eb;">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="badge">Câu {st.session_state.current_q_index + 1}/{total}</span>
            <span style="color:#64748b; font-weight:600; font-size:0.9rem;">{q.get('category','Chung')}</span>
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
    st.markdown('<div style="height:60px"></div>', unsafe_allow_html=True)
    
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
        st.markdown(f"<div style='text-align:center; padding-top:10px; color:#64748b; font-weight:600;'>Câu {st.session_state.current_q_index + 1}</div>", unsafe_allow_html=True)

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
        st.caption("Ver 11.0: Font Inter & Giao diện lớn")

    if mode == "📖 Học Mẹo":
        render_tips_page(st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
