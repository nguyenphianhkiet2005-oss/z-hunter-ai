import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CẤU HÌNH GIAO DIỆN TỐI GIẢN
st.set_page_config(page_title="Z-Tutor AI", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    /* Ẩn các menu thừa của Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Tùy chỉnh thanh chat */
    .stChatInputContainer { padding-bottom: 10px; }
    
    /* Làm gọn khu vực nút chức năng */
    .upload-section {
        display: flex;
        gap: 10px;
        margin-bottom: -10px;
        padding: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. THANH SIDEBAR (Chỉ giữ lại tên và lịch sử)
with st.sidebar:
    st.title("🎓 Z-Tutor AI")
    student_name = st.text_input("👤 Tên học viên:", value="Bạn")
    if st.button("🗑️ Xóa hội thoại"):
        st.session_state.messages = []
        st.rerun()

# 3. KHỞI TẠO API
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("🔑 API Key:", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

# Hiển thị lịch sử chat
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 4. KHU VỰC CÔNG CỤ SIÊU NHỎ (Nằm ngay trên thanh Chat)
st.markdown('<div class="upload-section">', unsafe_allow_html=True)
col1, col2 = st.columns([1, 4]) # Chia tỉ lệ để nút nhỏ lại

with col1:
    # Nút upload file/ảnh thu nhỏ bằng expander
    menu = st.popover("➕") # Dấu cộng nhỏ gọn như ChatGPT
    img_file = menu.camera_input("📷 Chụp ảnh bài tập")
    up_file = menu.file_uploader("📁 Gửi tài liệu (PDF, Ảnh)", type=['png', 'jpg', 'jpeg', 'pdf'])
st.markdown('</div>', unsafe_allow_html=True)

# 5. XỬ LÝ NHẬP LIỆU VÀ PHẢN HỒI
if prompt := st.chat_input("Hỏi gia sư..."):
    
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.chat_message("assistant"):
                with st.spinner("Đang xử lý..."):
                    content_parts = [f"Học sinh {student_name} hỏi: {prompt}"]
                    
                    # Kiểm tra nếu có ảnh chụp hoặc file tải lên
                    active_file = img_file or up_file
                    if active_file:
                        try:
                            # Nếu là ảnh thì mở bằng Image
                            img = Image.open(active_file)
                            content_parts.append(img)
                        except:
                            content_parts.append("\n(Đã nhận một tài liệu đính kèm)")

                    response = model.generate_content(content_parts)
                    st.markdown(response.text)
                    
            st.session_state.messages.append({"role": "assistant", "content": response.text})
            
        except Exception as e:
            st.error(f"Lỗi: {e}")
    else:
        st.warning("Vui lòng nhập API Key!")
