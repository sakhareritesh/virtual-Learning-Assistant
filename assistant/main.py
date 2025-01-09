import tkinter as tk
import customtkinter as ctk
from utils.gesture_detector import GestureDetector
from utils.ocr_handler import OCRHandler
from utils.screen_recorder import ScreenRecorder
from config import Config
import cv2
from PIL import Image
import speech_recognition as sr
import threading
import pyttsx3
import google.generativeai as genai
import time
from queue import Queue
import numpy as np

class EnhancedVisualAssistant:
    def __init__(self):
        Config.initialize()
        self.setup_window()
        
        # Initialize components
        self.gesture_detector = GestureDetector()
        self.ocr_handler = OCRHandler()
        self.screen_recorder = ScreenRecorder()
        
        # Initialize speech recognition
        self.recognizer = sr.Recognizer()
        
        # Initialize text-to-speech
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 150)  # Slower speaking rate
        
        # Initialize Gemini
        genai.configure(api_key=Config.GOOGLE_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Start camera
        self.cap = cv2.VideoCapture(0)
        self.update_camera()
        
        self.is_listening = False
        self.is_speaking = False
        self.question_queue = Queue()
        self.current_mic = None
        
    def setup_window(self):
        # Set theme and colors
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("AI Vision Assistant")
        self.root.geometry("1400x800")
        self.root.configure(fg_color="#1a1a1a")
        
        # Create main container with grid
        self.root.grid_columnconfigure(0, weight=3)  # Left panel takes 3/4
        self.root.grid_columnconfigure(1, weight=1)  # Right panel takes 1/4
        self.root.grid_rowconfigure(0, weight=1)
        
        # Create left panel
        self.left_panel = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.left_panel.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        # Title label
        self.title_label = ctk.CTkLabel(
            self.left_panel,
            text="AI Vision Assistant",
            font=("Roboto", 24, "bold"),
            text_color="#ffffff"
        )
        self.title_label.pack(pady=10)
        
        # Camera frame
        self.camera_frame = ctk.CTkFrame(
            self.left_panel,
            fg_color="#1a1a1a",
            corner_radius=15,
            border_width=2,
            border_color="#3b3b3b"
        )
        self.camera_frame.pack(padx=20, pady=10, fill="both", expand=True)
        
        self.camera_label = ctk.CTkLabel(self.camera_frame, text="")
        self.camera_label.pack(padx=10, pady=10)
        
        # Create right panel
        self.right_panel = ctk.CTkFrame(self.root, fg_color="#2b2b2b", corner_radius=15)
        self.right_panel.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Control buttons frame
        self.button_frame = ctk.CTkFrame(self.right_panel, fg_color="transparent")
        self.button_frame.pack(fill="x", padx=20, pady=20)
        
        # Listen button with modern styling
        self.listen_button = ctk.CTkButton(
            self.button_frame,
            text="Start Listening",
            command=self.toggle_listening,
            font=("Roboto", 16),
            height=50,
            corner_radius=25,
            fg_color="#007AFF",
            hover_color="#0056b3"
        )
        self.listen_button.pack(fill="x", padx=10)
        
        # Status indicator
        self.status_indicator = ctk.CTkLabel(
            self.button_frame,
            text="●",
            font=("Roboto", 24),
            text_color="#ff3b30"
        )
        self.status_indicator.pack(pady=5)
        
        # Text display
        self.text_display = ctk.CTkTextbox(
            self.right_panel,
            font=("Roboto", 14),
            fg_color="#1a1a1a",
            text_color="#ffffff",
            corner_radius=10,
            border_width=1,
            border_color="#3b3b3b"
        )
        self.text_display.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # Welcome message
        welcome_msg = "Welcome to AI Vision Assistant! 🤖\n\n"
        welcome_msg += "Click 'Start Listening' to begin.\n"
        welcome_msg += "I'm here to help you with anything you need!\n\n"
        self.text_display.insert("1.0", welcome_msg)
        
    def update_status(self, is_active):
        color = "#30d158" if is_active else "#ff3b30"
        self.status_indicator.configure(text_color=color)
        
    def update_camera(self):
        ret, frame = self.cap.read()
        if ret:
            frame, gesture = self.gesture_detector.detect_gestures(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame = cv2.flip(frame, 1)
            
            # Add rounded corners effect
            height, width = frame.shape[:2]
            mask = np.zeros(frame.shape[:2], dtype="uint8")
            cv2.rectangle(mask, (0, 0), (width, height), 255, -1)
            frame = cv2.bitwise_and(frame, frame, mask=mask)
            
            img = Image.fromarray(frame)
            ctk_image = ctk.CTkImage(light_image=img, dark_image=img, size=(800, 600))
            self.camera_label.configure(image=ctk_image)
            self.camera_label.image = ctk_image
            
        self.root.after(10, self.update_camera)
        
    def get_ai_response(self, text):
        try:
            response = self.model.generate_content(text)
            return response.text
        except Exception as e:
            return f"Error getting response: {str(e)}"
            
    def speak_response(self, text):
        self.is_speaking = True
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.text_display.insert("end", f"Speech Error: {str(e)}\n")
        finally:
            self.is_speaking = False
            
    def listen_for_speech(self):
        try:
            with sr.Microphone() as source:
                self.text_display.insert("end", "\n🎤 Listening...\n")
                self.text_display.see("end")
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=5)
                return audio
        except Exception as e:
            self.text_display.insert("end", f"🚫 Microphone Error: {str(e)}\n")
            return None
            
    def process_speech(self):
        while self.is_listening:
            try:
                audio = self.listen_for_speech()
                if audio:
                    text = self.recognizer.recognize_google(audio)
                    self.text_display.insert("end", f"\n👤 You: {text}\n")
                    self.text_display.see("end")
                    
                    response = self.get_ai_response(text)
                    self.text_display.insert("end", f"\n🤖 Assistant: {response}\n")
                    self.text_display.see("end")
                    
                    threading.Thread(target=self.speak_response, args=(response,), daemon=True).start()
                    time.sleep(0.5)
                    
            except sr.UnknownValueError:
                self.text_display.insert("end", "Sorry, I didn't catch that.\n")
            except sr.RequestError as e:
                self.text_display.insert("end", f"Error: {str(e)}\n")
            except Exception as e:
                self.text_display.insert("end", f"Error: {str(e)}\n")
                time.sleep(1)
                
    def toggle_listening(self):
        if not self.is_listening:
            self.is_listening = True
            self.listen_button.configure(
                text="Stop Listening",
                fg_color="#ff3b30",
                hover_color="#d63030"
            )
            self.update_status(True)
            self.text_display.insert("end", "Started listening...\n")
            threading.Thread(target=self.process_speech, daemon=True).start()
        else:
            self.is_listening = False
            self.listen_button.configure(
                text="Start Listening",
                fg_color="#007AFF",
                hover_color="#0056b3"
            )
            self.update_status(False)
            self.text_display.insert("end", "Stopped listening\n")
        
    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = EnhancedVisualAssistant()
    app.run() 