import tkinter as tk
import vlc
import os
import threading
from tkinter import messagebox, filedialog
from src.components.FileSelectComponent import FileSelectComponent
from PIL import Image, ImageTk
from moviepy import VideoFileClip

class VideoClipper(tk.Tk):
    def __init__(self):
        super().__init__()
        self._initialize_window()
        self._initialize_vlc()
        self._initialize_ui()
        self.bind_shortcuts()
        
    def _initialize_window(self):
        self.geometry(f'{int(self.winfo_screenwidth() * 0.75)}x{int(self.winfo_screenheight() * 0.75)}+0+0')
        
    
    def _initialize_vlc(self):
        self.instance = vlc.Instance()
        self.media_player = self.instance.media_player_new()
        self.split_record_times: list = []
        self.last_split_index = None
        self.split_time = {
            "start_time": 0,
            "end_time": 0
        }
        
    def _initialize_ui(self):
        self.main_container = tk.Frame(self)
        self.main_container.pack(fill='both', expand=True)
        
        self._setup_video_frame()
        self._setup_timestamp_frame()
        self._setup_controls()
        
    
    def _setup_video_frame(self):
        self.video_container = tk.Frame(self.main_container)
        self.video_container.pack(side='left', expand=True, fill='both')
        
        self.file_select = FileSelectComponent(self.video_container, vlc_instance=self.instance, media_player=self.media_player)
        self.file_select.pack(expand=True, fill='both')
        
    def _setup_timestamp_frame(self):
        self.timestamp_frame = tk.Frame(self.main_container, padx=10)
        self.timestamp_frame.pack(side='right', fill='y')
        
        self.timestamp_label = tk.Label(self.timestamp_frame, text='Timestamps', font=('Arial', 12, 'bold'))
        self.timestamp_label.pack(anchor='w')
        
        self.timestamp_listbox = tk.Listbox(self.timestamp_frame, width=32, height=10)
        self.timestamp_listbox.pack(fill='both', expand=True)
        
        self.skip_reference = tk.StringVar(value='0.05')
        self.skip_reference_entry = tk.Entry(self, textvariable=self.skip_reference, justify='center')
        self.skip_reference_entry.pack(pady=10)
        
    def _setup_controls(self):
        self.previous_icon = ImageTk.PhotoImage(Image.open('src/assets/icons8-previous-24.png'))
        self.play_icon = ImageTk.PhotoImage(Image.open('src/assets/icons8-play-24.png'))
        self.pause_icon = ImageTk.PhotoImage(Image.open('src/assets/icons8-pause-24.png'))
        self.next_icon = ImageTk.PhotoImage(Image.open('src/assets/icons8-last-24.png'))
        self.split_icon = ImageTk.PhotoImage(Image.open('src/assets/icons8-clip-snapping-24.png'))
        self.export_icon = ImageTk.PhotoImage(Image.open('src/assets/icons8-export-24.png'))
        
        self.button_containers = tk.Frame(self)
        self.button_containers.pack(fill='x', pady=10)
        
        controls = [
            (self.previous_icon, self.prev_frame_event),
            (self.play_icon, self.toggle_pause_play),
            (self.pause_icon, self.toggle_pause_play),
            (self.next_icon, self.next_frame_event),
            (self.split_icon, self.record_split),
            (self.export_icon, self.export_videos)
            
        ]
        
        for i, (icon, command) in enumerate(controls):
            tk.Button(self.button_containers, image=icon, compound='center', command=command).grid(row=0, column=i, padx=5)
            
    def bind_shortcuts(self):
        self.bind('<space>', self.toggle_pause_play)
        self.bind('<Left>', self.prev_frame_event)
        self.bind('<Right>', self.next_frame_event)
        
        
    @staticmethod
    def _convert_millis(millis: int) -> tuple[float, str]:
        seconds = millis / 1000
        
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        seconds = int((seconds % 60))
        millis = int((seconds % 1) * 1000)
        
        formatted_time = f"{hours:02}:{minutes:02}:{seconds:02}.{millis:03}"
        return seconds, formatted_time
    
    @staticmethod
    def _convert_to_seconds(millis:int) -> float:
        return millis / 1000


    def toggle_pause_play(self, event=None):
        self.focus_set()
        
        if (self.media_player.is_playing()):
            self.media_player.pause()
        else:
            self.media_player.play()
        
        
    def prev_frame_event(self, event=None):
        self.focus_set()
        
        current_time = self.media_player.get_time()
        new_time = max(current_time - int(float(self.skip_reference.get()) * 1000), 0)
        self.media_player.set_time(new_time)
    
    
    def next_frame_event(self, event=None):
        self.focus_set()
        
        current_time = self.media_player.get_time()
        new_time = current_time + int(float(self.skip_reference.get()) * 1000)
        self.media_player.set_time(new_time)
        
        
    def record_split(self, event=None):
        current_time = self.media_player.get_time()
        _, formatted_time = self._convert_millis(current_time)
        
        if self.split_time['start_time'] == 0:
            self.split_time['start_time'] = current_time
            
            # Insert placeholder
            placeholder = f'Start: {formatted_time} End: ...'
            self.last_split_index = self.timestamp_listbox.size()
            self.timestamp_listbox.insert(tk.END, placeholder)
            return
        
        if self.split_time['end_time'] == 0:
            _, prev_formatted_time = self._convert_millis(self.split_time['start_time'])
            self.split_time['end_time'] = current_time
            
            # Add to list once filled
            self.split_record_times.append(self.split_time)
            
            updated_time = (
                f"Start: {prev_formatted_time:<10} "
                f"End: {formatted_time}"
            )
            self.timestamp_listbox.delete(self.last_split_index)
            self.timestamp_listbox.insert(self.last_split_index, updated_time)
            
            # Create new empty fields
            self.split_time = {
                'start_time': 0,
                'end_time': 0
            }
            self.last_split_index = None
            return
        
        messagebox.showerror('Error', 'Something went wrong\ncode:0x00')
        
    
    def export_videos(self):
        if not self.file_select.video_file_path:
            messagebox.showerror('No video', ' Please load a video first.')
            return
        
        if not self.split_record_times:
            messagebox.showerror('No recorded time', 'No timestamps recorded to export.')
            return
        
        export_dir = filedialog.askdirectory(title='Select export path')
        if not export_dir:
            return
        
        try:
            original_clip = VideoFileClip(self.file_select.video_file_path)
            
            for i, split in enumerate(self.split_record_times, 1):
                start_time = self._convert_to_seconds(split['start_time'])
                end_time = self._convert_to_seconds(split['end_time'])
                
                print(start_time)
                
                subclip = original_clip.subclipped(start_time, end_time)
                output_path = os.path.join(export_dir, f'exported_clip_{i:02d}.mp4')
                subclip.write_videofile(output_path, codec='libx264')
                
            messagebox.showinfo('Success', 'Clipping completed!')
            original_clip.close()
            
        except Exception as e:
            messagebox.showerror('Error', str(e))
            
    def start_clipping(self):
        threading.Thread(target=self.export_videos, daemon=True).start()
            