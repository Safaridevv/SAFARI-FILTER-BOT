# This code has been modified by @Safaridev
# Please do not remove this credit
import re
import time
import pytz
import asyncio
import logging
import hashlib
import random
import string
from os import environ
from info import ADMINS, PREMIUM_LOGS
from datetime import datetime, timedelta
from pyrogram import Client, filters
from database.users_chats_db import db


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


def hash_code(code):
    return hashlib.sha256(code.encode()).hexdigest()

async def generate_code(duration_str):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    kolkata_tz = pytz.timezone("Asia/Kolkata")
    created_at = datetime.now(tz=kolkata_tz) 

    await db.codes.insert_one({
        "code_hash": hash_code(code),
        "duration": duration_str,
        "used": False,
        "created_at": created_at,
        "original_code": code
    })
    return code
        
async def parse_duration(duration_str):
    pattern = r'(\d+)\s*(minute|minutes|hour|hours|day|days|week|weeks|month|months)'
    match = re.match(pattern, duration_str.lower())

    if not match:
        return None  

    value, unit = match.groups()
    value = int(value)

    if "minute" in unit:
        return value * 60
    elif "hour" in unit:
        return value * 60 * 60
    elif "day" in unit:
        return value * 24 * 60 * 60
    elif "week" in unit:
        return value * 7 * 24 * 60 * 60
    elif "month" in unit:
        return value * 30 * 24 * 60 * 60

    return None

@Client.on_message(filters.command("code") & filters.user(ADMINS))
async def generate_code_cmd(client, message):
    if len(message.command) == 2:
        duration_str = message.command[1]
        premium_duration_seconds = await parse_duration(duration_str)
        if premium_duration_seconds is not None:
            token = await generate_code(duration_str)
            await message.reply_text(f"✅ ᴄᴏᴅᴇ ɢᴇɴᴇʀᴀᴛᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ ♻️\n\n🔑 ᴄᴏᴅᴇ: `{token}`\n⌛ Vᴀʟɪᴅɪᴛʏ: {duration_str}\n\n𝐔𝐬𝐚𝐠𝐞 : <a href=https://t.me/c/2165249824/4>/redeem</a> xxxxxxxxxx\n\n𝐍𝐨𝐭𝐞 : Oɴʟʏ Oɴᴇ Usᴇʀ Cᴀɴ Usᴇ")
                                       
        else:
            await message.reply_text("❌ ɪɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ғᴏʀᴍᴀᴛ. ᴘʟᴇᴀsᴇ ᴇɴᴛᴇʀ ᴀ ᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ʟɪᴋᴇ '1minute', '1hours', '1days', '1months', etc.")
    else:
        await message.reply_text("Usage: /code 1month")

@Client.on_message(filters.command("redeem"))
async def redeem_code_cmd(client, message):
    if len(message.command) == 2:
        code = message.command[1]
        user_id = message.from_user.id

        if not await db.has_premium_access(user_id):
            code_data = await db.codes.find_one({"code_hash": hash_code(code)})
            if code_data:
                if code_data['used']:
                    await message.reply_text(f"🚫 ᴛʜɪs ᴄᴏᴅᴇ ᴀʟʀᴇᴀᴅʏ ᴜsᴇᴅ 🚫.")
                    return
                premium_duration_seconds = await parse_duration(code_data['duration'])
                if premium_duration_seconds is not None:
                    new_expiry = datetime.now() + timedelta(seconds=premium_duration_seconds)
                    user_data = {"id": user_id, "expiry_time": new_expiry}
                    await db.update_user(user_data)
                    await db.codes.update_one({"_id": code_data["_id"]}, {"$set": {"used": True, "user_id": user_id}})
                    expiry_str_in_ist = new_expiry.astimezone(pytz.timezone("Asia/Kolkata")).strftime("⌛️ ᴇxᴘɪʀʏ ᴅᴀᴛᴇ: %d-%m-%Y\n⏱️ ᴇxᴘɪʀʏ ᴛɪᴍᴇ: %I:%M:%S %p")
                    await message.reply_text(f"🎉 ᴄᴏᴅᴇ ʀᴇᴅᴇᴇᴍᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!\nᴏᴜ ɴᴏᴡ ʜᴀᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss ᴜɴᴛɪʟ:\n\n✨ᴅᴜʀᴀᴛɪᴏɴ: {code_data['duration']}\n{expiry_str_in_ist}")
                else:
                    await message.reply_text("🚫 ɪɴᴠᴀʟɪᴅ ᴅᴜʀᴀᴛɪᴏɴ ɪɴ ᴛʜᴇ ᴄᴏᴅᴇ.")
            else:
                await message.reply_text("🚫 ɪɴᴠᴀʟɪᴅ ᴏʀ ᴇxᴘɪʀᴇᴅ ᴄᴏᴅᴇ.")
        else:
            await message.reply_text("❌ ʏᴏᴜ ᴀʟʀᴇᴀᴅʏ ʜᴀᴠᴇ ᴘʀᴇᴍɪᴜᴍ ᴀᴄᴄᴇss.")
    else:
        await message.reply_text("Usage: /redeem <code>")

@Client.on_message(filters.command("clearcodes") & filters.user(ADMINS))
async def clear_codes_cmd(client, message):
    result = await db.codes.delete_many({})
    if result.deleted_count > 0:
        await message.reply_text(f"✅ ᴀʟʟ {result.deleted_count} ᴄᴏᴅᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ʀᴇᴍᴏᴠᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ.")
    else:
        await message.reply_text("⚠️ ɴᴏ ᴄᴏᴅᴇs ғᴏᴜɴᴅ ᴛʜᴀᴛ ᴄᴏᴜʟᴅ ʙᴇ ᴄʟᴇᴀʀᴇᴅ.")

@Client.on_message(filters.command("allcodes") & filters.user(ADMINS))
async def all_codes_cmd(client, message):
    all_codes = await db.codes.find({}).to_list(length=None)
    if not all_codes:
        await message.reply_text("⚠️ ᴛʜᴇʀᴇ ᴀʀᴇ ɴᴏ ᴄᴏᴅᴇs ᴀᴠᴀɪʟᴀʙʟᴇ.")
        return

    codes_info = "📝 **ɢᴇɴᴇʀᴀᴛᴇᴅ ᴄᴏᴅᴇs ᴅᴇᴛᴀɪʟs:**\n\n"
    for code_data in all_codes:
        original_code = code_data.get("original_code", "Unknown") 
        duration = code_data.get("duration", "Unknown")
        user_id = code_data.get("user_id")
        used = "Yes ✅" if code_data.get("used", False) else "No ⭕"
        created_at = code_data["created_at"].astimezone(pytz.timezone("Asia/Kolkata")).strftime("%d-%m-%Y %I:%M %p")
        if user_id:
            user = await client.get_users(user_id)
            user_name = user.first_name if user.first_name else "Unknown User"
            user_mention = f"[{user_name}](tg://user?id={user_id})"
        else:
            user_mention = "Not Redeemed"
        
        codes_info += f"**🔑 Code**: `{original_code}`\n"
        codes_info += f"**⌛ Duration**: {duration}\n"
        codes_info += f"**‼ Used**: {used}\n"
        codes_info += f"**🕓 Created At**: {created_at}\n"
        codes_info += f"**🙎 User ID**: {user_mention}\n\n"


    for chunk in [codes_info[i:i + 4096] for i in range(0, len(codes_info), 4096)]:
        await message.reply_text(chunk)
