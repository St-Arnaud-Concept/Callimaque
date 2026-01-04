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
        
        # --- Main Layout Frames ---
        self.top_frame = ctk.CTkFrame(self.root)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.text_frame = ctk.CTkFrame(self.root)
        self.text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.bottom_frame = ctk.CTkFrame(self.root)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.X, expand=False, padx=10, pady=5)
        
        # --- Top Frame Widgets ---
        
        # Directory
        self.dir_container = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.dir_container.pack(side=tk.TOP, fill=tk.X, pady=10)
        
        self.dir_inner = ctk.CTkFrame(self.dir_container, fg_color="transparent")
        self.dir_inner.pack(side=tk.TOP, expand=True)

        self.directory_label = ctk.CTkLabel(self.dir_inner, text="Directory:")
        self.directory_label.pack(side=tk.LEFT, padx=5)
        
        self.directory_entry = ctk.CTkEntry(self.dir_inner, textvariable=self.current_directory, width=400)
        self.directory_entry.pack(side=tk.LEFT, padx=5)
        
        self.browse_button = ctk.CTkButton(self.dir_inner, text="Browse", command=self.browse_directory)
        self.browse_button.pack(side=tk.LEFT, padx=5)
        
        # Image
        self.image_data = {'label': ctk.CTkLabel(self.top_frame, text=""), 'image': None, 'photo': None}
        self.image_data['label'].pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.image_data['label'].bind("<Enter>", self.show_magnifier)
        self.image_data['label'].bind("<Leave>", self.hide_magnifier)
        self.image_data['label'].bind("<Motion>", self.move_magnifier)
        
        # Navigation
        self.nav_container = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.nav_container.pack(side=tk.TOP, pady=5)

        self.left_button = ctk.CTkButton(self.nav_container, text="<", command=self.show_previous_image, width=40)
        self.left_button.pack(side=tk.LEFT, padx=20)
        
        self.right_button = ctk.CTkButton(self.nav_container, text=">", command=self.show_next_image, width=40)
        self.right_button.pack(side=tk.LEFT, padx=20)
        
        # --- AI Split Button ---
        self.ai_container = ctk.CTkFrame(self.top_frame, fg_color="transparent")
        self.ai_container.pack(side=tk.TOP, pady=10)
        
        pill_color = "#D35400"
        hover_color = "#BA4A00"
        
        # Get parent background color to ensure rounded corners blend perfectly
        # Default CTkFrame color is usually a tuple for light/dark mode
        parent_bg = self.top_frame.cget("fg_color")
        
        # Main Pill Frame
        self.ai_pill_frame = ctk.CTkFrame(
            self.ai_container, 
            fg_color=pill_color, 
            corner_radius=25, 
            bg_color=parent_bg,
            border_width=0
        )
        self.ai_pill_frame.pack(side=tk.TOP)

        # Buttons are downsized and padded to float safely inside the rounded container
        self.ai_btn_main = ctk.CTkButton(
            self.ai_pill_frame, 
            text="Ai Correction", 
            fg_color="transparent", 
            hover_color=hover_color,
            width=100,
            height=32,
            corner_radius=16,
            bg_color=pill_color, # Blends with container
            border_width=0,
            command=self.perform_ai_correction
        )
        self.ai_btn_main.pack(side=tk.LEFT, padx=(15, 0), pady=4)
        
        # Separator (Vertical line)
        self.ai_separator = ctk.CTkFrame(self.ai_pill_frame, width=1, height=18, fg_color="#E59866", bg_color=pill_color) 
        self.ai_separator.pack(side=tk.LEFT, padx=5, pady=6)
        
        self.ai_btn_menu = ctk.CTkButton(
            self.ai_pill_frame, 
            text=">", 
            fg_color="transparent", 
            hover_color=hover_color,
            width=32,
            height=32,
            corner_radius=16,
            bg_color=pill_color, # Blends with container
            border_width=0,
            command=self.toggle_ai_menu
        )
        self.ai_btn_menu.pack(side=tk.LEFT, padx=(0, 15), pady=4)

        # --- AI Settings Panel (Hidden by default) ---
        # Styled like a dark dropdown card
        self.ai_settings_panel = ctk.CTkFrame(self.top_frame, fg_color="#2B2B2B", corner_radius=15, border_width=1, border_color="#404040")
        # We don't pack it yet.
        
        # Panel Content
        self.ai_model_var = tk.StringVar(value=self.ai_manager.current_model_name)
        
        # Title
        panel_header = ctk.CTkLabel(self.ai_settings_panel, text="AI Models", font=("Roboto", 14, "bold"), text_color="white")
        panel_header.pack(anchor="w", padx=20, pady=(15, 10))
        
        # List of Radio Buttons
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
            
        # API Key Section
        ctk.CTkLabel(self.ai_settings_panel, text="API Key:", text_color="gray").pack(anchor="w", padx=20, pady=(10, 0))
        self.api_key_entry = ctk.CTkEntry(self.ai_settings_panel, width=250, show="*")
        self.api_key_entry.pack(fill="x", padx=20, pady=(5, 15))
        self.api_key_entry.bind("<KeyRelease>", self.save_api_key) # Auto-save on type
        
        # Initial Key Load
        current_key = self.ai_manager.api_keys.get(self.ai_manager.current_model_name, "")
        self.api_key_entry.insert(0, current_key)


        # --- Text Frame Widgets ---
        self.text_editor = ctk.CTkTextbox(self.text_frame, wrap=tk.WORD, width=600, height=300)
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.text_editor.bind("<Control-a>", self.select_all)
        self.text_editor.bind("<Control-A>", self.select_all)
        
        # --- Bottom Frame Widgets ---
        self.bottom_container = ctk.CTkFrame(self.bottom_frame, fg_color="transparent")
        self.bottom_container.pack(side=tk.TOP, pady=10)

        self.button_append = ctk.CTkButton(self.bottom_container, text="Append", command=self.append_text)
        self.button_append.pack(side=tk.LEFT, padx=10)

        self.destination_label = ctk.CTkLabel(self.bottom_container, text="Destination:")
        self.destination_label.pack(side=tk.LEFT, padx=5)

        self.destination_entry = ctk.CTkEntry(self.bottom_container, textvariable=self.file_path, width=400)
        self.destination_entry.pack(side=tk.LEFT, padx=5)

        self.destination_button = ctk.CTkButton(self.bottom_container, text="Browse", command=self.browse_file)
        self.destination_button.pack(side=tk.LEFT, padx=5)

        self.magnifier = None

    # --- AI Panel Logic ---
    def toggle_ai_menu(self):
        if self.ai_settings_panel.winfo_ismapped():
            self.ai_settings_panel.pack_forget()
        else:
            # Show panel directly below the AI container
            self.ai_settings_panel.pack(after=self.ai_container, pady=5, padx=50) # Use fill/padx if needed
            
            # Refresh Key Entry for current model
            self.api_key_entry.delete(0, tk.END)
            key = self.ai_manager.api_keys.get(self.ai_manager.current_model_name, "")
            self.api_key_entry.insert(0, key)

    def on_model_select(self):
        new_model = self.ai_model_var.get()
        self.ai_manager.set_model(new_model)
        # Update Key Entry
        self.api_key_entry.delete(0, tk.END)
        key = self.ai_manager.api_keys.get(new_model, "")
        self.api_key_entry.insert(0, key)

    def save_api_key(self, event=None):
        key = self.api_key_entry.get()
        self.ai_manager.set_api_key(self.ai_manager.current_model_name, key)

    def perform_ai_correction(self):
        current_model = self.ai_manager.current_model_name
        
        # Check for key
        if "Gemini" in current_model and not self.ai_manager.api_keys.get(current_model):
            # Open the menu to prompt user
            if not self.ai_settings_panel.winfo_ismapped():
                self.toggle_ai_menu()
            self.api_key_entry.focus_set()
            messagebox.showinfo("API Key Needed", "Please enter your API Key in the settings panel below.")
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
    def browse_file(self):
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
        
        max_width = max(1, self.top_frame.winfo_width() - 20)
        max_height = max(1, self.top_frame.winfo_height() - 250) # Adjusted for panel
        
        width, height = self.image_data['image'].size
        new_width, new_height = width, height

        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = max(1, int(width * ratio))
            new_height = max(1, int(height * ratio))
        
        self.image_data['photo'] = ctk.CTkImage(light_image=self.image_data['image'], 
                                              dark_image=self.image_data['image'],
                                              size=(new_width, new_height))
        
        self.image_data['label'].configure(image=self.image_data['photo'])
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