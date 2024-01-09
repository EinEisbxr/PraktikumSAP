import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import time
import cv2
import mediapipe as mp
from google.protobuf.json_format import MessageToDict
import numpy as np
from PIL import Image, ImageTk
import os
import sqlite3


global tkapp


class HandTracking():
    def __init__(self, tkapp) -> None:
        self.cap = cv2.VideoCapture(1)
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles

        # Initializing the Model 
        self.mpHands = mp.solutions.hands   
        self.hands = self.mpHands.Hands(    
            static_image_mode=False, 
            model_complexity=int(tkapp.model_complexity.get()),
            min_detection_confidence=float(tkapp.detection_confidence.get()),
            min_tracking_confidence=float(tkapp.tracking_confidence.get()),
            max_num_hands=int(tkapp.max_num_hands.get()))
        
        self.tkapp = tkapp
        
    def process_video(self):
        #frame=np.random.randint(0,255,[1000,1000,3],dtype='uint8')
        #load frames from file
        #frame = cv2.imread("test3.jpeg")
        #ret = True
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (1280, 720))
        
        #flip the frame
        frame = cv2.flip(frame, 1)

        if ret:
            #frame = cv2.flip(frame, 1)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frameRGB = frame

            cv2.putText(frame, f"FPS: {self.tkapp.fps:.2f}", (600, 360), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)


            results = self.hands.process(frameRGB)

            # If hands are present in image(frame) 
            if results.multi_hand_landmarks: 
                for i, hand_landmarks in enumerate(results.multi_hand_landmarks):
                    coordinates6 = (hand_landmarks.landmark[6].x, hand_landmarks.landmark[6].y)
                    coordinates7 = (hand_landmarks.landmark[7].x, hand_landmarks.landmark[7].y)
                    coordinates8 = (hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y)
                    #print(coordinates7, coordinates8)

                    # Calculate slopes
                    slope1 = (coordinates7[1] - coordinates6[1]) / (coordinates7[0] - coordinates6[0]) if coordinates7[0] != coordinates6[0] else float('inf')
                    slope2 = (coordinates8[1] - coordinates7[1]) / (coordinates8[0] - coordinates7[0]) if coordinates8[0] != coordinates7[0] else float('inf')

                    if abs(slope1 - slope2) < 0.5:
                        # Calculate the direction of the line from coordinates7 to coordinates8
                        direction = (coordinates8[0] - coordinates7[0], coordinates8[1] - coordinates7[1])

                        # Normalize the direction
                        length = (direction[0]**2 + direction[1]**2)**0.5
                        direction = (direction[0]/length, direction[1]/length)

                        # Calculate the point on the border of the screen
                        # Assuming the screen size is (1280, screen_height)
                        border_point = (int(coordinates7[0]*1280 + direction[0]*1280), int(coordinates7[1]*720 + direction[1]*720))

                        # Draw the line from coordinates7 to coordinates8
                        cv2.line(frame, (int(coordinates7[0]*1280), int(coordinates7[1]*720)), (int(coordinates8[0]*1280), int(coordinates8[1]*720)), (0, 255, 0), 10)

                        # Draw the line from coordinates8 to the border of the screen
                        cv2.line(frame, (int(coordinates8[0]*1280), int(coordinates8[1]*720)), border_point, (0, 255, 0), 10)
                        
                    

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
                      
                print(self.tkapp.skeleton_mode.get())            
                if self.tkapp.skeleton_mode.get():
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
        
        Label_skeleton_mode = ctk.CTkLabel(self, text="Toggle the skeleton mode")
        Label_skeleton_mode.pack(side=tk.TOP)
        Checkbox_skeleton_mode = ctk.CTkCheckBox(self, variable=self.tkapp.skeleton_mode)
        Checkbox_skeleton_mode.pack(side=tk.TOP)
        
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
        
        save_settigs = """
        INSERT INTO settings (detection_confidence, tracking_confidence, max_num_hands, model_complexity, skeleton_mode)
        VALUES (?, ?, ?, ?, ?)
        """
        
        self.tkapp.c.execute(save_settigs, (self.tkapp.detection_confidence.get(),
                                            self.tkapp.tracking_confidence.get(),
                                            self.tkapp.max_num_hands.get(),
                                            self.tkapp.model_complexity.get(),
                                            self.tkapp.skeleton_mode.get()))
        
        self.tkapp.conn.commit()

class Window(ctk.CTk):  
    def __init__(self):
        super().__init__()
        self.settings_window = None

        self.screenheight = self.winfo_screenheight()
        self.screenwidth = self.winfo_screenwidth()

        self.toplevel_window = None
        self.fps = -1
        self.skeleton_mode = False
        
        # Set window title
        self.title("Hand Tracking App")
        self.after(0, lambda:self.state('zoomed'))
        self.configure(fg_color="#0e1718", bg_color="#3D3D3D")
        self.geometry(f"{self.screenwidth}x{self.screenheight}")
        
        self.tk_setPalette(background='#3D3D3D', foreground='#ffffff',
               activeBackground='#3D3D3D', activeForeground='#ffffff')
        
        self.create_navigation_bar()
        
        self.init_sqlite_db()
        self.load_settings()
        
        self.video_feed()   
        
        
    def load_settings(self):
        self.c.execute("SELECT * FROM settings ORDER BY id DESC LIMIT 1")
        settings = self.c.fetchone()
        self.detection_confidence = tk.StringVar(value="0.75") 
        self.tracking_confidence = tk.StringVar(value="0.75")
        self.max_num_hands = tk.StringVar(value="2")
        self.model_complexity = tk.StringVar(value="1")
        self.skeleton_mode = tk.BooleanVar(value=False)
        
        if settings is not None:
            self.detection_confidence.set(settings[1])
            self.tracking_confidence.set(settings[2])
            self.max_num_hands.set(settings[3])
            self.model_complexity.set(settings[4])
            self.skeleton_mode.set(settings[5])
        
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
        
    def video_feed(self):
        
        image_label = ctk.CTkLabel(self, text="", width=1280, height=720, bg_color="#ffffff")
        empty_image = Image.new('RGB', (1280, 720))
        ctkimage = ctk.CTkImage(empty_image, empty_image, size=(1280, 720))
        image_label.pack(side=tk.TOP)
        
        self.HandTracker = HandTracking(self)
        
        while True:
            StartT = time.time()
            #time.sleep(0.03)
            frame = self.HandTracker.process_video()

            #Update the image to tkinter...
            try:
                img_update = Image.fromarray(frame, 'RGB')
                
                ctkimage.configure(light_image=img_update, dark_image=img_update)
                    
                image_label.configure(image=ctkimage)
                image_label.update()
                
                self.fps = 1/(time.time()-StartT)
                
            except RuntimeError:
                print("Window was closed: RuntimeError")
                os._exit(0)  
            
            except AttributeError:
                print("Window was closed: AttributeError")
                os._exit(0)
                        
    def init_sqlite_db(self):
        self.conn = sqlite3.connect('settings.db')
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        detection_confidence TEXT DEFAULT 0.75,
                        tracking_confidence TEXT DEFAULT 0.75,
                        max_num_hands TEXT DEFAULT 2,
                        model_complexity TEXT DEFAULT 0,
                        skeleton_mode BOOLEAN DEFAULT FALSE
                        )""")
        self.conn.commit()


        
tkapp = Window()



if __name__ == "__main__":
    tkapp.mainloop()