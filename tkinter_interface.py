import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import threading
import requests
import os
import time
import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict

global tkapp


class HandTracking():
    def __init__(self) -> None:
        self.cap = cv2.VideoCapture(0)

        # Initializing the Model 
        mpHands = mp.solutions.hands 
        self.hands = mpHands.Hands( 
            static_image_mode=False, 
            model_complexity=1,
            min_detection_confidence=0.75, 
            min_tracking_confidence=0.75, 
            max_num_hands=2) 
        
    def process_video(self):
        ret, frame = self.cap.read()

        if ret:
            frame = cv2.flip(frame, 1)
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            results = self.hands.process(frameRGB)

            # If hands are present in image(frame) 
            if results.multi_hand_landmarks: 

                # Both Hands are present in image(frame) 
                if len(results.multi_handedness) == 2: 
                        # Display 'Both Hands' on the image 
                    cv2.putText(frame, 'Both Hands', (250, 50), 
                                cv2.FONT_HERSHEY_COMPLEX, 
                                0.9, (0, 255, 0), 2) 
                    
            # If any hand present 
            else:
                for i in results.multi_handedness: 
                    
                    # Return whether it is Right or Left Hand 
                    label = MessageToDict(i) 
                    ['classification'][0]['label'] 

                    if label == 'Left': 
                        
                        # Display 'Left Hand' on 
                        # left side of window 
                        cv2.putText(frame, label+' Hand', 
                                    (20, 50), 
                                    cv2.FONT_HERSHEY_COMPLEX, 
                                    0.9, (0, 255, 0), 2) 

                    if label == 'Right': 
                        
                        # Display 'Left Hand' 
                        # on left side of window 
                        cv2.putText(frame, label+' Hand', (460, 50), 
                                    cv2.FONT_HERSHEY_COMPLEX, 
                                    0.9, (0, 255, 0), 2) 
                        
            return frame

        else:
            print("Error while reading frame")    
            



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


tkapp = Window()



if __name__ == "__main__":
    tkapp.mainloop()