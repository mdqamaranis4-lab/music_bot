import os
import yt_dlp
import threading
import asyncio
from flask import Flask
from telethon import TelegramClient, events

# --- Flask Server (Render ko Active rakhne ke liye) ---
app = Flask(__name__)

@app.route('/')
def hello():
    return "Bot is Running 24/7!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Aapki Details ---
API_ID = 36209925
API_HASH = '59e1a8970239f845b05d7a5adc2e2af1'
BOT_TOKEN = '8416504909:AAGQj6B303vvnFSRbMZyriMESZ8prRB6btw'

bot = TelegramClient('music_bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- Music Download Function ---
def download_audio(query):
    file_name = "song.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_name,
        'default_search': 'ytsearch',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Search karke download karna
        info = ydl.extract_info(f"ytsearch1:{query}", download=True)['entries'][0]
        return info['title'], file_name

# --- Bot Commands ---
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("🎵 **PHONK MUSIC BOT** 🎵\n\nKisi bhi gaane ka naam likhein, main use dhoond kar bhej dunga.")

@bot.on(events.NewMessage)
async def handle_music(event):
    # --- 1. LOOP FIX: Bot khud ke message ignore karega ---
    me = await bot.get_me()
    if event.sender_id == me.id:
        return

    # --- 2. COMMANDS IGNORE ---
    if event.text.startswith('/'):
        return
    
    query = event.text
    status = await event.respond(f"🔍 `{query}` dhoond raha hoon...")

    try:
        # Background mein download karna taaki bot hang na ho
        title, file_path = await asyncio.to_thread(download_audio, query)
        
        await status.edit(f"📥 `{title}` mil gaya! Upload ho raha hai...")
        
        # Audio file bhejna
        await bot.send_file(
            event.chat_id, 
            file_path, 
            caption=f"🎵 **Gaana:** {title}\n✨ Enjoy!",
            voice_note=False
        )
        
        # File delete karna space ke liye
        if os.path.exists(file_path):
            os.remove(file_path)
        await status.delete()

    except Exception as e:
        print(f"Error: {e}")
        await status.edit("😔 Maaf kijiye, ye gaana nahi mil paya. Kuch aur try karein?")

if __name__ == "__main__":
    # Flask ko alag thread mein chalana
    threading.Thread(target=run_flask).start()
    print("🚀 Bot Started and Flask is Live...")
    bot.run_until_disconnected()
