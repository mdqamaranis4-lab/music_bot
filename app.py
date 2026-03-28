import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events
from youtube_search import YoutubeSearch
import yt_dlp

# --- MANDATORY FOR RENDER ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Alive!"

# --- BOT CONFIG ---
API_ID = 36209925
API_HASH = '59e1a8970239f845b05d7a5adc2e2af1'
BOT_TOKEN = '8416504909:AAGQj6B303vvnFSRbMZyriMESZ8prRB6btw'

client = TelegramClient('session', API_ID, API_HASH)

def download_audio(url):
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.mp3',
        'quiet': True,
        'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192'}],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return 'song.mp3'

@client.on(events.NewMessage(pattern='/start'))
async def start(event):
    await event.reply("🎵 Send me a song name!")

@client.on(events.NewMessage)
async def handle_msg(event):
    if event.text.startswith('/') or event.sender_id == (await client.get_me()).id:
        return
    query = event.text
    msg = await event.respond(f"🔍 Searching: `{query}`...")
    try:
        search = YoutubeSearch(query, max_results=1).to_dict()
        if not search:
            await msg.edit("❌ Not found!")
            return
        url = f"https://www.youtube.com/watch?v={search[0]['id']}"
        file = await asyncio.to_thread(download_audio, url)
        await client.send_file(event.chat_id, file, caption=f"🎵 {search[0]['title']}")
        os.remove(file)
        await msg.delete()
    except:
        await msg.edit("⚠️ Error. Try again.")

# --- THE FIX: Running both together ---
def run_bot():
    client.start(bot_token=BOT_TOKEN)
    client.run_until_disconnected()

if __name__ == "__main__":
    # Start bot in background
    threading.Thread(target=run_bot).start()
    # Start Flask on the port Render provides
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
