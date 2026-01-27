import streamlit as st
import json
import os
import random
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX Pro",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. KHỞI TẠO STATE ---
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = set()
if 'zoomed_image_data' not in st.session_state:
    st.session_state.zoomed_image_data = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
# State để lưu câu trả lời tạm thời của người dùng cho câu hỏi hiện tại
if 'user_selected_answer' not in st.session_state:
    st.session_state.user_selected_answer = None

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    
    /* Giao diện thẻ */
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    
    /* Tiêu đề */
    .tip-header {
        color: #b71c1c; font-size: 1.2rem; font-weight: 700; margin-bottom: 10px;
    }
    .question-header {
        color: #0d47a1; font-size: 1.3rem; font-weight: 700; margin-bottom: 15px;
    }

    /* Nhãn Category */
    .badge {
        font-size: 0.8rem; padding: 4px 8px; border-radius: 12px;
        color: white; font-weight: 600; text-transform: uppercase;
        margin-bottom: 8px; display: inline-block;
    }
    
    /* Badge Điểm liệt */
    .danger-badge {
        background-color: #ffebee; color: #c62828; font-weight: bold;
        padding: 5px 10px; border-radius: 4px; border: 1px solid #ffcdd2;
        display: inline-block; margin-bottom: 10px;
    }
    
    /* Highlight */
    .highlight {
        background-color: #ffebee; color: #c62828; font-weight: bold;
        padding: 2px 6px; border-radius: 4px; border: 1px solid #ffcdd2;
    }
    
    .hidden-answer {
        color: #999; font-style: italic; border: 1px dashed #ccc; padding: 0 8px; border-radius: 4px;
    }

    /* Nội dung câu hỏi 600 câu */
    .question-content {
        font-size: 1.2rem;
        line-height: 1.6;
        color: #333;
        font-weight: 500;
        margin-bottom: 20px;
    }
    
    /* Giải thích */
    .explanation-box {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 15px;
        margin-top: 15px;
        border-radius: 4px;
    }

    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU & ẢNH ---
def get_category_color(category):
    colors = {
        "Biển báo": "#1976D2", "Sa hình": "#F57C00", "Khái niệm": "#388E3C",
        "Quy tắc": "#00796B", "Văn hóa": "#7B1FA2", "Kỹ thuật": "#455A64", "Tốc độ": "#D32F2F"
    }
    for key, color in colors.items():
        if key in category: return color
    return "#616161"

@st.cache_data
def load_tips():
    try:
        # Load file data.json (Mẹo)
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'category' not in item: item['category'] = "Chung"
            return data
    except FileNotFoundError:
        return []

