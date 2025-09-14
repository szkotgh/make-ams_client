import os
import tkinter as tk
import subprocess
from managers import auth_manager
import setting
import utils
import managers.log_manager as log_manager
import managers.hardware_manager as hardware_manager

class PageAdminMain(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.admin_frame = tk.Frame(self)
        self.admin_frame.pack(expand=True)

        title_frame = tk.Frame(self.admin_frame)
        title_frame.pack(pady=30)

        tk.Label(title_frame, text="관리자 메뉴", font=(setting.DEFAULT_FONT, 28, "bold"), fg="black").pack(pady=10)
        tk.Label(title_frame, text=f"PID: {utils.get_program_pid()} | 디스플레이 크기: {utils.get_display_size()}", font=(setting.DEFAULT_FONT, 16), fg="black").pack()
        self.wifi_label = tk.Label(title_frame, text=f"연결정보: ", font=(setting.DEFAULT_FONT, 16), fg="black")
        self.uptime = utils.get_now_datetime() - setting.START_TIME
        self.uptime_label = tk.Label(title_frame, text=f"작동시간: | 마지막 하트비트: ", font=(setting.DEFAULT_FONT, 16), fg="black")
        def update_wifi_info():
            ssid = utils.get_wifi_ssid()
            lan_ip = utils.get_lan_ip()
            self.wifi_label.config(text=f"연결정보: {ssid if ssid else '없음'}({lan_ip if lan_ip else '없음'})")
            self.wifi_label.after(3000, update_wifi_info)
        update_wifi_info()
        self.wifi_label.pack()
        def update_uptime():
            time_label = str(self.uptime)[:-7]
            self.uptime = utils.get_now_datetime() - setting.START_TIME
            self.uptime_label.config(text=f"작동시간: {time_label} | 마지막 하트비트: {auth_manager.service.last_internet_heartbeat}")
            self.uptime_label.after(1000, update_uptime)
        update_uptime()
        self.uptime_label.pack()

        button_frame = tk.Frame(self.admin_frame)
        button_frame.pack()

        button_frame_two = tk.Frame(self.admin_frame)
        button_frame_two.pack()

        # 버튼 객체 저장
        self.button_reboot = tk.Button(button_frame, text="시스템 재시작", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=self.reboot_system)
        self.button_reboot.pack(side="left", padx=2)
        self.button_exit = tk.Button(button_frame, text="프로그램 종료", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=self.program_exit)
        self.button_exit.pack(side="left", padx=2)
        self.button_restart = tk.Button(button_frame, text="프로그램 재시작", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=self.program_restart)
        self.button_restart.pack(side="left", padx=2)
        self.button_open_door = tk.Button(button_frame, text="자동문 작동", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=self.open_door)
        self.button_open_door.pack(side="left", padx=2)
        self.button_log = tk.Button(button_frame, text="로그 열람", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.controller.show_page("PageAdminLog"))
        self.button_log.pack(side="left", padx=2)

        self.button_force_open = tk.Button(button_frame_two, text="문 열어놓기", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=lambda: self.controller.show_page("PageAdminForceOpen"))
        self.button_force_open.pack(side="left", padx=2)
        self.button_tts = tk.Button(button_frame_two, text="TTS테스트", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=self.test_tts)
        self.button_tts.pack(side="left", padx=2)
        self.button_sound = tk.Button(button_frame_two, text="소리테스트", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=self.test_sound)
        self.button_sound.pack(side="left", padx=2)
        self.button_test_qr = tk.Button(button_frame_two, text="QR테스트", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=self.test_qr)
        self.button_test_qr.pack(side="left", padx=2)
        self.button_test_nfc = tk.Button(button_frame_two, text="NFC테스트", font=(setting.DEFAULT_FONT, 16, 'bold'), height=2, command=self.test_nfc)
        self.button_test_nfc.pack(side="left", padx=2)
        self.button_close_admin = tk.Button(self.admin_frame, text="관리자 종료", font=(setting.DEFAULT_FONT, 14), width=14, height=2, command=self.close_admin_page)
        self.button_close_admin.pack(pady=10)

        self.all_buttons = [self.button_reboot, self.button_exit, self.button_restart, self.button_open_door, self.button_log, self.button_force_open, self.button_tts, self.button_sound, self.button_test_qr, self.button_test_nfc, self.button_close_admin]

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