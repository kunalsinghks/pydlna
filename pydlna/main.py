import uvicorn
import logging
import argparse
import threading
import sys
import os
import signal
import asyncio
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox
import customtkinter as ctk
import pystray
from PIL import Image, ImageDraw
from pydlna.config import load_settings, settings, update_media_paths, save_config
from pydlna.scanner import MediaScanner

# Setup basic logging
try:
    log_dir = os.path.expanduser("~")
    log_file = os.path.join(log_dir, "pydlna_debug.log")
except Exception:
    log_file = "pydlna.log"

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, mode='w'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("pydlna")
logger.info("Application starting...")

# Global reference to control server
server_instance = None
server_thread = None

class PyDLNAGUI(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title(f"{settings.friendly_name} pyDLNA")
        self.geometry("800x600")
        self.protocol("WM_DELETE_WINDOW", self.minimize_to_tray)
        
        # Appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Grid config
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(7, weight=1) # Main Spacer row at bottom
        
        self.sidebar_label = ctk.CTkLabel(self.sidebar, text="PyDLNA", font=ctk.CTkFont(size=24, weight="bold"))
        self.sidebar_label.grid(row=0, column=0, padx=20, pady=(20, 10))
        
        self.rescan_btn = ctk.CTkButton(self.sidebar, text="Rescan Library", command=self.rescan)
        self.rescan_btn.grid(row=1, column=0, padx=20, pady=10)
        
        self.stop_btn = ctk.CTkButton(self.sidebar, text="Stop Server", fg_color="#ef4444", hover_color="#dc2626", command=self.toggle_server)
        self.stop_btn.grid(row=2, column=0, padx=20, pady=10)
        
        self.quit_btn = ctk.CTkButton(self.sidebar, text="Quit App", fg_color="transparent", border_width=1, border_color="#ef4444", text_color="#ef4444", hover_color="#330000", command=self.quit_fully)
        self.quit_btn.grid(row=5, column=0, padx=20, pady=20)
        
        self.clear_cache_btn = ctk.CTkButton(self.sidebar, text="Clear Cache", fg_color="transparent", border_width=1, border_color="#ef4444", text_color="#ef4444", hover_color="#330000", command=self.clear_cache)
        self.clear_cache_btn.grid(row=3, column=0, padx=20, pady=10)

        # Server Settings in Sidebar (Label removed as requested)
        self.name_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Server Name")
        self.name_entry.grid(row=4, column=0, padx=20, pady=(5, 2))
        self.name_entry.insert(0, settings.friendly_name)
        
        self.port_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Port (e.g. 8200)")
        self.port_entry.grid(row=5, column=0, padx=20, pady=2)
        self.port_entry.insert(0, str(settings.port))
        
        self.save_settings_btn = ctk.CTkButton(self.sidebar, text="Update Discovery / Link", command=self.save_general_settings)
        self.save_settings_btn.grid(row=6, column=0, padx=20, pady=(2, 10))
        
        # Spacer configuration moved to top for clarity (already updated)
        
        self.pass_btn = ctk.CTkButton(self.sidebar, text="Set Credentials", fg_color="transparent", border_width=1, border_color="#3b82f6", text_color="#3b82f6", command=self.set_password)
        self.pass_btn.grid(row=8, column=0, padx=20, pady=5)

        self.quit_btn = ctk.CTkButton(self.sidebar, text="Quit App", fg_color="transparent", border_width=1, border_color="#ef4444", text_color="#ef4444", hover_color="#330000", command=self.quit_fully)
        self.quit_btn.grid(row=9, column=0, padx=20, pady=20)

        # Main Content
        self.main_frame = ctk.CTkFrame(self, corner_radius=15)
        self.main_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.main_frame.grid_columnconfigure(0, weight=1)

        self.label = ctk.CTkLabel(self.main_frame, text="Media Libraries", font=ctk.CTkFont(size=20, weight="bold"))
        self.label.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="w")

        # Scrollable list for paths
        self.path_frame = ctk.CTkScrollableFrame(self.main_frame, label_text="Configured Paths")
        self.path_frame.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        self.main_frame.grid_rowconfigure(1, weight=1)

        self.add_btn = ctk.CTkButton(self.main_frame, text="Add New Directory", command=self.add_directory)
        self.add_btn.grid(row=2, column=0, padx=20, pady=20)
        
        # Status area
        self.status_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        self.status_frame.grid(row=3, column=0, padx=20, pady=10, sticky="ew")
        
        self.server_label = ctk.CTkLabel(self.status_frame, text="Server:", text_color="#94a3b8")
        self.server_label.pack(side="left", padx=(0, 5))
        
        # Clickable Link
        self.link_label = ctk.CTkLabel(self.status_frame, text=settings.base_url, text_color="#3b82f6", cursor="hand2")
        self.link_label.pack(side="left", padx=5)
        self.link_label.bind("<Button-1>", lambda e: self.open_link())
        self.link_label.bind("<Enter>", lambda e: self.link_label.configure(text_color="#60a5fa"))
        self.link_label.bind("<Leave>", lambda e: self.link_label.configure(text_color="#3b82f6"))
        
        # Icon-style Copy Button (unicode clipboard)
        self.copy_btn = ctk.CTkButton(self.status_frame, text="📋", width=30, height=30, fg_color="transparent", hover_color="#334155", 
                                      command=self.copy_link, font=("Arial", 16))
        self.copy_btn.pack(side="left", padx=5)

        self.should_run_headless = False
        self.tray_icon = None
        self.update_path_list()
        self.update_server_status()

    def save_general_settings(self):
        new_name = self.name_entry.get().strip()
        new_port_str = self.port_entry.get().strip()
        if not new_name:
            messagebox.showerror("Error", "Server name cannot be empty.")
            return
        try:
            new_port = int(new_port_str)
            if not (1024 <= new_port <= 65535): raise ValueError()
        except ValueError:
            messagebox.showerror("Error", "Port must be 1024-65535.")
            return

        old_port = settings.port
        settings.friendly_name = new_name
        settings.port = new_port
        save_config()
        self.title(f"{new_name} pyDLNA")
        self.update_server_status()
        
        if old_port != new_port:
            messagebox.showinfo("Restart Required", "Port changed. Please Stop/Start the server.")
        else:
            messagebox.showinfo("Success", "Server name updated.")

    # Create a simple icon image
    def create_icon_image(self):
        # Create a simple colored square icon
        width = 64
        height = 64
        color1 = "#3b82f6"
        color2 = "#a855f7"
        image = Image.new('RGB', (width, height), color1)
        dc = ImageDraw.Draw(image)
        dc.rectangle(
            (width // 2, 0, width, height // 2),
            fill=color2)
        dc.rectangle(
            (0, height // 2, width // 2, height),
            fill=color2)
        return image

    def minimize_to_tray(self):
        self.withdraw()
        if not self.tray_icon:
            image = self.create_icon_image()
            menu = (pystray.MenuItem('Show', self.show_window, default=True), pystray.MenuItem('Quit', self.quit_app))
            self.tray_icon = pystray.Icon("name", image, "PyDLNA", menu)
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
            
            # Show toast only once per session or always? Let's show it if supported
            # CTk doesn't have toast, but we can make a custom one or just rely on tray logic
            # Since pystray runs in thread, we can't easily pop UI from there without care.
            # We'll rely on the user finding the icon.
    
    def show_window(self, icon, item):
        self.tray_icon.stop()
        self.tray_icon = None
        # Schedule GUI update on main thread
        self.after(0, self.deiconify)

    def quit_app(self, icon, item):
        self.tray_icon.stop()
        os.kill(os.getpid(), signal.SIGTERM)

    def quit_fully(self):
        if messagebox.askyesno("Quit", "Completely exit PyDLNA?"):
             if self.tray_icon: self.tray_icon.stop()
             self.quit()
             os.kill(os.getpid(), signal.SIGTERM)

    def update_server_status(self):
        global server_instance
        if server_instance and not server_instance.should_exit:
            self.stop_btn.configure(text="Stop Server", fg_color="#ef4444", hover_color="#dc2626")
            self.link_label.configure(text=settings.base_url, text_color="#3b82f6")
            self.copy_btn.configure(state="normal")
        else:
            self.stop_btn.configure(text="Start Server", fg_color="#22c55e", hover_color="#15803d")
            self.link_label.configure(text="Server Stopped", text_color="#ef4444")
            self.copy_btn.configure(state="disabled")

    def update_path_list(self):
        for widget in self.path_frame.winfo_children():
            widget.destroy()
        
        for i, path in enumerate(settings.media_paths):
            row = ctk.CTkFrame(self.path_frame)
            row.pack(fill="x", padx=5, pady=2)
            lbl = ctk.CTkLabel(row, text=str(path), wraplength=400, justify="left")
            lbl.pack(side="left", padx=10, pady=5)
            del_btn = ctk.CTkButton(row, text="Remove", width=60, height=25, fg_color="#ef4444", hover_color="#dc2626", 
                                  command=lambda p=path: self.remove_directory(p))
            del_btn.pack(side="right", padx=10)

    def add_directory(self):
        dir_path = filedialog.askdirectory()
        self.lift()
        self.focus_force()
        if dir_path:
            current = [str(p) for p in settings.media_paths]
            if dir_path not in current:
                current.append(dir_path)
                update_media_paths(current)
                self.update_path_list()
                self.rescan()

    def remove_directory(self, path):
        current = [str(p) for p in settings.media_paths if str(p) != str(path)]
        update_media_paths(current)
        self.update_path_list()

    def rescan(self):
        scanner = MediaScanner(settings.media_paths)
        threading.Thread(target=lambda: asyncio.run(scanner.scan()), daemon=True).start()
    
    def copy_link(self):
        text = self.link_label.cget("text")
        if text != "Server Stopped":
            self.clipboard_clear()
            self.clipboard_append(text)
            
            # Flash feedback
            orig_color = self.copy_btn.cget("text_color")
            self.copy_btn.configure(text="✔️", text_color="#22c55e")
            self.after(1500, lambda: self.copy_btn.configure(text="📋", text_color=orig_color))
        
    def open_link(self):
        url = self.link_label.cget("text")
        if url and url != "Server Stopped":
            ip = settings.interface_ip or settings._get_local_ip()
            url = f"http://{ip}:{settings.port}"
            import webbrowser
            webbrowser.open(url)

    def set_password(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Set Credentials")
        dialog.geometry("300x250")
        dialog.attributes("-topmost", True)
        
        ctk.CTkLabel(dialog, text="Set Username & Password").pack(pady=10)
        
        user_entry = ctk.CTkEntry(dialog, placeholder_text="Username (default: admin)")
        user_entry.pack(pady=5, padx=20)
        if settings.username: user_entry.insert(0, settings.username)
        
        pass_entry = ctk.CTkEntry(dialog, placeholder_text="Password (leave empty to remove)", show="*")
        pass_entry.pack(pady=5, padx=20)
        if settings.password: pass_entry.insert(0, settings.password)
        
        def save():
            u = user_entry.get().strip() or "admin"
            p = pass_entry.get().strip()
            
            settings.username = u
            settings.password = p if p else None
            
            # Save to config file
            save_config(settings)
            
            self.status_label.configure(text=f"Credentials updated. User: {u}")
            dialog.destroy()
            
        ctk.CTkButton(dialog, text="Save", command=save).pack(pady=20)
    def clear_cache(self):
        if not messagebox.askyesno("Clear Cache / Reset DB", "This will WIPE the database and reset the schema. Proceed?"):
            return
            
        async def do_reset():
            from pydlna.db import engine
            from sqlmodel import SQLModel
            try:
                async with engine.begin() as conn:
                    await conn.run_sync(SQLModel.metadata.drop_all)
                    await conn.run_sync(SQLModel.metadata.create_all)
                self.after(0, lambda: messagebox.showinfo("Success", "Database reset! Please run a Rescan now."))
                self.update_server_status()
            except Exception as e:
                self.after(0, lambda: messagebox.showerror("Error", f"Failed to reset: {e}"))
        
        threading.Thread(target=lambda: asyncio.run(do_reset()), daemon=True).start()

    def toggle_server(self):
        global server_instance, server_thread
        
        if server_instance and not server_instance.should_exit:
            # Stop it
            server_instance.should_exit = True
            self.update_server_status()
        else:
            # Start it
            server_thread = threading.Thread(target=run_server, daemon=True)
            server_thread.start()
            self.after(1000, self.update_server_status)


def run_server():
    global server_instance
    try:
        logger.info("Importing web app...")
        try:
            from pydlna.web.server import app
        except ImportError:
            from web.server import app
            
        logger.info(f"Starting Uvicorn on {settings.host}:{settings.port}...")
        
        # We need a reference to the server to stop it
        # uvicorn.run doesn't return the server easily.
        # So we keep using Server but simplify the loop.
        
        config = uvicorn.Config(app, host=settings.host, port=settings.port, log_level="info", workers=1, log_config=None)
        server_instance = uvicorn.Server(config)
        
        # This is the most robust way to run uvicorn in a thread
        server_instance.run() 
        
    except Exception as e:
        logger.error(f"FATAL: Uvicorn server failed: {e}", exc_info=True)
        try:
            import tkinter.messagebox as mb
            mb.showerror("Server Error", f"Server failed to start:\n{e}")
        except:
            pass
        server_instance = None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="config.json", help="Path to config file")
    parser.add_argument("--port", type=int, help="Port to run on")
    parser.add_argument("--no-gui", action="store_true", help="Run without GUI")
    args = parser.parse_args()
    
    load_settings(args.config)
    if args.port:
        settings.port = args.port

    server_thread = threading.Thread(target=run_server, daemon=True)
    server_thread.start()

    try:
        if args.no_gui:
            logger.info("Running in headless mode...")
            try:
                while True:
                    server_thread.join(timeout=1.0)
            except KeyboardInterrupt:
                sys.exit(0)
        else:
            app = PyDLNAGUI()
            app.mainloop()
                    
    except Exception as e:
        logger.error(f"App failed: {e}")
        from tkinter import messagebox
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Error", f"Failed to start PyDLNA: {e}")

if __name__ == "__main__":
    main()
