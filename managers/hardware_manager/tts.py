import threading
from google.cloud import texttospeech

class TTSManager:
    '''
        Require: enviroment variable GOOGLE_APPLICATION_CREDENTIALS\n
        GOOGLE_APPLICATION_CREDENTIALS: Service Account Key JSON file path\n\n
        https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries#before
    '''
    
    def __init__(self):
        from managers.hardware_manager import speaker
        self.speaker = speaker

    def _gen_tts_url(self, text):
        url = f"https://cache-a.oddcast.com/tts/genC.php?EID=3&LID=13&VID=6&EXT=mp3&TXT={text}"
        return url

    def play(self, text: str):
        print(f"[TTSManager] Playing: {text}")
        self.speaker.play(self._gen_tts_url(text))

    def stop(self):
        self.speaker.stop()