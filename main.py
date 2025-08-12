import requests
from telethon import TelegramClient, events
from config import BOT_TOKEN, API_ID, API_HASH, TMDB_API, IMDB_API

bot = TelegramClient('movie_bot', API_ID, API_HASH).start(bot_token=BOT_TOKEN)

def get_tmdb_data(title):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API}&query={title}"
    res = requests.get(url).json()
    if res.get("results"):
        movie = res["results"][0]
        return {
            "title": movie.get("title"),
            "overview": movie.get("overview"),
            "poster": f"https://image.tmdb.org/t/p/w500{movie.get('poster_path')}" if movie.get("poster_path") else None,
            "release_date": movie.get("release_date"),
            "rating": movie.get("vote_average")
        }
    return None

def get_imdb_data(imdb_id):
    url = f"{IMDB_API}?id={imdb_id}"
    return requests.get(url).json()

@bot.on(events.NewMessage(pattern="/movie"))
async def movie_handler(event):
    query = event.message.text.replace("/movie", "").strip()
    if not query:
        await event.reply("Please provide a movie name. Example:\n`/movie The Pickup`")
        return

    tmdb_data = get_tmdb_data(query)
    if not tmdb_data:
        await event.reply("Movie not found ❌")
        return

    # Example fixed OTT, genres, etc. (You can modify to fetch dynamically)
    caption = f"""
✨ ᴛɪᴛʟᴇ : {tmdb_data['title']} ({tmdb_data['release_date'][:4] if tmdb_data['release_date'] else 'N/A'})

🎭 ɢᴇɴʀᴇs : Action, Comedy
📺 ᴏᴛᴛ        : Amazon Prime Video
🎞️ ǫᴜᴀʟɪᴛʏ : 1080p, 720p, Web DL
🎧 ᴀᴜᴅɪᴏ    : Hindi 
🔥 ʀᴀᴛɪɴɢ   : {tmdb_data['rating']}

❗️❗️Now Available on our website ❗️❗️

💥Visit Now:-  https://filmy4uhd.vercel.app/mov/30445556 ⭐
"""

    if tmdb_data["poster"]:
        await bot.send_file(event.chat_id, tmdb_data["poster"], caption=caption)
    else:
        await event.reply(caption)

print("Bot is running...")
bot.run_until_disconnected()