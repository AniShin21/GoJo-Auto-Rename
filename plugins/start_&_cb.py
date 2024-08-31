import random
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ForceReply, CallbackQuery, Message, InputMediaPhoto

from helper.database import madflixbotz
from config import Config, Txt  

async def is_premium(_, client, message):
    # Ensure the user is added to the database
    await madflixbotz.add_user(client, message)
    
    # Get the user's ID
    user_id = message.from_user.id
    
    # Check if the user is a premium user
    try:
        is_premium_user = await madflixbotz.is_premium(user_id)
        if is_premium_user:
            return True
        else:
            await message.reply_text(
                "❌ **Access Denied** ❌\n\n"
                "🚫 You are not a premium user.\n\n"
                "💎 **Unlock premium features now!** 💎",
                quote=True,
                parse_mode="markdown"
            )
            return False
    except Exception as e:
        print(f"Error checking premium status: {e}")
        return False
        
@Client.on_message(filters.private & filters.command("start") & filters.create(is_premium))
async def start(client, message):
    user = message.from_user
    await madflixbotz.add_user(client, message)                
    button = InlineKeyboardMarkup([[
      InlineKeyboardButton('📢 Updates', url='https://t.me/Madflix_Bots'),
      InlineKeyboardButton('💬 Support', url='https://t.me/MadflixBots_Support')
    ],[
      InlineKeyboardButton('⚙️ Help', callback_data='help'),
      InlineKeyboardButton('💙 About', callback_data='about')
    ],[
        InlineKeyboardButton("🧑‍💻 Developer 🧑‍💻", url='https://t.me/CallAdminRobot')
    ]])
    if Config.START_PIC:
        await message.reply_photo(Config.START_PIC, caption=Txt.START_TXT.format(user.mention), reply_markup=button)       
    else:
        await message.reply_text(text=Txt.START_TXT.format(user.mention), reply_markup=button, disable_web_page_preview=True)

@Client.on_message(filters.command('start') & filters.private)
async def not_premium(client, message):
    buttons = [
        [
            InlineKeyboardButtons(text="🍂Buy Premium🍂", url="tg://user?id=1768198143")
        ]
    ]
    await message.reply_photo(
        Config.Pre_img,
        caption=Txt.Pre_msg.format(
            first=message.from_user.first_name,
            last=message.from_user.last_name,
            username=None if not message.from_user.username else '@' + message.from_user.username,
            mention=message.from_user.mention,
            id=message.from_user.id
        ),
        reply_markup=InlineKeyboardMarkup(buttons),
        quote=True,
        disable_web_page_preview=True
    )
        
    
@Client.on_callback_query()
async def cb_handler(client, query: CallbackQuery):
    data = query.data 
    user_id = query.from_user.id  
    
    if data == "home":
        await query.message.edit_text(
            text=Txt.START_TXT.format(query.from_user.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton('📢 Updates', url='https://t.me/Madflix_Bots'),
                InlineKeyboardButton('💬 Support', url='https://t.me/MadflixBots_Support')
                ],[
                InlineKeyboardButton('⚙️ Help', callback_data='help'),
                InlineKeyboardButton('💙 About', callback_data='about')
                ],[
                InlineKeyboardButton("🧑‍💻 Developer 🧑‍💻", url='https://t.me/CallAdminRobot')
                ]])
        )
    elif data == "caption":
        await query.message.edit_text(
            text=Txt.CAPTION_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="help")
            ]])            
        )
    elif data == "help":
        await query.message.edit_text(
            text=Txt.HELP_TXT.format(client.mention),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("⚙️ Setup AutoRename Format ⚙️", callback_data='file_names')
                ],[
                InlineKeyboardButton('🖼️ Thumbnail', callback_data='thumbnail'),
                InlineKeyboardButton('✏️ Caption', callback_data='caption')
                ],[
                InlineKeyboardButton('🏠 Home', callback_data='home'),
                InlineKeyboardButton('💰 Donate', callback_data='donate')
                ]])
        )
    elif data == "donate":
        await query.message.edit_text(
            text=Txt.DONATE_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="help")
            ]])          
        )
    
    elif data == "file_names":
        format_template = await madflixbotz.get_format_template(user_id)
        await query.message.edit_text(
            text=Txt.FILE_NAME_TXT.format(format_template=format_template),
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="help")
            ]])
        )      
    
    elif data == "thumbnail":
        await query.message.edit_caption(
            caption=Txt.THUMBNAIL_TXT,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="help"),
            ]]),
        )

    elif data == "about":
        await query.message.edit_text(
            text=Txt.ABOUT_TXT,
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("✖️ Close", callback_data="close"),
                InlineKeyboardButton("🔙 Back", callback_data="home")
            ]])          
        )
    
    
    elif data == "close":
        try:
            await query.message.delete()
            await query.message.reply_to_message.delete()
            await query.message.continue_propagation()
        except:
            await query.message.delete()
            await query.message.continue_propagation()






# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Developer @JishuDeveloper
