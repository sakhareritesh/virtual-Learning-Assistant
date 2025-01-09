import cv2
import numpy as np
from datetime import datetime
import threading
from PIL import ImageGrab

class ScreenRecorder:
    def __init__(self):
        self.recording = False
        self.output = None
        
    def start_recording(self):
        self.recording = True
        filename = f"screen_recording_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi"
        screen = ImageGrab.grab()
        width, height = screen.size
        
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        self.output = cv2.VideoWriter(filename, fourcc, 20.0, (width, height))
        
        threading.Thread(target=self._record, daemon=True).start()
        
    def stop_recording(self):
        self.recording = False
        if self.output:
            self.output.release()
            
    def _record(self):
        while self.recording:
            try:
                # Capture the screen
                screen = ImageGrab.grab()
                # Convert to numpy array
                frame = np.array(screen)
                # Convert from RGB to BGR
                frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
                # Write the frame
                self.output.write(frame)
            except Exception as e:
                print(f"Recording error: {str(e)}")
                break 