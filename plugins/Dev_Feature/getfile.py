# This code has been modified by @Safaridev
# Please do not remove this credit
from utils import temp
from utils import get_poster
from info import POST_CHANNELS
from googletrans import Translator
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

translator = Translator()

async def get_hindi(plot):
    try:
        translated = translator.translate(plot, dest='hi')
        return translated.text
    except Exception as e:
        print(f"Translation Error: {e}")
        return plot
        
@Client.on_message(filters.command('getfile'))
async def getfile(client, message):
    try:
        query = message.text.split(" ", 1) 
        if len(query) < 2:
            return await message.reply_text("<b>Usage:</b> /getfile <movie_name>\n\nExample: /getfile Money Heist")
        file_name = query[1].strip() 
        movie_details = await get_poster(file_name)
        
        if not movie_details:
            return await message.reply_text(f"No results found for {file_name} on IMDB.")

        poster = movie_details.get('poster', None)
        movie_title = movie_details.get('title', 'N/A')
        rating = movie_details.get('rating', 'N/A')
        genres = movie_details.get('genres', 'N/A')
        plot = movie_details.get('plot', 'N/A')
        year = movie_details.get('year', 'N/A')
        hindi_plot = await get_hindi(plot)
        
        custom_link = f"https://t.me/{temp.U_NAME}?start=getfile-{file_name.replace(' ', '-').lower()}"
        safari_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Get File 📁", url=custom_link)
        ]])
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Yes", callback_data=f"post_yes_{file_name}"),
             InlineKeyboardButton("No", callback_data=f"post_no_{file_name}")]
        ])
        
        if poster:
            await message.reply_photo(
                poster,
                caption=(
                    f"<b>🔖Title: {movie_title}</b>\n"
                    f"<b>🎬 Genres: {genres}</b>\n"
                    f"<b>⭐️ Rating: {rating}/10</b>\n"
                    f"<b>📆 Year: {year}</b>\n\n"
                    f"📕 Story: {hindi_plot}"
                ),
                reply_markup=safari_markup,
                parse_mode=enums.ParseMode.HTML,
            )
            await message.reply_text("Do you want to post this content on POST_CAHNNELS ?",
                reply_markup=reply_markup)
        else:
            await message.reply_text(
                (
                    f"<b>🔖Title: {movie_title}</b>\n"
                    f"<b>🎬 Genres: {genres}</b>\n"
                    f"<b>⭐️ Rating: {rating}/10</b>\n"
                    f"<b>📆 Year: {year}</b>\n\n"
                    f"📕 Story: {hindi_plot}"
                ),
                reply_markup=safari_markup,
                parse_mode=enums.ParseMode.HTML,
            )
            await message.reply_text("Do you want to post this content on POST_CAHNNEL ?",
                reply_markup=reply_markup)
    except Exception as e:
        await message.reply_text(f"Error: {str(e)}")

@Client.on_callback_query(filters.regex(r'^post_(yes|no)_'))
async def post_to_channels(client, callback_query):
    action, file_name = callback_query.data.split('_')[1], callback_query.data.split('_')[2]
    
    if action == "yes":
        movie_details = await get_poster(file_name)
        
        if not movie_details:
            return await callback_query.message.reply_text(f"No results found for {file_name} on IMDB.")
        
        poster = movie_details.get('poster', None)
        movie_title = movie_details.get('title', 'N/A')
        rating = movie_details.get('rating', 'N/A')
        genres = movie_details.get('genres', 'N/A')
        plot = movie_details.get('plot', 'N/A')
        year = movie_details.get('year', 'N/A')
        hindi_plot = await get_hindi(plot)
        
        custom_link = f"https://t.me/{temp.U_NAME}?start=getfile-{file_name.replace(' ', '-').lower()}"
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("Get File 📁", url=custom_link)
        ]])
        for channel_id in POST_CHANNELS:
            try:
                if poster:
                    await client.send_photo(
                        chat_id=channel_id,
                        photo=poster,
                        caption=(
                            f"<b>🔖Title: {movie_title}</b>\n"
                            f"<b>🎬 Genres: {genres}</b>\n"
                            f"<b>⭐️ Rating: {rating}/10</b>\n"
                            f"<b>📆 Year: {year}</b>\n\n"
                            f"📕 Story: {hindi_plot}"
                        ),
                        reply_markup=reply_markup,
                        parse_mode=enums.ParseMode.HTML
                    )
                else:
                    await client.send_message(
                        chat_id=channel_id,
                        text=(
                            f"<b>🔖Title: {movie_title}</b>\n"
                            f"<b>🎬 Genres: {genres}</b>\n"
                            f"<b>⭐️ Rating: {rating}/10</b>\n"
                            f"<b>📆 Year: {year}</b>\n\n"
                            f"📕 Story: {hindi_plot}"
                        ),
                        reply_markup=reply_markup,
                        parse_mode=enums.ParseMode.HTML
                    )
            except Exception as e:
                await callback_query.message.reply_text(f"Error posting to channel {channel_id}: {str(e)}")
        
        await callback_query.message.edit_text("Movie details successfully posted to channels.")
    
    elif action == "no":
        await callback_query.message.edit_text("Movie details will not be posted to channels.")
