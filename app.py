import streamlit as st
import json
import os
import random
from PIL import Image
import pandas as pd

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi 600 Câu PRO",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. KHỞI TẠO STATE ---
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = set()
if 'zoomed_image_data' not in st.session_state:
    st.session_state.zoomed_image_data = None
if 'theory_mode' not in st.session_state:
    st.session_state.theory_mode = "tổng_quan"
if 'theory_questions' not in st.session_state:
    st.session_state.theory_questions = []
if 'current_question_idx' not in st.session_state:
    st.session_state.current_question_idx = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
if 'time_left' not in st.session_state:
    st.session_state.time_left = 1080
if 'filtered_questions' not in st.session_state:
    st.session_state.filtered_questions = []
if 'exam_results' not in st.session_state:
    st.session_state.exam_results = None

# --- 3. CSS ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #f0f0f0;
    }
    
    .tip-header {
        color: #b71c1c;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    
    .theory-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 6px solid #4CAF50;
    }
    
    .danger-card {
        border-left: 6px solid #FF4B4B !important;
        background-color: #fff5f5;
    }
    
    .badge {
        font-size: 0.8rem; padding: 4px 8px; border-radius: 12px;
        color: white; font-weight: 600; text-transform: uppercase;
        margin-bottom: 8px; display: inline-block;
    }
    
    .highlight {
        background-color: #ffebee; color: #c62828; font-weight: bold;
        padding: 2px 6px; border-radius: 4px; border: 1px solid #ffcdd2;
    }
    
    .hidden-answer {
        color: #999; font-style: italic; border: 1px dashed #ccc;
        padding: 0 8px; border-radius: 4px;
    }
    
    .stRadio > div {
        background-color: #f8f9fa;
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
    }
    
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM TẢI DỮ LIỆU ---
@st.cache_data
def load_tips_data():
    try:
        with open('data.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        st.error("Không tìm thấy file data.json")
        return []

@st.cache_data
def load_theory_data():
    """Tải dữ liệu lý thuyết 600 câu"""
    # Ưu tiên tìm file questions_full.json
    for file_name in ['questions_full.json', 'questions_enhanced.json', 'data_600_cau.json']:
        try:
            with open(file_name, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict) and 'questions' in data:
                    return data['questions']
                elif isinstance(data, list):
                    return data
        except:
            continue
    
    # Tạo dữ liệu mẫu nếu không có file
    st.warning("Không tìm thấy file dữ liệu 600 câu. Sử dụng dữ liệu mẫu.")
    return create_sample_questions()

def create_sample_questions():
    """Tạo dữ liệu mẫu cho lý thuyết"""
    questions = []
    for i in range(1, 31):  # 30 câu mẫu
        questions.append({
            "id": i,
            "question": f"Câu hỏi mẫu {i}: Khái niệm về làn đường là gì?",
            "choices": [
                f"Đáp án A cho câu {i}",
                f"Đáp án B cho câu {i}",
                f"Đáp án C cho câu {i}",
                f"Đáp án D cho câu {i}"
            ],
            "correct": i % 4,
            "explanation": f"Giải thích cho câu hỏi {i}",
            "danger": True if i <= 5 else False,
            "category": "khái_niệm" if i % 3 == 0 else "biển_báo",
            "chapter": (i % 6) + 1
        })
    return questions

def process_image(image_filename, tip_id):
    """Xử lý ảnh mẹo"""
    try:
        image_path = os.path.join("images", image_filename)
        if os.path.exists(image_path):
            img = Image.open(image_path)
            # Logic xoay ảnh của bạn
            if 1 <= tip_id <= 36:
                img = img.rotate(-270, expand=True)
            elif 37 <= tip_id <= 51:
                img = img.rotate(-90, expand=True)
            return img
    except:
        pass
    return None

# --- 5. HÀM HIỂN THỊ MẸO ---
def render_tip_card(tip, show_answer):
    cat_color = "#1976D2" if "Biển" in tip.get('category', '') else "#388E3C"
    is_bookmarked = tip['id'] in st.session_state.bookmarks
    
    st.markdown(f"""
    <div class="tip-card">
        <span class="badge" style="background-color: {cat_color}">{tip.get('category', 'Chung')}</span>
        <div class="tip-header"><span>{tip['title']}</span></div>
        <div class="tip-content">
    """, unsafe_allow_html=True)
    
    # Nội dung
    for line in tip['content']:
        if "=>" in line:
            parts = line.split("=>")
            q_text, a_text = parts[0], parts[1]
            if show_answer:
                st.markdown(f"• {q_text} <span class='highlight'>👉 {a_text}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"• {q_text} <span class='hidden-answer'>???</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"• {line}")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Ảnh
    if tip.get('image'):
        img = process_image(tip['image'], tip.get('id', 0))
        if img:
            st.image(img, use_container_width=True)
            if st.button("🔍 Phóng to ảnh", key=f"zoom_{tip['id']}", use_container_width=True):
                st.session_state.zoomed_image_data = {"image": img, "title": tip['title']}
                st.rerun()
    
    # Bookmark
    if st.checkbox("Lưu", value=is_bookmarked, key=f"bk_{tip['id']}"):
        st.session_state.bookmarks.add(tip['id'])
    else:
        st.session_state.bookmarks.discard(tip['id'])
    
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. HÀM LÝ THUYẾT ---
def render_theory_dashboard():
    """Tổng quan lý thuyết"""
    st.title("📚 Lý Thuyết 600 Câu")
    
    # Thống kê
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tổng số câu", len(st.session_state.theory_questions))
    with col2:
        answered = len([k for k in st.session_state.user_answers.keys() if k.startswith("theory_")])
        st.metric("Đã ôn", answered)
    with col3:
        danger_q = len([q for q in st.session_state.theory_questions if q.get('danger', False)])
        st.metric("Câu liệt", danger_q)
    
    st.markdown("---")
    
    # Các chương
    chapters = {
        1: "Quy định chung",
        2: "Văn hóa giao thông", 
        3: "Kỹ thuật lái xe",
        4: "Cấu tạo sửa chữa",
        5: "Báo hiệu đường bộ",
        6: "Sa hình & Xử lý"
    }
    
    st.subheader("📂 Nội dung ôn tập")
    cols = st.columns(3)
    
    for i, (chap_num, chap_name) in enumerate(chapters.items()):
        with cols[i % 3]:
            count = len([q for q in st.session_state.theory_questions if q.get('chapter') == chap_num])
            st.metric(chap_name, f"{count} câu")
            if st.button(f"Ôn tập {chap_name}", key=f"chap_{chap_num}", use_container_width=True):
                st.session_state.filtered_questions = [
                    q for q in st.session_state.theory_questions 
                    if q.get('chapter') == chap_num
                ]
                st.session_state.theory_mode = "ôn_tập"
                st.session_state.current_question_idx = 0
                st.rerun()
    
    st.markdown("---")
    
    # Câu liệt
    st.subheader("⚠️ 60 Câu Hỏi Liệt")
    st.warning("Sai 1 câu là TRƯỢT!")
    
    if st.button("🎯 Ôn 60 câu liệt ngay", use_container_width=True, type="primary"):
        danger_questions = [q for q in st.session_state.theory_questions if q.get('danger', False)]
        st.session_state.filtered_questions = danger_questions[:10]  # Giới hạn 10 câu mẫu
        st.session_state.theory_mode = "ôn_tập"
        st.session_state.current_question_idx = 0
        st.rerun()
    
    st.markdown("---")
    
    # Thi thử
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Thi thử 20 câu", use_container_width=True):
            st.session_state.filtered_questions = random.sample(st.session_state.theory_questions, min(20, len(st.session_state.theory_questions)))
            st.session_state.theory_mode = "thi_thử"
            st.session_state.test_started = True
            st.session_state.current_question_idx = 0
            st.session_state.time_left = 600
            st.rerun()
    with col2:
        if st.button("📖 Ôn tập tất cả", use_container_width=True):
            st.session_state.filtered_questions = st.session_state.theory_questions
            st.session_state.theory_mode = "ôn_tập"
            st.session_state.current_question_idx = 0
            st.rerun()

def render_theory_question():
    """Hiển thị 1 câu hỏi"""
    if not st.session_state.filtered_questions:
        st.warning("Không có câu hỏi nào!")
        return
    
    q = st.session_state.filtered_questions[st.session_state.current_question_idx]
    total = len(st.session_state.filtered_questions)
    
    # Header
    st.subheader(f"📝 Câu {st.session_state.current_question_idx + 1}/{total}")
    if q.get('danger'):
        st.error("⚠️ Câu liệt - Sai là trượt!")
    
    # Câu hỏi
    st.markdown(f"### {q['question']}")
    
    # Đáp án
    q_key = f"theory_{q['id']}"
    user_answer = st.session_state.user_answers.get(q_key)
    
    if user_answer is not None:
        # Đã trả lời
        for i, choice in enumerate(q["choices"]):
            if i == user_answer:
                if user_answer == q["correct"]:
                    st.success(f"✅ **{chr(65+i)}.** {choice}")
                else:
                    st.error(f"❌ **{chr(65+i)}.** {choice}")
            elif i == q["correct"]:
                st.info(f"✓ **{chr(65+i)}.** {choice}")
            else:
                st.markdown(f"**{chr(65+i)}.** {choice}")
        
        # Giải thích
        if q.get("explanation"):
            with st.expander("📖 Giải thích"):
                st.info(q["explanation"])
        
        # Nút tiếp
        if st.button("👉 Câu tiếp theo", use_container_width=True):
            if st.session_state.current_question_idx < total - 1:
                st.session_state.current_question_idx += 1
            st.rerun()
    else:
        # Chưa trả lời
        selected = st.radio(
            "Chọn đáp án:",
            [f"**{chr(65+i)}.** {choice}" for i, choice in enumerate(q["choices"])]
        )
        
        if selected:
            selected_idx = ord(selected[2]) - 65  # Lấy vị trí từ A, B, C, D
            st.session_state.user_answers[q_key] = selected_idx
            st.rerun()
    
    # Điều hướng
    st.markdown("---")
    cols = st.columns(4)
    with cols[0]:
        if st.button("◀️ Trước") and st.session_state.current_question_idx > 0:
            st.session_state.current_question_idx -= 1
            st.rerun()
    with cols[1]:
        if st.button("🔀 Ngẫu nhiên"):
            st.session_state.current_question_idx = random.randint(0, total-1)
            st.rerun()
    with cols[2]:
        if st.button("Tiếp theo ▶️") and st.session_state.current_question_idx < total - 1:
            st.session_state.current_question_idx += 1
            st.rerun()
    with cols[3]:
        if st.button("🏠 Về tổng quan"):
            st.session_state.theory_mode = "tổng_quan"
            st.rerun()

def render_theory_exam():
    """Thi thử"""
    st.subheader("📝 Thi thử sát hạch")
    
    if not st.session_state.test_started:
        st.info("Thi thử 20 câu - Thời gian: 10 phút")
        if st.button("▶️ Bắt đầu thi", type="primary", use_container_width=True):
            st.session_state.test_started = True
            st.rerun()
    else:
        # Đếm thời gian
        minutes = st.session_state.time_left // 60
        seconds = st.session_state.time_left % 60
        st.progress(st.session_state.time_left / 600, 
                   text=f"⏱️ {minutes:02d}:{seconds:02d}")
        
        # Hiển thị câu hỏi
        render_theory_question()
        
        # Nút kết thúc
        if st.button("⏹️ Kết thúc thi", type="secondary"):
            show_exam_results()
    
    # Tự động giảm thời gian
    if st.session_state.time_left > 0:
        st.session_state.time_left -= 1

def show_exam_results():
    """Hiển thị kết quả thi"""
    correct = 0
    danger_wrong = False
    results = []
    
    for q in st.session_state.filtered_questions:
        q_key = f"theory_{q['id']}"
        user_answer = st.session_state.user_answers.get(q_key, -1)
        is_correct = user_answer == q["correct"]
        
        if is_correct:
            correct += 1
        elif q.get('danger'):
            danger_wrong = True
        
        results.append({
            "Câu": q["id"],
            "Kết quả": "✅ Đúng" if is_correct else "❌ Sai",
            "Loại": "⚠️ Liệt" if q.get('danger') else "📌 Thường"
        })
    
    st.session_state.exam_results = {
        "total": len(st.session_state.filtered_questions),
        "correct": correct,
        "danger_wrong": danger_wrong
    }
    st.session_state.theory_mode = "kết_quả"
    st.rerun()

def render_results():
    """Hiển thị kết quả"""
    if not st.session_state.exam_results:
        st.info("Chưa có kết quả")
        return
    
    r = st.session_state.exam_results
    st.subheader("📊 Kết Quả Bài Thi")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tổng câu", r["total"])
    with col2:
        st.metric("Đúng", r["correct"])
    with col3:
        score = (r["correct"] / r["total"]) * 100
        if score >= 80 and not r["danger_wrong"]:
            st.success(f"🎉 {score:.1f}%")
        else:
            st.error(f"💥 {score:.1f}%")
    
    if r["danger_wrong"]:
        st.error("⚠️ Bạn đã sai câu liệt - KHÔNG ĐẠT!")
    
    if st.button("🔄 Làm bài khác", use_container_width=True):
        st.session_state.theory_mode = "tổng_quan"
        st.session_state.exam_results = None
        st.rerun()

# --- 7. MAIN APP ---
def main():
    # Tải dữ liệu
    if not st.session_state.theory_questions:
        st.session_state.theory_questions = load_theory_data()
    
    # Xử lý ảnh phóng to
    if st.session_state.zoomed_image_data:
        st.button("🔙 Quay lại", 
                 on_click=lambda: st.session_state.update(zoomed_image_data=None),
                 use_container_width=True)
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        return
    
    # Sidebar
    st.sidebar.title("🚗 ÔN THI LÁI XE")
    mode = st.sidebar.radio("Chế độ học:", ["📖 Học Mẹo", "📚 Lý Thuyết"])
    
    if mode == "📖 Học Mẹo":
        # Học mẹo
        data = load_tips_data()
        if not data:
            return
        
        with st.sidebar:
            show_answer = st.radio("Hiển thị:", ["Xem đáp án", "Che đáp án"]) == "Xem đáp án"
            filter_bookmark = st.checkbox("Chỉ hiện mẹo đã lưu")
        
        st.title("🚗 HỌC MẸO THI LÁI XE")
        search = st.text_input("🔍 Tìm kiếm:", placeholder="Nhập từ khóa...")
        
        filtered = data
        if search:
            filtered = [t for t in filtered if search.lower() in t['title'].lower()]
        if filter_bookmark:
            filtered = [t for t in filtered if t['id'] in st.session_state.bookmarks]
        
        for tip in filtered:
            render_tip_card(tip, show_answer)
    
    else:
        # Lý thuyết
        st.sidebar.markdown("---")
        st.sidebar.markdown("### ⚙️ Lý thuyết")
        
        if st.session_state.theory_mode in ["ôn_tập", "thi_thử"]:
            if st.sidebar.button("🔄 Xáo trộn"):
                random.shuffle(st.session_state.filtered_questions)
                st.rerun()
        
        if st.sidebar.button("🗑️ Xóa kết quả"):
            st.session_state.user_answers = {}
            st.session_state.theory_mode = "tổng_quan"
            st.rerun()
        
        # Main content lý thuyết
        if st.session_state.theory_mode == "tổng_quan":
            render_theory_dashboard()
        elif st.session_state.theory_mode == "ôn_tập":
            render_theory_question()
        elif st.session_state.theory_mode == "thi_thử":
            render_theory_exam()
        elif st.session_state.theory_mode == "kết_quả":
            render_results()

if __name__ == "__main__":
    main()
