import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import re
import asyncio

# Set up logging to see what your bot is doing
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)

# --- Configuration ---
# You must replace these with your actual values.
# Get your bot token from @BotFather on Telegram.
BOT_TOKEN = "8330541351:AAEFleMbw_y6VOGBep0bDXrvDDeIhAAYj7o"

# The unique identifier for your Telegram channel.
# To find your channel ID, you can forward any message from your channel to the @RawDataBot.
# It will provide the chat_id in the message details, which will be a negative number.
CHANNEL_ID = -1002912079466

# --- Bot Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends a welcome message and explains how to use the bot."""
    user = update.effective_user
    await update.message.reply_html(
        f"Hi {user.mention_html()}! I'm a bot that can download a sticker pack and upload all its stickers to a channel. To use me, type /download_stickers followed by the link to the sticker pack.\n\n"
        f"Example: /download_stickers https://t.me/addstickers/animals\n\n"
        f"Please note that the bot needs to be an administrator in the channel where you want to send the stickers.",
    )

async def download_stickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Downloads all stickers from a given sticker pack URL and uploads them
    to the specified channel.
    """
    # Check if a sticker pack URL was provided
    if not context.args:
        await update.message.reply_text("Please provide a sticker pack URL after the command.")
        return

    sticker_pack_url = context.args[0]
    
    # Use a regular expression to extract the sticker set name from the URL
    match = re.search(r't\.me/addstickers/(.*)', sticker_pack_url)
    if not match:
        await update.message.reply_text("Invalid sticker pack URL. Please use a link like 'https://t.me/addstickers/StickerPackName'.")
        return

    sticker_set_name = match.group(1)

    await update.message.reply_text(f"Fetching stickers from the pack '{sticker_set_name}'...")

    try:
        # Get the sticker set object from the Telegram API
        sticker_set = await context.bot.get_sticker_set(name=sticker_set_name)
        stickers_count = len(sticker_set.stickers)
        
        await update.message.reply_text(f"Found {stickers_count} stickers. Starting to upload them to the channel...")

        # Loop through each sticker in the set and send it to the channel
        for i, sticker in enumerate(sticker_set.stickers):
            # Add a small delay between sending each sticker to avoid flood control errors.
            await context.bot.send_sticker(chat_id=CHANNEL_ID, sticker=sticker.file_id)
            if i < stickers_count - 1:
                await asyncio.sleep(0.5)  # Sleep for 0.5 seconds

        await update.message.reply_text("All stickers have been successfully uploaded to the channel!")

    except TypeError as e:
        # This specific error handler is for the version mismatch issue
        logging.error(f"A TypeError occurred: {e}")
        await update.message.reply_text(
            "It looks like your python-telegram-bot library is out of date. "
            "Please update it by running: `pip install --upgrade python-telegram-bot`"
        )
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        await update.message.reply_text(f"An unexpected error occurred while processing your request: {e}")
        # Send a more user-friendly error message for common issues
        if "sticker set is not found" in str(e):
            await update.message.reply_text("Could not find the sticker pack. Please double-check the URL.")
        elif "bot is not an administrator" in str(e):
            await update.message.reply_text("I cannot send messages to that channel. Please make sure I'm an administrator with the 'Post Messages' permission.")

def main():
    """Starts the bot."""
    # Build the Application and pass it your bot's token.
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download_stickers", download_stickers))

    # Run the bot
    logging.info("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

