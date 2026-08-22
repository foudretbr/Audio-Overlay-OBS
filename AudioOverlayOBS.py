"""
Audio Overlay OBS - A standalone widget capturing Spotify and Deezer.
Provides a local HTTP server for OBS Studio integration.
"""

import asyncio
import json
import base64
import ctypes
import sys
import os
import threading
import time
import subprocess
import urllib.request
import winreg
import tkinter as tk
from tkinter import ttk
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image, ImageDraw
import pystray

from winsdk.windows.media.control import (
    GlobalSystemMediaTransportControlsSessionManager as MediaManager
)
from winsdk.windows.storage.streams import DataReader

CURRENT_VERSION = "1.0.5"
GITHUB_REPO = "foudretbr/Audio-Overlay-OBS"
REGISTRY_PATH = r"Software\Microsoft\Windows\CurrentVersion\Run"
APP_NAME = "AudioOverlayOBS"

media_data = {
    "title": "Waiting...",
    "artist": "-",
    "status": "paused",
    "position": 0,
    "duration": 1,
    "cover": "",
    "source_app": "deezer"
}

HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

        body {
            font-family: 'Inter', sans-serif;
            background: transparent;
            margin: 0;
            padding: 15px;
            color: white;
            overflow: hidden;
        }

        .player {
            background: #121216;
            border-radius: 8px;
            padding: 12px;
            display: flex;
            align-items: center;
            gap: 12px;
            width: 320px;
            box-sizing: border-box;
            box-shadow: 0 4px 15px rgba(0,0,0,0.6);
            border: 1px solid rgba(255,255,255,0.05);
        }

        .cover-container {
            width: 56px;
            height: 56px;
            border-radius: 4px;
            background-color: #2D2D38;
            overflow: hidden;
            flex-shrink: 0;
        }

        .cover-img {
            width: 100%;
            height: 100%;
            object-fit: cover;
            display: none;
        }

        .right-panel {
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
            overflow: hidden;
        }

        .info-row {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 8px;
        }

        .text-container {
            width: 100%;
            overflow: hidden;
            white-space: nowrap;
        }

        .title {
            font-weight: 700;
            font-size: 14px;
            margin: 0 0 3px 0;
            text-overflow: ellipsis;
            overflow: hidden;
            color: #FFFFFF;
        }

        .artist {
            font-weight: 600;
            font-size: 12px;
            color: #A2A2AD;
            margin: 0;
            text-overflow: ellipsis;
            overflow: hidden;
        }

        .progress-bar-bg {
            width: 100%;
            height: 3px;
            background: rgba(255, 255, 255, 0.15);
            border-radius: 2px;
            position: relative;
        }

        .progress-bar-fill {
            height: 100%;
            border-radius: 2px;
            width: 0%;
            transition: width 1s linear, background-color 0.5s ease;
        }
    </style>
</head>
<body>
    <div class="player">
        <div class="cover-container">
            <img id="cover" class="cover-img" src="" alt="cover">
        </div>

        <div class="right-panel">
            <div class="info-row">
                <div class="text-container">
                    <p class="title" id="title">Waiting...</p>
                    <p class="artist" id="artist">Play a song</p>
                </div>
            </div>

            <div class="progress-bar-bg">
                <div class="progress-bar-fill" id="progress"></div>
            </div>
        </div>
    </div>

    <script>
        async function updateWidget() {
            try {
                let response = await fetch('/api');
                let data = await response.json();

                document.getElementById('title').innerText = data.title;
                document.getElementById('artist').innerText = data.artist;

                let coverImg = document.getElementById('cover');
                if (data.cover !== "") {
                    coverImg.src = data.cover;
                    coverImg.style.display = "block";
                } else {
                    coverImg.style.display = "none";
                }

                let percent = (data.position / data.duration) * 100;
                if (percent > 100) percent = 100;
                if (percent < 0 || isNaN(percent)) percent = 0;

                let progressBar = document.getElementById('progress');
                progressBar.style.width = percent + '%';

                if (data.source_app === 'spotify') {
                    progressBar.style.backgroundColor = '#1DB954';
                } else {
                    progressBar.style.backgroundColor = '#A238FF';
                }

            } catch (error) {
                console.error("API Fetch Error");
            }
        }

        setInterval(updateWidget, 1000);
    </script>
