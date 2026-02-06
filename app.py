import streamlit as st
import json
import os
import time
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Full Mẹo 2026",
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

# --- 3. CSS GIAO DIỆN ---
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

    /* TIP BOX */
    .tip-box {
        background: white; border-radius: 18px; padding: 25px; margin-bottom: 20px;
        border-left: 12px solid #3b82f6; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.08);
    }
    .tip-title { color: #1e293b; font-weight: 800; font-size: 1.8rem; margin-bottom: 15px; text-transform: uppercase; }
    .tip-content { color: #334155; font-size: 1.5rem; line-height: 1.7; font-weight: 500; }
    
    .hl-red { color: #e11d48; font-weight: 800; background: #fff1f2; padding: 2px 8px; border-radius: 8px; }
    .hl-blue { color: #2563eb; font-weight: 800; background: #eff6ff; padding: 2px 8px; border-radius: 8px; }

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
    images = []
    for folder in folders:
        if not os.path.exists(folder): continue
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
    st.markdown('<div class="hero-card"><h1>🚗 GPLX MASTER PRO</h1><p style="font-size:1.4rem">Ôn thi cấp tốc - Đậu ngay lần đầu</p></div>', unsafe_allow_html=True)
    col_xm, col_ot = st.columns(2)

    with col_xm:
        st.markdown('<div class="section-title">🛵 XE MÁY (A1, A2)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Xe Máy", use_container_width=True, key="xm_cap"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Xe Máy", use_container_width=True, key="xm_tip"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Xe Máy", use_container_width=True, key="xm_exam"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "exam"; st.rerun()

    with col_ot:
        st.markdown('<div class="section-title">🚗 Ô TÔ (B1, B2, C)</div>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc Ô Tô", use_container_width=True, key="ot_cap"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết Ô Tô", use_container_width=True, key="ot_tip"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Luyện Thi Ô Tô", use_container_width=True, key="ot_exam"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC (FULL) ---
def render_captoc_page():
    if st.button("🏠 VỀ TRANG CHỦ"): st.session_state.page = "home"; st.rerun()
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    
    # Chia tab
    tab1, tab2, tab3, tab4 = st.tabs(["🔢 SỐ, TUỔI & ĐUA", "🏎️ TỐC ĐỘ", "🛑 BIỂN BÁO, KT & LÀN", "🚔 SA HÌNH & NHƯỜNG"])
    folders = ["images", "images_a1"]

    # TAB 1: TUỔI - HẠNG - ĐUA XE
    with tab1:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #8b5cf6;">
            <div class="tip-title">🏍️ Mẹo Đua Xe (Mới)</div>
            <div class="tip-content">
            • Lấy bánh xe cuối cùng <b>TRỪ 1</b> ➡ Ra đáp án.<br>
            • <i>Ví dụ:</i> Xe ô tô (4 bánh): 4 - 1 = <b>3</b> (Chọn ý 3).
            </div>
        </div>
        <div class="tip-box">
            <div class="tip-title">🎂 Mẹo Độ Tuổi</div>
            <div class="tip-content">👉 Nhìn 3 đáp án đầu, chọn số <span class="highlight-red">LỚN NHẤT</span>.<br>Ví dụ: 18, 21, 24 ➡ Chọn <b>24</b>.</div>
        </div>
        <div class="tip-box" style="border-left-color: #8b5cf6;">
            <div class="tip-title">🆔 Mẹo Hạng Xe</div>
            <div class="tip-content">
            • Hỏi <b>"B1, C1, D1, D2"</b> ➡ Lấy số + 1 = Đáp án.<br>
            • Hỏi <b>"A, B, C, D"</b> (không số) ➡ Chọn đáp án <b>cuối</b>.<br>
            • Hỏi <b>"BE, CE, DE"</b> ➡ Bỏ E, tìm đáp án có chữ cái <b>B, C, D</b>.<br>
            • <b>Niên hạn:</b> Xe tải 25 năm | Xe khách 20 năm.
            </div>
        </div>
        """, unsafe_allow_html=True)
        imgs = load_multiple_images("tip_tuoi", folders) + load_multiple_images("tip_hang", folders) + load_multiple_images("tip_duaxe", folders)
        for img in imgs: st.image(img, use_container_width=True)

    # TAB 2: TỐC ĐỘ
    with tab2:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #f59e0b;">
            <div class="tip-title">🏎️ Tốc độ & Khoảng cách</div>
            <div class="tip-content">
            • Đường <b>ĐÔI</b> (Có giải phân cách): <span class="highlight-blue">60 km/h</span>.<br>
            • Đường <b>2 CHIỀU</b> (Không giải phân cách): <span class="highlight-blue">50 km/h</span>.<br>
            • <b>Khoảng cách:</b> Lấy V(max) <span class="highlight-red">TRỪ 30</span> ➡ Ra đáp án.
            </div>
        </div>
        """, unsafe_allow_html=True)
        imgs = load_multiple_images("tip_tocdo", folders)
        for img in imgs: st.image(img, use_container_width=True)

    # TAB 3: BIỂN BÁO - KỸ THUẬT - LÀN - KÉO/MÓC
    with tab3:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #f97316;">
            <div class="tip-title">⚙️ Mẹo Kỹ Thuật & Từ Khóa</div>
            <div class="tip-content">
            • Câu hỏi có từ <b>"số tự động"</b> ➡ Luôn chọn ý <span class="highlight-red">1</span>.<br>
            • Cuối câu có từ <b>"Kéo"</b> ➡ Chọn ý <b>2</b> hoặc <b>3</b>.<br>
            • Cuối câu có từ <b>"Móc"</b> ➡ Chọn ý <b>1</b> hoặc <b>2</b>.<br>
            • <b>Lên cầu - Xuống hầm:</b> Về số thấp (số 1).
            </div>
        </div>
        <div class="tip-box" style="border-left-color: #10b981;">
            <div class="tip-title">🛣️ Mẹo Đi Đúng Làn (Cộng 1)</div>
            <div class="tip-content">
            • Câu hỏi có chữ <b>"làn đường 1"</b> (làn dòng 1) ➡ Ta <b>+1</b> ➡ Chọn ý <b>2</b>.<br>
            • Câu hỏi có chữ <b>"làn đường 2"</b> (làn dòng 2) ➡ Ta <b>+1</b> ➡ Chọn ý <b>3</b>.
            </div>
        </div>
        <div class="tip-box" style="border-left-color: #ef4444;">
            <div class="tip-title">🛑 Mẹo Biển Báo Cấm & Được</div>
            <div class="tip-content">
            <b>1. Mô tô & Ô tô đi cùng nhau:</b><br>
            • Có từ <b>"Cấm"</b> ➡ Chọn ý <span class="highlight-red">1</span>.<br>
            • Có từ <b>"Được"</b> ➡ Chọn ý <span class="highlight-red">3</span>.<br><br>
            <b>2. Cấm Mô tô & Cấm xe cơ giới:</b><br>
            • Hỏi <b>"Cấm"</b> ➡ Chọn ý <span class="highlight-red">1</span>.<br>
            • Hỏi <b>"Được"</b> ➡ Chọn ý <span class="highlight-red">3</span>.<br><br>
            <b>3. Biển cấm Luật định và STOP:</b><br>
            • Có từ <b>"Cấm"</b> ➡ Chọn ý <b>1</b>. | Còn lại ➡ Chọn ý <b>2</b>.
            </div>
        </div>
        <div class="tip-box" style="border-left-color: #ef4444;">
            <div class="tip-title">🛑 Dừng Đỗ & Cấm Moóc</div>
            <div class="tip-content">
            • 1 gạch (/) ➡ Cấm Đỗ ➡ Chọn <b>3</b>.<br>
            • 2 gạch (X) ➡ Cấm Dừng & Đỗ ➡ Chọn <b>4</b>.<br>
            • Cấm Máy kéo (không cấm Moóc). Cấm Moóc (cấm luôn Máy kéo).
            </div>
        </div>
        """, unsafe_allow_html=True)
        imgs = load_multiple_images("tip_bienbao", folders) + load_multiple_images("tip_cau_ham", folders) + load_multiple_images("tip_mooc", folders)
        for img in imgs: st.image(img, use_container_width=True)

    # TAB 4: SA HÌNH
    with tab4:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #10b981;">
            <div class="tip-title">👮 Mẹo Sa Hình & Nhường Đường</div>
            <div class="tip-content">
            • <b>Mẹo Nhường:</b> Thứ tự ưu tiên chọn đáp án: <b>1 Khách ➡ 2 Bạn ➡ 3 Con</b>.<br>
            &nbsp;&nbsp;<i>(Thần chú: Khách - Bạn - Con)</i><br>
            • <b>CSGT dang 2 tay</b> (đứng trên bục): Chọn ý <span class="highlight-red">4</span>.<br>
            • <b>CSGT giơ tay</b> (hoặc còn lại): Chọn ý <span class="highlight-red">3</span>.<br>
            • <b>Xe Mô tô:</b> Đường thẳng chọn <b>2</b>, đường nằm ngang chọn <b>3</b>.<br>
            • <b>Áo xanh/đỏ:</b> Xe gắn máy áo xanh chọn <b>1</b>, Ô tô áo đỏ chọn <b>3</b>.<br>
            • <b>Quy tắc 1-1-2-4:</b> Nhất chớm - Nhì ưu - Tam đường - Tứ hướng.
            </div>
        </div>
        """, unsafe_allow_html=True)
        imgs = load_multiple_images("tip_sahinh", folders)
        if imgs:
            cols = st.columns(2)
            for i, img in enumerate(imgs):
                with cols[i % 2]: st.image(img, use_container_width=True)

# --- 7. TRANG MẸO CHI TIẾT ---
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

# --- 8. TRANG LUYỆN THI ---
def render_exam_page():
    if st.button("🏠 VỀ TRANG CHỦ"): st.session_state.page = "home"; st.rerun()
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Lỗi dữ liệu!"); return
    total = len(all_qs)

    st.write("---")
    c1, c2, c3 = st.columns([1, 1, 1])
    with c1:
        if st.button("⬅️ Trước"): st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with c2:
        new_q = st.number_input("Câu:", 1, total, st.session_state.current_q_index + 1)
        if new_q - 1 != st.session_state.current_q_index: st.session_state.current_q_index = new_q - 1; st.rerun()
    with c3:
        if st.button("Tiếp ➡️"): st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

    auto_mode = st.toggle("🚀 AUTO CHẠY LUÔN", key="auto")
    delay = st.slider("Tốc độ:", 1, 5, 2)

    q = all_qs[st.session_state.current_q_index]
    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    st.info(f"**{q['question']}**")
    
    current_img = q.get('image')
    if current_img:
        # Lọc bỏ ảnh mẹo nếu dính vào câu 1
        if not (st.session_state.current_q_index == 0 and ("tip" in str(current_img) or current_img == "1")):
            img = load_image_smart(current_img, ["images", "images_a1"])
            if img: st.image(img)

    correct_ans = q['correct_answer'].strip()
    options = q['options']
    correct_idx = [i for i, opt in enumerate(options) if opt.strip() == correct_ans][0]

    user_choice = st.radio("Chọn:", options, index=correct_idx if auto_mode else None, key=f"r_{st.session_state.current_q_index}")

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
                st.write(f"⏳ Qua câu sau {delay}s...")
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
