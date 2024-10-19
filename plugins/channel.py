# This code has been modified by @Safaridev
# Please do not remove this credit
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from info import CHANNELS, POST_CHANNELS
from database.ia_filterdb import save_file, get_file_details
from utils import get_poster, get_size, temp
from os import environ
import logging
import re

collected_files = []
post_active = False

media_filter = filters.document | filters.video | filters.audio


@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    global post_active, collected_files

    language_map = {
        "hin": "Hindi",
        "eng": "English",
        "en": "English",
        "tel": "Telugu",
        "tam": "Tamil",
        "jap": "Japanese",
        "mar": "Marathi",
        "guj": "Gujarati",
        "Pun": "Punjabi",
        "Hindi": "Hindi",
        "English": "English",
        "Telugu": "Telugu",
        "Tamil": "Tamil",
        "Japanese": "Japanese",
        "Marathi": "Marathi",
        "Gujarati": "Gujarati",
        "Punjabi": "Punjabi"
        
    }

    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    media.caption = message.caption
    success, file_id = await save_file(media)
    
    if success and file_id:
        file_details = await get_file_details(file_id)
        if file_details:
            file_id = file_details[0]['file_id']
            
    if success and "post count" in (media.caption or "").lower():
        post_active = True
        collected_files = []

    if post_active:
        languages_in_caption = re.findall(r'\b(' + '|'.join(language_map.keys()) + r')\b', media.caption)
        full_languages = ", ".join(language_map[lang] for lang in languages_in_caption)
        updated_caption = f"{media.caption}\n\nLanguage: {full_languages}"
        collected_files.append((file_id, media.file_name.replace('_', ' '), updated_caption, media.file_size))

    if success and "send post" in (media.caption or "").lower():
        post_active = False 

        if collected_files:
            imdb_info = None

            for file_id, file_name, caption, file_size in collected_files:
                size_text = get_size(file_size)
                file_url = f"📁 [{size_text}]👇\n<a href='https://t.me/{temp.U_NAME}?start=files_{CHANNELS[0]}_{file_id}'>{file_name}</a>"

                if imdb_info is None:
                    try:
                        movie_name = caption.split('|')[0].strip()
                        logging.info(f"Searching IMDb for: {movie_name}")
                        imdb_info = await get_poster(movie_name)
                        if not imdb_info:
                            logging.error(f"IMDb information not found for: {movie_name}")
                            return
                    except Exception as e:
                        logging.error(f"Error while fetching IMDb info: {str(e)}")
                        return

            if imdb_info:
                title = imdb_info.get('title', 'N/A')
                rating = imdb_info.get('rating', 'N/A')
                genre = imdb_info.get('genres', 'N/A')
                description = imdb_info.get('plot', 'N/A')
                poster_url = imdb_info.get('poster', None)
                year = imdb_info.get('year', 'N/A')
                
                urls_text = "\n\n".join([f"📁 [{get_size(size)}]👇\n<a href='https://t.me/{temp.U_NAME}?start=files_{CHANNELS[0]}_{file_id}'>{file_name}</a>" for file_id, file_name, caption, size in collected_files])

                language_in_caption = caption.split("Language:")[-1].strip()
                final_caption = f"<b>🏷 Title: {title}\n🎭 Genres: {genre}\n📆 Year: {year}\n🌟 Rating: {rating}\n🔊 Language: {language_in_caption}\n\n{urls_text}</b>"

                for channel in POST_CHANNELS:
                    if poster_url:
                        try:
                            await bot.send_photo(
                                chat_id=channel,
                                photo=poster_url,
                                caption=final_caption,
                                parse_mode=enums.ParseMode.HTML
                            )
                        except Exception as e:
                            logging.error(f"Error sending poster to channel {channel}: {str(e)}")
                            await bot.send_message(
                                chat_id=channel,
                                text=final_caption,
                                parse_mode=enums.ParseMode.HTML
                            )
                    else:
                        url_text = "\n\n".join([f"📁 [{get_size(size)}]👇\n<a href='https://t.me/{temp.U_NAME}?start=files_{CHANNELS[0]}_{file_id}'>{file_name}</a>" for file_id, file_name, caption, size in collected_files])
                        captionn = f"<b>#Information_Not_Available\n\nTotal Files: {len(collected_files)}\n\n{url_text}</b>"
                        await bot.send_message(
                            chat_id=channel,
                            text=captionn,
                            parse_mode=enums.ParseMode.HTML
                        )
        collected_files = []
