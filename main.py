import os
import sys
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import Message


# Define the owner's user ID
OWNER_ID = 7804396225 # Replace with the actual owner's user ID

# List of sudo users (initially empty or pre-populated)
SUDO_USERS = [7804396225]

AUTH_CHANNEL = -1002690129228

# Function to check if a user is authorized
def is_authorized(user_id: int) -> bool:
    return user_id == OWNER_ID or user_id in SUDO_USERS or user_id == AUTH_CHANNEL
    
# Replace with your API ID, API Hash, and Bot Token
API_ID = "27900743"
API_HASH = "ebb06ea8d41420e60b29140dcee902fc"
BOT_TOKEN = "8003649544:AAGoiThVN8KLJyKGsGf1BcfTsjDTrSmjFR8"
        
# Telegram channel where files will be forwarded
CHANNEL_USERNAME = "@mrkrsrawat"  # Replace with your channel username

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
            new_url = f"https://api.extractor.workers.dev/player?url={url}"
            videos.append((name, new_url))
        elif "media-cdn.classplusapp.com/" in url:
            new_url = f"https://api.extractor.workers.dev/player?url={url}"
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

# Function to generate HTML file with Video.js player, YouTube player, and download feature
def generate_html(file_name, videos, pdfs, others):
    file_name_without_extension = os.path.splitext(file_name)[0]

    video_links = "".join(f'<a href="#" onclick="playVideo(\'{url}\')">{name}</a>' for name, url in videos)
    pdf_links = "".join(f'<a href="{url}" target="_blank">{name}</a> <a href="{url}" download>📥 Download PDF</a>' for name, url in pdfs)
    other_links = "".join(f'<a href="{url}" target="_blank">{name}</a>' for name, url in others)

    html_template = f"""
import os
import re
from bs4 import BeautifulSoup

def txt_to_html(input_file, output_file, base_dir="."):
    """
    TXT फ़ाइल को HTML में बदलता है, जिसमें विषयवार वीडियो और PDF हों।
    """
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        return

    # विषय के आधार पर सामग्री को विभाजित करें
    topics = re.split(r'#\s*(.+?)\n', content)
    topics = [topic for topic in topics if topic.strip()]

    if len(topics) % 2 != 0:
        print("Error: Topics are not properly formatted in the TXT file.")
        return

    # HTML सामग्री बनाएँ
    html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Topic-wise Content</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f4f4f4;
            color: #333;
        }

        h1 {
            color: #0056b3;
            text-align: center;
            margin-bottom: 30px;
        }

        .topic {
            margin-bottom: 20px;
            background-color: #fff;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }

        .topic-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
            color: #0056b3;
        }

        .video-player-container {
            position: relative;
            padding-bottom: 56.25%; /* 16:9 aspect ratio */
            height: 0;
            overflow: hidden;
            margin-bottom: 15px;
        }

        .video-player {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            border: none;
        }

        .link {
            display: block;
            margin-bottom: 5px;
            color: #007bff;
            text-decoration: none;
            transition: color 0.3s ease;
        }

        .link:hover {
            color: #0056b3;
        }

        .error {
            color: #dc3545;
            font-style: italic;
        }
    </style>
</head>
<body>
    <h1>Topic-wise Content</h1>
"""

    for i in range(0, len(topics), 2):
        topic_title = topics[i]
        topic_content = topics[i+1]

        html_content += f"""
    <div class="topic">
        <div class="topic-title">{topic_title}</div>
"""

        # वीडियो लिंक निकालें
        video_links = re.findall(r'\[VIDEO:(.*?)\]', topic_content)
        for video_link in video_links:
            html_content += f"""
        <div class="video-player-container">
            <iframe class="video-player" src="{video_link}" frameborder="0" allowfullscreen></iframe>
        </div>
"""

        # अन्य लिंक निकालें
        links = re.findall(r'(https?://\S+)', topic_content)
        for link in links:
            html_content += f"""
            <a class="link" href="{link}">{link}</a>
"""

        html_content += """
    </div>
"""

    html_content += """
</body>
</html>
"""

    # फ़ाइल में HTML सामग्री लिखें
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        print(f"Successfully converted {input_file} to {output_file}")
    except Exception as e:
        print(f"Error writing to file: {e}")

