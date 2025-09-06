import os
import threading
import time
import pygame
import logging

logging.basicConfig(level=logging.WARNING)

class Speaker:
    def __init__(self):
        os.environ['SDL_AUDIODRIVER'] = 'alsa'
        try:
            pygame.mixer.init(
                frequency=44100,
                size=-16,
                channels=2,
                buffer=512,
                allowedchanges=pygame.AUDIO_ALLOW_FREQUENCY_CHANGE
            )
        except pygame.error as e:
            logging.warning(f"[Speaker] Failed to initialize mixer: {e}")
        self._lock = threading.Lock()
        self._volume = 1.0
        self._play_thread = None
        self._current_file = None

    def set_volume(self, volume):
        with self._lock:
            self._volume = max(0.0, min(1.0, volume))
            try:
                pygame.mixer.music.set_volume(self._volume)
            except pygame.error as e:
                logging.warning(f"[Speaker] Error setting volume: {e}")

    def get_volume(self):
        return self._volume

    def play(self, file_path):
        print(f"[Speaker] Playing sound: {file_path}")
        if not os.path.exists(file_path):
            logging.warning(f"[Speaker] Audio file not found: {file_path}")
            return

        def _play():
            with self._lock:
                try:
                    if pygame.mixer.music.get_busy():
                        pygame.mixer.music.stop()
                        while pygame.mixer.music.get_busy():
                            time.sleep(0.01)

                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.set_volume(self._volume)
                    pygame.mixer.music.play()
                    self._current_file = file_path
                except pygame.error as e:
                    logging.warning(f"[Speaker] Error playing sound: {e}")

        if self._play_thread is None or not self._play_thread.is_alive():
            self._play_thread = threading.Thread(target=_play, daemon=True)
            self._play_thread.start()
        else:
            self._play_thread = threading.Thread(target=_play, daemon=True)
            self._play_thread.start()

    def stop(self):
        with self._lock:
            try:
                pygame.mixer.music.stop()
                while pygame.mixer.music.get_busy():
                    time.sleep(0.01)
            except pygame.error as e:
                logging.warning(f"[Speaker] Error stopping sound: {e}")
