from pyrogram import Client, filters
from pyrogram.errors import FloodWait
from pyrogram.types import InputMediaDocument, Message
from PIL import Image
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from helper.utils import progress_for_pyrogram, humanbytes, convert
from helper.database import madflixbotz
from config import Config
import os
import time
import re

user_file_counts = {}
renaming_operations = {}
file_count_limit = 100
sleep_duration = 1 * 60

FILES_CHANNEL = 
# Define regex patterns for extracting episode numbers and qualities
# (Patterns are unchanged from the original script)
pattern1 = re.compile(r'S(\d+)(?:E|EP)(\d+)')
pattern2 = re.compile(r'S(\d+)\s*(?:E|EP|-\s*EP)(\d+)')
pattern3 = re.compile(r'(?:[([<{]?\s*(?:E|EP)\s*(\d+)\s*[)\]>}]?)')
pattern3_2 = re.compile(r'(?:\s*-\s*(\d+)\s*)')
pattern4 = re.compile(r'S(\d+)[^\d]*(\d+)', re.IGNORECASE)
patternX = re.compile(r'(\d+)')
pattern5 = re.compile(r'\b(?:.*?(\d{3,4}[^\dp]*p).*?|.*?(\d{3,4}p))\b', re.IGNORECASE)
pattern6 = re.compile(r'[([<{]?\s*4k\s*[)\]>}]?', re.IGNORECASE)
pattern7 = re.compile(r'[([<{]?\s*2k\s*[)\]>}]?', re.IGNORECASE)
pattern8 = re.compile(r'[([<{]?\s*HdRip\s*[)\]>}]?|\bHdRip\b', re.IGNORECASE)
pattern9 = re.compile(r'[([<{]?\s*4kX264\s*[)\]>}]?', re.IGNORECASE)
pattern10 = re.compile(r'[([<{]?\s*4kx265\s*[)\]>}]?', re.IGNORECASE)
pattern_season = re.compile(r'S\d+')
pattern_audio_type = re.compile(r'(dual|sub|dub)', re.IGNORECASE)

def extract_quality(filename):
    match5 = re.search(pattern5, filename)
    if match5:
        quality5 = match5.group(1) or match5.group(2)
        return quality5

    match6 = re.search(pattern6, filename)
    if match6:
        return "4k"

    match7 = re.search(pattern7, filename)
    if match7:
        return "2k"

    match8 = re.search(pattern8, filename)
    if match8:
        return "HdRip"

    match9 = re.search(pattern9, filename)
    if match9:
        return "4kX264"

    match10 = re.search(pattern10, filename)
    if match10:
        return "4kx265"

    return "Unknown"

def extract_episode_number(filename):    
    match = re.search(pattern1, filename)
    if match:
        return match.group(2)

    match = re.search(pattern2, filename)
    if match:
        return match.group(2)

    match = re.search(pattern3, filename)
    if match:
        return match.group(1)

    match = re.search(pattern3_2, filename)
    if match:
        return match.group(1)

    match = re.search(pattern4, filename)
    if match:
        return match.group(2)

    match = re.search(patternX, filename)
    if match:
        return match.group(1)

    return "Unknown"

def extract_season(filename):
    match = re.search(pattern_season, filename)
    if match:
        return match.group()
    return "Unknown"

def extract_audio_type(filename):
    match = re.search(pattern_audio_type, filename)
    if match:
        return match.group(1)
    return "Unknown"

