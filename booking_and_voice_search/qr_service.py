import qrcode
from io import BytesIO
import base64


BANK_CODE = "TPBank"
ACCOUNT_NO = "59965725212"
ACCOUNT_NAME = "TRAN VAN DONG"

@staticmethod
def generate_qr_url(amount, movie_title):
    add_info = f"Thanh toan ve {movie_title}".replace(" ", "%20")

    return (
        f"https://img.vietqr.io/image/"
        f"{BANK_CODE}-{ACCOUNT_NO}-compact.png"
        f"?amount={amount}"
        f"&addInfo={add_info}"
        f"&accountName={ACCOUNT_NAME.replace(' ', '%20')}"
    )

@staticmethod
def generate_ticket_qr_base64(
    booking_id,
    movie_title,
    date,
    time,
    seats,
    total_price
):
        qr_text = f"""
START CINEMA 
==========================
MÃ VÉ: {booking_id}
PHIM: {movie_title}
NGÀY: {date}
GIỜ: {time}
GHẾ: {', '.join(seats)}
GIÁ VÉ: {total_price:,.0f} VND
TRẠNG THÁI: ĐÃ THANH TOÁN
==========================
Xuất trình mã QR tại quầy soát vé
"""

        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=6,
            border=3,
        )

        qr.add_data(qr_text.strip())
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        return base64.b64encode(buffer.getvalue()).decode()

 
