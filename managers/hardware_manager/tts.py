from pygame import mixer
import threading
from google.cloud import texttospeech

class TTSManager:
    '''
        Require: enviroment variable GOOGLE_APPLICATION_CREDENTIALS\n
        GOOGLE_APPLICATION_CREDENTIALS: Service Account Key JSON file path\n\n
        https://cloud.google.com/text-to-speech/docs/quickstart-client-libraries#before
    '''
    
    def __init__(self):
        self.is_initialized = False
        self.sound = None
        self.channel = None
        self.channel_ready = threading.Event()
        self.FILE_SAVE_PATH = ".tts_temp.mp3"
        
        print("[TTSManager] Initializing...")
        try:
            self.client = texttospeech.TextToSpeechClient()
            
            # Edit this section to set the pronunciation.
            # https://cloud.google.com/text-to-speech/docs/list-voices-and-types
            self.voice = texttospeech.VoiceSelectionParams(
                language_code="ko-KR",
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
                name="ko-KR-Standard-B"
            )
            self.audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.1,
            )
            
            mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("[TTSManager] Initialized")
            self.is_initialized = True
        except Exception as e:
            print(f"[TTSManager] Initialization Error: {e}")
            self.initialization_error_detail = str(e)
            self.is_initialized = False

    def _play_internal(self, text: str):
        try:
            synthesis_input = texttospeech.SynthesisInput(text=text)
            response = self.client.synthesize_speech(
                input=synthesis_input,
                voice=self.voice,
                audio_config=self.audio_config
            )

            if self.sound is not None:
                self.sound.stop()
                self.sound = None

            with open(self.FILE_SAVE_PATH, "wb") as out:
                out.write(response.audio_content)

            self.sound = mixer.Sound(self.FILE_SAVE_PATH)
            self.channel = self.sound.play()
            self.channel_ready.set()
        except Exception as e:
            print(f"[TTSManager] Play Error: {e}")
            self.channel_ready.clear()

    def play(self, text: str):
        if not self.is_initialized:
            print(f"[TTSManager] Not Initialized: {self.initialization_error_detail}")
            return
        print(f"[TTSManager] Playing: {text}")
        self.channel_ready.clear()
        thread = threading.Thread(target=self._play_internal, args=(text,))
        thread.start()

    def stop(self):
        if self.sound is None:
            return
        self.sound.stop()
        self.sound = None
        self.channel = None
        self.channel_ready.clear()

    def get_busy(self):
        if not self.is_initialized:
            return False
        if not self.channel_ready.is_set():
            return True
        if self.channel is None:
            return False
        return self.channel.get_busy()

    def set_volume(self, volume: float):
        if self.sound is None:
            return
        self.sound.set_volume(volume)

    def get_volume(self):
        if self.sound is None:
            return 0.0
        return self.sound.get_volume()

    def cleanup(self):
        print("[TTSManager] Cleaning up...")
        self.stop()
        mixer.quit()
        print("[TTSManager] Cleanup done.")