import streamlit as st
import json
import os
import re
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX SHOPTINHOC",
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
if 'license_type' not in st.session_state:
    st.session_state.license_type = "Ô tô (B1, B2, C...)" # Mặc định

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
    .highlight { background-color: #ffebee; color: #c62828; font-weight: bold; padding: 2px 6px; border-radius: 4px; }
    .hidden-answer { color: #999; font-style: italic; border: 1px dashed #ccc; padding: 0 8px; border-radius: 4px; }
    .explanation-box {
        background-color: #e8f5e9; border-left: 5px solid #4caf50;
        padding: 15px; margin-top: 15px; border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---

def get_category_color(category):
    colors = {
        "Biển báo": "#1976D2", "Sa hình": "#F57C00", "Khái niệm": "#388E3C",
        "Quy tắc": "#00796B", "Văn hóa": "#7B1FA2", "Kỹ thuật": "#455A64", "Tốc độ": "#D32F2F"
    }
    for key, color in colors.items():
        if key in category: return color
    return "#616161"

def normalize_questions(data):
    if isinstance(data, dict) and 'questions' in data:
        return data['questions']
    if isinstance(data, list):
        return data
    return []

# Hàm tải mẹo theo loại bằng
@st.cache_data
def load_tips(license_mode):
    # Xác định file cần tải
    filename = 'data.json' if license_mode == "oto" else 'tips_a1.json'
    
    if not os.path.exists(filename):
        return []
        
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            data = json.load(f)
            for item in data:
                if 'category' not in item: item['category'] = "Chung"
            return data
    except:
        return []

# Hàm tải câu hỏi theo loại bằng
@st.cache_data
def load_questions_v6(license_mode):
    # Xác định danh sách file ưu tiên
    if license_mode == "oto":
        candidates = ['dulieu_web_chuan.json', 'data_600cau.json']
    else:
        candidates = ['dulieu_a1.json', 'questions_a1.json'] # Bạn cần file này cho A1
    
    file_path = None
    for f in candidates:
        if os.path.exists(f) and os.path.getsize(f) > 1024:
            file_path = f
            break
            
    # Nếu không tìm thấy file cụ thể, thử tìm file json bất kỳ (fallback cũ)
    if not file_path and license_mode == "oto":
        for f in os.listdir('.'):
             if f.endswith('.json') and 'tips' not in f and os.path.getsize(f) > 50000:
                file_path = f
                break

    if not file_path:
        return [], f"Chưa có dữ liệu câu hỏi cho {license_mode}", None

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Logic parse JSON (Giữ nguyên logic Deep Miner cũ của bạn)
    key_pattern = '"questions"'
    idx = content.find(key_pattern)
    if idx != -1:
        array_start = content.find('[', idx)
        if array_start != -1:
            try:
                obj, _ = json.JSONDecoder().raw_decode(content, idx=array_start)
                return normalize_questions(obj), "Đã tải dữ liệu thành công", None
            except: pass
            
    try:
        d_all = normalize_questions(json.loads(content))
        return d_all, "Mode cơ bản", None
    except:
        return [], "Lỗi đọc file", None

def process_image(image_filename):
    if not image_filename: return None
    image_path = os.path.join("images", image_filename)
    if os.path.exists(image_path):
        return Image.open(image_path)
    return None

# --- 5. GIAO DIỆN HỌC MẸO ---
def render_tips_page(tips_data):
    st.header(f"💡 MẸO GIẢI NHANH ({st.session_state.license_type})")
    
    if not tips_data:
        st.info(f"Chưa có dữ liệu mẹo cho {st.session_state.license_type}. Vui lòng tạo file JSON.")
        return

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
        unique_key = f"{tip['id']}_{key_suffix}_{st.session_state.license_type}" # Unique key theo loại bằng
        
        st.markdown(f"""
        <div class="tip-card">
            <span class="badge" style="background-color: {cat_color}">{tip['category']}</span>
            <div class="tip-header"><b>{tip['title']}</b></div>
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
            img_obj = process_image(tip['image'])
            if img_obj:
                st.image(img_obj, use_container_width=True)
                if st.button("🔍 Phóng to", key=f"zoom_{unique_key}"):
                    st.session_state.zoomed_image_data = {"image": img_obj, "title": tip['title']}
                    st.rerun()
        
        # Bookmark logic
        if st.checkbox("Lưu mẹo", value=is_bookmarked, key=f"bk_{unique_key}"):
            st.session_state.bookmarks.add(tip['id'])
        else:
            st.session_state.bookmarks.discard(tip['id'])
        st.markdown("</div>", unsafe_allow_html=True)

# --- 6. GIAO DIỆN CÂU HỎI ---
def render_questions_page(questions_data, status_msg):
    st.header(f"📝 LUYỆN THI ({st.session_state.license_type})")
    
    if not questions_data:
        st.warning(f"⚠️ {status_msg}")
        st.info("Bạn cần upload file dữ liệu câu hỏi (JSON) cho hạng bằng này.")
        return

    total_questions = len(questions_data)
    
    # Navigation
    col_prev, col_idx, col_next = st.columns([1, 2, 1])
    
    with col_prev:
        if st.button("⬅️ Câu trước", use_container_width=True):
            if st.session_state.current_question_index > 0:
                st.session_state.current_question_index -= 1
                st.session_state.user_selected_answer = None
                st.rerun()
    with col_next:
        if st.button("Câu sau ➡️", use_container_width=True):
            if st.session_state.current_question_index < total_questions - 1:
                st.session_state.current_question_index += 1
                st.session_state.user_selected_answer = None
                st.rerun()
                
    # Hiển thị câu hỏi (Giữ nguyên logic hiển thị cũ)
    current_q = questions_data[st.session_state.current_question_index]
    is_danger = current_q.get('danger', False)
    
    st.markdown(f"""
    <div class="tip-card">
        <div class="question-header">Câu {st.session_state.current_question_index + 1} / {total_questions}</div>
        {'<div class="badge" style="background-color:red">⚠️ CÂU ĐIỂM LIỆT</div>' if is_danger else ''}
        <div class="question-content">{current_q.get('question', '')}</div>
    </div>
    """, unsafe_allow_html=True)

    if current_q.get('image'):
         img = process_image(current_q['image'])
         if img: st.image(img, caption="Hình huống", width=500)

    choices = current_q.get('choices', current_q.get('options', []))
    correct_val = current_q.get('correct', current_q.get('correct_answer', current_q.get('answer')))
    
    # Xử lý đáp án đúng (tương thích nhiều format)
    correct_idx = -1
    if isinstance(correct_val, int): correct_idx = correct_val if correct_val < 10 else correct_val - 1 # Simple heuristic
    elif str(correct_val).isdigit(): correct_idx = int(correct_val) - 1
    
    selected = st.radio("Chọn đáp án:", options=choices, index=None, key=f"q_{st.session_state.current_question_index}_{st.session_state.license_type}")
    
    if selected:
        if choices.index(selected) == correct_idx:
            st.success("✅ Chính xác!")
        else:
            st.error("❌ Sai rồi!")
            if 0 <= correct_idx < len(choices):
                st.info(f"👉 Đáp án đúng: **{choices[correct_idx]}**")
        
        if current_q.get('explanation'):
             st.markdown(f"""<div class="explanation-box"><b>📖 Giải thích:</b><br>{current_q['explanation']}</div>""", unsafe_allow_html=True)

# --- 7. MAIN APP ---
def main():
    if st.session_state.zoomed_image_data:
        st.button("🔙 QUAY LẠI", on_click=lambda: st.session_state.update(zoomed_image_data=None), type="primary")
        st.header(st.session_state.zoomed_image_data["title"])
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        return

    with st.sidebar:
        st.title("🗂️ Menu Ôn Thi")
        
        # --- CHỌN HẠNG BẰNG ---
        app_mode = st.selectbox(
            "Chọn hạng bằng:", 
            ["Ô tô (B1, B2, C...)", "Xe máy (A1, A2)"],
            index=0 if "Ô tô" in st.session_state.license_type else 1
        )
        
        # Reset index nếu đổi hạng bằng
        if app_mode != st.session_state.license_type:
            st.session_state.license_type = app_mode
            st.session_state.current_question_index = 0
            st.session_state.user_selected_answer = None
            st.rerun()

        st.divider()
        page = st.radio("Chế độ:", ["📖 Học Mẹo", "📝 Luyện Thi"])
        st.divider()
        st.caption("Developed by ShopTinHoc")

    # Xác định từ khóa mode để load file (oto / xemay)
    mode_key = "oto" if "Ô tô" in st.session_state.license_type else "xemay"

    if page == "📖 Học Mẹo":
        # Load data tương ứng
        tips_data = load_tips(mode_key)
        render_tips_page(tips_data)
        
    elif page == "📝 Luyện Thi":
        questions_data, status, _ = load_questions_v6(mode_key)
        render_questions_page(questions_data, status)

if __name__ == "__main__":
    main()
