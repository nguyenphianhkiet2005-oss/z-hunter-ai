import streamlit as st
import google.generativeai as genai
from PIL import Image

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Z-Tutor AI", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .stChatInputContainer { padding-bottom: 20px; }
    .stChatMessage { border-radius: 10px; }
    /* Làm gọn khu vực camera */
    .stCameraInput { margin-top: -50px; } 
    </style>
    """, unsafe_allow_html=True)

# 2. SIDEBAR - THÔNG TIN & FACEBOOK
with st.sidebar:
    st.title("🎓 Gia sư Z-Tutor")
    student_name = st.text_input("👤 Tên của bạn:", value="Học sinh")
    st.markdown("---")
    st.write("📲 **Kết nối với mình:**")
    st.link_button("Facebook hỗ trợ", "https://facebook.com/your_id") # Thay link của bạn vào đây
    if st.button("🗑️ Xóa lịch sử"):
        st.session_state.messages = []
        st.rerun()

# 3. KHỞI TẠO API & MODEL
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("🔑 API Key:", type="password")

if "messages" not in st.session_state:
    st.session_state.messages = []

# 4. HIỂN THỊ LỊCH SỬ CHAT
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. KHU VỰC NHẬP LIỆU (CAMERA & CHAT)
# Nút chụp hình nhỏ gọn ngay trên thanh chat
with st.expander("📸 Chụp ảnh bài tập (nếu cần)"):
    img_file = st.camera_input("Chụp đề bài")

if prompt := st.chat_input("Hỏi gia sư bất cứ điều gì..."):
    # Hiển thị tin nhắn người dùng
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Xử lý phản hồi từ AI
    if api_key:
        try:
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            with st.chat_message("assistant"):
                with st.spinner("Đang suy nghĩ..."):
                    # Nếu có ảnh, AI sẽ đọc ảnh + chữ
                    if img_file:
                        img = Image.open(img_file)
                        response = model.generate_content([prompt, img])
                    else:
                        response = model.generate_content(prompt)
                    
                    full_response = f"**Chào {student_name},**\n\n{response.text}"
                    st.markdown(full_response)
                    
            st.session_state.messages.append({"role": "assistant", "content": full_response})
            
        except Exception as e:
            st.error(f"Lỗi AI: {e}")
    else:
        st.warning("Vui lòng nhập API Key ở Sidebar!")
