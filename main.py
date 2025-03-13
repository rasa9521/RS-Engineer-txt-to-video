import os
from pyrogram import Client, filters
from bs4 import BeautifulSoup

# Replace these with your credentials
API_ID = "21705536"
API_HASH = "c5bb241f6e3ecf33fe68a444e288de2d"
BOT_TOKEN = "7480080731:AAGGgo9o_t9pmWsgT8lVO3PJ4OjPhLg2Aoo"

# Initialize the Pyrogram Client
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

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
        
        # Try extracting URLs using the specific structure first
        extracted_data = extract_specific_urls(html_content)
        
        # If no URLs are found, fall back to general <a> tag extraction
        if not extracted_data:
            extracted_data = extract_general_urls(html_content)
        
        if extracted_data:
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
            await message.reply("No URLs found in the HTML file.")
    else:
        await message.reply("Please send an HTML file.")

# Start the bot
print("Bot is running...")
app.run()
