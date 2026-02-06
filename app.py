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
    initial_sidebar_state="expanded"
)

# --- 2. KHỞI TẠO STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "home"
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Xe máy (A1, A2)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0

# --- 3. CSS GIAO DIỆN (ĐẸP - MƯỢT - HIỆN ĐẠI) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    
    /* Cấu hình chung */
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: #1e293b; }
    .stApp { background-color: #f1f5f9; }
    
    /* Sidebar đẹp hơn */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e2e8f0;
    }

    /* Container chính */
    .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 5rem !important; 
        max-width: 1100px;
    }

    /* CARD TRANG CHỦ GRADIENT */
    .hero-card {
        background: linear-gradient(135deg, #2563eb 0%, #4f46e5 100%);
        padding: 40px; border-radius: 24px; 
        color: white; text-align: center; margin-bottom: 30px;
        box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.4);
    }
    .hero-title { font-size: 2.5rem; font-weight: 800; letter-spacing: -1px; margin-bottom: 10px; }
    .hero-sub { font-size: 1.2rem; font-weight: 500; opacity: 0.9; }

    /* CARD MẸO (TIP BOX) */
    .tip-card {
        background: white; 
        padding: 20px; 
        border-radius: 16px;
        border-left-width: 6px; 
        border-left-style: solid;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        margin-bottom: 15px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .tip-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .tip-header { font-size: 1.3rem; font-weight: 800; color: #334155; margin-bottom: 8px; display: flex; align-items: center; gap: 8px;}
    .tip-body { font-size: 1.15rem; line-height: 1.7; color: #475569; }

    /* Highlight Text */
    .hl-box { padding: 2px 8px; border-radius: 6px; font-weight: 700; font-size: 0.9em; }
    .hl-red { color: #dc2626; background: #fef2f2; border: 1px solid #fecaca; }
    .hl-blue { color: #2563eb; background: #eff6ff; border: 1px solid #bfdbfe; }
    .hl-green { color: #16a34a; background: #f0fdf4; border: 1px solid #bbf7d0; }
    
    /* Nút bấm (Button) */
    div[data-testid="stButton"] button {
        border-radius: 12px; font-weight: 700; height: 3.5rem; 
        border: none; box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }
    div[data-testid="stButton"] button:hover {
        transform: scale(1.02); box-shadow: 0 5px 10px rgba(0,0,0,0.1);
    }

    /* Radio Button (Đáp án) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 1px solid #cbd5e1; padding: 15px !important;
        border-radius: 12px; margin-bottom: 8px; transition: all 0.2s;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #2563eb; background: #f8fafc;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.3rem !important; font-weight: 600 !important; color: #1e293b;
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
    st.markdown("""
    <div class="hero-card">
        <div class="hero-title">🚗 GPLX MASTER PRO</div>
        <div class="hero-sub">Hệ thống ôn thi thông minh - Cập nhật 2026</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_xm, col_ot = st.columns(2)
    with col_xm:
        st.markdown('<h3 style="text-align:center; color:#0f172a;">🛵 XE MÁY (A1, A2)</h3>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc", use_container_width=True, key="xm1"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết", use_container_width=True, key="xm2"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Thi Thử Ngay", use_container_width=True, key="xm3"):
            st.session_state.license_type = "Xe máy (A1, A2)"; st.session_state.page = "exam"; st.rerun()

    with col_ot:
        st.markdown('<h3 style="text-align:center; color:#0f172a;">🚗 Ô TÔ (B, C, D)</h3>', unsafe_allow_html=True)
        if st.button("🚀 Mẹo Cấp Tốc", use_container_width=True, key="ot1"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "captoc"; st.rerun()
        if st.button("📖 Mẹo Chi Tiết", use_container_width=True, key="ot2"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "tips"; st.rerun()
        if st.button("📝 Thi Thử Ngay", use_container_width=True, key="ot3"):
            st.session_state.license_type = "Ô tô (B1, B2, C...)"; st.session_state.page = "exam"; st.rerun()

# --- 6. TRANG MẸO CẤP TỐC (CÓ TÌM KIẾM & GIAO DIỆN ĐẸP) ---
def render_captoc_page():
    # Sidebar
    with st.sidebar:
        if st.button("🏠 Về Trang Chủ", use_container_width=True):
            st.session_state.page = "home"; st.rerun()
        st.markdown("### 💡 Hướng dẫn")
        st.info("Nhập từ khóa vào ô tìm kiếm để lọc nhanh mẹo bạn cần. Ví dụ: 'tuổi', 'tốc độ', 'biển báo'...")

    st.markdown(f'<h2 style="color:#1e40af; border-bottom: 3px solid #3b82f6; padding-bottom:10px;">⚡ MẸO CẤP TỐC: {st.session_state.license_type}</h2>', unsafe_allow_html=True)
    
    # --- DỮ LIỆU MẸO (FULL) ---
    tips_data = {
        "🔢 SỐ - TUỔI - ĐUA": [
            {
                "title": "🏍️ Mẹo Đua Xe (Mới)",
                "color": "#8b5cf6", # Tím
                "content": """• Lấy bánh xe cuối cùng <b>TRỪ 1</b> ➡ Ra đáp án.<br>• <i>Ví dụ:</i> Xe ô tô (4 bánh): 4 - 1 = <span class='hl-box hl-blue'>3</span> (Chọn ý 3).""",
                "images": ["tip_duaxe"]
            },
            {
                "title": "🎂 Mẹo Độ Tuổi",
                "color": "#3b82f6", # Xanh dương
                "content": """👉 Nhìn 3 đáp án đầu, chọn số <span class='hl-box hl-red'>LỚN NHẤT</span>.<br>Ví dụ: 18, 21, 24 ➡ Chọn <b>24</b>.""",
                "images": ["tip_tuoi"]
            },
            {
                "title": "🆔 Mẹo Hạng Xe",
                "color": "#3b82f6",
                "content": """• Hỏi <b>"B1, C1, D1, D2"</b> ➡ Lấy số + 1 = Đáp án.<br>
                              • Hỏi <b>"A, B, C, D"</b> (không số) ➡ Chọn đáp án <b>cuối</b>.<br>
                              • Hỏi <b>"BE, CE, DE"</b> ➡ Bỏ E, tìm đáp án có chữ cái <b>B, C, D</b>.<br>
                              • <b>Niên hạn:</b> Xe tải 25 năm | Xe khách 20 năm.""",
                "images": ["tip_hang"]
            }
        ],
        "🏎️ TỐC ĐỘ & KHOẢNG CÁCH": [
            {
                "title": "🏎️ Tốc độ Khu Dân Cư",
                "color": "#f59e0b", # Cam
                "content": """• Đường <b>ĐÔI</b> (Có giải phân cách): <span class='hl-box hl-blue'>60 km/h</span>.<br>
                              • Đường <b>2 CHIỀU</b> (Không giải phân cách): <span class='hl-box hl-blue'>50 km/h</span>.""",
                "images": ["tip_tocdo"]
            },
            {
                "title": "📏 Khoảng cách an toàn",
                "color": "#f59e0b",
                "content": """• <b>Mẹo Trừ 30:</b> Lấy Vận tốc lớn nhất <span class='hl-box hl-red'>TRỪ 30</span> ➡ Ra đáp án gần đúng nhất.""",
                "images": []
            }
        ],
        "🛑 BIỂN BÁO - KỸ THUẬT - LÀN": [
            {
                "title": "🛣️ Mẹo Đi Đúng Làn (Cộng 1)",
                "color": "#10b981", # Xanh lá
                "content": """• Thấy <b>"làn đường 1"</b> ➡ Ta <b>+1</b> ➡ Chọn ý <span class='hl-box hl-green'>2</span>.<br>
                              • Thấy <b>"làn đường 2"</b> ➡ Ta <b>+1</b> ➡ Chọn ý <span class='hl-box hl-green'>3</span>.""",
                "images": []
            },
            {
                "title": "🛑 Mẹo 3 Biển Tròn (Đỏ & Xanh)",
                "color": "#ef4444", # Đỏ
                "content": """<b>1. Gặp 3 biển tròn ĐỎ:</b><br>• Có từ <b>"hai bánh"</b> ➡ Chọn ý <span class='hl-box hl-red'>2</span>.<br>• Không có ➡ Chọn ý <span class='hl-box hl-red'>1</span>.<br>
                              <b>2. Gặp 3 biển tròn XANH:</b><br>• Có từ <b>"ngã ba, ngã tư"</b> ➡ Chọn ý <span class='hl-box hl-red'>3</span>.<br>• Không có ➡ Chọn ý <span class='hl-box hl-red'>1</span>.""",
                "images": []
            },
            {
                "title": "⚙️ Kỹ Thuật & Từ Khóa",
                "color": "#f97316", # Cam đậm
                "content": """• Câu hỏi có từ <b>"số tự động"</b> ➡ Luôn chọn ý <span class='hl-box hl-red'>1</span>.<br>
                              • Cuối câu có từ <b>"Kéo"</b> ➡ Chọn ý <b>2</b> hoặc <b>3</b>.<br>
                              • Cuối câu có từ <b>"Móc"</b> ➡ Chọn ý <b>1</b> hoặc <b>2</b>.<br>
                              • <b>Lên cầu - Xuống hầm:</b> Về số thấp (số 1).""",
                "images": ["tip_cau_ham", "tip_mooc"]
            },
            {
                "title": "🛑 Cấm, Được & Dừng Đỗ",
                "color": "#ef4444",
                "content": """• <b>Mô tô & Ô tô đi cùng:</b> Cấm chọn <b>1</b>, Được chọn <b>3</b>.<br>
                              • <b>Biển cấm Luật định/STOP:</b> Có "Cấm" chọn <b>1</b>, còn lại chọn <b>2</b>.<br>
                              • <b>Dừng Đỗ:</b> 1 gạch (/) chọn <b>3</b>, 2 gạch (X) chọn <b>4</b>.""",
                "images": ["tip_bienbao"]
            }
        ],
        "🚔 SA HÌNH & QUAN": [
            {
                "title": "👮 Mẹo Quan Lớn - Quan Bé",
                "color": "#10b981",
                "content": """• Gặp câu hỏi có <b>2, 3 xe Quan</b> (Công an, Quân sự...):<br>• Ưu tiên chọn đáp án có từ <span class='hl-box hl-green'>"Cả"</span>.""",
                "images": []
            },
            {
                "title": "👮 Sa Hình & Nhường Đường",
                "color": "#10b981",
                "content": """• <b>Nhường đường:</b> 1 Khách ➡ 2 Bạn ➡ 3 Con.<br>
                              • <b>CSGT dang 2 tay:</b> Chọn ý <span class='hl-box hl-red'>4</span>.<br>
                              • <b>CSGT giơ tay</b> (hoặc còn lại): Chọn ý <span class='hl-box hl-red'>3</span>.<br>
                              • <b>Xe Mô tô:</b> Đường thẳng chọn <b>2</b>, đường nằm ngang chọn <b>3</b>.<br>
                              • <b>Áo xanh/đỏ:</b> Xe máy xanh chọn <b>1</b>, Ô tô đỏ chọn <b>3</b>.<br>
                              • <b>Quy tắc 1-1-2-4:</b> Nhất chớm - Nhì ưu - Tam đường - Tứ hướng.""",
                "images": ["tip_sahinh"]
            }
        ]
    }

    # --- CHỨC NĂNG TÌM KIẾM ---
    search_term = st.text_input("🔍 Tìm kiếm mẹo (Ví dụ: tuổi, tốc độ, cấm...)", "").lower()
    
    if search_term:
        st.write(f"Kết quả tìm kiếm cho: **{search_term}**")
        found = False
        folders = ["images", "images_a1"]
        # Duyệt qua tất cả các mục để tìm kiếm
        for category, items in tips_data.items():
            for tip in items:
                if search_term in tip['title'].lower() or search_term in tip['content'].lower():
                    found = True
                    # Hiển thị thẻ kết quả
                    with st.expander(f"{tip['title']} (Trong mục {category})", expanded=True):
                        st.markdown(f"""
                        <div class="tip-card" style="border-left-color: {tip['color']};">
                            <div class="tip-body">{tip['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        if tip["images"]:
                            all_imgs = []
                            for prefix in tip["images"]: all_imgs.extend(load_multiple_images(prefix, folders))
                            if all_imgs:
                                cols = st.columns(min(len(all_imgs), 3))
                                for idx, img in enumerate(all_imgs):
                                    with cols[idx % 3]: st.image(img, use_container_width=True)
        if not found:
            st.warning("Không tìm thấy mẹo nào khớp với từ khóa.")

    else:
        # --- HIỂN THỊ DẠNG TAB (MẶC ĐỊNH) ---
        tabs = st.tabs(list(tips_data.keys()))
        folders = ["images", "images_a1"]

        for i, (tab_name, tips) in enumerate(tips_data.items()):
            with tabs[i]:
                for tip in tips:
                    # Thiết kế Card đẹp mắt
                    with st.expander(tip["title"], expanded=True):
                        st.markdown(f"""
                        <div class="tip-card" style="border-left-color: {tip['color']};">
                            <div class="tip-body">{tip['content']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Hiển thị ảnh
                        if tip["images"]:
                            all_imgs = []
                            for prefix in tip["images"]:
                                all_imgs.extend(load_multiple_images(prefix, folders))
                            
                            if all_imgs:
                                cols = st.columns(len(all_imgs)) if len(all_imgs) > 1 and len(all_imgs) <= 3 else [st]
                                for idx, img in enumerate(all_imgs):
                                    if len(all_imgs) > 1 and len(all_imgs) <=3:
                                        with cols[idx]: st.image(img, use_container_width=True)
                                    else:
                                        st.image(img, use_container_width=True)

# --- 7. TRANG MẸO CHI TIẾT ---
def render_tips_page():
    with st.sidebar:
        if st.button("🏠 Về Trang Chủ", use_container_width=True):
            st.session_state.page = "home"; st.rerun()
            
    st.markdown(f'<div class="section-title">📖 Mẹo Chi Tiết: {st.session_state.license_type}</div>', unsafe_allow_html=True)
    data = load_data_by_license(st.session_state.license_type)
    if not data: st.warning("Chưa có dữ liệu."); return
    
    cats = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Lọc theo chủ đề:", ["Tất cả"] + cats)
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]
    
    for tip in items:
        with st.expander(f"📌 {tip.get('title', 'Mẹo')}"):
            for line in tip.get('content', []):
                st.write(f"• {line}")
            if tip.get('image'):
                img = load_image_smart(tip['image'], ["images", "images_a1"])
                if img: st.image(img)

# --- 8. TRANG LUYỆN THI (AUTO) ---
def render_exam_page():
    with st.sidebar:
        if st.button("🏠 Về Trang Chủ", use_container_width=True):
            st.session_state.page = "home"; st.rerun()
        st.write("---")
        auto_mode = st.toggle("🚀 AUTO CHẠY LUÔN", key="auto")
        delay = st.slider("Tốc độ (s):", 1, 5, 2)

    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs: st.error("Lỗi dữ liệu!"); return
    total = len(all_qs)

    # Thanh điều hướng
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Trước", use_container_width=True): 
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1); st.rerun()
    with c2:
        st.markdown(f"<h3 style='text-align: center; margin:0'>Câu {st.session_state.current_q_index + 1} / {total}</h3>", unsafe_allow_html=True)
    with c3:
        if st.button("Tiếp ➡️", use_container_width=True): 
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1); st.rerun()

    st.progress((st.session_state.current_q_index + 1) / total)

    q = all_qs[st.session_state.current_q_index]
    st.info(f"**{q['question']}**")
    
    # Fix ảnh câu 1
    current_img = q.get('image')
    if current_img:
        if not (st.session_state.current_q_index == 0 and ("tip" in str(current_img) or current_img == "1")):
            img = load_image_smart(current_img, ["images", "images_a1"])
            if img: st.image(img)

    correct_ans = q['correct_answer'].strip()
    options = q['options']
    correct_idx = [i for i, opt in enumerate(options) if opt.strip() == correct_ans][0]

    user_choice = st.radio("Chọn đáp án:", options, index=correct_idx if auto_mode else None, key=f"r_{st.session_state.current_q_index}")

    if user_choice:
        if user_choice.strip() == correct_ans:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #dcfce7 !important; border: 2px solid #16a34a !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: #14532d !important; font-weight: 700 !important; }</style>""", unsafe_allow_html=True)
            st.success("✅ CHÍNH XÁC!")
        else:
            st.markdown("""<style>div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] { background-color: #fee2e2 !important; border: 2px solid #dc2626 !important; } div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] p { color: #7f1d1d !important; font-weight: 700 !important; }</style>""", unsafe_allow_html=True)
            st.error(f"❌ SAI! Đáp án là: {correct_ans}")

        if auto_mode:
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
