import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

def apply_lut_to_color(color, target_means, target_stds, source_means, source_stds):
    src_pixel = np.array([[color]], dtype=np.float32)
    color_lab = cv2.cvtColor((src_pixel * 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)[0,0]
    transferred = (color_lab - source_means) * (target_stds / (source_stds + 1e-6)) + target_means
    transferred = np.clip(transferred, 0, 255).astype(np.uint8)
    lab_pixel = transferred.reshape((1,1,3))
    transferred_rgb = cv2.cvtColor(lab_pixel, cv2.COLOR_LAB2RGB)[0,0] / 255.0
    return transferred_rgb

class LUTApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("VFXVerse Color Lab - Cinematic LAB LUT Generator with Preview")
        self.configure(bg="#1E1E1E")
        self.minsize(780, 620)
        self.resizable(True, True)

        self.target_path = None
        self.source_path = None
        self.output_dir = None
        self.LUT_SIZE = 17
        self.lut_data = None

        self.create_widgets()

        for i in range(4):
            self.grid_columnconfigure(i, weight=1)
        self.grid_rowconfigure(3, weight=1)

    def create_widgets(self):
        button_style = {
            "bg": "#008080",  # teal
            "fg": "white",
            "activebackground": "#FF6F00",  # orange
            "activeforeground": "white",
            "font": ("Segoe UI", 11, "bold"),
            "bd": 0,
            "relief": "flat",
            "cursor": "hand2",
            "padx": 10,
            "pady": 6,
        }

        label_style = {
            "bg": "#1E1E1E",
            "fg": "white",
            "font": ("Segoe UI", 10, "bold"),
            "anchor": "w",
        }

        # Buttons row
        self.target_btn = tk.Button(self, text="Select TARGET Image", command=self.select_target, **button_style)
        self.target_btn.grid(row=0, column=0, sticky="ew", padx=10, pady=(15,5))

        self.source_btn = tk.Button(self, text="Select SOURCE Image", command=self.select_source, **button_style)
        self.source_btn.grid(row=0, column=1, sticky="ew", padx=10, pady=(15,5))

        self.output_btn = tk.Button(self, text="Select OUTPUT Folder", command=self.select_output, **button_style)
        self.output_btn.grid(row=0, column=2, sticky="ew", padx=10, pady=(15,5))

        self.gen_button = tk.Button(self, text="Generate LUT & Preview", command=self.generate_and_preview,
                                    bg="#FF6F00", fg="white", font=("Segoe UI", 12, "bold"),
                                    activebackground="#FFB74D", activeforeground="white", bd=0, relief="flat", cursor="hand2")
        self.gen_button.grid(row=0, column=3, sticky="ew", padx=10, pady=(15,5))

        # Labels row
        self.target_label = tk.Label(self, text="No target image selected", **label_style)
        self.target_label.grid(row=1, column=0, sticky="ew", padx=10, pady=(0,5))

        self.source_label = tk.Label(self, text="No source image selected", **label_style)
        self.source_label.grid(row=1, column=1, sticky="ew", padx=10, pady=(0,5))

        self.output_label = tk.Label(self, text="No output folder selected", **label_style)
        self.output_label.grid(row=1, column=2, sticky="ew", padx=10, pady=(0,5))

        # Filename entry label and input
        self.filename_label = tk.Label(self, text="Output filename (.cube):", **label_style)
        self.filename_label.grid(row=2, column=0, sticky="e", padx=10, pady=(0,10))

        self.filename_entry = tk.Entry(self, font=("Segoe UI", 11))
        self.filename_entry.grid(row=2, column=1, sticky="ew", padx=10, pady=(0,10))
        self.filename_entry.insert(0, "vfxverse_color_lab_lut.cube")

        # Save LUT button
        self.save_button = tk.Button(self, text="Save LUT (.cube)", command=self.save_lut, state=tk.DISABLED,
                                     bg="#008080", fg="white", font=("Segoe UI", 12, "bold"),
                                     activebackground="#FF6F00", activeforeground="white", bd=0, relief="flat", cursor="hand2")
        self.save_button.grid(row=2, column=3, sticky="ew", padx=10, pady=(0,10))

        # Preview Canvas spanning all columns below
        canvas_frame = tk.Frame(self, bg="#121212", bd=3, relief="ridge")
        canvas_frame.grid(row=3, column=0, columnspan=4, sticky="nsew", padx=15, pady=(10,15))

        self.preview_canvas = tk.Canvas(canvas_frame, bg="black", highlightthickness=0)
        self.preview_canvas.pack(expand=True, fill="both", padx=5, pady=5)

    def select_target(self):
        path = filedialog.askopenfilename(title="Select Target Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path:
            self.target_path = path
            self.target_label.config(text=os.path.basename(path))

    def select_source(self):
        path = filedialog.askopenfilename(title="Select Source Image", filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if path:
            self.source_path = path
            self.source_label.config(text=os.path.basename(path))

    def select_output(self):
        path = filedialog.askdirectory(title="Select Output Folder for LUT")
        if path:
            self.output_dir = path
            self.output_label.config(text=path)

    def generate_and_preview(self):
        if not self.target_path or not self.source_path or not self.output_dir:
            messagebox.showerror("Missing Input", "Please select target image, source image, and output folder first.")
            return

        target_img = cv2.cvtColor(cv2.imread(self.target_path), cv2.COLOR_BGR2RGB) / 255.0
        source_img = cv2.cvtColor(cv2.imread(self.source_path), cv2.COLOR_BGR2RGB) / 255.0

        target_resized = cv2.resize(target_img, (source_img.shape[1], source_img.shape[0]))

        target_lab = cv2.cvtColor((target_resized * 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)
        source_lab = cv2.cvtColor((source_img * 255).astype(np.uint8), cv2.COLOR_RGB2LAB).astype(np.float32)

        self.target_means, self.target_stds = cv2.meanStdDev(target_lab)
        self.source_means, self.source_stds = cv2.meanStdDev(source_lab)

        self.target_means = self.target_means.flatten()
        self.target_stds = self.target_stds.flatten()
        self.source_means = self.source_means.flatten()
        self.source_stds = self.source_stds.flatten()

        # Generate LUT data
        lut_data = []
        for b in np.linspace(0, 1, self.LUT_SIZE):
            for g in np.linspace(0, 1, self.LUT_SIZE):
                for r in np.linspace(0, 1, self.LUT_SIZE):
                    color = [r, g, b]
                    transferred = apply_lut_to_color(color, self.target_means, self.target_stds, self.source_means, self.source_stds)
                    lut_data.append(transferred)
        self.lut_data = lut_data

        # Prepare preview image
        preview_img = cv2.resize(source_img, (700, 450))
        lut_size = self.LUT_SIZE

        # Prepare indices for LUT lookup
        indices_r = np.clip((preview_img[:, :, 0] * (lut_size - 1)).astype(int), 0, lut_size - 1)
        indices_g = np.clip((preview_img[:, :, 1] * (lut_size - 1)).astype(int), 0, lut_size - 1)
        indices_b = np.clip((preview_img[:, :, 2] * (lut_size - 1)).astype(int), 0, lut_size - 1)

        idx = indices_b * (lut_size ** 2) + indices_g * lut_size + indices_r

        lut_array = np.array(self.lut_data)

        h, w = preview_img.shape[:2]
        preview_img_out = lut_array[idx].reshape((h, w, 3))

        preview_img_out = np.clip(preview_img_out * 255, 0, 255).astype(np.uint8)
        preview_pil = Image.fromarray(preview_img_out)
        self.preview_tk = ImageTk.PhotoImage(preview_pil)
        self.preview_canvas.delete("all")
        self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=self.preview_tk)

        self.save_button.config(state=tk.NORMAL)

    def save_lut(self):
        if not self.lut_data or not self.output_dir:
            messagebox.showerror("Error", "No LUT generated or output folder missing.")
            return

        filename = self.filename_entry.get().strip()
        if not filename.endswith(".cube"):
            filename += ".cube"

        output_cube_path = os.path.join(self.output_dir, filename)

        try:
            with open(output_cube_path, 'w') as f:
                f.write(f"LUT_3D_SIZE {self.LUT_SIZE}\n")
                for color in self.lut_data:
                    f.write(f"{color[0]:.6f} {color[1]:.6f} {color[2]:.6f}\n")
            messagebox.showinfo("Saved", f"LUT saved successfully to:\n{output_cube_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save LUT:\n{e}")

def show_banner_then_start_app():
    splash = tk.Tk()
    splash.overrideredirect(True)  # No window borders
    splash.configure(bg='black')

    try:
        banner_img = Image.open("banner.png")
    except Exception as e:
        print("Banner image not found or failed to load:", e)
        splash.destroy()
        start_main_app()
        return

    banner_tk = ImageTk.PhotoImage(banner_img)

    screen_w = splash.winfo_screenwidth()
    screen_h = splash.winfo_screenheight()
    img_w, img_h = banner_img.size
    x = (screen_w - img_w) // 2
    y = (screen_h - img_h) // 2
    splash.geometry(f"{img_w}x{img_h}+{x}+{y}")

    label = tk.Label(splash, image=banner_tk, bg='black')
    label.pack()

    def close_splash():
        splash.destroy()
        start_main_app()

    splash.after(2000, close_splash)
    splash.mainloop()

def start_main_app():
    app = LUTApp()
    app.mainloop()

if __name__ == "__main__":
    try:
        import PIL
    except ImportError:
        print("Please install pillow package:\n pip install pillow")
        exit()

    show_banner_then_start_app()
