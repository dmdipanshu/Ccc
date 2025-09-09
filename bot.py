
import os
from telegram import Update, InputFile
from telegram.ext import Application, CommandHandler, ContextTypes
from telegram.constants import ParseMode

TOKEN = "8330541351:AAEFleMbw_y6VOGBep0bDXrvDDeIhAAYj7o"  # BotFather token
CHANNEL_ID = "-1002912079466"  # Or channel ID like -100xxxxxxxxxx

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send me a sticker pack link like:\n`/get https://t.me/addstickers/PackName`", parse_mode=ParseMode.MARKDOWN)

async def get_stickers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ Please provide a sticker pack link!\nUsage: `/get <link>`", parse_mode=ParseMode.MARKDOWN)
        return

    link = context.args[0]
    if not link.startswith("https://t.me/addstickers/"):
        await update.message.reply_text("❌ Invalid link! Must be a Telegram sticker pack link.")
        return

    pack_name = link.split("/")[-1]

    # Fetch sticker set
    sticker_set = await context.bot.get_sticker_set(pack_name)

    await update.message.reply_text(f"📦 Downloading {len(sticker_set.stickers)} stickers from *{sticker_set.title}* …", parse_mode=ParseMode.MARKDOWN)

    for idx, sticker in enumerate(sticker_set.stickers, start=1):
        # Download sticker file
        file = await context.bot.get_file(sticker.file_id)
        file_path = f"sticker_{idx}.webp"
        await file.download_to_drive(file_path)

        # Upload to channel
        await context.bot.send_document(chat_id=CHANNEL_ID, document=InputFile(file_path), caption=f"Sticker {idx}/{len(sticker_set.stickers)}")

        os.remove(file_path)  # cleanup

    await update.message.reply_text("✅ All stickers uploaded to channel!")

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("get", get_stickers))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
