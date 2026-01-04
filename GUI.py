import os
import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
import customtkinter as ctk
from PIL import Image, ImageTk
import pytesseract
from ai_manager import AIManager

# Set the appearance mode and color theme
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")


class MagnifyingGlass(tk.Toplevel):
    def __init__(self, parent, image_data, radius=100, zoom_factor=5):
        super().__init__(parent)
        self.overrideredirect(True)
        self.parent = parent
        self.image_data = image_data
        self.radius = radius
        self.zoom_factor = zoom_factor
        
        self.canvas = tk.Canvas(self, width=2*self.radius, height=2*self.radius, bg='white', highlightthickness=0)
        self.canvas.pack()
        
        self.withdraw()
        
    def update_magnifier(self, event):
        if not self.image_data or not self.image_data.get('image'):
            return

        x, y = event.x, event.y
        img_x, img_y = self.image_data['label'].winfo_rootx(), self.image_data['label'].winfo_rooty()
        
        rel_x = x - img_x
        rel_y = y - img_y
        
        zoomed_x = int(rel_x * self.zoom_factor)
        zoomed_y = int(rel_y * self.zoom_factor)
        
        if zoomed_x < 0: zoomed_x = 0
        elif zoomed_x > self.image_data['label'].winfo_width(): zoomed_x = self.image_data['label'].winfo_width()
        
        if zoomed_y < 0: zoomed_y = 0
        elif zoomed_y > self.image_data['label'].winfo_height(): zoomed_y = self.image_data['label'].winfo_height()
        
        magnified_region = self.image_data['image'].crop((
            rel_x - self.radius // self.zoom_factor,
            rel_y - self.radius // self.zoom_factor,
            rel_x + self.radius // self.zoom_factor,
            rel_y + self.radius // self.zoom_factor
        ))
        magnified_region = magnified_region.resize((2*self.radius, 2*self.radius), Image.LANCZOS)
        self.magnified_image = ImageTk.PhotoImage(magnified_region)
        self.canvas.create_image(self.radius, self.radius, image=self.magnified_image)
        
        self.geometry(f"+{event.x_root + 20}+{event.y_root + 20}")
        self.deiconify()

class CallimaqueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Callimaque")
        
        self.ai_manager = AIManager()
        
        try:
             self.root.attributes('-zoomed', True)
        except:
             self.root.state('zoomed')
        
        self.file_path = tk.StringVar()
        self.current_directory = tk.StringVar()
        
        # --- Menu Bar ---
        self.menu_bar = tk.Menu(self.root)
        self.root.config(menu=self.menu_bar)
        
        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.file_menu.add_command(label="Open Text File...", command=self.open_text_file)
        self.file_menu.add_command(label="Save", command=self.save_file)
        self.file_menu.add_command(label="Save As...", command=self.save_as_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Preferences", command=self.open_preferences)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.root.quit)

        # --- Main Layout Configuration ---
        # Column 0: Text Editor (Left) - Flexible
        # Column 1: Controls (Right) - Fixed/Standard width
        self.root.grid_columnconfigure(0, weight=1) 
        self.root.grid_columnconfigure(1, weight=0)
        self.root.grid_rowconfigure(0, weight=1)

        # --- Left Frame (Text Editor) ---
        self.left_frame = ctk.CTkFrame(self.root)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        self.text_editor = ctk.CTkTextbox(self.left_frame, wrap=tk.WORD)
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_editor.bind("<Control-a>", self.select_all)
        self.text_editor.bind("<Control-A>", self.select_all)

        # --- Right Frame (Controls) ---
        self.right_frame = ctk.CTkFrame(self.root, width=500) # Set a default width preference
        self.right_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        # Prevent right frame from shrinking too much
        self.right_frame.grid_propagate(True)

        # 1. Directory Section
        self.dir_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.dir_container.pack(side=tk.TOP, fill=tk.X, padx=10, pady=(10, 5))
        
        ctk.CTkLabel(self.dir_container, text="Directory:").pack(anchor="w", padx=5)
        
        self.dir_input_frame = ctk.CTkFrame(self.dir_container, fg_color="transparent")
        self.dir_input_frame.pack(fill=tk.X, pady=2)
        
        self.directory_entry = ctk.CTkEntry(self.dir_input_frame, textvariable=self.current_directory)
        self.directory_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))
        
        self.browse_button = ctk.CTkButton(self.dir_input_frame, text="Browse", width=60, command=self.browse_directory)
        self.browse_button.pack(side=tk.LEFT, padx=5)

        # 2. Image Section
        self.image_data = {'label': ctk.CTkLabel(self.right_frame, text="No Image Loaded"), 'image': None, 'photo': None}
        self.image_data['label'].pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.image_data['label'].bind("<Enter>", self.show_magnifier)
        self.image_data['label'].bind("<Leave>", self.hide_magnifier)
        self.image_data['label'].bind("<Motion>", self.move_magnifier)

        # 3. Navigation Section
        self.nav_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.nav_container.pack(side=tk.TOP, pady=5)

        self.left_button = ctk.CTkButton(self.nav_container, text="<", command=self.show_previous_image, width=40)
        self.left_button.pack(side=tk.LEFT, padx=20)
        
        self.right_button = ctk.CTkButton(self.nav_container, text=">", command=self.show_next_image, width=40)
        self.right_button.pack(side=tk.LEFT, padx=20)

        # 4. AI Split Button Section
        self.ai_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.ai_container.pack(side=tk.TOP, pady=15)
        
        self.pill_color = "#D35400"
        self.hover_color = "#BA4A00"
        
        # Get parent background color
        parent_bg = self.right_frame.cget("fg_color")
        
        self.ai_pill_frame = ctk.CTkFrame(
            self.ai_container, 
            fg_color=self.pill_color, 
            corner_radius=25, 
            bg_color=parent_bg,
            border_width=0
        )
        self.ai_pill_frame.pack(side=tk.TOP)

        # AI Button Click Area
        self.ai_main_click_area = ctk.CTkFrame(
            self.ai_pill_frame,
            fg_color=self.pill_color, 
            corner_radius=16,
            width=140, 
            height=32,
            bg_color=self.pill_color 
        )
        self.ai_main_click_area.pack(side=tk.LEFT, padx=(15, 0), pady=4)
        
        # Label 1: "Ai Correction"
        self.ai_title_label = ctk.CTkLabel(
            self.ai_main_click_area,
            text="Ai Correction",
            font=("Roboto", 13, "bold"),
            text_color="white",
            fg_color="transparent"
        )
        self.ai_title_label.pack(side=tk.TOP, pady=0) 

        # Label 2: Selected Model
        self.ai_subtitle_label = ctk.CTkLabel(
            self.ai_main_click_area,
            text=self.ai_manager.current_model_name,
            font=("Roboto", 10),
            text_color="#E0E0E0", 
            fg_color="transparent"
        )
        self.ai_subtitle_label.pack(side=tk.TOP, pady=0)

        # Bind events
        for widget in [self.ai_main_click_area, self.ai_title_label, self.ai_subtitle_label]:
            widget.bind("<Button-1>", lambda e: self.perform_ai_correction())
            widget.bind("<Enter>", self.on_ai_hover_enter)
            widget.bind("<Leave>", self.on_ai_hover_leave)

        # AI Separator
        self.ai_separator = ctk.CTkFrame(self.ai_pill_frame, width=1, height=18, fg_color="#E59866", bg_color=self.pill_color) 
        self.ai_separator.pack(side=tk.LEFT, padx=5, pady=6)
        
        # AI Menu Button
        self.ai_btn_menu = ctk.CTkButton(
            self.ai_pill_frame, 
            text=">", 
            fg_color="transparent", 
            hover_color=self.hover_color,
            width=32,
            height=32,
            corner_radius=16,
            bg_color=self.pill_color, 
            border_width=0,
            command=self.toggle_ai_menu
        )
        self.ai_btn_menu.pack(side=tk.LEFT, padx=(0, 15), pady=4)

        # AI Settings Panel (Hidden)
        self.ai_settings_panel = ctk.CTkFrame(self.right_frame, fg_color="#2B2B2B", corner_radius=15, border_width=1, border_color="#404040")
        
        self.ai_model_var = tk.StringVar(value=self.ai_manager.current_model_name)
        
        ctk.CTkLabel(self.ai_settings_panel, text="AI Models", font=("Roboto", 14, "bold"), text_color="white").pack(anchor="w", padx=20, pady=(15, 10))
        
        self.models_frame = ctk.CTkFrame(self.ai_settings_panel, fg_color="transparent")
        self.models_frame.pack(fill="x", padx=10)
        
        for model in self.ai_manager.get_available_models():
            rb = ctk.CTkRadioButton(
                self.models_frame, 
                text=model, 
                variable=self.ai_model_var, 
                value=model,
                command=self.on_model_select,
                text_color="#DDDDDD",
                hover_color="#D35400",
                fg_color="#D35400"
            )
            rb.pack(anchor="w", padx=10, pady=5)
            
        ctk.CTkLabel(self.ai_settings_panel, text="API Key:", text_color="gray").pack(anchor="w", padx=20, pady=(10, 0))
        self.api_key_entry = ctk.CTkEntry(self.ai_settings_panel, width=250, show="*")
        self.api_key_entry.pack(fill="x", padx=20, pady=(5, 15))
        self.api_key_entry.bind("<KeyRelease>", self.save_api_key)
        
        current_key = self.ai_manager.api_keys.get(self.ai_manager.current_model_name, "")
        self.api_key_entry.insert(0, current_key)


        # 5. Append/Destination Section (Bottom of Right Frame)
        self.bottom_container = ctk.CTkFrame(self.right_frame, fg_color="transparent")
        self.bottom_container.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=20)

        ctk.CTkLabel(self.bottom_container, text="Destination File:").pack(anchor="w", padx=5)

        self.dest_input_frame = ctk.CTkFrame(self.bottom_container, fg_color="transparent")
        self.dest_input_frame.pack(fill=tk.X, pady=2)

        self.destination_entry = ctk.CTkEntry(self.dest_input_frame, textvariable=self.file_path)
        self.destination_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 5))

        self.destination_button = ctk.CTkButton(self.dest_input_frame, text="Browse", width=60, command=self.browse_destination_file)
        self.destination_button.pack(side=tk.LEFT, padx=5)
        
        self.button_append = ctk.CTkButton(self.bottom_container, text="Append Text", command=self.append_text)
        self.button_append.pack(side=tk.TOP, fill=tk.X, padx=5, pady=10)

        self.magnifier = None

    # --- Menu Functions ---
    def open_text_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    self.text_editor.delete("1.0", tk.END)
                    self.text_editor.insert(tk.END, content)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to open file: {e}")

    def save_file(self):
        # Implementation depends on whether we have an "opened" text file or just appending
        # For this logic, we'll save the editor content to a new file if not specified
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
             try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.text_editor.get("1.0", tk.END))
                messagebox.showinfo("Success", "File saved.")
             except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {e}")

    def save_as_file(self):
        self.save_file()

    def open_preferences(self):
        messagebox.showinfo("Preferences", "Preferences window placeholder.")

    # --- AI UI Interaction ---
    def on_ai_hover_enter(self, event):
        self.ai_main_click_area.configure(fg_color=self.hover_color)
    
    def on_ai_hover_leave(self, event):
        self.ai_main_click_area.configure(fg_color=self.pill_color)

    # --- AI Panel Logic ---
    def toggle_ai_menu(self):
        if self.ai_settings_panel.winfo_ismapped():
            self.ai_settings_panel.pack_forget()
        else:
            self.ai_settings_panel.pack(after=self.ai_container, pady=5, padx=10, fill='x')
            
            self.api_key_entry.delete(0, tk.END)
            key = self.ai_manager.api_keys.get(self.ai_manager.current_model_name, "")
            self.api_key_entry.insert(0, key)

    def on_model_select(self):
        new_model = self.ai_model_var.get()
        self.ai_manager.set_model(new_model)
        self.ai_subtitle_label.configure(text=new_model)
        self.api_key_entry.delete(0, tk.END)
        key = self.ai_manager.api_keys.get(new_model, "")
        self.api_key_entry.insert(0, key)

    def save_api_key(self, event=None):
        key = self.api_key_entry.get()
        self.ai_manager.set_api_key(self.ai_manager.current_model_name, key)

    def perform_ai_correction(self):
        current_model = self.ai_manager.current_model_name
        if "Gemini" in current_model and not self.ai_manager.api_keys.get(current_model):
            if not self.ai_settings_panel.winfo_ismapped():
                self.toggle_ai_menu()
            self.api_key_entry.focus_set()
            messagebox.showinfo("API Key Needed", "Please enter your API Key in the settings panel.")
            return

        original_text = self.text_editor.get("1.0", tk.END)
        if not original_text.strip():
             messagebox.showwarning("Warning", "No text to correct.")
             return

        self.root.config(cursor="watch")
        self.root.update()
        corrected_text = self.ai_manager.correct_text(original_text)
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, corrected_text)
        self.root.config(cursor="")

    # --- Existing Functionality ---
    def browse_destination_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path: self.file_path.set(file_path)  
        
    def browse_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.current_directory.set(directory_path)
            self.load_images(directory_path)
    
    def load_images(self, directory):
        self.image_files = []
        try:
            for filename in os.listdir(directory):
                if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                    self.image_files.append(os.path.join(directory, filename))
            print(f"Loaded {len(self.image_files)} images.")
        except Exception as e:
            print(f"Error loading images: {e}")

        if self.image_files:
            self.current_image_index = 0
            self.show_image()
    
    def show_image(self):
        image_path = self.image_files[self.current_image_index]
        self.image_data['image'] = Image.open(image_path)
        
        # Adjust sizing calculations for right frame width
        max_width = max(1, self.right_frame.winfo_width() - 20)
        if max_width < 100: max_width = 400 # Default fallback if not drawn yet
        
        max_height = 400 # Fixed height max for image in control panel to avoid pushing everything off
        
        width, height = self.image_data['image'].size
        new_width, new_height = width, height

        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = max(1, int(width * ratio))
            new_height = max(1, int(height * ratio))
        
        self.image_data['photo'] = ctk.CTkImage(light_image=self.image_data['image'], 
                                              dark_image=self.image_data['image'],
                                              size=(new_width, new_height))
        
        self.image_data['label'].configure(image=self.image_data['photo'], text="")
        self.root.title(f"Callimaque - {os.path.basename(image_path)}")
        
        extracted_text = self.perform_ocr(image_path)
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert(tk.END, extracted_text)
    
    def perform_ocr(self, image_path):
        try:
            return pytesseract.image_to_string(Image.open(image_path))
        except Exception as e:
            print(f"Error: {e}")
            return ""
    
    def show_previous_image(self):
        if self.image_files:
            self.current_image_index = (self.current_image_index - 1) % len(self.image_files)
            self.show_image()
    
    def show_next_image(self):
        if self.image_files:
            self.current_image_index = (self.current_image_index + 1) % len(self.image_files)
            self.show_image()
    
    def show_magnifier(self, event):
        if not self.image_data or not self.image_data.get('image'): return
        self.root.config(cursor='none')
        if not self.magnifier: self.magnifier = MagnifyingGlass(self.root, self.image_data)
        self.magnifier.update_magnifier(event)
    
    def move_magnifier(self, event):
        if self.magnifier: self.magnifier.update_magnifier(event)
    
    def hide_magnifier(self, event):
        self.root.config(cursor='')
        if self.magnifier: self.magnifier.withdraw()

    def append_text(self):
        text_to_append = self.text_editor.get("1.0", tk.END)
        if not text_to_append.strip():
            messagebox.showwarning("Error", "Empty text!")
            return
        file_path = self.destination_entry.get()
        if not file_path: return
        try:
            with open(file_path, 'a') as file: file.write(text_to_append.strip() + "\n")
            messagebox.showinfo("Success", "Appended!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed: {e}")

    def select_all(self, event=None):
        self.text_editor.tag_add("sel", "1.0", "end-1c")
        return "break"


if __name__ == "__main__":
    root = ctk.CTk()
    app = CallimaqueApp(root)
    root.mainloop()