import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime

# Replace with your API ID, API Hash, and Bot Token
API_ID = "21705536"
API_HASH = "c5bb241f6e3ecf33fe68a444e288de2d"
BOT_TOKEN = "7480080731:AAGGgo9o_t9pmWsgT8lVO3PJ4OjPhLg2Aoo"

# Telegram channel where files will be forwarded
CHANNEL_USERNAME = "engineerbabutxtfiles"  # Replace with your channel username

# Initialize Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to extract names and URLs from the text file
def extract_names_and_urls(file_content):
    lines = file_content.strip().split("\n")
    data = []
    for line in lines:
        if ":" in line:
            name, url = line.split(":", 1)
            data.append((name.strip(), url.strip()))
    return data

# Function to categorize URLs
def categorize_urls(urls):
    videos = []
    pdfs = []
    others = []

    for name, url in urls:
        new_url = url
        if "media-cdn.classplusapp.com/drm/" in url or "cpvod.testbook" in url:
            new_url = f"https://dragoapi.vercel.app/video/{url}"
            videos.append((name, new_url))
        elif "dragoapi.vercel" in url:
            videos.append((name, url))
        elif "/master.mpd" in url:
            vid_id = url.split("/")[-2]
            new_url = f"https://player.muftukmall.site/?id={vid_id}"
            videos.append((name, new_url))
        elif "youtube.com/embed" in url or "youtu.be" in url or "youtube.com/watch" in url:
            yt_id = url.split("v=")[-1].split("&")[0] if "v=" in url else url.split("/")[-1]
            new_url = f"https://www.youtube.com/watch?v={yt_id}"
            videos.append((name, new_url))
        elif ".m3u8" in url or ".mp4" in url or ".mkv" in url or ".webm" in url or ".m3u" in url or ".epg" in url:
            videos.append((name, url))
        elif "pdf*" in url:
            new_url = f"https://dragoapi.vercel.app/pdf/{url}"
            pdfs.append((name, new_url))
        elif "pdf" in url:
            pdfs.append((name, url))
        else:
            others.append((name, url))

    return videos, pdfs, others

# Function to generate HTML file with Video.js player, YouTube player, and download feature
def generate_html(file_name, videos, pdfs, others):
    file_name_without_extension = os.path.splitext(file_name)[0]

    video_links = "".join(f'<a href="#" onclick="playVideo(\'{url}\')">{name}</a>' for name, url in videos)
    pdf_links = "".join(f'<a href="{url}" target="_blank">{name}</a> <a href="{url}" download>📥 Download PDF</a>' for name, url in pdfs)
    other_links = "".join(f'<a href="{url}" target="_blank">{name}</a>' for name, url in others)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_name_without_extension}</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
    <style>
        /* Add your CSS styles here */
    </style>
</head>
<body>
    <div class="header">{file_name_without_extension}</div>
    <div class="subheading">📥 Extracted By: <a href="https://t.me/Engineers_Babu" target="_blank">Engineers Babu™</a></div>
    <div class="datetime" id="datetime">📅 {datetime.now().strftime('%A %d %B, %Y | ⏰ %I:%M:%S %p')}</div>
    <br>
    <p>🔹Use This Bot for TXT to HTML file Extraction: <a href="https://t.me/htmldeveloperbot" target="_blank">@htmldeveloperbot 🚀</a></p>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search for videos, PDFs, or other resources..." oninput="filterContent()">
    </div>

    <div id="noResults" class="no-results">No results found.</div>

    <div id="video-player">
        <video id="engineer-babu-player" class="video-js vjs-default-skin" controls preload="auto" width="640" height="360">
            <p class="vjs-no-js">
                To view this video please enable JavaScript, and consider upgrading to a web browser that
                <a href="https://videojs.com/html5-video-support/" target="_blank">supports HTML5 video</a>
            </p>
        </video>
        <div class="download-button">
            <a id="download-link" href="#" download>Download Video</a>
        </div>
        <div style="text-align: center; margin-top: 10px; font-weight: bold; color: #007bff;">Engineer Babu Player</div>
    </div>

    <div id="youtube-player">
        <div id="player"></div>
        <div style="text-align: center; margin-top: 10px; font-weight: bold; color: #007bff;">YouTube Player</div>
    </div>

    <div class="container">
        <div class="tab" onclick="showContent('videos')">Videos</div>
        <div class="tab" onclick="showContent('pdfs')">PDFs</div>
        <div class="tab" onclick="showContent('others')">Others</div>
    </div>

    <div id="videos" class="content">
        <h2>All Video Lectures</h2>
        <div class="video-list">
            {video_links}
        </div>
    </div>

    <div id="pdfs" class="content">
        <h2>All PDFs</h2>
        <div class="pdf-list">
            {pdf_links}
        </div>
    </div>

    <div id="others" class="content">
        <h2>Other Resources</h2>
        <div class="other-list">
            {other_links}
        </div>
    </div>

    <div class="footer">Extracted By - <a href="https://t.me/Engineers_Babu" target="_blank">Engineer Babu</a></div>

    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script src="https://www.youtube.com/iframe_api"></script>
    <script>
        // Add your JavaScript logic here
    </script>
</body>
</html>
    """
    return html_template

# Command handler for /start
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("Welcome! Please upload a .txt file containing URLs.")

# Message handler for file uploads
@app.on_message(filters.document)
async def handle_file(client: Client, message: Message):
    # Check if the file is a .txt file
    if not message.document.file_name.endswith(".txt"):
        await message.reply_text("Please upload a .txt file.")
        return

    try:
        # Download the file
        file_path = await message.download()
        file_name = message.document.file_name

        # Read the file content
        with open(file_path, "r") as f:
            file_content = f.read()

        # Extract names and URLs
        urls = extract_names_and_urls(file_content)

        # Categorize URLs
        videos, pdfs, others = categorize_urls(urls)

        # Generate HTML
        html_content = generate_html(file_name, videos, pdfs, others)
        html_file_path = file_path.replace(".txt", ".html")
        with open(html_file_path, "w") as f:
            f.write(html_content)

        # Send the HTML file to the user
        await message.reply_document(
            document=html_file_path,
            caption=f"✅ Successfully Done!\n\n📥 Extracted By: Engineers Babu™\n\n📅 {datetime.now().strftime('%A %d %B, %Y | ⏰ %I:%M:%S %p')}"
        )

        # Forward the .txt file to the channel
        await client.send_document(
            chat_id=CHANNEL_USERNAME,
            document=file_path,
            caption=f"📥 User: @{message.from_user.username}\n\n📅 {datetime.now().strftime('%A %d %B, %Y | ⏰ %I:%M:%S %p')}"
        )

    except Exception as e:
        await message.reply_text(f"An error occurred: {str(e)}")
    finally:
        # Clean up files
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(html_file_path):
            os.remove(html_file_path)

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()