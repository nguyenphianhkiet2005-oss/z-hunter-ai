import streamlit as st
import google.generativeai as genai
from PIL import Image
import io

# 1. CẤU HÌNH GIAO DIỆN
st.set_page_config(page_title="Z-Tutor Pro", page_icon="🎓", layout="wide")

# Giao diện CSS tùy chỉnh
st.markdown("""
    <style>
    .stApp { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 15px; margin-bottom: 10px; }
    .sidebar-content { padding: 20px; background-color: #ffffff; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# 2. THANH SIDEBAR (QUẢN LÝ NGƯỜI DÙNG & FACEBOOK)
with st.sidebar:
    st.title("🎓 Gia sư AI Pro")
    student_name = st.text_input("👤 Tên học viên:", value="Bạn mới", help="Nhập tên để AI xưng hô thân thiện hơn")
    
    st.markdown("---")
    st.subheader("📲 Theo dõi hỗ trợ")
    # Thay link Facebook của bạn vào đây
    st.link_button("Facebook Cá Nhân", "https://www.facebook.com/yourprofile")
    st.link_button("Group Học Tập", "https://www.facebook.com/groups/yourgroup")
    
    st.markdown("---")
    if st.button("🗑️ Xóa lịch sử học tập"):
        st.session_state.history = []
        st.rerun()

# 3. KIỂM TRA API KEY
api_key = st.secrets.get("GEMINI_API_KEY") or st.sidebar.text_input("🔑 Nhập API Key (nếu chưa cài):", type="password")

# 4. KHỞI TẠO LỊCH SỬ (SESSION STATE)
if "history" not in st.session_state:
    st.session_state.history = []

# 5. GIAO DIỆN CHÍNH
st.title(f"Chào {student_name}! Hôm nay bạn cần hỗ trợ gì?")

tab1, tab2 = st.tabs(["📚 Giải bài & Chụp ảnh", "📜 Lịch sử bài học"])

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📸 Chụp ảnh đề bài")
        img_file = st.camera_input("Đưa đề bài hoặc trang sách vào camera")
        
    with col2:
        st.subheader("✏️ Nhập yêu cầu")
        user_text = st.chat_input("Hỏi gia sư bất cứ điều gì (ví dụ: Giải bài toán này cho mình...)")

    # XỬ LÝ KHI CÓ INPUT
    if (user_text or img_file) and api_key:
        try:
            genai.configure(api_key=api_key)
            # Dùng bản Flash để phân tích ảnh nhanh và rẻ
            model = genai.GenerativeModel('gemini-1.5-flash')
            
            inputs = []
            if user_text:
                inputs.append(f"Chào gia sư, mình là {student_name}. Hãy hỗ trợ mình: {user_text}")
            else:
                inputs.append(f"Hãy phân tích hình ảnh đề bài này giúp mình ({student_name})")
            
            if img_file:
                img = Image.open(img_file)
                inputs.append(img)
            
            with st.spinner("🧠 Gia sư đang suy nghĩ..."):
                response = model.generate_content(inputs)
                ai_reply = response.text
                
                # Lưu vào lịch sử
                st.session_state.history.append({
                    "role": "user", 
                    "content": user_text if user_text else "[Đã gửi 1 hình ảnh]"
                })
                st.session_state.history.append({
                    "role": "assistant", 
                    "content": ai_reply
                })
                
                st.write("### ✅ Kết quả giải đáp:")
                st.markdown(ai_reply)
        
        except Exception as e:
            st.error(f"Lỗi: {e}")

with tab2:
    st.subheader("🕒 Quá trình học tập của bạn")
    if not st.session_state.history:
        st.info("Bạn chưa có câu hỏi nào. Hãy bắt đầu ở tab 'Giải bài' nhé!")
    else:
        for msg in reversed(st.session_state.history):
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            with st.chat_message(msg["role"]):
                st.write(f"**{role_icon} {msg['role'].upper()}:**")
                st.write(msg["content"])
                st.markdown("---")

# 6. CHÂN TRANG
st.markdown("---")
st.caption(f"© 2024 Z-Tutor Pro - Tài khoản đang dùng: {student_name}")
