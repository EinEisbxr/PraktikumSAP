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
import numpy as np
from PIL import Image, ImageTk


global tkapp


class HandTracking():
    def __init__(self) -> None:
        self.cap = cv2.VideoCapture(1)
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Initializing the Model 
        self.mpHands = mp.solutions.hands 
        self.hands = self.mpHands.Hands( 
            static_image_mode=False, 
            model_complexity=1,
            min_detection_confidence=0.75, 
            min_tracking_confidence=0.75, 
            max_num_hands=2) 
        
    def process_video(self):
        #frame=np.random.randint(0,255,[1000,1000,3],dtype='uint8')
        #load frames from file
        #frame = cv2.imread("test3.jpeg")
        #frame = cv2.resize(frame, (600, 600))
        #ret = True
        ret, frame = self.cap.read()

        if ret:
            #frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frameRGB = frame

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
                        label = MessageToDict(i)['classification'][0]['label'] 
                        
                        if label == 'Left':
                            label = 'Right'
                        elif label == 'Right':
                            label = 'Left'

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
                            
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mpHands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()) 
        
                        
            return frame

        else:
            print("Error while reading frame")    
            



class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, tkapp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x400")
        self.title("Settings")
        tkapp.detection_confidence = tk.StringVar(value="0.75") 
        tkapp.tracking_confidence = tk.StringVar(value="0.75")
        tkapp.max_num_hands = tk.StringVar(value="2")
        tkapp.model_complexity = tk.StringVar(value="1")
        
        #self.configure(fg_color="#0e1718")
        #self.tk_setPalette(background='#ffffff', foreground='#0e1718',
        #       activeBackground='#ffffff', activeForeground='#0e1718')
        self.tkapp = tkapp
        self.create_widgets()
        
        
        
    def create_widgets(self):
        Label_detection_confidence = ctk.CTkLabel(self, text="Detection Confidence")
        Label_detection_confidence.pack(side=tk.TOP)
        Entry_detection_confidence = ctk.CTkEntry(self, textvariable=self.tkapp.detection_confidence)
        Entry_detection_confidence.pack(side=tk.TOP)

        Label_tracking_confidence = ctk.CTkLabel(self, text="Tracking Confidence")
        Label_tracking_confidence.pack(side=tk.TOP)
        Entry_tracking_confidence = ctk.CTkEntry(self, textvariable=self.tkapp.tracking_confidence)
        Entry_tracking_confidence.pack(side=tk.TOP)
        
        Label_max_num_hands = ctk.CTkLabel(self, text="Max Number of Hands")
        Label_max_num_hands.pack(side=tk.TOP)
        Entry_max_num_hands = ctk.CTkEntry(self, textvariable=self.tkapp.max_num_hands)
        Entry_max_num_hands.pack(side=tk.TOP)
        
        Label_model_complexity = ctk.CTkLabel(self, text="Model Complexity")
        Label_model_complexity.pack(side=tk.TOP)
        Entry_model_complexity = ctk.CTkEntry(self, textvariable=self.tkapp.model_complexity)
        Entry_model_complexity.pack(side=tk.TOP)
        
        self.bind("<Return>", lambda event: self.apply_settings())
        
        Button_apply = ctk.CTkButton(self, text="Apply", command=self.apply_settings)
        Button_apply.pack(side=tk.TOP)
        
    def apply_settings(self):
        self.tkapp.HandTracker.hands = self.tkapp.HandTracker.mpHands.Hands( 
            static_image_mode=False, 
            model_complexity=int(self.tkapp.model_complexity.get()),
            min_detection_confidence=float(self.tkapp.detection_confidence.get()), 
            min_tracking_confidence=float(self.tkapp.tracking_confidence.get()),
            max_num_hands=int(self.tkapp.max_num_hands.get()))

class Window(ctk.CTk):  
    def __init__(self):
        super().__init__()
        self.settings_window = None

        self.screenheight = self.winfo_screenheight()
        self.screenwidth = self.winfo_screenwidth()

        self.toplevel_window = None
        
        # Set window title
        self.title("Hand Tracking App")
        self.after(0, lambda:self.state('zoomed'))
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
            self.toplevel_window.lift()
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
        self.HandTracker = HandTracking()
        
        while True:
            #StartT = time.time()
            #time.sleep(0.03)
            frame = self.HandTracker.process_video()

            #Update the image to tkinter...
            img_update = ImageTk.PhotoImage(Image.fromarray(frame))
            image_label.configure(image=img_update)
            image_label.image=img_update
            image_label.update()
            #self.fps = 1/(time.time()-StartT)

        
tkapp = Window()



if __name__ == "__main__":
    tkapp.mainloop()