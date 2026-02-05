import customtkinter as ctk
import random
import os
import sys
from tkinter import filedialog, messagebox

# --- UTILITY FOR PYINSTALLER PATHS ---
def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class RandomizerPanel(ctk.CTkFrame):
    """A self-contained randomizer column."""
    def __init__(self, master, name, log_callback, remove_callback, **kwargs):
        super().__init__(master, width=240, height=290, corner_radius=10, **kwargs)
        self.name = name
        self.log_callback = log_callback
        self.remove_callback = remove_callback
        self.items = []
        
        self.pack_propagate(False)

        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", pady=(5, 5))
        
        self.name_label = ctk.CTkLabel(header_frame, text=self.name, font=("Helvetica", 13, "bold"))
        self.name_label.pack(side="left", padx=(10, 5))
        
        self.edit_btn = ctk.CTkButton(header_frame, text="✎", width=20, height=20, font=("Helvetica", 10), command=self.rename_panel)
        self.edit_btn.pack(side="left")

        # Close/Remove Button
        self.close_btn = ctk.CTkButton(header_frame, text="X", width=20, height=20, fg_color="#611212", hover_color="#c62828", command=lambda: self.remove_callback(self))
        self.close_btn.pack(side="right", padx=5)

        # --- Display Result ---
        self.result_frame = ctk.CTkFrame(self, height=55, fg_color="#1a1a1a")
        self.result_frame.pack(fill="x", padx=15, pady=5)
        self.result_frame.pack_propagate(False)
        
        self.result_label = ctk.CTkLabel(self.result_frame, text="---", font=("Helvetica", 11), wraplength=180)
        self.result_label.place(relx=0.5, rely=0.5, anchor="center")

        # --- Buttons ---
        self.roll_button = ctk.CTkButton(self, text="🎲 ROLL", command=self.roll, fg_color="#217346", hover_color="#1e633d", height=35)
        self.roll_button.pack(pady=5, fill="x", padx=15)
        
        self.import_btn = ctk.CTkButton(self, text="📁 Import TXT", command=self.import_file, height=28)
        self.import_btn.pack(pady=2, fill="x", padx=15)
        
        self.reset_btn = ctk.CTkButton(self, text="🔄 Reset", fg_color="#c62828", hover_color="#a52121", command=self.reset, height=28)
        self.reset_btn.pack(pady=2, fill="x", padx=15)

    def import_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.items = [line.strip() for line in f if line.strip()]
                self.result_label.configure(text=f"Loaded {len(self.items)} items", text_color="white")
            except Exception as e:
                messagebox.showerror("Error", f"Could not read file: {e}")

    def roll(self):
        if self.items:
            result = random.choice(self.items)
            self.result_label.configure(text=result, text_color="#FFD700")
            self.log_callback(f"{self.name}: {result}")
        else:
            self.result_label.configure(text="No file loaded", text_color="#e74c3c")

    def reset(self):
        self.items = []
        self.result_label.configure(text="Cleared", text_color="white")

    def rename_panel(self):
        dialog = ctk.CTkInputDialog(text="New Name:", title="Rename")
        new_name = dialog.get_input()
        if new_name:
            self.name = new_name
            self.name_label.configure(text=new_name)

class LootGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()

        # --- FIX FOR WINDOWS TASKBAR ICON ---
        if sys.platform == "win32":
            import ctypes
            # Sets a unique ID so Windows doesn't group this with the Python interpreter
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("dnd.randomizer.pro.v1")

        self.title("D&D Multi-Randomizer Pro")
        self.geometry("1200x650")

        # Set Window Icon
        try:
            icon_p = get_resource_path("search.ico")
            self.iconbitmap(icon_p)
        except:
            pass

        # --- Top Menu ---
        self.menu_frame = ctk.CTkFrame(self, height=40)
        self.menu_frame.pack(fill="x", side="top")
        
        self.file_menu_btn = ctk.CTkOptionMenu(
            self.menu_frame, 
            values=["New Panel", "Clear All Logs", "Remove All Panels"], 
            command=self.menu_callback,
            width=140
        )
        self.file_menu_btn.set("📁 File Menu")
        self.file_menu_btn.pack(side="left", padx=10, pady=5)

        self.panel_count_label = ctk.CTkLabel(self.menu_frame, text="Panels: 0/7", font=("Helvetica", 12, "bold"))
        self.panel_count_label.pack(side="right", padx=20)

        # --- Horizontal Scroll Area ---
        self.scroll_frame = ctk.CTkScrollableFrame(self, orientation="horizontal")
        self.scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.panels = []

        # --- Universal Log (Smallest) ---
        self.log_container = ctk.CTkFrame(self, height=130)
        self.log_container.pack(fill="x", side="bottom", padx=20, pady=(0, 15))
        self.log_container.pack_propagate(False)
        
        ctk.CTkLabel(self.log_container, text="Universal History Log", font=("Helvetica", 11, "bold")).pack(pady=2)
        self.history_box = ctk.CTkTextbox(self.log_container, font=("Consolas", 12))
        self.history_box.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Start with one default panel
        self.add_new_panel()

    def add_new_panel(self):
        if len(self.panels) < 7:
            name = f"Group {len(self.panels) + 1}"
            panel = RandomizerPanel(
                self.scroll_frame, 
                name=name, 
                log_callback=self.update_log,
                remove_callback=self.remove_panel
            )
            panel.pack(side="left", padx=10, pady=5)
            self.panels.append(panel)
            self.update_counter()
        else:
            messagebox.showwarning("Limit Reached", "Maximum of 7 panels allowed.")

    def remove_panel(self, panel_instance):
        panel_instance.destroy()
        self.panels.remove(panel_instance)
        self.update_counter()

    def update_counter(self):
        self.panel_count_label.configure(text=f"Panels: {len(self.panels)}/7")

    def menu_callback(self, choice):
        if choice == "New Panel":
            self.add_new_panel()
        elif choice == "Clear All Logs":
            self.history_box.delete("1.0", "end")
        elif choice == "Remove All Panels":
            if messagebox.askyesno("Confirm", "Are you sure you want to remove all panels?"):
                for p in self.panels[:]:
                    self.remove_panel(p)
        self.file_menu_btn.set("📁 File Menu")

    def update_log(self, message):
        self.history_box.insert("1.0", f"• {message}\n")

if __name__ == "__main__":
    app = LootGenerator()
    app.mainloop()