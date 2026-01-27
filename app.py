import streamlit as st
import json
import os
import re
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
if 'user_selected_answer' not in st.session_state:
    st.session_state.user_selected_answer = None

# --- 3. CSS GIAO DIỆN ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    .question-header { color: #0d47a1; font-size: 1.3rem; font-weight: 700; margin-bottom: 15px; }
    .badge {
        font-size: 0.8rem; padding: 4px 8px; border-radius: 12px;
        color: white; font-weight: 600; text-transform: uppercase;
        margin-bottom: 8px; display: inline-block;
    }
    .danger-badge {
        background-color: #ffebee; color: #c62828; font-weight: bold;
        padding: 5px 10px; border-radius: 4px; border: 1px solid #ffcdd2;
        display: inline-block; margin-bottom: 10px;
    }
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    .hidden-answer { color: #999; font-style: italic; border: 1px dashed #ccc; padding: 0 8px; border-radius: 4px; }
    .question-content { font-size: 1.2rem; line-height: 1.6; color: #333; font-weight: 500; margin-bottom: 20px; }
    .explanation-box {
        background-color: #e8f5e9; border-left: 5px solid #4caf50;
        padding: 15px; margin-top: 15px; border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU (AUTO DETECT) ---

def get_category_color(category):
    colors = {
        "Biển báo": "#1976D2", "Sa hình": "#F57C00", "Khái niệm": "#388E3C",
        "Quy tắc": "#00796B", "Văn hóa": "#7B1FA2", "Kỹ thuật": "#455A64", "Tốc độ": "#D32F2F"
    }
    for key, color in colors.items():
        if key in category: return color
    return "#616161"

def normalize_questions(data):
    """Đưa dữ liệu về dạng list câu hỏi chuẩn"""
    if isinstance(data, dict) and 'questions' in data:
        return data['questions']
    if isinstance(data, list):
        return data
    return []

@st.cache_data
def load_tips():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'category' not in item: item['category'] = "Chung"
            return data
    except:
        return []

@st.cache_data
def load_questions_v3():
    """
    V3.0: Tự động tìm file (kể cả file (1)) và tự động cắt phần lỗi.
    """
    # 1. Tự động tìm file tiềm năng
    candidates = [
        'dulieu_web_chuan.json', 
        'dulieu_web_chuan (1).json', 
        'dulieu_web_chuan (2).json',
        'data.json' # Fallback
    ]
    
    file_path = None
    # Ưu tiên các tên file chuẩn
    for f in candidates:
        if os.path.exists(f):
            # Kiểm tra nhanh kích thước để tránh file rỗng
            if os.path.getsize(f) > 1024: 
                file_path = f
                break
    
    # Nếu không tìm thấy, quét tất cả file .json lớn trong thư mục
    if not file_path:
        for f in os.listdir('.'):
            if f.endswith('.json') and os.path.getsize(f) > 50000: # Lớn hơn 50KB khả năng cao là data
                file_path = f
                break
                
    if not file_path:
        return [], "Không tìm thấy file .json nào!"

    # 2. Đọc và Sửa lỗi nội dung
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Chiến thuật 1: Regex cắt đoạn giao nhau giữa 2 json ] {
    # File của bạn có dạng: [ ... ] { "meta": ... }
    # Ta sẽ lấy phần [ ... ]
    match = re.search(r'\]\s*\{', content)
    if match:
        # Cắt lấy phần đầu tiên
        clean_content = content[:match.start()+1]
        try:
            data = json.loads(clean_content)
            return normalize_questions(data), f"Đã đọc file '{file_path}' (Chế độ cắt lỗi)"
        except:
            pass # Thử cách khác

    # Chiến thuật 2: Dựa vào thông báo lỗi của Python (fallback)
    try:
        data = json.loads(content)
        return normalize_questions(data), f"Đã đọc file '{file_path}' (Chuẩn)"
    except json.JSONDecodeError as e:
        try:
            # Cắt ngay tại vị trí lỗi
            data = json.loads(content[:e.pos])
            return normalize_questions(data), f"Đã đọc file '{file_path}' (Sửa lỗi dòng {e.lineno})"
        except:
            pass

    return [], f"Đã tìm thấy file '{file_path}' nhưng không đọc được nội dung."

def process_image(image_filename, tip_id):
    if not image_filename: return None
    image_path = os.path.join("images", image_filename)
    if os.path.exists(image_path):
        img = Image.open(image_path)
        if 1 <= tip_id <= 36: img = img.rotate(-270, expand=True)
        elif 37 <= tip_id <= 51: img = img.rotate(-90, expand=True)
        return img
    return None

# --- 5. GIAO DIỆN HỌC MẸO ---
def render_tips_page(tips_data):
    st.header("💡 MẸO GIẢI NHANH")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("", placeholder="🔍 Tìm kiếm mẹo...")
    with col2:
        study_mode = st.radio("Chế độ:", ["Xem đáp án", "Học thuộc"], horizontal=True, label_visibility="collapsed")
    
    show_answer = (study_mode == "Xem đáp án")
    filtered_data = tips_data
    if search:
        filtered_data = [t for t in filtered_data if search.lower() in t['title'].lower() or any(search.lower() in x.lower() for x in t['content'])]

    if not filtered_data:
        st.warning("Không tìm thấy mẹo nào!")
        return

    if not search:
        categories = ["Tất cả"] + sorted(list(set([t['category'] for t in tips_data])))
        tabs = st.tabs(categories)
        for i, category in enumerate(categories):
            with tabs[i]:
                current_tips = tips_data if category == "Tất cả" else [t for t in tips_data if t['category'] == category]
                display_tips_list(current_tips, show_answer, key_suffix=f"{category}_{i}")
    else:
        display_tips_list(filtered_data, show_answer, key_suffix="search")

def display_tips_list(tips_list, show_answer, key_suffix=""):
    for tip in tips_list:
        cat_color = get_category_color(tip['category'])
        is_bookmarked = tip['id'] in st.session_state.bookmarks
        unique_key = f"{tip['id']}_{key_suffix}"
        
        st.markdown(f"""
        <div class="tip-card">
            <span class="badge" style="background-color: {cat_color}">{tip['category']}</span>
            <div class="tip-header"><span>{tip['title']}</span></div>
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
                if st.button("🔍 Phóng to ảnh", key=f"zoom_{unique_key}", use_container_width=True):
                    st.session_state.zoomed_image_data = {"image": img_obj, "title": tip['title']}
                    st.rerun()
        
        col_bk, _ = st.columns([0.2, 0.8])
        with col_bk:
            if st.checkbox("Lưu", value=is_bookmarked, key=f"bk_{unique_key}"):
                st.session_state.bookmarks.add(tip['id'])
            else:
                st.session_state.bookmarks.discard(tip['id'])
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. GIAO DIỆN 600 CÂU (V3) ---
def render_questions_page(questions_data, status_msg):
    st.header("📝 LUYỆN THI 600 CÂU")
    
    # Hiển thị trạng thái load file để debug
    if "Đã đọc file" in status_msg:
        st.success(f"✅ {status_msg} - Tổng số câu: {len(questions_data)}")
    else:
        st.error(f"⚠️ {status_msg}")
        return

    if not questions_data:
        st.warning("File không chứa câu hỏi nào.")
        return

    total_questions = len(questions_data)
    
    # Điều hướng
    col_prev, col_idx, col_next = st.columns([1, 2, 1])
    
    def change_question(new_index):
        st.session_state.current_question_index = new_index
        st.session_state.user_selected_answer = None 
    
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
        val_input = st.session_state.current_question_index + 1
        selected_index = st.number_input("Đến câu số:", 1, total_questions, val_input)
        if selected_index - 1 != st.session_state.current_question_index:
            change_question(selected_index - 1)
            st.rerun()

    # Hiển thị câu hỏi
    current_q = questions_data[st.session_state.current_question_index]
    is_danger = current_q.get('danger', False)
    
    st.markdown(f"""
    <div class="tip-card">
        <div class="question-header">Câu {current_q.get('id', st.session_state.current_question_index + 1)} / {total_questions}</div>
        {'<div class="danger-badge">⚠️ CÂU ĐIỂM LIỆT</div>' if is_danger else ''}
        <div class="question-content">{current_q.get('question', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    if current_q.get('image'):
         # Xử lý ảnh: thử tìm trong images/
         q_img_path = os.path.join("images", current_q['image'])
         if os.path.exists(q_img_path):
             st.image(q_img_path, caption="Hình ảnh tình huống", width=500)
    
    # Xử lý Đáp án
    choices = current_q.get('choices', current_q.get('options', []))
    correct_val = current_q.get('correct', current_q.get('correct_answer'))
    
    # Xác định index đáp án đúng
    correct_idx = -1
    has_correct_data = False
    
    if isinstance(correct_val, int):
        correct_idx = correct_val 
        has_correct_data = True
    elif isinstance(correct_val, str) and correct_val.strip().isdigit():
        correct_idx = int(correct_val) - 1
        has_correct_data = True
    
    # Form chọn
    selected_option = st.radio("Chọn đáp án:", options=choices, index=None, key=f"q_{st.session_state.current_question_index}")

    if selected_option:
        if not has_correct_data:
             st.warning("⚠️ Câu hỏi này trong file dữ liệu chưa được nhập đáp án đúng.")
        else:
            try:
                user_idx = choices.index(selected_option)
                if user_idx == correct_idx:
                    st.success("✅ Chính xác!")
                else:
                    st.error("❌ Sai rồi!")
                    # Hiển thị đáp án đúng an toàn
                    true_ans = "Không xác định"
                    if 0 <= correct_idx < len(choices):
                        true_ans = choices[correct_idx]
                    else:
                        true_ans = f"Đáp án số {correct_idx + 1}"
                        
                    st.info(f"👉 Đáp án đúng là: **{true_ans}**")
            except:
                st.error("Lỗi xử lý đáp án.")

        if current_q.get('explanation'):
             st.markdown(f"""<div class="explanation-box"><b>📖 Giải thích:</b><br>{current_q['explanation']}</div>""", unsafe_allow_html=True)

# --- 7. MAIN APP ---
def main():
    if st.session_state.zoomed_image_data:
        st.button("🔙 QUAY LẠI", on_click=lambda: st.session_state.update(zoomed_image_data=None), type="primary")
        st.header(st.session_state.zoomed_image_data["title"])
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        return

    tips_data = load_tips()
    # LOAD DATA V3
    questions_data, load_status = load_questions_v3()

    with st.sidebar:
        st.title("🗂️ Menu")
        page = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện 600 Câu"])
        st.divider()
        if st.checkbox("❤️ Chỉ xem Mẹo đã Lưu"):
            st.session_state.show_bookmarks_only = True
        else:
            st.session_state.show_bookmarks_only = False

    if page == "📖 Học Mẹo":
        display_data = tips_data
        if st.session_state.get('show_bookmarks_only'):
            display_data = [t for t in tips_data if t['id'] in st.session_state.bookmarks]
            if not display_data: st.warning("Bạn chưa lưu mẹo nào!")
        render_tips_page(display_data)
        
    elif page == "📝 Luyện 600 Câu":
        render_questions_page(questions_data, load_status)

if __name__ == "__main__":
    main()
