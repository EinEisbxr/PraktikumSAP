import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import threading
import requests
import os
import time

global tkapp

class Window(ctk.CTk):
          
    def __init__(self):
        super().__init__()
        self.settings_window = None

        self.screenheight = self.winfo_screenheight()
        self.screenwidth = self.winfo_screenwidth()
        
        # Set window title
        self.title("Hand Tracking App")
        self.after(0, lambda:self.state('normal'))
        self.configure(fg_color="#0e1718")
        self.geometry(f"{self.screenwidth}x{self.screenheight}")
        
        self.tk_setPalette(background='#ffffff', foreground='#0e1718',
               activeBackground='#ffffff', activeForeground='#0e1718')
        
        self.create_navigation_bar()
        
    # create settings window when settings button was pressed 
    def create_settings_window(self):
        if self.settings_window == None:
            self.settings_window = ctk.CTkToplevel(self)
            
            #Configure settings window
            self.settings_window.title("Settings")
            self.settings_window.geometry("400x400")
            self.settings_window.configure(fg_color="#0e1718")
            self.settings_window.tk_setPalette(background='#0e1718', foreground='#0e1718',
               activeBackground='#0e1718', activeForeground='#0e1718')
            
            
            self.settings_window.mainloop()
            
        else:
            self.settings_window.lift()
            
    def on_settings_window_destroy(self, event):
        self.settings_window = None

            
    def create_navigation_bar(self):
        menu = tk.Menu(self)
        
        file_menu = tk.Menu(self)
        menu.add_cascade(label="Settings", menu=file_menu, command=self.create_settings_window)
       
        
        self.configure(menu=menu)


tkapp = Window()



if __name__ == "__main__":
    tkapp.mainloop()