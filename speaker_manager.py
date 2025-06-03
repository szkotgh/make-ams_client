import os
import platform
import subprocess
import threading

class SpeakerManager:
    def __init__(self):
        self._process = None

    def play(self, file_path):
        if not os.path.isfile(file_path):
            raise FileNotFoundError()

        self.stop()

        threading.Thread(target=self._play_file, args=(file_path,), daemon=True).start()

    def _play_file(self, file_path):
        system = platform.system()
        cmd = None
        if system == "Darwin":
            cmd = ["afplay", file_path]
        elif system == "Windows":
            cmd = ["wmplayer", file_path]
        elif system == "Linux":
            cmd = ["ffplay", "-nodisp", "-autoexit", file_path]

        if cmd:
            try:
                self._process = subprocess.Popen(cmd)
                self._process.wait()
            except Exception as e:
                print(f"Error playing sound: {e}")
                self._process = None

    def stop(self):
        if self._process and self._process.poll() is None:
            self._process.terminate()
            self._process.wait()
        self._process = None

service = SpeakerManager()