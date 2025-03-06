import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Replace with your API credentials
API_ID = "21705536"
API_HASH = "c5bb241f6e3ecf33fe68a444e288de2d"
BOT_TOKEN = "7694154149:AAF2RNkhIkTnYqt4uG9AaqQyJwHKQp5fzpE"

# Telegram channel where files will be forwarded
CHANNEL_USERNAME = "engineerbabuxtfiles"  

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
        elif ".m3u8" in url:
            videos.append((name, url))
        elif "pdf" in url:
            pdfs.append((name, url))
        else:
            others.append((name, url))

    return videos, pdfs, others

# Function to generate HTML file
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
        body {{ text-align: center; background: #f5f7fa; }}
        .header {{ background: linear-gradient(90deg, #007bff, #6610f2); color: white; padding: 15px; font-size: 24px; font-weight: bold; }}
        .container {{ display: flex; justify-content: space-around; margin: 30px auto; width: 80%; }}
        .tab {{ flex: 1; padding: 20px; background: white; cursor: pointer; transition: 0.3s; border-radius: 10px; font-size: 20px; font-weight: bold; }}
        .content {{ display: none; margin-top: 20px; }}
        .active {{ display: block; }}
        .video-list, .pdf-list, .other-list a {{ display: block; padding: 10px; margin: 5px 0; font-weight: bold; }}
        .search-bar {{ margin: 20px auto; width: 80%; max-width: 600px; }}
        .search-bar input {{ width: 100%; padding: 10px; font-size: 16px; }}
        .no-results {{ color: red; font-weight: bold; margin-top: 20px; display: none; }}
        #video-player {{ display: none; margin: 20px auto; width: 80%; max-width: 800px; }}
        .download-button a {{ background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; }}
    </style>
</head>
<body>
    <div class="header">{file_name_without_extension}</div>
    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search..." oninput="filterContent()">
    </div>
    <div id="noResults" class="no-results">No results found.</div>
    <div id="video-player">
        <video id="player" class="video-js vjs-default-skin" controls></video>
        <div class="download-button"><a id="download-link" href="#" download>Download Video</a></div>
    </div>
    <div class="container">
        <div class="tab" onclick="showContent('videos')">Videos</div>
        <div class="tab" onclick="showContent('pdfs')">PDFs</div>
        <div class="tab" onclick="showContent('others')">Others</div>
    </div>
    <div id="videos" class="content">{video_links}</div>
    <div id="pdfs" class="content">{pdf_links}</div>
    <div id="others" class="content">{other_links}</div>
    <script>
        function showContent(tabName) {{
            document.querySelectorAll('.content').forEach(el => el.style.display = 'none');
            document.getElementById(tabName).style.display = 'block';
            filterContent();
        }}

        function filterContent() {{
            const searchTerm = document.getElementById('searchInput').value.toLowerCase();
            let hasResults = false;
            ['videos', 'pdfs', 'others'].forEach(category => {{
                let found = false;
                document.querySelectorAll(`#${{category}} a`).forEach(item => {{
                    if (item.textContent.toLowerCase().includes(searchTerm)) {{
                        item.style.display = 'block';
                        found = true;
                        hasResults = true;
                    }} else {{
                        item.style.display = 'none';
                    }}
                }});
                document.getElementById(category).style.display = found ? 'block' : 'none';
            }});
            document.getElementById('noResults').style.display = hasResults ? 'none' : 'block';
        }}

        function playVideo(url) {{
            document.getElementById('video-player').style.display = 'block';
            document.getElementById('player').src = url;
            document.getElementById('download-link').href = url;
        }}

        document.addEventListener('DOMContentLoaded', () => {{
            showContent('videos');
        }});
    </script>
</body>
</html>
    """
    return html_template

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("Welcome! Upload a .txt file with URLs.")

@app.on_message(filters.document)
async def handle_file(client: Client, message: Message):
    file_path = await message.download()
    with open(file_path, "r") as f:
        urls = extract_names_and_urls(f.read())

    videos, pdfs, others = categorize_urls(urls)
    html_content = generate_html(message.document.file_name, videos, pdfs, others)
    
    html_file_path = file_path.replace(".txt", ".html")
    with open(html_file_path, "w") as f:
        f.write(html_content)

    await message.reply_document(document=html_file_path, caption="✅ Done!")
    os.remove(file_path)
    os.remove(html_file_path)

app.run()
