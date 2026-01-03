import os
import tkinter as tk
from tkinter import ttk, filedialog, scrolledtext
from PIL import Image, ImageTk
import pytesseract
from tkinter import messagebox


class MagnifyingGlass(tk.Toplevel):
    def __init__(self, parent, image_data, radius=100, zoom_factor=5):
        super().__init__(parent)
        self.overrideredirect(True)  # Remove window decorations
        self.parent = parent
        self.image_data = image_data
        self.radius = radius
        self.zoom_factor = zoom_factor
        
        # Create a canvas for the magnifying glass
        self.canvas = tk.Canvas(self, width=2*self.radius, height=2*self.radius, bg='white', highlightthickness=0)
        self.canvas.pack()
        
        # Hide initially
        self.withdraw()
        
    def update_magnifier(self, event):
        x, y = event.x, event.y
        img_x, img_y = self.image_data['label'].winfo_rootx(), self.image_data['label'].winfo_rooty()
        
        # Calculate coordinates relative to the image
        rel_x = x - img_x
        rel_y = y - img_y
        
        # Calculate coordinates for the magnified image
        zoomed_x = int(rel_x * self.zoom_factor)
        zoomed_y = int(rel_y * self.zoom_factor)
        
        # Ensure bounds within the image
        if zoomed_x < 0:
            zoomed_x = 0
        elif zoomed_x > self.image_data['label'].winfo_width():
            zoomed_x = self.image_data['label'].winfo_width()
        
        if zoomed_y < 0:
            zoomed_y = 0
        elif zoomed_y > self.image_data['label'].winfo_height():
            zoomed_y = self.image_data['label'].winfo_height()
        
        # Update magnifying glass image
        magnified_region = self.image_data['image'].crop((
            rel_x - self.radius // self.zoom_factor,
            rel_y - self.radius // self.zoom_factor,
            rel_x + self.radius // self.zoom_factor,
            rel_y + self.radius // self.zoom_factor
        ))
        magnified_region = magnified_region.resize((2*self.radius, 2*self.radius), Image.LANCZOS)
        self.magnified_image = ImageTk.PhotoImage(magnified_region)
        self.canvas.create_image(self.radius, self.radius, image=self.magnified_image)
        
        # Update position
        self.geometry(f"+{event.x_root + 20}+{event.y_root + 20}")
        
        # Show magnifying glass
        self.deiconify()

class CallimaqueApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Callimaque")
        
        # Maximize the window
        self.root.attributes('-zoomed', True)
        
        # File path
        self.file_path = tk.StringVar()
        # Directory path
        self.current_directory = tk.StringVar()
        
        # Create frames
        self.top_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.top_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.text_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.text_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.bottom_frame = tk.Frame(self.root, bd=2, relief=tk.SUNKEN)
        self.bottom_frame.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        
        # Centering top_frame and bottom_frame
        self.top_frame.grid_rowconfigure(1, weight=1)
        self.top_frame.grid_columnconfigure(0, weight=1)
        
        self.bottom_frame.grid_rowconfigure(0, weight=1)
        self.bottom_frame.grid_columnconfigure(0, weight=1)
        
        # Top frame widgets
        self.directory_label = ttk.Label(self.top_frame, text="Directory:")
        self.directory_label.grid(row=0, column=1, padx=10, pady=10, sticky=tk.E)
        
        self.directory_entry = ttk.Entry(self.top_frame, textvariable=self.current_directory, width=50)
        self.directory_entry.grid(row=0, column=2, padx=10, pady=10, sticky=tk.W)
        
        self.browse_button = ttk.Button(self.top_frame, text="Browse", command=self.browse_directory)
        self.browse_button.grid(row=0, column=3, padx=10, pady=10)
        
        self.image_data = {'label': tk.Label(self.top_frame), 'image': None, 'photo': None}
        self.image_data['label'].grid(row=1, column=0, columnspan=3, padx=10, pady=10, sticky=tk.NSEW)
        self.image_data['label'].bind("<Enter>", self.show_magnifier)
        self.image_data['label'].bind("<Leave>", self.hide_magnifier)
        self.image_data['label'].bind("<Motion>", self.move_magnifier)
        
        self.left_button = ttk.Button(self.top_frame, text="<", command=self.show_previous_image)
        self.left_button.grid(row=2, column=0, padx=10, pady=10)
        
        self.right_button = ttk.Button(self.top_frame, text=">", command=self.show_next_image)
        self.right_button.grid(row=2, column=1, padx=10, pady=10)
        




        # Bottom frame widgets (text editor)
        self.text_editor = scrolledtext.ScrolledText(self.text_frame, wrap=tk.WORD, width=80, height=20)
        self.text_editor.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.text_editor.bind("<Control-a>", self.select_all)
        self.text_editor.bind("<Control-A>", self.select_all) 
        
        self.button_append = ttk.Button(self.bottom_frame, text="Append", command=self.append_text)
        self.button_append.grid(row=1, column=0)

        self.destination_label = ttk.Label(self.bottom_frame, text="Destination:")
        self.destination_label.grid(row=1, column=0, padx=10, pady=10, sticky=tk.E)

        self.destination_entry = ttk.Entry(self.bottom_frame, textvariable=self.file_path, width=50)
        self.destination_entry.grid(row=1, column=1, padx=10, pady=10, sticky=tk.W)

        self.destination_button = ttk.Button(self.bottom_frame, text="Browse", command=self.browse_file)
        self.destination_button.grid(row=1, column=2, padx=10, pady=10)




        
        # Magnifying glass
        self.magnifier = None


    def browse_file(self):
        file_path = filedialog.askopenfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
             self.file_path.set(file_path)  
        
    def browse_directory(self):
        directory_path = filedialog.askdirectory()
        if directory_path:
            self.current_directory.set(directory_path)
            self.load_images(directory_path)
    
    def load_images(self, directory):
        self.image_files = []
        for filename in os.listdir(directory):
            if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif')):
                self.image_files.append(os.path.join(directory, filename))
        if self.image_files:
            self.current_image_index = 0
            self.show_image()
    
    def show_image(self):
        image_path = self.image_files[self.current_image_index]
        self.image_data['image'] = Image.open(image_path)
        



        #It is right here that the image agrandizing problem begins
        #each time you press < to show previous image or > to show the next the image gets bigger and bigger 
      
        # Calculate maximum display dimensions
        max_width = max(1, self.top_frame.winfo_width() - 20)  # Adjust for padding, ensure > 0
        max_height = max(1, self.top_frame.winfo_height() - 150)  # Adjust for other widgets, ensure > 0
        
        # Resize image while preserving aspect ratio
        width, height = self.image_data['image'].size
        display_image = self.image_data['image']
        
        if width > max_width or height > max_height:
            ratio = min(max_width / width, max_height / height)
            new_width = max(1, int(width * ratio))
            new_height = max(1, int(height * ratio))
            display_image = self.image_data['image'].resize((new_width, new_height), Image.LANCZOS)
        
        self.image_data['photo'] = ImageTk.PhotoImage(display_image)
        self.image_data['label'].configure(image=self.image_data['photo'])
        self.image_data['label'].image = self.image_data['photo']
        self.root.title(f"Callimaque - {os.path.basename(image_path)}")
        
        # Perform OCR on the image and update text editor
        extracted_text = self.perform_ocr(image_path)
        self.text_editor.delete(1.0, tk.END)
        self.text_editor.insert(tk.END, extracted_text)
    
    def perform_ocr(self, image_path):
        # Using pytesseract for OCR
        try:
            extracted_text = pytesseract.image_to_string(Image.open(image_path))
            return extracted_text
        except Exception as e:
            print(f"Error performing OCR: {e}")
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
        # Hide the cursor
        self.root.config(cursor='none')
        
        # Show magnifier at the cursor position
        if not self.magnifier:
            self.magnifier = MagnifyingGlass(self.root, self.image_data)
        self.magnifier.update_magnifier(event)
    
    def move_magnifier(self, event):
        # Update magnifier position
        if self.magnifier:
            self.magnifier.update_magnifier(event)
    
    def hide_magnifier(self, event):
        # Show the cursor
        self.root.config(cursor='')
        
        if self.magnifier:
            self.magnifier.withdraw()

    def append_text(self):
        text_to_append = self.text_editor.get("1.0", tk.END)
        if not text_to_append.strip():
            messagebox.showwarning("Error", "Text editor is empty!")
            return
        file_path = self.destination_entry.get()
        #file_path = filedialog.asksaveasfilename(defaultextension=".txt",
                                                 #filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not file_path:
            return  # User canceled save operation

        try:
            with open(file_path, 'a') as file:
                file.write(text_to_append.strip() + "\n")
            messagebox.showinfo("Success", "Text appended successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to append text to file:\n{str(e)}")


    def select_all(self, event=None):
        """Select all text in the Text widget."""
        self.text_editor.tag_add("sel", "1.0", "end-1c")  # Select from the first line to the last character
        return "break"  # Prevent default behavior


if __name__ == "__main__":
    root = tk.Tk()
    app = CallimaqueApp(root)
    root.mainloop()