</body>
</html>
"""

class SimpleHandler(BaseHTTPRequestHandler):
    """
    Custom HTTP handler for serving the HTML widget and JSON API.
    """
    def do_GET(self):
        """Handles incoming HTTP GET requests."""
        if self.path == '/api':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(media_data).encode("utf-8"))
        else:
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode("utf-8"))

    def log_message(self, format, *args):
        """Suppresses default console logging for incoming requests."""
        return

def get_target_session(manager):
    """
    Finds the first active session matching Spotify or Deezer.
    """
    session_list = manager.get_sessions()
    for session in session_list:
        app_id = session.source_app_user_model_id
        app_id_lower = app_id.lower() if app_id else ""
        if "spotify" in app_id_lower:
            return session, "spotify"
        if "deezer" in app_id_lower:
            return session, "deezer"
    return None, "deezer"

async def fetch_thumbnail_base64(info):
    """
    Safely retrieves the thumbnail stream and converts it to a Base64 string.
    Properly handles WinRT stream lifecycle to prevent memory leaks.
    """
    if not info.thumbnail:
        return ""

    stream = None
    reader = None
    try:
        stream = await info.thumbnail.open_read_async()
        if stream and stream.size > 0:
            reader = DataReader(stream)
            await reader.load_async(stream.size)
            buffer = reader.read_buffer(stream.size)
            image_bytes = bytes(buffer)

            # Detect actual MIME type using file magic bytes
            mime_type = "image/png" if image_bytes.startswith(b'\x89PNG') else "image/jpeg"
            encoded_str = base64.b64encode(image_bytes).decode('utf-8')
            return f"data:{mime_type};base64,{encoded_str}"
        return ""
    except Exception:
        return ""
    finally:
        if reader:
            try:
                reader.close()
            except Exception:
                pass
        if stream:
            try:
                stream.close()
            except Exception:
                pass

async def update_media_loop():
    """
    Asynchronous loop that continuously polls Windows SMTC for media properties.
    Optimized for long streaming sessions and prevents API freezes.
    """
    manager = None
    last_song_id = ""

    while True:
        try:
            if not manager:
                manager = await MediaManager.request_async()

            target_session, detected_app = get_target_session(manager)

            if target_session:
                info = await target_session.try_get_media_properties_async()
                if info and (info.title or info.artist):
                    media_data["title"] = info.title if info.title else "Unknown"
                    media_data["artist"] = info.artist if info.artist else "Unknown"
                    media_data["source_app"] = detected_app

                    current_song_id = f"{media_data['title']}-{media_data['artist']}"

                    if current_song_id != last_song_id or not media_data["cover"]:
                        media_data["cover"] = await fetch_thumbnail_base64(info)
                        last_song_id = current_song_id

                playback = target_session.get_playback_info()
                if playback:
                    if playback.playback_status == 4:
                        media_data["status"] = "playing"
                    else:
                        media_data["status"] = "paused"

                timeline = target_session.get_timeline_properties()
                if timeline and timeline.end_time.total_seconds() > 0:
                    media_data["duration"] = timeline.end_time.total_seconds()
                    media_data["position"] = timeline.position.total_seconds()

        except Exception:
            manager = None

        await asyncio.sleep(1)

def enforce_single_instance():
    """
    Checks if another instance is running using a Windows Mutex. Exits if it is.
    """
    mutex_name = "AudioOverlayOBS_SingleInstance_Mutex"
    mutex = ctypes.windll.kernel32.CreateMutexW(None, False, mutex_name)
    last_error = ctypes.windll.kernel32.GetLastError()

    if last_error == 183:
        sys.exit(0)

    return mutex

def run_server():
    """Starts the local HTTP server."""
    server = HTTPServer(('localhost', 8055), SimpleHandler)
    server.serve_forever()

def create_tray_icon():
    """Generates a simple icon with a white play triangle for the system tray."""
    image = Image.new('RGB', (64, 64), color=(30, 30, 30))
    draw = ImageDraw.Draw(image)
    draw.polygon([(20, 15), (20, 49), (50, 32)], fill=(255, 255, 255))
    return image

def is_startup_enabled():
    """Checks if the application is currently in the Windows startup registry."""
    if not getattr(sys, 'frozen', False):
        return False

    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_PATH, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, APP_NAME)
            return value == sys.executable
    except WindowsError:
        return False

def toggle_startup(icon, item):
    """Toggles the application in the Windows startup registry."""
    if not getattr(sys, 'frozen', False):
        if icon:
            icon.notify("Startup toggle only works in compiled .exe mode.", "Info")
        return

    enabled = is_startup_enabled()
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, REGISTRY_PATH, 0, winreg.KEY_WRITE) as key:
            if enabled:
                winreg.DeleteValue(key, APP_NAME)
                if icon:
                    icon.notify("Removed from Windows startup.", "Startup")
            else:
                winreg.SetValueEx(key, APP_NAME, 0, winreg.REG_SZ, sys.executable)
                if icon:
                    icon.notify("Added to Windows startup.", "Startup")
    except Exception:
        if icon:
            icon.notify("Failed to modify startup settings.", "Error")

def apply_update(download_url, icon=None):
    """
    Downloads the new executable, renames files to bypass AV, and restarts.
    """
    if not getattr(sys, 'frozen', False):
        if icon:
            icon.notify("Auto-update disabled in script mode.", "Update")
        return

    current_exe = sys.executable
    old_exe = current_exe + ".old"
    new_exe = current_exe + ".new"

    try:
        root = tk.Tk()
        root.title("Audio Overlay Updater")
        root.geometry("350x70")
        root.resizable(False, False)
        root.attributes("-topmost", True)

        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        x_cordinate = int((screen_width / 2) - (350 / 2))
        y_cordinate = int((screen_height / 2) - (70 / 2))
        root.geometry(f"350x70+{x_cordinate}+{y_cordinate}")

        ttk.Label(root, text="Downloading update...").pack(pady=(8, 2))
        progress_var = tk.DoubleVar()
        progress_bar = ttk.Progressbar(root, variable=progress_var, maximum=100)
        progress_bar.pack(fill=tk.X, padx=20, pady=5)

        def download_progress(count, block_size, total_size):
            if total_size > 0:
                percent = min(int(count * block_size * 100 / total_size), 100)
                progress_var.set(percent)
                root.update()

        root.update()

        urllib.request.urlretrieve(download_url, new_exe, reporthook=download_progress)
        root.destroy()

        if os.path.exists(old_exe):
            os.remove(old_exe)
        os.rename(current_exe, old_exe)
        os.rename(new_exe, current_exe)

        if icon:
            icon.stop()

        subprocess.Popen([current_exe, "--updated"], creationflags=subprocess.CREATE_NO_WINDOW)
        os._exit(0)

    except Exception:
        if 'root' in locals():
            root.destroy()
        if icon:
            icon.notify("Update failed.", "Error")
        if os.path.exists(old_exe) and not os.path.exists(current_exe):
            os.rename(old_exe, current_exe)

def check_for_updates(icon=None, item=None):
    """Checks the GitHub API for new releases and triggers the update process if found."""
    try:
        url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))

        latest_version = data.get("tag_name", "").replace("v", "")

        if latest_version and latest_version > CURRENT_VERSION:
            assets = data.get("assets", [])
            for asset in assets:
                if asset.get("name", "").endswith(".exe"):
                    download_url = asset.get("browser_download_url")
                    if download_url:
                        apply_update(download_url, icon)
                        return

        if item and icon:
            icon.notify("You are on the latest version.", "Up to date")

    except Exception:
        if item and icon:
            icon.notify("Could not check for updates.", "Error")

def dummy_action(icon, item):
    """Dummy function for non-clickable menu items."""

def quit_app(icon, item):
    """Stops the tray icon and exits the application entirely."""
    icon.stop()
    sys.exit(0)

def show_notification(icon):
    """
    Triggers a Windows notification and automatically checks for updates silently.
    """
    time.sleep(1)

    if "--updated" in sys.argv:
        icon.notify(f"Successfully updated to version {CURRENT_VERSION}!", "Update Complete")
    else:
        icon.notify("Widget is running in the background. Ready for OBS!", "Audio Overlay OBS")
        check_for_updates(icon)

def run_async_loop_thread():
    """Wrapper to run the asyncio loop in a separate thread."""
    asyncio.run(update_media_loop())

def cleanup_old_updates():
    """Removes the leftover .old executable from previous updates."""
    if getattr(sys, 'frozen', False):
        try:
            old_file = sys.executable + ".old"
            if os.path.exists(old_file):
                os.remove(old_file)
        except Exception:
            pass

if __name__ == '__main__':
    cleanup_old_updates()
    app_mutex = enforce_single_instance()

    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=run_async_loop_thread, daemon=True).start()

    tray_menu = pystray.Menu(
        pystray.MenuItem(f'Version {CURRENT_VERSION}', dummy_action, enabled=False),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Run at startup', toggle_startup, checked=lambda i: is_startup_enabled()),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Check for updates', check_for_updates),
        pystray.Menu.SEPARATOR,
        pystray.MenuItem('Exit / Quitter', quit_app)
    )

    tray_icon = pystray.Icon("AudioOverlayOBS", create_tray_icon(), "Audio Overlay OBS", tray_menu)
    threading.Thread(target=show_notification, args=(tray_icon,), daemon=True).start()
    tray_icon.run()