import tkinter as tk

class PageAuthQR(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="QR Auth").pack(pady=50)
        tk.Button(self, text="Back to Main",
                  command=lambda: controller.show_page("MainPage")).pack()
