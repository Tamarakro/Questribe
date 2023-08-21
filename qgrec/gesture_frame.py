import os
import tkinter as tk
from tkinter import ttk  # Import ttk for ComboBox
import tkinter.simpledialog
from tkinter import messagebox
from tkinter import PhotoImage
from PIL import Image, ImageTk
import cv2
import numpy as np
import mediapipe as mp
from keras.models import load_model
from gtts import gTTS
from io import BytesIO
import pygame
from translate import Translator
from threading import Thread
import time
import sqlite3
import bcrypt
import json
from uuid import uuid4
from .constants import (
    colors,
    font,
    x_pad,
    y_pad,
    LANGUAGE_OPTIONS,
    RESOURCES_DIR,
    DEFAULT_LANGUAGE,
)


class GestureRecognitionApp(tk.Frame):
    def __init__(self, master=None, userid=None, uname=None, lang=DEFAULT_LANGUAGE):
        super().__init__(master)
        pygame.mixer.init()
        pygame.mixer.music.set_volume(0.5)

        # Parent Window Properties
        self.root = master
        self.configure(background=colors.get("white"))

        # Initialize Variables
        self.uname = uname
        self.userid = userid
        self.language = lang
        self.className = ""
        self.classNameUpdated = False
        self.playThread = None

        self.is_running = False

        self.is_showing_popup = False
        self.recognized_gesture_history = []
        self.translated_gesture_history = []

        # Initialize tkinter variables
        self.translated_gesture = tk.StringVar()
        self.recognized_gesture = tk.StringVar()
        self.volume = tk.DoubleVar(value=50)

        # Set Default to User's preferred language
        self.translation_language = tk.StringVar(value=self.language)

        # Dictionary to store custom labels for recognized gestures
        self.custom_labels_file = f"{RESOURCES_DIR}/{userid}_custom_labels.json"
        self.custom_labels = {}
        self.load_custom_labels()

        self.load_classnames()

        # Load class names

        # Load the gesture recognizer model
        self.model = load_model(f"{RESOURCES_DIR}/mp_hand_gesture")

        # Initialize mediapipe
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(max_num_hands=1, min_detection_confidence=0.7)
        self.mpDraw = mp.solutions.drawing_utils

        # Initialize the webcam
        self.cap = None

        # Configure ttk  Styling
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Configure Default Background
        self.style.configure("TFrame", background=colors.get("white"))
        self.style.configure(
            "TScale",
            background=colors.get("white"),
            sliderlength=15,
            sliderthickness=60,
            border=0,
            borderwidth=0,
            relief="flat",
        )

        # Configure Custom Button Styles
        self.style.configure(
            "Start.TButton",
            background=colors.get("green"),
            font=font,
            borderwidth=0,
            relief="flat",
        )
        self.style.configure(
            "Stop.TButton",
            background=colors.get("red"),
            font=font,
            border=0,
            borderwidth=0,
            relief="flat",
        )

        # Create a Frames to hold the different UI elements the same background color
        top_left_frame = ttk.Frame(self, style="TFrame")
        top_right_frame = ttk.Frame(self, style="TFrame")
        bottom_left_frame = ttk.Frame(self, style="TFrame")
        bottom_right_frame = ttk.Frame(self, style="TFrame")
        middle_centered_frame = ttk.Frame(self, style="TFrame")

        # Create start and stop buttons and add them to the bottom right frame
        start_button = ttk.Button(
            bottom_right_frame,
            text="Start Recognition",
            command=self.start_gesture_recognition,
            style="Start.TButton",
        )
        stop_button = ttk.Button(
            bottom_right_frame,
            text="Stop Recognition",
            command=self.stop_gesture_recognition,
            style="Stop.TButton",
        )

        start_button.pack(pady=10, padx=10, fill=tk.X, side="left")
        stop_button.pack(pady=10, padx=10, fill=tk.X, side="left")

        # Create "show history" and "set custom label" buttons and add them to the bottom left frame
        show_history_button = ttk.Button(
            bottom_left_frame,
            text="Show Gesture History",
            command=self.show_gesture_history,
            style="Default.TButton",
        )

        set_custom_label_button = ttk.Button(
            bottom_left_frame,
            text="Set Custom Label",
            command=self.set_custom_label,
            style="Default.TButton",
        )

        show_history_button.pack(pady=10, padx=10, fill=tk.X, side="left")
        set_custom_label_button.pack(pady=10, padx=10, fill=tk.X, side="left")

        # Create a Canvas to display the webcam feed
        self.canvas = tk.Canvas(
            middle_centered_frame, width=1280, height=720, bg=colors.get("dark-gray")
        )
        self.canvas.pack()

        volume_frame = ttk.Frame(self, style="TFrame")

        # Create a volume control slider
        volume_label = ttk.Label(
            volume_frame,
            text="Volume Control:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        volume_label.pack(side="left")

        self.volume_slider = ttk.Scale(
            volume_frame,
            variable=self.volume,
            from_=0,
            to=100,
            orient=tk.HORIZONTAL,
            style="TScale",
            command=self.adjust_volume,
        )

        self.volume_slider.pack(side="left")

        # Create frames to hold entry fields and their labels
        language_frame = ttk.Frame(top_left_frame, style="TFrame")
        recognized_gesture_frame = ttk.Frame(top_left_frame, style="TFrame")
        translated_gesture_frame = ttk.Frame(top_left_frame, style="TFrame")

        language_label = ttk.Label(
            language_frame,
            text="Select Language:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        # List containing accepted languages
        language_combobox = ttk.Combobox(
            language_frame,
            textvariable=self.translation_language,
            values=sorted(LANGUAGE_OPTIONS.keys()),
            state="readonly",
            font=font,
        )

        language_label.pack(anchor="w")
        language_combobox.pack(padx=x_pad, pady=y_pad)
        language_frame.pack(side="left", padx=30, expand=True)

        # Create field label followed by entry field
        recognized_gesture_label = ttk.Label(
            recognized_gesture_frame,
            text="Recognized Gesture:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        # Create an Entry widget to display the recognized gesture
        self.recognized_entry = ttk.Entry(
            recognized_gesture_frame,
            textvariable=self.recognized_gesture,
            font=font,
            state="readonly",
            background=colors.get("white"),
        )

        translated_gesture_label = ttk.Label(
            translated_gesture_frame,
            text="Translated Gesture:",
            foreground=colors.get("black"),
            background=colors.get("white"),
            font=font,
        )

        # Create an Entry widget to display the translated gesture
        self.translated_entry = ttk.Entry(
            translated_gesture_frame,
            textvariable=self.translated_gesture,
            font=font,
            state="readonly",
            background=colors.get("white"),
        )

        self.log_out_button = ttk.Button(
            top_left_frame,
            text="Home",
            command=self.log_out,
            style="Default.TButton",
        )

        self.log_out_button.pack(side="right", padx=80, pady=(15, 5), expand=True)

        translated_gesture_label.pack(anchor="w")
        self.translated_entry.pack(padx=x_pad, pady=y_pad, expand=True)
        translated_gesture_frame.pack(side="right", padx=30)

        recognized_gesture_label.pack(anchor="w")
        self.recognized_entry.pack(padx=x_pad, pady=y_pad, expand=True)
        recognized_gesture_frame.pack(side="right", padx=30)

        # Pack Frames in desired order
        top_left_frame.pack(anchor="center", padx=x_pad, pady=y_pad, expand=True)
        middle_centered_frame.pack(anchor="center", padx=x_pad, pady=y_pad)

        bottom_left_frame.pack(side="left", padx=x_pad, pady=y_pad)
        volume_frame.pack(side="left", padx=100, pady=y_pad, expand=True)
        bottom_right_frame.pack(side="right", padx=x_pad, pady=y_pad)

    def play_audio(self, text, lang):
        translated_text = text

        if lang != DEFAULT_LANGUAGE:
            self.translated_gesture.set("Translating...")
            translator = Translator(from_lang="en", to_lang=lang)
            translated_text = translator.translate(text)
            translated_text = translated_text[:1].upper() + translated_text[1:].lower()

        self.translated_gesture.set(translated_text)

        self.update_gesture_history(text, translated_text)

        tts = gTTS(
            text=translated_text, lang=LANGUAGE_OPTIONS.get(lang, "en"), slow=False
        )

        fp_io = BytesIO()
        tts.write_to_fp(fp_io)
        fp_io.seek(0)

        pygame.mixer.music.load(fp_io)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue

    def run_gesture_recognition(self):
        _, frame = self.cap.read()

        start = time.time()

        x, y, c = frame.shape

        frame = cv2.flip(frame, 1)

        framergb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        result = self.hands.process(framergb)

        if result.multi_hand_landmarks:
            landmarks = []

            for handslms in result.multi_hand_landmarks:
                for lm in handslms.landmark:
                    lmx = int(lm.x * x)
                    lmy = int(lm.y * y)
                    landmarks.append([lmx, lmy])

            self.mpDraw.draw_landmarks(
                framergb, handslms, self.mpHands.HAND_CONNECTIONS
            )

            prediction = self.model.predict([landmarks], batch_size=5000)

            classID = np.argmax(prediction)

            self.classNameUpdated = self.className != self.classNames[classID]

            if self.playThread is None or not self.playThread.is_alive():
                self.className = self.classNames[classID]

            # Update the recognized gesture in the Entry widget

            self.recognized_gesture.set(self.className)

            # Check if a custom label exists for the recognized gesture

            if self.className in self.custom_labels:
                recognized_text = self.custom_labels[self.className]

                self.translated_gesture.set(recognized_text)

            else:
                recognized_text = self.className

            # Display the recognized gesture in the Entry widget

            self.recognized_gesture.set(recognized_text)

            # Translate recognized gesture to the selected language

            translation_language = self.translation_language.get()

            # Display the translated gesture in the Entry widget

            # Play the audio of the translated gesture

            if (
                self.classNameUpdated
                and recognized_text
                and (self.playThread is None or not self.playThread.is_alive())
            ):
                self.playThread = Thread(
                    target=self.play_audio, args=(recognized_text, translation_language)
                )

                self.playThread.start()

        # Update the gesture history display

        cv2.putText(
            framergb,
            f"{1/(time.time() - start):.2F} FPS",
            (10, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2,
            cv2.LINE_AA,
        )

        # Convert the frame to a format compatible with tkinter
        image = Image.fromarray(framergb)

        photo = ImageTk.PhotoImage(image=image)

        # Update the Canvas with the new frame

        self.canvas.create_image(0, 0, anchor=tk.NW, image=photo)

        self.canvas.image = photo

        if self.is_running:
            # Call this function again after 10 milliseconds to update the frame

            self.after(25, self.run_gesture_recognition)
        else:
            self.canvas.delete("all")
            self.cap = None

    def set_custom_label(self):
        recognized_gesture = self.className

        if not recognized_gesture:
            return

        if self.is_showing_popup:
            messagebox.showinfo("Info", "A Popup Window Is Currently Open!")
            return

        self.is_showing_popup = True

        set_label_popup = tk.Toplevel(bg=colors.get("white"))
        set_label_popup.wm_title(f"Set Custom Label For {recognized_gesture}")

        label_input_frame = tk.Frame(set_label_popup)

        label_title = ttk.Label(
            set_label_popup,
            text=f"Set Custom Label For {recognized_gesture}:",
            font=font,
            foreground=colors.get("black"),
            background=colors.get("white"),
        )

        label_input = ttk.Entry(
            set_label_popup,
            font=font,
            background=colors.get("white"),
        )

        def close_label_popup():
            self.is_showing_popup = False
            custom_label = label_input.get()
            if custom_label:
                self.custom_labels[recognized_gesture] = custom_label
                self.recognized_gesture.set(custom_label)
                self.translated_gesture.set(custom_label)
                self.update_gesture_history(custom_label, custom_label)
                self.save_custom_labels()
            set_label_popup.destroy()

        ok_button = ttk.Button(
            set_label_popup,
            text="Save",
            command=close_label_popup,
            style="Default.TButton",
        )

        label_title.pack(anchor="w")
        label_input.pack(padx=x_pad, pady=y_pad)
        ok_button.pack(padx=x_pad, pady=y_pad)
        set_label_popup.protocol("WM_DELETE_WINDOW", close_label_popup)

    def start_gesture_recognition(self):
        # Set the is_running variable to True and start updating the Canvas with webcam feed
        if self.is_running:
            return
        self.is_running = True
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
        self.run_gesture_recognition()

    def stop_gesture_recognition(self):
        # Set the is_running variable to False to stop updating the Canvas
        self.is_running = False

    def update_gesture_history(self, recognized_gesture, translated_gesture):
        # Add the recognized gesture and its translation to the Listbox
        self.recognized_gesture_history.append(recognized_gesture)
        self.translated_gesture_history.append(translated_gesture)

    def show_gesture_history(self):
        if self.is_showing_popup:
            messagebox.showinfo("Info", "A Popup Window Is Currently Open!")
            return

        self.is_showing_popup = True

        gesture_popup = tk.Toplevel()
        gesture_popup.wm_title("Gesture History")

        gesture_history_frame = tk.Frame(gesture_popup)

        recognized_gesture_frame = tk.Frame(gesture_history_frame)
        recognized_list_label = ttk.Label(
            recognized_gesture_frame, text="Recognized Gestures:", font=font
        )
        recognized_gesture_listbox = tk.Listbox(
            recognized_gesture_frame, width=20, height=10, font=font
        )

        recognized_list_label.pack(anchor="w")
        recognized_gesture_listbox.pack()

        translated_gesture_frame = tk.Frame(gesture_history_frame)
        translated_list_label = ttk.Label(
            translated_gesture_frame, text="Translated Gestures:", font=font
        )
        translated_gesture_listbox = tk.Listbox(
            translated_gesture_frame, width=20, height=10, font=font
        )

        translated_list_label.pack(anchor="w")
        translated_gesture_listbox.pack()

        for gesture in self.recognized_gesture_history[::-1]:
            recognized_gesture_listbox.insert(tk.END, gesture)

        for gesture in self.translated_gesture_history[::-1]:
            translated_gesture_listbox.insert(tk.END, gesture)

        recognized_gesture_frame.pack(side="left", padx=x_pad, pady=y_pad)
        translated_gesture_frame.pack(side="left", padx=x_pad, pady=y_pad)

        gesture_history_frame.pack()

        def close_gesture_popup():
            self.is_showing_popup = False
            gesture_popup.destroy()

        ok_button = ttk.Button(
            gesture_popup,
            text="Okay",
            command=close_gesture_popup,
            style="Default.TButton",
        )
        ok_button.pack(padx=x_pad, pady=y_pad)
        gesture_popup.protocol("WM_DELETE_WINDOW", close_gesture_popup)

    def adjust_volume(self, value):
        # The 'value' parameter will be the current value of the volume slider (between 0 and 1)

        volume = float(value) / 100  # Convert the value to a float
        pygame.mixer.music.set_volume(volume)  # Set the volume of audio playback

    def load_custom_labels(self):
        self.custom_labels = {}
        if self.userid and os.path.exists(self.custom_labels_file):
            with open(self.custom_labels_file, "r") as f:
                self.custom_labels = json.load(f)

    def save_custom_labels(self):
        if self.userid:
            with open(self.custom_labels_file, "w") as f:
                json.dump(self.custom_labels, f, ensure_ascii=False, indent=4)

    def load_classnames(self):
        classnames_file = f"{RESOURCES_DIR}/gesture.names"
        if os.path.exists(classnames_file):
            with open(classnames_file, "r") as f:
                self.classNames = [
                    classname[:1].upper() + classname[1:].lower()
                    for classname in f.read().split("\n")
                ]

    def set_user_details(self, userid=None, uname=None, lang=DEFAULT_LANGUAGE):
        self.uname = uname
        self.userid = userid
        self.language = lang
        self.custom_labels_file = f"{RESOURCES_DIR}/{userid}_custom_labels.json"
        self.load_custom_labels()
        self.translation_language.set(lang)
        if userid:
            self.log_out_button.config(text="Log out")

    def log_out(self):
        self.userid = None
        self.uname = None
        self.language = DEFAULT_LANGUAGE
        self.log_out_button.config(text="Home")
        self.custom_labels_file = None
        self.custom_labels = {}
        self.translated_gesture.set("")
        self.recognized_gesture.set("")
        self.recognized_gesture_history = []
        self.translated_gesture_history = []
        self.className = ""
        self.exit()
        time.sleep(0.05)
        self.root.show_home()

    def exit(self):
        self.stop_gesture_recognition()
        time.sleep(0.05)
