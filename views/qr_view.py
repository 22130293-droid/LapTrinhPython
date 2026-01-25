import streamlit as st
from booking_and_voice_search.booking_serveice import save_booking
from core.email_service import send_ticket_email
from booking_and_voice_search.qr_service import generate_qr_url
from booking_and_voice_search.booking_serveice import generate_booking_id

def render_qr_overlay():
    info = st.session_state.get("payment_info")
    if not info:
        return

    seats = info.get("seats", [])
    if not isinstance(seats, list):
        seats = [str(seats)]

    amount = int(info["total_price"])
    if "booking_id" not in info:
        info["booking_id"] = generate_booking_id(info["movie_id"])

    booking_id = info["booking_id"]

    qr_image_url = generate_qr_url(
        amount=amount,
        movie_title=info["movie_title"],
        booking_id=info["booking_id"]
    )

    @st.dialog("THANH TOÁN QR", width="small")
    def qr_popup():
        st.markdown(
            f"""
            <div style="text-align:center;">
                <img src="{qr_image_url}"
                     style="width:220px;margin:15px auto;display:block;" />
            <b>Ngân hàng:</b> TPBank<br>
            <b>Số tài khoản:</b> 5996&nbsp;5725&nbsp;212<br>
            <b>Chủ tài khoản:</b> TRAN VAN DONG<br>
            <i style="color:#000000;">Quét QR để thanh toán</i>

            </div>
            """,
            unsafe_allow_html=True
        )

        _, col1, col2, _ = st.columns([1, 2, 2, 1])

        with col1:
            if st.button("ĐÃ THANH TOÁN", type="primary", use_container_width=True):
                save_booking(
                    st.session_state.get('user_id', 0),  # Thêm ID người dùng vào đây
                    info["movie_id"],
                    info["day"],
                    info["time"],
                    seats,
                    info["total_price"]
                )

                send_ticket_email(
                    info.get("email", ""),
                    info.get("username", "Khách hàng"),
                    info["movie_title"],
                    info["day"],
                    info["time"],
                    seats,
                    amount,
                    booking_id
                )

                st.session_state["show_qr"] = False
                st.session_state.pop("payment_info", None)
                st.session_state["selected_seats"] = []

                st.success(" Thanh toán thành công!")
                st.rerun()

        with col2:
            if st.button("HỦY", type="primary", use_container_width=True):
                st.session_state["show_qr"] = False
                st.session_state.pop("payment_info", None)
                st.rerun()

    qr_popup()
