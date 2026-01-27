import streamlit as st
import json
import os
import random
from PIL import Image

# --- 1. CẤU HÌNH TRANG (Phải đặt đầu tiên) ---
st.set_page_config(
    page_title="Ôn Thi 600 Câu PRO",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. KHỞI TẠO STATE ---
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = set()
if 'zoomed_image_data' not in st.session_state:
    st.session_state.zoomed_image_data = None
# State cho phần ôn tập 600 câu
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {} # Lưu đáp án user chọn: {question_id: selected_option_text}

# --- 3. CSS CAO CẤP ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    
    /* Giao diện thẻ bài Mẹo */
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .tip-header { color: #b71c1c; font-size: 1.25rem; font-weight: 700; margin-bottom: 10px; }
    .badge { font-size: 0.8rem; padding: 4px 8px; border-radius: 12px; color: white; font-weight: 600; margin-bottom: 8px; display: inline-block; }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    .hidden-answer { color: #999; font-style: italic; border: 1px dashed #ccc; padding: 0 8px; border-radius: 4px; }
    
    /* Giao diện Câu hỏi ôn tập */
    .question-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1976D2; margin-bottom: 15px; }
    .question-text { font-size: 1.2rem; font-weight: 600; color: #2c3e50; }
    .correct-ans { color: #2e7d32; font-weight: bold; }
    .wrong-ans { color: #c62828; font-weight: bold; }
    .explanation { background-color: #e8f5e9; padding: 10px; border-radius: 8px; margin-top: 10px; border: 1px dashed #2e7d32; }

    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. CÁC HÀM HỖ TRỢ ---
def get_category_color(category):
    colors = { "Biển báo": "#1976D2", "Sa hình": "#F57C00", "Khái niệm": "#388E3C", "Quy tắc": "#00796B", "Văn hóa": "#7B1FA2", "Kỹ thuật": "#455A64", "Tốc độ": "#D32F2F" }
    for key, color in colors.items():
        if key in category: return color
    return "#616161"

@st.cache_data
def load_tips_data():
    # Load dữ liệu Mẹo (data.json)
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'category' not in item: item['category'] = "Chung"
            return data
    except FileNotFoundError:
        return []

@st.cache_data
def load_questions_data():
    # Load dữ liệu 600 câu (dulieu_web_chuan.json)
    try:
        with open('dulieu_web_chuan.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Kiểm tra sơ bộ cấu trúc
            if isinstance(data, list) and len(data) > 0:
                return data
            return []
    except FileNotFoundError:
        return []

def process_image(image_filename, tip_id=0, is_question=False):
    # Nếu là ảnh câu hỏi (600 câu), folder chung là images
    if not image_filename: return None
    
    image_path = os.path.join("images", image_filename)
    if os.path.exists(image_path):
        img = Image.open(image_path)
        # Logic xoay ảnh chỉ áp dụng cho phần Mẹo (tip_id > 0)
        if not is_question: 
            if 1 <= tip_id <= 36: img = img.rotate(-270, expand=True)
            elif 37 <= tip_id <= 51: img = img.rotate(-90, expand=True)
        return img
    return None

# --- 5. LOGIC HIỂN THỊ: MẸO GHI NHỚ ---
def render_tips_view(data):
    if 'random_tip' in st.session_state:
        st.info("🎲 **Mẹo ngẫu nhiên dành cho bạn:**")
        render_tip_card(st.session_state['random_tip'], True)
        st.divider()

    st.header("📚 MẸO GHI NHỚ NHANH")
    
    # Sidebar lọc riêng cho phần Mẹo
    with st.sidebar:
        st.divider()
        st.subheader("🛠️ Công cụ Mẹo")
        study_mode = st.radio("Chế độ xem mẹo:", ["📖 Xem đáp án", "🫣 Học thuộc (Che đi)"])
        show_result = (study_mode == "📖 Xem đáp án")
        filter_bookmark = st.checkbox("❤️ Chỉ hiện mẹo đã Lưu")
        if st.button("🎲 Bốc thăm mẹo"):
            st.session_state['random_tip'] = random.choice(data)
        if st.button("❌ Xóa bốc thăm"):
            if 'random_tip' in st.session_state: del st.session_state['random_tip']

    search = st.text_input("", placeholder="🔍 Nhập từ khóa tìm mẹo (vd: độ tuổi, cấm dừng...)...")

    filtered_data = data
    if search:
        filtered_data = [t for t in filtered_data if search.lower() in t['title'].lower() or any(search.lower() in x.lower() for x in t['content'])]
    if filter_bookmark:
        filtered_data = [t for t in filtered_data if t['id'] in st.session_state.bookmarks]

    if not filtered_data:
        st.warning("Không tìm thấy mẹo nào phù hợp!")
    else:
        if search or filter_bookmark:
            st.caption(f"Tìm thấy {len(filtered_data)} mẹo:")
            for tip in filtered_data:
                render_tip_card(tip, show_result)
        else:
            categories = ["Tất cả"] + sorted(list(set([t['category'] for t in data])))
            tabs = st.tabs(categories)
            for i, category in enumerate(categories):
                with tabs[i]:
                    current_tips = data if category == "Tất cả" else [t for t in data if t['category'] == category]
                    for tip in current_tips:
                        render_tip_card(tip, show_result)

def render_tip_card(tip, show_answer):
    cat_color = get_category_color(tip['category'])
    is_bookmarked = tip['id'] in st.session_state.bookmarks
    
    st.markdown(f"""
    <div class="tip-card">
        <span class="badge" style="background-color: {cat_color}">{tip['category']}</span>
        <div class="tip-header"><span>{tip['title']}</span></div>
        <div class="tip-content">
    """, unsafe_allow_html=True)
    
    for line in tip['content']:
        if "=>" in line:
            parts = line.split("=>")
            q_text, a_text = parts[0], parts[1]
            if show_answer:
                display_line = f"{q_text} <span class='highlight'>👉 {a_text}</span>"
            else:
                display_line = f"{q_text} <span class='hidden-answer'>???</span>"
        else:
            display_line = line
        st.markdown(f"• {display_line}", unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    if tip.get('image'):
        img_obj = process_image(tip['image'], tip.get('id', 0), is_question=False)
        if img_obj:
            st.image(img_obj, use_container_width=True)
            if st.button("🔍 Phóng to ảnh", key=f"zoom_{tip['id']}", use_container_width=True):
                st.session_state.zoomed_image_data = {"image": img_obj, "title": tip['title']}
                st.rerun()
    
    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.checkbox("Lưu", value=is_bookmarked, key=f"bk_{tip['id']}"):
            st.session_state.bookmarks.add(tip['id'])
        else:
            st.session_state.bookmarks.discard(tip['id'])
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. LOGIC HIỂN THỊ: ÔN TẬP 600 CÂU (NEW) ---
def render_practice_view(questions):
    if not questions:
        st.error("⚠️ Chưa có dữ liệu câu hỏi. Vui lòng kiểm tra file `dulieu_web_chuan.json`.")
        return

    total_q = len(questions)
    
    # Sidebar Navigation cho câu hỏi
    with st.sidebar:
        st.divider()
        st.subheader("🔢 Chọn câu hỏi")
        # Nhập số câu để nhảy đến
        q_num = st.number_input("Đi tới câu số:", min_value=1, max_value=total_q, value=st.session_state.current_question_index + 1)
        st.session_state.current_question_index = q_num - 1
        
        # Thanh tiến độ
        answered_count = len(st.session_state.user_answers)
        st.progress(answered_count / total_q)
        st.caption(f"Đã làm: {answered_count}/{total_q} câu")

    # Lấy câu hỏi hiện tại
    idx = st.session_state.current_question_index
    q_data = questions[idx]
    q_id = q_data.get('id', idx + 1)
    
    # Xử lý nội dung câu hỏi: Ưu tiên lấy từ content[0] vì question có thể bị cắt
    q_content_full = q_data.get('content', [])
    q_text = q_content_full[0] if len(q_content_full) > 0 else q_data.get('question', "Nội dung câu hỏi bị thiếu")

    # Hiển thị câu hỏi
    st.subheader(f"Câu {q_id}:")
    st.markdown(f"""
    <div class="question-box">
        <div class="question-text">{q_text}</div>
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị ảnh nếu có
    if q_data.get('image'):
        img_obj = process_image(q_data['image'], is_question=True)
        if img_obj:
            st.image(img_obj, caption=f"Hình ảnh câu {q_id}")
            # Zoom ảnh
            if st.button("🔍 Phóng to ảnh", key=f"zoom_q_{q_id}"):
                st.session_state.zoomed_image_data = {"image": img_obj, "title": f"Câu hỏi {q_id}"}
                st.rerun()

    # Hiển thị các lựa chọn
    # Lấy options từ field 'options' hoặc từ 'content'
    options = q_data.get('options', [])
    if not options and len(q_content_full) > 1:
        options = q_content_full[1:] # Fallback nếu options rỗng

    # Kiểm tra xem user đã chọn đáp án chưa
    user_choice_text = st.session_state.user_answers.get(str(q_id), None)
    
    # Tìm index của lựa chọn đã lưu (nếu có)
    saved_index = None
    if user_choice_text in options:
        saved_index = options.index(user_choice_text)

    # Dùng Radio button để chọn
    selected_option = st.radio(
        "Chọn đáp án:", 
        options, 
        index=saved_index,
        key=f"q_radio_{q_id}"
    )

    # Nút xác nhận & Điều hướng
    col1, col2 = st.columns([1, 1])
    
    # Logic kiểm tra đáp án
    correct_ans_text = q_data.get('correct_answer', "")
    
    if selected_option:
        # Lưu vào state
        st.session_state.user_answers[str(q_id)] = selected_option
        
        # Chỉ kiểm tra nếu có dữ liệu correct_answer
        if correct_ans_text:
            if selected_option.strip() == correct_ans_text.strip(): # So sánh chuỗi
                st.success("✅ Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Đáp án đúng là: {correct_ans_text}")
        else:
            st.info("ℹ️ Đã lưu câu trả lời. (Câu này chưa cập nhật đáp án đúng trong hệ thống)")
            
    st.divider()
    
    # Nút Next/Prev
    c_prev, c_next = st.columns(2)
    with c_prev:
        if st.button("⬅️ Câu trước", disabled=(idx == 0), use_container_width=True):
            st.session_state.current_question_index -= 1
            st.rerun()
    with c_next:
        if st.button("Câu sau ➡️", disabled=(idx == total_q - 1), type="primary", use_container_width=True):
            st.session_state.current_question_index += 1
            st.rerun()

# --- 7. CHƯƠNG TRÌNH CHÍNH ---
def main():
    # === XỬ LÝ ẢNH PHÓNG TO (GLOBAL) ===
    if st.session_state.zoomed_image_data:
        st.button("🔙 QUAY LẠI", on_click=lambda: st.session_state.update(zoomed_image_data=None), type="primary")
        st.header(st.session_state.zoomed_image_data["title"])
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        return

    # --- SIDEBAR CHÍNH ---
    with st.sidebar:
        st.title("🚗 MENU CHÍNH")
        app_mode = st.radio("Chọn chức năng:", ["💡 Mẹo ghi nhớ", "📝 Luyện thi 600 câu"])

    # --- ĐIỀU HƯỚNG ---
    if app_mode == "💡 Mẹo ghi nhớ":
        tips_data = load_tips_data()
        if not tips_data:
            st.warning("Vui lòng tải file data.json để xem mẹo.")
        else:
            render_tips_view(tips_data)
            
    elif app_mode == "📝 Luyện thi 600 câu":
        questions_data = load_questions_data()
        render_practice_view(questions_data)

if __name__ == "__main__":
    main()
