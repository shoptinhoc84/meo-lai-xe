import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Auto Color Master",
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

# --- 3. CSS GIAO DIỆN TỔNG THỂ ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* Giao diện Thẻ nội dung */
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

    /* CSS CHO TRANG MẸO CẤP TỐC */
    .tip-box {
        background: white; border-radius: 16px; padding: 20px; margin-bottom: 15px;
        border-left: 6px solid #3b82f6; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    .tip-title { color: #1e293b; font-weight: 800; font-size: 1.1rem; margin-bottom: 8px; text-transform: uppercase; }
    .formula-box { background: #f1f5f9; border: 2px dashed #cbd5e1; border-radius: 12px; padding: 15px; text-align: center; font-weight: 700; font-size: 1.2rem; color: #475569; margin: 10px 0; }

    /* --- RADIO BUTTONS GỐC (STYLE CHƯA CHỌN) --- */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 16px; display: flex; flex-direction: column; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #e2e8f0; padding: 20px 20px !important;
        border-radius: 16px; width: 100%; cursor: pointer; display: flex; align-items: center; transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.5rem !important; font-weight: 500 !important; color: #64748b !important; line-height: 1.5 !important;
    }

    /* Style ảnh câu hỏi */
    div[data-testid="stImage"] img { border-radius: 12px; max-height: 400px; object-fit: contain; }

</style>
""", unsafe_allow_html=True)

# --- 4. HÀM TIỆN ÍCH ---
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

def load_image_smart(base_name, folders):
    if not base_name: return None
    exts = ['.png', '.jpg', '.jpeg', '.PNG', '.JPG']
    clean_name = str(base_name).strip()
    for folder in folders:
        for ext in exts:
            path = os.path.join(folder, clean_name if clean_name.endswith(tuple(exts)) else clean_name + ext)
            if os.path.exists(path):
                return ImageOps.exif_transpose(Image.open(path))
    return None

# --- 5. TRANG CHỦ ---
def render_home_page():
    st.markdown('<div class="hero-card"><h2>🚗 GPLX MASTER PRO</h2><p>Ôn thi lý thuyết hiệu quả nhất</p></div>', unsafe_allow_html=True)
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
        st.markdown('<div class="action-card" style="border-left: 5px solid #4f46e5;"><h3>⚡ Mẹo Cấp Tốc</h3><p>Học nhanh qua hình ảnh</p></div>', unsafe_allow_html=True)
        if st.button("Vào học mẹo ⚡", use_container_width=True): st.session_state.page = "captoc"; st.rerun()
    with col2:
        st.markdown('<div class="action-card"><h3>📝 Luyện Thi</h3><p>600 câu trắc nghiệm</p></div>', unsafe_allow_html=True)
        if st.button("Bắt đầu thi 📝", use_container_width=True): st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC (Dựa trên captoc_sach_dep.docx) ---
def render_captoc_page():
    if st.button("🏠 Trang chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Bí kíp cấp tốc: {st.session_state.license_type}")
    
    tab1, tab2, tab3 = st.tabs(["🔢 Con số & Độ tuổi", "🚀 Tốc độ & Hạng xe", "🚥 Sa hình"])
    folders = ["images"]

    with tab1:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            [cite_start]st.markdown('<div class="tip-box"><div class="tip-title">🎂 Mẹo Độ Tuổi</div>Nhìn 3 đáp án đầu và tìm số <b>LỚN NHẤT</b>[cite: 21].</div>', unsafe_allow_html=True)
            [cite_start]st.markdown('<div class="tip-box"><div class="tip-title">⏳ Niên hạn xe</div>Xe tải: <b>25 năm</b> | Xe khách: <b>20 năm</b>[cite: 22].</div>', unsafe_allow_html=True)
        with c2:
            img = load_image_smart("tip_tuoi", folders)
            if img: st.image(img, use_container_width=True)

    with tab2:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            [cite_start]st.markdown('<div class="tip-box"><div class="tip-title">📏 Mẹo Khoảng cách</div>Tốc độ lớn nhất - 30 = Đáp án gần nhất[cite: 23].</div>', unsafe_allow_html=True)
        with c2:
            img = load_image_smart("tip_tocdo", folders)
            if img: st.image(img, use_container_width=True)

    with tab3:
        [cite_start]st.markdown('<div class="tip-box"><div class="tip-title">👮 Mẹo Sa hình</div>Thấy CSGT giơ tay: chọn đáp án <b>3</b>[cite: 26, 27].</div>', unsafe_allow_html=True)

# --- 7. TRANG LUYỆN THI (LOGIC ĐỔI MÀU AUTO) ---
def render_exam_page():
    if st.button("🏠 Home"): st.session_state.page = "home"; st.rerun()
    
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Thiếu file dữ liệu!"); return

    # Filter & Settings
    c1, c2, c3 = st.columns([2, 1, 1])
    with c1: auto_next = st.toggle("Chế độ Tự động chuyển câu (Auto)", key="auto_mode")
    with c2: delay = st.slider("Thời gian chờ (giây)", 1, 5, 2)
    with c3: show_ans = st.toggle("Hiện đáp án ngay", key="show_ans")

    q = all_qs[st.session_state.current_q_index]
    total = len(all_qs)

    st.subheader(f"Câu {st.session_state.current_q_index + 1}/{total}")
    st.info(q['question'])
    
    if q.get('image'):
        img = load_image_smart(q['image'], ["images"])
        if img: st.image(img)

    user_choice = st.radio("Chọn đáp án đúng:", q['options'], index=None, key=f"q_{q['id']}")

    # --- XỬ LÝ MÀU SẮC NGAY LẬP TỨC ---
    if user_choice:
        is_correct = user_choice.strip() == q['correct_answer'].strip()
        
        if is_correct:
            # Inject CSS Xanh Lá Đậm cho câu Đúng
            st.markdown("""
                <style>
                div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
                    background-color: #22c55e !important; /* Green 500 */
                    border: 4px solid #166534 !important;
                }
                div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p {
                    color: white !important; font-weight: 900 !important;
                }
                </style>
            """, unsafe_allow_html=True)
            st.success("✅ CHÍNH XÁC!")
        else:
            # Inject CSS Đỏ Đậm cho câu Sai
            st.markdown("""
                <style>
                div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
                    background-color: #ef4444 !important; /* Red 500 */
                    border: 4px solid #991b1b !important;
                }
                div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p {
                    color: white !important; font-weight: 900 !important;
                }
                </style>
            """, unsafe_allow_html=True)
            st.error(f"❌ SAI! Đáp án đúng là: {q['correct_answer']}")

        if auto_next:
            # Hiển thị thanh tiến trình để người dùng kịp nhìn thấy màu sắc
            progress_bar = st.progress(0, text=f"Chuyển câu sau {delay}s...")
            for percent_complete in range(100):
                time.sleep(delay / 100)
                progress_bar.progress(percent_complete + 1)
            
            # Chuyển câu
            if st.session_state.current_q_index < total - 1:
                st.session_state.current_q_index += 1
                st.rerun()

    # Điều hướng thủ công
    st.write("---")
    col_p, col_n = st.columns(2)
    with col_p:
        if st.button("⬅️ Câu trước"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with col_n:
        if st.button("Câu tiếp theo ➡️"):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

# --- 8. LUỒNG CHÍNH ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
