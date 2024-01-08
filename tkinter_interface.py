import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import threading
import requests
import os
import time
import numpy as np
from PIL import Image, ImageTk
import cv2

global tkapp


class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x400")
        self.title("Settings")
        tkapp.detection_confidence = tk.StringVar(value="0.5") 
        tkapp.tracking_confidence = tk.StringVar(value="0.5")
        #self.configure(fg_color="#0e1718")
        #self.tk_setPalette(background='#ffffff', foreground='#0e1718',
        #       activeBackground='#ffffff', activeForeground='#0e1718')
        self.create_widgets()
        
        
    def create_widgets(self):
        Label_detection_confidence = ctk.CTkLabel(self, text="Detection Confidence")
        Label_detection_confidence.pack(side=tk.TOP)
        Entry_detection_confidence = ctk.CTkEntry(self, textvariable=tkapp.detection_confidence)
        Entry_detection_confidence.pack(side=tk.TOP)

        Label_tracking_confidence = ctk.CTkLabel(self, text="Tracking Confidence")
        Label_tracking_confidence.pack(side=tk.TOP)
        Entry_tracking_confidence = ctk.CTkEntry(self, textvariable=tkapp.tracking_confidence)
        Entry_tracking_confidence.pack(side=tk.TOP)

class Window(ctk.CTk):
          
    def __init__(self):
        super().__init__()
        self.settings_window = None

        self.screenheight = self.winfo_screenheight()
        self.screenwidth = self.winfo_screenwidth()

        self.toplevel_window = None
        
        # Set window title
        self.title("Hand Tracking App")
        self.after(0, lambda:self.state('normal'))
        self.configure(fg_color="#0e1718", bg_color="#3D3D3D")
        self.geometry(f"{self.screenwidth}x{self.screenheight}")
        
        self.tk_setPalette(background='#3D3D3D', foreground='#ffffff',
               activeBackground='#3D3D3D', activeForeground='#ffffff')
        
        self.create_navigation_bar()
        self.fake_video()   
        
    # create settings window when settings button was pressed 
    def create_settings_window(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed
        else:
            self.toplevel_window.focus()  # if window exists focus it

            
    def create_navigation_bar(self):
        menu = tk.Menu(self)
        
        file_menu = tk.Menu()
        menu.add_cascade(label="File", menu=file_menu, foreground="#ffffff", background="#3D3D3D")
        file_menu.add_command(label="Settings", command=self.create_settings_window, foreground="#ffffff", background="#3D3D3D")
        file_menu.add_command(label="Exit", command=self.destroy, foreground="#ffffff", background="#3D3D3D")
       
        
        self.configure(menu=menu)
        
    def fake_video(self):
        
        image_label = ctk.CTkLabel(self, text="", width=1000, height=1000, bg_color="#ffffff")
        image_label.pack(side=tk.TOP)
        
        while True:
            time.sleep(1)
            frame=np.random.randint(0,255,[1000,1000,3],dtype='uint8')

            #Update the image to tkinter...
            frame=cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
            img_update = ImageTk.PhotoImage(Image.fromarray(frame))
            image_label.configure(image=img_update)
            image_label.image=img_update
            image_label.update()

        
tkapp = Window()



if __name__ == "__main__":
    tkapp.mainloop()