import streamlit as st
import json
import os
from PIL import Image, ImageOps

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX - Logic Chuẩn",
    page_icon="🚗",
    layout="wide"
)

# --- 2. KHỞI TẠO STATE (Lưu trạng thái) ---
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)"
if 'current_q_index' not in st.session_state:
    st.session_state.current_q_index = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False

# --- 3. CSS GIAO DIỆN (Đã fix lỗi lệch hàng) ---
st.markdown("""
<style>
    /* Card cho mẹo */
    .tip-card {
        background-color: #ffffff; border-radius: 12px; padding: 20px;
        margin-bottom: 20px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
        border: 1px solid #f0f0f0;
    }
    /* Box câu hỏi */
    .question-box {
        background-color: #f8f9fa; border-radius: 10px; padding: 25px;
        border-left: 6px solid #007bff; margin-bottom: 20px;
    }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    
    /* CSS CĂN CHỈNH RADIO BUTTON CHUẨN */
    div[data-testid="stRadio"] > label { display: none; } /* Ẩn label mặc định */
    div[data-testid="stRadio"] div[role="radiogroup"] { gap: 12px; }
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background-color: #ffffff;
        border: 1px solid #dee2e6;
        padding: 12px 15px;
        border-radius: 8px;
        width: 100%;
        display: flex;
        align-items: center; /* Căn giữa dọc quan trọng */
        cursor: pointer;
        transition: all 0.2s;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #007bff;
        background-color: #f0f7ff;
    }
    /* Căn giữa ảnh */
    div[data-testid="stImage"] { display: flex; justify-content: center; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

@st.cache_data
def load_json_data(filename):
    """Hàm load dữ liệu chung, xử lý lỗi nếu không thấy file"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error(f"⚠️ LỖI: Không tìm thấy file '{filename}'. Vui lòng kiểm tra lại tên file trong thư mục.")
        return []
    except Exception as e:
        st.error(f"⚠️ LỖI: File '{filename}' bị lỗi định dạng. Chi tiết: {e}")
        return []

def load_image_strict(image_name, mode="EXAM"):
    """
    Hàm load ảnh 'nghiêm ngặt'. 
    - EXAM: Chỉ tìm trong folder 'images' (cho 600 câu).
    - TIP: Chỉ tìm trong folder 'images_a1' hoặc 'images' tùy loại.
    """
    if not image_name: return None
    img_name = str(image_name).strip()
    
    # LOGIC CÁCH LY THƯ MỤC
    if mode == "EXAM":
        # CHẾ ĐỘ THI: BẮT BUỘC folder 'images'. 
        # Không tìm chỗ khác để tránh lấy nhầm ảnh mẹo.
        paths_to_check = [os.path.join("images", img_name)]
    else:
        # CHẾ ĐỘ MẸO: Ưu tiên folder a1 trước
        paths_to_check = [
            os.path.join("images_a1", img_name),
            os.path.join("images", img_name)
        ]

    for path in paths_to_check:
        if os.path.exists(path) and os.path.isfile(path):
            try:
                # Mở ảnh và xoay đúng chiều
                img = Image.open(path)
                return ImageOps.exif_transpose(img)
            except: 
                continue
    return None

# --- 5. GIAO DIỆN HỌC MẸO ---
def render_tips_page(license_type):
    is_oto = "Ô tô" in license_type
    # Tự động chọn file dựa trên loại bằng
    filename = 'data.json' if is_oto else 'tips_a1.json'
    
    st.header(f"📖 Mẹo Thi Lý Thuyết {license_type}")
    data = load_json_data(filename)
    
    if not data: return

    # Lọc danh mục
    categories = sorted(list(set([i.get('category', 'Khác') for i in data])))
    selected_cat = st.selectbox("Chọn chủ đề:", ["Tất cả"] + categories)
    items = data if selected_cat == "Tất cả" else [d for d in data if d.get('category') == selected_cat]

    for tip in items:
        # Card hiển thị
        st.markdown(f'<div class="tip-card"><h3>📌 {tip.get("title", "Mẹo")}</h3>', unsafe_allow_html=True)
        c1, c2 = st.columns([1.5, 1]) # Chia cột 60-40
        
        with c1:
            for line in tip.get('content', []):
                # Highlight từ khóa sau dấu =>
                if "=>" in line:
                    p = line.split("=>")
                    line = f"{p[0]} => <span class='highlight'>{p[1]}</span>"
                st.markdown(f"• {line}", unsafe_allow_html=True)
                
        with c2:
            if tip.get('image'):
                img = load_image_strict(tip['image'], mode="TIP")
                if img: 
                    st.image(img, use_container_width=True)
                else:
                    st.caption(f"(Thiếu ảnh minh họa: {tip['image']})")
                    
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. GIAO DIỆN LUYỆN THI (600 CÂU) ---
def render_exam_page():
    st.header("📝 Luyện Tập 600 Câu Hỏi")
    questions = load_json_data('dulieu_600_cau.json')
    
    if not questions: return

    total = len(questions)
    
    # Thanh điều hướng câu hỏi
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Câu trước", use_container_width=True):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.session_state.show_answer = False
            st.rerun()
    with c3:
        if st.button("Câu sau ➡️", use_container_width=True):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.session_state.show_answer = False
            st.rerun()
    with c2:
        # Nhập số câu để nhảy nhanh
        val = st.number_input("Nhảy tới câu số:", 1, total, st.session_state.current_q_index + 1)
        if val - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = val - 1
            st.session_state.show_answer = False
            st.rerun()

    # Lấy câu hỏi hiện tại
    q = questions[st.session_state.current_q_index]
    
    # Hiển thị nội dung câu hỏi
    st.markdown(f"""
    <div class="question-box">
        <div style="color:#666; font-size: 0.9em; margin-bottom: 5px;">Câu {q['id']} / {total}</div>
        <div style="font-size: 1.1em; font-weight: 600;">{q['question']}</div>
    </div>
    """, unsafe_allow_html=True)

    # XỬ LÝ ẢNH (Quan trọng)
    if q.get('image'):
        # Gọi chế độ EXAM để chỉ tìm trong folder images
        img = load_image_strict(q['image'], mode="EXAM")
        if img:
            st.image(img, width=500)
        else:
            # Nếu không thấy ảnh, báo lỗi rõ ràng chứ không lấy ảnh bậy
            st.warning(f"⚠️ Không tìm thấy file ảnh: {q['image']} trong thư mục 'images'")

    # Phần chọn đáp án
    st.write("---")
    user_choice = st.radio(
        "Chọn đáp án:", 
        q['options'], 
        index=None, 
        key=f"q_radio_{st.session_state.current_q_index}"
    )

    # Nút kiểm tra
    if st.button("Kiểm tra kết quả", type="primary", use_container_width=True):
        st.session_state.show_answer = True

    # Hiển thị kết quả
    if st.session_state.show_answer:
        st.write("")
        correct = q['correct_answer'].strip()
        if user_choice:
            if user_choice.strip() == correct:
                st.success(f"🎉 CHÍNH XÁC! Đáp án là: {correct}")
            else:
                st.error(f"❌ SAI RỒI! Đáp án đúng là: {correct}")
        else:
            st.info(f"👉 Đáp án đúng là: {correct}")

# --- 7. MAIN APP ---
def main():
    with st.sidebar:
        st.title("🗂️ MENU ÔN TẬP")
        st.write("---")
        
        # Chọn loại bằng
        license_mode = st.selectbox("Chọn hạng bằng:", ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"])
        if license_mode != st.session_state.license_type:
            st.session_state.license_type = license_mode
            st.session_state.current_q_index = 0
            st.session_state.show_answer = False
            st.rerun()

        # Chọn chế độ
        app_mode = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi (600 câu)"])
        
        st.write("---")
        st.caption("Ver: Final Fix Logic")

    # Điều hướng
    if app_mode == "📖 Học Mẹo":
        render_tips_page(st.session_state.license_type)
    else:
        render_exam_page()

if __name__ == "__main__":
    main()
