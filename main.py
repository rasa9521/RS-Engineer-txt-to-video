import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Replace with your API ID, API Hash, and Bot Token
API_ID = "21705536"
API_HASH = "c5bb241f6e3ecf33fe68a444e288de2d"
BOT_TOKEN = "8013725761:AAGQyr32ibk7HQNqxv4FSD2ZrrSLOmzknlg"

# Telegram channel where files will be forwarded
CHANNEL_USERNAME = "engineerbabuxtfiles"  # Replace with your channel username

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
        if "media-cdn.classplusapp.com/drm/" in url or "cpvod.testbook" in url:
            new_url = f"https://dragoapi.vercel.app/video/{url}"
            videos.append((name, new_url))
        elif "/master.mpd" in url:
            vid_id = url.split("/")[-2]
            new_url = f"https://player.muftukmall.site/?id={vid_id}"
            videos.append((name, new_url))
        elif "youtube.com/embed" in url:
            yt_id = url.split("/")[-1]
            new_url = f"https://www.youtube.com/watch?v={yt_id}"
            videos.append((name, new_url))
        elif ".m3u8" in url:
            videos.append((name, url))
        elif "pdf" in url.lower():
            pdfs.append((name, url))
        else:
            others.append((name, url))

    return videos, pdfs, others

# Function to generate HTML file with Video.js player
def generate_html(file_name, videos, pdfs, others):
    file_name_without_extension = os.path.splitext(file_name)[0]

    video_links = "".join(f'<a href="#" onclick="playVideo(\'{url}\')">{name}</a><br>' for name, url in videos)
    pdf_links = "".join(f'<a href="{url}" target="_blank">{name}</a><br>' for name, url in pdfs)
    other_links = "".join(f'<a href="{url}" target="_blank">{name}</a><br>' for name, url in others)

    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{file_name_without_extension}</title>
    <link href="https://vjs.zencdn.net/8.10.0/video-js.css" rel="stylesheet" />
    <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; }}
        .tab {{ cursor: pointer; padding: 10px; background: #f0f0f0; margin: 5px; }}
        .content {{ display: none; padding: 10px; border: 1px solid #ccc; }}
        .active {{ display: block; }}
    </style>
</head>
<body>
    <h1>{file_name_without_extension}</h1>
    <div class="tab" onclick="showContent('videos')">Videos</div>
    <div class="tab" onclick="showContent('pdfs')">PDFs</div>
    <div class="tab" onclick="showContent('others')">Others</div>

    <div id="videos" class="content">
        <h2>Video Lectures</h2>
        {video_links}
    </div>
    <div id="pdfs" class="content">
        <h2>PDFs</h2>
        {pdf_links}
    </div>
    <div id="others" class="content">
        <h2>Other Resources</h2>
        {other_links}
    </div>

    <div id="video-player">
        <video id="engineer-babu-player" class="video-js vjs-default-skin" controls preload="auto" width="640" height="360">
            <p class="vjs-no-js">
                To view this video please enable JavaScript, and consider upgrading to a web browser that
                <a href="https://videojs.com/html5-video-support/" target="_blank">supports HTML5 video</a>
            </p>
        </video>
    </div>

    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script>
        const player = videojs('engineer-babu-player', {{
            controls: true,
            autoplay: false,
            preload: 'auto',
            fluid: true
        }});

        function playVideo(url) {{
            if (url.includes('.m3u8')) {{
                document.getElementById('video-player').style.display = 'block';
                player.src({{ src: url, type: 'application/x-mpegURL' }});
                player.play();
            }} else {{
                window.open(url, '_blank');
            }}
        }}

        function showContent(tabName) {{
            const contents = document.querySelectorAll('.content');
            contents.forEach(content => content.style.display = 'none');
            document.getElementById(tabName).style.display = 'block';
        }}

        // Show videos tab by default
        showContent('videos');
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
            caption="✅ Successfully processed your file!\n\n📥 Extracted By: Engineers Babu™"
        )

        # Forward the .txt file to the channel
        await client.send_document(chat_id=CHANNEL_USERNAME, document=file_path)

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")
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
