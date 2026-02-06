import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Siêu Cấp Tốc 2026",
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

# --- 3. CSS TỔNG THỂ (FONT TO, MÀU ĐẬM, FIX LAYOUT) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* FIX LỖI CHE TIÊU ĐỀ */
    .block-container { 
        padding-top: 5rem !important; 
        padding-bottom: 6rem !important; 
        max-width: 1100px;
    }

    /* CARD TRANG CHỦ */
    .hero-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px; border-radius: 30px; color: white; text-align: center; margin-bottom: 30px;
    }
    .section-title {
        font-size: 2rem; font-weight: 800; color: #1e293b;
        margin: 20px 0 15px 0; padding-bottom: 5px; border-bottom: 5px solid #3b82f6; display: inline-block;
    }

    /* --- STYLE MẸO CẤP TỐC --- */
    .tip-box {
        background: white; border-radius: 18px; padding: 22px; margin-bottom: 20px;
        border-left: 10px solid #3b82f6; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
    }
    .tip-title { color: #1e293b; font-weight: 800; font-size: 1.4rem; margin-bottom: 10px; text-transform: uppercase; }
    .tip-content { color: #334155; font-size: 1.3rem; line-height: 1.6; font-weight: 500; }
    .highlight-red { color: #e11d48; font-weight: 800; background: #fff1f2; padding: 2px 6px; border-radius: 6px; }
    .highlight-blue { color: #2563eb; font-weight: 800; background: #eff6ff; padding: 2px 6px; border-radius: 6px; }
    .formula-box {
        background: #f8fafc; border: 2px dashed #94a3b8; border-radius: 12px;
        padding: 15px; text-align: center; font-weight: 800; font-size: 1.5rem; color: #1e293b; margin: 10px 0;
    }

    /* RADIO BUTTONS (ĐÁP ÁN) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 25px !important;
        border-radius: 18px; width: 100%; cursor: pointer; margin-bottom: 10px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.6rem !important; font-weight: 600 !important; color: #1e293b;
    }

    /* NÚT BẤM */
    div[data-testid="stButton"] button {
        border-radius: 15px; font-weight: 800; height: 4.2rem; font-size: 1.3rem !important; transition: all 0.3s ease;
    }
    div[data-testid="stButton"] button:hover { transform: scale(1.02); }
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
    if not base_name or str(base_name).strip() == "": return None
    exts = ['', '.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    clean_name = str(base_name).strip()
    for folder in folders:
        for ext in exts:
            path = os.path.join(folder, clean_name + ext)
            if os.path.exists(path):
                try: return ImageOps.exif_transpose(Image.open(path))
                except: continue
    return None

# --- 5. TRANG CHỦ (TỐI ƯU MỘT CHẠM) ---
def render_home_page():
    st.markdown('<div class="hero-card"><h1>🚗 GPLX MASTER PRO</h1><p style="font-size:1.3rem">Học nhanh - Thi dễ - Đậu ngay trong 1 lần thi</p></div>', unsafe_allow_html=True)
    col_xm, col_ot = st.columns(2)

    with col_xm:
        st.markdown('<div class="section-title">🛵 XE MÁY (A1, A2)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Xe Máy", use_container_width=True, key="btn_xm_captoc"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Xe Máy", use_container_width=True, key="btn_xm_tips"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Xe Máy", use_container_width=True, key="btn_xm_exam"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "exam"; st.rerun()

    with col_ot:
        st.markdown('<div class="section-title">🚗 Ô TÔ (B1, B2, C)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Ô Tô", use_container_width=True, key="btn_ot_captoc"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Ô Tô", use_container_width=True, key="btn_ot_tips"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Ô Tô", use_container_width=True, key="btn_ot_exam"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC (KHÔI PHỤC NỘI DUNG) ---
def render_captoc_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🔢 CON SỐ & TUỔI", "🏎️ TỐC ĐỘ", "🆔 HẠNG XE", "🚔 SA HÌNH"])
    folders = ["images", "images_a1"]

    with tab1:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown("""<div class="tip-box"><div class="tip-title">🎂 Mẹo Độ Tuổi</div><div class="tip-content">👉 Nhìn 3 đáp án đầu, chọn số <span class="highlight-red">LỚN NHẤT</span>.</div><div class="formula-box">Đáp án = Số Tuổi Lớn Nhất</div></div>""", unsafe_allow_html=True)
            st.markdown("""<div class="tip-box" style="border-left-color: #8b5cf6;"><div class="tip-title">⏳ Niên hạn & Số liệu</div><div class="tip-content">• 🚛 Xe tải: <span class="highlight-blue">25 năm</span> | 🚌 Xe khách: <span class="highlight-blue">20 năm</span><br>• Còi: <span class="highlight-red">05h - 22h</span> | Đỗ xe cách lề: <span class="highlight-blue">0.25m</span><br>• Khoảng cách xe ngược chiều: <span class="highlight-blue">20m</span></div></div>""", unsafe_allow_html=True)
        with c2:
            img = load_image_smart("tip_tuoi", folders)
            if img: st.image(img, caption="Mẹo độ tuổi")

    with tab2:
        st.markdown("""<div class="tip-box" style="border-left-color: #f59e0b;"><div class="tip-title">🏎️ Tốc độ trong khu dân cư</div><div class="tip-content">• 🛣️ Đường <b>ĐÔI</b> (có dải phân cách): <span class="highlight-blue">60 km/h</span><br>• 🛣️ Đường <b>2 CHIỀU</b> (không có dải phân cách): <span class="highlight-blue">50 km/h</span></div></div>""", unsafe_allow_html=True)
        st.markdown("""<div class="tip-box" style="border-left-color: #f59e0b;"><div class="tip-title">📏 Khoảng cách an toàn (Mẹo trừ 30)</div><div class="tip-content">Lấy tốc độ lớn nhất <span class="highlight-red">Trừ đi 30</span> -> Ra đáp án gần nhất.</div><div class="formula-box">Tốc độ Max - 30 = Khoảng cách</div></div>""", unsafe_allow_html=True)

    with tab3:
        st.markdown("""<div class="tip-box" style="border-left-color: #10b981;"><div class="tip-title">🆔 Mẹo Hạng Giấy Phép</div><div class="tip-content">• Hỏi <b>FE</b>: Chọn ý 1 (Em 1)<br>• Hỏi <b>FC</b>: Chọn ý 2 (Chị 2)<br>• 🛵 <b>Hạng A1 (2025):</b> Lái xe đến <span class="highlight-blue">125cm3</span> hoặc điện <span class="highlight-blue">11kW</span>.</div></div>""", unsafe_allow_html=True)

    with tab4:
        st.markdown("""<div class="tip-box" style="border-left-color: #ef4444;"><div class="tip-title">👮 Sa Hình & CSGT</div><div class="tip-content">• Thấy hình CSGT giơ tay: Chọn ngay ý <span class="highlight-red">3</span>.<br>• Ưu tiên: <b>Hỏa > Sự > Thương > Công</b>.</div></div>""", unsafe_allow_html=True)
        img = load_image_smart("tip_sahinh", folders)
        if img: st.image(img)

# --- 7. TRANG MẸO CHI TIẾT ---
def render_tips_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.markdown(f"## 📖 Mẹo Chi Tiết: {st.session_state.license_type}")
    data = load_data_by_license(st.session_state.license_type)
    if not data: st.warning("Chưa có dữ liệu."); return
    for tip in data:
        st.markdown(f'<div class="tip-box" style="border-left-color:#db2777"><div class="tip-title">📌 {tip.get("title", "Mẹo")}</div>', unsafe_allow_html=True)
        for line in tip.get('content', []):
            st.markdown(f'<div class="tip-content">• {line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if tip.get('image'):
            img = load_image_smart(tip['image'], ["images", "images_a1"])
            if img: st.image(img, use_container_width=True)

# --- 8. TRANG LUYỆN THI (FIX AUTO, FIX ẢNH CÂU 1) ---
def render_exam_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Thiếu dữ liệu!"); return
    total = len(all_qs)

    # ĐIỀU HƯỚNG TRÊN
    st.write("---")
    n1, n2, n3 = st.columns([1, 1, 1])
    with n1:
        if st.button("⬅️ Trước", key="p_top"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with n2:
        new_q = st.number_input("Nhảy tới câu:", 1, total, st.session_state.current_q_index + 1)
        if new_q - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_q - 1; st.rerun()
    with n3:
        if st.button("Tiếp theo ➡️", key="n_top", type="primary"):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

    # CÀI ĐẶT
    auto_mode = st.toggle("🚀 CHẾ ĐỘ AUTO (Chạy liên tục - Tự chọn đúng)", key="auto_mode")
    delay = st.slider("Giây chờ qua câu:", 1, 5, 2)

    # CÂU HỎI
    q = all_qs[st.session_state.current_q_index]
    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    st.info(f"**{q['question']}**")
    
    # --- FIX DÍNH ẢNH CÂU 1 ---
    current_img = q.get('image')
    if current_img:
        # Nếu là câu 1, kiểm tra kĩ để không dính ảnh mẹo 1
        if st.session_state.current_q_index == 0 and (current_img == "1" or "tip" in str(current_img)):
            img_data = None
        else:
            img_data = load_image_smart(current_img, ["images", "images_a1"])
        if img_data: st.image(img_data)

    correct_ans = q['correct_answer'].strip()
    options = q['options']
    correct_idx = [i for i, opt in enumerate(options) if opt.strip() == correct_ans][0]

    # RADIO (Tự chọn đúng nếu bật Auto)
    user_choice = st.radio("Chọn đáp án:", options, index=correct_idx if auto_mode else None, key=f"r_{st.session_state.current_q_index}")

    if user_choice:
        if user_choice.strip() == correct_ans:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #16a34a !important; border: 4px solid #14532d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.success("ĐÚNG!")
        else:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dc2626 !important; border: 4px solid #7f1d1d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"SAI! Đáp án là: {correct_ans}")

        # LOGIC AUTO QUA CÂU
        if auto_mode:
            placeholder = st.empty()
            with placeholder.container():
                st.write(f"⏳ Sẽ chuyển câu sau {delay} giây...")
                st.progress(100)
            time.sleep(delay)
            if st.session_state.current_q_index < total - 1:
                st.session_state.current_q_index += 1
                st.rerun()

# --- 9. LUỒNG CHÍNH ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "tips": render_tips_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