@st.cache_data
def load_questions():
    try:
        # Load file dulieu_web_chuan.json (Câu hỏi)
        # Ưu tiên load file này vì nó có cấu trúc choices và explanation chuẩn
        with open('dulieu_web_chuan.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Kiểm tra nếu file json có key 'questions' (như cấu trúc bạn gửi) hay là list trực tiếp
            if isinstance(data, dict) and 'questions' in data:
                return data['questions']
            return data
    except FileNotFoundError:
        return []

def process_image(image_filename, tip_id):
    image_path = os.path.join("images", image_filename)
    if os.path.exists(image_path):
        img = Image.open(image_path)
        # Logic xoay ảnh theo yêu cầu
        if 1 <= tip_id <= 36:
            img = img.rotate(-270, expand=True)
        elif 37 <= tip_id <= 51:
            img = img.rotate(-90, expand=True)
        return img
    return None

# --- 5. GIAO DIỆN HỌC MẸO (Tab 1) ---
def render_tips_page(tips_data):
    st.header("💡 MẸO GIẢI NHANH")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("", placeholder="🔍 Tìm kiếm mẹo (vd: độ tuổi, 18 tuổi, cấm dừng...)...")
    with col2:
        study_mode = st.radio("Chế độ:", ["Xem đáp án", "Học thuộc"], horizontal=True, label_visibility="collapsed")
    
    show_answer = (study_mode == "Xem đáp án")

    # Lọc dữ liệu
    filtered_data = tips_data
    if search:
        filtered_data = [t for t in filtered_data if search.lower() in t['title'].lower() or any(search.lower() in x.lower() for x in t['content'])]

    if not filtered_data:
        st.warning("Không tìm thấy mẹo nào phù hợp!")
        return

    # Hiển thị Tabs Category
    if not search:
        categories = ["Tất cả"] + sorted(list(set([t['category'] for t in tips_data])))
        tabs = st.tabs(categories)
        for i, category in enumerate(categories):
            with tabs[i]:
                current_tips = tips_data if category == "Tất cả" else [t for t in tips_data if t['category'] == category]
                display_tips_list(current_tips, show_answer)
    else:
        display_tips_list(filtered_data, show_answer)

def display_tips_list(tips_list, show_answer):
    for tip in tips_list:
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
                display_line = f"{q_text} <span class='highlight'>👉 {a_text}</span>" if show_answer else f"{q_text} <span class='hidden-answer'>???</span>"
            else:
                display_line = line
            st.markdown(f"• {display_line}", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        if tip.get('image'):
            img_obj = process_image(tip['image'], tip.get('id', 0))
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

# --- 6. GIAO DIỆN LUYỆN 600 CÂU (ĐÃ NÂNG CẤP) ---
def render_questions_page(questions_data):
    st.header("📝 LUYỆN THI 600 CÂU")
    
    if not questions_data:
        st.error("Chưa tìm thấy dữ liệu câu hỏi. Vui lòng kiểm tra file 'dulieu_web_chuan.json'.")
        return

    total_questions = len(questions_data)
    
    # --- THANH ĐIỀU HƯỚNG ---
    col_prev, col_idx, col_next = st.columns([1, 2, 1])
    
    def change_question(new_index):
        st.session_state.current_question_index = new_index
        # Reset câu trả lời khi chuyển câu hỏi
        st.session_state.user_selected_answer = None 
        # Cần rerun để UI cập nhật lại trạng thái radio button
        # (Streamlit đôi khi giữ cache của radio nếu key không đổi)
    
    with col_prev:
        if st.button("⬅️ Câu trước", use_container_width=True):
            if st.session_state.current_question_index > 0:
                change_question(st.session_state.current_question_index - 1)
                st.rerun()

    with col_next:
        if st.button("Câu sau ➡️", use_container_width=True):
            if st.session_state.current_question_index < total_questions - 1:
                change_question(st.session_state.current_question_index + 1)
                st.rerun()
                
    with col_idx:
        # Chọn câu nhanh
        selected_index = st.number_input(
            "Chuyển nhanh đến câu số:", 
            min_value=1, 
            max_value=total_questions, 
            value=st.session_state.current_question_index + 1
        )
        if selected_index - 1 != st.session_state.current_question_index:
            change_question(selected_index - 1)
            st.rerun()

    # --- HIỂN THỊ CÂU HỎI ---
    current_q = questions_data[st.session_state.current_question_index]
    
    # Kiểm tra xem câu này có phải câu điểm liệt không
    is_danger = current_q.get('danger', False)
    
    st.markdown(f"""
    <div class="tip-card">
        <div class="question-header">Câu hỏi số {current_q['id']} / {total_questions}</div>
        {'<div class="danger-badge">⚠️ CÂU ĐIỂM LIỆT</div>' if is_danger else ''}
        <div class="question-content">
            {current_q['question']}
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Hiển thị hình ảnh câu hỏi (nếu có)
    # Lưu ý: File json của bạn có trường 'image' (ví dụ: null hoặc tên file)
    if current_q.get('image'):
         # Đường dẫn ảnh câu hỏi thường nằm trong thư mục images
         q_img_path = os.path.join("images", current_q['image'])
         if os.path.exists(q_img_path):
             st.image(q_img_path, caption="Hình ảnh minh họa", width=500)
    
    # --- PHẦN TRẢ LỜI ---
    choices = current_q.get('choices', [])
    correct_idx = int(current_q.get('correct', 0)) # Index đáp án đúng (trong json 0-based hay 1-based tùy file)
    # File dulieu_web_chuan.json của bạn: Question 2 correct=0. Vậy là 0-based index.
    
    # Callback khi chọn radio
    def on_radio_change():
        # Hàm này chạy sau khi user click, giá trị đã được update vào key
        pass

    # Radio button cho các đáp án
    # Key phải là unique theo câu hỏi để reset khi chuyển câu
    radio_key = f"q_radio_{current_q['id']}"
    
    selected_option = st.radio(
        "Chọn đáp án:",
        options=choices,
        index=None, # Mặc định chưa chọn
        key=radio_key,
        on_change=on_radio_change
    )

    # --- XỬ LÝ KẾT QUẢ ---
    if selected_option:
        # Tìm index của đáp án người dùng chọn
        user_idx = choices.index(selected_option)
        
        if user_idx == correct_idx:
            st.success("✅ Chính xác!")
        else:
            st.error(f"❌ Sai rồi! Đáp án đúng là: {choices[correct_idx]}")
            
        # Hiển thị giải thích
        explanation = current_q.get('explanation', "Không có giải thích chi tiết.")
        st.markdown(f"""
        <div class="explanation-box">
            <b>📖 Giải thích:</b><br>
            {explanation}
        </div>
        """, unsafe_allow_html=True)


# --- 7. CHƯƠNG TRÌNH CHÍNH (MAIN) ---
def main():
    # === XỬ LÝ ZOOM FULLSCREEN ===
    if st.session_state.zoomed_image_data:
        st.button("🔙 QUAY LẠI", on_click=lambda: st.session_state.update(zoomed_image_data=None), type="primary", use_container_width=True)
        st.header(st.session_state.zoomed_image_data["title"])
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        return

    # Tải dữ liệu
    tips_data = load_tips()
    questions_data = load_questions()

    # === MENU SIDEBAR ===
    with st.sidebar:
        st.title("🗂️ Menu Chức Năng")
        page = st.radio("Chọn chế độ học:", ["📖 Học Mẹo (51 Mẹo)", "📝 Luyện 600 Câu"], index=0)
        
        st.divider()
        st.subheader("Công cụ bổ trợ")
        if st.checkbox("❤️ Xem Mẹo đã Lưu"):
            st.session_state.show_bookmarks_only = True
        else:
            st.session_state.show_bookmarks_only = False
            
        if st.button("🎲 Bốc thăm Mẹo ngẫu nhiên"):
             if tips_data:
                st.session_state['random_tip'] = random.choice(tips_data)

    # === LOGIC HIỂN THỊ CHÍNH ===
    
    # Nếu có bốc thăm ngẫu nhiên -> Hiển thị ưu tiên
    if 'random_tip' in st.session_state:
        st.info("🎲 **Mẹo ngẫu nhiên:**")
        tip = st.session_state['random_tip']
        st.markdown(f"**{tip['title']}**")
        st.write(tip['content'])
        if st.button("Đóng bốc thăm"):
            del st.session_state['random_tip']
            st.rerun()
        st.divider()

    # Điều hướng trang
    if page == "📖 Học Mẹo (51 Mẹo)":
        display_data = tips_data
        if st.session_state.get('show_bookmarks_only'):
            display_data = [t for t in tips_data if t['id'] in st.session_state.bookmarks]
            if not display_data: st.warning("Bạn chưa lưu mẹo nào!")
            
        render_tips_page(display_data)
        
    elif page == "📝 Luyện 600 Câu":
        render_questions_page(questions_data)

if __name__ == "__main__":
    main()
