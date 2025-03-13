import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from datetime import datetime
from bs4 import BeautifulSoup

# Replace with your API ID, API Hash, and Bot Token
API_ID = "21705536"
API_HASH = "c5bb241f6e3ecf33fe68a444e288de2d"
BOT_TOKEN = "7480080731:AAGGgo9o_t9pmWsgT8lVO3PJ4OjPhLg2Aoo"

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
        * {{ margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }}
        body {{ background: #f5f7fa; text-align: center; }}
        .header {{ background: linear-gradient(90deg, #007bff, #6610f2); color: white; padding: 15px; font-size: 24px; font-weight: bold; }}
        .subheading {{ font-size: 18px; margin-top: 10px; color: #555; font-weight: bold; }}
        .subheading a {{ background: linear-gradient(90deg, #ff416c, #ff4b2b); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-decoration: none; font-weight: bold; }}
        .container {{ display: flex; justify-content: space-around; margin: 30px auto; width: 80%; }}
        .tab {{ flex: 1; padding: 20px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); cursor: pointer; transition: 0.3s; border-radius: 10px; font-size: 20px; font-weight: bold; }}
        .tab:hover {{ background: #007bff; color: white; }}
        .content {{ display: none; margin-top: 20px; }}
        .active {{ display: block; }}
        .footer {{ margin-top: 30px; font-size: 18px; font-weight: bold; padding: 15px; background: #1c1c1c; color: white; border-radius: 10px; }}
        .footer a {{ color: #ffeb3b; text-decoration: none; font-weight: bold; }}
        .video-list, .pdf-list, .other-list {{ text-align: left; max-width: 600px; margin: auto; }}
        .video-list a, .pdf-list a, .other-list a {{ display: block; padding: 10px; background: #fff; margin: 5px 0; border-radius: 5px; text-decoration: none; color: #007bff; font-weight: bold; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }}
        .video-list a:hover, .pdf-list a:hover, .other-list a:hover {{ background: #007bff; color: white; }}
        .search-bar {{ margin: 20px auto; width: 80%; max-width: 600px; }}
        .search-bar input {{ width: 100%; padding: 10px; border: 2px solid #007bff; border-radius: 5px; font-size: 16px; }}
        .no-results {{ color: red; font-weight: bold; margin-top: 20px; display: none; }}
        #video-player {{ display: none; margin: 20px auto; width: 80%; max-width: 800px; }}
        #youtube-player {{ display: none; margin: 20px auto; width: 80%; max-width: 800px; }}
        .download-button {{ margin-top: 10px; text-align: center; }}
        .download-button a {{ background: #007bff; color: white; padding: 10px 20px; border-radius: 5px; text-decoration: none; font-weight: bold; }}
        .download-button a:hover {{ background: #0056b3; }}
    </style>
</head>
<body>
    <div class="header">{file_name_without_extension}</div>
    <div class="subheading">📥 𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 : <a href="https://t.me/Engineers_Babu" target="_blank">𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚™</a></div>
    <br>
    <p>🔹𝐔𝐬𝐞 𝐓𝐡𝐢𝐬 𝐁𝐨𝐭 𝐟𝐨𝐫 𝐓𝐗𝐓 𝐭𝐨 𝐇𝐓𝐌𝐋 𝐟𝐢𝐥𝐞 𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐢𝐨𝐧 : <a href="https://t.me/htmldeveloperbot" target="_blank"> @𝐡𝐭𝐦𝐥𝐝𝐞𝐯𝐞𝐥𝐨𝐩𝐞𝐫𝐛𝐨𝐭 🚀</a></p>

    <div class="search-bar">
        <input type="text" id="searchInput" placeholder="Search for videos, PDFs, or other resources..." oninput="filterContent()">
    </div>

    <div class="subheading" id="datetime">📅 {datetime.now().strftime('%A %d %B, %Y | ⏰ %I:%M:%S %p')}</div>

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
        const player = videojs('engineer-babu-player', {{
            controls: true,
            autoplay: false,
            preload: 'auto',
            fluid: true,
            techOrder: ['html5', 'flash'], // Add flash fallback for older browsers
        }});

        let youtubePlayer;

        function onYouTubeIframeAPIReady() {{
            youtubePlayer = new YT.Player('player', {{
                height: '360',
                width: '640',
                playerVars: {{
                    'playsinline': 1, // Play inline on mobile devices
                    'rel': 0, // Disable related videos
                    'modestbranding': 1, // Reduce YouTube branding
                }},
                events: {{
                    'onReady': onPlayerReady,
                    'onError': onPlayerError,
                }}
            }});
        }}

        function onPlayerReady(event) {{
            console.log('YouTube player is ready');
        }}

        function onPlayerError(event) {{
            console.error('YouTube player error:', event.data);
            alert('Error loading YouTube video. Please try again.');
        }}

        function playVideo(url) {{
            if (url.includes('.m3u8') || url.includes('.mp4') || url.includes('.mkv') || url.includes('.webm') || url.includes('.m3u') || url.includes('.epg')) {{
                document.getElementById('video-player').style.display = 'block';
                document.getElementById('youtube-player').style.display = 'none';
                player.src({{ src: url, type: getVideoType(url) }});
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

        function getVideoType(url) {{
            if (url.includes('.m3u8')) return 'application/x-mpegURL';
            if (url.includes('.mp4')) return 'video/mp4';
            if (url.includes('.mkv')) return 'video/x-matroska';
            if (url.includes('.webm')) return 'video/webm';
            if (url.includes('.m3u')) return 'application/x-mpegURL';
            if (url.includes('.epg')) return 'application/x-mpegURL';
            return 'video/mp4';
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

        function updateDateTime() {{
            const now = new Date();
            const options = {{ weekday: 'long', year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: true }};
            const formattedDateTime = now.toLocaleDateString('en-US', options);
            document.getElementById('datetime').textContent = `📅 ${{formattedDateTime}}`;
        }}

        setInterval(updateDateTime, 1000);

        document.addEventListener('DOMContentLoaded', () => {{
            showContent('videos');
            updateDateTime();
        }});
    </script>
</body>
</html>
    """
    return html_template

# Function to extract URLs and names from specific HTML structure
def extract_specific_urls(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    link_items = soup.find_all('div', class_='link-item')
    
    extracted_data = []
    for item in link_items:
        link_name = item.find('span', class_='link-name').text.strip()
        link_url = item.find('button', class_='link-button')['onclick']
        link_url = link_url.split("'")[1]  # Extract URL from onclick attribute
        extracted_data.append(f"{link_name} : {link_url}")
    
    return extracted_data

# Function to extract URLs and names from general HTML <a> tags
def extract_general_urls(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = []

    # Find all <a> tags in the HTML
    for a_tag in soup.find_all('a', href=True):
        url_name = a_tag.text.strip()  # Extract the text content (URL name)
        url = a_tag['href']  # Extract the href attribute (URL)
        if url_name and url:  # Ensure both name and URL are present
            extracted_data.append(f"{url_name} : {url}")
    
    return extracted_data

# Function to extract URLs from onclick attributes in <a> tags
def extract_onclick_urls(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    extracted_data = []

    # Find all <a> tags with onclick attributes
    for a_tag in soup.find_all('a', onclick=True):
        url_name = a_tag.text.strip()  # Extract the text content (URL name)
        onclick_attr = a_tag['onclick']
        
        # Extract URL from the onclick attribute
        if "playVideo(" in onclick_attr:
            url = onclick_attr.split("'")[1]  # Extract URL from playVideo('URL')
            extracted_data.append(f"{url_name} : {url}")
    
    return extracted_data

# Command handler for /start
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("𝐖𝐞𝐥𝐜𝐨𝐦𝐞! 𝐏𝐥𝐞𝐚𝐬𝐞 𝐮𝐩𝐥𝐨𝐚𝐝 𝐚 .𝐭𝐱𝐭 𝐟𝐢𝐥𝐞 𝐜𝐨𝐧𝐭𝐚𝐢𝐧𝐢𝐧𝐠 𝐔𝐑𝐋𝐬 𝐨𝐫 𝐮𝐬𝐞 /𝐡𝐭𝐦𝐥 𝐨𝐫 /𝐭𝐱𝐭 𝐜𝐨𝐦𝐦𝐚𝐧𝐝𝐬.")

# Command handler for /html (TXT to HTML extraction)
@app.on_message(filters.command("html"))
async def html_command(client: Client, message: Message):
    await message.reply_text("Please upload a .txt file for HTML extraction.")

# Command handler for /txt (HTML to TXT extraction)
@app.on_message(filters.command("txt"))
async def txt_command(client: Client, message: Message):
    await message.reply_text("Please upload an HTML file for TXT extraction.")

# Message handler for file uploads (TXT to HTML)
@app.on_message(filters.document & filters.command("html"))
async def handle_txt_file(client: Client, message: Message):
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

    # Calculate totals
    total_videos = len(videos)
    total_pdfs = len(pdfs)
    total_others = len(others)

    # Send the HTML file to the user
    await message.reply_document(
        document=html_file_path,
        caption=f"✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐃𝐨𝐧𝐞!\n\n📥 𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 : 𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚™\n\n📅 {datetime.now().strftime('%A %d %B, %Y | ⏰ %I:%M:%S %p')}\n\n🎞️: {total_videos}, 📖: {total_pdfs}, 🔖: {total_others}"
    )

    # Forward the .txt file to the channel
    await client.send_document(
        chat_id=CHANNEL_USERNAME,
        document=file_path,
        caption=f"📥Used By - @{message.from_user.username}\n\n📅 {datetime.now().strftime('%A %d %B, %Y | ⏰ %I:%M:%S %p')}"
    )

    # Clean up files
    os.remove(file_path)
    os.remove(html_file_path)

# Message handler for file uploads (HTML to TXT)
@app.on_message(filters.document & filters.command("txt"))
async def handle_html_file(client: Client, message: Message):
    # Check if the file is an HTML file
    if not message.document.mime_type == "text/html":
        await message.reply_text("Please upload an HTML file.")
        return

    # Download the HTML file
    file_path = await message.download()
    
    # Read the HTML content
    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Try extracting URLs using the specific structure first
    extracted_data = extract_specific_urls(html_content)
    
    # If no URLs are found, try extracting from general <a> tags
    if not extracted_data:
        extracted_data = extract_general_urls(html_content)
    
    # If still no URLs are found, try extracting from onclick attributes in <a> tags
    if not extracted_data:
        extracted_data = extract_onclick_urls(html_content)
    
    if extracted_data:
        # Create a .txt file with the extracted data
        txt_file_path = "extracted_urls.txt"
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write("\n".join(extracted_data))
        
        # Send the .txt file back to the user
        await message.reply_document(
            txt_file_path,
            caption=f"✅ 𝐒𝐮𝐜𝐜𝐞𝐬𝐬𝐟𝐮𝐥𝐥𝐲 𝐃𝐨𝐧𝐞!\n\n📥 𝐄𝐱𝐭𝐫𝐚𝐜𝐭𝐞𝐝 𝐁𝐲 : 𝕰𝖓𝖌𝖎𝖓𝖊𝖊𝖗𝖘 𝕭𝖆𝖇𝖚™\n\n📅 {datetime.now().strftime('%A %d %B, %Y | ⏰ %I:%M:%S %p')}"
        )
        
        # Clean up files
        os.remove(file_path)
        os.remove(txt_file_path)
    else:
        await message.reply("No URLs found in the HTML file.")

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
