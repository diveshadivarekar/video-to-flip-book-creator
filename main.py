import cv2
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinterdnd2 import DND_FILES, TkinterDnD
import threading
import os
import sys
import subprocess
import platform
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib.colors import Color, black, blue, red
from datetime import datetime

def extract_frames(video_path, output_folder, frame_rate=1, image_quality='high', start_time=0, end_time=None, progress_var=None):
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    vidcap = cv2.VideoCapture(video_path)
    total_frames = int(vidcap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = int(vidcap.get(cv2.CAP_PROP_FPS))
    duration = total_frames / fps
    success, image = vidcap.read()
    count = 0

    quality_params = {
        'Default High': [int(cv2.IMWRITE_JPEG_QUALITY), 95],
        'High': [int(cv2.IMWRITE_JPEG_QUALITY), 95],
        'Medium': [int(cv2.IMWRITE_JPEG_QUALITY), 75],
        'Low': [int(cv2.IMWRITE_JPEG_QUALITY), 50]
    }

    if end_time is None:
        end_time = duration

    while success:
        current_time = count / fps
        if start_time <= current_time <= end_time:
            vidcap.set(cv2.CAP_PROP_POS_MSEC, (count * 1000 / frame_rate))
            cv2.imwrite(os.path.join(output_folder, f"frame{count:05d}.jpg"), image, quality_params[image_quality])
            success, image = vidcap.read()
            count += 1

            if progress_var:
                progress_var.set((count / total_frames) * 100)
        else:
            success, image = vidcap.read()
            count += 1

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

    # Add creation date and time to the first frame
    current_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Main title
    c.setFont("Helvetica-Bold", 24)
    c.setFillColor(blue)
    c.drawCentredString(width / 2, height - margin - 50, "Video to Flipbook Creator")

    # Subheadings and details
    c.setFont("Helvetica", 14)
    c.setFillColor(black)
    c.drawCentredString(width / 2, height - margin - 80, "Developed by Divesh Adivarekar")
    c.setFillColor(blue)
    c.drawCentredString(width / 2, height - margin - 110, "https://diveshadivarekar.github.io/")
    
    # Line separator
    c.setStrokeColor(black)
    c.setLineWidth(0.5)
    c.line(margin, height - margin - 130, width - margin, height - margin - 130)

    # Video details
    c.setFont("Helvetica-Bold", 16)
    c.setFillColor(black)
    c.drawString(margin, height - margin - 160, f"Flipbook for Video: {video_name}")
    c.drawString(margin, height - margin - 180, f"Total Frames: {total_frames}")
    c.drawString(margin, height - margin - 200, f"Created on: {current_datetime}")
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

def browse_output_folder():
    folder_path = filedialog.askdirectory()
    output_folder_var.set(folder_path)

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_video_length(video_path):
    vidcap = cv2.VideoCapture(video_path)
    fps = vidcap.get(cv2.CAP_PROP_FPS)
    frame_count = vidcap.get(cv2.CAP_PROP_FRAME_COUNT)
    duration = frame_count / fps
    vidcap.release()
    return duration

def browse_video():
    file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
    video_path_var.set(file_path)
    video_length = get_video_length(file_path)
    end_time_var.set(f"{int(video_length // 3600):02}:{int((video_length % 3600) // 60):02}:{int(video_length % 60):02}")

def time_str_to_seconds(time_str):
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s

def generate_flipbook():
    video_path = video_path_var.get()
    video_file_name_without_ext = os.path.splitext(os.path.basename(video_path))[0]
    output_folder = output_folder_var.get()
    frame_rate = int(frame_rate_var.get())
    frames_per_page = int(frames_per_page_var.get())
    add_space = add_space_var.get()
    image_quality = image_quality_var.get()
    start_time = time_str_to_seconds(start_time_var.get())
    end_time = time_str_to_seconds(end_time_var.get())

    # Increment file name if it already exists
    pdf_base_path = os.path.join(output_folder, f"flipbook for [{video_file_name_without_ext}]")
    pdf_path = f"{pdf_base_path}.pdf"
    count = 1
    while os.path.exists(pdf_path):
        pdf_path = f"{pdf_base_path}_{count}.pdf"
        count += 1
    
    if not video_path or not output_folder:
        messagebox.showerror("Error", "Please select both a video file and an output folder.")
        return

    progress_bar.grid()
    progress_var.set(0)
    root.update_idletasks()

    # Run the extraction and PDF creation in a separate thread to avoid freezing the GUI
    threading.Thread(target=process_flipbook, args=(video_path, output_folder, frame_rate, frames_per_page, add_space, image_quality, start_time, end_time, pdf_path, video_file_name_without_ext)).start()

     # Open the output folder
    open_output_folder(output_folder)

def process_flipbook(video_path, output_folder, frame_rate, frames_per_page, add_space, image_quality, start_time, end_time, pdf_path, video_file_name_without_ext):
    total_frames = extract_frames(video_path, output_folder, frame_rate, image_quality, start_time, end_time, progress_var=progress_var)
    create_pdf_from_frames(output_folder, pdf_path, frames_per_page, video_name=video_file_name_without_ext, total_frames=total_frames, add_space=add_space, progress_var=progress_var)
    delete_images(output_folder)
    progress_var.set(100)
    messagebox.showinfo("Success", f"Flipbook PDF created: {pdf_path}")
    progress_bar.grid_remove()

def open_output_folder(path):
    # Ensure the path is correctly formatted
    path = os.path.abspath(path)

    if platform.system() == "Windows":
        subprocess.Popen(f'explorer "{path}"')
    elif platform.system() == "Darwin":
        subprocess.Popen(["open", path])
    else:
        subprocess.Popen(["xdg-open", path])

# Modern GUI with ttk and menu bar
root = TkinterDnD.Tk()
root.title("Video to Flipbook Creator")
root.geometry("700x380")
root.resizable(False, False)

style = ttk.Style()
style.theme_use('xpnative')

# Function to change theme
def change_theme(theme_name):
    style.theme_use(theme_name)
# Menu bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

file_menu = tk.Menu(menu_bar, tearoff=0)
file_menu.add_command(label="Open Video", command=browse_video)
file_menu.add_command(label="Save Output Folder", command=browse_output_folder)
file_menu.add_separator()
file_menu.add_command(label="Exit", command=root.quit)
menu_bar.add_cascade(label="File", menu=file_menu)

help_menu = tk.Menu(menu_bar, tearoff=0)
help_menu.add_command(label="About", command=lambda: messagebox.showinfo("About", "Video to Flipbook Creator\nDeveloped by Divesh Adivarekar"))
menu_bar.add_cascade(label="Help", menu=help_menu)

theme_menu = tk.Menu(menu_bar, tearoff=0)
theme_menu.add_command(label="Default", command=lambda: change_theme("default"))
theme_menu.add_command(label="Clam", command=lambda: change_theme("clam"))
theme_menu.add_command(label="Alt", command=lambda: change_theme("alt"))
theme_menu.add_command(label="Classic", command=lambda: change_theme("classic"))
theme_menu.add_command(label="Vista", command=lambda: change_theme("vista"))
theme_menu.add_command(label="Xpnative", command=lambda: change_theme("xpnative"))

menu_bar.add_cascade(label="Theme", menu=theme_menu)

# Main frame
main_frame = ttk.Frame(root, padding="10 10 10 10")
main_frame.grid(column=0, row=0, sticky=(tk.W, tk.E, tk.N, tk.S))

video_path_var = tk.StringVar()
output_folder_var = tk.StringVar()
frame_rate_var = tk.StringVar(value="1")
frames_per_page_var = tk.StringVar(value="10")
add_space_var = tk.BooleanVar(value=True)
image_quality_var = tk.StringVar(value='high')
start_time_var = tk.StringVar(value='00:00:00')
end_time_var = tk.StringVar(value='00:00:00')

ttk.Label(main_frame, text="Video File:").grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
ttk.Entry(main_frame, textvariable=video_path_var, width=50).grid(row=0, column=1, padx=5, pady=5)
ttk.Button(main_frame, text="Browse", command=browse_video).grid(row=0, column=2, padx=5, pady=5)

ttk.Label(main_frame, text="Output Folder:").grid(row=1, column=0, padx=5, pady=5, sticky=tk.W)
ttk.Entry(main_frame, textvariable=output_folder_var, width=50).grid(row=1, column=1, padx=5, pady=5)
ttk.Button(main_frame, text="Browse", command=browse_output_folder).grid(row=1, column=2, padx=5, pady=5)

ttk.Label(main_frame, text="Frame Rate:").grid(row=2, column=0, padx=5, pady=5, sticky=tk.W)
ttk.Entry(main_frame, textvariable=frame_rate_var).grid(row=2, column=1, padx=5, pady=5, sticky=tk.W)

ttk.Label(main_frame, text="Frames per Page:").grid(row=3, column=0, padx=5, pady=5, sticky=tk.W)
ttk.Spinbox(main_frame, from_=1, to=10, textvariable=frames_per_page_var).grid(row=3, column=1, padx=5, pady=5, sticky=tk.W)

ttk.Checkbutton(main_frame, text="Add space on left side of frames", variable=add_space_var).grid(row=4, column=0, columnspan=3, padx=5, pady=5, sticky=tk.W)

ttk.Label(main_frame, text="Image Quality:").grid(row=5, column=0, padx=5, pady=5, sticky=tk.W)
ttk.OptionMenu(main_frame, image_quality_var, 'Default High','High', 'Medium', 'Low').grid(row=5, column=1, padx=5, pady=5, sticky=tk.W)

ttk.Label(main_frame, text="Start Time (HH:MM:SS):").grid(row=6, column=0, padx=5, pady=5, sticky=tk.W)
ttk.Entry(main_frame, textvariable=start_time_var).grid(row=6, column=1, padx=5, pady=5, sticky=tk.W)

ttk.Label(main_frame, text="End Time (HH:MM:SS):").grid(row=7, column=0, padx=5, pady=5, sticky=tk.W)
ttk.Entry(main_frame, textvariable=end_time_var).grid(row=7, column=1, padx=5, pady=5, sticky=tk.W)

generate_button = ttk.Button(main_frame, text="Generate Flipbook", command=generate_flipbook)
generate_button.grid(row=8, column=0, columnspan=3, pady=10)

# Progress bar
progress_var = tk.DoubleVar()
progress_bar = ttk.Progressbar(main_frame, variable=progress_var, maximum=100)
progress_bar.grid(row=8, column=0, columnspan=1, padx=5, pady=5)
progress_bar.grid_remove()

# Adding a tooltip
tooltip = ttk.Label(main_frame, text="It may take time to create", background="yellow")
tooltip.grid_forget()  

def show_tooltip(event):
    tooltip.grid(row=4, column=0, columnspan=3, pady=5)

def hide_tooltip(event):
    tooltip.grid_forget()

generate_button.bind("<Enter>", show_tooltip)
generate_button.bind("<Leave>", hide_tooltip)

root.mainloop()