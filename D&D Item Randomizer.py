import customtkinter as ctk
import random
import os
import sys
from tkinter import filedialog

def get_resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class LootGenerator(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("D&D Pro Loot Tool")
        self.geometry("450x600")

        # --- SET THE WINDOW ICON ---
        try:
            icon_path = get_resource_path("logo.ico")
            self.after(200, lambda: self.iconbitmap(icon_path))
        except:
            pass 
        
        # Load the "baked" file automatically
        self.default_file = get_resource_path("dnd_items_list.txt")
        self.current_pool = self.load_items(self.default_file)

        # --- UI ELEMENTS ---
        self.label = ctk.CTkLabel(self, text="Dungeons & Dragons Randomizer Tool", font=("Helvetica", 24, "bold"))
        self.label.pack(pady=20)

        self.result_frame = ctk.CTkFrame(self, width=380, height=120, fg_color="#2b2b2b")
        self.result_frame.pack(pady=10)
        self.result_frame.pack_propagate(False) # Prevents frame from shrinking to text size

        self.result_label = ctk.CTkLabel(self.result_frame, text="Ready for random!", font=("Helvetica", 18), wraplength=350)
        self.result_label.place(relx=0.5, rely=0.5, anchor="center")

        self.roll_button = ctk.CTkButton(self, text="🎲 ROLL", command=self.roll_loot, height=45, font=("Helvetica", 16, "bold"))
        self.roll_button.pack(pady=15)

        self.file_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.file_frame.pack(pady=5)
        
        ctk.CTkButton(self.file_frame, text="📁 Import New", command=self.import_file, width=120).grid(row=0, column=0, padx=10)
        ctk.CTkButton(self.file_frame, text="🔄 Reset", command=self.reset_app, width=120, fg_color="#c62828").grid(row=0, column=1, padx=10)

        self.history_box = ctk.CTkTextbox(self, width=380, height=200)
        self.history_box.pack(pady=20)

    def load_items(self, path):
        if os.path.exists(path):
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    items = [line.strip() for line in f if line.strip()]
                    return items if items else ["(Empty File)"]
            except Exception as e:
                return [f"Error reading file: {e}"]
        return ["No items loaded. Please import a TXT file."]

    def roll_loot(self):
        if self.current_pool:
            item = random.choice(self.current_pool)
            self.result_label.configure(text=item, text_color="#FFD700")
            self.history_box.insert("0.0", f"• {item}\n")

    def import_file(self):
        path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
        if path:
            self.current_pool = self.load_items(path)
            self.result_label.configure(text=f"Loaded {len(self.current_pool)} items!", text_color="white")

    def reset_app(self):
        self.current_pool = self.load_items(self.default_file)
        self.history_box.delete("0.0", "end")
        self.result_label.configure(text="Reset to Default List", text_color="white")

if __name__ == "__main__":
    app = LootGenerator()

    app.mainloop()
