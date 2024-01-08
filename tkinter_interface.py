import tkinter as tk
from tkinter import ttk
from tkinter import filedialog
import customtkinter as ctk
import threading
import requests
import os
import time

global tkapp


class ToplevelWindow(ctk.CTkToplevel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geometry("400x400")


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
        self.configure(fg_color="#0e1718")
        self.geometry(f"{self.screenwidth}x{self.screenheight}")
        
        self.tk_setPalette(background='#ffffff', foreground='#0e1718',
               activeBackground='#ffffff', activeForeground='#0e1718')
        
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
        menu.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Settings", command=self.create_settings_window)
        file_menu.add_command(label="Exit", command=self.destroy)
       
        
        self.configure(menu=menu)


tkapp = Window()



if __name__ == "__main__":
    tkapp.mainloop()