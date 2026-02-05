import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Bản Cải Tiến 2026",
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

# --- 3. CSS CẢI TIẾN (FONT TO, FIX LAYOUT & COLOR BOLD) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* FIX LỖI LÚ TRÊN: Tăng padding để nội dung không bị che */
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
        margin: 20px 0 15px 0; padding-bottom: 5px; border-bottom: 5px solid #3b82f6;
        display: inline-block;
    }
    
    /* MẸO CHI TIẾT (MẸO CŨ) - FONT SIÊU TO RÕ */
    .detail-card {
        background: white; border-radius: 20px; padding: 30px; margin-bottom: 25px; 
        box-shadow: 0 10px 20px rgba(0,0,0,0.05); border-top: 10px solid #3b82f6;
    }
    .detail-title { font-size: 1.8rem !important; font-weight: 800 !important; color: #0f172a; margin-bottom: 20px; }
    .detail-line { font-size: 1.5rem !important; line-height: 1.6; color: #334155; margin-bottom: 12px; }

    /* RADIO BUTTONS (ĐÁP ÁN) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 25px !important;
        border-radius: 18px; width: 100%; cursor: pointer; margin-bottom: 10px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.6rem !important; font-weight: 600 !important; color: #1e293b;
    }

    /* NÚT ĐIỀU HƯỚNG */
    div[data-testid="stButton"] button {
        border-radius: 15px; font-weight: 800; height: 4.5rem; font-size: 1.4rem !important;
        transition: all 0.3s ease;
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

# --- 5. TRANG CHỦ (TỐI ƯU MỘT CHẠM - VÀO LUÔN) ---
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

# --- 6. TRANG MẸO CẤP TỐC ---
def render_captoc_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    tab1, tab2, tab3 = st.tabs(["🔢 Con số", "🏎️ Tốc độ", "🚔 Sa hình"])
    with tab1:
        st.info("💡 Mẹo tuổi: Chọn số LỚN NHẤT trong các đáp án.")
        img = load_image_smart("tip_tuoi", ["images"])
        if img: st.image(img)

# --- 7. TRANG MẸO CHI TIẾT (CẢI TIẾN FONT/MÀU) ---
def render_tips_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.markdown(f"## 📖 Mẹo Chi Tiết: {st.session_state.license_type}")
    
    data = load_data_by_license(st.session_state.license_type)
    if not data: st.warning("Chưa có dữ liệu."); return
    
    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Lọc theo chủ đề:", ["Tất cả"] + cats)
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    
    for tip in items:
        st.markdown(f'<div class="detail-card"><div class="detail-title">📌 {tip.get("title", "Mẹo")}</div>', unsafe_allow_html=True)
        for line in tip.get('content', []):
            st.markdown(f'<div class="detail-line">• {line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if tip.get('image'):
            img = load_image_smart(tip['image'], ["images", "images_a1"])
            if img: st.image(img, use_container_width=True)

# --- 8. TRANG LUYỆN THI (FIX AUTO, FIX DÍNH ẢNH CÂU 1) ---
def render_exam_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Lỗi: Thiếu file dữ liệu!"); return
    total = len(all_qs)

    # THANH ĐIỀU HƯỚNG TRÊN
    st.write("---")
    n1, n2, n3 = st.columns([1, 1, 1])
    with n1:
        if st.button("⬅️ Câu trước", key="p_top"):
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
    delay = st.slider("Giây chờ chuyển câu:", 1, 5, 2)

    # LẤY CÂU HỎI
    q = all_qs[st.session_state.current_q_index]
    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    st.info(f"**{q['question']}**")
    
    # --- FIX DÍNH ẢNH CÂU 1 ---
    # Nếu là câu 1, ta bỏ qua ảnh nếu nó dính tên "1" (trùng tên mẹo)
    current_img = q.get('image')
    if current_img:
        # Lọc bỏ ảnh mẹo nếu vô tình dính vào câu 1
        if st.session_state.current_q_index == 0 and (current_img == "1" or "tip" in str(current_img)):
            img_data = None
        else:
            img_data = load_image_smart(current_img, ["images", "images_a1"])
        
        if img_data: st.image(img_data)

    # ĐÁP ÁN
    correct_ans = q['correct_answer'].strip()
    options = q['options']
    correct_idx = [i for i, opt in enumerate(options) if opt.strip() == correct_ans][0]

    # HIỂN THỊ (Nếu Auto thì ép index đúng luôn để chạy)
    user_choice = st.radio("Chọn đáp án:", options, index=correct_idx if auto_mode else None, key=f"r_{st.session_state.current_q_index}")

    if user_choice:
        if user_choice.strip() == correct_ans:
            # ÉP CSS MÀU XANH ĐẬM
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #16a34a !important; border: 4px solid #14532d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.success("ĐÚNG!")
        else:
            # ÉP CSS MÀU ĐỎ ĐẬM
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dc2626 !important; border: 4px solid #7f1d1d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"SAI! Đáp án là: {correct_ans}")

        # LOGIC AUTO - CHẠY LUÔN
        if auto_mode:
            placeholder = st.empty()
            with placeholder.container():
                st.write(f"⏳ Sẽ chuyển sang câu tiếp theo sau {delay} giây...")
                st.progress(100)
            
            time.sleep(delay)
            if st.session_state.current_q_index < total - 1:
                st.session_state.current_q_index += 1
                st.rerun()

# --- MAIN ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "tips": render_tips_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
