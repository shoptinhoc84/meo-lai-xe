import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Master 2026",
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

# --- 3. CSS GIAO DIỆN (FONT TO, CARD ĐẸP, MÀU SẮC CHUẨN) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    /* FIX LỖI CHE TIÊU ĐỀ */
    .block-container { 
        padding-top: 5rem !important; 
        padding-bottom: 6rem !important; 
        max-width: 1200px;
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

    /* --- STYLE MẸO CẤP TỐC (MỚI) --- */
    .tip-box {
        background: white; border-radius: 18px; padding: 25px; margin-bottom: 20px;
        border-left: 10px solid #2563eb; box-shadow: 0 5px 15px rgba(0,0,0,0.05);
    }
    .tip-title { color: #1e293b; font-weight: 800; font-size: 1.6rem; margin-bottom: 15px; text-transform: uppercase; display: flex; align-items: center; gap: 10px; }
    .tip-content { color: #334155; font-size: 1.4rem; line-height: 1.6; font-weight: 500; }
    
    /* Highlight màu sắc */
    .hl-red { color: #dc2626; font-weight: 800; background: #fee2e2; padding: 2px 8px; border-radius: 6px; }
    .hl-blue { color: #2563eb; font-weight: 800; background: #eff6ff; padding: 2px 8px; border-radius: 6px; }
    .hl-green { color: #16a34a; font-weight: 800; background: #dcfce7; padding: 2px 8px; border-radius: 6px; }

    /* RADIO BUTTONS */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 20px !important;
        border-radius: 15px; width: 100%; cursor: pointer; margin-bottom: 10px;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.5rem !important; font-weight: 600 !important; color: #1e293b;
    }

    div[data-testid="stButton"] button {
        border-radius: 12px; font-weight: 800; height: 4.5rem; font-size: 1.3rem !important; transition: all 0.2s;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM HỖ TRỢ ---
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f: return json.load(f)
    except: return None

def load_data_by_license(license_type):
    """Load mẹo chi tiết (cũ)"""
    is_oto = "Ô tô" in license_type
    target = ['data.json', 'data (6).json'] if is_oto else ['tips_a1.json', 'tips_a1 (1).json']
    for f in target:
        d = load_json_file(f)
        if d: return d
    return []

def load_multiple_images(prefix, folders):
    """Load nhiều ảnh cùng lúc (ví dụ: tip_sahinh_1, tip_sahinh_2...)"""
    images = []
    # Quét tất cả file trong thư mục
    for folder in folders:
        if not os.path.exists(folder): continue
        all_files = sorted(os.listdir(folder)) # Sắp xếp để hiện theo thứ tự 1, 2, 3...
        for f in all_files:
            if f.startswith(prefix):
                try:
                    img = ImageOps.exif_transpose(Image.open(os.path.join(folder, f)))
                    images.append(img)
                except: continue
    return images

def load_image_smart(base_name, folders):
    """Load 1 ảnh thông minh cho phần thi"""
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
    st.markdown('<div class="hero-card"><h1>🚗 GPLX MASTER PRO</h1><p style="font-size:1.4rem">Hệ thống ôn thi thông minh & Mẹo cấp tốc</p></div>', unsafe_allow_html=True)
    col_xm, col_ot = st.columns(2)

    with col_xm:
        st.markdown('<div class="section-title">🛵 XE MÁY (A1, A2)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Xe Máy", use_container_width=True, key="xm_1"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Xe Máy", use_container_width=True, key="xm_2"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Xe Máy", use_container_width=True, key="xm_3"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "exam"; st.rerun()

    with col_ot:
        st.markdown('<div class="section-title">🚗 Ô TÔ (B1, B2, C)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Ô Tô", use_container_width=True, key="ot_1"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Ô Tô", use_container_width=True, key="ot_2"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Ô Tô", use_container_width=True, key="ot_3"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC (NỘI DUNG TỪ FILE WORD) ---
def render_captoc_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    
    # Chia thành 4 Tab logic theo sách
    tab1, tab2, tab3, tab4 = st.tabs(["🔢 TUỔI & HẠNG", "🏎️ TỐC ĐỘ", "🛑 BIỂN BÁO", "🚔 SA HÌNH"])
    folders = ["images", "images_a1"]

    # TAB 1: TUỔI & HẠNG XE
    with tab1:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown("""
            <div class="tip-box">
                <div class="tip-title">🎂 Mẹo Độ Tuổi</div>
                <div class="tip-content">
                    👉 Nhìn 3 đáp án đầu, tìm số <span class="hl-red">LỚN NHẤT</span>.<br>
                    Ví dụ: 18, 21, 24 -> Chọn <b>24</b>.
                </div>
            </div>
            <div class="tip-box" style="border-left-color: #8b5cf6;">
                <div class="tip-title">🆔 Mẹo Hạng Xe</div>
                <div class="tip-content">
                    • Hỏi <b>FE</b>: Chọn ý <b>1</b> (Em 1)<br>
                    • Hỏi <b>FC</b>: Chọn ý <b>2</b> (Chị 2)<br>
                    • <b>Niên hạn:</b> Xe tải <span class="hl-blue">25 năm</span>, Xe khách <span class="hl-blue">20 năm</span>.
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            # Load tất cả ảnh có tên bắt đầu bằng tip_tuoi... và tip_hang...
            imgs = load_multiple_images("tip_tuoi", folders) + load_multiple_images("tip_hang", folders)
            for img in imgs: st.image(img, use_container_width=True)

    # TAB 2: TỐC ĐỘ & KHOẢNG CÁCH
    with tab2:
        c1, c2 = st.columns([1.5, 1])
        with c1:
            st.markdown("""
            <div class="tip-box" style="border-left-color: #f59e0b;">
                <div class="tip-title">🏎️ Tốc Độ Khu Dân Cư</div>
                <div class="tip-content">
                    • Có giải phân cách (Đường đôi): <span class="hl-blue">60 km/h</span><br>
                    • Không có giải phân cách (2 chiều): <span class="hl-blue">50 km/h</span>
                </div>
            </div>
            <div class="tip-box" style="border-left-color: #f59e0b;">
                <div class="tip-title">📏 Khoảng Cách (Trừ 30)</div>
                <div class="tip-content">
                    Lấy tốc độ lớn nhất <span class="hl-red">TRỪ ĐI 30</span> -> Ra đáp án gần đúng nhất.<br>
                    <i>Ví dụ: 80-100km/h -> 100 - 30 = 70m.</i>
                </div>
            </div>
            """, unsafe_allow_html=True)
        with c2:
            imgs = load_multiple_images("tip_tocdo", folders)
            for img in imgs: st.image(img, use_container_width=True)

    # TAB 3: BIỂN BÁO
    with tab3:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #ef4444;">
            <div class="tip-title">🛑 Mẹo Biển Báo Cấm & Dừng Đỗ</div>
            <div class="tip-content">
                • <b>Cấm:</b> Cấm nhỏ thì cấm lớn (Cấm xe con -> Cấm xe tải).<br>
                • <b>Dừng / Đỗ:</b><br>
                &nbsp;&nbsp;+ 1 vạch chéo (/): Cấm đỗ -> Chọn ý <span class="hl-red">3</span><br>
                &nbsp;&nbsp;+ 2 vạch chéo (X): Cấm dừng đỗ -> Chọn ý <span class="hl-red">4</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        imgs = load_multiple_images("tip_bienbao", folders)
        for img in imgs: st.image(img, use_container_width=True)

    # TAB 4: SA HÌNH
    with tab4:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #10b981;">
            <div class="tip-title">👮 Mẹo Sa Hình & CSGT</div>
            <div class="tip-content">
                • Thấy hình <b>CSGT</b> giơ tay: Luôn chọn đáp án <span class="hl-red">3</span>.<br>
                • <b>Xe tải:</b> Xe tải đi thẳng hướng nào chọn đáp án đó (Trừ biển xanh).<br>
                • <b>Thứ tự ưu tiên:</b> Hỏa > Sự > Thương > Công.
            </div>
        </div>
        """, unsafe_allow_html=True)
        # Load tất cả ảnh sa hình (tip_sahinh_1, tip_sahinh_2...)
        imgs = load_multiple_images("tip_sahinh", folders)
        if imgs:
            # Hiển thị lưới ảnh (2 ảnh mỗi hàng)
            cols = st.columns(2)
            for i, img in enumerate(imgs):
                with cols[i % 2]:
                    st.image(img, caption=f"Hình minh họa {i+1}", use_container_width=True)
        else:
            st.info("Chưa có ảnh. Hãy đặt tên: tip_sahinh_1.jpg, tip_sahinh_2.jpg...")

# --- 7. TRANG MẸO CHI TIẾT (JSON CŨ) ---
def render_tips_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    st.markdown(f"## 📖 Mẹo Chi Tiết: {st.session_state.license_type}")
    data = load_data_by_license(st.session_state.license_type)
    if not data: st.warning("Chưa có dữ liệu mẹo cũ."); return
    
    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Lọc chủ đề:", ["Tất cả"] + cats)
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    
    for tip in items:
        st.markdown(f'<div class="tip-box" style="border-left-color: #db2777;"><div class="tip-title">📌 {tip.get("title", "Mẹo")}</div>', unsafe_allow_html=True)
        for line in tip.get('content', []):
            st.markdown(f'<div class="tip-content">• {line}</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        if tip.get('image'):
            img = load_image_smart(tip['image'], ["images", "images_a1"])
            if img: st.image(img, use_container_width=True)

# --- 8. TRANG LUYỆN THI (AUTO CHẠY LUÔN & FIX ẢNH) ---
def render_exam_page():
    if st.button("🏠 Về Trang Chủ"): st.session_state.page = "home"; st.rerun()
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Thiếu dữ liệu!"); return
    total = len(all_qs)

    # ĐIỀU HƯỚNG TRÊN
    st.write("---")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("⬅️ Câu trước"): st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with c2:
        new_q = st.number_input("Nhảy tới câu:", 1, total, st.session_state.current_q_index + 1)
        if new_q - 1 != st.session_state.current_q_index: st.session_state.current_q_index = new_q - 1; st.rerun()
    with c3:
        if st.button("Tiếp theo ➡️"): st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

    auto_mode = st.toggle("🚀 CHẾ ĐỘ AUTO (Chạy liên tục - Tự chọn đúng)", key="auto")
    delay = st.slider("Giây chờ qua câu:", 1, 5, 2)

    q = all_qs[st.session_state.current_q_index]
    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    st.info(f"**{q['question']}**")
    
    # Fix dính ảnh câu 1 (Chỉ hiện ảnh nếu không phải là ảnh mẹo)
    current_img = q.get('image')
    if current_img:
        # Nếu là câu 1, kiểm tra kỹ hơn
        if st.session_state.current_q_index == 0:
             # Nếu tên ảnh là "1" hoặc chứa chữ "tip" thì bỏ qua
             if current_img != "1" and "tip" not in str(current_img):
                 img = load_image_smart(current_img, ["images", "images_a1"])
                 if img: st.image(img)
        else:
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
