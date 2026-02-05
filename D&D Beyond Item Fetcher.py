import tkinter as tk
from tkinter import messagebox, scrolledtext, filedialog
import requests
from bs4 import BeautifulSoup
import threading
import time
import json
import os
import sys
import ctypes

# --- TASKBAR ICON FIX ---
try:
    myappid = 'mycompany.myproduct.subproduct.version' # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

CONFIG_FILE = "config.json"
DEFAULT_URLS = "https://www.dndbeyond.com/equipment\nhttps://www.dndbeyond.com/magic-items"

class DnDFetcherGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("D&D Beyond Item Fetcher")
        self.root.geometry("600x850")
        
        self.is_running = False
        self.default_path = os.path.join(os.getcwd(), "dnd_items_list.txt")

        # --- SET WINDOW ICON ---
        try:
            icon_file = resource_path("search.ico")
            self.root.iconbitmap(icon_file)
        except:
            pass 

        # --- Data Persistence ---
        self.saved_data = self.load_config()
        self.output_path = self.saved_data.get("output_file", self.default_path)

        # --- UI Layout ---
        tk.Label(root, text="D&D Beyond Data Fetcher", font=("Arial", 16, "bold"), fg="#2c3e50").pack(pady=10)
        
        # --- Authentication Section ---
        token_frame = tk.LabelFrame(root, text=" Authentication ", padx=10, pady=10)
        token_frame.pack(fill="x", padx=20, pady=5)

        tk.Label(token_frame, text="CobaltSession Token:", font=("Arial", 9, "bold")).pack(anchor="w")
        self.token_entry = tk.Entry(token_frame, width=60, show="*")
        self.token_entry.insert(0, self.saved_data.get("token", ""))
        self.token_entry.pack(pady=5)

        self.remember_var = tk.BooleanVar(value=self.saved_data.get("remember", False))
        tk.Checkbutton(token_frame, text="Remember Token locally", variable=self.remember_var).pack(anchor="w")
        
        tk.Button(token_frame, text="How to get your token?", command=self.show_help, 
                  fg="#3498db", cursor="hand2", bd=0, font=("Arial", 9, "underline")).pack(anchor="e")

        # --- Output Path Section ---
        path_frame = tk.LabelFrame(root, text=" Save Location ", padx=10, pady=10)
        path_frame.pack(fill="x", padx=20, pady=5)
        
        self.path_label = tk.Label(path_frame, text=f"File: {os.path.basename(self.output_path)}", fg="#7f8c8d", wraplength=400)
        self.path_label.pack(side="left", padx=5)
        tk.Button(path_frame, text="Browse...", command=self.browse_file).pack(side="right")

        # --- URL Section ---
        url_frame = tk.LabelFrame(root, text=" Target URLs (One per line) ", padx=10, pady=10)
        url_frame.pack(fill="x", padx=20, pady=5)

        self.url_text = scrolledtext.ScrolledText(url_frame, height=4, width=60, font=("Consolas", 9))
        self.url_text.pack(pady=5)
        self.url_text.insert(tk.END, self.saved_data.get("urls", DEFAULT_URLS))

        # --- Control Buttons ---
        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=10)

        self.start_btn = tk.Button(btn_frame, text="🚀 START", command=self.start_thread, 
                                   bg="#27ae60", fg="white", font=("Arial", 10, "bold"), width=10, height=2, cursor="hand2")
        self.start_btn.pack(side="left", padx=5)

        self.stop_btn = tk.Button(btn_frame, text="🛑 STOP", command=self.stop_fetching, 
                                  bg="#f39c12", fg="white", font=("Arial", 10, "bold"), width=10, height=2, state="disabled")
        self.stop_btn.pack(side="left", padx=5)

        tk.Button(btn_frame, text="🗑️ CLEAR LOG", command=self.clear_log, 
                  bg="#95a5a6", fg="white", font=("Arial", 10), width=10, height=2).pack(side="left", padx=5)

        tk.Button(btn_frame, text="🔄 RESET", command=self.reset_defaults, 
                  bg="#e74c3c", fg="white", font=("Arial", 10, "bold"), width=10, height=2).pack(side="left", padx=5)

        # --- Progress Log ---
        tk.Label(root, text="Activity Log:", font=("Arial", 9, "bold")).pack(anchor="w", padx=20)
        self.log_area = scrolledtext.ScrolledText(root, height=12, width=65, state='disabled', bg="#ecf0f1", font=("Consolas", 9))
        self.log_area.pack(padx=20, pady=5)

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r") as f: return json.load(f)
            except: return {}
        return {}

    def reset_defaults(self):
        if messagebox.askyesno("Reset", "Are you sure you want to reset all settings to default?"):
            if os.path.exists(CONFIG_FILE):
                os.remove(CONFIG_FILE)
            self.token_entry.delete(0, tk.END)
            self.remember_var.set(False)
            self.url_text.delete('1.0', tk.END)
            self.url_text.insert(tk.END, DEFAULT_URLS)
            self.output_path = self.default_path
            self.path_label.config(text=f"File: {os.path.basename(self.output_path)}")
            self.clear_log()
            self.log("All settings reset to default.")

    def browse_file(self):
        file = filedialog.asksaveasfilename(initialdir=os.path.dirname(self.output_path),
            defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file:
            self.output_path = file
            self.path_label.config(text=f"File: {os.path.basename(file)}")

    def clear_log(self):
        self.log_area.config(state='normal')
        self.log_area.delete('1.0', tk.END)
        self.log_area.config(state='disabled')

    def show_help(self):
        msg = ("1. Log in to D&D Beyond.\n2. F12 -> Application/Storage -> Cookies.\n"
               "3. Select dndbeyond.com.\n4. Copy 'CobaltSession' value.")
        messagebox.showinfo("Token Help", msg)

    def log(self, message):
        self.log_area.config(state='normal')
        self.log_area.insert(tk.END, f"[{time.strftime('%H:%M:%S')}] {message}\n")
        self.log_area.see(tk.END)
        self.log_area.config(state='disabled')

    def stop_fetching(self):
        self.is_running = False
        self.log("Stopping process... finalizing current page.")

    def start_thread(self):
        token = self.token_entry.get().strip()
        urls = self.url_text.get("1.0", tk.END).strip()
        if not token:
            messagebox.showwarning("Input Error", "Please provide a token.")
            return
        
        # Save config
        data = {"urls": urls, "remember": self.remember_var.get(), "output_file": self.output_path}
        data["token"] = token if self.remember_var.get() else ""
        with open(CONFIG_FILE, "w") as f: json.dump(data, f)

        self.is_running = True
        self.start_btn.config(state='disabled', bg="#bdc3c7")
        self.stop_btn.config(state='normal')
        threading.Thread(target=self.run_fetcher, args=(token, urls), daemon=True).start()

    def run_fetcher(self, token, urls_string):
        all_names = set()
        urls = [u.strip() for u in urls_string.split('\n') if u.strip()]
        headers = {"User-Agent": "Mozilla/5.0", "Cookie": f"CobaltSession={token}"}

        for base_url in urls:
            if not self.is_running: break
            page, last_page_items = 1, []
            self.log(f"Fetching: {base_url}")
            
            while self.is_running:
                try:
                    response = requests.get(f"{base_url}?page={page}", headers=headers)
                    if response.status_code != 200: break
                    soup = BeautifulSoup(response.text, 'html.parser')
                    tags = soup.select('a.link, span.list-row-name-primary')
                    names = [t.get_text(strip=True) for t in tags if t.get_text(strip=True)]
                    names = [n for n in names if n not in ["Next", "Previous", "View Details"]]
                    if not names or names == last_page_items: break
                    for name in names: all_names.add(name)
                    self.log(f"Page {page}: Scraped {len(names)} items.")
                    last_page_items = names
                    page += 1
                    time.sleep(1.2)
                except: break

        if all_names:
            with open(self.output_path, "w", encoding="utf-8") as f:
                for name in sorted(list(all_names)): f.write(f"{name}\n")
            self.log(f"DONE: Saved {len(all_names)} unique items.")
            if self.is_running:
                messagebox.showinfo("Success", f"Extraction complete!\nSaved to: {self.output_path}")
        
        self.start_btn.config(state='normal', bg="#27ae60")
        self.stop_btn.config(state='disabled')
        self.is_running = False

if __name__ == "__main__":
    root = tk.Tk()
    app = DnDFetcherGUI(root)

    root.mainloop()
