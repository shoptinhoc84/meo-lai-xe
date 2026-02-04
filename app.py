import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX - Lọc Theo Chủ Đề",
    page_icon="🚗",
    layout="wide"
)

# --- 2. KHỞI TẠO STATE ---
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
# Lưu chủ đề đang chọn để reset câu hỏi khi đổi chủ đề
if 'exam_category' not in st.session_state:
    st.session_state.exam_category = "Tất cả"

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    .tip-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    .question-box {
        background-color: #f8f9fa; border-radius: 10px; padding: 25px;
        border-left: 6px solid #007bff; margin-bottom: 20px;
    }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    
    /* Giao diện nút chọn đáp án */
    div[data-testid="stRadio"] > label { display: none; }
    div[data-testid="stRadio"] div[role="radiogroup"] { gap: 10px; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 12px 15px;
        border-radius: 8px;
        width: 100%;
        display: flex;
        align-items: center;
        cursor: pointer;
        transition: all 0.2s;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #007bff;
        background-color: #f0f7ff;
    }
    div[data-testid="stImage"] { display: flex; justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

@st.cache_data
def load_json_file(filename):
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        return None

def load_data_by_license(license_type):
    is_oto = "Ô tô" in license_type
    files_oto = ['data.json', 'data (6).json']
    files_xe_may = ['tips_a1.json', 'tips_a1 (1).json']
    target_files = files_oto if is_oto else files_xe_may
    
    for fname in target_files:
        data = load_json_file(fname)
        if data: return data
    return []

def load_image_strict(image_name, folders_allowed):
    if not image_name: return None
    img_name = str(image_name).strip()
    
    for folder in folders_allowed:
        path = os.path.join(folder, img_name)
        if os.path.exists(path) and os.path.isfile(path):
            try:
                img = Image.open(path)
                return ImageOps.exif_transpose(img)
            except: continue
    return None

# --- 5. GIAO DIỆN HỌC MẸO ---
def render_tips_page(license_type):
    st.header(f"📖 Mẹo Thi Lý Thuyết {license_type}")
    data = load_data_by_license(license_type)
    if not data:
        st.warning("Chưa tìm thấy dữ liệu mẹo.")
        return

    categories = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Chọn chủ đề:", ["Tất cả"] + categories)
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    for tip in items:
        st.markdown(f'<div class="tip-card"><h3>📌 {tip.get("title", "Mẹo")}</h3>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.5, 1])
        with c1:
            for line in tip.get('content', []):
                if "=>" in line:
                    p = line.split("=>")
                    line = f"{p[0]} => <span class='highlight'>{p[1]}</span>"
                st.markdown(f"• {line}", unsafe_allow_html=True)
        with c2:
            if tip.get('image'):
                folders = ["images", "images_a1"] if "Ô tô" in license_type else ["images_a1", "images"]
                img = load_image_strict(tip['image'], folders)
                if img: st.image(img, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. GIAO DIỆN LUYỆN THI (ĐÃ CÓ LỌC CHỦ ĐỀ) ---
def render_exam_page():
    st.header("📝 Luyện Tập 600 Câu Hỏi")
    all_questions = load_json_file('dulieu_600_cau.json')
    if not all_questions:
        st.error("Lỗi file dữ liệu 600 câu.")
        return

    # 1. LẤY DANH SÁCH CHỦ ĐỀ TỪ DỮ LIỆU
    categories = sorted(list(set([q.get('category', 'Khác') for q in all_questions])))
    
    # 2. THANH CHỌN CHỦ ĐỀ
    # Sử dụng columns để để selectbox gọn hơn
    col_cat, col_info = st.columns([1, 2])
    with col_cat:
        selected_cat = st.selectbox("📂 Chọn chủ đề ôn tập:", ["Tất cả"] + categories)
    
    # Xử lý khi đổi chủ đề -> Reset về câu đầu tiên
    if selected_cat != st.session_state.exam_category:
        st.session_state.exam_category = selected_cat
        st.session_state.current_q_index = 0
        st.rerun()

    # 3. LỌC CÂU HỎI
    if selected_cat == "Tất cả":
        filtered_questions = all_questions
    else:
        filtered_questions = [q for q in all_questions if q.get('category') == selected_cat]

    if not filtered_questions:
        st.warning(f"Không có câu hỏi nào trong chủ đề '{selected_cat}'")
        return

    total = len(filtered_questions)
    
    # Đảm bảo index không vượt quá giới hạn (trường hợp danh sách lọc ngắn hơn index cũ)
    if st.session_state.current_q_index >= total:
        st.session_state.current_q_index = 0

    # 4. ĐIỀU HƯỚNG
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Câu trước", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.rerun()
    with c3:
        if st.button("Câu sau ➡️", use_container_width=True):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.rerun()
    with c2:
        val = st.number_input("Câu số:", 1, total, st.session_state.current_q_index + 1)
        if val - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = val - 1
            st.rerun()

    # Lấy câu hỏi từ danh sách ĐÃ LỌC
    q = filtered_questions[st.session_state.current_q_index]
    
    with col_info:
        # Hiển thị thông tin thống kê nhỏ bên cạnh selectbox
        st.info(f"Đang xem: **{selected_cat}** ({total} câu)")

    st.markdown(f"""
    <div class="question-box">
        <div style="color:#666; font-size: 0.9em; display:flex; justify-content:space-between;">
            <span>Câu {st.session_state.current_q_index + 1} / {total}</span>
            <span style="background:#e9ecef; padding:2px 8px; border-radius:4px;">{q.get('category','Chung')}</span>
        </div>
        <div style="font-size: 1.15em; font-weight: 600; margin-top: 10px;">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # --- FIX ẢNH CÂU 1 (GIỮ NGUYÊN) ---
    if q['id'] == 1:
        q['image'] = None

    if q.get('image'):
        img = load_image_strict(q['image'], folders_allowed=['images'])
        if img:
            st.image(img, width=500)
    # -----------------------------------

    st.write("---")
    
    # RADIO BUTTON CHỌN ĐÁP ÁN (HIỆN KẾT QUẢ NGAY)
    # Lưu ý: key phải là duy nhất, kết hợp cả id câu hỏi để tránh lỗi khi chuyển câu
    user_choice = st.radio(
        "Chọn đáp án:", 
        q['options'], 
        index=None, 
        key=f"q_{q['id']}" 
    )

    if user_choice:
        st.write("") 
        correct = q['correct_answer'].strip()
        
        if user_choice.strip() == correct:
            st.success(f"🎉 CHÍNH XÁC! Đáp án: {correct}")
        else:
            st.error(f"❌ SAI RỒI! Đáp án đúng là: {correct}")

# --- 7. MAIN APP ---
def main():
    with st.sidebar:
        st.title("🚗 MENU ÔN TẬP")
        st.divider()
        license = st.selectbox("Chọn hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license != st.session_state.license_type:
            st.session_state.license_type = license
            st.session_state.current_q_index = 0
            st.cache_data.clear()
            st.rerun()

        mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        st.divider()
        if st.button("🔄 Làm mới / Xóa Cache"):
            st.cache_data.clear()
            st.rerun()

    if mode == "📖 Học Mẹo":
        render_tips_page(st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
