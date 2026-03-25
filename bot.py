import logging
import asyncio
import os
import yt_dlp
import re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# --- AYARLAR ---
TOKEN = '7991569721:AAFQXQXSjXfk1tBZd8FtyyDwhhW7RRJbnik'
user_url_storage = {}
SAVE_PATH = "/sdcard/Download/Video Downloader Telegram"

if not os.path.exists(SAVE_PATH):
    try: os.makedirs(SAVE_PATH)
    except: SAVE_PATH = "downloads"

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Selam dostum! Ben senin akıllı medya asistanınım. ✨\n\nLinkini bana gönder, senin için en iyi seçenekleri hemen hazırlayayım! 🚀")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    if not url.startswith("http"):
        await update.message.reply_text("🧐 Bu pek linke benzemiyor dostum, tekrar kontrol eder misin? ❤️")
        return

    user_id = update.message.from_user.id
    user_url_storage[user_id] = url

    # Hızlı Analiz Mesajı
    status_msg = await update.message.reply_text("🔍 Hemen bakıyorum, beklemede kal... ✨")

    try:
        # Akıllı Analiz (Hızlı mod)
        ydl_opts_info = {'quiet': True, 'no_warnings': True, 'nocheckcertificate': True}
        with yt_dlp.YoutubeDL(ydl_opts_info) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=False)
            width = info.get('width', 0)
            height = info.get('height', 0)
            is_vertical = height > width if height and width else False

        # --- DİNAMİK BUTONLAR ---
        keyboard = []
        
        # Eğer video dikeyse (Shorts/Reels)
        if is_vertical:
            keyboard.append([InlineKeyboardButton("📱 Dikey İndir (Orijinal)", callback_data="fmt|best")])
            keyboard.append([InlineKeyboardButton("🖥️ Yatay Formata Zorla (Geniş)", callback_data="fmt|horizontal")])
        else:
            keyboard.append([InlineKeyboardButton("🎬 Full HD Video", callback_data="fmt|1080")])
            keyboard.append([InlineKeyboardButton("📽️ Standart Video", callback_data="fmt|720")])

        # Ortak Butonlar
        keyboard.append([InlineKeyboardButton("🎵 En İyi Kalite MP3", callback_data="fmt|mp3")])
        keyboard.append([InlineKeyboardButton("🖼️ Fotoğraf Olarak Al", callback_data="fmt|img")])

        await status_msg.edit_text("✅ İşte senin için bulduklarım! Hangisini yapalım? 👇", 
                                   reply_markup=InlineKeyboardMarkup(keyboard))
    
    except Exception as e:
        await status_msg.edit_text("😔 Üzgünüm, bu linki tam çözemedim. Başka bir tane deneyelim mi? 🌸")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    url = user_url_storage.get(user_id)
    fmt_choice = query.data.split('|')[1]
    
    msg = await query.edit_message_text("⚡ Harika seçim! Hemen hazırlıyorum, çok az kaldı... 🏃‍♂️💨")

    # HIZLANDIRILMIŞ İNDİRME AYARLARI
    ydl_opts = {
        'outtmpl': f'{SAVE_PATH}/%(title)s.%(ext)s',
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'noplaylist': True,
        'concurrent_fragment_downloads': 10, # 🚀 ÇOK DAHA HIZLI İNDİRME
        'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    }

    # Format Mantığı
    if fmt_choice == "mp3": ydl_opts['format'] = 'bestaudio/best'
    elif fmt_choice == "horizontal": ydl_opts['format'] = 'bestvideo[aspect_ratio>1]+bestaudio/best'
    elif fmt_choice == "img": ydl_opts['format'] = 'bestimage/best'
    else: ydl_opts['format'] = 'best'

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = await asyncio.to_thread(ydl.extract_info, url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            await msg.edit_text("🎉 İşte hazır! Keyfini çıkar dostum! 🎈")
            with open(filename, 'rb') as f:
                if fmt_choice == "img":
                    await context.bot.send_photo(chat_id=query.message.chat_id, photo=f)
                else:
                    await context.bot.send_document(chat_id=query.message.chat_id, document=f)
            # Telefonunda kalması için silmiyoruz
        else:
            await msg.edit_text("😥 Dosya bir şekilde kayboldu, tekrar denemeye ne dersin? ✨")

    except Exception as e:
        await msg.edit_text("⚠️ Bir aksilik oldu ama pes etmek yok! Başka bir linke bakalım. ❤️")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_click))
    print("🚀 Akıllı ve Samimi Botun Yayında!"); app.run_polling()

if __name__ == '__main__': main()
