from .speech_to_text import SpeechToText

class VoiceSearchController:
    def __init__(self):
        self.stt = SpeechToText(language="vi-VN")

    def get_voice_query(self):
        """
        Kích hoạt micro và lấy nội dung tìm kiếm
        """
        result = self.stt.listen()

        if result == "TIMEOUT":
            return None, "⏱️ Không nghe thấy giọng nói"

        if result == "UNKNOWN":
            return None, " Không nhận diện được giọng nói"

        if result.startswith("ERROR"):
            return None, " Lỗi micro"

        return result, None
