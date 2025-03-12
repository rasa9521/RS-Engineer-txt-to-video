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
        print(f"Fetching data from URL: {url}")
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        mpd_url = data.get("MPD", "")
        key_string = data.get("KEY_STRING", "")
        print(f"Extracted MPD: {mpd_url}")
        print(f"Extracted KEY_STRING: {key_string}")
        return mpd_url, key_string
    except Exception as e:
        print(f"Error extracting MPD and keys: {e}")
        return None, None

# Function to replace raw_url with final_url in the text file while preserving the name
def replace_urls_in_file(file_path):
    try:
        with open(file_path, 'r') as file:
            content = file.read()

        # Regex to find URLs while preserving the name
        url_pattern = re.compile(r'(.*?)(https://media-cdn\.classplusapp\.com/drm/[^\s]+)')
        new_content = content

        for match in url_pattern.finditer(content):
            name = match.group(1).strip()  # Extract the name
            raw_url = match.group(2)  # Extract the URL
            print(f"Processing URL: {raw_url}")
            new_url = f"https://dragoapi.vercel.app/classplus?link={raw_url}"
            mpd_url, key_string = extract_mpd_and_keys(new_url)
            if mpd_url and key_string:
                final_url = f"{mpd_url} {key_string}"
                # Replace only the URL while keeping the name intact
                new_content = new_content.replace(raw_url, final_url)
                print(f"Replaced URL: {final_url}")

        # Write the modified content to a new file
        new_file_path = file_path.replace('.txt', '_modified.txt')
        with open(new_file_path, 'w') as new_file:
            new_file.write(new_content)

        print(f"New file created: {new_file_path}")
        return new_file_path
    except Exception as e:
        print(f"Error in replace_urls_in_file: {e}")
        return None

# Handler for /start command
@app.on_message(filters.command("start"))
def start(client: Client, message: Message):
    message.reply_text("Send me a .txt file to process!")

# Handler for receiving documents
@app.on_message(filters.document)
def handle_file(client: Client, message: Message):
    try:
        # Check if the file is a .txt file
        if message.document.file_name.endswith('.txt'):
            # Download the file
            print(f"Downloading file: {message.document.file_name}")
            file_path = message.download(file_name=message.document.file_name)
            print(f"File downloaded to: {file_path}")

            # Process the file
            new_file_path = replace_urls_in_file(file_path)
            if new_file_path:
                # Send the modified file back to the user
                print(f"Sending modified file: {new_file_path}")
                message.reply_document(new_file_path)
                
                # Clean up: Delete the original and modified files
                os.remove(file_path)
                os.remove(new_file_path)
                print("Temporary files deleted.")
            else:
                message.reply_text("Error processing the file. Please try again.")
        else:
            message.reply_text("Please send a .txt file.")
    except Exception as e:
        print(f"Error in handle_file: {e}")
        message.reply_text("An error occurred. Please try again.")

# Start the bot
print("Bot is running...")
app.run()
