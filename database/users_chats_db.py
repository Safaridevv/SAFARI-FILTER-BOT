# This code has been modified by @Safaridev
# Please do not remove this credit
import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, SINGLE_BUTTON, SPELL_CHECK_REPLY, AUTO_DELETE, MAX_BTN, AUTO_FFILTER, TUTORIAL, TUTORIAL2, TUTORIAL3, REFERAL_TIME, STREAM_API, STREAM_SITE, VERIFY_URL, VERIFY_API, \
VERIFY_URL2, VERIFY_API2, VERIFY_URL3, VERIFY_API3, LIMIT_MODE, TWO_VERIFY_GAP, THIRD_VERIFY_GAP, STREAM_MODE, LOG_CHANNEL, IS_VERIFY, AUTH_CHANNEL, CUSTOM_FILE_CAPTION, FILE_LIMITE, SEND_ALL_LIMITE, STREAM_SITE, STREAM_API
from datetime import datetime, timedelta
import pytz
import re
import time
import hashlib
import random
import string
    
class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.users = self.db.uersz
        self.codes = self.db.codes
        self.safari = self.db.safari
        self.req = self.db.requests
        self.links_col = self.db.links
        self.verify_id = self.db.verify_id
        self.settings_col = self.db.settings
        
    def new_user(self, id, name):
        return dict(
            id = id,
            name = name,
            send_all=0,
            files_count=0,
            lifetime_files=0,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )

    def new_group(self, id, title, owner_id):
        return dict(
            id = id,
            title = title,
            owner_id=owner_id, 
            is_verified=False,
            is_rejected=False, 
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )
        
    async def get_setting(self, key, default=None):
        setting = await self.settings_col.find_one({"name": key})
        return setting.get("value", default) if setting else default

    async def set_setting(self, key, value):
        await self.settings_col.update_one(
            {"name": key},
            {"$set": {"value": value}},
            upsert=True)

    async def find_join_req(self, id):
        return bool(await self.req.find_one({'id': id}))
        
    async def add_join_req(self, id):
        await self.req.insert_one({'id': id})

    async def del_join_req(self):
        await self.req.drop()
        
    async def get_safari_user(self, user_id):
        user_id = int(user_id)
        user = await self.safari.find_one({"user_id": user_id})
        ist_timezone = pytz.timezone('Asia/Kolkata')
        if not user:
            res = {
                "user_id": user_id,
                "last_verified": datetime(2020, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
                "second_verified": datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone),
            }
            user = await self.safari.insert_one(res)
        return user

    async def update_safari_user(self, user_id, value:dict):
        user_id = int(user_id)
        myquery = {"user_id": user_id}
        newvalues = {"$set": value}
        return await self.safari.update_one(myquery, newvalues)

    async def is_user_verified(self, user_id):
        user = await self.get_safari_user(user_id)
        try:
            safariback = user["last_verified"]
        except Exception:
            user = await self.get_safari_user(user_id)
            safariback = user["last_verified"]
        ist_timezone = pytz.timezone('Asia/Kolkata')
        safariback = safariback.astimezone(ist_timezone)
        current_time = datetime.now(tz=ist_timezone)
        seconds_since_midnight = (current_time - datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, tzinfo=ist_timezone)).total_seconds()
        time_diff = current_time - safariback
        total_seconds = time_diff.total_seconds()
        return total_seconds <= seconds_since_midnight

    async def user_verified(self, user_id):
        user = await self.get_safari_user(user_id)
        try:
            safariback = user["second_verified"]
        except Exception:
            user = await self.get_safari_user(user_id)
            safariback = user["second_verified"]
        ist_timezone = pytz.timezone('Asia/Kolkata')
        safariback = safariback.astimezone(ist_timezone)
        current_time = datetime.now(tz=ist_timezone)
        seconds_since_midnight = (current_time - datetime(current_time.year, current_time.month, current_time.day, 0, 0, 0, tzinfo=ist_timezone)).total_seconds()
        time_diff = current_time - safariback
        total_seconds = time_diff.total_seconds()
        return total_seconds <= seconds_since_midnight

    async def use_second_shortener(self, user_id, time):
        user = await self.get_safari_user(user_id)
        if not user.get("second_verified"):
            ist_timezone = pytz.timezone('Asia/Kolkata')
            await self.update_safari_user(user_id, {"second_verified":datetime(2019, 5, 17, 0, 0, 0, tzinfo=ist_timezone)})
            user = await self.get_safari_user(user_id)
        if await self.is_user_verified(user_id):
            try:
                safariback = user["last_verified"]
            except Exception:
                user = await self.get_safari_user(user_id)
                safariback = user["last_verified"]
            ist_timezone = pytz.timezone('Asia/Kolkata')
            safariback = safariback.astimezone(ist_timezone)
            current_time = datetime.now(tz=ist_timezone)
            time_difference = current_time - safariback
            if time_difference > timedelta(seconds=time):
                safariback = user["last_verified"].astimezone(ist_timezone)
                second_time = user["second_verified"].astimezone(ist_timezone)
                return second_time < safariback
        return False
        
    async def use_third_shortener(self, user_id, time):
        user = await self.get_safari_user(user_id)
        if not user.get("third_verified"):
            ist_timezone = pytz.timezone('Asia/Kolkata')
            await self.update_safari_user(user_id, {"third_verified":datetime(2018, 5, 17, 0, 0, 0, tzinfo=ist_timezone)})
            user = await self.get_safari_user(user_id)
        if await self.user_verified(user_id):
            try:
                safariback = user["second_verified"]
            except Exception:
                user = await self.get_safari_user(user_id)
                safariback = user["second_verified"]
            ist_timezone = pytz.timezone('Asia/Kolkata')
            safariback = safariback.astimezone(ist_timezone)
            current_time = datetime.now(tz=ist_timezone)
            time_difference = current_time - safariback
            if time_difference > timedelta(seconds=time):
                safariback = user["second_verified"].astimezone(ist_timezone)
                second_time = user["third_verified"].astimezone(ist_timezone)
                return second_time < safariback
        return False
        
    async def create_verify_id(self, user_id: int, hash):
        res = {"user_id": user_id, "hash":hash, "verified":False}
        return await self.verify_id.insert_one(res)

    async def get_verify_id_info(self, user_id: int, hash):
        return await self.verify_id.find_one({"user_id": user_id, "hash": hash})

    async def update_verify_id_info(self, user_id, hash, value: dict):
        myquery = {"user_id": user_id, "hash": hash}
        newvalues = { "$set": value }
        return await self.verify_id.update_one(myquery, newvalues)
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})


    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats
   
    async def files_count(self, user_id, key):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            await self.add_user(user_id, "None")
            return 0
        return user.get(key, 0)
        
    async def update_files(self, user_id, key, value):
        await self.col.update_one({"id": user_id}, {"$set": {key: value}})
    
    async def reset_all_files_count(self):
        await self.col.update_many({}, {"$set": {"files_count": 0}})

    async def reset_allsend_files(self):
        await self.col.update_many({}, {"$set": {"send_all": 0}})
        
    async def reset_daily_files_count(self, user_id):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            return
        await self.col.update_one({"id": user_id}, {"$set": {"files_coun": 0}})

    async def add_chat(self, chat, title, owner_id):
        chat = self.new_group(chat, title, owner_id)
        await self.grp.insert_one(chat)
    
    async def get_chat(self, chat_id):
        chat = await self.grp.find_one({'id': int(chat_id)})
        return chat if chat else False
    
    
    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
            
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'auto_delete': AUTO_DELETE,
            'auto_ffilter': AUTO_FFILTER,
            'max_btn': MAX_BTN,
            'template': IMDB_TEMPLATE,
            'verify': VERIFY_URL,
            'verify_api': VERIFY_API,
            'verify_2': VERIFY_URL2,
            'verify_api2': VERIFY_API2,
            'verify_3': VERIFY_URL3,
            'verify_api3': VERIFY_API3,
            'verify_time': TWO_VERIFY_GAP,
            'verify_time2': THIRD_VERIFY_GAP,
            'tutorial': TUTORIAL,
            'tutorial2': TUTORIAL2, 
            'tutorial3': TUTORIAL3, 
            'filelock': LIMIT_MODE, 
            'log': LOG_CHANNEL,
            'is_verify': IS_VERIFY,
            'fsub_id': AUTH_CHANNEL, 
            'file_limit': FILE_LIMITE, 
            'all_limit': SEND_ALL_LIMITE, 
            'stream_mode': STREAM_MODE,
            'streamapi': STREAM_API, 
            'streamsite': STREAM_SITE,
            'caption': CUSTOM_FILE_CAPTION
        }
        chat = await self.grp.find_one({'id':int(id)})
        if chat:
            return chat.get('settings', default)
        return default
 
               
    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})

    async def verify_group(self, chat_id):
        await self.grp.update_one({'id': int(chat_id)}, {'$set': {'is_verified': True}})

    async def un_rejected(self, chat_id):
        await self.grp.update_one({'id': int(chat_id)}, {'$set': {'is_rejected': False}})

    async def reject_group(self, chat_id):
        await self.grp.update_one({'id': int(chat_id)}, {'$set': {'is_rejected': True}})

    async def check_group_verification(self, chat_id):
        chat = await self.get_chat(chat_id)
        if not chat:
            return False
        return chat.get('is_verified')

    async def rejected_group(self, chat_id):
        chat = await self.get_chat(chat_id)
        if not chat:
            return False
        return chat.get('is_rejected')

    async def get_all_groups(self):
        return await self.grp.find().to_list(None)

    async def delete_all_groups(self):
        await self.grp.delete_many({})

    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
    

    async def get_all_chats(self):
        return self.grp.find({})


    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']
        
    async def get_user(self, user_id):
        user_data = await self.users.find_one({"id": user_id})
        return user_data
        
    async def update_user(self, user_data):
        await self.users.update_one({"id": user_data["id"]}, {"$set": user_data}, upsert=True)

    async def has_premium_access(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            expiry_time = user_data.get("expiry_time")
            if expiry_time is None:
                return False
            elif isinstance(expiry_time, datetime) and datetime.now() <= expiry_time:
                return True
            else:
                await self.users.update_one({"id": user_id}, {"$set": {"expiry_time": None}})
        return False
        
    async def update_one(self, filter_query, update_data):
        try:
            result = await self.users.update_one(filter_query, update_data)
            return result.matched_count == 1
        except Exception as e:
            print(f"Error updating document: {e}")
            return False

    async def get_expired(self, current_time):
        expired_users = []
        if data := self.users.find({"expiry_time": {"$lt": current_time}}):
            async for user in data:
                expired_users.append(user)
        return expired_users

    async def remove_premium_access(self, user_id):
        return await self.update_one(
            {"id": user_id}, {"$set": {"expiry_time": None}}
        )

    async def check_trial_status(self, user_id):
        user_data = await self.get_user(user_id)
        if user_data:
            return user_data.get("has_free_trial", False)
        return False

    async def give_free_trial(self, user_id):
        user_id = user_id
        seconds = 5*60         
        expiry_time = datetime.now() + timedelta(seconds=seconds)
        user_data = {"id": user_id, "expiry_time": expiry_time, "has_free_trial": True}
        await self.users.update_one({"id": user_id}, {"$set": user_data}, upsert=True)

    async def give_referal(self, userid):        
        user_id = userid
        seconds = REFERAL_TIME       
        expiry_time = datetime.now() + timedelta(seconds=seconds)
        user_data = {"id": user_id, "expiry_time": expiry_time, "has_free_trial": True}
        await self.users.update_one({"id": user_id}, {"$set": user_data}, upsert=True)

  

db = Database(DATABASE_URI, DATABASE_NAME)
