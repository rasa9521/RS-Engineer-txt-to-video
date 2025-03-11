import re
from collections import defaultdict
from pyrogram import Client, filters
from pyrogram.types import Message

# Initialize the Pyrogram client
app = Client(
    "my_bot",
    api_id="21705536",  # Replace with your API ID
    api_hash="c5bb241f6e3ecf33fe68a444e288de2d",  # Replace with your API Hash
    bot_token="7694154149:AAF2RNkhIkTnYqt4uG9AaqQyJwHKQp5fzpE"  # Replace with your bot token
)

# Dictionary to store categorized links
categories = defaultdict(list)

# Function to extract name and URL from a line
def extract_name_and_url(line):
    # Regex to match the pattern: "Name: URL"
    match = re.match(r"^(.*?)\s*:\s*(https?://\S+)$", line.strip())
    if match:
        name = match.group(1).strip()
        url = match.group(2).strip()
        return name, url
    return None, None

# Function to categorize links based on the name
def categorize_links(text):
    # Clear previous categories
    categories.clear()

    # Process each line in the text
    for line in text.splitlines():
        name, url = extract_name_and_url(line)
        if name and url:
            # Extract the category from the name (e.g., first word or keyword)
            category = name.split()[0]  # Use the first word as the category
            categories[category].append((name, url))

    return categories

# Function to generate the categorized text file
def generate_categorized_file(categories):
    output = ""
    for category, items in categories.items():
        output += f"=== {category} ===\n"
        for name, url in items:
            output += f"{name}: {url}\n"
        output += "\n"
    return output

# Handler for /start command
@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    await message.reply_text("Welcome! Send me a .txt file, and I'll categorize the links based on their names.")

# Handler for .txt files
@app.on_message(filters.document & filters.regex(r"\.txt$"))
async def handle_file(client: Client, message: Message):
    # Download the file
    file_path = await message.download()

    # Read the file
    with open(file_path, "r") as f:
        text = f.read()

    # Categorize the links
    categorize_links(text)

    # Generate the categorized output
    output = generate_categorized_file(categories)

    # Save the output to a new file
    output_file_path = "categorized_output.txt"
    with open(output_file_path, "w") as f:
        f.write(output)

    # Send the categorized file back to the user
    await message.reply_document(output_file_path, caption="Here is your categorized file!")

# Run the bot
if __name__ == "__main__":
    print("Bot is running...")
    app.run()
