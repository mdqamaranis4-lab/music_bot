import os
import yt_dlp
import threading
from flask import Flask
from telethon import TelegramClient, events

# --- Render ke liye Web Server ---
app = Flask(__name__)

@app.route('/')
def hello():
    return "Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Bot ki Details ---
API_ID = 36209925
API_HASH = '59e1a8970239f845b05d7a5adc2e2af1'
BOT_TOKEN = '8416504909:AAGQj6B303vvnFSRbMZyriMESZ8prRB6btw'

bot = TelegramClient('music_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def download_audio(query):
    file_name = "song.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_name,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'quiet': True,
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{query}", download=True)['entries'][0]
        return info['title'], file_name

@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("🎵 **Music Bot Shuru Ho Gaya!**\n\nKisi bhi gaane ka naam likh kar bhejein.")

@bot.on(events.NewMessage)
async def handle_music(event):
    if event.text.startswith('/'): return
    
    query = event.text
    status = await event.respond(f"🔍 `{query}` dhoond raha hoon...")

    try:
        title, file_path = download_audio(query)
        await status.edit(f"📥 `{title}` upload ho raha hai...")
        await bot.send_file(event.chat_id, file_path, caption=f"🎵 **{title}**")
        
        if os.path.exists(file_path):
            os.remove(file_path)
        await status.delete()
    except Exception as e:
        await status.edit(f"❌ Error: Gaana nahi mila.")

if __name__ == "__main__":
    # Web server ko background mein chalana
    threading.Thread(target=run_flask).start()
    print("🚀 Bot Started...")
    bot.run_until_disconnected()
