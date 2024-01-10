import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import time
import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from google.protobuf.json_format import MessageToDict
import numpy as np
from PIL import Image, ImageTk
import os
import sqlite3
import keyboard
import pyautogui as pag
import threading


global tkapp


class HandTracking():
    def __init__(self, tkapp) -> None:
        self.cap = cv2.VideoCapture(int(tkapp.cam_number.get()))
        
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        
        VisionRunningMode = mp.tasks.vision.RunningMode
                
        self.base_options = python.BaseOptions(model_asset_path='gesture_recognizer.task')
        self.options = vision.GestureRecognizerOptions(base_options=self.base_options, running_mode=VisionRunningMode.VIDEO)
        self.recognizer = vision.GestureRecognizer.create_from_options(self.options)

        # Initializing the Model 
        self.mpHands = mp.solutions.hands   
        self.hands = self.mpHands.Hands(    
            static_image_mode=False, 
            model_complexity=int(tkapp.model_complexity.get()),
            min_detection_confidence=float(tkapp.detection_confidence.get()),
            min_tracking_confidence=float(tkapp.tracking_confidence.get()),
            max_num_hands=int(tkapp.max_num_hands.get()))
        
        self.tkapp = tkapp
        self.Timeout_Thumb_Up = 0
        
        self.open_palm_counter = 0
        self.none_counter = 0
        
    def process_video(self):
        #frame=np.random.randint(0,255,[1000,1000,3],dtype='uint8')
        #load frames from file
        #frame = cv2.imread("test3.jpeg")
        #ret = True
        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (self.tkapp.video_feed_width, self.tkapp.video_feed_height))
        
        #flip the frame
        frame = cv2.flip(frame, 1)

        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frameRGB = frame

            cv2.putText(frame, f"FPS: {self.tkapp.fps:.2f}", (int(self.tkapp.video_feed_width/2), int(self.tkapp.video_feed_height-50)), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)


            results = self.hands.process(frameRGB)

            # If hands are present in image(frame) 
            if results.multi_hand_landmarks: 
                            
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
                
                self.frame_timestamp_ms = int(round(time.time() * 1000))
                
                if self.tkapp.gesture_recognition.get():
                    gesture_recognition_result = self.recognizer.recognize_for_video(mp_image, self.frame_timestamp_ms)
                    
                    if gesture_recognition_result is not None:
                        #GestureRecognizerResult(gestures=[[Category(index=-1, score=0.552459716796875, display_name='', category_name='Open_Palm')]] get category name
                        if len(gesture_recognition_result.gestures) > 0:
                            if gesture_recognition_result.gestures[0][0].category_name != None and gesture_recognition_result.gestures[0][0].category_name != "" and gesture_recognition_result.gestures[0][0].category_name != "None":
                                cv2.putText(frame, f"Gesture: {gesture_recognition_result.gestures[0][0].category_name}", (int(self.tkapp.video_feed_width/2), int(self.tkapp.video_feed_height-100)), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
                            print(gesture_recognition_result.gestures[0][0].category_name)

                            #Quick Chat mode
                            if self.tkapp.gesture_mode.get() == 1:
                                if gesture_recognition_result.gestures[0][0].category_name == "Thumb_Up" and self.Timeout_Thumb_Up < time.time():
                                    keyboard.write("👍")
                                    keyboard.press_and_release('enter')
                                    self.Timeout_Thumb_Up = time.time() + 1
                                    
                                if gesture_recognition_result.gestures[0][0].category_name == "Thumb_Down" and self.Timeout_Thumb_Up < time.time():
                                    keyboard.write("👎")
                                    keyboard.press_and_release('enter')
                                    self.Timeout_Thumb_Up = time.time() + 1
                                    
                            #Macro mode
                            elif self.tkapp.gesture_mode.get() == 2:
                                pass
                            
                            #Mouse Control mode
                            elif self.tkapp.gesture_mode.get() == 3:
                                coordinates_index_finger = (results.multi_hand_landmarks[0].landmark[8].x, results.multi_hand_landmarks[0].landmark[8].y)
                                if threading.active_count() < 2:
                                    tmousemove = threading.Thread(target=pag.moveTo, args=(coordinates_index_finger[0]*self.tkapp.screenwidth*2, coordinates_index_finger[1]*self.tkapp.screenheight, 0.0, 0.0, False))
                                    tmousemove.start()
                                    
                                #When the palm is open, then display some sort of progress cirle around the hand and click when the circle is full it should be like a 1 second delay
                                if gesture_recognition_result.gestures[0][0].category_name == "Open_Palm":
                                    # Increase the counter
                                    self.open_palm_counter += 1

                                    # Reset the none counter
                                    self.none_counter = 0

                                    # Calculate the progress
                                    progress = self.open_palm_counter / self.tkapp.fps

                                    # Draw the circle
                                    cv2.circle(frame, (int(self.tkapp.video_feed_width/2), int(self.tkapp.video_feed_height/2)), 50, (0, 255, 0), 2)

                                    # Draw the progress arc
                                    cv2.ellipse(frame, (int(self.tkapp.video_feed_width/2), int(self.tkapp.video_feed_height/2)), (50, 50), 0, 0, progress * 360, (0, 255, 0), 2)

                                    # If the palm has been open for 1 second, trigger a click event
                                    if self.open_palm_counter >= self.tkapp.fps:
                                        pag.click()
                                        self.open_palm_counter = 0
                                else:
                                    # Increase the none counter
                                    self.none_counter += 1

                                    # If there have been 3 consecutive none statements, reset the open palm counter
                                    if self.none_counter >= 3:
                                        self.open_palm_counter = 0
                                        self.none_counter = 0
                                    
                            else:
                                print("Error: Gesture Mode not found")
                                    
                    
                if self.tkapp.laser_pointer.get():
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
                            # Assuming the screen size is (self.tkapp.video_feed_width, screen_height)
                            border_point = (int(coordinates7[0]*self.tkapp.video_feed_width + direction[0]*self.tkapp.video_feed_width), int(coordinates7[1]*self.tkapp.video_feed_height + direction[1]*self.tkapp.video_feed_height))

                            # Draw the line from coordinates7 to coordinates8
                            cv2.line(frame, (int(coordinates7[0]*self.tkapp.video_feed_width), int(coordinates7[1]*self.tkapp.video_feed_height)), (int(coordinates8[0]*self.tkapp.video_feed_width), int(coordinates8[1]*self.tkapp.video_feed_height)), (0, 255, 0), 10)

                            # Draw the line from coordinates8 to the border of the screen
                            cv2.line(frame, (int(coordinates8[0]*self.tkapp.video_feed_width), int(coordinates8[1]*self.tkapp.video_feed_height)), border_point, (0, 255, 0), 10)
                        
                
                #print(self.tkapp.skeleton_mode.get())            
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
        
        Label_cam_number = ctk.CTkLabel(self, text="Camera Number")
        Label_cam_number.pack(side=tk.TOP)
        Entry_cam_number = ctk.CTkEntry(self, textvariable=self.tkapp.cam_number)
        Entry_cam_number.pack(side=tk.TOP)  
        
        Checkboxframe = ctk.CTkFrame(self)
        Checkboxframe.pack(side=tk.TOP)
        
        Checkbox_skeleton_mode = ctk.CTkCheckBox(Checkboxframe, variable=self.tkapp.skeleton_mode, text="Toggle skeleton mode")
        Checkbox_skeleton_mode.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        Checkbox_laser_pointer = ctk.CTkCheckBox(Checkboxframe, variable=self.tkapp.laser_pointer, text="Toggle laser pointer")
        Checkbox_laser_pointer.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        Checkbox_gesture_recognition = ctk.CTkCheckBox(Checkboxframe, variable=self.tkapp.gesture_recognition, text="Toggle gesture recognition")
        Checkbox_gesture_recognition.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        RadioButton_quick_chat = ctk.CTkRadioButton(Checkboxframe, variable=self.tkapp.gesture_mode, value=1, text="Quick Chat")
        RadioButton_quick_chat.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        RadioButton_macro = ctk.CTkRadioButton(Checkboxframe, variable=self.tkapp.gesture_mode, value=2, text="Macro")
        RadioButton_macro.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        RadioButton_mouse_control = ctk.CTkRadioButton(Checkboxframe, variable=self.tkapp.gesture_mode, value=3, text="Mouse Control")
        RadioButton_mouse_control.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        
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
        INSERT INTO settings (detection_confidence, tracking_confidence, max_num_hands, model_complexity, skeleton_mode, laser_pointer, cam_number, gesture_recognition, gesture_mode)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        
        self.tkapp.c.execute(save_settigs, (self.tkapp.detection_confidence.get(),
                                            self.tkapp.tracking_confidence.get(),
                                            self.tkapp.max_num_hands.get(),
                                            self.tkapp.model_complexity.get(),
                                            self.tkapp.skeleton_mode.get(),
                                            self.tkapp.laser_pointer.get(),
                                            self.tkapp.cam_number.get(),
                                            self.tkapp.gesture_recognition.get(),
                                            self.tkapp.gesture_mode.get()))
        
        #self.cap.release()
        self.tkapp.HandTracker.cap = cv2.VideoCapture(int(self.tkapp.cam_number.get()))
        
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
        self.laser_pointer = False
        self.running = True
        
        self.video_feed_width = 640
        self.video_feed_height = 360
        
        self.tkinter_width = int(2560/2)
        self.tkinter_height = int(1440/2)
        
        # Set window title
        self.title("Hand Tracking App")
        self.after(0, lambda:self.state('zoomed'))
        self.configure(fg_color="#0e1718", bg_color="#3D3D3D")
        self.geometry(f"{self.screenwidth}x{self.screenheight}")
        
        self.tk_setPalette(background='#3D3D3D', foreground='#ffffff',
               activeBackground='#3D3D3D', activeForeground='#ffffff')
        
        self.bind("<Destroy>", lambda event: self.close_application())
        #bind ^ to opeb settings window
        self.bind("<s>", lambda event: self.create_settings_window())
        self.bind("<S>", lambda event: self.create_settings_window())
        
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
        self.laser_pointer = tk.BooleanVar(value=False)
        self.cam_number = tk.StringVar(value="0")
        self.gesture_recognition = tk.BooleanVar(value=False)
        self.gesture_mode = tk.IntVar(value=1)
        
        if settings is not None:
            self.detection_confidence.set(settings[1])
            self.tracking_confidence.set(settings[2])
            self.max_num_hands.set(settings[3])
            self.model_complexity.set(settings[4])
            self.skeleton_mode.set(settings[5])
            self.laser_pointer.set(settings[6])
            self.cam_number.set(settings[7])
            self.gesture_recognition.set(settings[8])
            self.gesture_mode.set(settings[9])
        
    # create settings window when settings button was pressed 
    def create_settings_window(self):
        if self.toplevel_window is None or not self.toplevel_window.winfo_exists():
            self.toplevel_window = ToplevelWindow(self)  # create window if its None or destroyed
            time.sleep(0.1)
            self.toplevel_window.update()
            self.toplevel_window.update_idletasks()
            self.update()
            self.update_idletasks()
            self.toplevel_window.lift()
            self.toplevel_window.focus()
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
        
        image_label = ctk.CTkLabel(self, text="", width=self.tkinter_width, height=self.tkinter_height, bg_color="#ffffff")
        #empty_image = Image.new('RGB', (self.tkinter_width, self.tkinter_height))
        #ctkimage = ctk.CTkImage(empty_image, empty_image, size=(self.tkinter_width, self.tkinter_height))
        image_label.pack(side=tk.TOP)
        
        self.HandTracker = HandTracking(self)
        
        while self.running:
            StartT = time.time()
            #time.sleep(0.03)
            frame = self.HandTracker.process_video()
            
            #Update the image to tkinter...
            try:
                img_update = Image.fromarray(frame, 'RGB')
                
                img_update = img_update.resize((self.tkinter_width, self.tkinter_height), Image.ANTIALIAS)
                
                ctkimage = ImageTk.PhotoImage(img_update)
                
    
                image_label.configure(image=ctkimage)
                image_label.update()
                
                self.fps = 1/(time.time()-StartT)
                
            except RuntimeError:
                print("Window was closed: RuntimeError") 
                self.close_application()
            
            except AttributeError:
                print("Window was closed: AttributeError")
                self.close_application()

                
    
    def close_application(self):
        self.running = False
        self.conn.close()
        #os._exit(0)
        
                        
    def init_sqlite_db(self):
        self.conn = sqlite3.connect('settings.db')
        self.c = self.conn.cursor()
        self.c.execute("""CREATE TABLE IF NOT EXISTS settings (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        detection_confidence TEXT DEFAULT 0.75,
                        tracking_confidence TEXT DEFAULT 0.75,
                        max_num_hands TEXT DEFAULT 2,
                        model_complexity TEXT DEFAULT 0,
                        skeleton_mode BOOLEAN DEFAULT FALSE,
                        laser_pointer BOOLEAN DEFAULT FALSE,
                        cam_number TEXT DEFAULT 0,
                        gesture_recognition BOOLEAN DEFAULT FALSE,
                        gesture_mode TEXT DEFAULT 1
                        )""")
        self.conn.commit()


        
tkapp = Window()



if __name__ == "__main__":
    tkapp.mainloop()