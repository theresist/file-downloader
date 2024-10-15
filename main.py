import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext

# Google Custom Search API Key and Custom Search Engine ID
API_KEY = 'AIzaSyA7WHDVkjy43QtSoE8XPZB96jcxsLjW9q4'
SEARCH_ENGINE_ID = 'a46cd15dbd5924154'

# Telegram Bot Token
BOT_API_TOKEN = '6454133526:AAFMG9qJUO1RziEY4s_DzursYY4351dOnD8'

# Function to search and download images
def download_image(query, download_dir):
    # Validate the API key and search engine ID
    if not API_KEY or not SEARCH_ENGINE_ID:
        raise ValueError("Google API Key or Search Engine ID is missing.")

    # Construct the search URL
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&cx={SEARCH_ENGINE_ID}&searchType=image&key={API_KEY}"
    response = requests.get(search_url)

    # Check for a successful response
    if response.status_code != 200:
        print(f"Failed to fetch search results: {response.status_code}")
        return None

    data = response.json()

    # Check if the API returned any images
    if 'items' not in data or len(data['items']) == 0:
        print("No images found for the query.")
        return None

    # Get the URL of the first image
    image_url = data['items'][0]['link']

    # Extract the file extension from the image URL
    file_extension = os.path.splitext(image_url)[-1]
    if not file_extension:
        print(f"Could not determine the file extension for the image URL: {image_url}")
        return None

    # Define the path for saving the image, using the correct extension
    download_path = os.path.join(download_dir, f"{query}{file_extension}")

    # Check if the download directory exists, and create it if necessary
    if not os.path.exists(download_dir):
        os.makedirs(download_dir)

    # Download and save the image
    try:
        img_data = requests.get(image_url).content
        with open(download_path, 'wb') as img_file:
            img_file.write(img_data)
        return download_path
    except Exception as e:
        print(f"Failed to download the image: {str(e)}")
        return None

# Command to start the bot
async def start(update: Update, context: CallbackContext):
    await update.message.reply_text("Hi! Send me a name or keyword, and I'll try to download an image for you.")

# Function to handle text messages
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text
    await update.message.reply_text(f"Searching for a picture of '{text}'...")

    # Define where to save the image
    download_dir = "/tmp"

    try:
        # Download the image
        downloaded_image = download_image(text, download_dir)
        if downloaded_image:
            # Send the image back to the user
            await update.message.reply_photo(photo=open(downloaded_image, 'rb'))
        else:
            await update.message.reply_text("No image found for that search term.")
    except Exception as e:
        print(f"Error occurred: {str(e)}")  # Log the error for debugging
        await update.message.reply_text(f"Failed to download the image: {str(e)}")

# Set up the bot
def main():
    # Validate the Telegram Bot Token
    if not BOT_API_TOKEN:
        raise ValueError("Telegram Bot API Token is missing.")

    application = Application.builder().token(BOT_API_TOKEN).build()

    # Handlers for the bot commands and messages
    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
