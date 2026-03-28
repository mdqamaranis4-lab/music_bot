import os
import yt_dlp
from telethon import TelegramClient, events

# --- Configuration (Koyeb Environment Variables se lega) ---
API_ID = int(os.getenv('API_ID', '36209925'))
API_HASH = os.getenv('API_HASH', '59e1a8970239f845b05d7a5adc2e2af1')
BOT_TOKEN = os.getenv('BOT_TOKEN', '8151473210:AAFT7oO_g5x91ZqPstB3Pq2Bw9_m6-rVv0s')

# Bot client setup
bot = TelegramClient('music_bot_session', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def download_audio(query):
    file_name = f"{query[:10].replace(' ', '_')}.mp3"
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
    await event.respond("👋 **Music Bot Online Hai!**\n\nBas gaane ka naam likh kar bhejein.")

@bot.on(events.NewMessage)
async def handle_music(event):
    if event.text.startswith('/'): return
    
    song_name = event.text
    status = await event.respond(f"🔍 `{song_name}` dhoond raha hoon...")

    try:
        title, file_path = download_audio(song_name)
        await status.edit(f"📥 `{title}` upload ho raha hai...")
        
        await bot.send_file(
            event.chat_id, 
            file_path, 
            caption=f"🎵 **{title}**",
            voice_note=False # Audio file ki tarah bhejne ke liye
        )
        
        if os.path.exists(file_path):
            os.remove(file_path)
        await status.delete()

    except Exception as e:
        await status.edit(f"❌ Error: {str(e)}")

print("🚀 Bot is running 24/7...")
bot.run_until_disconnected()
