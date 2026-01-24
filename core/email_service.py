import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import EMAIL_SENDER, EMAIL_PASSWORD
from booking_and_voice_search.qr_service import generate_ticket_qr_base64
from email.mime.image import MIMEImage
import smtplib
import base64

def send_email(to_email, subject, body):
    """Hàm gửi email cơ bản (Core function)"""
    if not EMAIL_SENDER or not EMAIL_PASSWORD:
        return False, "Chưa cấu hình Email Server trong config.py"

    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_SENDER
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        # Kết nối tới Gmail SMTP
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        text = msg.as_string()
        server.sendmail(EMAIL_SENDER, to_email, text)
        server.quit()
        return True, "Gửi thành công!"
    except Exception as e:
        return False, f"Lỗi gửi mail: {str(e)}"

# --- 1. Hàm gửi vé (Khi đặt vé thành công) ---

def send_ticket_email(to_email, username, movie_title, date, time, seats, total_price, booking_id):
    # 1. QR
    qr_base64 = generate_ticket_qr_base64(
        booking_id=booking_id,
        movie_title=movie_title,
        date=date,
        time=time,
        seats=seats,
        total_price=total_price
    )
    qr_bytes = base64.b64decode(qr_base64)

    # 2. Root message
    msg = MIMEMultipart("related")
    msg["From"] = EMAIL_SENDER
    msg["To"] = to_email
    msg["Subject"] = f"🎟️ VÉ XEM PHIM: {movie_title}"

    # 3. Alternative (BẮT BUỘC)
    alternative = MIMEMultipart("alternative")
    msg.attach(alternative)

    # 4. HTML body
    html_body = f"""
    <html>
    <body>
        <h2 style="color:#e52d27;">Cảm ơn {username} đã đặt vé tại Start Cinema!</h2>

        <div style="border:2px dashed #333; padding:20px; background:#f9f9f9;">
            <p><strong>Mã vé:</strong> {booking_id}</p>
            <p><strong>Phim:</strong> {movie_title}</p>
            <p><strong>Suất chiếu:</strong> {date} | {time}</p>
            <p><strong>Ghế:</strong> {', '.join(seats)}</p>
            <hr>
            <strong>Tổng tiền: {total_price:,.0f} đ</strong>
        </div>

        <h3>MÃ QR NHẬN VÉ</h3>
        <img src="cid:ticket_qr" width="180"/>

        <p><i>Start Cinema AI System</i></p>
    </body>
    </html>
    """

    alternative.attach(MIMEText(html_body, "html"))

    # 5. Image CID
    qr_img = MIMEImage(qr_bytes, "png")
    qr_img.add_header("Content-ID", "<ticket_qr>")
    qr_img.add_header("Content-Disposition", "inline", filename="ticket_qr.png")
    msg.attach(qr_img)

    # 6. Send
    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

    return True, "Gửi vé thành công"

# --- 2. Hàm gửi mật khẩu mới (Khi quên mật khẩu) ---
def send_reset_password_email(to_email, new_password):
    subject = "🔐 Cấp lại mật khẩu - Start Cinema"
    body = f"""
    <html>
    <body>
        <p>Xin chào,</p>
        <p>Yêu cầu cấp lại mật khẩu của bạn đã được xử lý.</p>
        <p>Mật khẩu mới của bạn là: <strong style="font-size: 20px; color: #e52d27;">{new_password}</strong></p>
        <p>Vui lòng đăng nhập và đổi lại mật khẩu ngay để bảo mật.</p>
        <br>
        <p><i>Start Cinema Support Team</i></p>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)

# --- 3. Hàm gửi mail chào mừng (Khi đăng ký thành công) - ĐÃ BỔ SUNG ---
def send_welcome_email(to_email, username):
    subject = "🎉 Chào mừng bạn đến với Start Cinema!"
    body = f"""
    <html>
    <body>
        <h2 style="color: #e52d27;">Xin chào {username},</h2>
        <p>Chúc mừng bạn đã đăng ký tài khoản thành công tại hệ thống Start Cinema.</p>
        <p>Bây giờ bạn có thể:</p>
        <ul>
            <li>Đặt vé xem phim trực tuyến.</li>
            <li>Nhận vé điện tử qua email.</li>
            <li>Tra cứu lịch chiếu nhanh chóng.</li>
        </ul>
        <p>Hãy truy cập ứng dụng và trải nghiệm ngay!</p>
        <br>
        <p>Trân trọng,</p>
        <p><i>Start Cinema Team</i></p>
    </body>
    </html>
    """
    return send_email(to_email, subject, body)
