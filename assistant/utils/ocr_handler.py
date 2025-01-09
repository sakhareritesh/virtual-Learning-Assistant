import pytesseract
import cv2
import numpy as np
from PIL import Image
import re

class OCRHandler:
    def __init__(self):
        self.tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pytesseract.pytesseract.tesseract_cmd = self.tesseract_path
        
    def process_image(self, image):
        # Preprocess image
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Extract text
        text = pytesseract.image_to_string(thresh)
        return text
        
    def extract_math_problem(self, text):
        # Use regex to identify mathematical expressions
        math_pattern = r'[\d\s+\-*/()=]+|[\d\s+\-*/()=]+\?'
        matches = re.findall(math_pattern, text)
        return matches if matches else None 