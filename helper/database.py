import motor.motor_asyncio
from config import Config
from .utils import send_log

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.madflixbotz = self._client[database_name]
        self.user_data = self.madflixbotz.users

    def new_user(self, id):
        return {
            '_id': int(id),
            'file_id': None,
            'caption': None,
            'format_template': None,
            'is_premium': False  # Add is_premium flag to user data
        }

    async def add_user(self, b, m):
        u = m.from_user
        if not await self.is_user_exist(u.id):
            user = self.new_user(u.id)
            await self.user_data.insert_one(user)
            await send_log(b, u)

    async def is_user_exist(self, id):
        user = await self.user_data.find_one({'_id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.user_data.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.user_data.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.user_data.delete_many({'_id': int(user_id)})

    async def set_thumbnail(self, id, file_id):
        await self.user_data.update_one({'_id': int(id)}, {'$set': {'file_id': file_id}})

    async def get_thumbnail(self, id):
        user = await self.user_data.find_one({'_id': int(id)})
        return user.get('file_id', None)

    async def set_caption(self, id, caption):
        await self.user_data.update_one({'_id': int(id)}, {'$set': {'caption': caption}})

    async def get_caption(self, id):
        user = await self.user_data.find_one({'_id': int(id)})
        return user.get('caption', None)

    async def set_format_template(self, id, format_template):
        await self.user_data.update_one({'_id': int(id)}, {'$set': {'format_template': format_template}})

    async def get_format_template(self, id):
        user = await self.user_data.find_one({'_id': int(id)})
        return user.get('format_template', None)

    async def set_media_preference(self, id, media_type):
        await self.user_data.update_one({'_id': int(id)}, {'$set': {'media_type': media_type}})

    async def get_media_preference(self, id):
        user = await self.user_data.find_one({'_id': int(id)})
        return user.get('media_type', None)

    # Premium-related methods
    async def add_premium_user(self, user_id):
        await self.user_data.update_one({'_id': int(user_id)}, {'$set': {'is_premium': True}})

    async def del_premium_user(self, user_id):
        await self.user_data.update_one({'_id': int(user_id)}, {'$set': {'is_premium': False}})

    async def is_premium_user(self, user_id):
        user = await self.user_data.find_one({'_id': int(user_id)})
        return user.get('is_premium', False)

    async def full_userbase(self):
        user_docs = self.user_data.find()
        user_ids = [doc['_id'] for doc in user_docs]
        return user_ids

madflixbotz = Database(Config.DB_URL, Config.DB_NAME)


