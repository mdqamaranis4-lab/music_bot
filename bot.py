import os
import yt_dlp
import threading
import asyncio
from flask import Flask
from telethon import TelegramClient, events
from youtube_search import YoutubeSearch

app = Flask(__name__)
@app.route('/')
def hello(): return "Bot is Alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

API_ID = 36209925
API_HASH = '59e1a8970239f845b05d7a5adc2e2af1'
BOT_TOKEN = '8416504909:AAGQj6B303vvnFSRbMZyriMESZ8prRB6btw'

bot = TelegramClient('music_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def download_audio(url):
    file_name = "song.mp3"
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': file_name,
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
    return file_name

@bot.on(events.NewMessage)
async def handle_music(event):
    me = await bot.get_me()
    if event.sender_id == me.id or event.text.startswith('/'): return
    
    query = event.text
    status = await event.respond(f"🔍 `{query}` dhoond raha hoon...")

    try:
        # YoutubeSearch se link nikalna (Ye block nahi hota)
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await status.edit("❌ Gaana nahi mila. Kuch aur try karein.")
            return

        video_id = results[0]['id']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        title = results[0]['title']

        await status.edit(f"📥 `{title}` download ho raha hai...")
        
        # Download function call karna
        file_path = await asyncio.to_thread(download_audio, video_url)
        
        await bot.send_file(event.chat_id, file_path, caption=f"🎵 **{title}**")
        
        if os.path.exists(file_path): os.remove(file_path)
        await status.delete()

    except Exception as e:
        print(e)
        await status.edit("❌ Error: Download nahi ho paya.")

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    bot.run_until_disconnected()
