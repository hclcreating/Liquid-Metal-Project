import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk
import pillow_heif

# Register HEIF opener with Pillow
pillow_heif.register_heif_opener()

class ImageProcessor:
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # Hide main window
        self.crop_coords = None
        self.start_x = None
        self.start_y = None
        self.rect = None

    def select_folder(self):
        folder_selected = filedialog.askdirectory(title="Select Folder containing HEIC photos")
        return folder_selected

    def get_crop_area(self, image_path):
        """Opens a window to let the user draw a crop rectangle."""
        crop_win = tk.Toplevel()
        crop_win.title("Select Crop Area and Press Enter")
        
        img = Image.open(image_path)
        # Resize for display if the image is too large for the screen
        screen_width = self.root.winfo_screenwidth() * 0.8
        screen_height = self.root.winfo_screenheight() * 0.8
        
        scale = min(screen_width/img.width, screen_height/img.height, 1.0)
        display_size = (int(img.width * scale), int(img.height * scale))
        img_display = img.resize(display_size, Image.LANCZOS)
        
        tk_img = ImageTk.PhotoImage(img_display)
        canvas = tk.Canvas(crop_win, width=display_size[0], height=display_size[1])
        canvas.pack()
        canvas.create_image(0, 0, anchor="nw", image=tk_img)

        def on_button_press(event):
            self.start_x = event.x
            self.start_y = event.y
            self.rect = canvas.create_rectangle(self.start_x, self.start_y, 1, 1, outline='red', width=2)

        def on_move_press(event):
            canvas.coords(self.rect, self.start_x, self.start_y, event.x, event.y)

        def on_button_release(event):
            # Calculate coordinates relative to original image size
            x1, y1, x2, y2 = canvas.coords(self.rect)
            self.crop_coords = (
                int(min(x1, x2) / scale),
                int(min(y1, y2) / scale),
                int(max(x1, x2) / scale),
                int(max(y1, y2) / scale)
            )

        def finish(event):
            crop_win.destroy()

        canvas.bind("<ButtonPress-1>", on_button_press)
        canvas.bind("<B1-Motion>", on_move_press)
        canvas.bind("<ButtonRelease-1>", on_button_release)
        crop_win.bind("<Return>", finish)
        
        crop_win.wait_window()
        return self.crop_coords

    def process_images(self):
        source_folder = self.select_folder()
        if not source_folder:
            return

        # Setup output directory
        folder_name = os.path.basename(source_folder)
        output_folder = os.path.join(source_folder, f"{folder_name}_crop")
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)

        files = [f for f in os.listdir(source_folder) if f.lower().endswith(('.heic', '.heif'))]
        if not files:
            messagebox.showwarning("No Files", "No HEIC files found in the selected folder.")
            return

        # 1. Convert first image and get crop area
        first_heic_path = os.path.join(source_folder, files[0])
        crop_area = self.get_crop_area(first_heic_path)

        if not crop_area:
            messagebox.showwarning("Cancelled", "No crop area selected.")
            return

        # 2. Process all images
        for filename in files:
            print(f"Processing {filename}...")
            file_path = os.path.join(source_folder, filename)
            
            # Load and convert to RGB (JPEG requirement)
            heif_file = pillow_heif.read_heif(file_path)
            img = Image.frombytes(
                heif_file.mode, 
                heif_file.size, 
                heif_file.data, 
                "raw", 
                heif_file.mode, 
                heif_file.stride,
            )
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Crop
            cropped_img = img.crop(crop_area)
            
            # Save
            base_name = os.path.splitext(filename)[0]
            save_path = os.path.join(output_folder, f"{base_name}_crop.jpg")
            cropped_img.save(save_path, "JPEG", quality=95)

        messagebox.showinfo("Success", f"Processed {len(files)} images to:\n{output_folder}")

if __name__ == "__main__":
    app = ImageProcessor()
    app.process_images()