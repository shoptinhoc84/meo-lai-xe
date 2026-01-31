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

# --- 4. HÀM XỬ LÝ DỮ LIỆU (V6.0 - DEEP MINER) ---

def get_category_color(category):
    colors = {
        "Biển báo": "#1976D2", "Sa hình": "#F57C00", "Khái niệm": "#388E3C",
        "Quy tắc": "#00796B", "Văn hóa": "#7B1FA2", "Kỹ thuật": "#455A64", "Tốc độ": "#D32F2F"
    }
    for key, color in colors.items():
        if key in category: return color
    return "#616161"

def normalize_questions(data):
    """Chuẩn hóa dữ liệu về list"""
    if isinstance(data, dict) and 'questions' in data:
        return data['questions']
    if isinstance(data, list):
        return data
    return []

def check_data_quality(questions):
    """Chấm điểm: Ưu tiên bộ dữ liệu có đáp án"""
    if not questions: return 0
    score = 0
    # Quét 50 câu đầu để kiểm tra
    for q in questions[:50]: 
        # Kiểm tra mọi biến thể của trường đáp án
        ans = str(q.get('correct_answer', q.get('correct', q.get('answer', '')))).strip()
        if ans and ans != '0' and ans != '': 
            score += 1
    return score

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
def load_questions_v6():
    """
    V6.0: Deep Miner - Tìm kiếm trực tiếp block 'questions': [...] để bỏ qua phần lỗi.
    """
    # 1. Tìm file
    candidates = ['dulieu_web_chuan.json', 'dulieu_web_chuan (1).json', 'dulieu_web_chuan (2).json', 'data.json']
    file_path = None
    for f in candidates:
        if os.path.exists(f) and os.path.getsize(f) > 1024:
            file_path = f
            break
            
    if not file_path:
        for f in os.listdir('.'):
            if f.endswith('.json') and os.path.getsize(f) > 50000:
                file_path = f
                break

    if not file_path:
        return [], "Không tìm thấy file .json!", None

    # 2. Đọc file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    potential_datasets = []

    # --- CHIẾN THUẬT 1: TÌM 'questions': [ ---
    # Đây là chìa khóa để lấy bộ dữ liệu V2.0 xịn
    key_pattern = '"questions"'
    start_search = 0
    
    while True:
        idx = content.find(key_pattern, start_search)
        if idx == -1: break
        
        # Tìm dấu [ mở đầu mảng
        array_start = content.find('[', idx)
        if array_start != -1:
            try:
                # Dùng raw_decode để parse mảng JSON bắt đầu từ dấu [
                obj, end_idx = json.JSONDecoder().raw_decode(content, idx=array_start)
                data = normalize_questions(obj)
                score = check_data_quality(data)
                potential_datasets.append({
                    "data": data, 
                    "source": f"Bộ dữ liệu 'questions' (tìm thấy tại ký tự {idx})", 
                    "score": score + 5 # Cộng điểm ưu tiên cho bộ này
                })
            except: pass
        
        start_search = idx + len(key_pattern)

    # --- CHIẾN THUẬT 2: PARSE TRUYỀN THỐNG (BACKUP) ---
    if not potential_datasets:
        # Thử regex tách 2 file
        split_match = re.search(r'\]\s*\{', content)
        if split_match:
            try:
                d1 = normalize_questions(json.loads(content[:split_match.start()+1]))
                potential_datasets.append({"data": d1, "source": "Phần đầu file", "score": check_data_quality(d1)})
            except: pass
            
    # 3. CHỐT BỘ DỮ LIỆU TỐT NHẤT
    if not potential_datasets:
        # Last resort: Đọc toàn bộ
        try:
            d_all = normalize_questions(json.loads(content))
            return d_all, "Đọc toàn bộ file (Mode cơ bản)", d_all[0] if d_all else {}
        except:
             return [], f"Không đọc được dữ liệu nào từ '{file_path}'.", None
    
    # Sắp xếp theo điểm chất lượng cao nhất
    best_set = sorted(potential_datasets, key=lambda x: x['score'], reverse=True)[0]
    
    msg = f"Đã kích hoạt {best_set['source']} - Chất lượng: {best_set['score']} điểm"
    sample = best_set['data'][0] if best_set['data'] else {}
    
    return best_set['data'], msg, sample

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
    st.header("💡 MẸO GIẢI NHANH by SHOPTINHOC")
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

