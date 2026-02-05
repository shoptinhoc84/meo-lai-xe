import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Mẹo Chi Tiết Mới",
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

# --- 3. CSS CẢI TIẾN (FONT CHỮ TO & MÀU SẮC RÕ RÀNG) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f1f5f9; }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 6rem !important; }

    /* --- PHẦN MẸO CHI TIẾT (CẢI TIẾN) --- */
    .detail-card {
        background: white; 
        border-radius: 20px; 
        padding: 30px; 
        margin-bottom: 25px; 
        box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
        border-top: 10px solid #3b82f6; /* Màu sẽ thay đổi theo chủ đề */
    }
    .detail-category {
        font-size: 1.1rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 10px;
    }
    .detail-title {
        font-size: 1.8rem !important; 
        font-weight: 800 !important; 
        color: #0f172a; 
        line-height: 1.3;
        margin-bottom: 20px;
    }
    .detail-line {
        font-size: 1.5rem !important; 
        line-height: 1.6; 
        color: #334155;
        margin-bottom: 15px;
        padding-left: 20px;
        position: relative;
    }
    .detail-line::before {
        content: "👉";
        position: absolute;
        left: -10px;
    }

    /* --- CÁC THÀNH PHẦN KHÁC --- */
    .hero-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px; border-radius: 30px; color: white; text-align: center; margin-bottom: 30px;
    }
    .action-card {
        background: white; padding: 35px; border-radius: 25px;
        border: 2px solid #e2e8f0; text-align: center; cursor: pointer;
        transition: all 0.3s ease; height: 100%;
    }
    .action-card:hover { transform: translateY(-8px); border-color: #3b82f6; }

    /* Radio Buttons cho luyện thi */
    div[role="radiogroup"] { gap: 16px; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 25px !important;
        border-radius: 18px; width: 100%; cursor: pointer;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.6rem !important; font-weight: 600 !important; color: #1e293b;
    }

    div[data-testid="stButton"] button { border-radius: 15px; font-weight: 800; height: 4rem; font-size: 1.3rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM HỖ TRỢ ---
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

def load_image_smart(base_name, folders):
    if not base_name: return None
    exts = ['', '.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    clean_name = str(base_name).strip()
    for folder in folders:
        for ext in exts:
            path = os.path.join(folder, clean_name + ext)
            if os.path.exists(path):
                try: return ImageOps.exif_transpose(Image.open(path))
                except: continue
    return None

def get_category_color(category):
    # Trả về mã màu đậm cho từng loại mẹo
    colors = {
        "Biển báo": "#dc2626", # Đỏ
        "Sa hình": "#ca8a04",  # Vàng đậm
        "Khái niệm": "#2563eb",# Xanh dương
        "Kỹ thuật": "#16a34a", # Xanh lá
        "Văn hóa": "#db2777"   # Hồng
    }
    for key, color in colors.items():
        if key.lower() in category.lower(): return color
    return "#6366f1" # Tím mặc định

# --- 5. TRANG CHỦ ---
def render_home_page():
    st.markdown('<div class="hero-card"><h1>🚗 GPLX PRO: BẢN CẢI TIẾN 2026</h1><p style="font-size:1.3rem">Giao diện mới cho Mẹo Chi Tiết - Học nhanh, nhớ lâu</p></div>', unsafe_allow_html=True)
    
    st.markdown("### 1. Chọn loại giấy phép")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛵 XE MÁY (A1, A2)", type="primary" if "Xe máy" in st.session_state.license_type else "secondary", use_container_width=True):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.rerun()
    with c2:
        if st.button("🚗 Ô TÔ (B1, B2, C)", type="primary" if "Ô tô" in st.session_state.license_type else "secondary", use_container_width=True):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.rerun()

    st.markdown("---")
    st.markdown("### 2. Chế độ học tập")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div class="action-card" style="border-top: 8px solid #3b82f6;"><h3>⚡ MẸO CẤP TỐC</h3><p>Học vẹt qua ảnh tóm tắt</p></div>', unsafe_allow_html=True)
        if st.button("XEM MẸO NHANH ⚡", use_container_width=True): st.session_state.page = "captoc"; st.rerun()
    with col2:
        st.markdown('<div class="action-card" style="border-top: #db2777 8px solid;"><h3>📖 MẸO CHI TIẾT</h3><p>Đầy đủ bí kíp từng chủ đề</p></div>', unsafe_allow_html=True)
        if st.button("XEM MẸO CŨ 📖", use_container_width=True): st.session_state.page = "tips"; st.rerun()
    with col3:
        st.markdown('<div class="action-card" style="border-top: 8px solid #10b981;"><h3>📝 LUYỆN THI</h3><p>Chế độ Auto chuyển câu</p></div>', unsafe_allow_html=True)
        if st.button("VÀO THI 📝", use_container_width=True): st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CHI TIẾT (CẢI TIẾN MÀU & FONT) ---
def render_tips_page():
    if st.button("🏠 VỀ TRANG CHỦ"): st.session_state.page = "home"; st.rerun()
    
    st.markdown(f"## 📖 Mẹo Chi Tiết: {st.session_state.license_type}")
    data = load_data_by_license(st.session_state.license_type)
    if not data: 
        st.warning("Chưa có dữ liệu mẹo cũ cho hạng này."); return
    
    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Lọc theo chủ đề:", ["Tất cả"] + cats)
    
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    st.write("---")
    
    for tip in items:
        color = get_category_color(tip.get('category', 'Khác'))
        
        # Thẻ card mẹo chi tiết
        st.markdown(f"""
        <div class="detail-card" style="border-top-color: {color};">
            <div class="detail-category" style="color: {color};">{tip.get('category', 'Mẹo')}</div>
            <div class="detail-title">📌 {tip.get('title', 'Mẹo')}</div>
        """, unsafe_allow_html=True)
        
        # Nội dung từng dòng
        for line in tip.get('content', []):
            display_line = line.replace("=>", "👉").replace("(", "<br><small>(").replace(")", ")</small>")
            st.markdown(f'<div class="detail-line">{display_line}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True) # Đóng thẻ card
        
        if tip.get('image'):
            img = load_image_smart(tip['image'], ["images", "images_a1"])
            if img: st.image(img, use_container_width=True)
        st.write("---")

# --- 7. TRANG MẸO CẤP TỐC ---
def render_captoc_page():
    if st.button("🏠 TRANG CHỦ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    tab1, tab2, tab3 = st.tabs(["🔢 Con số", "🏎️ Tốc độ", "🚔 Sa hình"])
    with tab1:
        st.info("💡 Mẹo tuổi: Chọn số LỚN NHẤT trong 3 đáp án đầu.")
        img = load_image_smart("tip_tuoi", ["images"])
        if img: st.image(img)
    # (Các mẹo khác tương tự bản cũ)

# --- 8. TRANG LUYỆN THI (AUTO CHẠY LUÔN) ---
def render_exam_page():
    if st.button("🏠 TRANG CHỦ"): st.session_state.page = "home"; st.rerun()
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Thiếu dữ liệu!"); return

    auto_next = st.toggle("🚀 CHẾ ĐỘ AUTO", key="auto_mode")
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

# --- 9. LUỒNG CHÍNH ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "tips": render_tips_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
