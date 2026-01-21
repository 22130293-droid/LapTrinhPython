import streamlit as st
import time as et
from booking_and_voice_search.booking_serveice import check_availability, save_booking
from streamlit_extras.stylable_container import stylable_container

def render_booking(service):
    # --- 1. KIỂM TRA DỮ LIỆU ---
    if not st.session_state.get('selected_movie_id'):
        st.error("Chưa chọn phim nào!")
        if st.button("Quay lại trang chủ"):
            st.session_state['page'] = 'home'
            st.rerun()
        return

    movie = service.get_movie_by_id(st.session_state['selected_movie_id'])
    if not movie:
        st.error("Không tìm thấy phim!")
        st.session_state['page'] = 'home'
        st.rerun()
        return

    if st.button("⬅ QUAY LẠI TRANG CHỦ", key="back_home"):
        st.session_state['page'] = 'home'
        st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    # Chia cột 1.3 - 2.5 để nút thanh toán không bị lỗi chữ
    col_L, col_R = st.columns([1.3, 2.5], gap="large")

    # --- 2. CỘT TRÁI: THÔNG TIN & THANH TOÁN ---
    with col_L:
        st.markdown(f"""
            <div style="background: rgba(255,255,255,0.05); padding: 20px; border-radius: 15px; border: 1px solid rgba(255,255,255,0.1); backdrop-filter: blur(10px);">
                <div style="display: flex; gap: 15px; align-items: start;">
                    <img src="{movie.poster}" style="width: 90px; border-radius: 8px;">
                    <div>
                        <h3 style="margin: 0; font-size: 20px;">{movie.title}</h3>
                        <p style="margin: 5px 0; font-size: 13px; color: #aaa;">⏱ {movie.duration} | 🎭 {movie.genre}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("### 📅 SUẤT CHIẾU")
        days = list(service.showtimes.keys())
        if 'selected_date' not in st.session_state: st.session_state['selected_date'] = days[0]
        s_day = st.selectbox("Chọn Ngày", days, index=days.index(st.session_state['selected_date']), label_visibility="collapsed")
        st.session_state['selected_date'] = s_day

        st.write("")
        times = service.showtimes.get(s_day, [])
        s_time = st.radio("Chọn Giờ", times, horizontal=True)
        st.session_state['selected_time'] = s_time

        seats = st.session_state['selected_seats']
        count = len(seats)

        # Logic VIP: Hàng C-E, Cột 3-6
        def is_vip(seat_code):
            row_char = seat_code[0]
            col_num = int(seat_code[1:])
            return row_char in ['C', 'D', 'E'] and (3 <= col_num <= 6)

        total_price = sum([movie.price + (15000 if is_vip(s) else 0) for s in seats])

        st.markdown(f"""
        <div style="background: white; color: #333; padding: 20px; border-radius: 15px; margin-top: 25px; box-shadow: 0 10px 30px rgba(0,0,0,0.2);">
            <div style="text-align: center; font-weight: 800; letter-spacing: 2px; font-size: 16px; margin-bottom: 15px; color: #16213e;">TICKET INFO</div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color:#666;">Phim</span><strong>{movie.title[:15]}...</strong>
            </div>
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span style="color:#666;">Ghế</span><strong>{', '.join(seats) if count else '--'}</strong>
            </div>
            <hr style="border-top: 2px dashed #ccc; margin: 15px 0;">
            <div style="display: flex; justify-content: space-between; font-size: 24px; font-weight: 800;">
                <span>TỔNG</span><span style="color: #d63031;">{total_price:,.0f} đ</span>
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
                        save_booking(movie.id, s_day, s_time, seats)
                        st.session_state['selected_seats'] = []
                        st.balloons()
                        st.success("Đặt vé thành công!")
                        et.sleep(2)
                        st.session_state['page'] = 'home'
                        st.rerun()

    # --- 3. CỘT PHẢI: MÀN HÌNH & LƯỚI GHẾ ---
    with col_R:
        st.markdown("""
            <div style="perspective: 600px; margin-bottom: 30px; text-align: center;">
                <div style="width: 70%; margin: 0 auto; height: 6px; background: #e0e0e0; box-shadow: 0 15px 40px rgba(255,255,255,0.6); border-radius: 50%; transform: rotateX(-20deg);"></div>
                <div style="margin-top: 15px; color: #888; font-size: 11px; letter-spacing: 4px;">MÀN HÌNH</div>
            </div>
        """, unsafe_allow_html=True)

        layout = service.get_seat_layout(movie.id, st.session_state['selected_date'], st.session_state['selected_time'])

        # Tạo khung bao quanh vùng chọn ghế
        st.markdown('<div style="border: 2px dashed rgba(255,255,255,0.1); border-radius: 12px; padding: 15px; width: fit-content; margin: 0 auto;">', unsafe_allow_html=True)

        # --- CSS GỐC CHO LƯỚI GHẾ (Đảm bảo tỷ lệ 48x40px) ---
        with stylable_container(
                key="seat_grid_fixed",
                css_styles="""
                button {
                    width: 48px !important;
                    height: 40px !important;
                    padding: 0 !important;
                    margin: 3px 0 !important;
                    border-radius: 8px !important;
                    border: 1px solid rgba(255,255,255,0.3) !important;
                    background-color: transparent !important;
                    color: white !important;
                    transition: all 0.2s;
                }
                button:hover {
                    border-color: #ff4b2b !important;
                    background-color: rgba(255, 255, 255, 0.1) !important;
                    transform: scale(1.1);
                }
                button[kind="primary"] {
                    background-color: #2ecc71 !important;
                    border-color: #27ae60 !important;
                    box-shadow: 0 0 10px #2ecc71 !important;
                }
                button:disabled {
                    background-color: #383838 !important;
                    border: 1px solid #444 !important;
                    color: #666 !important;
                    opacity: 1 !important;
                    cursor: not-allowed;
                }
            """
        ):
            for r, row in enumerate(layout):
                cols = st.columns([0.5] + [1]*8 + [0.5])
                for c, status in enumerate(row):
                    seat_id = f"{chr(65 + r)}{c + 1}"
                    # Logic xác định ghế VIP (Hàng C-E, Cột 3-6)
                    is_vip_seat = (chr(65 + r) in ['C', 'D', 'E']) and (3 <= (c + 1) <= 6)

                    with cols[c+1]:
                        # --- NẾU LÀ GHẾ VIP: Bọc thêm lớp CSS viền vàng ---
                        if is_vip_seat:
                            with stylable_container(
                                    key=f"vip_{seat_id}",
                                    css_styles="""
                                    button {
                                        border: 2px solid #f1c40f !important; /* VIỀN VÀNG */
                                        color: #f1c40f !important; /* Chữ vàng */
                                    }
                                    button:hover {
                                        box-shadow: 0 0 10px #f1c40f !important;
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
                                if st.button(f"{seat_id}", key=seat_id, type="primary"):
                                    st.session_state['selected_seats'].remove(seat_id)
                                    st.rerun()
                            else:
                                if st.button(f"{seat_id}", key=seat_id):
                                    st.session_state['selected_seats'].append(seat_id)
                                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        # Chú thích thêm màu VIP
        xc1, xc2, xc3, xc4, xc5 = st.columns([1, 1.5, 1.5, 1.5, 1.5])
        with xc2: st.markdown("⬜ **Thường**")
        with xc3: st.markdown("🟨 **Vùng VIP**") # Chú thích cho vùng trung tâm
        with xc4: st.markdown("⬛ **Đã đặt**")
        with xc5: st.markdown("🟢 **Đang chọn**")