# --- 6. GIAO DIỆN 600 CÂU (V6) ---
def render_questions_page(questions_data, status_msg, sample_item):
    st.header("📝 LUYỆN THI 600 CÂU")
    
    if "Chất lượng" in status_msg and float(status_msg.split('Chất lượng:')[1].split('điểm')[0]) > 2:
        st.success(f"✅ {status_msg} - Đã tải {len(questions_data)} câu hỏi.")
    else:
        st.warning(f"⚠️ {status_msg}")
        if sample_item:
            with st.expander("🛠️ Debug Dữ liệu", expanded=False):
                st.json(sample_item)

    if not questions_data: return

    total_questions = len(questions_data)
    
    # --- ĐIỀU HƯỚNG ---
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
        val = st.session_state.current_question_index + 1
        selected_index = st.number_input("Đến câu số:", 1, total_questions, val)
        if selected_index - 1 != st.session_state.current_question_index:
            change_question(selected_index - 1)
            st.rerun()

    # --- HIỂN THỊ CÂU HỎI ---
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
         q_img_path = os.path.join("images", current_q['image'])
         if os.path.exists(q_img_path):
             st.image(q_img_path, caption="Hình ảnh tình huống", width=500)
    
    # --- XỬ LÝ ĐÁP ÁN (AUTO DETECT) ---
    choices = current_q.get('choices', current_q.get('options', []))
    
    # Tìm trường đáp án (hỗ trợ nhiều tên)
    correct_val = current_q.get('correct', current_q.get('correct_answer', current_q.get('answer')))
    
    correct_idx = -1
    has_correct_data = False
    
    if isinstance(correct_val, int):
        correct_idx = correct_val 
        has_correct_data = True
    elif isinstance(correct_val, str) and correct_val.strip().isdigit():
        correct_idx = int(correct_val)
        # Giả định chuẩn: Nếu đáp án > 0 và là số chuỗi, file dùng 1-based index
        if correct_idx > 0: correct_idx -= 1
        has_correct_data = True
    elif isinstance(correct_val, str) and correct_val:
        # Hỗ trợ đáp án dạng text
        try:
             norm_ans = correct_val.lower().strip()
             for i, c in enumerate(choices):
                 if norm_ans in str(c).lower():
                     correct_idx = i
                     has_correct_data = True
                     break
        except: pass

    # Radio
    selected_option = st.radio("Chọn đáp án:", options=choices, index=None, key=f"q_{st.session_state.current_question_index}")

    if selected_option:
        if not has_correct_data:
             st.warning(f"⚠️ Không tìm thấy đáp án trong dữ liệu (Giá trị raw: {correct_val})")
        else:
            try:
                user_idx = choices.index(selected_option)
                if user_idx == correct_idx:
                    st.success("✅ Chính xác!")
                else:
                    st.error("❌ Sai rồi!")
                    # Hiển thị đáp án đúng
                    true_ans_text = choices[correct_idx] if 0 <= correct_idx < len(choices) else f"Đáp án {correct_idx + 1}"
                    st.info(f"👉 Đáp án đúng là: **{true_ans_text}**")
            except:
                st.error("Lỗi so sánh đáp án.")

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
    # GỌI HÀM V6
    questions_data, load_status, sample_item = load_questions_v6() 

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
        render_questions_page(questions_data, load_status, sample_item)

if __name__ == "__main__":
    main()
