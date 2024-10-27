import tkinter as tk
from tkinter import messagebox, filedialog, ttk
from moviepy.video.io.VideoFileClip import VideoFileClip
import threading
import os
import re
from urllib.parse import urlparse, parse_qs
import urllib.request
import yt_dlp

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Video Downloader")
        self.root.geometry("600x700")  # Increased height for new elements

        self.internet_status_var = tk.StringVar()
        self.setup_gui()
        self.check_internet_connection()
        
    def setup_gui(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Internet connection status
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(status_frame, text="Internet Status:").pack(side=tk.LEFT, padx=5)
        self.internet_status_label = ttk.Label(status_frame, textvariable=self.internet_status_var)
        self.internet_status_label.pack(side=tk.LEFT, padx=5)
        
        # URL input section
        url_frame = ttk.LabelFrame(main_frame, text="Video URL", padding="5")
        url_frame.pack(fill=tk.X, pady=5)
        
        self.url_entry = ttk.Entry(url_frame, width=50)
        self.url_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Download options section
        options_frame = ttk.LabelFrame(main_frame, text="Download Options", padding="5")
        options_frame.pack(fill=tk.X, pady=5)
        
        self.full_video_var = tk.BooleanVar(value=True)
        full_video_checkbox = ttk.Checkbutton(
            options_frame,
            text="Download Full Video",
            variable=self.full_video_var,
            command=self.toggle_time_entries
        )
        full_video_checkbox.pack(pady=5)
        
        # Time input frame
        self.time_frame = ttk.Frame(options_frame)
        self.time_frame.pack(fill=tk.X, pady=5)
        
        # Start time input
        start_frame = ttk.Frame(self.time_frame)
        start_frame.pack(fill=tk.X, pady=2)
        ttk.Label(start_frame, text="Start Time:").pack(side=tk.LEFT, padx=5)
        self.start_entry = ttk.Entry(start_frame, width=10)
        self.start_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(start_frame, text="(hh:mm:ss)").pack(side=tk.LEFT)
        
        # End time input
        end_frame = ttk.Frame(self.time_frame)
        end_frame.pack(fill=tk.X, pady=2)
        ttk.Label(end_frame, text="End Time:").pack(side=tk.LEFT, padx=5)
        self.end_entry = ttk.Entry(end_frame, width=10)
        self.end_entry.pack(side=tk.LEFT, padx=5)
        ttk.Label(end_frame, text="(hh:mm:ss)").pack(side=tk.LEFT)
        
        # File save options section
        save_frame = ttk.LabelFrame(main_frame, text="Save Options", padding="5")
        save_frame.pack(fill=tk.X, pady=5)
        
        # Directory selection
        dir_frame = ttk.Frame(save_frame)
        dir_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(dir_frame, text="Save to:").pack(side=tk.LEFT, padx=5)
        self.output_dir = tk.StringVar(value=os.path.expanduser("~/Downloads"))
        self.dir_entry = ttk.Entry(dir_frame, textvariable=self.output_dir)
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        browse_button = ttk.Button(dir_frame, text="Browse", command=self.browse_directory)
        browse_button.pack(side=tk.RIGHT, padx=5)
        
        # Filename options
        filename_frame = ttk.Frame(save_frame)
        filename_frame.pack(fill=tk.X, pady=5)
        
        # Filename choice
        self.filename_var = tk.StringVar(value="auto")
        ttk.Radiobutton(
            filename_frame,
            text="Auto (Video Title)",
            variable=self.filename_var,
            value="auto",
            command=self.toggle_filename_entry
        ).pack(anchor=tk.W, padx=5)
        
        custom_filename_frame = ttk.Frame(filename_frame)
        custom_filename_frame.pack(fill=tk.X, pady=2)
        
        ttk.Radiobutton(
            custom_filename_frame,
            text="Custom:",
            variable=self.filename_var,
            value="custom",
            command=self.toggle_filename_entry
        ).pack(side=tk.LEFT, padx=5)
        
        self.filename_entry = ttk.Entry(custom_filename_frame)
        self.filename_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        ttk.Label(custom_filename_frame, text=".mp4").pack(side=tk.LEFT)
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="5")
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_var,
            maximum=100
        )
        self.progress_bar.pack(fill=tk.X, pady=5)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to download")
        self.progress_label.pack(pady=5)
        
        # Video info section
        self.info_frame = ttk.LabelFrame(main_frame, text="Video Information", padding="5")
        self.info_frame.pack(fill=tk.X, pady=5)
        
        self.title_label = ttk.Label(self.info_frame, text="", wraplength=550)
        self.title_label.pack(pady=5)
        
        # Download button
        self.download_button = ttk.Button(
            main_frame,
            text="Download",
            command=self.start_download,
            style="Accent.TButton"
        )
        self.download_button.pack(pady=10)
        
        # Initialize state
        self.toggle_time_entries()
        self.toggle_filename_entry()
    
    def toggle_filename_entry(self):
        """Enable/disable custom filename entry based on radio button selection"""
        if self.filename_var.get() == "auto":
            self.filename_entry.config(state="disabled")
        else:
            self.filename_entry.config(state="normal")
    
    def get_safe_filename(self, title):
        """Generate safe filename based on user selection"""
        if self.filename_var.get() == "custom" and self.filename_entry.get().strip():
            # Use custom filename
            base_name = self.filename_entry.get().strip()
            # Remove invalid characters
            base_name = "".join(c for c in base_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        else:
            # Use video title
            base_name = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_')).rstrip()
        
        # Add trimmed suffix if needed
        if not self.full_video_var.get():
            base_name += "_trimmed"
        
        return base_name + ".mp4"
    
    def browse_directory(self):
        """Open directory browser dialog"""
        directory = filedialog.askdirectory(
            initialdir=self.output_dir.get(),
            title="Select Download Directory"
        )
        if directory:
            self.output_dir.set(directory)
    
    def toggle_time_entries(self):
        """Enable/disable time entry fields based on checkbox state"""
        state = 'disabled' if self.full_video_var.get() else 'normal'
        self.start_entry.config(state=state)
        self.end_entry.config(state=state)
    
    def parse_time(self, time_str):
        """Convert time string (HH:MM:SS) to seconds"""
        if not time_str:
            return None
            
        # Check if input is already in seconds
        if time_str.isdigit():
            return int(time_str)
            
        # Parse HH:MM:SS format
        time_pattern = re.compile(r'^(?:(?P<hours>\d+):)?(?:(?P<minutes>\d+):)?(?P<seconds>\d+)$')
        match = time_pattern.match(time_str)
        
        if not match:
            raise ValueError("Invalid time format. Use HH:MM:SS or seconds")
            
        parts = match.groupdict(default='0')
        hours = int(parts['hours'])
        minutes = int(parts['minutes'])
        seconds = int(parts['seconds'])
        
        return hours * 3600 + minutes * 60 + seconds
    
    def download_youtube_video(self, url, start_time=None, end_time=None):
        """Download and optionally trim YouTube video"""
        try:
            # Update UI state
            self.download_button.config(state='disabled')
            self.progress_label.config(text="Initializing download...")
            
            # Set up yt-dlp options
            ydl_opts = {
                'format': 'best',
                'progress_hooks': [self.progress_hook],
                'outtmpl': os.path.join(self.output_dir.get(), '%(title)s.%(ext)s')
            }
            
            # Download video
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                title = info_dict.get('title', None)
                filename = self.get_safe_filename(title)
                original_path = os.path.join(self.output_dir.get(), f"{title}.mp4")
                video_path = os.path.join(self.output_dir.get(), filename)
                
                # Rename file to match user preferences
                if os.path.exists(original_path):
                    os.rename(original_path, video_path)
                
                # Trim video if needed
                if not self.full_video_var.get() and (start_time is not None or end_time is not None):
                    self.progress_label.config(text="Trimming video...")
                    self.progress_var.set(0)
                    
                    with VideoFileClip(video_path) as video:
                        trimmed_clip = video.subclip(start_time, end_time)
                        trimmed_path = os.path.join(
                            self.output_dir.get(),
                            filename
                        )
                        trimmed_clip.write_videofile(
                            trimmed_path,
                            codec="libx264",
                            audio_codec="aac"
                        )
                    
                    # Remove original if trimming was successful
                    if os.path.exists(video_path):
                        os.remove(video_path)
                    final_path = trimmed_path
                else:
                    final_path = video_path
                
                self.progress_var.set(100)
                self.progress_label.config(text="Download complete!")
                messagebox.showinfo(
                    "Success",
                    f"Video saved to:\n{final_path}"
                )
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.progress_label.config(text="Download failed")
        finally:
            self.download_button.config(state='normal')
            self.progress_var.set(0)
    
    def progress_hook(self, d):
        """Hook to update progress bar during download"""
        if d['status'] == 'downloading':
            downloaded = d.get('_downloaded_bytes', 0)
            total = d.get('total_bytes', 1)
            percentage = (downloaded / total) * 100
            self.progress_var.set(percentage)
            self.progress_label.config(
                text=f"Downloading... {int(percentage)}% "
                     f"({downloaded / (1024 * 1024):.1f}MB / {total / (1024 * 1024):.1f}MB)"
            )
            self.root.update_idletasks()
    
    def check_internet_connection(self):
        try:
            urllib.request.urlopen('https://www.google.com', timeout=5)
            self.internet_status_var.set("Connected")
            if hasattr(self, 'internet_status_label'):
                self.internet_status_label.config(foreground='green')
            return True
        except:
            self.internet_status_var.set("Disconnected")
            if hasattr(self, 'internet_status_label'):
                self.internet_status_label.config(foreground='red')
            return False

    def start_download(self):
        """Validate inputs and start download process"""
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Please enter a YouTube URL")
            return
        
        # Validate output directory
        if not os.path.isdir(self.output_dir.get()):
            messagebox.showerror("Error", "Please select a valid output directory")
            return
            
        # Validate custom filename if selected
        if self.filename_var.get() == "custom":
            if not self.filename_entry.get().strip():
                messagebox.showerror("Error", "Please enter a filename")
                return
        
        try:
            if self.full_video_var.get():
                start_time = end_time = None
            else:
                start_time = self.parse_time(self.start_entry.get())
                end_time = self.parse_time(self.end_entry.get())
            
            threading.Thread(
                target=self.download_youtube_video,
                args=(url, start_time, end_time),
                daemon=True
            ).start()
            
        except ValueError as e:
            messagebox.showerror("Error", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = YouTubeDownloader(root)
    root.mainloop()
