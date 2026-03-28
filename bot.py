import os
import yt_dlp
import threading
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from youtube_search import YoutubeSearch

# --- Flask Server (Render isse active rehta hai) ---
app = Flask(__name__)

@app.route('/')
def health_check():
    return "Bot is Running!"

def run_flask():
    # Render default port 10000 use karta hai
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Details ---
API_ID = 36209925
API_HASH = '59e1a8970239f845b05d7a5adc2e2af1'
BOT_TOKEN = '8416504909:AAGQj6B303vvnFSRbMZyriMESZ8prRB6btw'

client = TelegramClient('phonk_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- Audio Download Logic ---
def download_audio(url):
    file_name = "song.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_name,
        'quiet': True,
        'no_warnings': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return file_name

# --- Handlers ---
@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.respond("🎵 **PHONK MUSIC BOT** 🎵\n\nGaane ka naam likhein, main dhoond kar bhej dunga!")

@client.on(events.NewMessage)
async def handle_music(event):
    # Loop Fix: Bot apne messages ko ignore karega
    me = await client.get_me()
    if event.sender_id == me.id or event.text.startswith('/'):
        return
    
    query = event.text
    status = await event.respond(f"🔍 `{query}` dhoond raha hoon...")

    try:
        # Search Fix: YoutubeSearch ka use
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await status.edit("❌ Maaf kijiye, gaana nahi mila.")
            return

        video_id = results[0]['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        title = results[0]['title']

        await status.edit(f"📥 `{title}` download ho raha hai...")
        
        # Download in background
        file_path = await asyncio.to_thread(download_audio, video_url)
        
        # Uploading
        await client.send_file(event.chat_id, file_path, caption=f"🎵 **{title}**\n\n✨ @PhonkMusicBot")
        
        if os.path.exists(file_path):
            os.remove(file_path)
        await status.delete()

    except Exception as e:
        print(f"Error: {e}")
        await status.edit("❌ Kuch error aaya. Dubara koshish karein.")

if __name__ == "__main__":
    # Web server start
    threading.Thread(target=run_flask).start()
    print("🚀 Bot is live!")
    client.run_until_disconnected()
