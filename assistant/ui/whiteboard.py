import tkinter as tk
from PIL import Image, ImageDraw
import numpy as np

class Whiteboard(tk.Canvas):
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)
        self.parent = parent
        self.setup()
        
    def setup(self):
        self.image = Image.new('RGB', (800, 600), 'white')
        self.draw = ImageDraw.Draw(self.image)
        self.last_x = None
        self.last_y = None
        self.line_width = 2
        self.line_color = 'black'
        
        self.bind('<Button-1>', self.start_draw)
        self.bind('<B1-Motion>', self.draw_line)
        self.bind('<ButtonRelease-1>', self.stop_draw)
        
    def start_draw(self, event):
        self.last_x = event.x
        self.last_y = event.y
        
    def draw_line(self, event):
        if self.last_x and self.last_y:
            self.create_line(
                self.last_x, self.last_y, event.x, event.y,
                width=self.line_width, fill=self.line_color,
                capstyle=tk.ROUND, smooth=True
            )
            self.draw.line(
                [self.last_x, self.last_y, event.x, event.y],
                fill=self.line_color, width=self.line_width
            )
        self.last_x = event.x
        self.last_y = event.y
        
    def clear(self):
        self.delete("all")
        self.image = Image.new('RGB', (800, 600), 'white')
        self.draw = ImageDraw.Draw(self.image) 