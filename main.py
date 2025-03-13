import re
import os
from pyrogram import Client, filters
from pyrogram.types import Message

# Initialize Pyrogram client
app = Client(
    "html_converter_bot",
    api_id="21705536",
    api_hash="c5bb241f6e3ecf33fe68a444e288de2d",
    bot_token="7694154149:AAF2RNkhIkTnYqt4uG9AaqQyJwHKQp5fzpE"
)

def parse_content(lines):
    """
    Parse the content of the .txt file into a structured dictionary.
    """
    structure = {}
    for line in lines:
        if not line.strip():
            continue
        
        # Extract components using regex
        parts = re.findall(r'\((.*?)\)', line)
        url = re.search(r'https?://\S+', line).group()
        
        if not parts or not url:
            continue
            
        # Extract title and resource type
        title_part = line.split(':')[0]
        title = re.sub(r'\([^)]*\)', '', title_part).strip()
        resource_type = 'video' if 'm3u8' in url else 'pdf'
        pdf_version = None
        
        # Check for pdf versions
        if '(pdf-2)' in line:
            resource_type = 'pdf'
            pdf_version = 2
        elif '(pdf)' in line:
            resource_type = 'pdf'
            pdf_version = 1
        
        # Build hierarchy
        current = structure
        for part in parts[:-1]:  # Last part is author (perospero)
            if part not in current:
                current[part] = {}
            current = current[part]
        
        # Add resource
        if title not in current:
            current[title] = {}
        
        if resource_type == 'video':
            current[title]['video'] = url
        else:
            if 'pdfs' not in current[title]:
                current[title]['pdfs'] = {}
            current[title]['pdfs'][f'pdf{"" if pdf_version == 1 else "-2"}'] = url
    
    return structure

def generate_html(structure, title):
    """
    Generate HTML content from the parsed structure.
    """
    html_template = f"""<!DOCTYPE html>
<html>
    <head>
        <title>{title}</title>
        <meta content="width=device-width, initial-scale=1" name="viewport"/>
        <link href="https://devsfiles.netlify.app/stiq.css" rel="stylesheet"/>
        <link href="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.css" rel="stylesheet"/>
        <script src="https://code.jquery.com/jquery-1.11.3.min.js"></script>
        <script src="https://code.jquery.com/mobile/1.4.5/jquery.mobile-1.4.5.min.js"></script>
    </head>
    <body>
        <div data-role="page" id="pageone">
            <div data-role="header">
                <h1>{title}</h1>
            </div>
            <div class="ui-content" data-role="main">
                {{content}}
            </div>
            <div data-role="footer">
                <h1>Made with ❤️ By @Engineer_Babu</h1>
            </div>
        </div>
    </body>
</html>"""
    
    def build_section(data, level=0):
        html = []
        for key, value in data.items():
            if level == 0:
                html.append('<div data-role="collapsible">')
                html.append(f'<h1>{key}</h1>')
                html.append(build_section(value, level+1))
                html.append('</div>')
            elif isinstance(value, dict):
                if 'video' in value or 'pdfs' in value:
                    # Resource item
                    html.append('<div data-role="collapsible">')
                    html.append(f'<h1>{key}</h1>')
                    
                    if 'video' in value:
                        html.append(f'<p class="video"><a class="studyiq" href="{value["video"]}" target="__blank">Click Here</a></p>')
                    
                    if 'pdfs' in value:
                        for pdf_name, pdf_url in value['pdfs'].items():
                            html.append('<div data-role="collapsible">')
                            html.append(f'<h1>{pdf_name}</h1>')
                            html.append(f'<p class="video"><a class="studyiq" href="{pdf_url}" target="__blank">Click Here</a></p>')
                            html.append('</div>')
                    
                    html.append('</div>')
                else:
                    # Subcategory
                    html.append('<div data-role="collapsible">')
                    html.append(f'<h1>{key}</h1>')
                    html.append(build_section(value, level+1))
                    html.append('</div>')
        return '\n'.join(html)
    
    content = build_section(structure)
    return html_template.format(content=content)

@app.on_message(filters.document)
async def handle_document(client: Client, message: Message):
    """
    Handle incoming .txt files and convert them to HTML.
    """
    try:
        # Check if the file is a .txt file
        if not message.document.file_name.endswith('.txt'):
            await message.reply("Please send a .txt file.")
            return
        
        # Download the file
        file_path = await message.download()
        
        # Read the file content
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Get the title from the file name (without extension)
        title = os.path.splitext(message.document.file_name)[0]
        
        # Parse the content and generate HTML
        structure = parse_content(lines)
        html_content = generate_html(structure, title)
        
        # Save the HTML file
        output_file = f"{title}.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        # Send the HTML file back to the user
        await message.reply_document(output_file)
        
        # Clean up files
        os.remove(file_path)
        os.remove(output_file)
        
    except Exception as e:
        await message.reply(f"Error processing file: {str(e)}")

@app.on_message(filters.command("start"))
async def start(client: Client, message: Message):
    """
    Start command handler.
    """
    await message.reply("Send me a .txt file to convert it into an HTML file!")

if __name__ == "__main__":
    print("Bot is running...")
    app.run()
