import streamlit as st
import time as et
import random
import string
from views.components import render_header
from database import create_user, verify_user, get_user_by_email, update_password
# Import đầy đủ các hàm
from email_service import send_welcome_email, send_reset_password_email

def render_login():
    render_header()

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 1.5, 1])

    with c2:
        tab_login, tab_signup, tab_forgot = st.tabs(["🔐 ĐĂNG NHẬP", "✨ ĐĂNG KÝ", "❓ QUÊN MẬT KHẨU"])

        # --- TAB 1: ĐĂNG NHẬP ---
        with tab_login:
            st.markdown("### Welcome Back")
            with st.form("login_form"):
                username = st.text_input("Tên đăng nhập", key="login_user")
                password = st.text_input("Mật khẩu", type="password", key="login_pass")
                submit_login = st.form_submit_button("ĐĂNG NHẬP", type="primary", use_container_width=True)

                if submit_login:
                    user = verify_user(username, password)
                    if user:
                        st.session_state['is_logged_in'] = True
                        st.session_state['username'] = user[1]
                        st.session_state['email'] = user[2]
                        st.success(f"Xin chào {user[1]}!")
                        et.sleep(0.5)
                        st.session_state['page'] = st.session_state.get('pre_login_page', 'home')
                        st.rerun()
                    else:
                        st.error("Sai tài khoản hoặc mật khẩu!")

        # --- TAB 2: ĐĂNG KÝ (FIX TỰ ĐỘNG ĐĂNG NHẬP) ---
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
                        success, msg = create_user(new_user, new_email, new_pass)
                        if success:
                            # 1. Gửi mail chào mừng (bắt lỗi nếu chưa config mail)
                            try:
                                send_welcome_email(new_email, new_user)
                            except Exception:
                                pass

                            st.success("Đăng ký thành công! Đang tự động đăng nhập...")

                            # 2. [FIX QUAN TRỌNG] Tự động set trạng thái đăng nhập
                            st.session_state['is_logged_in'] = True
                            st.session_state['username'] = new_user
                            st.session_state['email'] = new_email

                            # 3. Chờ xíu rồi chuyển trang
                            et.sleep(1)
                            st.session_state['page'] = st.session_state.get('pre_login_page', 'home')
                            st.rerun()
                        else:
                            st.error(msg)

        # --- TAB 3: QUÊN MẬT KHẨU ---
        with tab_forgot:
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
                            success, msg = send_reset_password_email(f_email, new_pwd)
                            if success:
                                st.success(f"Mật khẩu mới đã gửi tới {f_email}")
                            else:
                                st.error(f"Lỗi gửi mail: {msg}")
                        except Exception as e:
                            st.error(f"Lỗi hệ thống mail: {e}")
                    else:
                        st.error("Email này chưa được đăng ký!")