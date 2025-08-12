# main.py
import os
from telethon import TelegramClient, events
import requests
from flask import Flask

# Env variables
BOT_TOKEN = os.getenv("BOT_TOKEN", "8347005060:AAHf11nTICnku70OKIcX8OccXr8DlhKa17s")
API_ID = int(os.getenv("API_ID", "26954495"))
API_HASH = os.getenv("API_HASH", "2061c55207cfee4f106ff0dc331fe3d9")
TMDB_API = os.getenv("TMDB_API", "0da8b26f661ce60b48bb5f2876e13c74")
IMDB_API = os.getenv("IMDB_API", "https://imdb-api-lux.wemedia360.workers.dev/")

# Telegram Client
client = TelegramClient("bot", API_ID, API_HASH).start(bot_token=BOT_TOKEN)

# Web server (Render ping prevention)
app = Flask(__name__)

@app.route("/")
def home():
    return "Bot is running!"

# Movie Info Command
@client.on(events.NewMessage(pattern="/movie"))
async def movie_handler(event):
    query = event.text.replace("/movie", "").strip()
    if not query:
        await event.reply("Please provide a movie name. Example: `/movie The Pickup 2025`")
        return

    # TMDB search
    tmdb_url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API}&query={query}"
    tmdb_data = requests.get(tmdb_url).json()

    if not tmdb_data.get("results"):
        await event.reply("Movie not found on TMDB.")
        return

    movie = tmdb_data["results"][0]
    title = movie.get("title", "N/A")
    overview = movie.get("overview", "No description available.")
    release_date = movie.get("release_date", "Unknown")
    rating = movie.get("vote_average", "N/A")
    poster_path = movie.get("poster_path")
    poster_url = f"https://image.tmdb.org/t/p/w500{poster_path}" if poster_path else None

    # IMDb fetch
    imdb_url = f"{IMDB_API}/?q={title}"
    imdb_data = requests.get(imdb_url).json()

    genres = ", ".join([g.get("name") for g in movie.get("genre_ids", [])]) if "genre_ids" in movie else "N/A"

    caption = f"✨ **ᴛɪᴛʟᴇ:** {title}\n" \
              f"🎭 **ɢᴇɴʀᴇs:** {genres}\n" \
              f"📅 **ʀᴇʟᴇᴀsᴇ ᴅᴀᴛᴇ:** {release_date}\n" \
              f"🔥 **ʀᴀᴛɪɴɢ:** {rating}\n\n" \
              f"📝 **ᴏᴠᴇʀᴠɪᴇᴡ:** {overview}"

    if poster_url:
        await event.reply(file=poster_url, message=caption)
    else:
        await event.reply(caption)

if __name__ == "__main__":
    import threading

    def run_flask():
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))

    threading.Thread(target=run_flask).start()
    client.run_until_disconnected()
