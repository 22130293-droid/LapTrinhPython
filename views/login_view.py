import streamlit as st
import time as et
import random
import string
from views.components import render_header
from core.database import create_user, verify_user, get_user_by_email, update_password
from core.email_service import send_welcome_email, send_reset_password_email


def render_login():
    render_header()

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])

    with c2:
        tab_login, tab_signup, tab_forgot = st.tabs(["🔐 ĐĂNG NHẬP", "✨ ĐĂNG KÝ", "❓ QUÊN MẬT KHẨU"])

        # --- TAB 1: ĐĂNG NHẬP (CẬP NHẬT ROLE) ---
        with tab_login:
            st.markdown("### Welcome Back")
            with st.form("login_form"):
                username = st.text_input("Tên đăng nhập", key="login_user")
                password = st.text_input("Mật khẩu", type="password", key="login_pass")
                submit_login = st.form_submit_button("ĐĂNG NHẬP", type="primary", use_container_width=True)

                if submit_login:
                    user = verify_user(username, password)
                    if user:
                        # Lưu thông tin vào session_state từ Row object
                        st.session_state['is_logged_in'] = True
                        st.session_state['username'] = user['username']
                        st.session_state['email'] = user['email']
                        st.session_state['role'] = user['role']  # CỘT QUAN TRỌNG NHẤT

                        if user['role'] == 1:
                            st.success(f"Chào Quản trị viên {user['username']}!")
                        else:
                            st.success(f"Xin chào {user['username']}!")

                        et.sleep(0.5)
                        # Nếu là admin, ưu tiên về trang home để chọn dashboard trong sidebar
                        st.session_state['page'] = 'home'
                        st.rerun()
                    else:
                        st.error("Sai tài khoản hoặc mật khẩu!")

        # --- TAB 2: ĐĂNG KÝ (MẶC ĐỊNH ROLE = 0) ---
        with tab_signup:
            st.markdown("### Tạo tài khoản mới")
            with st.form("signup_form"):
                new_user = st.text_input("Tên đăng nhập", key="su_user")
                new_email = st.text_input("Email (để nhận vé)", key="su_email")
                new_pass = st.text_input("Mật khẩu", type="password", key="su_pass")
                confirm_pass = st.text_input("Nhập lại mật khẩu", type="password", key="su_confirm")
                submit_signup = st.form_submit_button("ĐĂNG KÝ NGAY", use_container_width=True)

                if submit_signup:
                    if not new_user or not new_email or not new_pass:
                        st.warning("Vui lòng điền đầy đủ thông tin!")
                    elif new_pass != confirm_pass:
                        st.error("Mật khẩu nhập lại không khớp!")
                    else:
                        # Role mặc định là 0 cho người dùng mới
                        success, msg = create_user(new_user, new_email, new_pass, role=0)
                        if success:
                            try:
                                send_welcome_email(new_email, new_user)
                            except Exception:
                                pass

                            st.success("Đăng ký thành công!")
                            # Tự động đăng nhập
                            st.session_state['is_logged_in'] = True
                            st.session_state['username'] = new_user
                            st.session_state['email'] = new_email
                            st.session_state['role'] = 0

                            et.sleep(1)
                            st.session_state['page'] = 'home'
                            st.rerun()
                        else:
                            st.error(msg)

        # --- TAB 3: QUÊN MẬT KHẨU ---
        with tab_forgot:
            # Giữ nguyên phần logic quên mật khẩu cũ
            st.markdown("### Khôi phục mật khẩu")
            with st.form("forgot_form"):
                f_email = st.text_input("Nhập Email đã đăng ký", key="f_email")
                submit_forgot = st.form_submit_button("GỬI MẬT KHẨU MỚI", use_container_width=True)

                if submit_forgot:
                    user = get_user_by_email(f_email)
                    if user:
                        new_pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
                        update_password(f_email, new_pwd)
                        try:
                            send_reset_password_email(f_email, new_pwd)
                            st.success(f"Mật khẩu mới đã gửi tới {f_email}")
                        except:
                            st.error("Lỗi gửi mail!")
                    else:
                        st.error("Email này chưa được đăng ký!")