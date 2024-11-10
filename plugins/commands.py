import os
import sys
import logging
import random
import asyncio
import pytz
import requests
import string
from Script import script
from datetime import datetime, timedelta
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files, get_search_results
from database.users_chats_db import db
from database.safari_reffer import sdb
from info import *
from utils import get_size, is_subscribed, temp, get_shortlink, get_seconds
import re
import json
import base64
logger = logging.getLogger(__name__)

TIMEZONE = "Asia/Kolkata"

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    try: 
        user_id = message.from_user.id
        if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            buttons = [[
                        InlineKeyboardButton('☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                      ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_text(
                text="ᴏᴋ ɪ ᴄᴀɴ ʜᴇʟᴘ ʏᴏᴜ ᴊᴜsᴛ sᴛᴀʀᴛ ᴘᴍ", 
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            await asyncio.sleep(2) # 😢 https://github.com/EvamariaTG/EvaMaria/blob/master/plugins/p_ttishow.py#L17 😬 wait a bit, before checking.
            if not await db.get_chat(message.chat.id):
                total=await client.get_chat_members_count(message.chat.id)
                await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(temp.B_NAME, message.chat.title, message.chat.id, total, "Unknown"))       
                await db.add_chat(message.chat.id, message.chat.title, message.from_user.id)
            return 
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention, temp.B_NAME))
        if len(message.command) != 2:
            buttons = [[
                        InlineKeyboardButton('☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                    ],[
                        InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇꜱ', callback_data='channels'), 
                        InlineKeyboardButton('✨ ғᴇᴀᴛᴜʀᴇs', callback_data='features')
                    ],[
                        InlineKeyboardButton('❓Hᴇʟᴘ', callback_data='help'),
                        InlineKeyboardButton('ℹ ᴀʙᴏᴜᴛ', callback_data='about')
                    ]]
            if await db.get_setting("IS_VERIFY", default=IS_VERIFY):
                buttons.append(
                        [InlineKeyboardButton('🎁 ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ', callback_data="pm_reff"),
                        InlineKeyboardButton('💎 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ✨', callback_data="premium")])
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return
        if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
            buttons = [[
                        InlineKeyboardButton('☆ ᴀᴅᴅ ᴍᴇ ᴛᴏ ʏᴏᴜʀ ɢʀᴏᴜᴘ ☆', url=f'http://telegram.me/{temp.U_NAME}?startgroup=true')
                    ],[
                        InlineKeyboardButton('📢 ᴜᴘᴅᴀᴛᴇꜱ', callback_data='channels'), 
                        InlineKeyboardButton('✨ ғᴇᴀᴛᴜʀᴇs', callback_data='features')
                    ],[
                        InlineKeyboardButton('❓Hᴇʟᴘ', callback_data='help'),
                        InlineKeyboardButton('ℹ ᴀʙᴏᴜᴛ', callback_data='about')
                    ]]
            if await db.get_setting("IS_VERIFY", default=IS_VERIFY):
                buttons.append(
                        [InlineKeyboardButton('🎁 ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ', callback_data="pm_reff"),
                        InlineKeyboardButton('💎 ʙᴜʏ ᴘʀᴇᴍɪᴜᴍ ✨', callback_data="premium")])
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_photo(
                photo=random.choice(PICS),
                caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return
        if len(message.command) == 2 and message.command[1] in ["safaridev"]:
            buttons = [[
                        InlineKeyboardButton('📲 ꜱᴇɴᴅ ᴘᴀʏᴍᴇɴᴛ ꜱᴄʀᴇᴇɴꜱʜᴏᴛ', url=f"https://t.me/{OWNER_USER_NAME}")
                      ],[
                        InlineKeyboardButton('❌ ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
                      ]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await message.reply_photo(
                photo=(PREMIUM_PIC),
                caption=script.PREMIUM_CMD,
                reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            return  
        if message.command[1].startswith("reff_"):
            try:
                user_id = int(message.command[1].split("_")[1])
            except ValueError:
                await message.reply_text("Invalid refer!")
                return
            if user_id == message.from_user.id:
                await message.reply_text("Hᴇʏ Dᴜᴅᴇ, Yᴏᴜ Cᴀɴ'ᴛ Rᴇғᴇʀ Yᴏᴜʀsᴇʟғ 🤣!\n\nsʜᴀʀᴇ ʟɪɴᴋ ʏᴏᴜʀ ғʀɪᴇɴᴅ ᴀɴᴅ ɢᴇᴛ 5 ʀᴇғᴇʀʀᴀʟ ᴘᴏɪɴᴛ ɪғ ʏᴏᴜ ᴀʀᴇ ᴄᴏʟʟᴇᴄᴛɪɴɢ 50 ʀᴇғᴇʀʀᴀʟ ᴘᴏɪɴᴛs ᴛʜᴇɴ ʏᴏᴜ ᴄᴀɴ ɢᴇᴛ 1 ᴍᴏɴᴛʜ ғʀᴇᴇ ᴘʀᴇᴍɪᴜᴍ ᴍᴇᴍʙᴇʀsʜɪᴘ.")
                return
            if sdb.is_user_in_list(message.from_user.id):
                await message.reply_text("Yᴏᴜ ʜᴀᴠᴇ ʙᴇᴇɴ ᴀʟʀᴇᴀᴅʏ ɪɴᴠɪᴛᴇᴅ ❗")
                return
            try:
                uss = await client.get_users(user_id)
            except Exception:
                return 	    
            sdb.add_user(message.from_user.id)
            fromuse = sdb.get_refer_points(user_id) + 10
            sdb.add_refer_points(user_id, fromuse)
            await message.reply_text(f"You have been successfully invited by {uss.mention}!")
            await client.send_message(user_id, f"𝗖𝗼𝗻𝗴𝗿𝗮𝘁𝘂𝗹𝗮𝘁𝗶𝗼𝗻𝘀! 𝗬𝗼𝘂 𝘄𝗼𝗻 𝟭𝟬 𝗥𝗲𝗳𝗲𝗿𝗿𝗮𝗹 𝗽𝗼𝗶𝗻𝘁 𝗯𝗲𝗰𝗮𝘂𝘀𝗲 𝗬𝗼𝘂 𝗵𝗮𝘃𝗲 𝗯𝗲𝗲𝗻 𝗦𝘂𝗰𝗰𝗲𝘀𝘀𝗳𝘂𝗹𝗹𝘆 𝗜𝗻𝘃𝗶𝘁𝗲𝗱 ☞{message.from_user.mention}!") 
            if fromuse == REFFER_POINT:
                await db.give_referal(user_id)
                sdb.add_refer_points(user_id, 0) 
                await client.send_message(chat_id=user_id,
                    text=f"<b>Hᴇʏ {uss.mention}\n\nYᴏᴜ ɢᴏᴛ 1 ᴍᴏɴᴛʜ ᴘʀᴇᴍɪᴜᴍ sᴜʙsᴄʀɪᴘᴛɪᴏɴ ʙʏ ɪɴᴠɪᴛɪɴɢ 5 ᴜsᴇʀs ❗", disable_web_page_preview=True              
                    )
                for admin in ADMINS:
                    await client.send_message(chat_id=admin, text=f"Sᴜᴄᴄᴇss ғᴜʟʟʏ ᴛᴀsᴋ ᴄᴏᴍᴘʟᴇᴛᴇᴅ ʙʏ ᴛʜɪs ᴜsᴇʀ:\n\nuser Nᴀᴍᴇ: {uss.mention}\n\nUsᴇʀ ɪᴅ: {uss.id}!")	
                return
        safari = message
        if len(safari.command) == 2:
            if safari.command[1].startswith(('verify', 'sendall')):
                _, userid, verify_id, file_id = safari.command[1].split("_", 3)
                user_id = int(userid)
                verify_id_info = await db.get_verify_id_info(user_id, verify_id)
                if not verify_id_info or verify_id_info["verified"]:
                    await message.reply("<b>ʟɪɴᴋ ᴇxᴘɪʀᴇᴅ ᴛʀʏ ᴀɢᴀɪɴ...</b>")
                    return
                
                ist_timezone = pytz.timezone('Asia/Kolkata')
                if await db.user_verified(user_id):
                    key = "third_verified"
                else:
                    key = "second_verified" if await db.is_user_verified(user_id) else "last_verified"
                current_time = datetime.now(tz=ist_timezone)
                result = await db.update_safari_user(user_id, {key:current_time})
                await db.update_verify_id_info(user_id, verify_id, {"verified":True})
                if key == "third_verified": 
                    num = 3 
                else: 
                    num =  2 if key == "second_verified" else 1
                if key == "third_verified":
                    msg = script.THIRDT_COMPLETE_TEXT
                else:
                    msg = script.SECOND_COMPLETE_TEXT if key == "second_verified" else script.VERIFY_COMPLETE_TEXT
                if safari.command[1].startswith('sendall'):
                    verify = f"https://telegram.me/{temp.U_NAME}?start=allfiles_{file_id}"
                else:
                    verify = f"https://telegram.me/{temp.U_NAME}?start=files_{file_id}"
                await client.send_message(GROUP_VERIFY_LOGS, script.VERIFIED_LOG_TEXT.format(safari.from_user.mention, user_id, datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%d %B %Y'), num))
                btn = [[
                    InlineKeyboardButton("✅ ɢᴇᴛ ꜰɪʟᴇ ✅", url=verify),
                ]]
                reply_markup=InlineKeyboardMarkup(btn)
                dlt=await safari.reply_photo(
                    photo=(VERIFY_IMG),
                    caption=msg.format(message.from_user.mention),
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                await asyncio.sleep(600)
                await dlt.delete()
                return
        
        data = message.command[1]
        try:
            pre, file_id = data.split('_', 1)
        except:
            file_id = data
            pre = ""
        if AUTH_CHANNEL and not await is_subscribed(client, message):
            if not await db.find_join_req(user_id):
                try:
                    invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL), creates_join_request=True)
                    channel = invite_link.invite_link
                except ChatAdminRequired:
                    logger.error("Mᴀᴋᴇ sᴜʀᴇ Bᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ Fᴏʀᴄᴇsᴜʙ ᴄʜᴀɴɴᴇʟ")
                except Exception:
                    invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
                    channel = invite_link.invite_link
                    return
                btn = [[ 
                    InlineKeyboardButton('❆ Jᴏɪɴ Cʜᴀɴɴᴇʟ ❆', url=channel)
                    ],[
                    InlineKeyboardButton('↻ Tʀʏ Aɢᴀɪɴ', callback_data=f'checksub#{pre}#{file_id}')
                ]]
                temp.SFILE_ID[user_id] = [pre, file_id]
                msg=await client.send_message(
                    chat_id=message.from_user.id,
                    text=f"<b>Hello {message.from_user.mention}\n\n<blockquote>➤<i>To use this bot, you need to join our channel first!</i>\n\n➤<u>इस बॉट का उपयोग करने के लिए, आपको पहले हमारे चैनल से जुड़ना होगा!</u></blockquote>\n\n➤Tap to Button and join channel</b>👇👇",
                    reply_markup=InlineKeyboardMarkup(btn)
                   
                    )
                await asyncio.sleep(120)
                await msg.delete()
                return
        if not await db.has_premium_access(user_id):
            is_verify = await db.get_setting("IS_VERIFY", default=IS_VERIFY)
            second_verify_gap = await db.get_setting("SECOND_VERIFY_GAP", default=SECOND_VERIFY_GAP)
            third_verify_gap = await db.get_setting("THIRD_VERIFY_GAP", default=THIRD_VERIFY_GAP)
            gap2 = int(second_verify_gap)
            gap3 = int(third_verify_gap) 
            user_verified = await db.is_user_verified(user_id)
            is_second_shortener = await db.use_second_shortener(user_id, gap2)
            is_third_shortener = await db.use_third_shortener(user_id, gap3)    
            if (not user_verified or is_second_shortener or is_third_shortener) and is_verify:
                verify_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))
                await db.create_verify_id(user_id, verify_id)
                tutorial = await db.get_setting("TUTORIAL3", default=TUTORIAL3) if is_third_shortener else await db.get_setting("TUTORIAL2", default=TUTORIAL2) if is_second_shortener else await db.get_setting("TUTORIAL", default=TUTORIAL) 
                
                if safari.command[1].startswith('allfiles'):
                    verify = await get_shortlink(f"https://telegram.me/{temp.U_NAME}?start=sendall_{user_id}_{verify_id}_{file_id}", is_second_shortener, is_third_shortener)
                else:
                    verify = await get_shortlink(f"https://telegram.me/{temp.U_NAME}?start=verify_{user_id}_{verify_id}_{file_id}", is_second_shortener, is_third_shortener)
                if not await db.check_trial_status(user_id):
                    buttons = [[
                        InlineKeyboardButton("✅️ ᴠᴇʀɪғʏ ✅️", url=verify)
                    ],[
                        InlineKeyboardButton("⁉️ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ⁉️", url=tutorial)
                    ],[
                        InlineKeyboardButton("✨5ᴍɪɴ Pʀᴇᴍɪᴜᴍ Tʀᴀɪʟ✨", callback_data=f'give_trial')
                    ]]
                else:
                    buttons = [[
                        InlineKeyboardButton("✅️ ᴠᴇʀɪғʏ ✅️", url=verify)
                    ],[
                        InlineKeyboardButton("⁉️ ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ ⁉️", url=tutorial)
                    ],[
                        InlineKeyboardButton("✨ ʀᴇᴍᴏᴠᴇ ᴠᴇʀɪғʏ ✨", callback_data=f'premium_info')
                    ]]
                reply_markup=InlineKeyboardMarkup(buttons) 
                if await db.user_verified(user_id): 
                    msg = script.THIRDT_VERIFICATION_TEXT   
                else:        
                    msg = script.SECOND_VERIFICATION_TEXT if is_second_shortener else script.VERIFICATION_TEXT
                d = await safari.reply_text(
                    text=msg.format(message.from_user.mention),
                    reply_markup=reply_markup,
                    parse_mode=enums.ParseMode.HTML
                )
                await asyncio.sleep(600) 
                await d.delete()
                await safari.delete()
                return
        if data and data.startswith("allfiles"):
            files = temp.GETALL.get(file_id)
            if not files:
                return await message.reply('<b><i>Nᴏ Sᴜᴄʜ Fɪʟᴇ Eᴇxɪsᴛ.</b></i>')
            filesarr = []
            for file in files:
                file_id = file.file_id
                files_ = await get_file_details(file_id)
                files1 = files_[0]
                title = files1.file_name
                size=get_size(files1.file_size)
                f_caption=files1.caption
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
                    except Exception as e:
                        logger.exception(e)
                        f_caption=f_caption
                if f_caption is None:
                    f_caption = f"{files1.file_name}"
                button = [[
                    InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
                    ]]
                reply_markup=InlineKeyboardMarkup(button)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    caption=f_caption,
                    reply_markup=reply_markup
                )
        if not data:
            return
        files_ = await get_file_details(file_id)           
        if not files_:
            pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
            try:
                button = [[
                    InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
                    ]]
                reply_markup=InlineKeyboardMarkup(button)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                    reply_markup=reply_markup
                )
                filetype = msg.media
                file = getattr(msg, filetype.value)
                title = file.file_name
                size=get_size(file.file_size)
                f_caption = f"<code>{title}</code>"
                if CUSTOM_FILE_CAPTION:
                    try:
                        f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='')
                    except:
                        return
                await msg.edit_caption(f_caption)
                return
            except:
                pass
            return await message.reply('Nᴏ sᴜᴄʜ ғɪʟᴇ ᴇxɪsᴛ.')
        
        files = files_[0]
        title = files.file_name
        size=get_size(files.file_size)
        f_caption=files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption=CUSTOM_FILE_CAPTION.format(file_name= '' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption=f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        button = [[
            InlineKeyboardButton("🖥️ ᴡᴀᴛᴄʜ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
            ]]
        reply_markup=InlineKeyboardMarkup(button)
        msg=await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f_caption,
            reply_markup=reply_markup
        )
    except Exception as e:
        await message.reply(f"{e}")
        
@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Uɴᴇxᴘᴇᴄᴛᴇᴅ ᴛʏᴘᴇ ᴏғ CHANNELS")

    text = '📑 **Iɴᴅᴇxᴇᴅ ᴄʜᴀɴɴᴇʟs/ɢʀᴏᴜᴘs**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    """Send log file"""
    try:
        await message.reply_document('Logs.txt')
    except Exception as e:
        await message.reply(str(e))

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Pʀᴏᴄᴇssɪɴɢ...⏳", quote=True)
    else:
        await message.reply('Rᴇᴘʟʏ ᴛᴏ ғɪʟᴇ ᴡɪᴛʜ /delete ᴡʜɪᴄʜ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴅᴇʟᴇᴛᴇ', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('Tʜɪs ɪs ɴᴏᴛ sᴜᴘᴘᴏʀᴛᴇᴅ ғɪʟᴇ ғᴏʀᴍᴀᴛ')
        return
    
    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
        else:
            # files indexed before https://github.com/EvamariaTG/EvaMaria/commit/f3d2a1bcb155faf44178e5d7a685a1b533e714bf#diff-86b613edf1748372103e94cacff3b578b36b698ef9c16817bb98fe9ef22fb669R39 
            # have original file name.
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('Fɪʟᴇ ɪs sᴜᴄᴄᴇssғᴜʟʟʏ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ')
            else:
                await msg.edit('Fɪʟᴇ ɴᴏᴛ ғᴏᴜɴᴅ ɪɴ ᴅᴀᴛᴀʙᴀsᴇ')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'Tʜɪs ᴡɪʟʟ ᴅᴇʟᴇᴛᴇ ᴀʟʟ ɪɴᴅᴇxᴇᴅ ғɪʟᴇs.\nDᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ ?',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Yᴇs", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cᴀɴᴄᴇʟ", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer("Eᴠᴇʀʏᴛʜɪɴɢ's Gᴏɴᴇ")
    await message.message.edit('Sᴜᴄᴄᴇsғᴜʟʟʏ Dᴇʟᴇᴛᴇᴅ Aʟʟ Tʜᴇ Iɴᴅᴇxᴇᴅ Fɪʟᴇs.')

@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "Usᴇʀs Sᴀᴠᴇᴅ Iɴ DB Aʀᴇ:\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"<b>Yᴏᴜʀ ᴍᴇssᴀɢᴇ ʜᴀs ʙᴇᴇɴ sᴜᴄᴄᴇssғᴜʟʟʏ sᴇɴᴅ ᴛᴏ {user.mention}.</b>")
            else:
                await message.reply_text("<b>Tʜɪs ᴜsᴇʀ ᴅɪᴅɴ'ᴛ sᴛᴀʀᴛᴇᴅ ᴛʜɪs ʙᴏᴛ ʏᴇᴛ!</b>")
        except Exception as e:
            await message.reply_text(f"<b>Eʀʀᴏʀ: {e}</b>")
    else:
        await message.reply_text("<b>Usᴇ ᴛʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴀs ᴀ ʀᴇᴘʟʏ ᴛᴏ ᴀɴʏ ᴍᴇssᴀɢᴇ ᴜsɪɴɢ ᴛʜᴇ ᴛᴀʀɢᴇᴛ ᴄʜᴀᴛ ɪᴅ. Fᴏʀ ᴇɢ: /send ᴜsᴇʀɪᴅ</b>")

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Tʜɪs ᴄᴏᴍᴍᴀɴᴅ ᴡᴏɴ'ᴛ ᴡᴏʀᴋ ɪɴ ɢʀᴏᴜᴘs. Iᴛ ᴏɴʟʏ ᴡᴏʀᴋs ᴏɴ ᴍʏ PM!</b>")
    else:
        pass
    try:
        keyword = message.text.split(" ", 1)[1]
    except:
        return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, Gɪᴠᴇ ᴍᴇ ᴀ ᴋᴇʏᴡᴏʀᴅ ᴀʟᴏɴɢ ᴡɪᴛʜ ᴛʜᴇ ᴄᴏᴍᴍᴀɴᴅ ᴛᴏ ᴅᴇʟᴇᴛᴇ ғɪʟᴇs.</b>")
    btn = [[
       InlineKeyboardButton("Yᴇs, Cᴏɴᴛɪɴᴜᴇ !", callback_data=f"killfilesdq#{keyword}")
       ],[
       InlineKeyboardButton("Nᴏ, Aʙᴏʀᴛ ᴏᴘᴇʀᴀᴛɪᴏɴ !", callback_data="close_data")
    ]]
    await message.reply_text(
        text="<b>Aʀᴇ ʏᴏᴜ sᴜʀᴇ? Dᴏ ʏᴏᴜ ᴡᴀɴᴛ ᴛᴏ ᴄᴏɴᴛɪɴᴜᴇ?\n\nNᴏᴛᴇ:- Tʜɪs ᴄᴏᴜʟᴅ ʙᴇ ᴀ ᴅᴇsᴛʀᴜᴄᴛɪᴠᴇ ᴀᴄᴛɪᴏɴ!</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML
    )

@Client.on_message(filters.command("restart") & filters.user(ADMINS))
async def stop_button(bot, message):
    msg = await bot.send_message(text="<b><i>ʙᴏᴛ ɪꜱ ʀᴇꜱᴛᴀʀᴛɪɴɢ</i></b>", chat_id=message.chat.id)       
    await asyncio.sleep(3)
    await msg.edit("<b><i><u>ʙᴏᴛ ɪꜱ ʀᴇꜱᴛᴀʀᴛᴇᴅ</u> ✅</i></b>")
    os.execl(sys.executable, sys.executable, *sys.argv)

@Client.on_message(filters.command("setmode") & filters.user(ADMINS))
async def setmode(client, message):
    valid_modes = ["PM_FILTER", "IS_VERIFY", "STREAM_MODE", "AUTO_FILE_DELETE"]  
    try:
        args = message.text.split()   
        if len(args) == 3:
            mode_name = args[1]
            value = args[2].lower() == 'true'    
            if mode_name in valid_modes:
                await db.set_setting(mode_name, value)
                await message.reply(f"{mode_name} has been set to {value}.")
            else:
                await message.reply("Invalid mode name. Please use one of the following:\n\n" + "\n\n".join(valid_modes))
        else:
            await message.reply("Please specify the mode name and 'True' or 'False' as arguments. Example: /setmode PM_FILTER True\n\nTrue, False Variable Available ☟\n\n" + "\n\n".join(valid_modes))
    except Exception as e:
        await message.reply(f"An error occurred: {e}")

@Client.on_message(filters.command("setvalue") & filters.user(ADMINS))
async def set_value(client, message):
    valid_key = ["TUTORIAL", "TUTORIAL2", "TUTORIAL3", "SECOND_VERIFY_GAP", "THIRD_VERIFY_GAP"]  
    try:
        args = message.text.split()
        if len(args) == 3:
            key = args[1]
            value = args[2]
            if key in valid_key:
                await db.set_setting(key, value)
                await message.reply(f"{key} has been set to: {value}")
            else:
                await message.reply("Invalid value name. Please use one of the following:\n\n" + "\n\n".join(valid_key))
        else:
            await message.reply("Please specify the key and link. Example: /setvalue TUTORIAL https://t.me/c/1998895377/2184\n\nSet Value Available\n\n☟" + "\n\n".join(valid_key))
    except Exception as e:
        await message.reply(f"An error occurred: {e}")

@Client.on_message(filters.command("shortlink") & filters.user(ADMINS))
async def shortlink(client, message):
    valid_key = ["STREAM", "VERIFY1", "VERIFY2", "VERIFY3"]  
    try:
        args = message.text.split()
        if len(args) == 4:
            key_name = args[1]
            key = args[2]
            value = args[3]
            
            if key_name in valid_key:
                if key_name == "VERIFY1":
                    await db.set_setting("VERIFY_URL", key)
                    await db.set_setting("VERIFY_API", value)
                    await message.reply(f"shortlink changed successfully for {key_name} : {key} {value}")
                elif key_name == "VERIFY2":
                    await db.set_setting("VERIFY_URL2", key)
                    await db.set_setting("VERIFY_API2", value)
                    await message.reply(f"shortlink changed successfully for {key_name} : {key} {value}")
                elif key_name == "VERIFY3":
                    await db.set_setting("VERIFY_URL3", key)
                    await db.set_setting("VERIFY_API3", value)
                    await message.reply(f"shortlink changed successfully for {key_name} : {key} {value}")
                else:
                    await db.set_setting("STREAM_SITE", key)
                    await db.set_setting("STREAM_API", value)
                    await message.reply(f"shortlink changed successfully for {key_name} : {key} {value}")
            else:   
                await message.reply("Invalid value name. Please use one of the following:\n\n" + "\n\n".join(valid_key))
        else:
            await message.reply("Please specify the key and link. Example: `/shortlink tnshort.net 06b24eb6bbb025713cd522fb3f696b6d5de11354`\n\nshortlink set type ☟\n\n" + "\n\n".join(valid_key))
    except Exception as e:
        await message.reply(f"An error occurred: {e}")

