import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Sửa Lỗi Auto",
    page_icon="🚗",
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

# --- 3. CSS GIAO DIỆN (FONT TO & FIX LAYOUT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
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

    /* ĐÁP ÁN - FONT CHỮ TO */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 20px !important;
        border-radius: 15px; width: 100%; cursor: pointer; margin-bottom: 10px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.5rem !important; font-weight: 600 !important;
    }

    /* NÚT ĐIỀU HƯỚNG */
    div[data-testid="stButton"] button {
        border-radius: 12px; font-weight: 800; height: 3.5rem; font-size: 1.2rem !important;
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
    # Loại bỏ phần mở rộng cũ nếu có để tránh trùng lặp
    clean_name = str(base_name).split('.')[0]
    for folder in folders:
        for ext in exts:
            path = os.path.join(folder, clean_name + ext)
            if os.path.exists(path):
                try: return ImageOps.exif_transpose(Image.open(path))
                except: continue
    return None

# --- 5. TRANG CHỦ ---
def render_home_page():
    st.markdown('<div class="hero-card"><h1>🚗 GPLX MASTER PRO</h1><p>Học nhanh một chạm - Tự động chuyển câu</p></div>', unsafe_allow_html=True)
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

# --- 6. TRANG MẸO CẤP TỐC ---
def render_captoc_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    tab1, tab2, tab3 = st.tabs(["🔢 Con số", "🏎️ Tốc độ", "🚔 Sa hình"])
    with tab1:
        st.info("💡 Mẹo tuổi: Chọn số LỚN NHẤT trong các lựa chọn.")
        img = load_image_smart("tip_tuoi", ["images"])
        if img: st.image(img)

# --- 7. TRANG MẸO CHI TIẾT ---
def render_tips_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    data = load_data_by_license(st.session_state.license_type)
    if not data: st.warning("Không có dữ liệu."); return
    for tip in data:
        st.markdown(f'<div class="detail-card"><div class="detail-title">📌 {tip.get("title", "Mẹo")}</div>', unsafe_allow_html=True)
        for line in tip.get('content', []):
            st.markdown(f'<div class="detail-line">• {line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

# --- 8. TRANG LUYỆN THI (FIX LỖI AUTO & ẢNH) ---
def render_exam_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Lỗi dữ liệu!"); return
    total = len(all_qs)

    # ĐIỀU HƯỚNG
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("⬅️ Trước", key="p_top"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with c2:
        new_idx = st.number_input("Câu số:", 1, total, st.session_state.current_q_index + 1)
        if new_idx - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_idx - 1; st.rerun()
    with c3:
        if st.button("Tiếp ➡️", key="n_top"):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

    # CÀI ĐẶT
    auto_mode = st.toggle("🚀 CHẾ ĐỘ AUTO", key="auto_mode")
    delay = st.slider("Giây chờ:", 1, 5, 2)

    # CÂU HỎI
    q = all_qs[st.session_state.current_q_index]
    st.markdown(f"### Câu {st.session_state.current_q_index + 1}:")
    st.info(f"**{q['question']}**")
    
    # ẢNH (Dùng hàm smart để không bị dính ảnh cũ)
    img_data = load_image_smart(q.get('image'), ["images", "images_a1"])
    if img_data:
        st.image(img_data)

    # ĐÁP ÁN
    correct_ans = q['correct_answer'].strip()
    options = q['options']
    correct_idx = -1
    for i, opt in enumerate(options):
        if opt.strip() == correct_ans:
            correct_idx = i
            break

    # Nếu bật Auto, hệ thống tự chọn câu đúng
    user_choice = st.radio(
        "Lựa chọn:", 
        options, 
        index=correct_idx if auto_mode else None, 
        key=f"radio_{st.session_state.current_q_index}"
    )

    if user_choice:
        if user_choice.strip() == correct_ans:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #16a34a !important; border: 4px solid #14532d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.success("ĐÚNG!")
        else:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dc2626 !important; border: 4px solid #7f1d1d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"SAI! Đáp án là: {correct_ans}")

        # LOGIC CHUYỂN CÂU TỰ ĐỘNG
        if auto_mode:
            placeholder = st.empty()
            for i in range(delay, 0, -1):
                placeholder.write(f"Sẽ chuyển sang câu tiếp theo sau {i} giây...")
                time.sleep(1)
            
            if st.session_state.current_q_index < total - 1:
                st.session_state.current_q_index += 1
                st.rerun()
            else:
                st.balloons()
                st.success("Đã hoàn thành bộ câu hỏi!")

# --- MAIN ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "tips": render_tips_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
