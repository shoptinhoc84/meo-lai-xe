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
# Lưu câu trả lời của người dùng (id câu hỏi: đáp án đã chọn)
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
# Lưu kết quả kiểm tra (đúng/sai)
if 'answer_results' not in st.session_state:
    st.session_state.answer_results = {}
# Lưu chế độ học (học từng câu/tất cả)
if 'study_mode' not in st.session_state:
    st.session_state.study_mode = "sequential"  # "sequential" hoặc "all"
# Lưu filter theo loại câu hỏi
if 'question_filter' not in st.session_state:
    st.session_state.question_filter = "all"  # "all", "danger", "undanger"
# Lưu thông tin kết quả bài thi
if 'exam_results' not in st.session_state:
    st.session_state.exam_results = {
        "total": 0,
        "correct": 0,
        "incorrect": 0,
        "score": 0
    }

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
    
    /* Badge loại câu hỏi */
    .type-badge {
        background-color: #e3f2fd; color: #1565c0; font-weight: 600;
        padding: 3px 8px; border-radius: 10px; font-size: 0.8rem;
        margin-right: 5px; margin-bottom: 5px; display: inline-block;
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
    
    /* Đáp án */
    .answer-option {
        padding: 10px 15px;
        margin: 5px 0;
        border-radius: 8px;
        border: 1px solid #e0e0e0;
        cursor: pointer;
        transition: all 0.3s;
    }
    .answer-option:hover {
        background-color: #f5f5f5;
    }
    .answer-option.correct {
        background-color: #e8f5e9;
        border-color: #4caf50;
        color: #2e7d32;
    }
    .answer-option.incorrect {
        background-color: #ffebee;
        border-color: #f44336;
        color: #c62828;
    }
    .answer-option.selected {
        background-color: #e3f2fd;
        border-color: #2196f3;
        color: #0d47a1;
        font-weight: bold;
    }
    
    /* Giải thích */
    .explanation-box {
        background-color: #e8f5e9;
        border-left: 5px solid #4caf50;
        padding: 15px;
        margin-top: 15px;
        border-radius: 4px;
    }
    
    .warning-box {
        background-color: #fff3e0;
        border-left: 5px solid #ff9800;
        padding: 15px;
        margin-top: 15px;
        border-radius: 4px;
    }

    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
    
    /* Progress bar */
    .progress-container {
        width: 100%;
        background-color: #e0e0e0;
        border-radius: 10px;
        margin: 10px 0;
    }
    .progress-bar {
        height: 10px;
        border-radius: 10px;
        background-color: #4caf50;
        transition: width 0.3s;
    }
    
    /* Thống kê */
    .stats-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
    }
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
        # Thử load nhiều tên file json khác nhau
        possible_files = ['dulieu_web_chuan.json', 'questions.json', 'data_questions.json', '600_cau.json']
        
        for file_name in possible_files:
            if os.path.exists(file_name):
                with open(file_name, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Chuẩn hóa dữ liệu
                    if isinstance(data, dict):
                        if 'questions' in data:
                            questions = data['questions']
                        else:
                            # Nếu không có key 'questions', thử lấy tất cả các key khác
                            questions = []
                            for key, value in data.items():
                                if isinstance(value, list):
                                    questions = value
                                    break
                    else:
                        questions = data
                    
                    # Đảm bảo mỗi câu hỏi có đầy đủ thông tin
                    for i, q in enumerate(questions):
                        if 'id' not in q:
                            q['id'] = i + 1
                        if 'danger' not in q:
                            q['danger'] = False
                        if 'type' not in q:
                            q['type'] = "Khái niệm"  # Default type
                        if 'explanation' not in q:
                            q['explanation'] = "Không có giải thích chi tiết."
                    
                    return questions
        return []
    except Exception as e:
        st.error(f"Lỗi khi tải dữ liệu câu hỏi: {str(e)}")
        return []

def filter_questions(questions, filter_type="all"):
    """Lọc câu hỏi theo loại"""
    if filter_type == "all":
        return questions
    elif filter_type == "danger":
        return [q for q in questions if q.get('danger', False)]
    elif filter_type == "undanger":
        return [q for q in questions if not q.get('danger', False)]
    return questions

def calculate_results(questions):
    """Tính toán kết quả bài làm"""
    total = len(questions)
    correct = 0
    incorrect = 0
    score = 0
    
    for q in questions:
        q_id = str(q['id'])
        if q_id in st.session_state.user_answers:
            user_answer = st.session_state.user_answers[q_id]
            correct_answer = q.get('correct', 0)
            
            if isinstance(correct_answer, str):
                correct_answer = int(correct_answer)
            
            if user_answer == correct_answer:
                correct += 1
                score += 1
            else:
                incorrect += 1
    
    return {
        "total": total,
        "correct": correct,
        "incorrect": incorrect,
        "score": score,
        "percentage": (correct / total * 100) if total > 0 else 0
    }

# --- 5. GIAO DIỆN HỌC MẸO (Tab 1) ---
def render_tips_page(tips_data):
    st.header("💡 MẸO GIẢI NHANH")
    
    col1, col2 = st.columns([3, 1])
    with col1:
        search = st.text_input("", placeholder="🔍 Tìm kiếm mẹo (vd: độ tuổi, 18 tuổi, cấm dừng...)...")
    with col2:
        study_mode = st.radio("Chế độ:", ["Xem đáp án", "Học thuộc"], horizontal=True, label_visibility="collapsed")
    
    show_answer = (study_mode == "Xem đáp án")

    filtered_data = tips_data
    if search:
        filtered_data = [t for t in filtered_data if search.lower() in t['title'].lower() or any(search.lower() in x.lower() for x in t['content'])]

    if not filtered_data:
        st.warning("Không tìm thấy mẹo nào phù hợp!")
        return

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
        st.error("""
        ❌ Chưa tìm thấy dữ liệu câu hỏi. 
        
        Vui lòng kiểm tra file dữ liệu (tên file có thể là):
        - `dulieu_web_chuan.json`
        - `questions.json`
        - `data_questions.json`
        - `600_cau.json`
        
        Đảm bảo file JSON có cấu trúc đúng (list các câu hỏi) và nằm trong cùng thư mục với ứng dụng.
        """)
        return

    # Lọc câu hỏi
    filtered_questions = filter_questions(questions_data, st.session_state.question_filter)
    total_questions = len(filtered_questions)
    
    if total_questions == 0:
        st.warning("Không tìm thấy câu hỏi nào phù hợp với bộ lọc!")
        return
    
    # --- THANH ĐIỀU HƯỚNG & CÔNG CỤ ---
    col_tools = st.columns([2, 2, 2, 2])
    
    with col_tools[0]:
        # Chế độ học
        mode = st.selectbox(
            "Chế độ học:",
            ["Từng câu", "Tất cả câu"],
            index=0 if st.session_state.study_mode == "sequential" else 1,
            key="study_mode_select"
        )
        st.session_state.study_mode = "sequential" if mode == "Từng câu" else "all"
    
    with col_tools[1]:
        # Lọc câu hỏi
        filter_type = st.selectbox(
            "Lọc câu hỏi:",
            ["Tất cả", "Câu điểm liệt", "Câu thường"],
            key="question_filter_select"
        )
        filter_map = {"Tất cả": "all", "Câu điểm liệt": "danger", "Câu thường": "undanger"}
        st.session_state.question_filter = filter_map[filter_type]
        if st.button("Áp dụng bộ lọc"):
            st.rerun()
    
    with col_tools[2]:
        # Chuyển nhanh đến câu
        if st.session_state.study_mode == "sequential":
            selected_index = st.number_input(
                "Chuyển đến câu:",
                min_value=1,
                max_value=total_questions,
                value=st.session_state.current_question_index + 1,
                key="jump_to_question"
            )
            if selected_index - 1 != st.session_state.current_question_index:
                st.session_state.current_question_index = selected_index - 1
                st.rerun()
    
    with col_tools[3]:
        # Nút làm bài thi
        if st.button("📝 Làm bài thi thử", use_container_width=True):
            st.session_state.exam_mode = True
            st.session_state.exam_questions = random.sample(questions_data, min(20, len(questions_data)))
            st.session_state.exam_current_index = 0
            st.session_state.exam_answers = {}
            st.rerun()
    
    # --- THỐNG KÊ ---
    if st.session_state.study_mode == "all":
        results = calculate_results(filtered_questions)
        
        col_stats = st.columns(4)
        with col_stats[0]:
            st.metric("Tổng số câu", results["total"])
        with col_stats[1]:
            st.metric("Đã làm", f"{results['correct'] + results['incorrect']}/{results['total']}")
        with col_stats[2]:
            st.metric("Đúng", results["correct"])
        with col_stats[3]:
            st.metric("Tỷ lệ đúng", f"{results['percentage']:.1f}%")
        
        # Progress bar
        progress = (results['correct'] + results['incorrect']) / results['total'] if results['total'] > 0 else 0
        st.markdown(f"""
        <div class="progress-container">
            <div class="progress-bar" style="width: {progress * 100}%"></div>
        </div>
        <div style="text-align: center; font-size: 0.9rem; color: #666;">
            Tiến độ: {results['correct'] + results['incorrect']}/{results['total']} câu
        </div>
        """, unsafe_allow_html=True)
    
    # --- HIỂN THỊ CÂU HỎI ---
    if st.session_state.study_mode == "sequential":
        # Chế độ từng câu
        current_q = filtered_questions[st.session_state.current_question_index]
        display_question(current_q, st.session_state.current_question_index, total_questions)
        
        # Nút điều hướng
        col_nav = st.columns(4)
        with col_nav[0]:
            if st.button("⬅️ Câu trước", disabled=st.session_state.current_question_index == 0, use_container_width=True):
                st.session_state.current_question_index -= 1
                st.rerun()
        
        with col_nav[1]:
            if st.button("Câu sau ➡️", disabled=st.session_state.current_question_index == total_questions - 1, use_container_width=True):
                st.session_state.current_question_index += 1
                st.rerun()
        
        with col_nav[2]:
            if st.button("❌ Bỏ chọn", use_container_width=True):
                q_id = str(current_q['id'])
                if q_id in st.session_state.user_answers:
                    del st.session_state.user_answers[q_id]
                if q_id in st.session_state.answer_results:
                    del st.session_state.answer_results[q_id]
                st.rerun()
        
        with col_nav[3]:
            if st.button("🔄 Câu ngẫu nhiên", use_container_width=True):
                st.session_state.current_question_index = random.randint(0, total_questions - 1)
                st.rerun()
    
    else:
        # Chế độ tất cả câu
        st.subheader(f"📚 Tất cả câu hỏi ({total_questions} câu)")
        
        # Hiển thị tất cả câu hỏi
        for idx, question in enumerate(filtered_questions):
            display_question(question, idx, total_questions)
            st.divider()

def display_question(question, index, total):
    """Hiển thị một câu hỏi và các đáp án"""
    q_id = str(question['id'])
    is_danger = question.get('danger', False)
    q_type = question.get('type', "Khái niệm")
    
    # Tách loại nếu có nhiều loại
    types = [t.strip() for t in q_type.split(',')] if ',' in q_type else [q_type]
    
    st.markdown(f"""
    <div class="tip-card">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div class="question-header">Câu {question['id']} ({index + 1}/{total})</div>
            <div style="display: flex; gap: 5px;">
                {'<span class="danger-badge">⚠️ ĐIỂM LIỆT</span>' if is_danger else ''}
                {' '.join([f'<span class="type-badge">{t}</span>' for t in types])}
            </div>
        </div>
        <div class="question-content">
            {question['question']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hiển thị hình ảnh (nếu có)
    if question.get('image') and question['image'] not in [None, "null", ""]:
        img_path = os.path.join("images", question['image'])
        if os.path.exists(img_path):
            st.image(img_path, caption="Hình minh họa", use_container_width=True)
    
    # Hiển thị các đáp án
    choices = question.get('choices', [])
    correct_answer = question.get('correct', 0)
    
    # Chuẩn hóa đáp án đúng (có thể là string hoặc number)
    if isinstance(correct_answer, str):
        try:
            correct_answer = int(correct_answer)
        except:
            correct_answer = 0
    
    # Lấy đáp án người dùng đã chọn (nếu có)
    user_answer = st.session_state.user_answers.get(q_id)
    user_correct = st.session_state.answer_results.get(q_id, None)
    
    # Tạo radio buttons cho đáp án
    answer_key = f"answer_{q_id}"
    
    if user_answer is None:
        # Chưa trả lời
        selected_index = st.radio(
            "Chọn đáp án:",
            options=choices,
            index=None,
            key=answer_key,
            horizontal=False
        )
        
        if selected_index is not None:
            selected_idx = choices.index(selected_index)
            st.session_state.user_answers[q_id] = selected_idx
            
            # Kiểm tra đúng/sai
            is_correct = (selected_idx == correct_answer)
            st.session_state.answer_results[q_id] = is_correct
            
            if is_correct:
                st.success("✅ Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Đáp án đúng là: {choices[correct_answer]}")
            
            # Hiển thị giải thích
            display_explanation(question, correct_answer, choices)
    
    else:
        # Đã trả lời - hiển thị kết quả
        is_correct = st.session_state.answer_results[q_id]
        
        # Hiển thị đáp án đã chọn và kết quả
        for i, choice in enumerate(choices):
            css_class = "answer-option"
            if i == user_answer:
                css_class += " selected"
            if i == correct_answer:
                css_class += " correct"
            elif i == user_answer and not is_correct:
                css_class += " incorrect"
            
            st.markdown(f"""
            <div class="{css_class}">
                {'✅ ' if i == correct_answer else '❌ ' if i == user_answer and not is_correct else '○ '}
                {choice}
            </div>
            """, unsafe_allow_html=True)
        
        if is_correct:
            st.success("✅ Bạn đã trả lời đúng câu này!")
        else:
            st.error(f"❌ Bạn đã trả lời sai. Đáp án đúng là: {choices[correct_answer]}")
        
        # Hiển thị giải thích
        display_explanation(question, correct_answer, choices)
        
        # Nút để thay đổi đáp án
        if st.button(f"🔄 Thay đổi đáp án câu {question['id']}", key=f"change_{q_id}"):
            del st.session_state.user_answers[q_id]
            del st.session_state.answer_results[q_id]
            st.rerun()

def display_explanation(question, correct_answer, choices):
    """Hiển thị phần giải thích cho câu hỏi"""
    explanation = question.get('explanation', "Không có giải thích chi tiết.")
    
    if explanation and explanation != "Không có giải thích chi tiết.":
        st.markdown(f"""
        <div class="explanation-box">
            <b>📖 Giải thích:</b><br>
            {explanation}
        </div>
        """, unsafe_allow_html=True)

# --- 7. CHẾ ĐỘ THI THỬ ---
def render_exam_mode(questions_data):
    """Giao diện làm bài thi thử"""
    if 'exam_questions' not in st.session_state:
        st.session_state.exam_mode = False
        st.rerun()
        return
    
    exam_questions = st.session_state.exam_questions
    current_index = st.session_state.exam_current_index
    current_q = exam_questions[current_index]
    total_exam = len(exam_questions)
    
    st.header("📝 BÀI THI THỬ GPLX")
    
    # Thanh tiến độ
    progress = (current_index + 1) / total_exam
    st.markdown(f"""
    <div class="progress-container">
        <div class="progress-bar" style="width: {progress * 100}%"></div>
    </div>
    <div style="text-align: center; font-size: 1rem; font-weight: bold; color: #333;">
        Câu {current_index + 1}/{total_exam}
    </div>
    """, unsafe_allow_html=True)
    
    # Hiển thị câu hỏi thi
    q_id = f"exam_{current_q['id']}"
    
    st.markdown(f"""
    <div class="tip-card">
        <div class="question-header">Câu hỏi số {current_index + 1}</div>
        <div class="question-content">
            {current_q['question']}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hình ảnh (nếu có)
    if current_q.get('image'):
        img_path = os.path.join("images", current_q['image'])
        if os.path.exists(img_path):
            st.image(img_path, caption="Hình minh họa", use_container_width=True)
    
    # Đáp án
    choices = current_q.get('choices', [])
    exam_answer_key = f"exam_answer_{q_id}"
    
    if q_id not in st.session_state.exam_answers:
        selected = st.radio(
            "Chọn đáp án:",
            options=choices,
            index=None,
            key=exam_answer_key,
            horizontal=False
        )
        
        if selected is not None:
            selected_idx = choices.index(selected)
            st.session_state.exam_answers[q_id] = selected_idx
            
            # Tự động chuyển câu sau 2 giây
            with st.spinner("Chuyển câu tiếp theo..."):
                import time
                time.sleep(2)
                if current_index < total_exam - 1:
                    st.session_state.exam_current_index += 1
                else:
                    # Đã hết bài thi, tính kết quả
                    calculate_exam_results(exam_questions)
                st.rerun()
    else:
        # Đã trả lời, hiển thị và cho phép chuyển câu
        st.info("Bạn đã trả lời câu này. Nhấn nút bên dưới để tiếp tục.")
    
    # Nút điều hướng
    col_nav = st.columns(3)
    with col_nav[0]:
        if st.button("⬅️ Câu trước", disabled=current_index == 0, use_container_width=True):
            st.session_state.exam_current_index -= 1
            st.rerun()
    
    with col_nav[1]:
        if st.button("Bỏ qua ➡️", use_container_width=True):
            if current_index < total_exam - 1:
                st.session_state.exam_current_index += 1
            else:
                calculate_exam_results(exam_questions)
            st.rerun()
    
    with col_nav[2]:
        if st.button("🏁 Kết thúc thi", type="primary", use_container_width=True):
            calculate_exam_results(exam_questions)
            st.rerun()
    
    # Hiển thị các câu đã trả lời/chưa trả lời
    st.subheader("Trạng thái các câu hỏi:")
    cols = st.columns(10)
    for i in range(total_exam):
        with cols[i % 10]:
            status = "✅" if f"exam_{exam_questions[i]['id']}" in st.session_state.exam_answers else "⬜"
            if i == current_index:
                st.markdown(f"**{i+1}**", help=f"Câu hiện tại: {i+1}")
            else:
                if st.button(f"{status}{i+1}", key=f"jump_exam_{i}", use_container_width=True):
                    st.session_state.exam_current_index = i
                    st.rerun()

def calculate_exam_results(exam_questions):
    """Tính toán kết quả bài thi"""
    correct = 0
    total = len(exam_questions)
    danger_wrong = 0
    
    for q in exam_questions:
        q_id = f"exam_{q['id']}"
        if q_id in st.session_state.exam_answers:
            user_answer = st.session_state.exam_answers[q_id]
            correct_answer = int(q.get('correct', 0))
            
            if user_answer == correct_answer:
                correct += 1
            elif q.get('danger', False):
                danger_wrong += 1
    
    score = correct
    passed = (correct >= 16) and (danger_wrong == 0)  # Điều kiện đậu: ≥16/20 và không sai câu điểm liệt
    
    st.session_state.exam_results = {
        "total": total,
        "correct": correct,
        "incorrect": total - correct,
        "score": score,
        "danger_wrong": danger_wrong,
        "passed": passed,
        "percentage": (correct / total * 100)
    }
    
    st.session_state.show_exam_results = True

def display_exam_results():
    """Hiển thị kết quả bài thi"""
    results = st.session_state.exam_results
    
    st.header("📊 KẾT QUẢ BÀI THI")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        <div class="stats-box">
            <h3>Thống kê</h3>
            <p>Số câu đúng: <b>{results['correct']}/{results['total']}</b></p>
            <p>Tỷ lệ đúng: <b>{results['percentage']:.1f}%</b></p>
            <p>Số câu sai điểm liệt: <b>{results['danger_wrong']}</b></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if results['passed']:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #4CAF50 0%, #2E7D32 100%); 
                       color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h2>🎉 CHÚC MỪNG!</h2>
                <h3>Bạn đã ĐẬU bài thi</h3>
                <p>Điểm số: {}/{}</p>
            </div>
            """.format(results['correct'], results['total']), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="background: linear-gradient(135deg, #F44336 0%, #C62828 100%); 
                       color: white; padding: 20px; border-radius: 10px; text-align: center;">
                <h2>😔 RẤT TIẾC</h2>
                <h3>Bạn đã TRƯỢT bài thi</h3>
                <p>Lý do: {}</p>
            </div>
            """.format("Sai câu điểm liệt" if results['danger_wrong'] > 0 else "Không đủ điểm đậu"), unsafe_allow_html=True)
    
    # Nút làm lại
    if st.button("🔄 Làm bài thi khác", use_container_width=True, type="primary"):
        st.session_state.exam_mode = False
        st.session_state.show_exam_results = False
        st.rerun()
    
    if st.button("📚 Quay lại học", use_container_width=True):
        st.session_state.exam_mode = False
        st.session_state.show_exam_results = False
        st.rerun()

# --- 8. CHƯƠNG TRÌNH CHÍNH (MAIN) ---
def main():
    # === XỬ LÝ ZOOM FULLSCREEN ===
    if st.session_state.zoomed_image_data:
        st.button("🔙 QUAY LẠI", on_click=lambda: st.session_state.update(zoomed_image_data=None), type="primary", use_container_width=True)
        st.header(st.session_state.zoomed_image_data["title"])
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        return
    
    # === XỬ LÝ KẾT QUẢ THI ===
    if st.session_state.get('show_exam_results', False):
        display_exam_results()
        return
    
    # === CHẾ ĐỘ THI THỬ ===
    if st.session_state.get('exam_mode', False):
        render_exam_mode(load_questions())
        return

    # Tải dữ liệu
    tips_data =
