import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Siêu Cấp Tốc",
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

# --- 3. CSS GIAO DIỆN CẢI TIẾN (FONT TO & RÕ) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f0f2f6; }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 6rem !important; }

    /* THẺ MẸO CẤP TỐC CẢI TIẾN */
    .tip-box {
        background: white; border-radius: 20px; padding: 25px; margin-bottom: 20px;
        border-left: 10px solid #3b82f6; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1);
    }
    .tip-title {
        color: #1e293b; font-weight: 800; font-size: 1.4rem; 
        margin-bottom: 12px; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .tip-content { color: #334155; font-size: 1.3rem; line-height: 1.6; font-weight: 500; }
    .highlight-red { color: #e11d48; font-weight: 800; background: #fff1f2; padding: 2px 8px; border-radius: 8px; }
    .highlight-blue { color: #2563eb; font-weight: 800; background: #eff6ff; padding: 2px 8px; border-radius: 8px; }
    
    /* CÔNG THỨC NHỚ NHANH */
    .formula-box {
        background: #f8fafc; border: 3px dashed #94a3b8; border-radius: 15px;
        padding: 20px; text-align: center; font-weight: 800; font-size: 1.6rem;
        color: #1e293b; margin: 15px 0;
    }

    /* TRANG CHỦ CARD */
    .hero-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px; border-radius: 30px; color: white; text-align: center; margin-bottom: 30px;
    }
    .action-card {
        background: white; padding: 35px; border-radius: 25px;
        border: 2px solid #e2e8f0; text-align: center; cursor: pointer;
        transition: all 0.3s ease; height: 100%; box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .action-card:hover { transform: translateY(-8px); border-color: #3b82f6; box-shadow: 0 20px 25px -5px rgba(0,0,0,0.1); }

    /* RADIO BUTTONS (AUTO COLOR BOLD) */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 18px; display: flex; flex-direction: column; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 25px 25px !important;
        border-radius: 18px; width: 100%; cursor: pointer; transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.5rem !important; font-weight: 600 !important; color: #1e293b !important;
    }
    
    /* ẢNH & NÚT */
    div[data-testid="stImage"] img { border-radius: 15px; border: 3px solid #fff; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    div[data-testid="stButton"] button { border-radius: 15px; font-weight: 800; height: 4rem; font-size: 1.3rem !important; }

</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

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

# --- 5. GIAO DIỆN TRANG CHỦ ---
def render_home_page():
    st.markdown('<div class="hero-card"><h1>🚗 GPLX PRO: HỌC LÀ ĐẬU</h1><p style="font-size:1.2rem">Học vẹt thông minh qua hình ảnh & Auto luyện tập</p></div>', unsafe_allow_html=True)
    
    st.markdown("### 1. Chọn loại giấy phép")
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🛵 XE MÁY (A1, A2)", type="primary" if "Xe máy" in st.session_state.license_type else "secondary", use_container_width=True):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.rerun()
    with c2:
        if st.button("🚗 Ô TÔ (B1, B2, C)", type="primary" if "Ô tô" in st.session_state.license_type else "secondary", use_container_width=True):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.rerun()

    st.markdown("---")
    st.markdown("### 2. Chọn phương pháp học")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="action-card" style="border-top: 8px solid #3b82f6;"><h3>⚡ MẸO CẤP TỐC</h3><p style="font-size:1.1rem; color:#64748b">Dành cho người bận rộn, học theo quy luật con số và hình ảnh</p></div>', unsafe_allow_html=True)
        if st.button("XEM MẸO NHANH ⚡", use_container_width=True): st.session_state.page = "captoc"; st.rerun()
    with col2:
        st.markdown('<div class="action-card" style="border-top: 8px solid #10b981;"><h3>📝 LUYỆN THI 600 CÂU</h3><p style="font-size:1.1rem; color:#64748b">Chế độ tự động chọn đáp án đúng giúp ghi nhớ mặt chữ</p></div>', unsafe_allow_html=True)
        if st.button("VÀO LUYỆN THI 📝", use_container_width=True): st.session_state.page = "exam"; st.rerun()

# --- 6. GIAO DIỆN MẸO CẤP TỐC (CẢI TIẾN FONT & MÀU) ---
def render_captoc_page():
    if st.button("🏠 VỀ TRANG CHỦ"): st.session_state.page = "home"; st.rerun()
    st.markdown(f"## ⚡ BÍ KÍP CẤP TỐC: {st.session_state.license_type}")
    
    folders = ["images", "images_a1"]
    tab1, tab2, tab3, tab4 = st.tabs(["🔢 CON SỐ & TUỔI", "🏎️ TỐC ĐỘ", "🆔 HẠNG XE", "🚔 SA HÌNH"])

    with tab1:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown(f"""<div class="tip-box">
                <div class="tip-title">🎂 Mẹo Độ Tuổi</div>
                <div class="tip-content">Câu hỏi về tuổi: Nhìn 3 đáp án đầu, chọn số <span class="highlight-red">LỚN NHẤT</span>.</div>
                <div class="formula-box">Đáp án = Số Lớn Nhất</div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="tip-box" style="border-left-color: #8b5cf6;">
                <div class="tip-title">⏳ Niên hạn & Còi</div>
                <div class="tip-content">
                • Xe tải: <span class="highlight-blue">25 năm</span> | Xe khách: <span class="highlight-blue">20 năm</span> [cite: 22]<br>
                • Sử dụng còi: <span class="highlight-red">05h - 22h</span>. Cấm còi ban đêm.
                </div>
            </div>""", unsafe_allow_html=True)
        with c2:
            img = load_image_smart("tip_tuoi", folders)
            if img: st.image(img, caption="Minh họa mẹo độ tuổi", use_container_width=True)

    with tab2:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown(f"""<div class="tip-box" style="border-left-color: #f59e0b;">
                <div class="tip-title">🏎️ Tốc độ trong khu dân cư</div>
                <div class="tip-content">
                • Đường <b>ĐÔI</b> (có dải phân cách): <span class="highlight-blue">60 km/h</span><br>
                • Đường <b>2 CHIỀU</b> (không dải phân cách): <span class="highlight-blue">50 km/h</span> [cite: 23]
                </div>
            </div>""", unsafe_allow_html=True)
            st.markdown(f"""<div class="tip-box" style="border-left-color: #f59e0b;">
                <div class="tip-title">📏 Mẹo Khoảng cách (Trừ 30)</div>
                <div class="tip-content">Lấy tốc độ lớn nhất <span class="highlight-red">Trừ đi 30</span> -> Ra số gần đáp án nhất.</div>
                <div class="formula-box">V(max) - 30 = Đáp án</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            img = load_image_smart("tip_tocdo", folders)
            if img: st.image(img, use_container_width=True)

    with tab3:
        st.markdown(f"""<div class="tip-box" style="border-left-color: #10b981;">
            <div class="tip-title">🛵 Hạng xe A1 (Luật mới 2025)</div>
            <div class="tip-content">Được lái xe 2 bánh đến <span class="highlight-blue">125 cm3</span> hoặc điện đến <span class="highlight-blue">11 kW</span>.</div>
        </div>""", unsafe_allow_html=True)
        st.markdown(f"""<div class="tip-box" style="border-left-color: #10b981;">
            <div class="tip-title">🆔 Mẹo Hạng FE, FC</div>
            <div class="tip-content">Hỏi <b>FE</b>: Chọn ý 1 (Em 1) | Hỏi <b>FC</b>: Chọn ý 2 (Chị 2).</div>
        </div>""", unsafe_allow_html=True)

    with tab4:
        st.markdown(f"""<div class="tip-box" style="border-left-color: #ef4444;">
            <div class="tip-title">👮 Mẹo CSGT & Sa Hình</div>
            <div class="tip-content">
            • Thấy CSGT giơ tay: Chọn luôn ý <span class="highlight-red">3</span>[cite: 38].<br>
            • Thứ tự xe: <b>Hỏa > Sự > Thương > Công</b> (Cứu hỏa - Quân sự - Cứu thương - Công an).
            </div>
        </div>""", unsafe_allow_html=True)
        img = load_image_smart("tip_sahinh", folders)
        if img: st.image(img, use_container_width=True)

# --- 7. GIAO DIỆN LUYỆN THI (FIX CSS MÀU ĐẬM) ---
def render_exam_page():
    if st.button("🏠 VỀ TRANG CHỦ"): st.session_state.page = "home"; st.rerun()
    
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Thiếu dữ liệu câu hỏi!"); return

    with st.expander("⚙️ CÀI ĐẶT LUYỆN TẬP", expanded=True):
        c1, c2 = st.columns(2)
        with c1: auto_next = st.toggle("🚀 CHẾ ĐỘ AUTO (Tự động chọn đúng & chuyển câu)", key="auto_mode")
        with c2: delay = st.slider("Giây chuyển câu", 1, 5, 2)

    q = all_qs[st.session_state.current_q_index]
    total = len(all_qs)

    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    st.info(f"**{q['question']}**")
    
    # Hiển thị ảnh câu hỏi
    if q.get('image'):
        img = load_image_smart(q['image'], ["images", "images_a1"])
        if img: st.image(img)
        else: st.warning(f"Không tìm thấy ảnh: {q['image']}")

    # Logic tìm đáp án đúng
    correct_ans = q['correct_answer'].strip()
    options = q['options']
    correct_idx = 0
    for i, opt in enumerate(options):
        if opt.strip() == correct_ans:
            correct_idx = i
            break

    # HIỂN THỊ ĐÁP ÁN
    user_choice = st.radio("Chọn đáp án:", options, index=correct_idx if auto_next else None, key=f"r_{st.session_state.current_q_index}")

    if user_choice:
        is_correct = user_choice.strip() == correct_ans
        if is_correct:
            # TIÊM CSS XANH LÁ ĐẬM
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #16a34a !important; border: 4px solid #14532d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.success("CHÍNH XÁC!")
        else:
            # TIÊM CSS ĐỎ ĐẬM
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dc2626 !important; border: 4px solid #7f1d1d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"SAI! Đáp án đúng là: {correct_ans}")

        if auto_next:
            bar = st.progress(0, text=f"Đang tự động chuyển câu sau {delay}s...")
            for i in range(100):
                time.sleep(delay/100)
                bar.progress(i + 1)
            if st.session_state.current_q_index < total - 1:
                st.session_state.current_q_index += 1
                st.rerun()

    # Nút bấm thủ công
    st.write("---")
    col_p, col_n = st.columns(2)
    with col_p:
        if st.button("⬅️ Câu trước"): st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with col_n:
        if st.button("Câu tiếp theo ➡️"): st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

# --- 8. CHƯƠNG TRÌNH CHÍNH ---
def main():
    if st.session_state.page == "home": render_home_page()
    elif st.session_state.page == "captoc": render_captoc_page()
    elif st.session_state.page == "exam": render_exam_page()

if __name__ == "__main__":
    main()
