import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - V33 Cheat Mode",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. KHỞI TẠO STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'exam_category' not in st.session_state:
    st.session_state.exam_category = "Tất cả"

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 6rem !important;
    }

    /* HERO & CARDS */
    .hero-card {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        padding: 30px; border-radius: 24px; color: white;
        text-align: center; margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(79, 70, 229, 0.4);
    }
    .hero-title { font-size: 2rem; font-weight: 800; margin-bottom: 10px; }
    .hero-subtitle { font-size: 1.1rem; opacity: 0.9; font-weight: 500; }

    .action-card {
        background: white; padding: 25px; border-radius: 20px;
        border: 1px solid #e2e8f0; text-align: center; cursor: pointer;
        transition: all 0.3s ease; height: 100%;
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .action-card:hover { transform: translateY(-5px); border-color: #6366f1; }
    .icon { font-size: 3rem; margin-bottom: 15px; }
    .card-title { font-size: 1.2rem; font-weight: 700; color: #1e293b; }
    .card-desc { font-size: 0.9rem; color: #64748b; }

    /* UI ELEMENTS */
    .top-nav-container {
        background: white; padding: 10px; border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); margin-bottom: 15px;
        border: 1px solid #e2e8f0;
    }
    .filter-area {
        background: white; padding: 15px; border-radius: 16px;
        border: 1px solid #e2e8f0; margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.02);
    }
    .content-card {
        background: white; padding: 25px; border-radius: 20px;
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.05);
        border: 1px solid #f1f5f9; margin-bottom: 20px;
    }
    .q-text { 
        font-size: 1.35rem !important; font-weight: 700 !important; 
        color: #0f172a !important; line-height: 1.5 !important; margin-top: 5px !important;
    }
    
    /* RADIO BUTTONS (ĐÁP ÁN) */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 16px; display: flex; flex-direction: column; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #e2e8f0; padding: 24px 20px !important;
        border-radius: 16px; width: 100%; cursor: pointer;
        display: flex; align-items: center; transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.6rem !important; font-weight: 600 !important;
        color: #334155 !important; line-height: 1.5 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #6366f1; background: #eef2ff; transform: translateY(-2px);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #4f46e5 !important; background: #eef2ff !important;
        box-shadow: 0 4px 10px rgba(79, 70, 229, 0.2);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p {
        color: #4338ca !important; font-weight: 800 !important;
    }

    div[data-testid="stButton"] button { width: 100%; border-radius: 12px; font-weight: 700; height: 3.5rem; font-size: 1.2rem !important; }
    div[data-testid="stImage"] { display: flex; justify-content: center; margin: 15px 0; }
    div[data-testid="stImage"] img { border-radius: 12px; max-height: 400px; object-fit: contain; }

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

def get_category_border(category):
    borders = {
        "Tất cả": "#cbd5e1", "Khái niệm và quy tắc": "#2563eb",
        "Văn hóa, đạo đức nghề nghiệp": "#db2777", "Kỹ thuật lái xe": "#16a34a",
        "Cấu tạo và sửa chữa": "#ea580c", "Biển báo đường bộ": "#dc2626",
        "Sa hình": "#ca8a04", "Nghiệp vụ vận tải": "#7c3aed"
    }
    return borders.get(category, "#94a3b8")

# --- 5. GIAO DIỆN TRANG CHỦ ---
def render_home_page():
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">🚗 GPLX MASTER PRO</div>
        <div class="hero-subtitle">Ôn thi lý thuyết lái xe hiệu quả</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("### 1. Chọn loại bằng")
    col_l1, col_l2 = st.columns(2)
    with col_l1:
        is_oto = "Ô tô" in st.session_state.license_type
        if st.button("🚗 Ô TÔ (B1, B2, C)", type="primary" if is_oto else "secondary", use_container_width=True): 
            st.session_state.license_type = "Ô tô (B1, B2, C...)"
            st.rerun()
    with col_l2:
        is_xm = "Xe máy" in st.session_state.license_type
        if st.button("🛵 XE MÁY (A1, A2)", type="primary" if is_xm else "secondary", use_container_width=True): 
            st.session_state.license_type = "Xe máy (A1, A2)"
            st.rerun()

    st.markdown("---")
    st.markdown(f"### 2. Bắt đầu học ({st.session_state.license_type})")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""
        <div class="action-card">
            <div class="icon">📝</div>
            <div class="card-title">Luyện Thi</div>
            <div class="card-desc">Chế độ thi thử & Học thuộc</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Vào Thi ➡️", key="btn_go_exam", use_container_width=True):
            st.session_state.page = "exam"
            st.rerun()
    with c2:
        st.markdown("""
        <div class="action-card">
            <div class="icon">💡</div>
            <div class="card-title">Học Mẹo</div>
            <div class="card-desc">Các mẹo ghi nhớ nhanh</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Xem Mẹo ➡️", key="btn_go_tips", use_container_width=True):
            st.session_state.page = "tips"
            st.rerun()

# --- 6. GIAO DIỆN HỌC MẸO ---
def render_tips_page():
    if st.button("🏠 Về Trang Chủ"):
        st.session_state.page = "home"
        st.rerun()
    license_type = st.session_state.license_type
    st.markdown(f"### 📖 Mẹo: {license_type}")
    data = load_data_by_license(license_type)
    if not data: return
    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#64748b; margin-bottom:5px;">CHỌN CHỦ ĐỀ:</div>', unsafe_allow_html=True)
    selected_cat = st.selectbox("Mẹo:", ["Tất cả"] + cats, label_visibility="collapsed")
    border = get_category_border(selected_cat)
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    st.write("---")
    for tip in items:
        st.markdown(f"""
        <div style="background:white; padding:25px; border-radius:16px; border-left:8px solid {border}; box-shadow:0 4px 10px rgba(0,0,0,0.05); margin-bottom:20px;">
            <div style="font-size:1rem; color:{border}; font-weight:800;">{tip.get('category', 'Mẹo')}</div>
            <div style="font-weight:800; font-size:1.4rem; margin-top:8px;">📌 {tip.get('title', 'Mẹo')}</div>
        </div>
        """, unsafe_allow_html=True)
        for line in tip.get('content', []):
            line = line.replace("=>", "👉 <b>").replace("(", "<br><span style='color:#718096; font-size:1.1rem'>(")
            if "<b>" in line: line += "</b>"
            st.markdown(f"<div style='font-size:1.25rem; margin-bottom:10px;'>• {line}</div>", unsafe_allow_html=True)
        if tip.get('image'):
            folders = ["images", "images_a1"] if "Ô tô" in license_type else ["images_a1", "images"]
            img = load_image_strict(tip['image'], folders)
            if img: st.image(img, use_container_width=True)
        st.write("---")

# --- 7. GIAO DIỆN LUYỆN THI (SHOW ANSWER + AUTO NEXT) ---
def render_exam_page():
    c_home, c_title = st.columns([1, 4])
    with c_home:
        if st.button("🏠 Home"):
            st.session_state.page = "home"
            st.rerun()
    with c_title:
        st.markdown(f"**Luyện thi: {st.session_state.license_type}**")

    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: return
    cats = sorted(list(set([q.get('category', 'Khác') for q in all_qs])))
    
    # FILTER AREA
    with st.container():
        st.markdown('<div class="filter-area">', unsafe_allow_html=True)
        # Chia cột: Search | Category | Auto Next | Show Answer
        c1, c2, c3, c4 = st.columns([1, 1, 0.6, 0.6])
        
        with c1:
            st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#64748b;">🔍 TÌM KIẾM:</div>', unsafe_allow_html=True)
            search_query = st.text_input("Search", placeholder="Từ khóa...", label_visibility="collapsed")
        with c2:
            st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#64748b;">📂 CHỦ ĐỀ:</div>', unsafe_allow_html=True)
            idx = 0
            if st.session_state.exam_category in cats: idx = cats.index(st.session_state.exam_category) + 1
            sel_cat = st.selectbox("Category", ["Tất cả"] + cats, index=idx, label_visibility="collapsed")
            if sel_cat != st.session_state.exam_category:
                st.session_state.exam_category = sel_cat
                st.session_state.current_q_index = 0
                st.rerun()
        
        # Nút chức năng nâng cao
        with c3:
            st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#64748b;">⚡ TỰ ĐỘNG:</div>', unsafe_allow_html=True)
            auto_next_mode = st.toggle("Auto Next", key="auto_next_toggle")
        
        with c4:
            st.markdown('<div style="font-size:0.8rem; font-weight:700; color:#64748b;">👀 HỌC THUỘC:</div>', unsafe_allow_html=True)
            show_answer_mode = st.toggle("Hiện đáp án", key="show_answer_toggle")

        st.markdown('</div>', unsafe_allow_html=True)

    # LOGIC LỌC
    if st.session_state.exam_category == "Tất cả": filtered = all_qs
    else: filtered = [q for q in all_qs if q.get('category') == st.session_state.exam_category]
    if search_query:
        filtered = [q for q in filtered if search_query.lower() in q['question'].lower()]

    total = len(filtered)
    if total == 0:
        st.warning("Không tìm thấy câu hỏi.")
        return

    if st.session_state.current_q_index >= total: st.session_state.current_q_index = 0
    q = filtered[st.session_state.current_q_index]
    border_color = get_category_border(q.get('category', 'Khác'))

    # NAV TOP
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

    # CONTENT
    st.markdown(f"""
    <div class="content-card" style="border-left: 8px solid {border_color};">
        <div style="font-size:0.9rem; color:{border_color}; text-transform:uppercase; margin-bottom:5px; font-weight:700;">{q.get('category','Chung')}</div>
        <div class="q-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    if q['id'] == 1: q['image'] = None
    if q.get('image'):
        img = load_image_strict(q['image'], ['images'])
        if img: st.image(img, use_container_width=True)

    # --- XỬ LÝ VIỆC CHỌN ĐÁP ÁN ---
    default_index = None
    
    # Nếu bật chế độ "Học thuộc" -> Tự tìm index của đáp án đúng
    if show_answer_mode:
        try:
            # Tìm vị trí của đáp án đúng trong danh sách options
            # Dùng strip() để xóa khoảng trắng thừa cho chắc chắn
            clean_ops = [opt.strip() for opt in q['options']]
            clean_correct = q['correct_answer'].strip()
            default_index = clean_ops.index(clean_correct)
        except:
            default_index = None

    # Render Radio Button
    user_choice = st.radio(
        "Lựa chọn:", 
        q['options'], 
        index=default_index,  # Tự động chọn nếu bật mode
        key=f"q_{q['id']}"
    )

    # Xử lý kết quả
    if user_choice:
        correct = q['correct_answer'].strip()
        if user_choice.strip() == correct:
            st.success(f"✅ CHÍNH XÁC: {correct}")
        else:
            st.error(f"❌ SAI: Đáp án là {correct}")

        # --- LOGIC AUTO NEXT ---
        # Nếu bật Auto Next VÀ (đang ở chế độ Học thuộc HOẶC người dùng tự bấm đúng)
        if auto_next_mode:
            if st.session_state.current_q_index < total - 1:
                time.sleep(1.0) # Chờ 1 giây cho dễ nhìn
                st.session_state.current_q_index += 1
                st.rerun()

    # NAV BOTTOM
    st.markdown("---")
    st.markdown('<div style="height:40px"></div>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("⬅️ Trước", key="bot_prev", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.rerun()
    with c3:
        if st.button("Tiếp theo ➡️", key="bot_next", type="primary", use_container_width=True):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.rerun()
    with c2:
         new_idx = st.number_input("Nhảy tới câu:", 1, total, st.session_state.current_q_index + 1, label_visibility="collapsed")
         if new_idx - 1 != st.session_state.current_q_index:
             st.session_state.current_q_index = new_idx - 1
             st.rerun()

# --- MAIN ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "tips": render_tips_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
