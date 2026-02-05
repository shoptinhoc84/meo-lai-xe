import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Auto Color",
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

# --- 3. CSS TÔ MÀU & GIAO DIỆN ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 6rem !important;
    }

    /* CARD CHUNG */
    .hero-card {
        background: linear-gradient(135deg, #4f46e5 0%, #3b82f6 100%);
        padding: 30px; border-radius: 24px; color: white;
        text-align: center; margin-bottom: 30px;
    }
    .action-card {
        background: white; padding: 25px; border-radius: 20px;
        border: 1px solid #e2e8f0; text-align: center; cursor: pointer;
        transition: all 0.3s ease; height: 100%; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        display: flex; flex-direction: column; align-items: center; justify-content: center;
    }
    .action-card:hover { transform: translateY(-5px); border-color: #6366f1; box-shadow: 0 10px 15px -3px rgba(99, 102, 241, 0.2); }

    /* FILTER & NAV */
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

    /* --- STYLE CHO TRANG MẸO CẤP TỐC --- */
    .tip-box {
        background: white;
        border-radius: 16px;
        padding: 20px;
        margin-bottom: 15px;
        border-left: 6px solid #3b82f6;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .tip-title {
        color: #1e293b;
        font-weight: 800;
        font-size: 1.1rem;
        margin-bottom: 8px;
        text-transform: uppercase;
        display: flex; align-items: center; gap: 8px;
    }
    .tip-content {
        color: #334155;
        font-size: 1.05rem;
        line-height: 1.6;
    }
    .highlight-red { color: #dc2626; font-weight: 700; background: #fee2e2; padding: 2px 6px; border-radius: 6px; }
    .highlight-green { color: #16a34a; font-weight: 700; background: #dcfce7; padding: 2px 6px; border-radius: 6px; }
    .highlight-blue { color: #2563eb; font-weight: 700; }
    
    .formula-box {
        background: #f1f5f9;
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
        font-weight: 700;
        font-size: 1.2rem;
        color: #475569;
        margin: 10px 0;
    }

    /* --- RADIO BUTTONS (CƠ BẢN - MẶC ĐỊNH MÀU XANH DƯƠNG KHI MỚI BẤM) --- */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 16px; display: flex; flex-direction: column; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #e2e8f0; padding: 20px 20px !important;
        border-radius: 16px; width: 100%; cursor: pointer; display: flex; align-items: center; transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.5rem !important; font-weight: 500 !important; color: #64748b !important; line-height: 1.5 !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover { border-color: #3b82f6; background: #eff6ff; }
    
    /* Mặc định khi chọn (Chưa biết đúng sai - trạng thái chờ) -> Màu xanh dương */
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        background-color: #eff6ff !important; 
        border: 3px solid #3b82f6 !important; /* Blue border */
        box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p {
        color: #1e40af !important; font-weight: 800 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { height: 50px; border-radius: 10px; background-color: white; border: 1px solid #e2e8f0; }
    .stTabs [aria-selected="true"] { background-color: #eff6ff !important; border-color: #3b82f6 !important; color: #1d4ed8 !important; font-weight: 700; }
    
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

# --- HÀM LOAD ẢNH THÔNG MINH ---
def load_image_smart(base_name, folders_allowed):
    if not base_name: return None
    extensions = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.JPEG']
    clean_name = str(base_name).strip()
    if any(clean_name.endswith(ext) for ext in extensions):
         for folder in folders_allowed:
            path = os.path.join(folder, clean_name)
            if os.path.exists(path) and os.path.isfile(path):
                return ImageOps.exif_transpose(Image.open(path))
    for folder in folders_allowed:
        for ext in extensions:
            path = os.path.join(folder, clean_name + ext)
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
        <h2 style='margin:0'>🚗 GPLX MASTER PRO</h2>
        <p style='margin:0; opacity:0.9'>Ôn thi lý thuyết lái xe hiệu quả</p>
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
    st.markdown("### 2. Chế độ học")
    
    # Hàng 1
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("""<div class="action-card" style="border-left: 5px solid #4f46e5;"><h3>🚀 Mẹo Cấp Tốc</h3><p style='color:#64748b'>Tổng hợp bí kíp khoanh nhanh</p></div>""", unsafe_allow_html=True)
        if st.button("Học Mẹo Nhanh ⚡", key="btn_go_captoc", use_container_width=True):
            st.session_state.page = "captoc"
            st.rerun()
    with c2:
        st.markdown("""<div class="action-card"><h3>📝 Luyện Thi</h3><p style='color:#64748b'>600 câu trắc nghiệm</p></div>""", unsafe_allow_html=True)
        if st.button("Vào Thi ➡️", key="btn_go_exam", use_container_width=True):
            st.session_state.page = "exam"
            st.rerun()
            
    # Hàng 2
    st.markdown("<div style='height:15px'></div>", unsafe_allow_html=True)
    c3, c4 = st.columns(2)
    with c3:
        st.markdown("""<div class="action-card"><h3>💡 Mẹo Chi Tiết</h3><p style='color:#64748b'>Dữ liệu chi tiết từng phần</p></div>""", unsafe_allow_html=True)
        if st.button("Xem Mẹo Cũ 📂", key="btn_go_tips", use_container_width=True):
            st.session_state.page = "tips"
            st.rerun()
    with c4:
        pass 

# --- 6. GIAO DIỆN MẸO CẤP TỐC ---
def render_captoc_page():
    c_home, c_title = st.columns([1, 4])
    with c_home:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = "home"
            st.rerun()
    with c_title:
        st.markdown(f"## ⚡ Bí Kíp Cấp Tốc: {st.session_state.license_type}")
    
    st.info("💡 Mẹo: Hệ thống tự động hiển thị ảnh .jpg hoặc .png từ thư mục images.")
    folders = ["images", "images_a1"]

    # Tab phân loại
    tab1, tab2, tab3, tab4 = st.tabs(["🔢 Con Số & Tuổi", "🚀 Tốc Độ & K/Cách", "🆔 Hạng Xe (Ảnh)", "🛑 Biển Báo & Sa Hình"])

    # --- TAB 1: CON SỐ & TUỔI ---
    with tab1:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown("""
            <div class="tip-box">
                <div class="tip-title">🎂 Mẹo Độ Tuổi</div>
                <div class="tip-content">
                    Câu hỏi về độ tuổi lái xe:<br>
                    👉 <b>Nhìn 3 đáp án đầu, tìm số LỚN NHẤT.</b><br>
                    Ví dụ: 18, 21, 24 -> Chọn <b>24</b>.<br>
                    <div class="formula-box">Đáp án = Số Tuổi Lớn Nhất</div>
                    <small><i>(Ngoại lệ: Hạng E là 27 tuổi)</i></small>
                </div>
            </div>
            <div class="tip-box">
                <div class="tip-title">⏳ Niên hạn & Quy Định Khác</div>
                <div class="tip-content">
                    • <b>Niên hạn xe tải:</b> <span class="highlight-red">25 năm</span><br>
                    • <b>Niên hạn xe khách (>9 chỗ):</b> <span class="highlight-red">20 năm</span><br>
                    • <b>Cấm bóp còi:</b> Từ <span class="highlight-red">22h đêm - 5h sáng</span>.<br>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            img1 = load_image_smart("tip_tuoi", folders)
            if img1: st.image(img1, caption="Mẹo chọn tuổi lớn nhất", use_container_width=True)
            img2 = load_image_smart("tip_khoangcach", folders)
            if img2: st.image(img2, caption="Quy định đỗ xe & Niên hạn", use_container_width=True)

    # --- TAB 2: TỐC ĐỘ & KHOẢNG CÁCH ---
    with tab2:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown("""
            <div class="tip-box" style="border-left-color: #f59e0b;">
                <div class="tip-title">🏎️ Tốc độ trong khu dân cư</div>
                <div class="tip-content">
                    Xe mô tô, ô tô con chạy bao nhiêu?<br>
                    🛣️ <b>Đường ĐÔI</b> (Có dải phân cách giữa): <span class="highlight-blue">60 km/h</span><br>
                    Road <b>Đường HAI CHIỀU/MỘT CHIỀU</b> (Không có dải phân cách): <span class="highlight-blue">50 km/h</span><br>
                </div>
            </div>
            <div class="tip-box" style="border-left-color: #10b981;">
                <div class="tip-title">📏 Khoảng cách an toàn (Mẹo Trừ 30)</div>
                <div class="tip-content">
                    Khi đề bài hỏi khoảng cách an toàn với tốc độ (60-80, 80-100...):<br>
                    👉 <b>Lấy tốc độ LỚN NHẤT trừ đi 30</b> -> Ra đáp án gần đúng nhất.<br><br>
                    Ví dụ: Tốc độ <b>60-80 km/h</b>.<br>
                    Lấy <span class="highlight-red">80 - 30 = 50</span> ➡ Chọn đáp án <b>55m</b>.<br>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            img = load_image_smart("tip_tocdo", folders)
            if img: st.image(img, caption="Bảng tốc độ & Khoảng cách", use_container_width=True)

    # --- TAB 3: HẠNG XE ---
    with tab3:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown("""
            <div class="tip-box" style="border-left-color: #8b5cf6;">
                <div class="tip-title">🆔 Mẹo Hạng Giấy Phép (FE, FC)</div>
                <div class="tip-content">
                    Nếu câu hỏi về hạng <b>FE, FC</b>:<br>
                    👉 Hỏi <b>FE</b>: Chọn ý <b>1</b> (Em 1)<br>
                    👉 Hỏi <b>FC</b>: Chọn ý <b>2</b> (Chị 2)<br>
                    <div class="formula-box">FE ➡ 1 | FC ➡ 2</div>
                </div>
            </div>
            <div class="tip-box">
                <div class="tip-title">🛵 Mẹo Hạng A1</div>
                <div class="tip-content">
                    • <b>Được lái:</b> Xe 2 bánh đến 125cm3 (Luật mới).<br>
                    • <b>KHÔNG lái:</b> Xe ba bánh (trừ xe cho người khuyết tật).<br>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("**📸 Hình ảnh minh họa:**")
            img_chung = load_image_smart("tip_hang_chung", folders)
            if img_chung: st.image(img_chung, caption="Tổng hợp hạng xe", use_container_width=True)
            img_fc = load_image_smart("tip_hang_fc", folders)
            if img_fc:
                with st.expander("Xem hình FE - FC"):
                    st.image(img_fc, caption="Mẹo FE - FC", use_container_width=True)
            img_a1 = load_image_smart("tip_hang_a1", folders)
            if img_a1:
                with st.expander("Xem hình A1"):
                    st.image(img_a1, caption="Mẹo A1", use_container_width=True)
            if not any([img_chung, img_fc, img_a1]):
                st.warning("Chưa tìm thấy ảnh. Hãy đặt tên: tip_hang_chung, tip_hang_fc, tip_hang_a1")

    # --- TAB 4: BIỂN BÁO & SA HÌNH ---
    with tab4:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown("""
            <div class="tip-box" style="border-left-color: #ef4444;">
                <div class="tip-title">🛑 Logic Cấm & Sa Hình</div>
                <div class="tip-content">
                    <b>1. Biển Cấm:</b><br>
                    • Cấm NHỎ -> Cấm LỚN (Cấm xe con thì cấm luôn xe tải).<br>
                    • Cấm LỚN -> KHÔNG cấm NHỎ.<br>
                </div>
            </div>
            <div class="tip-box" style="border-left-color: #ec4899;">
                <div class="tip-title">👮 Mẹo Cảnh Sát Giao Thông</div>
                <div class="tip-content">
                    Thấy hình CSGT giơ tay (1 tay hoặc 2 tay):<br>
                    👉 <b>Chọn ngay đáp án 3.</b><br>
                    <i>(Mẹo: Cứ thấy chú Công an đứng giữa đường là chọn ý 3).</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            img = load_image_smart("tip_sahinh", folders)
            if img: st.image(img, caption="Sa hình & CSGT", use_container_width=True)

# --- 7. GIAO DIỆN HỌC MẸO CHI TIẾT ---
def render_tips_page():
    if st.button("🏠 Về Trang Chủ"):
        st.session_state.page = "home"
        st.rerun()
    st.markdown(f"### 📖 Mẹo Chi Tiết (Dữ liệu cũ): {st.session_state.license_type}")
    data = load_data_by_license(st.session_state.license_type)
    if not data: 
        st.warning("Chưa có dữ liệu mẹo cũ.")
        return
    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#64748b;">CHỌN CHỦ ĐỀ:</div>', unsafe_allow_html=True)
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
            folders = ["images", "images_a1"] if "Ô tô" in st.session_state.license_type else ["images_a1", "images"]
            img = load_image_smart(tip['image'], folders)
            if img: st.image(img, use_container_width=True)
        st.write("---")

# --- 8. GIAO DIỆN LUYỆN THI (ĐÃ SỬA CSS ĐỔI MÀU MẠNH HƠN) ---
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
        c1, c2, c3, c4 = st.columns([1, 1, 0.8, 0.8])
        with c1:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#64748b;">🔍 TÌM KIẾM:</div>', unsafe_allow_html=True)
            search_query = st.text_input("Search", placeholder="Từ khóa...", label_visibility="collapsed")
        with c2:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#64748b;">📂 CHỦ ĐỀ:</div>', unsafe_allow_html=True)
            idx = 0
            if st.session_state.exam_category in cats: idx = cats.index(st.session_state.exam_category) + 1
            sel_cat = st.selectbox("Category", ["Tất cả"] + cats, index=idx, label_visibility="collapsed")
            if sel_cat != st.session_state.exam_category:
                st.session_state.exam_category = sel_cat
                st.session_state.current_q_index = 0
                st.rerun()
        
        # SETTINGS
        with c3:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#64748b;">⚡ TỰ ĐỘNG:</div>', unsafe_allow_html=True)
            auto_next_mode = st.toggle("Tự qua câu", key="auto_next_toggle")
            delay_seconds = 3
            if auto_next_mode:
                delay_seconds = st.slider("Chờ (s):", 1, 10, 3, label_visibility="collapsed")
        
        with c4:
            st.markdown('<div style="font-size:0.9rem; font-weight:700; color:#64748b;">👀 HỌC THUỘC:</div>', unsafe_allow_html=True)
            show_answer_mode = st.toggle("Hiện đáp án", key="show_answer_toggle")

        st.markdown('</div>', unsafe_allow_html=True)

    # LOGIC FILTER
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

    # CONTENT CARD
    st.markdown(f"""
    <div class="content-card" style="border-left: 8px solid {border_color};">
        <div style="font-size:0.9rem; color:{border_color}; text-transform:uppercase; margin-bottom:5px; font-weight:700;">{q.get('category','Chung')}</div>
        <div class="q-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    if q['id'] == 1: q['image'] = None
    if q.get('image'):
        img = load_image_smart(q['image'], ['images'])
        if img: st.image(img, use_container_width=True)

    # CHỌN ĐÁP ÁN
    default_index = None
    if show_answer_mode:
        try:
            clean_ops = [opt.strip() for opt in q['options']]
            clean_correct = q['correct_answer'].strip()
            default_index = clean_ops.index(clean_correct)
        except: default_index = None

    user_choice = st.radio("Lựa chọn:", q['options'], index=default_index, key=f"q_{q['id']}")

    # --- XỬ LÝ KẾT QUẢ & ĐỔI MÀU (LOGIC MỚI - MẠNH HƠN) ---
    if user_choice:
        clean_user = user_choice.strip()
        clean_correct = q['correct_answer'].strip()
        
        # Nếu ĐÚNG: Ghi đè CSS thành Xanh (Green)
        if clean_user == clean_correct:
            if not show_answer_mode: st.success(f"✅ CHÍNH XÁC: {clean_correct}")
            st.markdown("""
            <style>
                div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
                    background-color: #d1fae5 !important;
                    border: 3px solid #059669 !important;
                    box-shadow: 0 4px 15px rgba(16, 185, 129, 0.4) !important;
                }
                div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p {
                    color: #064e3b !important;
                }
            </style>
            """, unsafe_allow_html=True)
            
        # Nếu SAI: Ghi đè CSS thành Đỏ (Red)
        else:
            if not show_answer_mode: st.error(f"❌ SAI: Đáp án đúng là {clean_correct}")
            st.markdown("""
            <style>
                div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
                    background-color: #fee2e2 !important;
                    border: 3px solid #ef4444 !important;
                    box-shadow: 0 4px 15px rgba(239, 68, 68, 0.4) !important;
                }
                div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p {
                    color: #991b1b !important;
                }
            </style>
            """, unsafe_allow_html=True)

        if auto_next_mode:
            if st.session_state.current_q_index < total - 1:
                time.sleep(delay_seconds)
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
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
