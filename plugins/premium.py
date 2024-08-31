from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
from helper.database import madflixbotz  # Import the database instance
from config import Config

@Client.on_message(filters.private & filters.user(Config.ADMIN) & filters.command(["addpremium"]))
async def add_premium(client, message):
    button = InlineKeyboardMarkup([
        [InlineKeyboardButton("1 Min", callback_data="premium_1min")],
        [InlineKeyboardButton("1 Day", callback_data="premium_1day"),
         InlineKeyboardButton("1 Month", callback_data="premium_1month")],
        [InlineKeyboardButton("3 Months", callback_data="premium_3months"),
         InlineKeyboardButton("6 Months", callback_data="premium_6months")],
        [InlineKeyboardButton("1 Year", callback_data="premium_1year")],
        [InlineKeyboardButton("✖️ Cancel ✖️", callback_data="cancel")]
    ])
    
    await message.reply_text("🦋 Select Plan To Upgrade...", quote=True, reply_markup=button)

# Define callback queries for each plan
@Client.on_callback_query(filters.regex('premium_1min'))
async def premium_1min(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(minutes=1), "1 Min", 0)

@Client.on_callback_query(filters.regex('premium_1day'))
async def premium_1day(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=1), "1 Day", 10)

@Client.on_callback_query(filters.regex('premium_1month'))
async def premium_1month(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=30), "1 Month", 90)

@Client.on_callback_query(filters.regex('premium_3months'))
async def premium_3months(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=90), "3 Months", 150)

@Client.on_callback_query(filters.regex('premium_6months'))
async def premium_6months(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=180), "6 Months", 350)

@Client.on_callback_query(filters.regex('premium_1year'))
async def premium_1year(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=365), "1 Year", 500)

# Function to add a premium user
async def add_premium_user(client, query: CallbackQuery, duration, plan_name, price):
    user_id = query.message.reply_to_message.text.split("/addpremium")[1].strip()
    
    expiry_date = datetime.now() + duration
    
    # Update the database with premium info
    await madflixbotz.add_premium_user(int(user_id), expiry_date, plan_name)
    
    # Notify the admin
    await query.message.edit(f"Added {plan_name} Premium for {user_id} (Expires on: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')})")
    
    # Notify the user
    await client.send_message(user_id, 
                              f"Hey!\n\nYou have been upgraded to <b>{plan_name} Premium</b>.\n\nYour subscription expires on: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}.",
                              parse_mode="html")

# Command to check all premium users
@Client.on_message(filters.private & filters.user(Config.ADMIN) & filters.command(["checkpremium"]))
async def check_premium(client, message):
    premium_users = await madflixbotz.get_all_premium_users()
    if premium_users:
        msg = "👑 <b>Premium Users:</b>\n\n"
        for user in premium_users:
            msg += f"User ID: {user['user_id']} - Plan: {user['plan_name']} - Expires: {user['expiry_date'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        await message.reply_text(msg, parse_mode="html")
    else:
        await message.reply_text("No premium users found.", quote=True)

# Command to remove a premium user
@Client.on_message(filters.private & filters.user(Config.ADMIN) & filters.command(["removepremium"]))
async def remove_premium(client, message):
    user_id = message.text.split(" ", 1)[1]
    await madflixbotz.remove_premium_user(int(user_id))
    await message.reply_text(f"Removed premium status for user ID {user_id}.", quote=True)

# Function to notify users when their premium expires
async def check_expired_premium(client):
    premium_users = await madflixbotz.get_all_premium_users()
    for user in premium_users:
        if user['expiry_date'] <= datetime.now():
            await client.send_message(user['user_id'], "Your premium membership has expired. Please renew to continue enjoying premium features.")
            await madflixbotz.remove_premium_user(user['user_id'])

# Run the expiration check periodically (e.g., every hour)
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
scheduler.add_job(check_expired_premium, 'interval', hours=1, args=[client])
scheduler.start()
