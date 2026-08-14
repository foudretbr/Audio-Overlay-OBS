import asyncio
import json
import base64
import sys
import threading
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager as MediaManager
from winsdk.windows.storage.streams import DataReader
import pystray
from PIL import Image, ImageDraw

media_data = {
    "title": "Waiting...",
    "artist": "-",
    "status": "paused",
    "position": 0,
    "duration": 1,
    "cover": ""
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
            background: #A238FF;
            border-radius: 2px;
            width: 0%;
            transition: width 1s linear;
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
        /**
         * Fetches media data from the local API and updates the DOM elements.
         * 
         * @async
         * @function updateWidget
         * @returns {Promise<void>}
         */
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
                document.getElementById('progress').style.width = percent + '%';
                
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
        """
        Handles incoming HTTP GET requests.
        
        @param self: The class instance.
        @return: None
        """
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
        """
        Suppresses default console logging for incoming requests.
        """
        return 

async def update_media_loop():
    """
    Asynchronous loop that continuously polls Windows SMTC for media properties.
    
    @return: None
    """
    global media_data
    while True:
        try:
            sessions = await MediaManager.request_async()
            current_session = sessions.get_current_session()
            
            if current_session:
                info = await current_session.try_get_media_properties_async()
                if info and info.title:
                    media_data["title"] = info.title
                    media_data["artist"] = info.artist
                    
                    if info.thumbnail:
                        try:
                            stream = await info.thumbnail.open_read_async()
                            reader = DataReader(stream)
                            await reader.load_async(stream.size)
                            buffer = reader.read_buffer(stream.size)
                            image_bytes = bytes(buffer)
                            media_data["cover"] = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode('utf-8')
                        except Exception:
                            media_data["cover"] = ""
                    else:
                        media_data["cover"] = ""
                
                playback = current_session.get_playback_info()
                if playback:
                    if playback.playback_status == 4:
                        media_data["status"] = "playing"
                    else:
                        media_data["status"] = "paused"
                
                timeline = current_session.get_timeline_properties()
                if timeline and timeline.end_time.total_seconds() > 0:
                    media_data["duration"] = timeline.end_time.total_seconds()
                    media_data["position"] = timeline.position.total_seconds()
            
        except Exception:
            pass
            
        await asyncio.sleep(1)

def run_server():
    """
    Starts the local HTTP server.
    """
    server = HTTPServer(('localhost', 8055), SimpleHandler)
    server.serve_forever()

def create_tray_icon():
    """
    Generates a simple purple icon with a white play triangle for the system tray.
    
    @return: PIL.Image object
    """
    image = Image.new('RGB', (64, 64), color=(162, 56, 255))
    draw = ImageDraw.Draw(image)
    draw.polygon([(20, 15), (20, 49), (50, 32)], fill=(255, 255, 255))
    return image

def quit_app(icon, item):
    """
    Stops the tray icon and exits the application entirely.
    
    @param icon: The tray icon instance.
    @param item: The clicked menu item.
    @return: None
    """
    icon.stop()
    sys.exit(0)

def show_notification(icon):
    """
    Delays slightly and triggers a Windows notification.
    
    @param icon: The tray icon instance.
    @return: None
    """
    time.sleep(1)
    icon.notify("Widget is running in the background. Ready for OBS!", "Deezer OBS Widget")

def run_async_loop_thread():
    """
    Wrapper to run the asyncio loop in a separate thread.
    """
    asyncio.run(update_media_loop())

if __name__ == '__main__':
    threading.Thread(target=run_server, daemon=True).start()
    threading.Thread(target=run_async_loop_thread, daemon=True).start()
    
    tray_menu = pystray.Menu(pystray.MenuItem('Exit / Quitter', quit_app))
    tray_icon = pystray.Icon("DeezerOBS", create_tray_icon(), "Deezer OBS Widget", tray_menu)
    
    threading.Thread(target=show_notification, args=(tray_icon,), daemon=True).start()
    
    tray_icon.run()