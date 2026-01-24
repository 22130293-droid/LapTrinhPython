import streamlit as st

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&family=Roboto:wght@300;400;700&display=swap');
        
        /* --- GLOBAL THEME --- */
        .stApp { 
            background: radial-gradient(circle at top, #1b1b2f 0%, #16213e 50%, #0f3460 100%); 
            color: #FFFFFF; 
            font-family: 'Montserrat', sans-serif; 
        }
        
        h1, h2, h3, h4, h5, h6 { color: #FFFFFF !important; text-shadow: 0 4px 6px rgba(0,0,0,0.3); font-weight: 800 !important; }
        p, span, div, label { color: #e0e0e0; }

        /* ==========================================================================================
           1. FIX MÀU CHỮ INPUT (QUAN TRỌNG - ÉP MÀU ĐEN TRÊN NỀN TRẮNG)
           ========================================================================================== */
        
        /* Style cho ô nhập liệu thường */
        div[data-testid="stTextInput"] input, 
        div[data-testid="stPasswordInput"] input {
            background-color: #ffffff !important;   /* Nền TRẮNG tuyệt đối */
            color: #000000 !important;              /* Chữ ĐEN tuyệt đối */
            -webkit-text-fill-color: #000000 !important;
            caret-color: #000000 !important;        /* Con trỏ chuột màu đen */
            border-radius: 10px;
            border: 1px solid #ccc !important;
            font-weight: 600 !important;
        }

        /* Style đặc biệt xử lý lỗi Autofill của Chrome/Edge (khi nó tự điền màu vàng/trắng) */
        input:-webkit-autofill,
        input:-webkit-autofill:hover, 
        input:-webkit-autofill:focus, 
        input:-webkit-autofill:active {
            -webkit-box-shadow: 0 0 0 30px white inset !important; /* Ép nền trắng đè lên màu vàng */
            -webkit-text-fill-color: black !important;             /* Ép chữ đen */
        }

        /* Màu chữ placeholder (chữ gợi ý mờ) */
        ::placeholder { color: #666 !important; opacity: 1; }

        /* Fix màu chữ Selectbox (Hộp chọn ngày) */
        div[data-baseweb="select"] > div {
            background-color: #ffffff !important;
            color: #000000 !important;
        }
        div[data-baseweb="select"] span { -webkit-text-fill-color: black !important; }

        /* ==========================================================================================
           2. CẤU HÌNH HEADER & NÚT BẤM
           ========================================================================================== */
        
        .header-container {
            display: flex; justify-content: space-between; align-items: center;
            padding: 10px 20px;
            background: rgba(255, 255, 255, 0.03);
            backdrop-filter: blur(10px);
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 0 0 20px 20px;
            margin-bottom: 30px;
        }

        /* Style Nút Bấm - Thêm white-space: nowrap để CHỐNG GÃY DÒNG */
        div.stButton > button {
            background: linear-gradient(90deg, #e52d27 0%, #b31217 100%);
            color: white !important;
            border: none;
            border-radius: 20px;
            padding: 6px 18px !important;
            font-weight: 700;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(229, 45, 39, 0.4);
            min-height: 40px; 
            white-space: nowrap !important; /* QUAN TRỌNG: Không cho xuống dòng */
        }
        div.stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(229, 45, 39, 0.6);
        }
        div.stButton > button[kind="secondary"] {
            background: rgba(255,255,255,0.1);
            border: 1px solid rgba(255,255,255,0.3);
            box-shadow: none;
        }

        .logo { 
            font-size: 28px; font-weight: 900; letter-spacing: 2px;
            background: linear-gradient(to right, #ff416c, #ff4b2b); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
            text-decoration: none !important; 
        }

        /* --- CÁC THÀNH PHẦN KHÁC (Slider, Footer...) --- */
        .slide-images { width: 300%; height: 100%; display: flex; animation: slide_animation 18s infinite cubic-bezier(0.45, 0, 0.55, 1); }
        .img-container { width: 100%; height: 100%; position: relative; }
        .img-container img { width: 100%; height: 100%; object-fit: cover; object-position: center 20%; }
        @keyframes slide_animation { 0%, 28% { margin-left: 0%; } 33%, 61% { margin-left: -100%; } 66%, 94% { margin-left: -200%; } 100% { margin-left: 0%; } }
        
        .movie-container { background: rgba(255, 255, 255, 0.05); backdrop-filter: blur(5px); border-radius: 16px; padding: 12px; transition: all 0.4s; border: 1px solid rgba(255, 255, 255, 0.05); height: 100%; display: flex; flex-direction: column; }
        .movie-container:hover { transform: translateY(-10px) scale(1.02); border-color: #ff4b2b; box-shadow: 0 15px 30px rgba(255, 75, 43, 0.2); background: rgba(255, 255, 255, 0.1); }
        .movie-img-box { border-radius: 12px; overflow: hidden; margin-bottom: 12px; aspect-ratio: 2/3; width: 100%; }
        .movie-img-box img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s; }
        .movie-container:hover .movie-img-box img { transform: scale(1.1); }
        .movie-title { font-family: 'Montserrat', sans-serif; font-size: 16px; font-weight: 700; margin-bottom: 5px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; color: #FFF; }
        .tag { background: rgba(255,255,255,0.1); padding: 4px 8px; border-radius: 6px; font-size: 11px; color: #bbb; border: 1px solid rgba(255,255,255,0.1); }

        .footer { margin-top: 80px; padding: 40px 20px; background: rgba(0,0,0,0.3); border-top: 1px solid rgba(255,255,255,0.1); text-align: center; font-size: 14px; color: #888; }
        .footer a { color: #ff4b2b; text-decoration: none; font-weight: bold; margin: 0 10px; transition: 0.3s; }
        .footer a:hover { color: #fff; text-shadow: 0 0 10px #ff4b2b; }
        .footer-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; max-width: 1000px; margin: 0 auto 30px auto; text-align: left; }
        .footer-col h4 { color: #fff; margin-bottom: 15px; font-size: 16px; text-transform: uppercase; letter-spacing: 1px; }
        </style>
    """, unsafe_allow_html=True)


def render_header():
    with st.container():

        # Chia lại tỷ lệ: Logo bên trái, 2 nút chức năng dạt về bên phải
        c1, c2, c3 = st.columns([3, 1, 1.5])

        with c1:
            st.markdown('<a href="#" class="logo">🍿 START CINEMA</a>', unsafe_allow_html=True)


        with c3:
            # KIỂM TRA TRẠNG THÁI ĐĂNG NHẬP
            if st.session_state.get('is_logged_in'):
                # Hiển thị Tên User dưới dạng Popover (Cửa sổ thả xuống)
                with st.popover(f"👤 {st.session_state['username'].upper()}", use_container_width=True):
                    st.markdown(f"**Xin chào, {st.session_state['username']}!**")

                    # Ô 1: Nút Tài khoản
                    if st.button("📂 THÔNG TIN TÀI KHOẢN", use_container_width=True, key="header_profile"):
                        st.session_state['page'] = 'profile'
                        st.rerun()

                    # Ô 2: Nút Logout
                    if st.button("🚪 ĐĂNG XUẤT", use_container_width=True, key="header_logout"):
                        st.session_state['is_logged_in'] = False
                        st.session_state['username'] = ""
                        st.session_state['page'] = 'home'
                        st.rerun()
            else:
                # Nếu chưa đăng nhập thì hiện nút Đăng nhập bình thường
                if st.button("🔐 ĐĂNG NHẬP", key="login_btn_header", use_container_width=True):
                    st.session_state['pre_login_page'] = st.session_state.get('page', 'home')
                    st.session_state['page'] = 'login'
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

def render_footer():
    st.markdown("""
        <div class="footer">
            <div class="footer-grid">
                <div class="footer-col">
                    <h4>Về Start Cinema</h4>
                    <p>Hệ thống rạp chiếu phim hiện đại hàng đầu với công nghệ AI gợi ý phim thông minh và trải nghiệm đặt vé mượt mà.</p>
                </div>
                <div class="footer-col">
                    <h4>Liên kết nhanh</h4>
                    <p><a href="#">Tuyển dụng</a></p>
                    <p><a href="#">Điều khoản sử dụng</a></p>
                    <p><a href="#">Chính sách bảo mật</a></p>
                </div>
                <div class="footer-col">
                    <h4>Liên hệ</h4>
                    <p>📍 Dĩ An, Bình Dương, Vietnam</p>
                    <p>📞 1900 1234</p>
                    <p>📧 support@startcinema.vn</p>
                </div>
            </div>
            <hr style="border-color: rgba(255,255,255,0.1); margin-bottom: 20px;">
            <p>&copy; 2026 START CINEMA AI SYSTEM. All rights reserved.</p>
            <div>
                <a href="#">Facebook</a> • <a href="#">Instagram</a> • <a href="#">Youtube</a>
            </div>
        </div>
    """, unsafe_allow_html=True)

