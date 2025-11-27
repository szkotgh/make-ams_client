import os
import tkinter as tk
import subprocess
import threading
from managers import auth_manager
import setting
import utils
import managers.log_manager as log_manager
import managers.hardware_manager as hardware_manager

class PageAdminMain(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.inactivity_timer = None
        self.countdown_timer = None
        self.remaining_seconds = 60

        self.admin_frame = tk.Frame(self)
        self.admin_frame.pack(expand=True)

        title_frame = tk.Frame(self.admin_frame)
        title_frame.pack(pady=30)

        tk.Label(title_frame, text="관리자 메뉴", font=(setting.DEFAULT_FONT, 28, "bold"), fg="black").pack(pady=10)
        self.src_label = tk.Label(title_frame, text=f"PID: {utils.get_program_pid()} | DS:{utils.get_display_size()}", font=(setting.DEFAULT_FONT, 12), fg="black")
        self.wifi_label = tk.Label(title_frame, text=f"연결정보: ", font=(setting.DEFAULT_FONT, 12), fg="black")
        self.system_label = tk.Label(title_frame, text=f"CPU:n%(n℃) | RAM:n% | DISK:n%", font=(setting.DEFAULT_FONT, 12), fg="black")
        self.uptime = utils.get_now_datetime() - setting.START_TIME
        self.uptime_label = tk.Label(title_frame, text=f"작동시간: | 마지막 하트비트: ", font=(setting.DEFAULT_FONT, 12), fg="black")

        # Update info sections
        def update_src_info():
            self.src_label.config(text=f"PID: {utils.get_program_pid()} | DS:{utils.get_display_size()}")
            self.src_label.after(30000, update_src_info)
        update_src_info()
        self.src_label.pack()

        def update_system_info():
            def fetch_and_update():
                hardware_info = utils.get_hardware_info()
                cpu_usage = round(sum(hardware_info["cpu_usages"]) / hardware_info["cpu_count"], 2)
                cpu_temp = round(hardware_info['cpu_temp'], 1)
                memory_usage = f"{utils.format_bytes(hardware_info['used_memory'])}/{utils.format_bytes(hardware_info['total_memory'])}"
                disk_usage = f"{utils.format_bytes(hardware_info['used_disk'])}/{utils.format_bytes(hardware_info['total_disk'])}"
                text = f"CPU:{cpu_usage}%({cpu_temp}℃) | RAM:{memory_usage} | DISK:{disk_usage}"
                self.system_label.after(0, lambda: self.system_label.config(text=text))
            threading.Thread(target=fetch_and_update, daemon=True).start()
            self.after(10000, update_system_info)
        update_system_info()
        self.system_label.pack()

        def update_wifi_info():
            ssid = utils.get_wifi_ssid()
            lan_ip = utils.get_lan_ip()
            self.wifi_label.config(text=f"연결정보: {ssid if ssid else '없음'}({lan_ip if lan_ip else '없음'})")
            self.wifi_label.after(5000, update_wifi_info)
        update_wifi_info()
        self.wifi_label.pack()

        def update_uptime():
            time_label = str(self.uptime)[:-7]
            self.uptime = utils.get_now_datetime() - setting.START_TIME
            self.uptime_label.config(text=f"작동시간: {time_label} | 마지막 하트비트: {auth_manager.service.last_internet_heartbeat}")
            self.uptime_label.after(3000, update_uptime)
        update_uptime()
        self.uptime_label.pack()

        button_frame = tk.Frame(self.admin_frame)
        button_frame.pack()

        button_frame_two = tk.Frame(self.admin_frame)
        button_frame_two.pack()

        self.button_reboot = tk.Button(button_frame, text="시스템 재시작", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(self.reboot_system))
        self.button_reboot.pack(side="left", padx=2)
        self.button_exit = tk.Button(button_frame, text="프로그램 종료", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(self.program_exit))
        self.button_exit.pack(side="left", padx=2)
        self.button_restart = tk.Button(button_frame, text="프로그램 재시작", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(self.program_restart))
        self.button_restart.pack(side="left", padx=2)
        self.button_open_door = tk.Button(button_frame, text="자동문 작동", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(self.open_door))
        self.button_open_door.pack(side="left", padx=2)
        self.button_log = tk.Button(button_frame, text="로그 열람", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(lambda: self.controller.show_page("PageAdminLog")))
        self.button_log.pack(side="left", padx=2)

        self.button_force_open = tk.Button(button_frame_two, text="문 열어놓기", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(lambda: self.controller.show_page("PageAdminForceOpen")))
        self.button_force_open.pack(side="left", padx=2)
        self.button_tts = tk.Button(button_frame_two, text="TTS테스트", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(self.test_tts))
        self.button_tts.pack(side="left", padx=2)
        self.button_sound = tk.Button(button_frame_two, text="소리테스트", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(self.test_sound))
        self.button_sound.pack(side="left", padx=2)
        self.button_test_qr = tk.Button(button_frame_two, text="QR테스트", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(self.test_qr))
        self.button_test_qr.pack(side="left", padx=2)
        self.button_test_nfc = tk.Button(button_frame_two, text="NFC테스트", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.on_user_action(self.test_nfc))
        self.button_test_nfc.pack(side="left", padx=2)
        self.button_close_admin = tk.Button(self.admin_frame, text="관리자 종료 (60)", font=(setting.DEFAULT_FONT, 14), width=14, height=2, command=lambda: self.on_user_action(self.close_admin_page))
        self.button_close_admin.pack(pady=10)

        self.all_buttons = [self.button_reboot, self.button_exit, self.button_restart, self.button_open_door,
                            self.button_log, self.button_force_open, self.button_tts, self.button_sound,
                            self.button_test_qr, self.button_test_nfc, self.button_close_admin]

        self.reset_inactivity_timer()

    def on_user_action(self, func):
        self.reset_inactivity_timer()
        func()

    def reset_inactivity_timer(self):
        if self.inactivity_timer:
            self.after_cancel(self.inactivity_timer)
        if self.countdown_timer:
            self.after_cancel(self.countdown_timer)
        self.remaining_seconds = 60
        self.update_countdown_display()
        self.inactivity_timer = self.after(60000, self.auto_close_admin_page)  # 1 minute
        self.start_countdown()
    
    def start_countdown(self):
        if self.countdown_timer:
            self.after_cancel(self.countdown_timer)
        self.countdown_timer = self.after(1000, self.update_countdown)
    
    def update_countdown(self):
        if self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.update_countdown_display()
            self.countdown_timer = self.after(1000, self.update_countdown)
    
    def update_countdown_display(self):
        self.button_close_admin.config(text=f"관리자 종료 ({self.remaining_seconds})")
    
    def auto_close_admin_page(self):
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        log_manager.service.insert_log("ADMIN", "LOGOUT", "1분 이상 동작이 없어 관리자 페이지를 자동 종료했습니다.")
        self.controller.show_page("MainPage")

    def disable_all_buttons(self):
        for btn in self.all_buttons:
            btn.config(state="disabled")

    def test_tts(self):
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        log_manager.service.insert_log("ADMIN", "TEST", "TTS 테스트를 실행했습니다.")
        hardware_manager.tts.play("이 소리가 들리면 정상입니다.")

    def test_sound(self):
        log_manager.service.insert_log("ADMIN", "TEST", "소리 테스트를 실행했습니다.")
        hardware_manager.speaker.play(setting.ELEVATOR_MUSIC)

    def test_qr(self):
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        log_manager.service.insert_log("ADMIN", "TEST", "QR 테스트 페이지로 이동했습니다.")
        self.controller.show_page("PageAdminTestQR")

    def test_nfc(self):
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        log_manager.service.insert_log("ADMIN", "TEST", "NFC 테스트 페이지로 이동했습니다.")
        self.controller.show_page("PageAdminTestNFC")

    def reboot_system(self):
        self.disable_all_buttons()
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        hardware_manager.cleanup()
        log_manager.service.insert_log("ADMIN", "REBOOT", "관리자가 시스템을 재시작했습니다.")
        log_manager.service.log_close()
        subprocess.run("sudo reboot now", shell=True)

    def program_exit(self):
        self.disable_all_buttons()
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        hardware_manager.cleanup()
        log_manager.service.insert_log("ADMIN", "STOP", "관리자가 프로그램을 종료했습니다.")
        log_manager.service.log_close()
        os._exit(0)

    def program_restart(self):
        self.disable_all_buttons()
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        hardware_manager.cleanup()
        log_manager.service.insert_log("ADMIN", "RESTART", "관리자가 프로그램을 재시작했습니다.")
        log_manager.service.log_close()
        os._exit(1)

    def open_door(self):
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        hardware_manager.door.auto_open_door()
        self.button_open_door.config(state="disabled")
        self.after(3000, lambda: self.button_open_door.config(state="normal"))
        log_manager.service.insert_log("ADMIN", "DOOR_OPEN", "관리자가 수동으로 문을 열었습니다.")

    def close_admin_page(self):
        hardware_manager.speaker.play(setting.CLICK_SOUND_PATH)
        log_manager.service.insert_log("ADMIN", "LOGOUT", "관리자 페이지를 종료했습니다.")
        self.controller.show_page("MainPage")

    def on_show(self):
        log_manager.service.insert_log("ADMIN", "ACCESS", "관리자 메인 페이지에 접근했습니다.")
        self.reset_inactivity_timer()
