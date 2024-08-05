import cv2
import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm


def extract_frames(video_path, output_folder, frame_rate=1, progress_var=None):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    vidcap = cv2.VideoCapture(video_path)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    success, image = vidcap.read()
    count = 0

    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000 / frame_rate))
        cv2.imwrite(os.path.join(output_folder, f"frame{count:05d}.jpg"), image)
        success, image = vidcap.read()
        count += 1

        if progress_var:
            progress_var.set((count / total_frames) * 100)

    vidcap.release()
    return count

def create_pdf_from_frames(frame_folder, pdf_path, frames_per_page=10, video_name="", total_frames=0, add_space=True, progress_var=None):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    margin = 2 * cm
    space_width = 1 * cm if add_space else 0
    image_width = (width - 2 * margin - space_width) / 2
    image_height = (height - 2 * margin) / 5

    frames = [f for f in os.listdir(frame_folder) if f.endswith('.jpg')]
    frames.sort()

    c.setFont("Helvetica", 14)
    c.drawString(margin, height - margin - 20, "Video to Flipbook Creator")
    c.drawString(margin, height - margin - 40, "Developed by Divesh Adivarekar")
    c.drawString(margin, height - margin - 60, "https://diveshadivarekar.github.io/")
    c.drawString(margin, height - margin - 100, f"Flipbook for Video: {video_name}")
    c.drawString(margin, height - margin - 140, f"Total Frames: {total_frames}")
    c.showPage()
    
    for i in range(0, len(frames), frames_per_page):
        for j in range(frames_per_page):
            if i + j < len(frames):
                frame_path = os.path.join(frame_folder, frames[i + j])
                x = margin + (j % 2) * (image_width + space_width)
                y = height - margin - (j // 2 + 1) * image_height
                c.drawImage(frame_path, x, y, image_width, image_height)

                text_x = x
                text_y = y + image_height - 15
                text = f"{i + j + 1}"
                
                text_width = c.stringWidth(text, "Helvetica", 10)
                text_height = 10
                
                circle_center_x = (text_x + text_width / 2) + 10
                circle_center_y = text_y - text_height / 2
                circle_radius = max(text_width, text_height) / 2 + 3
                
                c.setFillColorRGB(1, 1, 1)  
                c.circle(circle_center_x, circle_center_y, circle_radius, fill=1, stroke=0)
                
                c.setFillColorRGB(0, 0, 0)  
                c.setFont("Helvetica", 10)
                c.drawString(text_x + 10, text_y - 8, text)
                
                c.setDash(1, 2)
                c.rect(x - space_width, y, image_width + space_width, image_height)

        if progress_var:
            progress_var.set((i / len(frames)) * 100)
        c.showPage()
    
    c.save()

def delete_images(folder):
    for f in os.listdir(folder):
        if f.endswith('.jpg'):
            os.remove(os.path.join(folder, f))

def browse_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
    video_path_var.set(file_path)

def browse_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder_var.set(folder_path)

def generate_flipbook():
    video_path = video_path_var.get()
    video_file_name_without_ext = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = output_folder_var.get()
    frame_rate = int(frame_rate_var.get())
    frames_per_page = int(frames_per_page_var.get())
    add_space = add_space_var.get()
    pdf_path = os.path.join(output_folder, f"flipbook for [{video_file_name_without_ext}].pdf")
    
    if not video_path or not output_folder:
        messagebox.showerror("Error", "Please select both a video file and an output folder.")
        return

    progress_bar.grid()
    progress_var.set(0)
    root.update_idletasks()  
    total_frames = extract_frames(video_path, output_folder, frame_rate, progress_var=progress_var)
    create_pdf_from_frames(output_folder, pdf_path, frames_per_page, video_name=video_file_name_without_ext, total_frames=total_frames, add_space=add_space, progress_var=progress_var)

    delete_images(output_folder)
    
    progress_var.set(100)
    messagebox.showinfo("Success", f"Flipbook PDF created: {pdf_path}")

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# GUI
root = tk.Tk()
root.title("Video to Flipbook Creator")
root.resizable(False, False) 

try:
    icon_path = resource_path('icon.ico')
    root.iconbitmap(icon_path)
except Exception:
    pass

try:
    root.iconbitmap("assets/icon.ico")
except Exception:
    pass

video_path_var = tk.StringVar()
output_folder_var = tk.StringVar()
frame_rate_var = tk.StringVar(value="1")
frames_per_page_var = tk.StringVar(value="10")
add_space_var = tk.BooleanVar(value=True)

tk.Label(root, text="Video File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
tk.Entry(root, textvariable=video_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_video).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Output Folder (preferably empty folder):").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_output_folder).grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="Frame Rate (frames per second):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
tk.Entry(root, textvariable=frame_rate_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

tk.Label(root, text="Frames per Page  (Max 10):").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
tk.Spinbox(root, from_=1, to=10, textvariable=frames_per_page_var).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

tk.Checkbutton(root, text="Add space on left side of frames", variable=add_space_var).grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

generate_button = tk.Button(root, text="Generate Flipbook", command=generate_flipbook)
generate_button.grid(row=6, column=0, columnspan=3, pady=10)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
progress_bar.grid(row=4, column=0, columnspan=3, padx=5, pady=5)
progress_bar.grid_remove()

# Adding a tooltip
tooltip = ttk.Label(root, text="It may take time to create", background="yellow")
tooltip.grid_forget()

def show_tooltip(event):
    tooltip.grid(row=4, column=0, columnspan=3, pady=5)

def hide_tooltip(event):
    tooltip.grid_forget()

generate_button.bind("<Enter>", show_tooltip)
generate_button.bind("<Leave>", hide_tooltip)

root.mainloop()
