import streamlit as st
import json
import os
import random
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
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
    st.session_state.user_answers = {} 

# --- 3. CSS CAO CẤP ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    
    /* Giao diện câu hỏi */
    .question-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid #1976D2; margin-bottom: 15px; }
    .question-text { font-size: 1.2rem; font-weight: 600; color: #2c3e50; }
    
    /* Highlight đáp án */
    .success-msg { color: #2e7d32; font-weight: bold; padding: 10px; background: #e8f5e9; border-radius: 5px; margin-top: 10px;}
    .error-msg { color: #c62828; font-weight: bold; padding: 10px; background: #ffebee; border-radius: 5px; margin-top: 10px;}
    
    /* Phần Mẹo */
    div.tip-card { background-color: #ffffff; border-radius: 12px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); border: 1px solid #f0f0f0; }
    .tip-header { color: #b71c1c; font-size: 1.25rem; font-weight: 700; margin-bottom: 10px; }
    .badge { font-size: 0.8rem; padding: 4px 8px; border-radius: 12px; color: white; font-weight: 600; margin-bottom: 8px; display: inline-block; }
    
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
    try:
        with open('dulieu_web_chuan.json', 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []

def process_image(image_filename, tip_id=0, is_question=False):
    if not image_filename: return None
    image_path = os.path.join("images", image_filename)
    if os.path.exists(image_path):
        img = Image.open(image_path)
        if not is_question: 
            if 1 <= tip_id <= 36: img = img.rotate(-270, expand=True)
            elif 37 <= tip_id <= 51: img = img.rotate(-90, expand=True)
        return img
    return None

# --- 5. LOGIC MẸO ---
def render_tips_view(data):
    # (Giữ nguyên phần render Mẹo như cũ)
    if 'random_tip' in st.session_state:
        st.info("🎲 **Mẹo ngẫu nhiên:**")
        render_tip_card(st.session_state['random_tip'], True)
        st.divider()

    st.header("📚 MẸO GHI NHỚ NHANH")
    with st.sidebar:
        st.divider()
        st.subheader("🛠️ Mẹo")
        study_mode = st.radio("Chế độ:", ["📖 Xem đáp án", "🫣 Học thuộc"])
        show_result = (study_mode == "📖 Xem đáp án")
        filter_bookmark = st.checkbox("❤️ Chỉ hiện mẹo đã Lưu")
        if st.button("🎲 Bốc thăm mẹo"): st.session_state['random_tip'] = random.choice(data)
        if st.button("❌ Xóa bốc thăm"): 
            if 'random_tip' in st.session_state: del st.session_state['random_tip']

    search = st.text_input("", placeholder="🔍 Tìm kiếm mẹo...")
    filtered_data = data
    if search:
        filtered_data = [t for t in filtered_data if search.lower() in t['title'].lower() or any(search.lower() in x.lower() for x in t['content'])]
    if filter_bookmark:
        filtered_data = [t for t in filtered_data if t['id'] in st.session_state.bookmarks]

    if not filtered_data:
        st.warning("Không tìm thấy mẹo nào!")
    else:
        if search or filter_bookmark:
            for tip in filtered_data: render_tip_card(tip, show_result)
        else:
            categories = ["Tất cả"] + sorted(list(set([t['category'] for t in data])))
            tabs = st.tabs(categories)
            for i, cat in enumerate(categories):
                with tabs[i]:
                    tips = data if cat == "Tất cả" else [t for t in data if t['category'] == cat]
                    for tip in tips: render_tip_card(tip, show_result)

def render_tip_card(tip, show_answer):
    cat_color = get_category_color(tip['category'])
    is_bookmarked = tip['id'] in st.session_state.bookmarks
    st.markdown(f"""<div class="tip-card"><span class="badge" style="background-color: {cat_color}">{tip['category']}</span><div class="tip-header">{tip['title']}</div>""", unsafe_allow_html=True)
    
    for line in tip['content']:
        if "=>" in line:
            parts = line.split("=>")
            display_line = f"{parts[0]} <span class='highlight'>👉 {parts[1]}</span>" if show_answer else f"{parts[0]} <span class='hidden-answer'>???</span>"
        else: display_line = line
        st.markdown(f"• {display_line}", unsafe_allow_html=True)
    
    if tip.get('image'):
        img_obj = process_image(tip['image'], tip.get('id', 0))
        if img_obj: 
            st.image(img_obj, use_container_width=True)
            if st.button("🔍 Phóng to", key=f"z_{tip['id']}"): 
                st.session_state.zoomed_image_data = {"image": img_obj, "title": tip['title']}
                st.rerun()

    col1, col2 = st.columns([0.8, 0.2])
    with col2:
        if st.checkbox("Lưu", value=is_bookmarked, key=f"bk_{tip['id']}"): st.session_state.bookmarks.add(tip['id'])
        else: st.session_state.bookmarks.discard(tip['id'])
    st.markdown("</div>", unsafe_allow_html=True)

# --- 6. LOGIC ÔN TẬP 600 CÂU (SỬA LẠI) ---
def render_practice_view(questions):
    if not questions:
        st.error("⚠️ File `dulieu_web_chuan.json` bị lỗi hoặc trống.")
        return

    total_q = len(questions)
    
    # Sidebar: Chọn câu
    with st.sidebar:
        st.divider()
        st.subheader("🔢 Điều hướng")
        q_num = st.number_input("Đến câu số:", 1, total_q, st.session_state.current_question_index + 1)
        st.session_state.current_question_index = q_num - 1
        st.progress(len(st.session_state.user_answers) / total_q)
        st.caption(f"Tiến độ: {len(st.session_state.user_answers)}/{total_q}")

    # Lấy dữ liệu câu hiện tại
    idx = st.session_state.current_question_index
    q_data = questions[idx]
    q_id = q_data.get('id', idx + 1)
    
    # Xử lý Text & Option
    q_content_full = q_data.get('content', [])
    q_text = q_content_full[0] if q_content_full else q_data.get('question', "Lỗi nội dung")
    options = q_data.get('options', [])
    if not options and len(q_content_full) > 1: options = q_content_full[1:]

    # --- GIAO DIỆN CHÍNH ---
    st.subheader(f"Câu {q_id}:")
    st.markdown(f'<div class="question-box"><div class="question-text">{q_text}</div></div>', unsafe_allow_html=True)

    if q_data.get('image'):
        img_obj = process_image(q_data['image'], is_question=True)
        if img_obj:
            st.image(img_obj, caption=f"Hình ảnh câu {q_id}")
            if st.button("🔍 Zoom ảnh", key=f"zq_{q_id}"):
                st.session_state.zoomed_image_data = {"image": img_obj, "title": f"Câu {q_id}"}
                st.rerun()

    # --- XỬ LÝ NHẬP LIỆU (PHÍM HOẶC CHUỘT) ---
    col_input, col_display = st.columns([1, 2])
    
    selected_option = None
    saved_ans = st.session_state.user_answers.get(str(q_id), None)
    
    with col_input:
        st.info("⌨️ **Nhập phím (1-4):**")
        # Ô input để bắt phím số
        key_input = st.text_input("Gõ số và Enter", key=f"key_{q_id}", placeholder="vd: 1", label_visibility="collapsed")
        
        # Logic: Nếu user nhập số vào ô text, ưu tiên lấy số đó
        if key_input and key_input.isdigit():
            val = int(key_input)
            if 1 <= val <= len(options):
                selected_option = options[val-1]
                # Tự động lưu và xóa text để input trống cho lần sau (hacky nhưng cần thiết)
            else:
                st.warning("Số không hợp lệ!")
    
    with col_display:
        # Nếu chưa có phím, dùng radio
        if not selected_option:
            # Tìm index của đáp án đã lưu để hiển thị lại
            idx_saved = options.index(saved_ans) if saved_ans in options else None
            selected_option = st.radio("Chọn đáp án:", options, index=idx_saved, key=f"radio_{q_id}")

    # --- CHẤM ĐIỂM ---
    if selected_option:
        st.session_state.user_answers[str(q_id)] = selected_option
        
        # Lấy đáp án đúng từ JSON
        correct_raw = str(q_data.get('correct_answer', "")).strip()
        
        # Logic so sánh thông minh (Số hoặc Chữ)
        is_correct = False
        has_data = False
        
        if correct_raw:
            has_data = True
            # Trường hợp 1: JSON lưu số "1", "2"...
            if correct_raw.isdigit():
                correct_idx = int(correct_raw) - 1
                if 0 <= correct_idx < len(options):
                    is_correct = (selected_option == options[correct_idx])
                    correct_text_display = options[correct_idx]
                else:
                    correct_text_display = f"Đáp án số {correct_raw}"
            # Trường hợp 2: JSON lưu text đầy đủ
            else:
                is_correct = (selected_option.strip() == correct_raw)
                correct_text_display = correct_raw

            if is_correct:
                st.markdown(f'<div class="success-msg">✅ CHÍNH XÁC! Bạn đã chọn: {selected_option}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="error-msg">❌ SAI RỒI! Đáp án đúng là:<br>{correct_text_display}</div>', unsafe_allow_html=True)
        else:
            # Nếu file JSON không có đáp án
            st.warning(f"⚠️ Đã lưu câu trả lời: '{selected_option}'.")
            st.caption("(Lưu ý: File dữ liệu 'dulieu_web_chuan.json' của bạn hiện đang để trống phần 'correct_answer', nên hệ thống chưa thể báo Đúng/Sai. Vui lòng cập nhật file dữ liệu.)")

    st.divider()
    c1, c2 = st.columns(2)
    with c1: 
        if st.button("⬅️ Trước", disabled=(idx==0), use_container_width=True): 
            st.session_state.current_question_index -= 1; st.rerun()
    with c2: 
        if st.button("Sau ➡️", disabled=(idx==total_q-1), type="primary", use_container_width=True): 
            st.session_state.current_question_index += 1; st.rerun()

# --- 7. MAIN ---
def main():
    if st.session_state.zoomed_image_data:
        st.button("🔙 QUAY LẠI", on_click=lambda: st.session_state.update(zoomed_image_data=None), type="primary")
        st.header(st.session_state.zoomed_image_data["title"])
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        return

    with st.sidebar:
        st.title("🚗 MENU")
        mode = st.radio("Chọn:", ["💡 Mẹo ghi nhớ", "📝 Luyện thi 600 câu"])

    if mode == "💡 Mẹo ghi nhớ": render_tips_view(load_tips_data())
    else: render_practice_view(load_questions_data())

if __name__ == "__main__":
    main()
