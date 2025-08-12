# main.py
import os
import requests
import logging
from threading import Thread
from time import sleep

from flask import Flask
from telethon import TelegramClient, events, errors

from config import BOT_TOKEN, API_ID, API_HASH, TMDB_API, IMDB_API, MOVIE_PAGE_BASE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("movie-bot")

# --- Telegram client (Telethon) ---
client = TelegramClient("movie_bot_session", API_ID, API_HASH)

# Start client with bot token when running
async def start_telethon_bot():
    await client.start(bot_token=BOT_TOKEN)
    logger.info("Telethon bot started.")

# Utility: fetch TMDB details by id or search by name
def tmdb_get_by_id(tmdb_id: str):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API, "append_to_response": "external_ids,credits", "language": "en-US"}
    r = requests.get(url, params=params, timeout=15)
    return r.json() if r.status_code == 200 else None

def tmdb_search(query: str):
    url = "https://api.themoviedb.org/3/search/movie"
    params = {"api_key": TMDB_API, "query": query, "language": "en-US", "page": 1}
    r = requests.get(url, params=params, timeout=15)
    j = r.json() if r.status_code == 200 else {}
    results = j.get("results") or []
    return results[0] if results else None

def imdb_fetch(imdb_id: str):
    if not imdb_id:
        return None
    # IMDB_API assumed to accept ?id=ttXXXXX
    url = f"{IMDB_API}?id={imdb_id}"
    try:
        r = requests.get(url, timeout=12)
        return r.json() if r.status_code == 200 else None
    except Exception:
        return None

def build_caption(tmdb_data: dict, imdb_data: dict = None):
    title = tmdb_data.get("title") or tmdb_data.get("name") or "Unknown Title"
    release_date = tmdb_data.get("release_date") or "N/A"
    year = release_date[:4] if release_date and release_date != "N/A" else ""
    genres = ", ".join([g["name"] for g in tmdb_data.get("genres", [])]) or "N/A"
    rating = tmdb_data.get("vote_average") or "N/A"
    overview = tmdb_data.get("overview") or "No overview available."
    imdb_id = tmdb_data.get("external_ids", {}).get("imdb_id") or ""

    # static placeholders (you can change to dynamic later)
    ott = "Amazon Prime Video"
    qualities = "1080p, 720p, WEB-DL"
    audio = "Hindi"

    tmdb_id = tmdb_data.get("id")
    movie_page = f"{MOVIE_PAGE_BASE}{tmdb_id}" if tmdb_id else MOVIE_PAGE_BASE

    caption = (
        f"✨ ᴛɪᴛʟᴇ : {title} {f'({year})' if year else ''}\n\n"
        f"🎭 ɢᴇɴʀᴇs : {genres}\n"
        f"📅 ʀᴇʟᴇᴀsᴇ ᴅᴀᴛᴇ : {release_date}\n"
        f"📺 ᴏᴛᴛ        : {ott}\n"
        f"🎞️ ǫᴜᴀʟɪᴛʏ : {qualities}\n"
        f"🎧 ᴀᴜᴅɪᴏ    : {audio}\n"
        f"🔥 ʀᴀᴛɪɴɢ   : {rating}\n\n"
        f"❗️❗️Now Available on our website ❗️❗️\n\n"
        f"💥Visit Now:- {movie_page} ⭐\n\n"
        f"📝 Overview:\n{overview}\n"
    )

    if imdb_id:
        caption += f"\n🎬 IMDb: https://www.imdb.com/title/{imdb_id}/"
        if imdb_data:
            imdb_rating = imdb_data.get("imDbRating")
            if imdb_rating:
                caption += f"\n⭐ IMDb Rating: {imdb_rating}"

    return caption

# --- Telethon handlers ---
@client
