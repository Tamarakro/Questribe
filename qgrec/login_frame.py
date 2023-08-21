import tkinter as tk
from tkinter import ttk  # Import ttk for ComboBox
import tkinter.simpledialog
from tkinter import messagebox
import bcrypt
from .db_manager import DB
from .constants import colors, font, x_pad, y_pad


class LoginApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.root = master
        self.configure(background=colors.get("white"))

        # Create labels and entry widgets for login
        self.username_label = ttk.Label(
            self,
            text="Username:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.username_entry = ttk.Entry(
            self, font=font, background=colors.get("white"), width=40
        )

        self.password_label = ttk.Label(
            self,
            text="Password:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.password_entry = ttk.Entry(
            self, show="*", font=font, background=colors.get("white"), width=40
        )

        # Create a button to log in

        self.login_button = ttk.Button(
            self, text="Log In", command=self.login, style="Default.TButton"
        )

        # No account prompt and sign up button

        self.no_account_label = ttk.Label(
            self,
            text="No account?",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.signup_button = ttk.Button(
            self, text="Sign Up", command=self.open_signup_page, style="Default.TButton"
        )

        self.username_label.pack(anchor="w", padx=x_pad, pady=y_pad)
        self.username_entry.pack(padx=x_pad, pady=y_pad)
        self.password_label.pack(anchor="w", padx=x_pad, pady=y_pad)
        self.password_entry.pack(padx=x_pad, pady=y_pad)
        self.login_button.pack(padx=x_pad, pady=y_pad)
        self.no_account_label.pack(padx=x_pad, pady=y_pad)
        self.signup_button.pack(padx=x_pad, pady=y_pad)

    def login(self):
        user = None

        try:
            uname = self.username_entry.get().lower()

            password = self.password_entry.get()

            if not (uname and password):
                raise Exception("Required fields not filled")

            user = DB.getuser(uname)

            if not user:
                raise Exception("User does not exist")

            pword_bytes = password.encode("utf-8")

            if not (bcrypt.checkpw(pword_bytes, user[4])):
                raise Exception("Wrong Password")

        except Exception as e:
            messagebox.showerror("Error when Logging In", str(e))

        else:
            messagebox.showinfo("Log In", "Login Successful!")

            self.open_gesture_recognition_page(user[0], user[3], user[5])

    def open_signup_page(self):
        self.root.show_signup()

    def open_gesture_recognition_page(self, userid, uname, lang):
        self.root.show_gesture_app(userid, uname, lang)
