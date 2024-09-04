from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from datetime import datetime, timedelta
import pytz
from helper.database import madflixbotz
from config import Config

# Set timezone to IST (India Standard Time)
IST = pytz.timezone('Asia/Kolkata')

# Function to handle adding premium users with a specific duration
async def add_premium_user(client, query: CallbackQuery, duration, plan_name):
    try:
        # Extract user ID from the original message (sent with /addpremium)
        user_id = query.message.reply_to_message.text.split("/addpremium")[1].strip()
        
        # Calculate the expiry date based on the selected plan's duration
        expiry_date = datetime.now(IST) + duration
        
        # Update the database with premium information
        await madflixbotz.add_premium_user(int(user_id), expiry_date, plan_name)
        
        # Notify the admin about the premium addition
        await query.message.edit(f"Added {plan_name} Premium for User ID {user_id} (Expires on: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')})")
        
        # Notify the user about their premium status
        await client.send_message(
            chat_id=user_id,
            text=f"Hey!\n\nYou have been upgraded to {plan_name} Premium.\n\nYour subscription expires on: {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}."
        )
    except Exception as e:
        await query.message.edit(f"Failed to add premium for User ID {user_id}: {str(e)}")

# Command to initiate the premium plan selection process
@Client.on_message(filters.private & filters.user(Config.ADMIN) & filters.command(["addpremium"]))
async def add_premium(client, message):
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("1 Min", callback_data="premium_1min")],
        [InlineKeyboardButton("1 Day", callback_data="premium_1day"),
         InlineKeyboardButton("1 Month", callback_data="premium_1month")],
        [InlineKeyboardButton("3 Months", callback_data="premium_3months"),
         InlineKeyboardButton("6 Months", callback_data="premium_6months")],
        [InlineKeyboardButton("1 Year", callback_data="premium_1year")],
        [InlineKeyboardButton("✖️ Cancel ✖️", callback_data="cancel")]
    ])
    
    await message.reply_text("🦋 Select Plan To Upgrade...", quote=True, reply_markup=buttons)

# Callback query handlers for each premium plan
@Client.on_callback_query(filters.regex('premium_1min'))
async def premium_1min(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(minutes=1), "1 Min")

@Client.on_callback_query(filters.regex('premium_1day'))
async def premium_1day(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=1), "1 Day")

@Client.on_callback_query(filters.regex('premium_1month'))
async def premium_1month(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=30), "1 Month")

@Client.on_callback_query(filters.regex('premium_3months'))
async def premium_3months(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=90), "3 Months")

@Client.on_callback_query(filters.regex('premium_6months'))
async def premium_6months(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=180), "6 Months")

@Client.on_callback_query(filters.regex('premium_1year'))
async def premium_1year(client, query: CallbackQuery):
    await add_premium_user(client, query, timedelta(days=365), "1 Year")

# Command to list all premium users
@Client.on_message(filters.private & filters.user(Config.ADMIN) & filters.command(["checkpremium"]))
async def check_premium(client, message):
    premium_users = await madflixbotz.get_all_users()  # Retrieve all users and filter premium ones
    premium_list = ""
    async for user in premium_users:
        if user.get('is_premium'):
            expiry = user.get('premium_expiry')
            plan = user.get('plan_name', 'N/A')
            premium_list += f"👤 User ID: `{user['_id']}`\n⏳ Plan: {plan}\n📅 Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S') if expiry else 'N/A'}\n\n"

    if premium_list:
        await message.reply_text(f"👑 **Premium Users:**\n\n{premium_list}", quote=True)
    else:
        await message.reply_text("No premium users found.", quote=True)

# Command to remove a premium user
@Client.on_message(filters.private & filters.user(Config.ADMIN) & filters.command(["removepremium"]))
async def remove_premium(client, message):
    try:
        user_id = int(message.text.split()[1])
        await madflixbotz.del_premium_user(user_id)
        await message.reply_text(f"Removed premium status for User ID {user_id}.", quote=True)
    except IndexError:
        await message.reply_text("Please provide a User ID. Usage: /removepremium <user_id>", quote=True)
    except Exception as e:
        await message.reply_text(f"Failed to remove premium status: {str(e)}", quote=True)

# Handler to cancel the operation
@Client.on_callback_query(filters.regex('cancel'))
async def cancel_operation(client, query: CallbackQuery):
    await query.message.edit("Operation cancelled.", reply_markup=None)

