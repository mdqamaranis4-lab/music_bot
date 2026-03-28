import os
import asyncio
import threading
from flask import Flask
from telethon import TelegramClient, events
from youtube_search import YoutubeSearch
import yt_dlp

# --- Flask for Render Health Check ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is Running!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- Bot Configuration ---
API_ID = 36209925
API_HASH = '59e1a8970239f845b05d7a5adc2e2af1'
BOT_TOKEN = '8416504909:AAGQj6B303vvnFSRbMZyriMESZ8prRB6btw'

client = TelegramClient('music_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# --- Audio Downloader ---
def download_audio(url):
    opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'song.mp3',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }
    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.download([url])
    return 'song.mp3'

# --- Events ---
@client.on(events.NewMessage(pattern='/start'))
async def start_cmd(event):
    await event.reply("👋 Hi! Gaane ka naam likho, main download kar dunga.")

@client.on(events.NewMessage)
async def handle_msg(event):
    if event.text.startswith('/') or event.sender_id == (await client.get_me()).id:
        return

    query = event.text
    msg = await event.respond(f"🔍 Searching for: `{query}`...")

    try:
        search = YoutubeSearch(query, max_results=1).to_dict()
        if not search:
            await msg.edit("❌ Gana nahi mila!")
            return

        url = f"https://www.youtube.com/watch?v={search[0]['id']}"
        title = search[0]['title']

        await msg.edit(f"📥 Downloading: `{title}`...")
        file = await asyncio.to_thread(download_audio, url)

        await client.send_file(event.chat_id, file, caption=f"🎵 {title}")
        os.remove(file)
        await msg.delete()
    except Exception as e:
        print(f"Error: {e}")
        await msg.edit("⚠️ Kuch error aaya, please try again.")

if __name__ == "__main__":
    # Start Flask in a separate thread
    threading.Thread(target=run_flask, daemon=True).start()
    print("🚀 Bot is running...")
    client.run_until_disconnected()
