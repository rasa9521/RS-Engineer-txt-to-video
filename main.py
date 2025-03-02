import os
import requests
import subprocess
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
        new_url = url
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
        elif "pdf*" in url:
            new_url = f"https://dragoapi.vercel.app/pdf/{url}"
            pdfs.append((name, new_url))
        elif "pdf" in url:
            pdfs.append((name, url))
        else:
            others.append((name, url))

    return videos, pdfs, others

# Function to generate HTML file with Video.js player
def generate_html(file_name, videos, pdfs, others):
    file_name_without_extension = os.path.splitext(file_name)[0]

    video_links = "".join(f'<a href="#" onclick="playVideo(\'{url}\')">{name}</a>' for name, url in videos)
    pdf_links = "".join(f'<a href="{url}" target="_blank">{name}</a>' for name, url in pdfs)
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
    <div class="header">
        {file_name_without_extension}
        <div class="subheading">📥 Extracted By: <a href="https://t.me/Engineers_Babu" target="_blank">Engineers Babu™</a></div>
    </div>

    <div id="video-player">
        <video id="engineer-babu-player" class="video-js vjs-default-skin" controls preload="auto" width="640" height="360">
            <p class="vjs-no-js">
                To view this video please enable JavaScript, and consider upgrading to a web browser that
                <a href="https://videojs.com/html5-video-support/" target="_blank">supports HTML5 video</a>
            </p>
        </video>
    </div>

    <div id="url-input-container">
        <input type="text" id="url-input" placeholder="Enter video URL to play...">
        <button onclick="playCustomUrl()">Play</button>
    </div>

    <button onclick="toggleUrlInput()" style="margin: 20px auto; padding: 10px 20px; background: #007bff; color: white; border: none; border-radius: 5px; cursor: pointer; display: block; width: 90%; max-width: 600px;">Enter Custom URL</button>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search for videos, PDFs, or other resources..." oninput="filterContent()">
    </div>

    <div id="noResults" class="no-results">No results found.</div>

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

    <div class="footer">Extracted By - <a href="https://t.me/Engineers_Babu" target="_blank">Engineers Babu</a></div>

    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script>
        const player = videojs('engineer-babu-player', {{
            controls: true,
            autoplay: false,
            preload: 'auto',
            fluid: true,
            controlBar: {{
                children: [
                    'playToggle',
                    'volumePanel',
                    'currentTimeDisplay',
                    'timeDivider',
                    'durationDisplay',
                    'progressControl',
                    'liveDisplay',
                    'remainingTimeDisplay',
                    'customControlSpacer',
                    'playbackRateMenuButton',
                    'chaptersButton',
                    'descriptionsButton',
                    'subsCapsButton',
                    'audioTrackButton',
                    'fullscreenToggle'
                ]
            }}
        }});

        function playVideo(url) {{
            if (url.includes('.m3u8')) {{
                document.getElementById('video-player').style.display = 'block';
                player.src({{ src: url, type: 'application/x-mpegURL' }});
                player.play().catch(() => {{
                    window.open(url, '_blank');
                }});
            }} else {{
                window.open(url, '_blank');
            }}
        }}

        function toggleUrlInput() {{
            const urlInputContainer = document.getElementById('url-input-container');
            urlInputContainer.style.display = urlInputContainer.style.display === 'none' ? 'block' : 'none';
        }}

        function playCustomUrl() {{
            const url = document.getElementById('url-input').value;
            if (url) {{
                playVideo(url);
            }}
        }}

        function showContent(tabName) {{
            const contents = document.querySelectorAll('.content');
            contents.forEach(content => {{
                content.style.display = 'none';
            }});
            const selectedContent = document.getElementById(tabName);
            if (selectedContent) {{
                selectedContent.style.display = 'block';
            }}
            filterContent();
        }}

        function filterContent() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            const categories = ['videos', 'pdfs', 'others'];
            let hasResults = false;

            categories.forEach(category => {{
                const items = document.querySelectorAll(`#${{category}} .${{category}}-list a`);
                let categoryHasResults = false;

                items.forEach(item => {{
                    const itemText = item.textContent.toLowerCase();
                    if (itemText.includes(searchTerm)) {{
                        item.style.display = 'block';
                        categoryHasResults = true;
                        hasResults = true;
                    }} else {{
                        item.style.display = 'none';
                    }}
                }});

                const categoryHeading = document.querySelector(`#${{category}} h2`);
                if (categoryHeading) {{
                    categoryHeading.style.display = categoryHasResults ? 'block' : 'none';
                }}
            }});

            const noResultsMessage = document.getElementById('noResults');
            if (noResultsMessage) {{
                noResultsMessage.style.display = hasResults ? 'none' : 'block';
            }}
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            showContent('videos');
        }});
    </script>
</body>
</html>
    """
    return html_template

# Function to download video using FFmpeg
def download_video(url, output_path):
    try:
        command = f"ffmpeg -i {url} -c copy {output_path}"
        subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error downloading video: {e}")

# Command handler for /start
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("𝐖𝐞𝐥𝐜𝐨𝐦𝐞! 𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐩𝐥𝐨𝐚𝐝 𝐚 .𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐜𝐨𝐧𝐭𝐚𝐢𝐧𝐢𝐧𝐠 𝐔𝐑𝐋𝐬.")

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

        # Send the HTML file to the user with a thumbnail
        thumbnail_url = ""
        await message.reply_document(
            document=html_file_path,
            caption="✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐃𝐨𝐧𝐞!\n\n📥 𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 : 𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚™",
            thumb=thumbnail_url,
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
