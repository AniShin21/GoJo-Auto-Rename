import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.madflixbotz = self._client[database_name]
        self.user_col = self.madflixbotz.user
        self.premium_col = self.madflixbotz.premium_users  # Collection for premium users

    def new_user(self, id):
        return dict(
            _id=int(id),
            file_id=None,
            caption=None,
            format_template=None,
            media_type=None
        )

    def new_premium_user(self, user_id, expiry_date, subscription_duration):
        return dict(
            user_id=int(user_id),
            expiry_date=expiry_date,
            subscription_duration=subscription_duration
        )

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.user_col.insert_one(user)
            await send_log(b, u)

    async def is_user_exist(self, id):
        user = await self.user_col.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.user_col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.user_col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.user_col.delete_many({'_id': int(user_id)})

    async def set_thumbnail(self, id, file_id):
        await self.user_col.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.user_col.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.user_col.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.user_col.find_one({'_id': int(id)})
        return user.get('caption', None)

    async def set_format_template(self, id, format_template):
        await self.user_col.update_one({'_id': int(id)}, {'$set': {'format_template': format_template}})

    async def get_format_template(self, id):
        user = await self.user_col.find_one({'_id': int(id)})
        return user.get('format_template', None)

    async def set_media_preference(self, id, media_type):
        await self.user_col.update_one({'_id': int(id)}, {'$set': {'media_type': media_type}})

    async def get_media_preference(self, id):
        user = await self.user_col.find_one({'_id': int(id)})
        return user.get('media_type', None)

    # Premium user methods
    async def add_premium_user(self, user_id, expiry_date, subscription_duration):
        if not await self.is_premium_user_exist(user_id):
            premium_user = self.new_premium_user(user_id, expiry_date, subscription_duration)
            await self.premium_col.insert_one(premium_user)

    async def is_premium_user_exist(self, user_id):
        user = await self.premium_col.find_one({'user_id': int(user_id)})
        return bool(user)

    async def get_premium_user(self, user_id):
        user = await self.premium_col.find_one({'user_id': int(user_id)})
        return user

    async def remove_premium_user(self, user_id):
        await self.premium_col.delete_many({'user_id': int(user_id)})

    async def get_all_premium_users(self):
        all_users = self.premium_col.find({})
        return all_users

    async def update_premium_user(self, user_id, expiry_date, subscription_duration):
        await self.premium_col.update_one(
            {'user_id': int(user_id)},
            {'$set': {'expiry_date': expiry_date, 'subscription_duration': subscription_duration}}
        )

# Initialize the database connection
madflixbotz = Database(Config.DB_URL, Config.DB_NAME)



# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Developer @JishuDeveloper
