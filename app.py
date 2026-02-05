import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Điều Hướng Thông Minh",
    page_icon="🛵",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. KHỞI TẠO STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Xe máy (A1, A2)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0

# --- 3. CSS CẢI TIẾN (SỬA LỖI GIAO DIỆN & FONT TO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* Tăng khoảng cách phía trên để không bị mất nội dung */
    .block-container { 
        padding-top: 4rem !important; 
        padding-bottom: 6rem !important; 
        max-width: 1100px;
    }

    /* CARD TRANG CHỦ */
    .hero-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 30px; border-radius: 25px; color: white; text-align: center; margin-bottom: 30px;
    }
    
    .section-title {
        font-size: 1.8rem; font-weight: 800; color: #1e293b;
        margin: 20px 0 10px 0; padding-bottom: 5px; border-bottom: 4px solid #3b82f6;
        display: inline-block;
    }
    
    /* MẸO CHI TIẾT - FONT SIÊU TO */
    .detail-card {
        background: white; border-radius: 20px; padding: 25px; margin-bottom: 20px; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-top: 10px solid #3b82f6;
    }
    .detail-title { font-size: 1.8rem !important; font-weight: 800 !important; color: #0f172a; margin-bottom: 15px; }
    .detail-line { font-size: 1.5rem !important; line-height: 1.6; color: #334155; margin-bottom: 10px; }

    /* RADIO BUTTONS (ĐÁP ÁN) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 20px !important;
        border-radius: 15px; width: 100%; cursor: pointer; margin-bottom: 5px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.5rem !important; font-weight: 600 !important;
    }

    /* NÚT BẤM ĐIỀU HƯỚNG */
    div[data-testid="stButton"] button {
        border-radius: 12px; font-weight: 800; height: 3.5rem; font-size: 1.2rem !important;
    }
    
    /* Thanh điều hướng câu hỏi */
    .nav-container {
        background: #f1f5f9; padding: 15px; border-radius: 15px; margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM HỖ TRỢ ---
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

def load_data_by_license(license_type):
    is_oto = "Ô tô" in license_type
    target = ['data.json', 'data (6).json'] if is_oto else ['tips_a1.json', 'tips_a1 (1).json']
    for f in target:
        d = load_json_file(f)
        if d: return d
    return []

def load_image_smart(base_name, folders):
    if not base_name: return None
    exts = ['', '.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    for folder in folders:
        for ext in exts:
            path = os.path.join(folder, str(base_name).strip() + ext)
            if os.path.exists(path):
                return ImageOps.exif_transpose(Image.open(path))
    return None

# --- 5. TRANG CHỦ (TỐI ƯU MỘT CHẠM) ---
def render_home_page():
    st.markdown('<div class="hero-card"><h1>🚗 GPLX MASTER PRO</h1><p>Bản cập nhật 2026 - Điều hướng một chạm</p></div>', unsafe_allow_html=True)
    
    col_xm, col_ot = st.columns(2)

    with col_xm:
        st.markdown('<div class="section-title">🛵 XE MÁY (A1, A2)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Xe Máy", use_container_width=True, key="xm_captoc"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Xe Máy", use_container_width=True, key="xm_tips"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Xe Máy", use_container_width=True, key="xm_exam"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "exam"; st.rerun()

    with col_ot:
        st.markdown('<div class="section-title">🚗 Ô TÔ (B1, B2, C)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Ô Tô", use_container_width=True, key="ot_captoc"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Ô Tô", use_container_width=True, key="ot_tips"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Ô Tô", use_container_width=True, key="ot_exam"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC (THEO WORD) ---
def render_captoc_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    tab1, tab2, tab3 = st.tabs(["🔢 Con số", "🏎️ Tốc độ", "🚔 Sa hình"])
    with tab1:
        st.info("💡 Mẹo tuổi: Nhìn 3 đáp án đầu và tìm số LỚN NHẤT.")
        img = load_image_smart("tip_tuoi", ["images"])
        if img: st.image(img)

# --- 7. TRANG MẸO CHI TIẾT (CẢI TIẾN) ---
def render_tips_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.markdown(f"## 📖 Mẹo Chi Tiết: {st.session_state.license_type}")
    data = load_data_by_license(st.session_state.license_type)
    if not data: st.warning("Chưa có dữ liệu mẹo."); return
    
    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Chủ đề:", ["Tất cả"] + cats)
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    
    for tip in items:
        st.markdown(f'<div class="detail-card"><div class="detail-title">📌 {tip.get("title", "Mẹo")}</div>', unsafe_allow_html=True)
        for line in tip.get('content', []):
            st.markdown(f'<div class="detail-line">• {line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if tip.get('image'):
            img = load_image_smart(tip['image'], ["images", "images_a1"])
            if img: st.image(img, use_container_width=True)

# --- 8. TRANG LUYỆN THI (FIX ĐIỀU HƯỚNG & AUTO) ---
def render_exam_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Thiếu dữ liệu!"); return
    total = len(all_qs)

    # THANH CÀI ĐẶT
    with st.expander("⚙️ Cài đặt & Tự động", expanded=True):
        c1, c2 = st.columns(2)
        with c1: auto_next = st.toggle("🚀 CHẾ ĐỘ AUTO (Tự chọn đúng & Chuyển câu)", key="auto_mode")
        with c2: delay = st.slider("Giây chờ chuyển câu", 1, 5, 2)

    # --- THANH ĐIỀU HƯỚNG TRÊN (NEW) ---
    st.markdown('<div class="nav-container">', unsafe_allow_html=True)
    n1, n2, n3 = st.columns([1, 1, 1])
    with n1:
        if st.button("⬅️ Câu trước", key="nav_top_prev", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with n2:
        new_q = st.number_input("Nhảy tới câu:", 1, total, st.session_state.current_q_index + 1, key="jump_top")
        if new_q - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_q - 1; st.rerun()
    with n3:
        if st.button("Tiếp theo ➡️", key="nav_top_next", use_container_width=True, type="primary"):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # NỘI DUNG CÂU HỎI
    q = all_qs[st.session_state.current_q_index]
    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    st.info(f"**{q['question']}**")
    
    if q.get('image'):
        img = load_image_smart(q['image'], ["images", "images_a1"])
        if img: st.image(img)

    correct_ans = q['correct_answer'].strip()
    options = q['options']
    correct_idx = [i for i, opt in enumerate(options) if opt.strip() == correct_ans][0]

    user_choice = st.radio("Lựa chọn:", options, index=correct_idx if auto_next else None, key=f"r_{st.session_state.current_q_index}")

    if user_choice:
        if user_choice.strip() == correct_ans:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #16a34a !important; border: 4px solid #14532d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.success("ĐÚNG!")
        else:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dc2626 !important; border: 4px solid #7f1d1d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"SAI! Đáp án là: {correct_ans}")

        if auto_next:
            prog = st.progress(0, text=f"Chuyển câu sau {delay}s...")
            for i in range(100):
                time.sleep(delay/100); prog.progress(i + 1)
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

    # --- THANH ĐIỀU HƯỚNG DƯỚI (DỰ PHÒNG) ---
    st.write("---")
    b1, b2 = st.columns(2)
    with b1:
        if st.button("⬅️ Trước", key="nav_bot_prev", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with b2:
        if st.button("Tiếp ➡️", key="nav_bot_next", use_container_width=True):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

# --- MAIN ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "tips": render_tips_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
