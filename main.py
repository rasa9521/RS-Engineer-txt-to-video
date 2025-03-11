
import os
import re
import subprocess
import shutil
from pyrogram import Client, filters
from pyrogram.types import Message
from n_m3u8dl import NM3U8DL

# Constants
# Replace these with your credentials
API_ID = "21705536"
API_HASH = "c5bb241f6e3ecf33fe68a444e288de2d"
BOT_TOKEN = "7694154149:AAF2RNkhIkTnYqt4uG9AaqQyJwHKQp5fzpE"
OUTPUT_DIR = 'output'  # Directory to store temporary files

# Ensure output directory exists
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Initialize Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

def extract_decryption_key(url):
    # Extract the decryption key from the URL
    match = re.search(r'--key\s+([a-f0-9]+:[a-f0-9]+)\s+--key\s+([a-f0-9]+:[a-f0-9]+)\s+--key\s+([a-f0-9]+:[a-f0-9]+)', url)
    if match:
        return f"--key {match.group(1)} --key {match.group(2)} --key {match.group(3)}"
    return None

def download_video(url, name):
    # Download the video using n_m3u8
    downloader = NM3U8DL(url, output_dir=OUTPUT_DIR, save_name=name)
    downloader.download()

def decrypt_files(video_file, audio_file, key):
    # Decrypt video and audio files using Bento4's mp4decrypt
    decrypted_video = os.path.join(OUTPUT_DIR, f'decrypted_{os.path.basename(video_file)}')
    decrypted_audio = os.path.join(OUTPUT_DIR, f'decrypted_{os.path.basename(audio_file)}')
    
    # Decrypt video
    subprocess.run(['mp4decrypt', *key.split(), video_file, decrypted_video])
    # Decrypt audio
    subprocess.run(['mp4decrypt', *key.split(), audio_file, decrypted_audio])

def combine_audio_video(video_file, audio_file, output_file):
    # Combine audio and video using ffmpeg
    subprocess.run(['ffmpeg', '-i', video_file, '-i', audio_file, '-c', 'copy', output_file])

@app.on_message(filters.document & filters.regex(r'\.txt$'))
async def handle_txt_file(client: Client, message: Message):
    # Download the .txt file sent by the user
    txt_file = await message.download(file_name=os.path.join(OUTPUT_DIR, "urls.txt"))

    # Read the URL from the .txt file
    with open(txt_file, 'r') as file:
        url = file.readline().strip()  # Read the first line as the URL

    # Extract the name from the URL or use a default name
    name = "video"  # Default name
    if "/drm/wv" in url:
        # Extract name from URL or use a default
        name_match = re.search(r'/([^/]+)\.mpd', url)
        if name_match:
            name = name_match.group(1)

    # Step 1: Extract the decryption key from the URL
    decryption_key = extract_decryption_key(url)
    if not decryption_key:
        await message.reply_text("Decryption key not found in the URL.")
        return

    # Step 2: Download the video
    await message.reply_text("Downloading video...")
    download_video(url, name)

    # Define file paths
    video_file = os.path.join(OUTPUT_DIR, f'{name}.mp4')
    audio_file = os.path.join(OUTPUT_DIR, f'{name}_audio.mp4')

    # Step 3: Decrypt the video and audio
    await message.reply_text("Decrypting video and audio...")
    decrypt_files(video_file, audio_file, decryption_key)

    # Define decrypted file paths
    decrypted_video = os.path.join(OUTPUT_DIR, f'decrypted_{name}.mp4')
    decrypted_audio = os.path.join(OUTPUT_DIR, f'decrypted_{name}_audio.mp4')

    # Step 4: Combine audio and video
    await message.reply_text("Combining audio and video...")
    final_video = os.path.join(OUTPUT_DIR, f'final_{name}.mp4')
    combine_audio_video(decrypted_video, decrypted_audio, final_video)

    # Step 5: Send the video to the user
    await message.reply_text("Sending video to you...")
    await message.reply_video(final_video)

    # Clean up temporary files
    shutil.rmtree(OUTPUT_DIR, ignore_errors=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

# Start the bot
print("Bot is running...")
app.run()
