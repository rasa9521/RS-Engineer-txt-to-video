import re
import os
from pyrogram import Client, filters
from pyrogram.types import Message, InputMediaDocument

# Function to extract URLs and their names from the text file
def extract_urls_and_names(text):
    url_pattern = re.compile(r'https?://[^\s]+')
    urls = url_pattern.findall(text)
    names = [url.split('/')[-1].split('.')[0] for url in urls]
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
        elif "pdf" in url:
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
        <title>{batch_name}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                margin: 0;
                padding: 20px;
            }}
            h1 {{
                color: #333;
                text-align: center;
            }}
            .quote {{
                text-align: center;
                font-style: italic;
                color: #555;
                margin-top: 10px;
            }}
            .extracted-by {{
                text-align: center;
                margin-top: 10px;
                font-size: 14px;
                color: #777;
            }}
            .section {{
                background-color: #fff;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            }}
            .section h2 {{
                color: #555;
                border-bottom: 2px solid #ddd;
                padding-bottom: 10px;
            }}
            .link {{
                display: block;
                margin: 10px 0;
                color: #007bff;
                text-decoration: none;
            }}
            .link:hover {{
                text-decoration: underline;
            }}
            .button {{
                display: inline-block;
                padding: 5px 10px;
                background-color: #28a745;
                color: #fff;
                text-decoration: none;
                border-radius: 4px;
                font-size: 14px;
            }}
            .button:hover {{
                background-color: #218838;
            }}
        </style>
    </head>
    <body>
        <h1>{batch_name}</h1>
        <div class="quote">{learning_quote}</div>
        <div class="extracted-by">Extracted By: <a href="https://t.me/Engineers_Babu" target="_blank">Engineer Babu</a></div>
        <div class="section">
            <h2>Videos</h2>
            {"".join(f'<a class="link" href="{url}" target="_blank">{name}</a>' for url, name in videos)}
        </div>
        <div class="section">
            <h2>PDFs</h2>
            {"".join(f'<a class="link" href="{url}" target="_blank">{name}</a> <a class="button" href="{url}" download>Download PDF</a>' for url, name in pdfs)}
        </div>
        <div class="section">
            <h2>Others</h2>
            {"".join(f'<a class="link" href="{url}" target="_blank">{name}</a>' for url, name in others)}
        </div>
    </body>
    </html>
    """

    html_filename = f"{batch_name.replace(' ', '_')}.html"
    with open(html_filename, "w") as file:
        file.write(html_content)
    return html_filename

# Initialize Pyrogram Client
app = Client("my_bot", api_id="YOUR_API_ID", api_hash="YOUR_API_HASH", bot_token="YOUR_BOT_TOKEN")

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

    # Clean up files
    os.remove(file_path)
    os.remove(html_filename)

# Run the bot
if __name__ == "__main__":
    app.run()
