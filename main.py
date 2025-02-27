import re
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaDocument

# Function to extract URLs and their names from the text file
def extract_urls_and_names(text):
    # Regex to match the pattern: <name>:<url>
    pattern = re.compile(r"([^:]+):\s*(https?://[^\s]+)")
    matches = pattern.findall(text)
    
    # Extract names and URLs
    names = [match[0].strip() for match in matches]
    urls = [match[1].strip() for match in matches]
    
    return urls, names
    
# Function to categorize URLs
def categorize_urls(urls, names):
    videos = []
    pdfs = []
    others = []

    for url, name in zip(urls, names):
        if "media-cdn.classplusapp.com/drm/" in url or "cpvod.testbook" in url:
            new_url = f"https://dragoapi.vercel.app/video/{url}"
            videos.append((new_url, name))
        elif "pdf" in url.lower():
            pdfs.append((url, name))
        else:
            others.append((url, name))

    return videos, pdfs, others

# Function to generate HTML file
def generate_html_file(filename, videos, pdfs, others):
    # Extract Batch Name from the file name
    batch_name = filename.replace(".txt", "").replace("_", " ").title()

    # Learning Quote
    learning_quote = "The beautiful thing about learning is that no one can take it away from you. - B.B. King"

    # HTML Content
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Batch Dashboard</title>
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.2/css/all.min.css">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; font-family: Arial, sans-serif; }
            body { background: #f5f7fa; text-align: center; }
            .header { background: linear-gradient(90deg, #007bff, #6610f2); color: white; padding: 15px; font-size: 24px; font-weight: bold; }
            .subheading { font-size: 18px; margin-top: 10px; color: #555; }
            .container { display: flex; justify-content: space-around; margin: 30px auto; width: 80%; }
            .tab { flex: 1; padding: 20px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); cursor: pointer; transition: 0.3s; border-radius: 10px; font-size: 20px; font-weight: bold; }
            .tab:hover { background: #007bff; color: white; }
            .content { display: none; margin-top: 20px; }
            .active { display: block; }
            .footer { margin-top: 30px; font-size: 18px; font-weight: bold; padding: 15px; background: #007bff; color: white; border-radius: 10px; }
            .footer a { color: #ffeb3b; text-decoration: none; font-weight: bold; }
            .video-list, .pdf-list, .other-list { text-align: left; max-width: 600px; margin: auto; }
            .video-list a, .pdf-list a, .other-list a { display: block; padding: 10px; background: #fff; margin: 5px 0; border-radius: 5px; text-decoration: none; color: #007bff; font-weight: bold; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1); }
            .video-list a:hover, .pdf-list a:hover, .other-list a:hover { background: #007bff; color: white; }
        </style>
    </head>
    <body>
        <div class="header">{batch_name}</div>
        <div class="subheading">Your one-stop destination for Learning</div>
    
        <div class="container">
            <div class="tab" onclick="toggleContent('videos')">Videos</div>
            <div class="tab" onclick="toggleContent('pdfs')">PDFs</div>
            <div class="tab" onclick="toggleContent('others')">Others</div>
        </div>
        
        <div id="videos" class="content">
            <h2>All Video Lectures</h2>
            <div class="video-list">
                {"".join(f'<a class="link" href="{url}" target="_blank">{name}</a>' for url, name in videos)}
            </div>
        </div>
        
        <div id="pdfs" class="content">
            <h2>All PDFs</h2>
            <div class="pdf-list">
                {"".join(f'<a class="link" href="{url}" target="_blank">{name}</a> <a class="button" href="{url}" download>Download PDF</a>' for url, name in pdfs)}
            </div>
        </div>
        
        <div id="others" class="content">
            <h2>Other Resources</h2>
            <div class="other-list">
                {"".join(f'<a class="link" href="{url}" target="_blank">{name}</a>' for url, name in others)}
            </div>
        </div>
        
        <div class="footer">Extracted By - <a href="https://t.me/Engineers_Babu" target="_blank">Engineer Babu</a></div>

        <script>
            function toggleContent(tabName) {
                const content = document.getElementById(tabName);
                if (content.classList.contains('active')) {
                    content.classList.remove('active');
                } else {
                    document.querySelectorAll('.content').forEach(el => el.classList.remove('active'));
                    content.classList.add('active');
                }
            }
        </script>
    </body>
    </html>
    """
    
    html_filename = f"{batch_name.replace(' ', '_')}.html"
    with open(html_filename, "w") as file:
        file.write(html_content)
    return html_filename

# Initialize Pyrogram Client
app = Client("my_bot", api_id="21705536", api_hash="c5bb241f6e3ecf33fe68a444e288de2d", bot_token="8013725761:AAF5p78PE7RSeKIQ0LNDiBE4bjn9tJqYRn4")

# Start Command Handler
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("Welcome! Please upload a .txt file.")

# File Handler
@app.on_message(filters.document)
async def handle_file(client: Client, message: Message):
    if not message.document.file_name.endswith(".txt"):
        await message.reply_text("Please upload a .txt file.")
        return

    try:
        # Download the file
        file_path = await message.download()
        with open(file_path, "r") as f:
            text = f.read()

        # Process the file
        urls, names = extract_urls_and_names(text)
        videos, pdfs, others = categorize_urls(urls, names)
        html_filename = generate_html_file(message.document.file_name, videos, pdfs, others)

        # Send the HTML file back to the user
        await message.reply_document(document=html_filename)

    except Exception as e:
        await message.reply_text(f"An error occurred: {e}")

    finally:
        # Clean up files
        if os.path.exists(file_path):
            os.remove(file_path)
        if os.path.exists(html_filename):
            os.remove(html_filename)

# Run the bot
if __name__ == "__main__":
    app.run()
