import streamlit as st
from core.services import CinemaService, AdminService
from core.database import init_db
from views.components import inject_custom_css, render_header, render_footer
from views.home_view import render_home
from views.booking_view import render_booking
from views.login_view import render_login
from views.admin_view import render_admin_dashboard
from views.profile_view import render_profile

# --- 1. CẤU HÌNH TRANG (Phải là lệnh đầu tiên của Streamlit) ---
st.set_page_config(
    page_title="Cinema AI System",
    page_icon="🍿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. KHỞI TẠO SESSION STATE ---
# Đảm bảo các biến này luôn tồn tại để không bị lỗi 'KeyError'
def init_session_state():
    if 'page' not in st.session_state: st.session_state['page'] = 'home'
    if 'movie_index' not in st.session_state: st.session_state['movie_index'] = 0
    if 'selected_movie_id' not in st.session_state: st.session_state['selected_movie_id'] = None
    if 'is_logged_in' not in st.session_state: st.session_state['is_logged_in'] = False
    if 'username' not in st.session_state: st.session_state['username'] = ""
    if 'role' not in st.session_state: st.session_state['role'] = 0  # 0: User, 1: Admin
    if 'selected_seats' not in st.session_state: st.session_state['selected_seats'] = []

# Gọi khởi tạo ngay lập tức
init_session_state()

def main():
    # 0. Khởi tạo Database (Tạo bảng nếu chưa có)
    try:
        init_db()
    except Exception as e:
        st.error(f"Lỗi khởi tạo Database: {e}")

    # 1. Load giao diện CSS chung
    inject_custom_css()

    # 2. Khởi tạo Service
    # CinemaService sẽ tải dữ liệu phim và Engine AI
    service = CinemaService()
    admin_service = AdminService(service.full_df)

    # 3. ĐIỀU HƯỚNG (ROUTING)

    # A. TRƯỜNG HỢP: TRANG ĐĂNG NHẬP
    if st.session_state['page'] == 'login':
        render_login()
        return

    # B. XỬ LÝ RIÊNG CHO ADMIN
    if st.session_state['is_logged_in'] and st.session_state['role'] == 1:
        with st.sidebar:
            st.markdown(f"## 🛡️ QUẢN TRỊ VIÊN")
            st.info(f"Tài khoản: **{st.session_state['username']}**")

            # Chọn chế độ hiển thị
            admin_mode = st.radio(
                "Điều hướng hệ thống:",
                ["🌐 Giao diện Người dùng", "📊 Dashboard Thống kê"]
            )

            st.divider()
            if st.button("🚪 Đăng xuất", type="primary", use_container_width=True):
                # Xóa toàn bộ state để reset App về trạng thái ban đầu
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()

        # Nếu Admin đang chọn xem Dashboard thống kê
        if admin_mode == "📊 Dashboard Thống kê":
            render_admin_dashboard(service.full_df, admin_service)
            return  # Thoát sớm để không hiện Header/Footer của User

    # C. GIAO DIỆN NGƯỜI DÙNG (HOME / BOOKING)
    # Các trang này luôn có Header và Footer
    render_header()

    if st.session_state['page'] == 'home':
        render_home(service)
    elif st.session_state['page'] == 'booking':
        # Bảo vệ: Nếu chưa chọn phim mà vào trang booking thì quay về home
        if st.session_state['selected_movie_id'] is None:
            st.session_state['page'] = 'home'
            st.rerun()
        render_booking(service)
    elif st.session_state['page'] == 'profile':
        render_profile(service)

    render_footer()

if __name__ == "__main__":
    main()