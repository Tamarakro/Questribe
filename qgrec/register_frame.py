import tkinter as tk
from tkinter import ttk  # Import ttk for ComboBox
import tkinter.simpledialog
from tkinter import messagebox
import bcrypt
from .db_manager import DB
from .constants import colors, font, x_pad, y_pad, LANGUAGE_OPTIONS, DEFAULT_LANGUAGE


class SignupApp(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.root = master
        self.root.configure(background=colors.get("white"))
        self.configure(background=colors.get("white"))

        self.first_name_label = ttk.Label(
            self,
            text="First Name:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.first_name_entry = ttk.Entry(
            self, font=font, background=colors.get("white"), width=40
        )

        self.last_name_label = ttk.Label(
            self,
            text="Last Name:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.last_name_entry = ttk.Entry(
            self, font=font, background=colors.get("white"), width=40
        )

        self.uname_label = ttk.Label(
            self,
            text="Username:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.uname_entry = ttk.Entry(
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

        self.confirm_password_label = ttk.Label(
            self,
            text="Confirm Password:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.confirm_password_entry = ttk.Entry(
            self, show="*", font=font, background=colors.get("white"), width=40
        )

        self.language_label = ttk.Label(
            self,
            text="Preferred Language:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.translation_language = tk.StringVar()

        self.translation_language.set(DEFAULT_LANGUAGE)

        self.language_combobox = ttk.Combobox(
            self,
            values=sorted(LANGUAGE_OPTIONS.keys()),
            textvariable=self.translation_language,
            state="readonly",
            font=font,
            width=40,
        )

        # Create a button to sign up
        self.signup_button = ttk.Button(
            self, text="Sign Up", command=self.signup, style="Default.TButton"
        )

        # Have an account prompt and sign in button
        self.have_account_label = ttk.Label(
            self,
            text="Have an account?",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        self.login_button = ttk.Button(
            self,
            text="Log In",
            command=self.open_login_page,
            style="Default.TButton",
        )

        self.first_name_label.pack(anchor="w", padx=x_pad, pady=y_pad)
        self.first_name_entry.pack(padx=x_pad, pady=y_pad)
        self.last_name_label.pack(anchor="w", padx=x_pad, pady=y_pad)
        self.last_name_entry.pack(padx=x_pad, pady=y_pad)
        self.uname_label.pack(anchor="w", padx=x_pad, pady=y_pad)
        self.uname_entry.pack(padx=x_pad, pady=y_pad)
        self.password_label.pack(anchor="w", padx=x_pad, pady=y_pad)
        self.password_entry.pack(padx=x_pad, pady=y_pad)
        self.confirm_password_label.pack(anchor="w", padx=x_pad, pady=y_pad)
        self.confirm_password_entry.pack(padx=x_pad, pady=y_pad)
        self.language_label.pack(anchor="w", padx=x_pad, pady=y_pad)
        self.language_combobox.pack(padx=x_pad, pady=y_pad)
        self.signup_button.pack(padx=x_pad, pady=y_pad)
        self.have_account_label.pack(padx=x_pad, pady=y_pad)
        self.login_button.pack(padx=x_pad, pady=y_pad)

    def signup(self):
        try:
            fname = self.first_name_entry.get()
            lname = self.last_name_entry.get()
            uname = self.uname_entry.get().lower()
            password = self.password_entry.get()
            lang = self.translation_language.get()

            if DB.getuser(uname):
                raise Exception("Username Already exists")

            if not (fname and lname and uname and password):
                raise Exception("Required fields not filled")

            if password != self.confirm_password_entry.get():
                raise Exception("Passwords do not match")

            pword_bytes = password.encode("utf-8")
            hashed_pword = bcrypt.hashpw(pword_bytes, bcrypt.gensalt())
            DB.saveuser(fname, lname, uname, hashed_pword, lang)

        except Exception as e:
            messagebox.showerror("Error when Signing Up", str(e))
        else:
            messagebox.showinfo("Sign Up", "Account created successfully!")
            self.open_login_page()

    def open_login_page(self):
        self.root.show_login()
