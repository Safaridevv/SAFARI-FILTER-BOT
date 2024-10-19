import os, asyncio
from pyrogram import Client, filters
from pyrogram.types import *
from telegraph import upload_file


@Client.on_message(filters.command("telegraph") & filters.private)
async def telegraph_upload(bot, update):
    replied = update.reply_to_message
    if not replied:
        return await update.reply_text("Reply to a photo or video.")
    
    if not (replied.photo or replied.video):
        return await update.reply_text("Please reply with a valid media.")
    
    text = await update.reply_text("<code>Downloading...</code>", disable_web_page_preview=True)
    media = await replied.download()   
    await text.edit_text("<code>Uploading...</code>", disable_web_page_preview=True)                                            
    
    try:
        response = upload_file(media)
    except Exception as error:
        print(error)
        return await text.edit_text(text=f"Error: {error}", disable_web_page_preview=True)
    
    try:
        os.remove(media)
    except Exception as error:
        print(error)
        return
    
    # Access the first item of the response list
    await text.edit_text(
        text=f"https://telegra.ph{response[0]}",
        disable_web_page_preview=True
    )
