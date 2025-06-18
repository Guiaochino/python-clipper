import tkinter as tk
from tkinter import filedialog, messagebox
import vlc

class FileSelectComponent(tk.Frame):
    def __init__(self, root, vlc_instance, media_player):
        super().__init__(master=root)
        self.video_file_path=None
        
        self.instance = vlc_instance
        self.media_player = media_player
        
        self.select_video_button = tk.Button(master=self, text='Select a Video', command=self.select_video, bg='#000000', fg='#ffffff', bd=None, )
        self.select_video_button.pack(pady=200)
        
        
    def select_video(self):
        self.video_file_path = filedialog.askopenfilename(filetypes=[("Video files", "*.mp4;*.avi;*.mov")])
        if self.video_file_path:
            media = self.instance.media_new(self.video_file_path)
            self.media_player.set_media(media)
            
            if self.winfo_id():
                self.media_player.set_hwnd(self.winfo_id())
                
            self.media_player.play()
        
        