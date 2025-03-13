import os
from pyrogram import Client, filters
from bs4 import BeautifulSoup

# Replace these with your credentials
API_ID = "21705536"
API_HASH = "c5bb241f6e3ecf33fe68a444e288de2d"
BOT_TOKEN = "7694154149:AAF2RNkhIkTnYqt4uG9AaqQyJwHKQp5fzpE"

# Initialize the Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function to extract URLs and names from HTML
def extract_urls_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    link_items = soup.find_all('div', class_='link-item')
    
    extracted_data = []
    for item in link_items:
        link_name = item.find('span', class_='link-name').text.strip()
        link_url = item.find('button', class_='link-button')['onclick']
        link_url = link_url.split("'")[1]  # Extract URL from onclick attribute
        extracted_data.append(f"{link_name} : {link_url}")
    
    return extracted_data

# Handler for document messages
@app.on_message(filters.document)
async def handle_document(client, message):
    # Check if the document is an HTML file
    if message.document.mime_type == "text/html":
        # Download the HTML file
        file_path = await message.download()
        
        # Read the HTML content
        with open(file_path, 'r', encoding='utf-8') as file:
            html_content = file.read()
        
        # Extract URLs and names
        extracted_data = extract_urls_from_html(html_content)
        
        # Create a .txt file with the extracted data
        txt_file_path = "extracted_urls.txt"
        with open(txt_file_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write("\n".join(extracted_data))
        
        # Send the .txt file back to the user
        await message.reply_document(txt_file_path)
        
        # Clean up files
        os.remove(file_path)
        os.remove(txt_file_path)
    else:
        await message.reply("Please send an HTML file.")

# Start the bot
app.run()
