import speech_recognition as sr


class SpeechToText:
    def __init__(self, language="vi-VN"):
        self.recognizer = sr.Recognizer()
        self.language = language

    def listen(self, timeout=5, phrase_time_limit=7):
        """
        Nghe giọng nói từ microphone và chuyển thành văn bản
        """
        with sr.Microphone() as source:
            self.recognizer.adjust_for_ambient_noise(source, duration=0.5)

            try:
                audio = self.recognizer.listen(
                    source,
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                text = self.recognizer.recognize_google(
                    audio,
                    language=self.language
                )
                return text

            except sr.WaitTimeoutError:
                return "TIMEOUT"

            except sr.UnknownValueError:
                return "UNKNOWN"

            except Exception as e:
                return f"ERROR: {str(e)}"