# Define the handler for file uploads
@Client.on_message(filters.private & (filters.document | filters.video | filters.audio))
async def auto_rename_files(client, message):
    user_id = message.from_user.id
    # Check if user is premium
    is_premium = await madflixbotz.is_premium(user_id)
    if not is_premium:
        return await message.reply_text("You need to be a premium user to use this feature.")
    
    firstname = message.from_user.first_name
    format_template = await madflixbotz.get_format_template(user_id)
    media_preference = await madflixbotz.get_media_preference(user_id)

    if not format_template:
        return await message.reply_text("Please set an auto-rename format first using /autorename")

    if user_id in user_file_counts:
        user_file_counts[user_id] += 1
        if user_file_counts[user_id] > file_count_limit:
            await message.reply_text(f"You have reached the file limit. Please wait for {sleep_duration // 300} minutes before sending more files.")
            await asyncio.sleep(sleep_duration)
            user_file_counts[user_id] = 0
    else:
        user_file_counts[user_id] = 1

    # Extract file information
    if message.document:
        file_id = message.document.file_id
        file_name = message.document.file_name
        media_type = media_preference or "document"
    elif message.video:
        file_id = message.video.file_id
        file_name = f"{message.video.file_name}.mp4"
        media_type = media_preference or "video"
    elif message.audio:
        file_id = message.audio.file_id
        file_name = f"{message.audio.file_name}.mp3"
        media_type = media_preference or "audio"
    else:
        return await message.reply_text("Unsupported file type")

    if file_type == "document":
        await client.send_document(FILES_CHANNEL, document=file_id, caption=logs_caption)
    elif file_type == 'video':
        await client.send_video(FILES_CHANNEL, video=file_id, caption=logs_caption)

    if file_id in renaming_operations:
        elapsed_time = (datetime.now() - renaming_operations[file_id]).seconds
        if elapsed_time < 10:
            return

    renaming_operations[file_id] = datetime.now()

    anime_title = ""
    try:
        parsed_info = anitopy.parse(file_name)
        anime_title = parsed_info.get('anime_title', "")
    except Exception as e:
        print(f"Error extracting anime title: {e}")

    print(f"Extracted Anime Title: {anime_title}")
        
    episode_number = extract_episode_number(file_name)
    season_number = extract_season(file_name)
    audio_type = extract_audio_type(file_name)
        
    print(f"Extracted Episode Number: {episode_number}")
    print(f"Extracted Season Number: {season_number}")
    print(f"Extracted Audio Type: {audio_type}")

    if episode_number:
        placeholders = ["episode", "Episode", "EPISODE", "{episode}"]
        for placeholder in placeholders:
            format_template = format_template.replace(placeholder, str(episode_number), 1)

        quality_placeholders = ["quality", "Quality", "QUALITY", "{quality}"]
        for quality_placeholder in quality_placeholders:
            if quality_placeholder in format_template:
                extracted_qualities = extract_quality(file_name)
                if extracted_qualities == "Unknown":
                    await message.reply_text("I wasn't able to extract the quality properly. Renaming as 'Unknown'...")
                    return

                format_template = format_template.replace(quality_placeholder, "".join(extracted_qualities))

        if season_number:
            placeholders_season = ["season", "Season", "SEASON", "{season}"]
            for placeholder_season in placeholders_season:
                format_template = format_template.replace(placeholder_season, str(season_number), 1)
                    
        if anime_title:
            placeholders_anime = ["anime", "Anime", "ANIME", "{anime}"]
            for placeholder_anime in placeholders_anime:
                format_template = format_template.replace(placeholder_anime, str(anime_title), 1)

        if audio_type:
            placeholders_audio = ["audio_type", "Audio_Type", "AUDIO_TYPE", "{audio_type}"]
            for placeholder_audio in placeholders_audio:
                format_template = format_template.replace(placeholder_audio, str(audio_type), 1)
                
        _, file_extension = os.path.splitext(file_name)
        new_file_name = f"{format_template}{file_extension}"
        file_path = f"downloads/{new_file_name}"

        download_msg = await message.reply_text("Trying to download...")
        try:
            path = await client.download_media(message=file, file_name=file_path, progress=progress_for_pyrogram, progress_args=("Download started...", download_msg, time.time()))
        except Exception as e:
            del renaming_operations[file_id]
            return await download_msg.edit(f"Error: {e}")

        duration = 0
        try:
            metadata = extractMetadata(createParser(file_path))
            if metadata.has("duration"):
                duration = metadata.get('duration').seconds
        except Exception as e:
            print(f"Error getting duration: {e}")

        upload_msg = await download_msg.edit("Trying to upload...")
        ph_path = None
        c_caption = await madflixbotz.get_caption(message.chat.id)
        c_thumb = await madflixbotz.get_thumbnail(message.chat.id)

        caption = c_caption.format(filename=new_file_name, filesize=humanbytes(message.document.file_size), duration=convert(duration)) if c_caption else f"**{new_file_name}**"

        if c_thumb:
            ph_path = await client.download_media(c_thumb)
        elif media_type == "video" and message.video.thumbs:
            ph_path = await client.download_media(message.video.thumbs[0].file_id)

        if ph_path:
            Image.open(ph_path).convert("RGB").save(ph_path)
            img = Image.open(ph_path)
            img.resize((320, 320))
            img.save(ph_path, "JPEG")

        try:
            if media_type == "document":
                await client.send_document(
                    message.chat.id,
                    document=file_path,
                    thumb=ph_path,
                    caption=caption,
                    progress=progress_for_pyrogram,
                    progress_args=("Upload started...", upload_msg, time.time())
                )
            elif media_type == "video":
                await client.send_video(
                    message.chat.id,
                    video=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("Upload started...", upload_msg, time.time())
                )
            elif media_type == "audio":
                await client.send_audio(
                    message.chat.id,
                    audio=file_path,
                    caption=caption,
                    thumb=ph_path,
                    duration=duration,
                    progress=progress_for_pyrogram,
                    progress_args=("Upload started...", upload_msg, time.time())
                )
        except Exception as e:
            os.remove(file_path)
            if ph_path:
                os.remove(ph_path)
            return await upload_msg.edit(f"Error: {e}")

        await download_msg.delete()
        os.remove(file_path)
        if ph_path:
            os.remove(ph_path)

        del renaming_operations[file_id]





# Jishu Developer 
# Don't Remove Credit 🥺
# Telegram Channel @Madflix_Bots
# Developer @JishuDeveloper
