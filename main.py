
import os
import re
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# Replace these with your credentials
API_ID = "21705536"
API_HASH = "c5bb241f6e3ecf33fe68a444e288de2d"
BOT_TOKEN = "7694154149:AAF2RNkhIkTnYqt4uG9AaqQyJwHKQp5fzpE"

# Initialize the Pyrogram client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to extract MPD and KEY_STRING from the JSON response
def extract_mpd_and_keys(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        mpd_url = data.get("MPD", "")
        key_string = data.get("KEY_STRING", "")
        return mpd_url, key_string
    except Exception as e:
        print(f"Error extracting MPD and keys: {e}")
        return None, None

# Function to replace raw_url with final_url in the text file
def replace_urls_in_file(file_path):
    with open(file_path, 'r') as file:
        content = file.read()

    # Regex to find raw_url
    raw_url_pattern = re.compile(r'https://media-cdn\.classplusapp\.com/drm/[^\s]+')
    new_content = content

    for match in raw_url_pattern.finditer(content):
        raw_url = match.group(0)
        new_url = f"https://dragoapi.vercel.app/classplus?link={raw_url}"
        mpd_url, key_string = extract_mpd_and_keys(new_url)
        if mpd_url and key_string:
            final_url = f"{mpd_url} {key_string}"
            new_content = new_content.replace(raw_url, final_url)

    # Write the modified content to a new file
    new_file_path = file_path.replace('.txt', '_modified.txt')
    with open(new_file_path, 'w') as new_file:
        new_file.write(new_content)

    return new_file_path

# Handler for /start command
@app.on_message(filters.command("start"))
def start(client: Client, message: Message):
    message.reply_text("Send me a .txt file to process!")

# Handler for receiving documents
@app.on_message(filters.document)
def handle_file(client: Client, message: Message):
    # Check if the file is a .txt file
    if message.document.file_name.endswith('.txt'):
        # Download the file
        file_path = message.download(file_name=message.document.file_name)
        
        # Process the file
        new_file_path = replace_urls_in_file(file_path)
        
        # Send the modified file back to the user
        message.reply_document(new_file_path)
        
        # Clean up: Delete the original and modified files
        os.remove(file_path)
        os.remove(new_file_path)
    else:
        message.reply_text("Please send a .txt file.")

# Start the bot
print("Bot is running...")
app.run()
