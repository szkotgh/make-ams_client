import os
import platform
import threading

class SpeakerManager:
    def __init__(self):
        self._current_thread = None

    def play(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError()

        if self._current_thread and self._current_thread.is_alive():
            self.stop()

        self._current_thread = threading.Thread(target=self._play_file, args=(file_path,))
        self._current_thread.start()

    def _play_file(self, file_path):
        system = platform.system()
        if system == "Darwin":  # macOS
            os.system(f"afplay '{file_path}'")
        elif system == "Windows":
            os.system(f'start /min wmplayer "{file_path}"')
        elif system == "Linux":
            os.system(f"aplay '{file_path}' || paplay '{file_path}' || ffplay -nodisp -autoexit '{file_path}'")
        else:
            raise NotImplementedError("not support os error: " + system)

    def stop(self):
        system = platform.system()
        if system == "Darwin":
            os.system("killall afplay")
        elif system == "Windows":
            os.system("taskkill /im wmplayer.exe /f")
        elif system == "Linux":
            os.system("killall aplay paplay ffplay")
        if self._current_thread:
            self._current_thread.join(timeout=1)
            self._current_thread = None

service = SpeakerManager()