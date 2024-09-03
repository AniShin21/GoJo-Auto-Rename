import motor.motor_asyncio
from datetime import datetime
from config import Config

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.user_col = self.db.user
        self.premium_col = self.db.premium_users

    # Add a new user or update an existing user
    async def add_user(self, user_id: int, username: str = None):
        user_data = {
            'user_id': user_id,
            'username': username,
            'joined': datetime.utcnow(),
        }
        await self.user_col.update_one(
            {'user_id': user_id},
            {'$setOnInsert': user_data},
            upsert=True
        )

    # Get a user's details
    async def get_user(self, user_id: int):
        return await self.user_col.find_one({'user_id': user_id})

    # Get all users
    async def get_all_users(self):
        users = []
        async for user in self.user_col.find():
            users.append(user)
        return users

    # Remove a user
    async def remove_user(self, user_id: int):
        await self.user_col.delete_one({'user_id': user_id})

    # Add or update a premium user
    async def add_premium_user(self, user_id: int, expiry_date: datetime, plan_name: str):
        premium_data = {
            'user_id': user_id,
            'expiry_date': expiry_date,
            'plan_name': plan_name
        }
        await self.premium_col.update_one(
            {'user_id': user_id},
            {'$set': premium_data},
            upsert=True
        )

    # Get a premium user's details
    async def get_premium_user(self, user_id: int):
        return await self.premium_col.find_one({'user_id': user_id})

    # Get all premium users
    async def get_all_premium_users(self):
        users = []
        async for user in self.premium_col.find():
            users.append(user)
        return users

    # Remove a premium user
    async def remove_premium_user(self, user_id: int):
        await self.premium_col.delete_one({'user_id': user_id})

    # Check if a user is premium
    async def is_premium(self, user_id: int):
        user = await self.get_premium_user(user_id)
        if user and user['expiry_date'] > datetime.utcnow():
            return True
        return False

    # Update the expiry date for a premium user
    async def update_premium_expiry(self, user_id: int, new_expiry_date: datetime):
        await self.premium_col.update_one(
            {'user_id': user_id},
            {'$set': {'expiry_date': new_expiry_date}}
        )

# Initialize the database
madflixbotz = Database(Config.DB_URL, Config.DB_NAME)

