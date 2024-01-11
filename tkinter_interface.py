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
        self.TimeoutUpDown = 0
        
        self.open_palm_counter = 0
        self.none_counter = 0
        self.thumb_up_counter = 0
        self.thumb_down_counter = 0
        
    def process_video(self):
        
        
        
        video_feed_width = self.tkapp.video_feed_width 
        video_feed_width_half = int(video_feed_width / 2) 
        video_feed_height = self.tkapp.video_feed_height 
        video_feed_height_minus_50 = int(video_feed_height - 50) 
        video_feed_height_minus_100 = int(video_feed_height - 100) 
        screenwidth = self.tkapp.screenwidth 
        screenheight = self.tkapp.screenheight 
        fps = self.tkapp.fps 
        gesture_mode = self.tkapp.gesture_mode.get() 
        skeleton_mode = self.tkapp.skeleton_mode.get() 
        
        
        # gesture_recognition = self.tkapp.gesture_recognition.get()
        timetime = time.time()

        ret, frame = self.cap.read()
        frame = cv2.resize(frame, (video_feed_width, video_feed_height))
        frame = cv2.flip(frame, 1)
          

        if not ret:
            
            print("Error: No video feed")
            return
        
            
        frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame = frameRGB

        cv2.putText(frame, f"FPS: {fps:.2f}", (video_feed_width_half, video_feed_height_minus_50), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)

        results = self.hands.process(frameRGB)

        # If hands are present in image(frame) 
        if results.multi_hand_landmarks: 
                        
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame)
            
            self.frame_timestamp_ms = int(round(timetime * 1000))
            
            if self.tkapp.gesture_recognition.get():
                gesture_recognition_result = self.recognizer.recognize_for_video(mp_image, self.frame_timestamp_ms)
                
                if gesture_recognition_result is not None and len(gesture_recognition_result.gestures) > 0:
                    category_name = gesture_recognition_result.gestures[0][0].category_name
                    if category_name and category_name != "None":
                        cv2.putText(frame, f"Gesture: {category_name}", (video_feed_width_half, video_feed_height_minus_100), cv2.FONT_HERSHEY_COMPLEX, 0.9, (0, 255, 0), 2)
                    print(category_name)

                    #Quick Chat mode
                    if gesture_mode == 1:
                        if category_name == "Thumb_Up" and self.Timeout_Thumb_Up < timetime:
                            keyboard.write("👍")
                            keyboard.press_and_release('enter')
                            self.Timeout_Thumb_Up = timetime + 1
                            
                        if category_name == "Thumb_Down" and self.Timeout_Thumb_Up < timetime:
                            keyboard.write("👎")
                            keyboard.press_and_release('enter')
                            self.Timeout_Thumb_Up = timetime + 1
                            
                    #Macro mode
                    elif gesture_mode == 2:
                        pass
                    
                    #Mouse Control mode
                    elif gesture_mode == 3:
                        coordinates_index_finger = (results.multi_hand_landmarks[0].landmark[8].x, results.multi_hand_landmarks[0].landmark[8].y)
                        if threading.active_count() < 2:
                            tmousemove = threading.Thread(target=pag.moveTo, args=(coordinates_index_finger[0]*screenwidth*1.2, coordinates_index_finger[1]*screenheight*1.2, 0.0, 0.0, False))
                            tmousemove.start()
                            
                        #When the palm is open, then display some sort of progress cirle around the hand and click when the circle is full it should be like a 1 second delay
                        if category_name == "Open_Palm":
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
                    
                        elif category_name == "Thumb_Up" and self.TimeoutUpDown < timetime:
                            self.thumb_up_counter += 1
                            self.none_counter = 0
                            if self.thumb_up_counter >= self.tkapp.fps:
                                #press arrow up
                                keyboard.press_and_release('up')
                                self.thumb_up_counter = 0
                                self.TimeoutUpDown = timetime + 1
                            
                        elif category_name == "Thumb_Down"and self.TimeoutUpDown < timetime:
                            self.thumb_down_counter += 1
                            self.none_counter = 0
                            if self.thumb_down_counter >= self.tkapp.fps:
                                #press arrow down
                                keyboard.press_and_release('down')
                                self.thumb_down_counter = 0
                                self.TimeoutUpDown = timetime + 1
                        
                        else:
                            # Increase the none counter
                            self.none_counter += 1
                            
                            # If there have been 3 consecutive none statements, reset the open palm counter
                            if self.none_counter >= self.tkapp.fps:
                                self.open_palm_counter = 0
                                self.none_counter = 0
                                self.thumb_up_counter = 0
                                self.thumb_down_counter = 0

                    elif gesture_mode == 4:
                        lines = []
                        for hand_landmarks in results.multi_hand_landmarks:
                            coordinates6 = (hand_landmarks.landmark[6].x, hand_landmarks.landmark[6].y)
                            coordinates7 = (hand_landmarks.landmark[7].x, hand_landmarks.landmark[7].y)
                            coordinates8 = (hand_landmarks.landmark[8].x, hand_landmarks.landmark[8].y)

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
                                border_point = (int(coordinates7[0]*video_feed_width + direction[0]*video_feed_width), int(coordinates7[1]*video_feed_height + direction[1]*video_feed_height))

                                # Draw the line from coordinates7 to coordinates8
                                cv2.line(frame, (int(coordinates7[0]*video_feed_width), int(coordinates7[1]*video_feed_height)), (int(coordinates8[0]*video_feed_width), int(coordinates8[1]*video_feed_height)), (0, 255, 0), 10)

                                # Draw the line from coordinates8 to the border of the screen
                                cv2.line(frame, (int(coordinates8[0]*video_feed_width), int(coordinates8[1]*video_feed_height)), border_point, (0, 255, 0), 10)
                                
                                lines.append(((int(coordinates7[0]*video_feed_width), int(coordinates7[1]*video_feed_height)), border_point))
                            
                        # Check for intersections
                        for i in range(len(lines)):
                            for j in range(i+1, len(lines)):
                                # Calculate intersection point
                                xdiff = (lines[i][0][0] - lines[i][1][0], lines[j][0][0] - lines[j][1][0])
                                ydiff = (lines[i][0][1] - lines[i][1][1], lines[j][0][1] - lines[j][1][1])

                                def det(a, b):
                                    return a[0] * b[1] - a[1] * b[0]

                                div = det(xdiff, ydiff)
                                if div == 0:
                                    continue

                                d = (det(*lines[i]), det(*lines[j]))
                                x = det(d, xdiff) / div
                                y = det(d, ydiff) / div

                                # Draw a circle at the intersection point
                                cv2.circle(frame, (int(x), int(y)), radius=40, color=(255, 0, 0), thickness=-1)
                            
                    else:
                        print("Error: Gesture Mode not found")

            
            if skeleton_mode:
                for hand_landmarks in results.multi_hand_landmarks:
                    self.mp_drawing.draw_landmarks(
                        frame, hand_landmarks, self.mpHands.HAND_CONNECTIONS,
                        self.mp_drawing_styles.get_default_hand_landmarks_style(),
                        self.mp_drawing_styles.get_default_hand_connections_style()) 


        return frame

      
        

