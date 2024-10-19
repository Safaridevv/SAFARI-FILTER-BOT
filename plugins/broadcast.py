# This code has been modified by @Safaridev
# Please do not remove this credit
from pyrogram import Client, filters
import datetime
import time
from database.users_chats_db import db
from info import ADMINS
from utils import broadcast_messages
import asyncio

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def verupikkals(bot, message):
    users = await db.get_all_users()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )   

    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed =0

    success = 0

    sem = asyncio.Semaphore(10) # limit the number of concurrent tasks to 100

    async def run_task(user):
        async with sem:
            res = await broadcast_func(user, b_msg)
            return res

    tasks = []

    async for user in users:
        task = asyncio.ensure_future(run_task(user))
        tasks.append(task)
        
    for res in await asyncio.gather(*tasks):
        success1, blocked1, deleted1, failed1, done1 = res
        done += done1
        blocked += blocked1
        deleted += deleted1
        failed += failed1
        success += success1

        if not done % 50:
            await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    

    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

@Client.on_message(filters.command("grp_broadcast") & filters.user(ADMINS) & filters.reply)
async def grp_brodcst(bot, message):
    chats = await db.get_all_chats()
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )
    start_time = time.time()
    total_chats = await db.total_chat_count()
    done = 0
    failed =0

    success = 0
    async for chat in chats:
        pti, sh = await broadcast_messages(int(chat['id']), b_msg)
        if pti:
            success += 1
        elif pti == False:
            if sh == "Blocked":
                blocked+=1
            elif sh == "Deleted":
                deleted += 1
            elif sh == "Error":
                failed += 1
        done += 1
        await asyncio.sleep(2)
        if not done % 20:
            await sts.edit(f"Broadcast in progress:\n\nTotal Chats {total_chats}\nCompleted: {done} / {total_chats}\nSuccess: {success}\nFailed: {failed}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Chats {total_chats}\nCompleted: {done} / {total_chats}\nSuccess: {success}\nFailed: {failed}")

async def broadcast_func(user, b_msg):
        success, blocked, deleted, failed, done = 0, 0, 0, 0, 0
        pti, sh = await broadcast_messages(int(user['id']), b_msg)
        if pti:
            success = 1
        elif pti == False:
            if sh == "Blocked":
                blocked=1
            elif sh == "Deleted":
                deleted = 1
            elif sh == "Error":
                failed = 1
        done = 1
        return success, blocked, deleted, failed, done
