import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Auto Next Generation",
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

# --- 3. CSS GIAO DIỆN TỔNG THỂ ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
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
    .action-card:hover { transform: translateY(-5px); border-color: #6366f1; }

    .tip-box {
        background: white; border-radius: 16px; padding: 20px; margin-bottom: 15px;
        border-left: 6px solid #3b82f6; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .tip-title { color: #1e293b; font-weight: 800; font-size: 1.1rem; margin-bottom: 8px; text-transform: uppercase; }

    /* RADIO BUTTONS STYLE */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 12px; display: flex; flex-direction: column; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #e2e8f0; padding: 15px 20px !important;
        border-radius: 12px; width: 100%; cursor: pointer; display: flex; align-items: center;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.25rem !important; font-weight: 500 !important; color: #334155 !important;
    }

    /* ẢNH CÂU HỎI */
    div[data-testid="stImage"] img { border-radius: 12px; max-height: 350px; object-fit: contain; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM HỖ TRỢ ---
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

def load_image_smart(base_name, folders):
    if not base_name: return None
    exts = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    name_only = str(base_name).split('.')[0]
    for folder in folders:
        for ext in exts:
            path = os.path.join(folder, name_only + ext)
            if os.path.exists(path):
                return ImageOps.exif_transpose(Image.open(path))
    return None

# --- 5. TRANG CHỦ ---
def render_home_page():
    st.markdown('<div class="hero-card"><h2>🚗 GPLX MASTER PRO</h2><p>Hệ thống tự động ôn tập thông minh</p></div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🚗 Ô TÔ", type="primary" if "Ô tô" in st.session_state.license_type else "secondary", use_container_width=True):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.rerun()
    with c2:
        if st.button("🛵 XE MÁY", type="primary" if "Xe máy" in st.session_state.license_type else "secondary", use_container_width=True):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.rerun()
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="action-card" style="border-left: 5px solid #4f46e5;"><h3>⚡ Mẹo Cấp Tốc</h3><p>Học nhanh qua bí kíp</p></div>', unsafe_allow_html=True)
        if st.button("Học Mẹo ⚡", use_container_width=True): st.session_state.page = "captoc"; st.rerun()
    with col2:
        st.markdown('<div class="action-card"><h3>📝 Luyện Thi</h3><p>600 câu có giải thích</p></div>', unsafe_allow_html=True)
        if st.button("Luyện Thi 📝", use_container_width=True): st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC ---
def render_captoc_page():
    if st.button("🏠 Trang chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo ôn thi: {st.session_state.license_type}")
    
    tab1, tab2, tab3 = st.tabs(["🔢 Con số & Độ tuổi", "🚀 Tốc độ & Hạng xe", "🚥 Sa hình"])
    folders = ["images"]

    with tab1:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown('<div class="tip-box"><div class="tip-title">🎂 Mẹo Độ Tuổi</div>Chọn đáp án có số <b>LỚN NHẤT</b>.</div>', unsafe_allow_html=True)
            st.markdown('<div class="tip-box"><div class="tip-title">⏳ Niên hạn</div>Xe tải: 25 năm | Xe khách: 20 năm.</div>', unsafe_allow_html=True)
        with c2:
            img = load_image_smart("tip_tuoi", folders)
            if img: st.image(img, use_container_width=True)

    with tab2:
        st.markdown('<div class="tip-box"><div class="tip-title">🏎️ Tốc độ khu dân cư</div>Đường đôi: 60km/h | Đường 2 chiều: 50km/h.</div>', unsafe_allow_html=True)
        st.markdown('<div class="tip-box"><div class="tip-title">📏 Khoảng cách an toàn</div>Lấy số Tốc độ lớn nhất trừ đi 30.</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown('<div class="tip-box"><div class="tip-title">👮 Cảnh sát giao thông</div>Thấy hình CSGT giơ tay: luôn chọn đáp án 3.</div>', unsafe_allow_html=True)

# --- 7. TRANG LUYỆN THI (FIX AUTO CHẠY LUÔN) ---
def render_exam_page():
    if st.button("🏠 Home"): st.session_state.page = "home"; st.rerun()
    
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Không tìm thấy file dulieu_600_cau.json"); return

    # THANH ĐIỀU KHIỂN
    with st.expander("⚙️ Cấu hình học tập", expanded=True):
        c1, c2 = st.columns(2)
        with c1: auto_next = st.toggle("🚀 CHẾ ĐỘ AUTO (Chạy liên tục)", key="auto_mode")
        with c2: delay = st.slider("Tốc độ chuyển câu (giây)", 1, 10, 3)

    q = all_qs[st.session_state.current_q_index]
    total = len(all_qs)

    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    st.info(q['question'])
    
    if q.get('image'):
        img = load_image_smart(q['image'], ["images"])
        if img: st.image(img)

    # LOGIC ÉP CHỌN ĐÁP ÁN KHI AUTO
    correct_ans = q['correct_answer'].strip()
    options = q['options']
    
    # Tìm vị trí đáp án đúng trong list options
    correct_idx = 0
    for i, opt in enumerate(options):
        if opt.strip() == correct_ans:
            correct_idx = i
            break

    # Nếu bật Auto, ép index về câu đúng luôn
    forced_index = None
    if auto_next:
        forced_index = correct_idx

    user_choice = st.radio(
        "Chọn đáp án:", 
        options, 
        index=forced_index, 
        key=f"radio_{st.session_state.current_q_index}"
    )

    # HIỂN THỊ MÀU SẮC & XỬ LÝ CHUYỂN CÂU
    if user_choice:
        is_correct = user_choice.strip() == correct_ans
        
        if is_correct:
            # Ép CSS màu xanh đậm cho câu Đúng
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #16a34a !important; border: 3px solid #14532d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 800 !important; }</style>""", unsafe_allow_html=True)
            st.success("Chính xác!")
        else:
            # Ép CSS màu đỏ đậm cho câu Sai
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dc2626 !important; border: 3px solid #7f1d1d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 800 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"Sai rồi! Đáp án đúng là: {correct_ans}")

        # Nếu đang ở chế độ Auto, chạy thanh đếm ngược và tự Rerun
        if auto_next:
            prog_bar = st.progress(0, text=f"Sẽ chuyển câu sau {delay}s...")
            for i in range(100):
                time.sleep(delay / 100)
                prog_bar.progress(i + 1)
            
            # Chuyển câu
            if st.session_state.current_q_index < total - 1:
                st.session_state.current_q_index += 1
                st.rerun()

    # Nút bấm thủ công
    st.write("---")
    col_p, col_n = st.columns(2)
    with col_p:
        if st.button("⬅️ Trước"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with col_n:
        if st.button("Tiếp theo ➡️"):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

# --- 8. LUỒNG CHÍNH ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
