import os
from pathlib import Path

class Config:
    # Google Gemini API Key
    GOOGLE_API_KEY = ""  # Replace with your actual Gemini API key
    
    # Paths
    BASE_DIR = Path(__file__).parent
    RESOURCES_DIR = BASE_DIR / "resources"
    SAVES_DIR = BASE_DIR / "saves"
    
    # Speech Recognition Settings
    SPEECH_ENGINE = "sphinx"
    LANGUAGE = "en-US"
    AUDIO_TIMEOUT = 5
    
    # Camera settings
    CAMERA_WIDTH = 1280
    CAMERA_HEIGHT = 720
    FPS = 30
    
    # OCR Settings
    TESSERACT_PATH = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    
    # Text to Speech Settings
    TTS_VOICE_RATE = 150
    TTS_VOICE_VOLUME = 1.0
    
    # Gesture Detection Settings
    GESTURE_CONFIDENCE = 0.7
    MAX_NUM_HANDS = 2
    
    @classmethod
    def initialize(cls):
        # Create necessary directories
        for directory in [cls.RESOURCES_DIR, cls.SAVES_DIR]:
            directory.mkdir(exist_ok=True)
            
        # Validate settings
        cls.validate_settings()
    
    @classmethod
    def validate_settings(cls):
        # Check Google API key
        if not cls.GOOGLE_API_KEY or cls.GOOGLE_API_KEY == "your-google-api-key-here":
            print("Warning: Google Gemini API key not set. Please add your API key.")
        
        # Check Tesseract installation
        if not os.path.exists(cls.TESSERACT_PATH):
            print(f"Warning: Tesseract not found at {cls.TESSERACT_PATH}")
            print("Please install Tesseract OCR or update the path.")
            
        # Check if required directories exist
        if not cls.RESOURCES_DIR.exists():
            print(f"Creating resources directory at {cls.RESOURCES_DIR}")
        if not cls.SAVES_DIR.exists():
            print(f"Creating saves directory at {cls.SAVES_DIR}")

    @classmethod
    def get_speech_recognizer(cls):
        """Returns appropriate speech recognition engine based on settings"""
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        
        if cls.SPEECH_ENGINE == 'sphinx':
            recognizer.recognize = recognizer.recognize_sphinx
        elif cls.SPEECH_ENGINE == 'whisper':
            recognizer.recognize = recognizer.recognize_whisper
        elif cls.SPEECH_ENGINE == 'vosk':
            # Add Vosk configuration if needed
            pass
            
        return recognizer
    
    @classmethod
    def get_tts_engine(cls):
        """Returns text-to-speech engine with configured settings"""
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', cls.TTS_VOICE_RATE)
        engine.setProperty('volume', cls.TTS_VOICE_VOLUME)
        return engine 
