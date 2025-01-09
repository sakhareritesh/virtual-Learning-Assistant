import cv2
import numpy as np

class GestureDetector:
    def __init__(self):
        self.background_subtractor = cv2.createBackgroundSubtractorMOG2()
        self.kernel = np.ones((3,3), np.uint8)
        
    def detect_gestures(self, frame):
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply Gaussian blur
            blurred = cv2.GaussianBlur(gray, (5, 5), 0)
            
            # Apply background subtraction
            fg_mask = self.background_subtractor.apply(blurred)
            
            # Apply morphological operations
            fg_mask = cv2.erode(fg_mask, self.kernel, iterations=1)
            fg_mask = cv2.dilate(fg_mask, self.kernel, iterations=2)
            
            # Find contours
            contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Draw contours and detect movement
            gesture = None
            for contour in contours:
                if cv2.contourArea(contour) > 1000:  # Filter small contours
                    cv2.drawContours(frame, [contour], -1, (0, 255, 0), 2)
                    gesture = "Movement detected"
            
            return frame, gesture
            
        except Exception as e:
            print(f"Error in gesture detection: {str(e)}")
            return frame, None
        
    def _classify_gesture(self, contour):
        # Basic gesture classification based on contour properties
        area = cv2.contourArea(contour)
        perimeter = cv2.arcLength(contour, True)
        if perimeter > 0:
            circularity = 4 * np.pi * area / (perimeter * perimeter)
            if circularity > 0.7:
                return "circle"
            else:
                return "other"
        return None 