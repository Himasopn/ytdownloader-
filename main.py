import telebot
from telebot import types
import yt_dlp
import os

TOKEN = os.getenv("TOKEN")  # Heroku ke config se token lega

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "👋 Hello! Send me a YouTube link to download.")

@bot.message_handler(func=lambda message: "youtube.com" in message.text or "youtu.be" in message.text)
def get_video(message):
    url = message.text
    markup = types.InlineKeyboardMarkup()
    markup.add(
        types.InlineKeyboardButton("🎥 360p", callback_data=f"360p|{url}"),
        types.InlineKeyboardButton("🎥 720p", callback_data=f"720p|{url}"),
        types.InlineKeyboardButton("🎧 Audio", callback_data=f"audio|{url}")
    )
    bot.send_message(message.chat.id, "Choose format:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    quality, url = call.data.split("|")
    bot.send_message(call.message.chat.id, f"⬇️ Downloading {quality}...")

    ydl_opts = {}
    file_name = "video.mp4"

    if quality == "audio":
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': 'audio.%(ext)s',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        file_name = "audio.mp3"
    else:
        ydl_opts = {
            'format': f'bestvideo[height<={quality[:-1]}]+bestaudio/best',
            'outtmpl': 'video.%(ext)s',
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        bot.send_message(call.message.chat.id, "✅ Uploading...")
        with open(file_name, "rb") as f:
            bot.send_document(call.message.chat.id, f)

    except Exception as e:
        bot.send_message(call.message.chat.id, f"❌ Error: {e}")

    finally:
        for f in ["video.mp4", "audio.mp3"]:
            if os.path.exists(f):
                os.remove(f)

bot.polling()
