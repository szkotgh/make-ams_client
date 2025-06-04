import pygame
import threading

class SpeakerManager:
    def __init__(self):
        pygame.mixer.init()
        self._lock = threading.Lock()

    def play(self, file_path):
        def _play():
            with self._lock:
                try:
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.play()
                except Exception as e:
                    print(f"Error playing sound: {e}")

        threading.Thread(target=_play, daemon=True).start()

    def stop(self):
        with self._lock:
            pygame.mixer.music.stop()

service = SpeakerManager()