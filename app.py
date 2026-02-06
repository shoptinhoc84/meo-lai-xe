import streamlit as st
import json
import os
import time
import random
from datetime import datetime
from PIL import Image, ImageOps
import pandas as pd

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="GPLX Pro - Full Mẹo 2026",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"  # Mở sidebar để hiển thị thống kê
)

# --- 2. KHỞI TẠO SESSION STATE ---
DEFAULT_STATES = {
    'page': "home",
    'license_type': "Xe máy (A1, A2)",
    'current_q_index': 0,
    'bookmarked_questions': [],
    'wrong_questions': [],
    'practice_history': [],
    'mock_exam_score': None,
    'last_mock_exam': None,
    'total_questions_attempted': 0,
    'total_correct': 0,
    'exam_started': False,
    'exam_questions': [],
    'exam_answers': [],
    'exam_time_left': 1200,  # 20 phút = 1200 giây
    'exam_finished': False
}

for key, value in DEFAULT_STATES.items():
    if key not in st.session_state:
        st.session_state[key] = value

# --- 3. CSS GIAO DIỆN NÂNG CẤP ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #f8fafc; }
    
    .block-container { 
        padding-top: 2rem !important; 
        padding-bottom: 3rem !important; 
        max-width: 1400px;
    }

    /* HERO CARD */
    .hero-card {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        padding: 40px; border-radius: 30px; color: white; text-align: center; 
        margin-bottom: 30px; box-shadow: 0 20px 40px rgba(37, 99, 235, 0.15);
    }
    
    /* SECTION TITLE */
    .section-title {
        font-size: 2rem; font-weight: 800; color: #1e293b;
        margin: 20px 0 15px 0; padding-bottom: 5px; border-bottom: 5px solid #3b82f6; 
        display: inline-block;
    }

    /* TIP BOX */
    .tip-box {
        background: white; border-radius: 18px; padding: 25px; margin-bottom: 20px;
        border-left: 12px solid #3b82f6; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    .tip-box:hover {
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.12);
    }
    .tip-title { 
        color: #1e293b; font-weight: 800; font-size: 1.6rem; 
        margin-bottom: 10px; text-transform: uppercase; letter-spacing: 0.5px;
    }
    .tip-content { 
        color: #334155; font-size: 1.3rem; line-height: 1.6; font-weight: 500;
    }
    
    /* HIGHLIGHT */
    .hl-red { color: #e11d48; font-weight: 800; background: #fff1f2; padding: 2px 8px; border-radius: 8px; }
    .hl-blue { color: #2563eb; font-weight: 800; background: #eff6ff; padding: 2px 8px; border-radius: 8px; }
    .hl-green { color: #059669; font-weight: 800; background: #d1fae5; padding: 2px 8px; border-radius: 8px; }

    /* RADIO BUTTONS */
    div[data-testid="stRadio"] div[role="radiogroup"] > label {
        background: white; border: 2px solid #cbd5e1; padding: 20px !important;
        border-radius: 15px; width: 100%; cursor: pointer; margin-bottom: 10px;
        transition: all 0.2s ease;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label:hover {
        border-color: #3b82f6; background-color: #f0f9ff;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label p {
        font-size: 1.4rem !important; font-weight: 600 !important; color: #1e293b;
        margin-bottom: 0;
    }

    /* BUTTONS */
    .stButton > button {
        border-radius: 15px; font-weight: 700; height: 3.5rem; 
        font-size: 1.1rem !important; transition: all 0.3s ease;
        border: none;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(0,0,0,0.1);
    }
    
    /* STATS CARDS */
    .stat-card {
        background: white; border-radius: 15px; padding: 20px; margin: 10px 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.05); border: 1px solid #e2e8f0;
        text-align: center;
    }
    .stat-number {
        font-size: 2.5rem; font-weight: 800; color: #1e3a8a; margin: 10px 0;
    }
    .stat-label {
        font-size: 0.9rem; color: #64748b; text-transform: uppercase; letter-spacing: 1px;
    }
    
    /* EXAM TIMER */
    .timer-box {
        background: linear-gradient(135deg, #dc2626 0%, #ef4444 100%);
        color: white; padding: 15px; border-radius: 15px; text-align: center;
        font-weight: 800; font-size: 1.5rem; margin: 10px 0;
    }
    
    /* PROGRESS BAR */
    .stProgress > div > div > div > div {
        background-color: #3b82f6;
    }
    
    /* SIDEBAR */
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
    }
    
    /* RESPONSIVE */
    @media (max-width: 768px) {
        .tip-content { font-size: 1.1rem !important; }
        .tip-title { font-size: 1.4rem !important; }
        .stat-number { font-size: 2rem !important; }
        .hero-card { padding: 25px !important; }
    }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM HỖ TRỢ ---
def load_json_file(filename):
    """Tải file JSON với xử lý lỗi"""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Lỗi khi tải {filename}: {str(e)}")
        return None

def load_data_by_license(license_type):
    """Tải dữ liệu theo loại bằng"""
    is_oto = "Ô tô" in license_type
    target = ['data.json', 'data (6).json'] if is_oto else ['tips_a1.json', 'tips_a1 (1).json']
    for f in target:
        d = load_json_file(f)
        if d:
            return d
    return []

def load_questions():
    """Tải toàn bộ câu hỏi"""
    questions = load_json_file('dulieu_600_cau.json')
    if not questions:
        st.error("Không thể tải dữ liệu câu hỏi!")
        return []
    return questions

def load_image_smart(base_name, folders):
    """Tải ảnh thông minh từ nhiều thư mục"""
    if not base_name or str(base_name).strip() == "":
        return None
    
    exts = ['', '.png', '.jpg', '.jpeg', '.PNG', '.JPG', '.webp']
    clean_name = str(base_name).strip()
    
    for folder in folders:
        for ext in exts:
            path = os.path.join(folder, clean_name + ext)
            if os.path.exists(path):
                try:
                    return ImageOps.exif_transpose(Image.open(path))
                except:
                    continue
    return None

def update_stats(is_correct):
    """Cập nhật thống kê học tập"""
    st.session_state.total_questions_attempted += 1
    if is_correct:
        st.session_state.total_correct += 1
    
    # Lưu lịch sử
    history_entry = {
        'timestamp': datetime.now().isoformat(),
        'question_index': st.session_state.current_q_index,
        'is_correct': is_correct,
        'license_type': st.session_state.license_type
    }
    st.session_state.practice_history.append(history_entry)
    
    # Giới hạn lịch sử (lưu 100 bản ghi gần nhất)
    if len(st.session_state.practice_history) > 100:
        st.session_state.practice_history = st.session_state.practice_history[-100:]

# --- 5. SIDEBAR - THỐNG KÊ HỌC TẬP ---
def render_sidebar_stats():
    """Hiển thị thống kê trong sidebar"""
    with st.sidebar:
        st.markdown("## 📊 THỐNG KÊ HỌC TẬP")
        
        # Hiển thị loại bằng hiện tại
        st.info(f"**Loại bằng:** {st.session_state.license_type}")
        
        # Thẻ thống kê chính
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Tổng câu đã làm</div>
                <div class="stat-number">{st.session_state.total_questions_attempted}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            accuracy = 0
            if st.session_state.total_questions_attempted > 0:
                accuracy = (st.session_state.total_correct / st.session_state.total_questions_attempted) * 100
            
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-label">Tỷ lệ đúng</div>
                <div class="stat-number">{accuracy:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Câu đã bookmark
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Câu đã đánh dấu</div>
            <div class="stat-number">{len(st.session_state.bookmarked_questions)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Câu sai cần ôn
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-label">Câu sai cần ôn</div>
            <div class="stat-number">{len(st.session_state.wrong_questions)}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Kết quả thi thử gần nhất
        if st.session_state.mock_exam_score is not None:
            st.markdown("---")
            st.markdown("### 🎯 THI THỬ GẦN NHẤT")
            score_color = "#059669" if st.session_state.mock_exam_score >= 21 else "#dc2626"
            st.markdown(f"""
            <div style="text-align: center; padding: 15px; background: {score_color}10; border-radius: 15px; border: 2px solid {score_color}30;">
                <div style="font-size: 2.5rem; font-weight: 800; color: {score_color};">
                    {st.session_state.mock_exam_score}/25
                </div>
                <div style="font-size: 0.9rem; color: #64748b;">
                    {st.session_state.last_mock_exam}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            if st.session_state.mock_exam_score >= 21:
                st.success("🎉 ĐẠT - Sẵn sàng thi thật!")
            else:
                st.warning("📚 Cần ôn tập thêm")
        
        # Nút nhanh
        st.markdown("---")
        st.markdown("### ⚡ LỘ TRÌNH ÔN TẬP")
        
        if st.button("📝 Luyện câu sai", use_container_width=True):
            if st.session_state.wrong_questions:
                st.session_state.page = "review_wrong"
                st.rerun()
            else:
                st.warning("Chưa có câu nào sai!")
        
        if st.button("🔖 Xem câu đánh dấu", use_container_width=True):
            if st.session_state.bookmarked_questions:
                st.session_state.page = "bookmarks"
                st.rerun()
            else:
                st.warning("Chưa có câu nào được đánh dấu!")
        
        # Đề xuất dựa trên thống kê
        st.markdown("---")
        if st.session_state.total_questions_attempted > 0:
            accuracy = (st.session_state.total_correct / st.session_state.total_questions_attempted) * 100
            if accuracy < 70:
                st.warning("**💡 Gợi ý:** Ôn lại các mẹo cấp tốc trước khi luyện đề!")
            elif accuracy < 85:
                st.info("**💡 Gợi ý:** Luyện thi thử để kiểm tra kiến thức!")
            else:
                st.success("**💡 Gợi ý:** Bạn đã sẵn sàng cho kỳ thi thật!")

# --- 6. TRANG CHỦ ---
def render_home_page():
    """Trang chủ với các lựa chọn chính"""
    st.markdown("""
    <div class="hero-card">
        <h1 style="font-size: 3.5rem; margin-bottom: 10px;">🚗 GPLX MASTER PRO</h1>
        <p style="font-size: 1.5rem; opacity: 0.9;">Ôn thi cấp tốc - Đậu ngay lần đầu 2026</p>
        <div style="margin-top: 20px; display: flex; justify-content: center; gap: 10px;">
            <div style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">📚 600+ Câu hỏi</div>
            <div style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">⚡ Mẹo cấp tốc</div>
            <div style="background: rgba(255,255,255,0.2); padding: 8px 16px; border-radius: 20px;">🎯 Thi thử thông minh</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Hiển thị thống kê nhanh
    if st.session_state.total_questions_attempted > 0:
        accuracy = (st.session_state.total_correct / st.session_state.total_questions_attempted) * 100
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📊 Câu đã làm", st.session_state.total_questions_attempted)
        with col2:
            st.metric("🎯 Tỷ lệ đúng", f"{accuracy:.1f}%")
        with col3:
            st.metric("🔖 Đã bookmark", len(st.session_state.bookmarked_questions))
    
    # Chọn loại bằng
    st.markdown("### 🎯 CHỌN LOẠI BẰNG ÔN TẬP")
    license_option = st.radio(
        "Loại bằng:",
        ["Xe máy (A1, A2)", "Ô tô (B1, B2, C...)"],
        horizontal=True,
        index=0 if st.session_state.license_type == "Xe máy (A1, A2)" else 1
    )
    
    if license_option != st.session_state.license_type:
        st.session_state.license_type = license_option
        st.rerun()
    
    # Các tính năng chính
    st.markdown("### 🚀 TÍNH NĂNG CHÍNH")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("**⚡ MẸO CẤP TỐC**\n\nÔn nhanh trong 30p", use_container_width=True, help="Tổng hợp mẹo học nhanh"):
            st.session_state.page = "captoc"
            st.rerun()
    
    with col2:
        if st.button("**📖 MẸO CHI TIẾT**\n\nGiải thích đầy đủ", use_container_width=True, help="Mẹo chi tiết từng chủ đề"):
            st.session_state.page = "tips"
            st.rerun()
    
    with col3:
        if st.button("**📝 LUYỆN THI**\n\nTừng câu hỏi", use_container_width=True, help="Luyện tập từng câu hỏi"):
            st.session_state.page = "exam"
            st.rerun()
    
    with col4:
        if st.button("**🎯 THI THỬ**\n\n25 câu như thật", use_container_width=True, 
                    help="Thi thử giống đề thi thật, tính thời gian"):
            st.session_state.page = "mock_exam"
            st.rerun()
    
    # Tính năng phụ
    st.markdown("### 💪 TÍNH NĂNG HỖ TRỢ")
    
    col_a, col_b, col_c = st.columns(3)
    
    with col_a:
        if st.button("🔖 Câu đánh dấu", use_container_width=True, 
                    disabled=len(st.session_state.bookmarked_questions) == 0):
            st.session_state.page = "bookmarks"
            st.rerun()
    
    with col_b:
        if st.button("📚 Ôn câu sai", use_container_width=True, 
                    disabled=len(st.session_state.wrong_questions) == 0):
            st.session_state.page = "review_wrong"
            st.rerun()
    
    with col_c:
        if st.button("📊 Xem thống kê", use_container_width=True):
            st.session_state.page = "stats"
            st.rerun()

# --- 7. TRANG THI THỬ (MOCK EXAM) ---
def render_mock_exam():
    """Trang thi thử 25 câu như thi thật"""
    
    # Nút quay lại
    if st.button("🏠 VỀ TRANG CHỦ"):
        st.session_state.page = "home"
        st.session_state.exam_started = False
        st.session_state.exam_finished = False
        st.rerun()
    
    st.markdown("## 🎯 THI THỬ GIẤY PHÉP LÁI XE")
    st.markdown(f"**Loại bằng:** {st.session_state.license_type}")
    
    # Chưa bắt đầu thi
    if not st.session_state.exam_started:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #8b5cf6;">
            <div class="tip-title">📝 Hướng dẫn thi thử</div>
            <div class="tip-content">
            1. Bài thi gồm <b>25 câu hỏi</b> (giống đề thi thật)<br>
            2. Thời gian làm bài: <b>20 phút</b><br>
            3. Điểm đạt: <b>21/25 câu đúng trở lên</b><br>
            4. Không thể quay lại câu trước<br>
            5. Kết quả sẽ được lưu vào thống kê
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🚀 BẮT ĐẦU THI THỬ", use_container_width=True, type="primary"):
                # Tạo đề thi ngẫu nhiên
                all_questions = load_questions()
                if len(all_questions) >= 25:
                    st.session_state.exam_questions = random.sample(all_questions, 25)
                    st.session_state.exam_answers = [None] * 25
                    st.session_state.exam_started = True
                    st.session_state.current_q_index = 0
                    st.session_state.exam_time_left = 1200  # 20 phút
                    st.session_state.exam_finished = False
                    st.rerun()
                else:
                    st.error("Không đủ câu hỏi để tạo đề thi!")
        
        # Hiển thị kết quả lần thi trước
        if st.session_state.mock_exam_score is not None:
            st.markdown("---")
            st.markdown(f"### 📊 KẾT QUẢ LẦN THI TRƯỚC: **{st.session_state.mock_exam_score}/25**")
            st.markdown(f"**Thời gian:** {st.session_state.last_mock_exam}")
            
            # Biểu đồ điểm
            score = st.session_state.mock_exam_score
            progress = score / 25
            st.progress(progress)
            
            if score >= 21:
                st.success(f"🎉 Xuất sắc! Bạn đã đạt {score}/25 điểm!")
            elif score >= 18:
                st.warning(f"📚 Khá tốt! Ôn thêm để đạt điểm cao hơn ({score}/25)")
            else:
                st.error(f"📖 Cần ôn tập nhiều hơn ({score}/25)")
    
    # Đang thi
    elif st.session_state.exam_started and not st.session_state.exam_finished:
        # Timer
        minutes = st.session_state.exam_time_left // 60
        seconds = st.session_state.exam_time_left % 60
        
        timer_color = "#059669" if st.session_state.exam_time_left > 300 else "#dc2626"
        st.markdown(f"""
        <div class="timer-box" style="background: linear-gradient(135deg, {timer_color} 0%, {timer_color}80 100%);">
            ⏱️ Thời gian còn lại: {minutes:02d}:{seconds:02d}
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        progress = (st.session_state.current_q_index + 1) / 25
        st.progress(progress)
        st.caption(f"Câu {st.session_state.current_q_index + 1}/25")
        
        # Hiển thị câu hỏi
        q = st.session_state.exam_questions[st.session_state.current_q_index]
        
        st.markdown(f"### Câu {st.session_state.current_q_index + 1}")
        st.markdown(f"**{q['question']}**")
        
        # Hiển thị ảnh nếu có
        if q.get('image'):
            img = load_image_smart(q['image'], ["images", "images_a1"])
            if img:
                st.image(img, use_container_width=True)
        
        # Hiển thị đáp án
        options = q['options']
        user_answer = st.radio(
            "Chọn đáp án:",
            options,
            index=None,
            key=f"exam_q_{st.session_state.current_q_index}"
        )
        
        # Lưu đáp án
        if user_answer:
            st.session_state.exam_answers[st.session_state.current_q_index] = user_answer
        
        # Nút điều hướng
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col1:
            if st.session_state.current_q_index > 0:
                if st.button("⬅️ Câu trước"):
                    st.session_state.current_q_index -= 1
                    st.rerun()
        
        with col2:
            if st.button("✅ Nộp bài", type="primary"):
                st.session_state.exam_finished = True
                calculate_exam_score()
                st.rerun()
        
        with col3:
            if st.session_state.current_q_index < 24:
                if st.button("Câu tiếp ➡️"):
                    if st.session_state.exam_answers[st.session_state.current_q_index] is None:
                        st.warning("Bạn chưa chọn đáp án cho câu này!")
                    else:
                        st.session_state.current_q_index += 1
                        st.rerun()
            else:
                if st.button("🔚 Kết thúc"):
                    st.session_state.exam_finished = True
                    calculate_exam_score()
                    st.rerun()
        
        # Auto timer
        if 'last_update' not in st.session_state:
            st.session_state.last_update = time.time()
        
        current_time = time.time()
        if current_time - st.session_state.last_update >= 1:
            st.session_state.exam_time_left -= 1
            st.session_state.last_update = current_time
            
            if st.session_state.exam_time_left <= 0:
                st.session_state.exam_finished = True
                calculate_exam_score()
                st.rerun()
            else:
                st.rerun()
    
    # Đã hoàn thành thi
    else:
        render_exam_results()

def calculate_exam_score():
    """Tính điểm bài thi"""
    correct_count = 0
    wrong_indices = []
    
    for i, (q, answer) in enumerate(zip(st.session_state.exam_questions, st.session_state.exam_answers)):
        correct_answer = q['correct_answer'].strip()
        if answer and answer.strip() == correct_answer:
            correct_count += 1
        else:
            wrong_indices.append(i)
    
    # Lưu kết quả
    st.session_state.mock_exam_score = correct_count
    st.session_state.last_mock_exam = datetime.now().strftime("%d/%m/%Y %H:%M")
    
    # Thêm câu sai vào danh sách ôn tập
    for idx in wrong_indices:
        q_data = {
            'question_index': idx,
            'question': st.session_state.exam_questions[idx]['question'],
            'correct_answer': st.session_state.exam_questions[idx]['correct_answer'],
            'user_answer': st.session_state.exam_answers[idx]
        }
        if q_data not in st.session_state.wrong_questions:
            st.session_state.wrong_questions.append(q_data)

def render_exam_results():
    """Hiển thị kết quả thi"""
    score = st.session_state.mock_exam_score
    total = 25
    
    st.markdown("## 🎯 KẾT QUẢ THI THỬ")
    
    # Hiển thị điểm
    if score >= 21:
        st.balloons()
        st.success(f"# 🎉 CHÚC MỪNG! Bạn đã ĐẠT: {score}/{total} điểm!")
    else:
        st.error(f"# 📚 RẤT TIẾC! Bạn đạt: {score}/{total} điểm")
    
    # Thông tin chi tiết
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Điểm số", f"{score}/{total}")
    
    with col2:
        percentage = (score / total) * 100
        st.metric("Tỷ lệ đúng", f"{percentage:.1f}%")
    
    with col3:
        minutes_used = (1200 - st.session_state.exam_time_left) // 60
        seconds_used = (1200 - st.session_state.exam_time_left) % 60
        st.metric("Thời gian làm", f"{minutes_used}:{seconds_used:02d}")
    
    # Phân tích kết quả
    st.markdown("### 📊 PHÂN TÍCH CHI TIẾT")
    
    if score >= 21:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%); 
                    padding: 20px; border-radius: 15px; border-left: 8px solid #059669;">
            <h4>✅ BẠN ĐÃ SẴN SÀNG CHO KỲ THI THẬT!</h4>
            <p>Với tỷ lệ đúng {:.1f}%, bạn hoàn toàn có thể tự tin đi thi. 
            Hãy ôn lại một vài câu sai để đạt điểm tuyệt đối!</p>
        </div>
        """.format(percentage), unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
                    padding: 20px; border-radius: 15px; border-left: 8px solid #dc2626;">
            <h4>📚 CẦN ÔN TẬP THÊM!</h4>
            <p>Bạn cần đúng thêm <b>{21 - score} câu</b> nữa để đạt. 
            Hãy ôn lại các câu sai và các mẹo cấp tốc!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Hiển thị câu sai
    if len(st.session_state.wrong_questions) > 0:
        st.markdown("### ❌ CÂU TRẢ LỜI SAI CẦN ÔN LẠI")
        
        for i, wrong_q in enumerate(st.session_state.wrong_questions[:5]):  # Hiển thị 5 câu đầu
            with st.expander(f"Câu {wrong_q['question_index'] + 1}: {wrong_q['question'][:50]}..."):
                st.markdown(f"**Câu hỏi:** {wrong_q['question']}")
                st.markdown(f"**Đáp án của bạn:** {wrong_q['user_answer']}")
                st.markdown(f"**Đáp án đúng:** {wrong_q['correct_answer']}")
    
    # Nút hành động
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Thi thử lại", use_container_width=True):
            reset_exam_state()
            st.rerun()
    
    with col2:
        if st.button("📚 Ôn câu sai", use_container_width=True):
            st.session_state.page = "review_wrong"
            st.rerun()
    
    with col3:
        if st.button("🏠 Về trang chủ", use_container_width=True):
            reset_exam_state()
            st.session_state.page = "home"
            st.rerun()

def reset_exam_state():
    """Reset trạng thái thi"""
    st.session_state.exam_started = False
    st.session_state.exam_finished = False
    st.session_state.exam_questions = []
    st.session_state.exam_answers = []
    st.session_state.current_q_index = 0

# --- 8. TRANG CÂU ĐÃ BOOKMARK ---
def render_bookmarks_page():
    """Trang hiển thị các câu đã bookmark"""
    if st.button("🏠 VỀ TRANG CHỦ"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("## 🔖 CÂU HỎI ĐÃ ĐÁNH DẤU")
    
    if not st.session_state.bookmarked_questions:
        st.info("Bạn chưa đánh dấu câu hỏi nào. Hãy đánh dấu câu hỏi trong trang luyện thi!")
        return
    
    all_questions = load_questions()
    
    # Hiển thị từng câu đã bookmark
    for i, q_idx in enumerate(st.session_state.bookmarked_questions):
        if q_idx < len(all_questions):
            q = all_questions[q_idx]
            
            with st.container():
                col1, col2 = st.columns([4, 1])
                
                with col1:
                    st.markdown(f"### Câu {q_idx + 1}")
                    st.markdown(f"**{q['question']}**")
                    
                    if q.get('image'):
                        img = load_image_smart(q['image'], ["images", "images_a1"])
                        if img:
                            st.image(img, use_container_width=True, width=300)
                
                with col2:
                    # Nút bỏ bookmark
                    if st.button("❌ Bỏ", key=f"remove_{i}"):
                        st.session_state.bookmarked_questions.remove(q_idx)
                        st.success("Đã bỏ đánh dấu!")
                        time.sleep(0.5)
                        st.rerun()
                    
                    # Nút luyện tập câu này
                    if st.button("📝 Luyện", key=f"practice_{i}"):
                        st.session_state.page = "exam"
                        st.session_state.current_q_index = q_idx
                        st.rerun()
                
                st.markdown("---")

# --- 9. TRANG ÔN CÂU SAI ---
def render_review_wrong_page():
    """Trang ôn lại các câu đã trả lời sai"""
    if st.button("🏠 VỀ TRANG CHỦ"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("## 📚 ÔN LẠI CÂU TRẢ LỜI SAI")
    
    if not st.session_state.wrong_questions:
        st.info("Bạn chưa có câu nào trả lời sai. Hãy tiếp tục luyện tập!")
        return
    
    all_questions = load_questions()
    
    # Lọc các câu sai cần ôn
    wrong_to_review = st.session_state.wrong_questions.copy()
    
    if not wrong_to_review:
        st.success("🎉 Bạn đã ôn hết các câu sai!")
        return
    
    # Hiển thị câu đầu tiên trong danh sách
    wrong_q = wrong_to_review[0]
    q_idx = wrong_q['question_index']
    
    if q_idx < len(all_questions):
        q = all_questions[q_idx]
        
        st.markdown(f"### Câu {q_idx + 1}")
        st.markdown(f"**{q['question']}**")
        
        # Hiển thị ảnh nếu có
        if q.get('image'):
            img = load_image_smart(q['image'], ["images", "images_a1"])
            if img:
                st.image(img, use_container_width=True)
        
        # Hiển thị thông tin cũ
        st.warning(f"**Lần trước bạn chọn:** {wrong_q['user_answer']}")
        st.success(f"**Đáp án đúng:** {wrong_q['correct_answer']}")
        
        # Kiểm tra lại kiến thức
        st.markdown("### 🔄 KIỂM TRA LẠI KIẾN THỨC")
        
        options = q['options']
        user_retry = st.radio(
            "Chọn đáp án:",
            options,
            key=f"retry_{q_idx}"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("✅ Kiểm tra đáp án"):
                if user_retry:
                    correct = user_retry.strip() == q['correct_answer'].strip()
                    
                    if correct:
                        st.success("🎉 Chính xác! Bạn đã hiểu câu này.")
                        
                        # Xóa khỏi danh sách câu sai
                        if wrong_q in st.session_state.wrong_questions:
                            st.session_state.wrong_questions.remove(wrong_q)
                        
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ Sai rồi! Đáp án đúng là: {q['correct_answer']}")
                else:
                    st.warning("Vui lòng chọn đáp án!")
        
        with col2:
            if st.button("⏭️ Bỏ qua câu này"):
                # Di chuyển câu này xuống cuối danh sách
                st.session_state.wrong_questions.append(st.session_state.wrong_questions.pop(0))
                st.rerun()
        
        # Thống kê
        st.markdown("---")
        st.info(f"**Còn {len(st.session_state.wrong_questions)} câu sai cần ôn**")

# --- 10. TRANG THỐNG KÊ CHI TIẾT ---
def render_stats_page():
    """Trang thống kê chi tiết"""
    if st.button("🏠 VỀ TRANG CHỦ"):
        st.session_state.page = "home"
        st.rerun()
    
    st.markdown("## 📊 THỐNG KÊ HỌC TẬP CHI TIẾT")
    
    if st.session_state.total_questions_attempted == 0:
        st.info("Bạn chưa bắt đầu luyện tập. Hãy bắt đầu ngay!")
        return
    
    # Tổng quan
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Tổng câu đã làm", st.session_state.total_questions_attempted)
    
    with col2:
        accuracy = (st.session_state.total_correct / st.session_state.total_questions_attempted) * 100
        st.metric("Tỷ lệ đúng", f"{accuracy:.1f}%")
    
    with col3:
        st.metric("Câu đã bookmark", len(st.session_state.bookmarked_questions))
    
    with col4:
        st.metric("Câu cần ôn", len(st.session_state.wrong_questions))
    
    # Biểu đồ đơn giản
    st.markdown("### 📈 BIỂU ĐỒ TIẾN ĐỘ")
    
    # Tạo dữ liệu giả cho biểu đồ (thực tế cần dùng pandas/plotly)
    if len(st.session_state.practice_history) > 1:
        # Tính accuracy theo thời gian
        dates = []
        accuracies = []
        
        for i in range(0, len(st.session_state.practice_history), 10):
            subset = st.session_state.practice_history[:i+10]
            if subset:
                correct = sum(1 for h in subset if h['is_correct'])
                total = len(subset)
                if total > 0:
                    dates.append(i)
                    accuracies.append((correct / total) * 100)
        
        if dates:
            # Hiển thị dạng table đơn giản
            data = {"Lần luyện": list(range(1, len(dates)+1)), 
                   "Tỷ lệ đúng (%)": [f"{acc:.1f}" for acc in accuracies]}
            st.dataframe(data, use_container_width=True)
    
    # Lịch sử luyện tập gần đây
    st.markdown("### 📝 LỊCH SỬ LUYỆN TẬP GẦN ĐÂY")
    
    if st.session_state.practice_history:
        recent = st.session_state.practice_history[-10:]  # 10 bản ghi gần nhất
        recent.reverse()
        
        for record in recent:
            time_str = datetime.fromisoformat(record['timestamp']).strftime("%H:%M %d/%m")
            status = "✅" if record['is_correct'] else "❌"
            st.text(f"{time_str} - Câu {record['question_index']+1} - {status}")
    
    # Nút reset thống kê
    st.markdown("---")
    if st.button("🔄 Reset thống kê", type="secondary"):
        st.session_state.total_questions_attempted = 0
        st.session_state.total_correct = 0
        st.session_state.practice_history = []
        st.success("Đã reset thống kê!")
        time.sleep(1)
        st.rerun()

# --- 11. TRANG LUYỆN THI (CẬP NHẬT) ---
def render_exam_page():
    """Trang luyện thi từng câu - ĐÃ THÊM BOOKMARK"""
    if st.button("🏠 VỀ TRANG CHỦ"):
        st.session_state.page = "home"
        st.rerun()
    
    all_qs = load_questions()
    if not all_qs:
        st.error("Lỗi dữ liệu!")
        return
    
    total = len(all_qs)
    
    # Thanh điều hướng cải tiến
    st.markdown("---")
    col1, col2, col3, col4, col5 = st.columns([1, 2, 1, 1, 1])
    
    with col1:
        if st.button("⬅️ Trước"):
            st.session_state.current_q_index = max(0, st.session_state.current_q_index - 1)
            st.rerun()
    
    with col2:
        new_q = st.number_input("Câu:", 1, total, st.session_state.current_q_index + 1, 
                               label_visibility="collapsed")
        if new_q - 1 != st.session_state.current_q_index:
            st.session_state.current_q_index = new_q - 1
            st.rerun()
    
    with col3:
        if st.button("Tiếp ➡️"):
            st.session_state.current_q_index = min(total - 1, st.session_state.current_q_index + 1)
            st.rerun()
    
    with col4:
        # Nút bookmark
        current_q = st.session_state.current_q_index
        is_bookmarked = current_q in st.session_state.bookmarked_questions
        
        if is_bookmarked:
            if st.button("🔖 Đã đánh dấu"):
                st.session_state.bookmarked_questions.remove(current_q)
                st.success("Đã bỏ đánh dấu!")
                time.sleep(0.5)
                st.rerun()
        else:
            if st.button("📌 Đánh dấu"):
                if current_q not in st.session_state.bookmarked_questions:
                    st.session_state.bookmarked_questions.append(current_q)
                    st.success("Đã đánh dấu câu hỏi!")
                    time.sleep(0.5)
                    st.rerun()
    
    with col5:
        if st.button("🎯 Thi thử"):
            st.session_state.page = "mock_exam"
            st.rerun()
    
    # Chế độ tự động
    auto_mode = st.toggle("🚀 TỰ ĐỘNG CHUYỂN CÂU", key="auto")
    if auto_mode:
        delay = st.slider("Tốc độ (giây):", 1, 10, 3)
    
    # Hiển thị câu hỏi
    q = all_qs[st.session_state.current_q_index]
    
    st.subheader(f"Câu {st.session_state.current_q_index + 1} / {total}")
    
    # Hiển thị trạng thái bookmark
    if st.session_state.current_q_index in st.session_state.bookmarked_questions:
        st.markdown("🔖 *Câu này đã được đánh dấu*")
    
    st.info(f"**{q['question']}**")
    
    # Hiển thị ảnh
    current_img = q.get('image')
    if current_img:
        # Lọc bỏ ảnh mẹo nếu dính vào câu 1
        if not (st.session_state.current_q_index == 0 and ("tip" in str(current_img) or current_img == "1")):
            img = load_image_smart(current_img, ["images", "images_a1"])
            if img:
                st.image(img, use_container_width=True)
    
    # Đáp án
    correct_ans = q['correct_answer'].strip()
    options = q['options']
    
    # Tìm index đáp án đúng
    correct_idx = None
    for i, opt in enumerate(options):
        if opt.strip() == correct_ans:
            correct_idx = i
            break
    
    # Hiển thị radio buttons
    user_choice = st.radio(
        "Chọn đáp án:",
        options,
        index=None,
        key=f"r_{st.session_state.current_q_index}"
    )
    
    # Xử lý khi có lựa chọn
    if user_choice:
        is_correct = user_choice.strip() == correct_ans
        
        # Cập nhật thống kê
        update_stats(is_correct)
        
        # Thêm vào danh sách câu sai nếu sai
        if not is_correct:
            wrong_data = {
                'question_index': st.session_state.current_q_index,
                'question': q['question'],
                'correct_answer': correct_ans,
                'user_answer': user_choice
            }
            if wrong_data not in st.session_state.wrong_questions:
                st.session_state.wrong_questions.append(wrong_data)
        
        # Hiển thị kết quả
        if is_correct:
            st.success("✅ **CHÍNH XÁC!**")
        else:
            st.error(f"❌ **SAI RỒI!** Đáp án đúng là: **{correct_ans}**")
        
        # Tự động chuyển câu
        if auto_mode and is_correct:
            placeholder = st.empty()
            with placeholder.container():
                st.write(f"⏳ Chuyển câu sau {delay} giây...")
                progress_bar = st.progress(0)
                
                for i in range(delay):
                    time.sleep(1)
                    progress_bar.progress((i + 1) / delay)
            
            if st.session_state.current_q_index < total - 1:
                st.session_state.current_q_index += 1
                st.rerun()
            else:
                st.success("🎉 Bạn đã hoàn thành tất cả câu hỏi!")

# --- 12. TRANG MẸO CẤP TỐC & CHI TIẾT (GIỮ NGUYÊN) ---
def render_captoc_page():
    """Trang mẹo cấp tốc - giữ nguyên từ code cũ"""
    if st.button("🏠 VỀ TRANG CHỦ"):
        st.session_state.page = "home"
        st.rerun()
    
    st.header(f"⚡ Mẹo Cấp Tốc: {st.session_state.license_type}")
    
    # Chia tab
    tab1, tab2, tab3, tab4 = st.tabs(["🔢 SỐ, TUỔI & ĐUA", "🏎️ TỐC ĐỘ", "🛑 BIỂN BÁO, KT & LÀN", "🚔 SA HÌNH & QUAN"])
    folders = ["images", "images_a1"]

    # TAB 1: TUỔI - HẠNG - ĐUA XE
    with tab1:
        st.markdown("""
        <div class="tip-box" style="border-left-color: #8b5cf6;">
            <div class="tip-title">🏍️ Mẹo Đua Xe (Mới)</div>
            <div class="tip-content">
            • Lấy bánh xe cuối cùng <b>TRỪ 1</b> ➡ Ra đáp án.<br>
            • <i>Ví dụ:</i> Xe ô tô (4 bánh): 4 - 1 = <b>3</b> (Chọn ý 3).
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Các phần khác giữ nguyên...
        # ... (giữ nguyên nội dung từ code cũ)

def render_tips_page():
    """Trang mẹo chi tiết - giữ nguyên từ code cũ"""
    if st.button("🏠 Về Trang Chủ"):
        st.session_state.page = "home"
        st.rerun()
    
    # ... (giữ nguyên nội dung từ code cũ)

# --- 13. ROUTING CHÍNH ---
def main():
    """Hàm chính điều hướng trang"""
    
    # Hiển thị sidebar thống kê
    render_sidebar_stats()
    
    # Điều hướng trang
    if st.session_state.page == "home":
        render_home_page()
    elif st.session_state.page == "captoc":
        render_captoc_page()
    elif st.session_state.page == "tips":
        render_tips_page()
    elif st.session_state.page == "exam":
        render_exam_page()
    elif st.session_state.page == "mock_exam":
        render_mock_exam()
    elif st.session_state.page == "bookmarks":
        render_bookmarks_page()
    elif st.session_state.page == "review_wrong":
        render_review_wrong_page()
    elif st.session_state.page == "stats":
        render_stats_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #64748b; font-size: 0.9rem; padding: 20px;">
        <p>🚗 <b>GPLX MASTER PRO</b> - Ôn thi giấy phép lái xe 2026</p>
        <p>📚 600+ câu hỏi | ⚡ Mẹo cấp tốc | 🎯 Thi thử thông minh</p>
    </div>
    """, unsafe_allow_html=True)

# --- 14. CHẠY ỨNG DỤNG ---
if __name__ == "__main__":
    main()
