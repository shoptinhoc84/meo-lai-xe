import streamlit as st
import json
import random
import os
from datetime import datetime, timedelta
import pandas as pd
import plotly.express as px
from PIL import Image

# Cấu hình trang
st.set_page_config(
    page_title="Thi Sát Hạch Lái Xe 600 Câu",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS tùy chỉnh
st.markdown("""
<style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .stButton > button {
        width: 100%;
        margin: 5px 0;
    }
    .category-card {
        padding: 20px;
        border-radius: 10px;
        background-color: #f0f2f6;
        margin: 10px 0;
        border-left: 5px solid #4CAF50;
    }
    .danger-card {
        border-left: 5px solid #FF4B4B;
        background-color: #ffe6e6;
    }
    .question-image {
        max-width: 300px;
        margin: 10px auto;
        display: block;
        border: 2px solid #ddd;
        border-radius: 8px;
        padding: 5px;
    }
    .result-correct {
        color: #4CAF50;
        font-weight: bold;
    }
    .result-wrong {
        color: #FF4B4B;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Load dữ liệu
@st.cache_data
def load_enhanced_questions():
    """Load câu hỏi với phân loại nâng cao"""
    try:
        with open("data/questions_enhanced.json", "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # Thêm thống kê phân loại
        categories = {}
        tags = {}
        for q in data["questions"]:
            cat = q.get("category", "khác")
            categories[cat] = categories.get(cat, 0) + 1
            
            for tag in q.get("tags", []):
                tags[tag] = tags.get(tag, 0) + 1
        
        data["stats"] = {
            "categories": categories,
            "tags": tags
        }
        
        return data
    except FileNotFoundError:
        # Fallback nếu file không tồn tại
        st.error("File dữ liệu không tồn tại. Tạo file mẫu...")
        return create_sample_data()

@st.cache_data
def load_danger_questions():
    try:
        with open("data/danger_questions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {"questions": []}

def create_sample_data():
    """Tạo dữ liệu mẫu nếu file không tồn tại"""
    return {
        "meta": {
            "title": "600 Câu Hỏi Sát Hạch",
            "year": 2025,
            "total_questions": 600
        },
        "questions": [],
        "stats": {"categories": {}, "tags": {}}
    }

def load_image(image_path):
    """Load và hiển thị hình ảnh"""
    if not image_path:
        return None
    
    full_path = os.path.join("data", "images", image_path)
    if os.path.exists(full_path):
        try:
            return Image.open(full_path)
        except:
            return None
    return None

# Khởi tạo session state
def init_session_state():
    defaults = {
        "current_question": 0,
        "answers": {},
        "test_started": False,
        "time_left": 1080,
        "mode": "dashboard",  # dashboard, study, exam, practice, category
        "selected_category": None,
        "selected_tags": [],
        "show_explanation": True,
        "exam_results": None,
        "question_order": [],
        "filtered_questions": []
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Load dữ liệu
data = load_enhanced_questions()
questions = data["questions"]
stats = data["stats"]
danger_data = load_danger_questions()
danger_questions = danger_data.get("questions", [])

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1998/1998610.png", width=80)
    st.title("🚗 Ôn Thi Lái Xe")
    
    # Menu chính
    menu = st.radio(
        "Chế độ học tập",
        ["📊 Tổng quan", "📚 Ôn tập theo nội dung", "🎯 60 Câu liệt", 
         "📝 Thi thử đầy đủ", "⚡ Thi nhanh", "📈 Kết quả & Thống kê"]
    )
    
    st.markdown("---")
    
    # Cài đặt
    with st.expander("⚙️ Cài đặt"):
        st.session_state.show_explanation = st.checkbox("Hiển thị giải thích", value=True)
        auto_next = st.checkbox("Tự động chuyển câu", value=True)
        
        if st.session_state.mode in ["study", "category"]:
            shuffle = st.checkbox("Xáo trộn câu hỏi", value=False)
            if shuffle and st.button("🔀 Xáo trộn ngay"):
                random.shuffle(st.session_state.filtered_questions)
                st.rerun()
    
    st.markdown("---")
    
    # Thống kê nhanh
    st.caption("📊 Thống kê nhanh")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Tổng câu", len(questions))
    with col2:
        st.metric("Đã trả lời", len(st.session_state.answers))
    
    # Nút reset
    if st.button("🔄 Đặt lại bài thi", use_container_width=True):
        for key in ["answers", "test_started", "exam_results", "question_order"]:
            if key in st.session_state:
                st.session_state[key] = None if key == "exam_results" else 0
        st.session_state.mode = "dashboard"
        st.rerun()
    
    st.markdown("---")
    st.caption(f"© {data['meta']['year']}")

# Xử lý menu chính
if menu == "📊 Tổng quan":
    st.session_state.mode = "dashboard"
elif menu == "📚 Ôn tập theo nội dung":
    st.session_state.mode = "category"
elif menu == "🎯 60 Câu liệt":
    st.session_state.mode = "danger"
elif menu == "📝 Thi thử đầy đủ":
    st.session_state.mode = "exam"
elif menu == "⚡ Thi nhanh":
    st.session_state.mode = "practice"
elif menu == "📈 Kết quả & Thống kê":
    st.session_state.mode = "results"

# Header chính
st.title(data["meta"]["title"])
st.markdown("---")

# ==================== DASHBOARD ====================
if st.session_state.mode == "dashboard":
    st.subheader("🎯 Tổng quan & Phân loại câu hỏi")
    
    # Thống kê phân loại
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Tổng số câu", len(questions))
    with col2:
        st.metric("Câu có hình ảnh", len([q for q in questions if q.get("has_image")]))
    with col3:
        st.metric("Câu nguy hiểm", len(danger_questions))
    
    # Phân bổ theo danh mục
    st.subheader("📂 Phân loại nội dung")
    
    # Tạo cards cho từng danh mục
    categories = {
        "khái_niệm": {"icon": "📖", "name": "Khái niệm & Quy tắc", "color": "#4CAF50"},
        "độ_tuổi": {"icon": "🎂", "name": "Độ tuổi lái xe", "color": "#2196F3"},
        "biển_báo": {"icon": "🚸", "name": "Biển báo đường bộ", "color": "#FF9800"},
        "kỹ_thuật_lái_xe": {"icon": "🔧", "name": "Kỹ thuật lái xe", "color": "#9C27B0"},
        "cấu_tạo_sửa_chữa": {"icon": "🚗", "name": "Cấu tạo & Sửa chữa", "color": "#607D8B"},
        "tốc_độ_khoảng_cách": {"icon": "📏", "name": "Tốc độ & Khoảng cách", "color": "#795548"},
        "hành_vi": {"icon": "🚦", "name": "Hành vi & Xử lý", "color": "#00BCD4"},
        "ưu_tiên": {"icon": "⭐", "name": "Ưu tiên & Nhường đường", "color": "#FF5722"}
    }
    
    # Hiển thị cards
    cols = st.columns(4)
    col_idx = 0
    
    for cat_id, cat_info in categories.items():
        count = stats["categories"].get(cat_id, 0)
        with cols[col_idx]:
            with st.container():
                st.markdown(f"""
                <div style='padding: 15px; border-radius: 10px; background-color: {cat_info['color']}20; 
                            border-left: 5px solid {cat_info['color']}; margin: 5px 0;'>
                    <h4 style='margin: 0;'>{cat_info['icon']} {cat_info['name']}</h4>
                    <p style='font-size: 24px; font-weight: bold; margin: 5px 0;'>{count} câu</p>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Ôn tập {cat_info['name']}", key=f"cat_{cat_id}", use_container_width=True):
                    st.session_state.selected_category = cat_id
                    st.session_state.mode = "category"
                    st.session_state.filtered_questions = [q for q in questions if q.get("category") == cat_id]
                    st.rerun()
        
        col_idx = (col_idx + 1) % 4
    
    # 60 câu liệt - card đặc biệt
    st.markdown("---")
    with st.container():
        st.markdown("""
        <div class='danger-card' style='padding: 20px; border-radius: 10px; margin: 10px 0;'>
            <h3 style='color: #FF4B4B; margin: 0;'>⚠️ 60 CÂU HỎI LIỆT</h3>
            <p style='margin: 5px 0;'><strong>Sai 1 câu là TRƯỢT!</strong></p>
            <p>Đây là những câu hỏi quan trọng nhất trong bài thi</p>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.progress(0, text="Chưa ôn tập")
        with col2:
            if st.button("🎯 Bắt đầu ôn 60 câu liệt", use_container_width=True):
                st.session_state.mode = "danger"
                st.rerun()
    
    # Biểu đồ thống kê
    st.markdown("---")
    st.subheader("📈 Phân bổ câu hỏi")
    
    if stats["categories"]:
        df_categories = pd.DataFrame({
            "Danh mục": [categories.get(cat, {"name": cat})["name"] for cat in stats["categories"].keys()],
            "Số câu": list(stats["categories"].values())
        })
        
        fig = px.pie(df_categories, values="Số câu", names="Danh mục", 
                     title="Phân bổ câu hỏi theo danh mục")
        st.plotly_chart(fig, use_container_width=True)

# ==================== ÔN TẬP THEO DANH MỤC ====================
elif st.session_state.mode == "category":
    if not st.session_state.filtered_questions:
        # Chọn danh mục nếu chưa chọn
        st.subheader("📚 Chọn nội dung ôn tập")
        
        # Lọc theo tag phổ biến
        popular_tags = sorted(stats["tags"].items(), key=lambda x: x[1], reverse=True)[:10]
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            selected_cat = st.selectbox(
                "Chọn danh mục chính",
                options=["Tất cả"] + list(categories.keys()),
                format_func=lambda x: categories.get(x, {"name": "Tất cả"})["name"]
            )
        
        with col2:
            if selected_cat != "Tất cả":
                tag_options = list(set([
                    tag for q in questions 
                    if q.get("category") == selected_cat 
                    for tag in q.get("tags", [])
                ]))
                if tag_options:
                    selected_tags = st.multiselect("Lọc theo tag", tag_options)
                    st.session_state.selected_tags = selected_tags
        
        if st.button("🔍 Bắt đầu ôn tập", type="primary", use_container_width=True):
            if selected_cat == "Tất cả":
                filtered = questions
            else:
                filtered = [q for q in questions if q.get("category") == selected_cat]
            
            if st.session_state.selected_tags:
                filtered = [q for q in filtered 
                          if any(tag in q.get("tags", []) for tag in st.session_state.selected_tags)]
            
            st.session_state.filtered_questions = filtered
            st.session_state.current_question = 0
            st.rerun()
    else:
        # Hiển thị câu hỏi
        display_questions()

# ==================== 60 CÂU LIỆT ====================
elif st.session_state.mode == "danger":
    st.subheader("🎯 60 Câu Hỏi Liệt (Nguy Hiểm)")
    
    if not st.session_state.test_started:
        st.warning("""
        ⚠️ **QUAN TRỌNG:** 
        - Sai 1 câu trong nhóm này là KHÔNG ĐẠT
        - Cần học kỹ trước khi thi thật
        """)
        
        if st.button("▶️ Bắt đầu ôn 60 câu liệt", type="primary"):
            st.session_state.test_started = True
            st.session_state.filtered_questions = danger_questions
            st.session_state.current_question = 0
            st.rerun()
    else:
        display_questions()

# ==================== THI THỬ ====================
elif st.session_state.mode in ["exam", "practice"]:
    handle_exam_mode()

# ==================== HIỂN THỊ KẾT QUẢ ====================
elif st.session_state.mode == "results":
    show_results()

# ==================== CÁC HÀM HỖ TRỢ ====================

def display_questions():
    """Hiển thị câu hỏi và đáp án"""
    if not st.session_state.filtered_questions:
        st.warning("Không có câu hỏi nào!")
        return
    
    total = len(st.session_state.filtered_questions)
    current_idx = st.session_state.current_question % total
    
    q = st.session_state.filtered_questions[current_idx]
    
    # Header với thông tin
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        category_name = categories.get(q.get("category", ""), {"name": "Khác"})["name"]
        st.subheader(f"📝 Câu {current_idx + 1}/{total} • {category_name}")
    with col2:
        if q.get("danger"):
            st.error("⚠️ Câu liệt")
        else:
            st.info("📌 Câu thường")
    with col3:
        progress = (current_idx + 1) / total
        st.progress(progress, text=f"{current_idx + 1}/{total}")
    
    # Hiển thị câu hỏi
    st.markdown(f"### {q['question']}")
    
    # Hiển thị hình ảnh nếu có
    if q.get("has_image") and q.get("image"):
        img = load_image(q["image"])
        if img:
            st.image(img, use_container_width=True, caption="Hình minh họa")
    
    # Hiển thị đáp án
    q_key = f"q_{q['id']}"
    user_answer = st.session_state.answers.get(q_key)
    
    # Tạo options
    options = q["choices"]
    option_labels = [f"**{chr(65+i)}.** {opt}" for i, opt in enumerate(options)]
    
    if user_answer is not None:
        # Đã trả lời
        selected_label = option_labels[user_answer]
        
        # Radio disabled với đáp án đã chọn
        st.radio(
            "Đáp án của bạn:",
            option_labels,
            index=user_answer,
            disabled=True,
            key=f"radio_{q_key}_result"
        )
        
        # Kiểm tra đúng/sai
        is_correct = user_answer == q["correct"]
        
        if is_correct:
            st.success(f"✅ **ĐÚNG!** Đáp án: {chr(65 + q['correct'])}")
        else:
            st.error(f"❌ **SAI!** Đáp án đúng: {chr(65 + q['correct'])}")
        
        # Hiển thị giải thích
        if st.session_state.show_explanation and q.get("explanation"):
            with st.expander("📖 Giải thích chi tiết"):
                st.info(q["explanation"])
                
                # Hiển thị tags nếu có
                if q.get("tags"):
                    tags_html = " ".join([f"<span style='background-color: #e0e0e0; padding: 2px 8px; border-radius: 10px; margin: 2px; display: inline-block;'>🏷️ {tag}</span>" 
                                          for tag in q["tags"]])
                    st.markdown(f"**Tags:** {tags_html}", unsafe_allow_html=True)
        
        # Nút tiếp tục
        if st.button("👉 Câu tiếp theo", use_container_width=True):
            if current_idx < total - 1:
                st.session_state.current_question += 1
            else:
                st.session_state.current_question = 0
            st.rerun()
            
    else:
        # Chưa trả lời - cho phép chọn
        selected = st.radio(
            "Chọn đáp án:",
            option_labels,
            key=f"radio_{q_key}"
        )
        
        if selected:
            selected_idx = option_labels.index(selected)
            st.session_state.answers[q_key] = selected_idx
            
            # Tự động chuyển nếu đang ở chế độ thi
            if st.session_state.mode in ["exam", "practice", "danger"]:
                if current_idx < total - 1:
                    st.session_state.current_question += 1
                    st.rerun()
    
    # Điều hướng
    st.markdown("---")
    nav_cols = st.columns(5)
    with nav_cols[0]:
        if st.button("⏮️ Đầu"):
            st.session_state.current_question = 0
            st.rerun()
    with nav_cols[1]:
        if st.button("◀️ Trước"):
            if current_idx > 0:
                st.session_state.current_question -= 1
            st.rerun()
    with nav_cols[2]:
        if st.button("🔀 Ngẫu nhiên"):
            st.session_state.current_question = random.randint(0, total-1)
            st.rerun()
    with nav_cols[3]:
        if st.button("Tiếp theo ▶️"):
            if current_idx < total - 1:
                st.session_state.current_question += 1
            st.rerun()
    with nav_cols[4]:
        if st.button("Cuối ⏭️"):
            st.session_state.current_question = total - 1
            st.rerun()
    
    # Thanh progress chi tiết
    st.markdown("### 📊 Tiến độ ôn tập")
    
    # Tính số câu đã làm
    answered_ids = [int(k.split("_")[1]) for k in st.session_state.answers.keys()]
    current_answered = [q_id for q_id in answered_ids 
                       if q_id in [q["id"] for q in st.session_state.filtered_questions]]
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Đã ôn", f"{len(current_answered)}/{total}")
    with col2:
        if current_answered:
            correct_count = sum(1 for q_id in current_answered 
                              for q in st.session_state.filtered_questions 
                              if q["id"] == q_id and 
                              st.session_state.answers.get(f"q_{q_id}") == q["correct"])
            st.metric("Đúng", f"{correct_count}/{len(current_answered)}")
        else:
            st.metric("Đúng", "0/0")
    with col3:
        if st.button("📈 Xem kết quả chi tiết"):
            st.session_state.mode = "results"
            st.rerun()

def handle_exam_mode():
    """Xử lý chế độ thi thử"""
    st.subheader("📝 Thi thử sát hạch")
    
    if not st.session_state.test_started:
        if st.session_state.mode == "exam":
            st.info("""
            **Thi thử đầy đủ 600 câu:**
            - Thời gian: 18 phút (1080 giây)
            - Số câu: 600
            - Điểm đạt: 80% (480/600 câu)
            - Sai câu liệt: TRƯỢT
            """)
            
            if st.button("▶️ Bắt đầu thi 600 câu", type="primary", use_container_width=True):
                st.session_state.test_started = True
                st.session_state.time_left = 1080
                st.session_state.filtered_questions = random.sample(questions, 600)
                st.session_state.current_question = 0
                st.rerun()
                
        else:  # practice mode
            col1, col2 = st.columns(2)
            with col1:
                num_q = st.number_input("Số câu thi", min_value=10, max_value=200, value=30)
            with col2:
                time_per_q = st.number_input("Thời gian/câu (giây)", min_value=10, max_value=120, value=20)
            
            if st.button(f"▶️ Bắt đầu thi {num_q} câu", type="primary", use_container_width=True):
                st.session_state.test_started = True
                st.session_state.time_left = num_q * time_per_q
                st.session_state.filtered_questions = random.sample(questions, num_q)
                st.session_state.current_question = 0
                st.rerun()
    else:
        # Đang thi
        display_exam_in_progress()

def display_exam_in_progress():
    """Hiển thị bài thi đang diễn ra"""
    # Thanh thời gian
    time_col1, time_col2 = st.columns([3, 1])
    with time_col1:
        minutes = st.session_state.time_left // 60
        seconds = st.session_state.time_left % 60
        
        # Thanh progress thời gian
        total_time = 1080 if st.session_state.mode == "exam" else len(st.session_state.filtered_questions) * 20
        time_progress = st.session_state.time_left / total_time
        
        st.progress(time_progress, 
                   text=f"⏱️ Thời gian còn lại: {minutes:02d}:{seconds:02d}")
    
    with time_col2:
        if st.button("⏹️ Kết thúc thi", type="secondary"):
            calculate_exam_results()
            st.rerun()
    
    # Hiển thị câu hỏi (không có giải thích trong lúc thi)
    temp_show = st.session_state.show_explanation
    st.session_state.show_explanation = False
    display_questions()
    st.session_state.show_explanation = temp_show
    
    # Tự động đếm thời gian
    if st.session_state.time_left > 0:
        st.session_state.time_left -= 1
        if st.session_state.time_left == 0:
            st.error("⏰ Hết giờ!")
            calculate_exam_results()

def calculate_exam_results():
    """Tính kết quả bài thi"""
    results = []
    total_questions = len(st.session_state.filtered_questions)
    correct_count = 0
    danger_wrong = False
    
    for q in st.session_state.filtered_questions:
        q_key = f"q_{q['id']}"
        user_answer = st.session_state.answers.get(q_key, -1)
        is_correct = user_answer == q["correct"]
        
        if is_correct:
            correct_count += 1
        elif q.get("danger"):
            danger_wrong = True
        
        results.append({
            "Câu": q["id"],
            "Nội dung": q["question"][:50] + "..." if len(q["question"]) > 50 else q["question"],
            "Đáp án bạn chọn": chr(65 + user_answer) if user_answer >= 0 else "Chưa trả lời",
            "Đáp án đúng": chr(65 + q["correct"]),
            "Kết quả": "✅ Đúng" if is_correct else "❌ Sai",
            "Loại": "⚠️ Liệt" if q.get("danger") else "📌 Thường"
        })
    
    score = (correct_count / total_questions) * 100
    passed = score >= 80 and not danger_wrong
    
    st.session_state.exam_results = {
        "total": total_questions,
        "correct": correct_count,
        "score": score,
        "passed": passed,
        "danger_wrong": danger_wrong,
        "details": results
    }
    
    st.session_state.mode = "results"
    st.session_state.test_started = False

def show_results():
    """Hiển thị kết quả chi tiết"""
    if not st.session_state.exam_results:
        st.info("Chưa có kết quả bài thi nào. Hãy làm bài thi trước!")
        return
    
    results = st.session_state.exam_results
    
    st.subheader("📊 Kết Quả Bài Thi")
    
    # Thông tin tổng quan
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Tổng số câu", results["total"])
    with col2:
        st.metric("Số câu đúng", results["correct"])
    with col3:
        st.metric("Tỷ lệ đúng", f"{results['score']:.1f}%")
    with col4:
        if results["passed"]:
            st.success("🎉 ĐẠT")
        else:
            st.error("💥 KHÔNG ĐẠT")
    
    # Cảnh báo câu liệt
    if results["danger_wrong"]:
        st.error("""
        ⚠️ **KHÔNG ĐẠT VÌ SAI CÂU LIỆT!**
        
        Bạn đã trả lời sai ít nhất 1 câu trong nhóm 60 câu hỏi liệt.
        Trong kỳ thi thật, bạn sẽ bị đánh trượt ngay lập tức.
        """)
    
    # Biểu đồ
    st.markdown("### 📈 Biểu đồ kết quả")
    
    df_results = pd.DataFrame({
        "Loại": ["Đúng", "Sai"],
        "Số câu": [results["correct"], results["total"] - results["correct"]]
    })
    
    fig = px.pie(df_results, values="Số câu", names="Loại", 
                 color_discrete_map={"Đúng": "#4CAF50", "Sai": "#FF4B4B"})
    st.plotly_chart(fig, use_container_width=True)
    
    # Chi tiết từng câu
    st.markdown("### 📋 Chi tiết từng câu")
    
    df_details = pd.DataFrame(results["details"])
    st.dataframe(df_details, use_container_width=True, hide_index=True)
    
    # Phân tích theo loại câu hỏi
    st.markdown("### 🔍 Phân tích theo nội dung")
    
    # Xuất kết quả
    st.markdown("### 💾 Xuất kết quả")
    
    csv = df_details.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Tải kết quả (CSV)",
        data=csv,
        file_name=f"ket_qua_thi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv"
    )
    
    # Nút làm lại
    if st.button("🔄 Làm bài thi khác", type="primary", use_container_width=True):
        st.session_state.mode = "dashboard"
        st.session_state.exam_results = None
        st.rerun()

# Footer
st.markdown("---")
st.caption(f"📚 {data['meta']['title']} • © {data['meta']['year']} • Phiên bản 2.0 với phân loại nâng cao")