# उदाहरण उपयोग
input_file = 'input.txt'
output_file = 'output.html'
txt_to_html(input_file, output_file)
</head>
<body>
    <div class="header">{file_name_without_extension}</div>
    <div class="subheading">📥 𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 : <a href="https://t.me/" target="_blank">🚩 𝐉𝐀𝐈 𝐁𝐀𝐉𝐑𝐀𝐍𝐆 𝐁𝐀𝐋𝐈 🚩</a></div>
    <br>
    <p>🔹आप जो सोचते हैं, वही बनते हैं : <a href="https://t.me" target="_blank"> </a></p>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search for videos, PDFs, or other resources..." oninput="filterContent()">
    </div>

    <div id="noResults" class="no-results">No results found.</div>

    <div id="video-player">
        <video id="jai-bajrang-bali-player" class="video-js vjs-default-skin" controls preload="auto" width="640" height="360">
            <p class="vjs-no-js">
                To view this video please enable JavaScript, and consider upgrading to a web browser that
                <a href="https://videojs.com/html5-video-support/" target="_blank">supports HTML5 video</a>
            </p>
        </video>
        <div class="download-button">
            <a id="download-link" href="#" download>Download Video</a>
        </div>
        <div style="text-align: center; margin-top: 10px; font-weight: bold; color: #007bff;">Jai Bajrang Bali Player</div>
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

    <div class="footer">Extracted By - <a href="https://t.me/" target="_blank">𝐉𝐀𝐈 𝐁𝐀𝐉𝐑𝐀𝐍𝐆 𝐁𝐀𝐋𝐈</a></div>

    <script src="https://vjs.zencdn.net/8.10.0/video.min.js"></script>
    <script src="https://www.youtube.com/iframe_api"></script>
    <script>
        const player = videojs('jai-bajrang-bali-player', {{
            controls: true,
            autoplay: false,
            preload: 'auto',
            fluid: true,
        }});

        let youtubePlayer;

        function onYouTubeIframeAPIReady() {{
            youtubePlayer = new YT.Player('player', {{
                height: '360',
                width: '640',
                events: {{
                    'onReady': onPlayerReady,
                }}
            }});
        }}

        function onPlayerReady(event) {{
            // You can add additional functionality here if needed
        }}

        function playVideo(url) {{
            if (url.includes('.m3u8')) {{
                document.getElementById('video-player').style.display = 'block';
                document.getElementById('youtube-player').style.display = 'none';
                player.src({{ src: url, type: 'application/x-mpegURL' }});
                player.play().catch(() => {{
                    window.open(url, '_blank');
                }});
                document.getElementById('download-link').href = url;
            }} else if (url.includes('youtube.com') || url.includes('youtu.be')) {{
                document.getElementById('video-player').style.display = 'none';
                document.getElementById('youtube-player').style.display = 'block';
                const videoId = extractYouTubeId(url);
                youtubePlayer.loadVideoById(videoId);
            }} else {{
                window.open(url, '_blank');
            }}
        }}

        function extractYouTubeId(url) {{
            const regExp = /^.*(youtu.be\/|v\/|u\/\w\/|embed\/|watch\?v=|&v=)([^#&?]*).*/;
            const match = url.match(regExp);
            return (match && match[2].length === 11) ? match[2] : null;
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

# Function to handle file processing
async def process_file(client: Client, message: Message):
    # Check if the file is a .txt file
    if not message.document.file_name.endswith(".txt"):
        await message.reply_text("Please upload a .txt file.")
        return

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
    await message.reply_document(document=html_file_path, caption="✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐃𝐨𝐧𝐞!\n\n📥 𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 : 🚩 𝐉𝐀𝐈 𝐁𝐀𝐉𝐑𝐀𝐍𝐆 𝐁𝐀𝐋𝐈 🚩")

    # Forward the .txt file to the channel
    await client.send_document(chat_id=CHANNEL_USERNAME, document=file_path)

    # Clean up files
    os.remove(file_path)
    os.remove(html_file_path)

# Function to extract names and URLs from an HTML file
def extract_name_urls(html_file):
    """
    Extracts names and their corresponding URLs from an HTML file.

    :param html_file: Path to the HTML file.
    :return: A list of tuples containing (name, url).
    """
    with open(html_file, 'r', encoding='utf-8') as file:
        soup = BeautifulSoup(file, 'html.parser')

    # Assuming names are within <a> tags and URLs are in the 'href' attribute
    name_urls = []
    for a_tag in soup.find_all('a', href=True):
        name = a_tag.text.strip()
        url = a_tag['href']
        if name and url:
            name_urls.append((name, url))

    return name_urls

# Function to write names and URLs to a text file
def write_name_urls_to_txt(name_urls, output_file):
    """
    Writes the extracted names and URLs to a text file in the format 'name : url'.

    :param name_urls: List of tuples containing (name, url).
    :param output_file: Path to the output text file.
    """
    with open(output_file, 'w', encoding='utf-8') as file:
        for name, url in name_urls:
            file.write(f"{name} : {url}\n")
    
# Upload command handler
@app.on_message(filters.command(["start"]))
async def upload(bot: Client, m: Message):
    if not is_authorized(m.chat.id):
        await m.reply_text("**🚫You are not authorized to use this bot.**")
        return

# Command handler for /txt
@app.on_message(filters.command("jaibajrangbali"))
async def txt_command(client: Client, message: Message):
    await message.reply_text("Please upload a .txt file containing URLs.")

# Message handler for file uploads
@app.on_message(filters.document)
async def handle_file(client: Client, message: Message):
    await process_file(client, message)

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
