# Simple YouTube Video Downloader

A Python app for downloading YouTube videos, with options for video trimming. Built with Python using Tkinter for the interface, yt-dlp for downloading, and moviepy for video processing.

## Prerequisites

- Python 3.6 or higher
- Required packages:
  ```
  tkinter (usually included with Python)
  moviepy
  yt-dlp
  ```

## Setup

1. Install the required packages:
```bash
pip install moviepy yt-dlp
```

2. Run the application:
```bash
python youtube_downloader.py
```

## Basic Usage

1. Enter a YouTube URL
2. Choose between downloading the full video or a trimmed section
3. If trimming, enter start and end times in HH:MM:SS format
4. Select where to save the video
5. Choose between using the video title as filename or a custom name
6. Click Download

## Features

- Download videos from YouTube
- Trim videos by specifying start and end times
- Choose download directory
- Use video title or custom filename
- Shows download progress
- Monitors internet connection status

## Technical Details

The application uses:
- yt-dlp for video downloading
- moviepy for video trimming
- Tkinter for the user interface
- Threading to prevent UI freezing during downloads

## Error Handling

The application handles:
- Network connection issues
- Invalid time formats
- Directory access problems
- Invalid URLs
- File system errors

## Note

This is a personal-use tool. Be mindful of YouTube's terms of service and content creators' rights when downloading videos.
