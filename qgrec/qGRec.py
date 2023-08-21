import tkinter as tk
from tkinter import ttk  # Import ttk for ComboBox
import tkinter.simpledialog
from tkinter import messagebox
import requests
from PIL import ImageTk, Image
from io import BytesIO

from .db_manager import DB
from .constants import (
    colors,
    font,
    x_pad,
    y_pad,
    LANGUAGE_OPTIONS,
    RESOURCES_DIR,
    DEFAULT_LANGUAGE,
)
from .gesture_frame import GestureRecognitionApp
from .login_frame import LoginApp
from .register_frame import SignupApp


class MainWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.configure(background=colors.get("white"))
        self.protocol("WM_DELETE_WINDOW", self.close_window)

        # Configure ttk  Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure Default Button Style
        self.style.configure(
            "Default.TButton",
            background=colors.get("blue"),
            font=font,
            border=0,
            borderwidth=0,
            relief="flat",
        )

        self.login_page = LoginApp(self)
        self.signup_page = SignupApp(self)
        self.gesture_app = GestureRecognitionApp(self)

        self.home_page = ttk.Frame()

        welcome_label = ttk.Label(
            self.home_page,
            text="Welcome to QG-REC",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=(font[0], 24, "bold"),
        )

        welcome_label_two = ttk.Label(
            self.home_page,
            text="A hand gesture recognition system that helps people connect.",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.signup_button = ttk.Button(
            self.home_page,
            text="Sign Up",
            command=self.show_signup,
            style="Default.TButton",
        )
        self.login_button = ttk.Button(
            self.home_page,
            text="Log In",
            command=self.show_login,
            style="Default.TButton",
        )

        self.guest_button = ttk.Button(
            self.home_page,
            text="Continue as Guest",
            command=self.show_gesture_app,
            style="Default.TButton",
        )

        welcome_label.pack(padx=x_pad, pady=(5, 15), expand=True)
        welcome_label_two.pack(padx=x_pad, pady=(5, 25), expand=True)
        self.login_button.pack(padx=x_pad, pady=y_pad, expand=True)
        self.signup_button.pack(padx=x_pad, pady=y_pad, expand=True)
        self.guest_button.pack(padx=x_pad, pady=y_pad, expand=True)

        self.show_home()

    def show_login(self):
        self.clear_page()
        self.center_window(500, 300)
        self.title("QG-REC: Log In")
        self.login_page.pack(anchor="center", expand=True)

    def show_signup(self):
        self.clear_page()
        self.title("QG-REC: Sign Up")
        self.center_window(500, 600)
        self.signup_page.pack(anchor="center", expand=True)

    def show_gesture_app(self, userid=None, uname=None, lang=DEFAULT_LANGUAGE):
        self.clear_page()
        self.title("QG-REC")
        self.center_window(1300, 950)
        self.gesture_app.set_user_details(userid, uname, lang)
        self.gesture_app.pack(anchor="center", expand=True)

    def show_home(self):
        self.clear_page()
        self.title("QG-REC: Welcome")
        self.center_window(800, 600)
        self.home_page.pack(anchor="center", expand=True)

    def clear_page(self):
        if self.home_page.winfo_ismapped():
            self.home_page.pack_forget()
        if self.signup_page.winfo_ismapped():
            self.signup_page.pack_forget()
        if self.gesture_app.winfo_ismapped():
            self.gesture_app.pack_forget()
        if self.login_page.winfo_ismapped():
            self.login_page.pack_forget()

    def center_window(self, width, height):
        # get screen width and height
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()

        x_offset = (screen_width / 2) - (width / 2)
        y_offset = (screen_height / 2) - (height / 2)

        self.geometry("%dx%d+%d+%d" % (width, height, x_offset, y_offset))

    def close_window(self):
        self.gesture_app.exit()
        self.destroy()
