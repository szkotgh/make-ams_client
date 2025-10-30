import subprocess, threading, queue, shutil, time, os

_MPG123_CMD = "mpg123"
_WATCHDOG_INTERVAL = 1.0

class SpeakerManager:
    def __init__(self, mpg123_cmd=_MPG123_CMD):
        if shutil.which(mpg123_cmd) is None:
            raise FileNotFoundError(f"{mpg123_cmd} not found. Install mpg123.")
        self._cmd = mpg123_cmd
        self._proc = None
        self._lock = threading.RLock()
        self._queue = queue.Queue()
        self._stop = threading.Event()
        self._current = None
        self._volume = 100
        self.STATUS_IDLE = "idle"
        self.STATUS_PLAYING = "playing"
        self.STATUS_STOPPED = "stopped"
        self._status = self.STATUS_IDLE

        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._watchdog = threading.Thread(target=self._watchdog_loop, daemon=True)
        self._reader = threading.Thread(target=self._reader_loop, daemon=True)

        self._start_proc()
        self._worker.start()
        self._watchdog.start()
        self._reader.start()

    def _start_proc(self):
        with self._lock:
            if self._proc and self._proc.poll() is None:
                return
            self._proc = subprocess.Popen(
                [self._cmd, "-R"],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL,
                text=True,
                bufsize=1,
            )
            time.sleep(0.05)

    def _send(self, cmd):
        with self._lock:
            if not self._proc or self._proc.poll() is not None:
                return False
            try:
                self._proc.stdin.write(cmd + "\n")
                self._proc.stdin.flush()
                return True
            except Exception:
                return False

    def _reader_loop(self):
        while not self._stop.is_set():
            proc = self._proc
            if not proc or not proc.stdout:
                time.sleep(0.2)
                continue
            line = proc.stdout.readline()
            if not line:
                time.sleep(0.1)
                continue
            if line.startswith("@P 0"):
                self._status = self.STATUS_IDLE
                self._current = None

    def _worker_loop(self):
        while not self._stop.is_set():
            try:
                target = self._queue.get(timeout=0.2)
            except queue.Empty:
                continue
            if target is None:
                break
            if not (target.startswith("http://") or target.startswith("https://") or target.startswith("rtsp://")):
                if not os.path.isfile(target):
                    continue
            self._start_proc()
            self._send(f"LOAD {target}")
            self._send(f"VOLUME {self._volume}")
            self._current = target
            self._status = self.STATUS_PLAYING
            while self._current == target and not self._stop.is_set():
                time.sleep(0.2)
        self._status = self.STATUS_IDLE

    def _watchdog_loop(self):
        while not self._stop.is_set():
            with self._lock:
                proc = self._proc
            if not proc or proc.poll() is not None:
                self._start_proc()
            time.sleep(_WATCHDOG_INTERVAL)

    def play(self, target):
        self.cancel()
        self._queue.queue.clear()
        self._queue.put(target)
        self._status = self.STATUS_PLAYING

    def enqueue(self, target):
        self._queue.put(target)

    def cancel(self):
        self._send("STOP")
        self._current = None
        self._status = self.STATUS_STOPPED

    def set_volume(self, percent):
        try:
            val = int(percent)
            val = max(0, min(100, val))
        except Exception:
            raise ValueError("Volume must be integer 0–100")
        self._volume = val
        self._send(f"VOLUME {val}")

    def get_status(self):
        return {
            "status": self._status,
            "current": self._current,
            "volume": self._volume
        }

    def shutdown(self):
        self._stop.set()
        try:
            self._queue.put_nowait(None)
        except Exception:
            pass
        self._send("QUIT")
        with self._lock:
            if self._proc:
                try:
                    self._proc.stdin.close()
                except Exception:
                    pass
                self._proc = None
        self._status = self.STATUS_STOPPED