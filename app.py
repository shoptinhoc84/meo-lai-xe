import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG (Full Width) ---
st.set_page_config(
    page_title="GPLX Master - Giao Diện App",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed" # Ẩn sidebar mặc định trên mobile cho rộng
)

# --- 2. KHỞI TẠO STATE ---
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'exam_category' not in st.session_state:
    st.session_state.exam_category = "Tất cả"

# --- 3. CSS TỐI ƯU UI/UX (MOBILE FIRST) ---
st.markdown("""
<style>
    /* 1. TỔNG THỂ */
    .stApp {
        background-color: #f8f9fa; /* Màu nền xám giấy dịu mắt */
    }
    
    /* 2. THANH ĐIỀU HƯỚNG CỐ ĐỊNH Ở DƯỚI (STICKY FOOTER) */
    .sticky-nav {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background: white;
        padding: 15px 20px;
        box-shadow: 0 -4px 10px rgba(0,0,0,0.1);
        z-index: 999;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-top: 1px solid #dee2e6;
    }
    /* Đẩy nội dung lên để không bị thanh điều hướng che mất */
    .block-container {
        padding-bottom: 100px !important; 
    }

    /* 3. THẺ CÂU HỎI */
    .question-card {
        background: white;
        padding: 25px;
        border-radius: 16px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
        border: 1px solid #edf2f7;
        margin-bottom: 20px;
    }
    .q-badge {
        background: #e3f2fd;
        color: #1565c0;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        display: inline-block;
        margin-bottom: 10px;
    }
    .q-text {
        font-size: 1.35rem;
        font-weight: 600;
        color: #2d3748;
        line-height: 1.6;
    }

    /* 4. ĐÁP ÁN DẠNG THẺ (BIG TOUCH TARGET) */
    div[data-testid="stRadio"] > label { display: none; }
    div[role="radiogroup"] { gap: 12px; display: flex; flex-direction: column; }
    
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: white;
        border: 2px solid #e2e8f0;
        padding: 16px 20px; /* Vùng bấm lớn */
        border-radius: 12px;
        width: 100%;
        cursor: pointer;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        display: flex;
        align-items: center;
        font-size: 1.05rem;
        color: #4a5568;
    }
    
    /* Hiệu ứng Hover & Selected */
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #3182ce;
        background-color: #ebf8ff;
        transform: translateY(-2px);
    }
    /* Khi được chọn (Streamlit tự thêm attribute này) */
    div[data-testid="stRadio"] div[role="radiogroup"] > label[data-checked="true"] {
        border-color: #3182ce !important;
        background-color: #ebf8ff !important;
        color: #2b6cb0 !important;
        font-weight: 600;
        box-shadow: 0 0 0 4px rgba(66, 153, 225, 0.2); /* Hiệu ứng focus đẹp */
    }

    /* 5. ẢNH MINH HỌA */
    div[data-testid="stImage"] {
        background: #fff;
        padding: 10px;
        border-radius: 12px;
        border: 1px solid #eee;
        margin: 15px 0;
    }
    div[data-testid="stImage"] > img {
        border-radius: 8px;
        max-height: 400px;
        object-fit: contain;
    }

    /* Nút bấm điều hướng custom */
    .nav-btn {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        border-radius: 8px;
        cursor: pointer;
        text-decoration: none;
        transition: 0.2s;
        border: none;
        width: 120px; /* Chiều rộng cố định cho đều */
    }
    .btn-prev { background: #cbd5e0; color: #4a5568; }
    .btn-next { background: #3182ce; color: white; box-shadow: 0 4px 6px rgba(49, 130, 206, 0.3); }
    .btn-next:hover { background: #2c5282; transform: translateY(-1px); }
    
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except: return None

def load_image_strict(image_name, folders_allowed):
    if not image_name: return None
    img_name = str(image_name).strip()
    for folder in folders_allowed:
        path = os.path.join(folder, img_name)
        if os.path.exists(path) and os.path.isfile(path):
            try: return ImageOps.exif_transpose(Image.open(path))
            except: continue
    return None

# --- 5. GIAO DIỆN CHÍNH ---
def render_exam_page():
    all_qs = load_json_file('dulieu_600_cau.json')
    if not all_qs:
        st.error("Lỗi dữ liệu")
        return

    # Lọc chủ đề
    categories = sorted(list(set([q.get('category', 'Khác') for q in all_qs])))
    
    # Header nhỏ gọn
    c1, c2 = st.columns([3, 1])
    with c1:
        st.markdown("### 🚦 Luyện Thi GPLX Pro")
    with c2:
        # Chọn chủ đề dạng Dropdown cho gọn trên mobile
        selected_cat = st.selectbox("Lọc chủ đề:", ["Tất cả"] + categories, label_visibility="collapsed")

    if selected_cat != st.session_state.exam_category:
        st.session_state.exam_category = selected_cat
        st.session_state.current_q_index = 0
        st.rerun()

    filtered_qs = all_qs if selected_cat == "Tất cả" else [q for q in all_qs if q.get('category') == selected_cat]
    total = len(filtered_qs)
    
    if st.session_state.current_q_index >= total: st.session_state.current_q_index = 0
    q = filtered_qs[st.session_state.current_q_index]

    # --- KHU VỰC CÂU HỎI (Card chính) ---
    st.markdown(f"""
    <div class="question-card">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <span class="q-badge">Câu {st.session_state.current_q_index + 1}/{total}</span>
            <span style="color:#718096; font-size:0.9rem;">{q.get('category','Chung')}</span>
        </div>
        <div class="q-text">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # Ảnh minh họa (Fix câu 1)
    if q['id'] == 1: q['image'] = None
    if q.get('image'):
        img = load_image_strict(q['image'], ['images'])
        if img: st.image(img, use_container_width=True) # Tự co giãn theo màn hình

    # Đáp án
    user_choice = st.radio("Chọn đáp án:", q['options'], index=None, key=f"q_{q['id']}")

    # Thông báo kết quả (Gọn gàng hơn)
    if user_choice:
        correct = q['correct_answer'].strip()
        if user_choice.strip() == correct:
            st.success(f"✅ CHÍNH XÁC: {correct}")
        else:
            st.error(f"❌ SAI: Đáp án đúng là {correct}")
            
    # --- THANH ĐIỀU HƯỚNG CỐ ĐỊNH (STICKY FOOTER) ---
    # Đây là phần quan trọng nhất để fix lỗi "mỏi tay" khi cuộn trang
    st.markdown("---") # Spacer
    st.markdown('<div style="height: 50px;"></div>', unsafe_allow_html=True) # Khoảng trống ảo

    # Sử dụng container của Streamlit để đặt nút
    # Lưu ý: Streamlit chưa hỗ trợ native sticky footer hoàn hảo, 
    # nên ta dùng columns ở cuối trang kết hợp CSS 'fixed' nếu cần, 
    # nhưng ở đây ta dùng layout chuẩn để nút luôn ở cuối cùng dễ bấm.
    
    col_nav = st.columns([1, 2, 1])
    with col_nav[0]:
        if st.button("⬅️ Trước", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.rerun()
    with col_nav[2]:
        # Nút "Sau" màu xanh nổi bật
        if st.button("Tiếp theo ➡️", type="primary", use_container_width=True):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.rerun()
    
    # Input nhảy trang nhanh (Nằm giữa)
    with col_nav[1]:
        st.markdown(
            f"<div style='text-align:center; color:#718096; padding-top:10px;'>Câu {st.session_state.current_q_index + 1}</div>", 
            unsafe_allow_html=True
        )

# --- MAIN ---
def main():
    with st.sidebar:
        st.header("⚙️ Cài Đặt")
        license = st.selectbox("Hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license != st.session_state.license_type:
            st.session_state.license_type = license
            st.session_state.current_q_index = 0
            st.cache_data.clear()
            st.rerun()
        
        mode = st.radio("Chế độ:", ["📝 Luyện Thi", "📖 Học Mẹo"])
        st.info("💡 Mẹo: Dùng giao diện này trên điện thoại sẽ giống App hơn Web.")

    if mode == "📖 Học Mẹo":
        # (Giữ nguyên code mẹo của bạn hoặc gọi hàm cũ)
        st.warning("Chuyển sang tab Luyện Thi để trải nghiệm giao diện App mới!")
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
