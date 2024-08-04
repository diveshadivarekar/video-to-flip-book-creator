import cv2
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm

def extract_frames(video_path, output_folder, frame_rate=1):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    vidcap = cv2.VideoCapture(video_path)
    success, image = vidcap.read()
    count = 0

    while success:
        vidcap.set(cv2.CAP_PROP_POS_MSEC, (count*1000/frame_rate))
        cv2.imwrite(os.path.join(output_folder, f"frame{count:05d}.jpg"), image)
        success, image = vidcap.read()
        count += 1

    vidcap.release()
    print(f"Extracted {count} frames.")
    return count

def create_pdf_from_frames(frame_folder, pdf_path, frames_per_page=10, video_name="", total_frames=0):
    c = canvas.Canvas(pdf_path, pagesize=A4)
    width, height = A4
    margin = 2 * cm
    image_width = (width - 2 * margin) / 2
    image_height = (height - 2 * margin) / 5

    frames = [f for f in os.listdir(frame_folder) if f.endswith('.jpg')]
    frames.sort()

    # First page with details
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
                x = margin + (j % 2) * image_width
                y = height - margin - (j // 2 + 1) * image_height
                c.drawImage(frame_path, x, y, image_width, image_height)
                c.setFont("Helvetica", 10)
                c.drawString(x, y + image_height + 5, f"Frame: {i + j + 1}")
                c.setDash(1, 2)
                c.rect(x, y, image_width, image_height)
        c.showPage()
    
    c.save()
    print(f"PDF saved as {pdf_path}")

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
    pdf_path = os.path.join(output_folder, f"flipbook for [{video_file_name_without_ext}].pdf")
    
    if not video_path or not output_folder:
        messagebox.showerror("Error", "Please select both a video file and an output folder.")
        return
    
    total_frames = extract_frames(video_path, output_folder, frame_rate)
    create_pdf_from_frames(output_folder, pdf_path, frames_per_page, video_name=video_file_name_without_ext, total_frames=total_frames)
    
    messagebox.showinfo("Success", f"Flipbook PDF created: {pdf_path}")

# GUI
root = tk.Tk()
root.title("Video to Flipbook Converter")

video_path_var = tk.StringVar()
output_folder_var = tk.StringVar()
frame_rate_var = tk.StringVar(value="10")
frames_per_page_var = tk.StringVar(value="10")

tk.Label(root, text="Video File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
tk.Entry(root, textvariable=video_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_video).grid(row=0, column=2, padx=5, pady=5)

tk.Label(root, text="Output Folder:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
tk.Entry(root, textvariable=output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
tk.Button(root, text="Browse", command=browse_output_folder).grid(row=1, column=2, padx=5, pady=5)

tk.Label(root, text="Frame Rate (frames per second):").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
tk.Entry(root, textvariable=frame_rate_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

tk.Label(root, text="Frames per Page:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
tk.Entry(root, textvariable=frames_per_page_var).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

generate_button = tk.Button(root, text="Generate Flipbook", command=generate_flipbook)
generate_button.grid(row=5, column=0, columnspan=3, pady=10)

# Adding a tooltip
tooltip = ttk.Label(root, text="It may take time to create", background="yellow")
tooltip.grid_forget()  # Initially hide the tooltip

def show_tooltip(event):
    tooltip.grid(row=3, column=0, columnspan=3, pady=10)

def hide_tooltip(event):
    tooltip.grid_forget()

generate_button.bind("<Enter>", show_tooltip)
generate_button.bind("<Leave>", hide_tooltip)

root.mainloop()
