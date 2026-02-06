import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Logic Sách",
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

# --- 3. CSS GIAO DIỆN (FONT TO, BỐ CỤC MỚI) ---
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

    /* TIP BOX: Dạng danh sách */
    .tip-box {
        background: white; border-radius: 15px; padding: 25px; margin-bottom: 15px;
        border-left: 8px solid #3b82f6; box-shadow: 0 5px 10px rgba(0,0,0,0.05);
    }
    .tip-title { color: #1e293b; font-weight: 800; font-size: 1.6rem; margin-bottom: 10px; text-transform: uppercase; }
    .tip-content { color: #334155; font-size: 1.4rem; line-height: 1.6; font-weight: 500; }
    
    /* Highlight text */
    .hl { background: #fef3c7; padding: 2px 6px; border-radius: 4px; font-weight: bold; color: #b45309; }
    .hl-red { color: #dc2626; font-weight: 900; background: #fee2e2; padding: 2px 8px; border-radius: 6px; }
    .hl-blue { color: #2563eb; font-weight: 900; }

    /* RADIO BUTTONS */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 20px !important;
        border-radius: 15px; width: 100%; cursor: pointer; margin-bottom: 10px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.5rem !important; font-weight: 600 !important; color: #1e293b;
    }

    /* BUTTONS */
    div[data-testid="stButton"] button {
        border-radius: 12px; font-weight: 800; height: 4rem; font-size: 1.3rem !important; transition: all 0.3s ease;
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

def load_multiple_images(prefix, folders):
    """Tìm tất cả ảnh có tiền tố (prefix) và trả về danh sách"""
    images = []
    for folder in folders:
        if not os.path.exists(folder): continue
        # Sắp xếp file để hiện đúng thứ tự 1, 2, 3...
        files = sorted(os.listdir(folder))
        for f in files:
            if f.startswith(prefix):
                try:
                    img = ImageOps.exif_transpose(Image.open(os.path.join(folder, f)))
                    images.append(img)
                except: continue
    return images

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

# --- 5. TRANG CHỦ ---
def render_home_page():
    st.markdown('<div class="hero-card"><h1>🚗 GPLX MASTER PRO</h1><p style="font-size:1.4rem">Hệ thống ôn thi thông minh 2026</p></div>', unsafe_allow_html=True)
    col_xm, col_ot = st.columns(2)

    with col_xm:
        st.markdown('<div class="section-title">🛵 XE MÁY (A1, A2)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Xe Máy", use_container_width=True, key="xm1"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Xe Máy", use_container_width=True, key="xm2"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Xe Máy", use_container_width=True, key="xm3"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "exam"; st.rerun()

    with col_ot:
        st.markdown('<div class="section-title">🚗 Ô TÔ (B1, B2, C)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Ô Tô", use_container_width=True, key="ot1"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Ô Tô", use_container_width=True, key="ot2"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Ô Tô", use_container_width=True, key="ot3"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC (HÌNH ẢNH NẰM CUỐI) ---
def render_captoc_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    
    # Chia 4 Tab chính theo sách
    tab1, tab2, tab3, tab4 = st.tabs(["🔢 CON SỐ & HẠNG", "🏎️ TỐC ĐỘ", "🛑 BIỂN BÁO", "🚔 SA HÌNH"])
    folders = ["images", "images_a1"]

    # TAB 1: CON SỐ
    with tab1:
        st.markdown("""
        <div class="tip-box">
            <div class="tip-title">🎂 Mẹo Độ Tuổi</div>
            <div class="tip-content">👉 Nhìn 3 đáp án đầu, chọn số <span class="hl-red">LỚN NHẤT</span>.<br>Ví dụ: 18, 21, 24 -> Chọn <b>24</b>.</div>
        </div>
        <div class="tip-box">
            <div class="tip-title">⏳ Niên Hạn & Còi</div>
            <div class="tip-content">
            • <b>Xe tải:</b> 25 năm | <b>Xe khách:</b> 20 năm.<br>
            • <b>Còi:</b> Được dùng từ 5h sáng đến 22h tối. Cấm còi ban đêm.
            </div>
        </div>
        <div class="tip-box" style="border-left-color: #8b5cf6;">
            <div class="tip-title">🆔 Mẹo Hạng Xe</div>
            <div class="tip-content">
            • Hỏi <b>FE</b>: Chọn ý <b>1</b> | Hỏi <b>FC</b>: Chọn ý <b>2</b>.<br>
            • <b>A1:</b> Xe đến 125cm3 hoặc 11kW. Không được lái xe 3 bánh.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📸 Hình ảnh minh họa (Tuổi & Hạng)")
        # Load ảnh: tip_tuoi_1, tip_tuoi_2... và tip_hang_1...
        imgs = load_multiple_images("tip_tuoi", folders) + load_multiple_images("tip_hang", folders)
        for img in imgs: st.image(img, use_container_width=True)

    # TAB 2: TỐC ĐỘ
    with tab2:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #f59e0b;">
            <div class="tip-title">🏎️ Tốc độ trong khu dân cư</div>
            <div class="tip-content">
            • Đường <b>ĐÔI</b> (Có giải phân cách): <span class="hl-blue">60 km/h</span>.<br>
            • Đường <b>2 CHIỀU</b> (Không giải phân cách): <span class="hl-blue">50 km/h</span>.
            </div>
        </div>
        <div class="tip-box" style="border-left-color: #f59e0b;">
            <div class="tip-title">📏 Mẹo Khoảng Cách (Trừ 30)</div>
            <div class="tip-content">
            Lấy tốc độ lớn nhất <span class="hl-red">TRỪ ĐI 30</span> -> Ra đáp án gần đúng nhất.<br>
            <i>Ví dụ: 60-80km/h -> 80 - 30 = 50. Chọn đáp án 55m.</i>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📸 Hình ảnh minh họa (Tốc độ)")
        imgs = load_multiple_images("tip_tocdo", folders)
        for img in imgs: st.image(img, use_container_width=True)

    # TAB 3: BIỂN BÁO
    with tab3:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #ef4444;">
            <div class="tip-title">🛑 Quy tắc Cấm</div>
            <div class="tip-content">
            • Cấm xe nhỏ -> Cấm luôn xe lớn.<br>
            • Cấm xe lớn -> <b>KHÔNG</b> cấm xe nhỏ.
            </div>
        </div>
        <div class="tip-box" style="border-left-color: #ef4444;">
            <div class="tip-title">🛑 Mẹo Dừng & Đỗ</div>
            <div class="tip-content">
            • Biển 1 gạch chéo (/): Cấm đỗ -> Chọn ý <span class="hl-red">3</span>.<br>
            • Biển 2 gạch chéo (X): Cấm dừng & đỗ -> Chọn ý <span class="hl-red">4</span>.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📸 Hình ảnh minh họa (Biển báo)")
        imgs = load_multiple_images("tip_bienbao", folders)
        for img in imgs: st.image(img, use_container_width=True)

    # TAB 4: SA HÌNH
    with tab4:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #10b981;">
            <div class="tip-title">👮 CSGT & Sa Hình</div>
            <div class="tip-content">
            • Thấy <b>CSGT</b> giơ tay: Chọn ngay đáp án <span class="hl-red">3</span>.<br>
            • <b>Xe tải:</b> Xe tải đi thẳng hướng nào chọn đáp án đó (Trừ biển xanh).<br>
            • <b>Thứ tự ưu tiên:</b> Hỏa > Sự > Thương > Công.
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        st.subheader("📸 Hình ảnh minh họa (Sa hình)")
        imgs = load_multiple_images("tip_sahinh", folders)
        if imgs:
            for i, img in enumerate(imgs):
                st.image(img, caption=f"Mẹo sa hình {i+1}", use_container_width=True)
        else:
            st.info("Chưa có ảnh. Hãy đặt tên file là: tip_sahinh_1.jpg, tip_sahinh_2.jpg...")

# --- 7. TRANG MẸO CHI TIẾT (MẸO CŨ) ---
def render_tips_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.markdown(f"## 📖 Mẹo Chi Tiết: {st.session_state.license_type}")
    data = load_data_by_license(st.session_state.license_type)
    if not data: st.warning("Chưa có dữ liệu."); return
    
    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Lọc chủ đề:", ["Tất cả"] + cats)
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    
    for tip in items:
        st.markdown(f"""
        <div class="tip-box" style="border-left-color: #db2777;">
            <div class="tip-title">📌 {tip.get('title', 'Mẹo')}</div>
        """, unsafe_allow_html=True)
        for line in tip.get('content', []):
            st.markdown(f'<div class="tip-content">• {line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if tip.get('image'):
            img = load_image_smart(tip['image'], ["images", "images_a1"])
            if img: st.image(img, use_container_width=True)

# --- 8. TRANG LUYỆN THI (AUTO CHẠY NGAY) ---
def render_exam_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Lỗi dữ liệu!"); return
    total = len(all_qs)

    st.write("---")
    # Điều hướng
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("⬅️ Câu trước", key="p"): st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with c2:
        new_q = st.number_input("Câu số:", 1, total, st.session_state.current_q_index + 1)
        if new_q - 1 != st.session_state.current_q_index: st.session_state.current_q_index = new_q - 1; st.rerun()
    with c3:
        if st.button("Tiếp theo ➡️", key="n", type="primary"): st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

    auto_mode = st.toggle("🚀 CHẾ ĐỘ AUTO (Chạy liên tục)", key="auto")
    delay = st.slider("Giây chờ:", 1, 5, 2)

    q = all_qs[st.session_state.current_q_index]
    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    st.info(f"**{q['question']}**")
    
    # Fix ảnh câu 1
    current_img = q.get('image')
    if current_img:
        if not (st.session_state.current_q_index == 0 and "tip" in str(current_img)):
            img = load_image_smart(current_img, ["images", "images_a1"])
            if img: st.image(img)

    correct_ans = q['correct_answer'].strip()
    options = q['options']
    correct_idx = [i for i, opt in enumerate(options) if opt.strip() == correct_ans][0]

    user_choice = st.radio("Chọn đáp án:", options, index=correct_idx if auto_mode else None, key=f"r_{st.session_state.current_q_index}")

    if user_choice:
        if user_choice.strip() == correct_ans:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #16a34a !important; border: 4px solid #14532d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.success("ĐÚNG!")
        else:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dc2626 !important; border: 4px solid #7f1d1d !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: white !important; font-weight: 900 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"SAI! Đáp án là: {correct_ans}")

        if auto_mode:
            placeholder = st.empty()
            with placeholder.container():
                st.write(f"⏳ Chuyển câu sau {delay}s...")
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