class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, tkapp, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x600")
        self.title("Settings")

        #self.configure(fg_color="#0e1718")
        #self.tk_setPalette(background='#ffffff', foreground='#0e1718',
        #       activeBackground='#ffffff', activeForeground='#0e1718')
        self.tkapp = tkapp
        
        self.bind("<s>", lambda event: self.tkapp.create_settings_window())
        self.bind("<S>", lambda event: self.tkapp.create_settings_window())
        
        self.bind("<q>", lambda event: self.tkapp.close_application())
        self.bind("<Q>", lambda event: self.tkapp.close_application())
        
        self.bind("<F1>", lambda event: self.tkapp.hotkey_functions("F1"))
        self.bind("<F2>", lambda event: self.tkapp.hotkey_functions("F2"))
        self.bind("<F3>", lambda event: self.tkapp.hotkey_functions("F3"))
        self.bind("<F4>", lambda event: self.tkapp.hotkey_functions("F4"))
        
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
        
        Checkbox_gesture_recognition = ctk.CTkCheckBox(Checkboxframe, variable=self.tkapp.gesture_recognition, text="Toggle gesture recognition")
        Checkbox_gesture_recognition.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        RadioButton_quick_chat = ctk.CTkRadioButton(Checkboxframe, variable=self.tkapp.gesture_mode, value=1, text="Quick Chat")
        RadioButton_quick_chat.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        RadioButton_macro = ctk.CTkRadioButton(Checkboxframe, variable=self.tkapp.gesture_mode, value=2, text="Macro")
        RadioButton_macro.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        RadioButton_mouse_control = ctk.CTkRadioButton(Checkboxframe, variable=self.tkapp.gesture_mode, value=3, text="Mouse Control")
        RadioButton_mouse_control.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        Radio_button_laser_pointer = ctk.CTkRadioButton(Checkboxframe, variable=self.tkapp.gesture_mode, value=4, text="Laser Pointer")
        Radio_button_laser_pointer.pack(side=tk.TOP, anchor=tk.W, pady=5, padx=5)
        
        
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
        UPDATE settings
        SET detection_confidence = ?, tracking_confidence = ?, max_num_hands = ?, model_complexity = ?, skeleton_mode = ?, cam_number = ?, gesture_recognition = ?, gesture_mode = ?
        WHERE id = 1
        """
        
        self.tkapp.c.execute(save_settigs, (self.tkapp.detection_confidence.get(),
                                            self.tkapp.tracking_confidence.get(),
                                            self.tkapp.max_num_hands.get(),
                                            self.tkapp.model_complexity.get(),
                                            self.tkapp.skeleton_mode.get(),
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
        self.running = True
        
        self.video_feed_width = 640
        self.video_feed_height = 360
        
        self.tkinter_width = int(self.screenwidth/2)
        self.tkinter_height = int(self.screenheight/2)
        
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
        
        self.bind("<q>", lambda event: self.close_application())
        self.bind("<Q>", lambda event: self.close_application())
        
        self.bind("<F1>", lambda event: self.hotkey_functions("F1"))
        self.bind("<F2>", lambda event: self.hotkey_functions("F2"))
        self.bind("<F3>", lambda event: self.hotkey_functions("F3"))
        self.bind("<F4>", lambda event: self.hotkey_functions("F4"))
        
                   
        
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
        self.cam_number = tk.StringVar(value="0")
        self.gesture_recognition = tk.BooleanVar(value=False)
        self.gesture_mode = tk.IntVar(value=1)
        
        if settings is not None:
            self.detection_confidence.set(settings[1])
            self.tracking_confidence.set(settings[2])
            self.max_num_hands.set(settings[3])
            self.model_complexity.set(settings[4])
            self.skeleton_mode.set(settings[5])
            self.cam_number.set(settings[6])
            self.gesture_recognition.set(settings[7])
            self.gesture_mode.set(settings[8])
        
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
        image_label.pack(side=tk.TOP)
        
        self.HandTracker = HandTracking(self)
        try:
            while self.running:
                StartT = time.time()
                
                frame = self.HandTracker.process_video()
                
                print("Time needed: ", time.time()-StartT)
                
                # Resize the frame before converting it to an image
                frame = cv2.resize(frame, (self.tkinter_width, self.tkinter_height), interpolation=cv2.INTER_NEAREST)
                
                # Convert the frame to an image
                img_update = Image.fromarray(frame, 'RGB')
                
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
                        skeleton_mode BOOLEAN DEFAULT FALSE,
                        cam_number TEXT DEFAULT 0,
                        gesture_recognition BOOLEAN DEFAULT FALSE,
                        gesture_mode TEXT DEFAULT 1
                        )""")
        self.conn.commit()

    def hotkey_functions(self, hotkey):
        if "F1" in hotkey:
            self.skeleton_mode.set(not self.skeleton_mode.get())
            self.apply_settings_hotkeys()
        elif "F2" in hotkey:
            self.gesture_recognition.set(not self.gesture_recognition.get())
            self.apply_settings_hotkeys()
        elif "F3" in hotkey:
            self.gesture_mode.set(self.gesture_mode.get() + 1 if self.gesture_mode.get() < 4 else 1)
            self.apply_settings_hotkeys()
        elif "F4" in hotkey:
            self.gesture_mode.set(self.gesture_mode.get() - 1 if self.gesture_mode.get() > 1 else 4)
            self.apply_settings_hotkeys()
        
        
    def apply_settings_hotkeys(self):

        save_settigs = """
        UPDATE settings
        SET skeleton_mode = ?, gesture_recognition = ?, gesture_mode = ?
        WHERE id = 1
        """
        
        self.tkapp.c.execute(save_settigs, (self.skeleton_mode.get(),
                                            self.gesture_recognition.get(),
                                            self.gesture_mode.get()))
        
        self.tkapp.conn.commit()
        
tkapp = Window()



if __name__ == "__main__":
    cv2.ocl.setUseOpenCL(True)
    pag.FAILSAFE = False
    tkapp.mainloop()