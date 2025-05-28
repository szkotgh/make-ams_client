import tkinter as tk

class PageAuthButton(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        tk.Label(self, text="Button AUTH").pack(pady=50)
        tk.Button(self, text="Back to Main",
                  command=lambda: controller.show_page("MainPage")).pack()
