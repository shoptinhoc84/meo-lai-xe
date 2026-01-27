import streamlit as st
import json
import os
import random
from PIL import Image

# --- 1. CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Ôn Thi GPLX 600 Câu",
    page_icon="🚗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. KHỞI TẠO STATE (Lưu trạng thái) ---
if 'bookmarks' not in st.session_state:
    st.session_state.bookmarks = set()
if 'zoomed_image_data' not in st.session_state:
    st.session_state.zoomed_image_data = None
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {} # Lưu đáp án người dùng đã chọn

# --- 3. CSS GIAO DIỆN ĐẸP ---
st.markdown("""
<style>
    html, body, [class*="css"] { font-family: 'Segoe UI', sans-serif; }
    
    /* Card chứa nội dung */
    div.tip-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
    }
    
    /* Tiêu đề */
    .tip-header { color: #b71c1c; font-size: 1.2rem; font-weight: 700; margin-bottom: 10px; }
    .question-header { color: #1565C0; font-size: 1.4rem; font-weight: 700; margin-bottom: 15px; }

    /* Highlight đáp án đúng/sai */
    .correct-ans { color: #2e7d32; font-weight: bold; padding: 5px; background: #e8f5e9; border-radius: 5px; }
    .wrong-ans { color: #c62828; font-weight: bold; padding: 5px; background: #ffebee; border-radius: 5px; }
    
    /* Badge danh mục */
    .badge {
        font-size: 0.8rem; padding: 4px 8px; border-radius: 12px;
        color: white; font-weight: 600; text-transform: uppercase;
        margin-bottom: 8px; display: inline-block;
    }

    /* Nút điều hướng to rõ */
    .stButton button { border-radius: 8px; font-weight: 600; }
    
    .block-container { padding-top: 1rem !important; padding-bottom: 2rem !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. HÀM XỬ LÝ DỮ LIỆU ---
@st.cache_data
def load_data(filename):
    try:
        if not os.path.exists(filename):
            return []
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Lỗi khi đọc file {filename}: {e}")
        return []

def get_category_color(category):
    colors = {
        "Biển báo": "#1976D2", "Sa hình": "#F57C00", "Khái niệm": "#388E3C",
        "Quy tắc": "#00796B", "Văn hóa": "#7B1FA2", "Kỹ thuật": "#455A64", "Tốc độ": "#D32F2F"
    }
    for key, color in colors.items():
        if key in category: return color
    return "#616161"

def process_image(image_filename, tip_id=0, is_question=False):
    # Đường dẫn ảnh
    image_path = os.path.join("images", image_filename)
    if os.path.exists(image_path):
        img = Image.open(image_path)
        # Logic xoay ảnh (Chỉ áp dụng cho phần Mẹo, phần Câu hỏi thường không cần xoay)
        if not is_question:
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

    # Hàm hiển thị danh sách
    def display_list(data_list):
        for tip in data_list:
            cat_color = get_category_color(tip.get('category', 'Chung'))
            is_bookmarked = tip['id'] in st.session_state.bookmarks
            
            st.markdown(f"""
            <div class="tip-card">
                <span class="badge" style="background-color: {cat_color}">{tip.get('category', 'Chung')}</span>
                <div class="tip-header">{tip['title']}</div>
            """, unsafe_allow_html=True)
            
            # Nội dung
            for line in tip['content']:
                if "=>" in line:
                    parts = line.split("=>")
                    display_line = f"{parts[0]} <span style='background:#ffebee; color:#c62828; padding:2px 5px; border-radius:4px'>👉 {parts[1]}</span>" if show_answer else f"{parts[0]} <span style='color:#bbb; border:1px dashed #ccc; padding:0 5px'>???</span>"
                else:
                    display_line = line
                st.markdown(f"• {display_line}", unsafe_allow_html=True)
            
            # Ảnh
            if tip.get('image'):
                img = process_image(tip['image'], tip.get('id', 0), is_question=False)
                if img:
                    st.image(img, use_container_width=True)
                    if st.button("🔍 Phóng to", key=f"z_tip_{tip['id']}"):
                        st.session_state.zoomed_image_data = {"image": img, "title": tip['title']}
                        st.rerun()

            # Nút Lưu
            if st.checkbox("Lưu", value=is_bookmarked, key=f"bk_{tip['id']}"):
                st.session_state.bookmarks.add(tip['id'])
            else:
                st.session_state.bookmarks.discard(tip['id'])
            
            st.markdown("</div>", unsafe_allow_html=True)

    # Hiển thị theo Tab hoặc List
    if not search:
        categories = ["Tất cả"] + sorted(list(set([t.get('category', 'Chung') for t in tips_data])))
        tabs = st.tabs(categories)
        for i, cat in enumerate(categories):
            with tabs[i]:
                display_list(tips_data if cat == "Tất cả" else [t for t in tips_data if t.get('category') == cat])
    else:
        display_list(filtered_data)

# --- 6. GIAO DIỆN LUYỆN 600 CÂU (Tab 2 - QUAN TRỌNG) ---
def render_questions_page(questions_data):
    if not questions_data:
        st.error("⚠️ Chưa tìm thấy file `dulieu_web_chuan.json`. Vui lòng kiểm tra lại thư mục.")
        return

    total = len(questions_data)
    idx = st.session_state.current_question_index
    current_q = questions_data[idx]
    
    # --- THANH ĐIỀU HƯỚNG ---
    c1, c2, c3 = st.columns([1, 2, 1])
    with c1:
        if st.button("⬅️ Câu trước", use_container_width=True, disabled=(idx==0)):
            st.session_state.current_question_index -= 1
            st.rerun()
    with c3:
        if st.button("Câu sau ➡️", use_container_width=True, disabled=(idx==total-1)):
            st.session_state.current_question_index += 1
            st.rerun()
    with c2:
        new_idx = st.number_input("Nhảy đến câu số:", min_value=1, max_value=total, value=idx+1, label_visibility="collapsed")
        if new_idx - 1 != idx:
            st.session_state.current_question_index = new_idx - 1
            st.rerun()

    # --- HIỂN THỊ CÂU HỎI ---
    st.markdown(f"""
    <div class="tip-card">
        <div class="question-header">Câu {current_q.get('id', idx+1)} / {total} { '🛑 CÂU ĐIỂM LIỆT' if current_q.get('is_critical') else ''}</div>
        <div style="font-size: 1.15rem; margin-bottom: 15px;">{current_q.get('question', '')}</div>
    """, unsafe_allow_html=True)

    # Ảnh câu hỏi (Nếu có)
    # Giả sử ảnh được đặt tên theo ID câu hỏi (VD: 150.jpg) hoặc trường 'image' trong json
    q_image = current_q.get('image')
    # Nếu json không có field image, thử tìm theo ID
    if not q_image:
        test_path = f"{current_q.get('id', idx+1)}.jpg"
        if os.path.exists(os.path.join("images", test_path)):
            q_image = test_path
            
    if q_image:
        img = process_image(q_image, is_question=True)
        if img:
            st.image(img, use_container_width=True)
            if st.button("🔍 Phóng to ảnh", key=f"z_q_{idx}"):
                st.session_state.zoomed_image_data = {"image": img, "title": f"Câu {current_q.get('id')}"}
                st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)

    # --- PHẦN ĐÁP ÁN (TRẮC NGHIỆM) ---
    st.write("##### Chọn đáp án:")
    
    # Lấy danh sách options (Nếu file json chuẩn có trường options)
    options = current_q.get('options', [])
    correct_ans = current_q.get('correct_answer') # Đáp án đúng (VD: 1 hoặc "1")

    # Nếu không có options tách riêng, hiển thị nội dung thô để người dùng tự đoán
    if not options:
        st.info("Câu hỏi này chưa có dữ liệu đáp án trắc nghiệm. Bạn hãy xem nội dung và tự kiểm tra.")
        if st.checkbox("Hiện đáp án gợi ý"):
            st.success(f"Đáp án đúng: {correct_ans if correct_ans else 'Đang cập nhật'}")
    else:
        # Hiển thị 4 nút chọn
        # Kiểm tra xem người dùng đã chọn câu này chưa
        user_choice = st.session_state.user_answers.get(str(current_q.get('id', idx)), None)
        
        # Nếu chưa chọn -> Hiện Radio
        if user_choice is None:
            choice = st.radio("Chọn:", options, index=None, key=f"rad_{idx}", label_visibility="collapsed")
            if choice:
                # Lưu đáp án (Lấy ký tự đầu tiên làm số, VD: "1. Ý một" -> 1)
                try:
                    selected_num = int(str(choice).split('.')[0])
                    st.session_state.user_answers[str(current_q.get('id', idx))] = selected_num
                    st.rerun()
                except:
                    pass # Xử lý lỗi nếu format options không chuẩn
        else:
            # Nếu đã chọn -> Hiện kết quả
            st.info(f"Bạn đã chọn: **Đáp án {user_choice}**")
            
            # Logic kiểm tra đúng sai
            try:
                # Chuyển correct_ans về số nguyên để so sánh
                correct_num = int(str(correct_ans))
                if user_choice == correct_num:
                    st.success("✅ CHÍNH XÁC! Xuất sắc.")
                else:
                    st.error(f"❌ SAI RỒI! Đáp án đúng là: **{correct_num}**")
            except:
                st.warning(f"Đáp án đúng theo dữ liệu: {correct_ans}")
            
            if st.button("🔄 Làm lại câu này"):
                del st.session_state.user_answers[str(current_q.get('id', idx))]
                st.rerun()


# --- 7. CHƯƠNG TRÌNH CHÍNH (MAIN) ---
def main():
    # --- XỬ LÝ ZOOM FULLSCREEN ---
    if st.session_state.zoomed_image_data:
        st.button("🔙 QUAY LẠI", on_click=lambda: st.session_state.update(zoomed_image_data=None), type="primary", use_container_width=True)
        st.header(st.session_state.zoomed_image_data["title"])
        st.image(st.session_state.zoomed_image_data["image"], use_container_width=True)
        return

    # Tải dữ liệu
    tips_data = load_data('data.json')
    questions_data = load_data('dulieu_web_chuan.json')

    # --- SIDEBAR ---
    with st.sidebar:
        st.title("🗂️ Menu")
        mode = st.radio("Chọn chức năng:", ["📖 Học Mẹo (51 Mẹo)", "📝 Luyện 600 Câu"], index=1) # Mặc định vào luyện thi
        
        st.divider()
        if mode == "📖 Học Mẹo (51 Mẹo)":
            if st.checkbox("❤️ Chỉ hiện đã Lưu"):
                tips_data = [t for t in tips_data if t['id'] in st.session_state.bookmarks]
            
            if st.button("🎲 Bốc thăm mẹo"):
                 if tips_data: st.session_state['random_tip'] = random.choice(tips_data)

        elif mode == "📝 Luyện 600 Câu":
             st.info(f"Tổng số câu: {len(questions_data)}")
             if st.button("🗑️ Xóa lịch sử làm bài"):
                 st.session_state.user_answers = {}
                 st.rerun()

    # --- HIỂN THỊ CHÍNH ---
    
    # Phần Random Mẹo (Nếu có)
    if 'random_tip' in st.session_state:
        st.info("🎲 **Mẹo ngẫu nhiên:**")
        tip = st.session_state['random_tip']
        st.markdown(f"**{tip['title']}**")
        for line in tip['content']: st.write(line)
        if st.button("Đóng"):
            del st.session_state['random_tip']
            st.rerun()
        st.divider()

    # Điều hướng trang
    if mode == "📖 Học Mẹo (51 Mẹo)":
        render_tips_page(tips_data)
    else:
        render_questions_page(questions_data)

if __name__ == "__main__":
    main()
