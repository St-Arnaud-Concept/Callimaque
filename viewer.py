import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import os

import ocr


class CallimaqueApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Callimaque")
        self.geometry("600x400")  # Initial size, will be adjusted later
        self.minsize(300, 200)  # Minimum size to prevent too small windows
        self.maxsize(self.winfo_screenwidth() // 2, self.winfo_screenheight())  # Max size is half the screen height

        self.setup_ui()

    def setup_ui(self):
        # Button to open a folder
        self.open_button = tk.Button(self, text="Open", command=self.open_folder)
        self.open_button.pack()

        # Image viewer
        self.image_label = tk.Label(self)
        self.image_label.pack(expand=True, fill=tk.BOTH)

        # Buttons for rotating
        self.rotate_left_button = tk.Button(self, text="←", command=self.rotate_left)
        self.rotate_left_button.pack(side=tk.LEFT)
        self.rotate_right_button = tk.Button(self, text="→", command=self.rotate_right)
        self.rotate_right_button.pack(side=tk.RIGHT)

        # Button to cut
        self.cut_button = tk.Button(self, text="Cut", command=self.cut)
        self.cut_button.pack()

    def open_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            image_files = [f for f in os.listdir(folder_path) if f.endswith(('.jpeg', '.jpg'))]
            if image_files:
                image_path = os.path.join(folder_path, image_files[0])
                self.show_image(image_path)

    def show_image(self, image_path):
        image = Image.open(image_path)
        # Resize image to fit in the viewer
        width, height = self.image_label.winfo_width(), self.image_label.winfo_height()
        image.thumbnail((width, height), Image.ANTIALIAS)
        photo = ImageTk.PhotoImage(image)
        self.image_label.config(image=photo)
        self.image_label.image = photo

    def rotate_left(self):
    # Rotate the image 90 degrees counter-clockwise
    image = self.image_label.image
    if image:
        rotated_image = image.rotate(90)
        self.image_label.config(image=rotated_image)
        self.image_label.image = rotated_image

    def rotate_right(self):
    # Rotate the image 90 degrees clockwise
        image = self.image_label.image
        if image:
           rotated_image = image.rotate(-90)
           self.image_label.config(image=rotated_image)
           self.image_label.image = rotated_image

    def cut(self):
    # Example cropping function, you may want to adjust the coordinates
        image = self.image_label.image
        if image:
            cropped_image = image.crop((100, 100, 300, 300))  # Example coordinates (x1, y1, x2, y2)
            self.image_label.config(image=cropped_image)
            self.image_label.image = cropped_image


if __name__ == "__main__":
    app = CallimaqueApp()
    app.mainloop()

