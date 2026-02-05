import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Cấp Tốc & Thông Minh",
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

# --- 3. CSS CẢI TIẾN (SỬA LỖI LÚ TRANG CHỦ & FONT TO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* FIX LỖI LÚ TRÊN: Tăng padding-top để nội dung không bị đè */
    .block-container { 
        padding-top: 4rem !important; 
        padding-bottom: 6rem !important; 
        max-width: 1000px;
    }

    /* CARD TRANG CHỦ */
    .hero-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 30px; border-radius: 25px; color: white; text-align: center; margin-bottom: 30px;
    }
    
    /* KHU VỰC PHÂN LOẠI XE MÁY / Ô TÔ */
    .section-title {
        font-size: 1.8rem; font-weight: 800; color: #1e293b;
        margin: 20px 0 10px 0; padding-bottom: 5px; border-bottom: 4px solid #3b82f6;
        display: inline-block;
    }
    
    /* THẺ MẸO CHI TIẾT (MẸO CŨ) - FONT SIÊU TO */
    .detail-card {
        background: white; border-radius: 20px; padding: 25px; margin-bottom: 20px; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); border-top: 10px solid #3b82f6;
    }
    .detail-title { font-size: 1.8rem !important; font-weight: 800 !important; color: #0f172a; margin-bottom: 15px; }
    .detail-line { font-size: 1.5rem !important; line-height: 1.6; color: #334155; margin-bottom: 10px; }

    /* RADIO BUTTONS (LUYỆN THI) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 20px !important;
        border-radius: 15px; width: 100%; cursor: pointer;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.5rem !important; font-weight: 600 !important;
    }

    /* NÚT BẤM TO RÕ */
    div[data-testid="stButton"] button {
        border-radius: 15px; font-weight: 800; height: 4.5rem; font-size: 1.3rem !important;
        transition: all 0.3s ease;
    }
    div[data-testid="stButton"] button:hover { transform: scale(1.02); }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ ---
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

# --- 5. TRANG CHỦ (TỐI ƯU MỘT CHẠM - VÀO LUÔN) ---
def render_home_page():
    st.markdown('<div class="hero-card"><h1>🚗 GPLX MASTER PRO</h1><p>Học nhanh - Thi dễ - Đậu ngay</p></div>', unsafe_allow_html=True)
    
    # Chia làm 2 cột lớn để người dùng "lựa chọn rồi vô luôn"
    col_xm, col_ot = st.columns(2)

    with col_xm:
        st.markdown('<div class="section-title">🛵 XE MÁY (A1, A2)</div>', unsafe_allow_html=True)
        # Nút 1: Mẹo Cấp Tốc
        if st.button("🚀 Mẹo Cấp Tốc Xe Máy", use_container_width=True, key="xm_captoc"):
            st.session_state.license_type = "Xe máy (A1, A2)"
            st.session_state.page = "captoc"; st.rerun()
        # Nút 2: Mẹo Chi Tiết
        if st.button("📖 Mẹo Chi Tiết Xe Máy", use_container_width=True, key="xm_tips"):
            st.session_state.license_type = "Xe máy (A1, A2)"
            st.session_state.page = "tips"; st.rerun()
        # Nút 3: Luyện Thi
        if st.button("📝 Luyện Thi 600 Câu Xe Máy", use_container_width=True, key="xm_exam"):
            st.session_state.license_type = "Xe máy (A1, A2)"
            st.session_state.page = "exam"; st.rerun()

    with col_ot:
        st.markdown('<div class="section-title">🚗 Ô TÔ (B1, B2, C)</div>', unsafe_allow_html=True)
        # Nút 1: Mẹo Cấp Tốc
        if st.button("🚀 Mẹo Cấp Tốc Ô Tô", use_container_width=True, key="ot_captoc"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"
            st.session_state.page = "captoc"; st.rerun()
        # Nút 2: Mẹo Chi Tiết
        if st.button("📖 Mẹo Chi Tiết Ô Tô", use_container_width=True, key="ot_tips"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"
            st.session_state.page = "tips"; st.rerun()
        # Nút 3: Luyện Thi
        if st.button("📝 Luyện Thi 600 Câu Ô Tô", use_container_width=True, key="ot_exam"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"
            st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC ---
def render_captoc_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    
    tab1, tab2, tab3 = st.tabs(["🔢 Con số & Độ tuổi", "🏎️ Tốc độ & K/cách", "🚔 Sa hình"])
    with tab1:
        st.info("💡 Mẹo tuổi: Chọn số LỚN NHẤT trong 3 đáp án đầu.")
        img = load_image_smart("tip_tuoi", ["images"])
        if img: st.image(img)
    with tab2:
        st.info("💡 Tốc độ: Trong dân cư -> Có giải phân cách (Đường đôi) chọn 60, không có chọn 50.")
    with tab3:
        st.info("💡 CSGT: Giơ tay chọn ý 3.")

# --- 7. TRANG MẸO CHI TIẾT (MẸO CŨ - CẢI TIẾN FONT/MÀU) ---
def render_tips_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.markdown(f"## 📖 Mẹo Chi Tiết: {st.session_state.license_type}")
    
    data = load_data_by_license(st.session_state.license_type)
    if not data: st.warning("Chưa có dữ liệu mẹo."); return
    
    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Chủ đề:", ["Tất cả"] + cats)
    
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    
    for tip in items:
        st.markdown(f"""
        <div class="detail-card">
            <div class="detail-title">📌 {tip.get('title', 'Mẹo')}</div>
        """, unsafe_allow_html=True)
        for line in tip.get('content', []):
            st.markdown(f'<div class="detail-line">• {line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        if tip.get('image'):
            img = load_image_smart(tip['image'], ["images", "images_a1"])
            if img: st.image(img, use_container_width=True)

# --- 8. TRANG LUYỆN THI (AUTO CHẠY LUÔN) ---
def render_exam_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Thiếu dữ liệu!"); return

    auto_next = st.toggle("🚀 CHẾ ĐỘ AUTO (Tự động chọn đúng & chuyển câu)", key="auto_mode")
    delay = st.slider("Giây chuyển câu", 1, 5, 2)

    q = all_qs[st.session_state.current_q_index]
    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {len(all_qs)}")
    st.info(f"**{q['question']}**")
    
    if q.get('image'):
        img = load_image_smart(q['image'], ["images"])
        if img: st.image(img)

    correct_ans = q['correct_answer'].strip()
    correct_idx = [i for i, opt in enumerate(q['options']) if opt.strip() == correct_ans][0]

    user_choice = st.radio("Chọn đáp án:", q['options'], index=correct_idx if auto_next else None, key=f"r_{st.session_state.current_q_index}")

    if user_choice:
        if user_choice.strip() == correct_ans:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #16a34a !important; border: 4px solid #14532d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.success("ĐÚNG!")
        else:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dc2626 !important; border: 4px solid #7f1d1d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"SAI! Đáp án là: {correct_ans}")

        if auto_next:
            time.sleep(delay)
            st.session_state.current_q_index = min(len(all_qs)-1, st.session_state.current_q_index + 1)
            st.rerun()

# --- MAIN ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "tips": render_tips_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
