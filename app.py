import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Siêu Cấp 2026",
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
    
    .block-container { 
        padding-top: 5rem !important; 
        padding-bottom: 6rem !important; 
        max-width: 1200px;
    }

    .hero-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px; border-radius: 30px; color: white; text-align: center; margin-bottom: 30px;
    }
    .section-title {
        font-size: 2rem; font-weight: 800; color: #1e293b;
        margin: 20px 0 15px 0; padding-bottom: 5px; border-bottom: 5px solid #3b82f6; display: inline-block;
    }

    .tip-box {
        background: white; border-radius: 18px; padding: 22px; margin-bottom: 20px;
        border-left: 12px solid #3b82f6; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
    }
    .tip-title { color: #1e293b; font-weight: 800; font-size: 1.5rem; margin-bottom: 10px; text-transform: uppercase; }
    .tip-content { color: #334155; font-size: 1.4rem; line-height: 1.6; font-weight: 600; }
    
    .highlight-red { color: white; background: #e11d48; padding: 2px 8px; border-radius: 8px; font-weight: 800; }
    .highlight-blue { color: white; background: #2563eb; padding: 2px 8px; border-radius: 8px; font-weight: 800; }

    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 25px !important;
        border-radius: 18px; width: 100%; cursor: pointer; margin-bottom: 12px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.6rem !important; font-weight: 700 !important; color: #1e293b;
    }

    div[data-testid="stButton"] button {
        border-radius: 15px; font-weight: 800; height: 4.5rem; font-size: 1.4rem !important; transition: all 0.3s ease;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM HỖ TRỢ (LOAD NHIỀU ẢNH) ---
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

def load_multiple_images(prefix, folders):
    """Tìm tất cả các ảnh có tên bắt đầu bằng prefix (ví dụ: tip_sahinh_)"""
    images = []
    exts = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    for folder in folders:
        if not os.path.exists(folder): continue
        # Lấy danh sách file trong thư mục, lọc những file bắt đầu bằng prefix
        all_files = sorted(os.listdir(folder))
        for filename in all_files:
            if filename.startswith(prefix):
                path = os.path.join(folder, filename)
                try:
                    img = ImageOps.exif_transpose(Image.open(path))
                    images.append(img)
                except: continue
    return images

def load_image_smart(base_name, folders):
    """Dùng cho ảnh câu hỏi đơn lẻ"""
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

# --- 5. TRANG CHỦ (VÀO LUÔN) ---
def render_home_page():
    st.markdown('<div class="hero-card"><h1>🚗 GPLX MASTER PRO</h1><p style="font-size:1.4rem">Hệ thống học vẹt thông minh - Tự động chọn đáp án đúng</p></div>', unsafe_allow_html=True)
    col_xm, col_ot = st.columns(2)

    with col_xm:
        st.markdown('<div class="section-title">🛵 XE MÁY (A1, A2)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Xe Máy", use_container_width=True, key="xm_1"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📝 Luyện Thi Xe Máy", use_container_width=True, key="xm_2"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "exam"; st.rerun()

    with col_ot:
        st.markdown('<div class="section-title">🚗 Ô TÔ (B1, B2, C)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Ô Tô", use_container_width=True, key="ot_1"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📝 Luyện Thi Ô Tô", use_container_width=True, key="ot_2"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC (HIỆN NHIỀU ẢNH) ---
def render_captoc_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    
    tab1, tab2, tab3 = st.tabs(["🔢 CON SỐ & TUỔI", "🏎️ TỐC ĐỘ", "🚔 SA HÌNH & BIỂN BÁO"])
    folders = ["images", "images_a1"]

    with tab1:
        st.markdown('<div class="tip-box"><div class="tip-title">🎂 Mẹo Độ Tuổi</div><div class="tip-content">👉 Nhìn 3 đáp án đầu, chọn số <span class="highlight-red">LỚN NHẤT</span>.</div></div>', unsafe_allow_html=True)
        imgs = load_multiple_images("tip_tuoi", folders)
        for i in imgs: st.image(i, use_container_width=True)

    with tab2:
        st.markdown('<div class="tip-box" style="border-left-color: #f59e0b;"><div class="tip-title">🏎️ Tốc độ khu dân cư</div><div class="tip-content">• Đường ĐÔI: <span class="highlight-blue">60 km/h</span><br>• Đường 2 CHIỀU: <span class="highlight-blue">50 km/h</span></div></div>', unsafe_allow_html=True)
        imgs = load_multiple_images("tip_tocdo", folders)
        for i in imgs: st.image(i, use_container_width=True)

    with tab3:
        st.markdown('<div class="tip-box" style="border-left-color: #ef4444;"><div class="tip-title">👮 Mẹo Sa Hình Nhiều Ảnh</div><div class="tip-content">Thấy CSGT giơ tay: Chọn ý <span class="highlight-red">3</span>.<br>Ưu tiên: <b>Hỏa > Sự > Thương > Công</b>.</div></div>', unsafe_allow_html=True)
        # TÌM TẤT CẢ ẢNH SA HÌNH (tip_sahinh_1, tip_sahinh_2...)
        imgs = load_multiple_images("tip_sahinh", folders)
        if imgs:
            for i, img in enumerate(imgs):
                st.image(img, caption=f"Hình minh họa sa hình {i+1}")
        else:
            st.warning("Hãy đặt tên ảnh là tip_sahinh_1.jpg, tip_sahinh_2.jpg... trong thư mục images")

# --- 7. TRANG LUYỆN THI (AUTO CHẠY LUÔN & FIX ẢNH) ---
def render_exam_page():
    if st.button("🏠 Trang Chủ"): st.session_state.page = "home"; st.rerun()
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Lỗi: Không có dữ liệu!"); return
    total = len(all_qs)

    # ĐIỀU HƯỚNG & AUTO
    st.write("---")
    c_nav1, c_nav2, c_nav3 = st.columns([1, 1, 1])
    with c_nav1:
        if st.button("⬅️ Câu trước"): st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with st.sidebar:
        auto_mode = st.toggle("🚀 CHẾ ĐỘ AUTO (Tự chọn đúng)", value=False, key="auto_mode")
        delay = st.slider("Giây chờ qua câu:", 1, 5, 2)

    q = all_qs[st.session_state.current_q_index]
    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    st.info(f"**{q['question']}**")
    
    # FIX LỖI DÍNH ẢNH CÂU 1
    current_img = q.get('image')
    if current_img and st.session_state.current_q_index != 0:
        img_data = load_image_smart(current_img, ["images", "images_a1"])
        if img_data: st.image(img_data)

    correct_ans = q['correct_answer'].strip()
    options = q['options']
    correct_idx = [i for i, opt in enumerate(options) if opt.strip() == correct_ans][0]

    # LOGIC AUTO: Nếu bật, index sẽ luôn là correct_idx
    user_choice = st.radio("Lựa chọn:", options, index=correct_idx if auto_mode else None, key=f"r_{st.session_state.current_q_index}")

    if user_choice:
        if user_choice.strip() == correct_ans:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #16a34a !important; border: 4px solid #14532d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.success("CHÍNH XÁC!")
        else:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dc2626 !important; border: 4px solid #7f1d1d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"SAI! Đáp án đúng là: {correct_ans}")

        if auto_mode:
            placeholder = st.empty()
            with placeholder.container():
                st.write(f"⏳ Đang chuyển câu sau {delay}s...")
                st.progress(100)
            time.sleep(delay)
            if st.session_state.current_q_index < total - 1:
                st.session_state.current_q_index += 1
                st.rerun()

# --- 8. LUỒNG CHÍNH ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
