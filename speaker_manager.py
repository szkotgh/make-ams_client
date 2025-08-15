import pygame
import threading
import time
import os

class SpeakerManager:
    def __init__(self):
        os.environ['SDL_AUDIODRIVER'] = 'alsa'
        
        pygame.mixer.init(
            frequency=44100,
            size=-16,
            channels=2,
            buffer=512,
            allowedchanges=pygame.AUDIO_ALLOW_FREQUENCY_CHANGE
        )
        
        self._lock = threading.Lock()
        self._current_file = None
        self._is_playing = False
        self._play_thread = None
        self._volume = 1.0
        
        time.sleep(0.2)

    def set_volume(self, volume):
        with self._lock:
            self._volume = max(0.0, min(1.0, volume))
            try:
                pygame.mixer.music.set_volume(self._volume)
            except Exception as e:
                print(f"Error setting volume: {e}")

    def play(self, file_path):
        def _play():
            with self._lock:
                try:
                    if self._is_playing:
                        pygame.mixer.music.stop()
                        time.sleep(0.1)
                    
                    if not os.path.exists(file_path):
                        print(f"Audio file not found: {file_path}")
                        return
                    
                    pygame.mixer.music.load(file_path)
                    pygame.mixer.music.set_volume(self._volume)
                    pygame.mixer.music.play()
                    self._current_file = file_path
                    self._is_playing = True
                    
                    while pygame.mixer.music.get_busy():
                        time.sleep(0.05)
                    
                    self._is_playing = False
                    self._current_file = None
                    
                except Exception as e:
                    print(f"Error playing sound: {e}")
                    self._is_playing = False
                    self._current_file = None

        if self._play_thread and self._play_thread.is_alive():
            self._play_thread.join(timeout=0.2)
        
        self._play_thread = threading.Thread(target=_play, daemon=True)
        self._play_thread.start()

    def stop(self):
        with self._lock:
            try:
                pygame.mixer.music.stop()
                self._is_playing = False
                self._current_file = None
            except Exception as e:
                print(f"Error stopping sound: {e}")

service = SpeakerManager()