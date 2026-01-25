import streamlit as st
import time as et
from booking_and_voice_search.booking_serveice import check_availability
from streamlit_extras.stylable_container import stylable_container
from views.qr_view import render_qr_overlay

def inject_custom_css():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@300;400;600;800&family=Roboto:wght@300;400;700&display=swap');

        .stApp { 
            background: radial-gradient(circle at top, #1b1b2f 0%, #16213e 50%, #0f3460 100%); 
            color: #FFFFFF; 
            font-family: 'Montserrat', sans-serif; 
        }

        h1, h2, h3, h4, h5, h6 {
            color: #FFFFFF !important;
            text-shadow: 0 4px 6px rgba(0,0,0,0.3);
            font-weight: 800 !important;
        }
        p,span, label {
            color: #e0e0e0;
        }
        
        div{
            color: #000000;
        }
        
        section[data-testid="stDialog"] p {
            text-align: center !important;
            font-weight: 800;
        }

        
        div[data-baseweb="select"] > div {
            color: #000000 !important;
            background-color: #ffffff !important;
            font-weight: 600 !important;
        }
        div[role="listbox"] li { color: #000000 !important; }

        div.stButton > button {
            background: linear-gradient(90deg, #e52d27 0%, #b31217 100%);
            color: white !important;
            border: none;
            border-radius: 12px;
            padding: 8px 16px;
            font-weight: 700;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(229, 45, 39, 0.4);
            min-height: 45px; 
        }
        
        </style>
    """, unsafe_allow_html=True)


# --- 2. HÀM RENDER BOOKING ---
def render_booking(service):
    # Gọi CSS để áp dụng giao diện Cinema
    inject_custom_css()

    # KHỞI TẠO BIẾN GHẾ (Tránh lỗi nếu chưa có)
    if 'selected_seats' not in st.session_state:
        st.session_state['selected_seats'] = []

    if 'show_qr' not in st.session_state:
        st.session_state['show_qr'] = False

    if st.session_state['show_qr']:
        render_qr_overlay()
        return

    # --- KIỂM TRA DỮ LIỆU PHIM ---
    if not st.session_state.get('selected_movie_id'):
        st.warning("⚠️ Vui lòng chọn phim từ trang chủ trước!")
        if st.button("Quay lại trang chủ"):
            st.session_state['page'] = 'home'
            st.rerun()
        return

    movie = service.get_movie_by_id(st.session_state['selected_movie_id'])
    if not movie:
        st.error("❌ Không tìm thấy thông tin phim này!")
        if st.button("Về trang chủ"):
            st.session_state['page'] = 'home'
            st.rerun()
        return

    # Nút quay lại
    if st.button("⬅ QUAY LẠI", key="back_home"):
        st.session_state['page'] = 'home'
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    col_L, col_R = st.columns([1.3, 2.5], gap="medium")

    with col_L:
        # Card thông tin phim
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
                <div style="display: flex; gap: 15px; align-items: start;">
                    <img src="{movie.poster}" style="width: 90px; border-radius: 8px; object-fit: cover;">
                    <div>
                        <h3 style="margin: 0; font-size: 18px; line-height: 1.2;">{movie.title}</h3>
                        <p style="margin: 5px 0; font-size: 12px; color: #aaa;">⏱ {movie.duration} | 🎭 {movie.genre}</p>
                    </div>
                </div>
            
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📅 CHỌN SUẤT CHIẾU")
        days = list(service.showtimes.keys())
        if 'selected_date' not in st.session_state:
            st.session_state['selected_date'] = days[0]

        s_day = st.selectbox("Ngày", days, index=days.index(st.session_state['selected_date']),
                             label_visibility="collapsed")
        st.session_state['selected_date'] = s_day

        times = service.showtimes.get(s_day, [])
        if times:
            s_time = st.radio("Giờ chiếu", times, horizontal=True)
            st.session_state['selected_time'] = s_time
        else:
            st.info("Ngày này hiện không có suất chiếu.")
            return

        seats = st.session_state['selected_seats']
        count = len(seats)

        # Logic giá vé
        def is_vip(seat_code):
            row_char = seat_code[0]
            col_num = int(seat_code[1:])
            return row_char in ['C', 'D', 'E'] and (3 <= col_num <= 6)

        total_price = sum([movie.price + (15000 if is_vip(s) else 0) for s in seats])

        # Render hóa đơn
        st.markdown(f"""
        <div style="background: white; color: #333; padding: 20px; border-radius: 15px; margin-top: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <div style="text-align: center; font-weight: 800; letter-spacing: 2px; font-size: 14px; margin-bottom: 15px; color: #16213e;">THÔNG TIN VÉ</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 13px;">
                <span style="color:#000000;">Phim:</span><strong>{movie.title[:20]}</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px; font-size: 13px;">
                <span style="color:#000000;">Ghế:</span><strong>{', '.join(seats) if count else '--'}</strong>
            </div>
            <hr style="border-top: 1px dashed #ccc; margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 20px; font-weight: 800;">
                <span style="color: #000000;">TỔNG:</span><span style="color: #d63031;">{total_price:,.0f}đ</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        if count > 0:
            st.write("")
            if st.button("💳 THANH TOÁN NGAY", type="primary", use_container_width=True):
                if not st.session_state.get('is_logged_in'):
                    st.warning("⚠️ Vui lòng đăng nhập!")
                    et.sleep(1)
                    st.session_state['pre_login_page'] = 'booking'
                    st.session_state['page'] = 'login'
                    st.rerun()
                else:
                    if not check_availability(movie.id, s_day, s_time, seats):
                        st.error("Ghế đã có người đặt!")
                    else:
                        # 🔑 LƯU THÔNG TIN THANH TOÁN
                        st.session_state['payment_info'] = {
                            "movie_id": movie.id,
                            "movie_title": movie.title,
                            "day": s_day,
                            "time": s_time,
                            "seats": seats,
                            "total_price": total_price,
                            "username": st.session_state.get('username', 'Khách hàng'),
                            "email": st.session_state.get('email', '')
                        }
                        st.session_state['show_qr'] = True
                        st.rerun()

    with col_R:
        st.markdown("""
            <div style="perspective: 600px; margin-bottom: 30px; text-align: center;">
                <div style="width: 70%; margin: 0 auto; height: 6px; background: #e0e0e0; box-shadow: 0 15px 40px rgba(255,255,255,0.6); border-radius: 50%; transform: rotateX(-20deg);"></div>
                <div style="margin-top: 15px; color: #888; font-size: 11px; letter-spacing: 4px;">MÀN HÌNH</div>
            </div>
        """, unsafe_allow_html=True)

        layout = service.get_seat_layout(movie.id, st.session_state['selected_date'], st.session_state['selected_time'])

        # --- CONTAINER CHỨA GRID GHẾ ---
        with stylable_container(
                key="seat_grid_fixed",
                css_styles="""
                /* 1. Target sâu vào nút để ép kích thước và flexbox */
                div[data-testid="stButton"] button {
                    width: 42px !important;    
                    height: 38px !important;
                    padding: 0px !important;
                    border-radius: 6px !important;
                    border: 1px solid rgba(255,255,255,0.3) !important;
                    background-color: transparent !important;
                    color: white !important;
                    # text-align:center;

                    /* Flexbox để căn giữa chữ */
                    display: flex !important;
                    justify-content: center !important;
                    align-items: center !important;
                    margin: 0 auto !important; 
                }

                /* 2. Reset thẻ P bên trong nút để chữ không bị lệch */
                div[data-testid="stButton"] button p {
                    font-size: 12px !important;
                    font-weight: bold !important;
                    margin: 0px !important;
                    padding: 0px !important;
                    line-height: 1 !important;
                    transform: translateY(0px) !important;
                }

                /* Hover Effect */
                div[data-testid="stButton"] button:hover {
                    border-color: #ff4b2b !important;
                    background-color: rgba(255, 255, 255, 0.2) !important;
                    transform: scale(1.1);
                    z-index: 10;
                }

                /* Disabled State */
                div[data-testid="stButton"] button:disabled {
                    background-color: #383838 !important;
                    border: 1px solid #444 !important;
                    color: #555 !important;
                    cursor: not-allowed;
                }
            """
        ):
            # Layout [1 - 6 - 1] để ép toàn bộ khối ghế vào giữa
            _, seat_area, _ = st.columns([1, 6, 1])

            with seat_area:
                for r, row in enumerate(layout):
                    # Gap="small" để các ghế sát nhau hơn
                    cols = st.columns(8, gap="small")

                    for c, status in enumerate(row):
                        seat_id = f"{chr(65 + r)}{c + 1}"
                        is_vip_seat = (chr(65 + r) in ['C', 'D', 'E']) and (3 <= (c + 1) <= 6)

                        with cols[c]:
                            # --- GHẾ VIP ---
                            if is_vip_seat:
                                with stylable_container(
                                        key=f"vip_{seat_id}",
                                        css_styles="""
                                    div[data-testid="stButton"] button { 
                                        border: 2px solid #f1c40f !important; 
                                        color: #f1c40f !important; 
                                    }
                                    div[data-testid="stButton"] button:hover {
                                        box-shadow: 0 0 8px #f1c40f !important;
                                    }
                                """
                                ):
                                    if status == 1:
                                        st.button(f"{seat_id}", key=seat_id, disabled=True)
                                    elif seat_id in seats:
                                        if st.button(f"{seat_id}", key=seat_id, type="primary"):
                                            st.session_state['selected_seats'].remove(seat_id)
                                            st.rerun()
                                    else:
                                        if st.button(f"{seat_id}", key=seat_id):
                                            st.session_state['selected_seats'].append(seat_id)
                                            st.rerun()

                            # --- GHẾ THƯỜNG ---
                            else:
                                if status == 1:
                                    st.button(f"{seat_id}", key=seat_id, disabled=True)
                                elif seat_id in seats:
                                    # CSS cho ghế thường đang chọn (Xanh lá)
                                    with stylable_container(
                                            key=f"active_{seat_id}",
                                            css_styles="""
                                            div[data-testid="stButton"] button {
                                                background-color: #2ecc71 !important;
                                                border-color: #27ae60 !important;
                                                box-shadow: 0 0 10px #2ecc71 !important;
                                            }
                                        """
                                    ):
                                        if st.button(f"{seat_id}", key=seat_id):
                                            st.session_state['selected_seats'].remove(seat_id)
                                            st.rerun()
                                else:
                                    if st.button(f"{seat_id}", key=seat_id):
                                        st.session_state['selected_seats'].append(seat_id)
                                        st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        _, note_area, _ = st.columns([1, 6, 1])
        with note_area:
            xc1, xc2, xc3, xc4 = st.columns(4)
            with xc1: st.markdown("⬜ **Thường**")
            with xc2: st.markdown("🟨 **VIP**")
            with xc3: st.markdown("⬛ **Đã đặt**")
            with xc4: st.markdown("🟢 **Đang chọn**")
