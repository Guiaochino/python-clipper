import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from moviepy import VideoFileClip
import csv
import os
import threading
import imageio_ffmpeg


root = tk.Tk()
root.title("Video Clipper")

video_path_var = tk.StringVar()
csv_path_var = tk.StringVar()
export_path_var = tk.StringVar()

def convert_time_to_seconds(time: str):
    hours, minutes, seconds = time.split(':')
    return int(hours) * 3600 + int(minutes) * 60 + float(seconds)

def clip_video():
    # Check for ffmpeg path
    ffmpeg_path = imageio_ffmpeg.get_ffmpeg_version()
    if ffmpeg_path is None:
        messagebox.showerror("Error", "FFMPEG not found! Please install imageio-ffmpeg")
        
    
    video_path = video_path_var.get()
    csv_path = csv_path_var.get()
    export_path = export_path_var.get()
    
    if not os.path.exists(video_path) or not os.path.exists(csv_path) or not os.path.exists(export_path):
        messagebox.showerror("Error", f"Invalid file paths:\nVideo: {video_path}\nCSV: {csv_path}\nExport: {export_path}")
        return
    
    try:
        clip = VideoFileClip(video_path)
        with open(csv_path, newline='') as csv_file:
            time_logs = list(csv.DictReader(csv_file))
            progressbar["maximum"] = len(time_logs)
            
            for i, logs in enumerate(time_logs, start=1):
                start = convert_time_to_seconds(logs.get('start_time', '').strip())
                end = convert_time_to_seconds(logs.get('end_time', '').strip())
                output_filename = os.path.join(export_path, logs.get('filename', 'output').strip() + ".mp4")
                
                trimmed_clip: VideoFileClip = clip.subclipped(start, end)
                # Type Guard
                if trimmed_clip is None:
                    messagebox.showerror('Error', f'Invalid subclip: {start} - {end}')
                    return
                
                trimmed_clip.write_videofile(output_filename, codec="libx264")
                
                progressbar["value"] = i
                root.update_idletasks()
                
        messagebox.showinfo("Success", "Clipping completed!")
        clip.close()
    except Exception as e:
        messagebox.showerror("Error", str(e))
        
def start_clipping():
    threading.Thread(target=clip_video, daemon=True).start()

def browse_video():
    filename = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
    video_path_var.set(filename)

def browse_csv():
    filename = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    csv_path_var.set(filename)

def browse_export():
    folder = filedialog.askdirectory()
    export_path_var.set(folder)


def main():
    # GUI Setup
    root.columnconfigure(1, weight=1)
    
    frame = tk.Frame(root)
    frame.pack(fill="both",expand=True, padx=5, pady=5)
    
    tk.Label(frame, text="Select Video File:", anchor="w").grid(column=0, row=0, sticky="w")
    tk.Entry(frame, textvariable=video_path_var, width=40).grid(column=1, row=0)
    tk.Button(frame, text="Browse", command=browse_video).grid(column=2, row=0)

    tk.Label(frame, text="Select CSV File:", anchor="w").grid(column=0, row=1, sticky="w")
    tk.Entry(frame, textvariable=csv_path_var, width=40).grid(column=1, row=1)
    tk.Button(frame, text="Browse", command=browse_csv).grid(column=2, row=1)

    tk.Label(frame, text="Select Export Folder:", anchor="w").grid(column=0, row=2, sticky="w")
    tk.Entry(frame, textvariable=export_path_var, width=40).grid(column=1, row=2)
    tk.Button(frame, text="Browse", command=browse_export).grid(column=2, row=2)

    tk.Button(root, text="Clip Video", command=start_clipping).pack(pady=10)
    
    global progressbar
    progressbar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
    progressbar.pack(pady=20)
    

    root.mainloop()
    
if __name__ == "__main__":
    main()
