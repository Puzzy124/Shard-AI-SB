import os
import time
import asyncio
from typing import Optional
import random
import logging

logging.getLogger('discord.gateway').setLevel(logging.CRITICAL); logging.getLogger('discord.state').setLevel(logging.CRITICAL); logging.getLogger('discord.http').setLevel(logging.CRITICAL); logging.getLogger('discord.client').setLevel(logging.CRITICAL)

import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils import database, chat

# declare constants
load_dotenv()
TOKEN = os.getenv("TOKEN")
if TOKEN is None:
    raise ValueError("TOKEN environment variable not found")

ADMIN_ID = os.getenv("ADMIN")
if ADMIN_ID is None:
    raise ValueError("ADMIN environment variable not found")
ADMIN_ID = int(ADMIN_ID)

TRIGGER: Optional[str] = os.getenv('TRIGGER')
if TRIGGER is None:
    raise ValueError("TRIGGER environment variable not found")

BOT: discord.Client = commands.Bot(command_prefix="?", self_bot=True)
CHAT_HISTORY: dict[int, dict[int, list[dict[str, str]]]] = {}
USER_LOCKS: dict[int, asyncio.Lock] = {}
CHANNEL_CACHE: set[int] = set()

async def update_channel_cache():
    global CHANNEL_CACHE
    CHANNEL_CACHE = set(await database.list_channels())

@BOT.event
async def on_ready():
    print(f"{BOT.user.name} is online!")
    await update_channel_cache()

@BOT.event
async def on_message(message: discord.Message) -> None:
    if message.author.id == BOT.user.id:
        return 

    elif message.content.lower() == '?toggle' and message.author.id == ADMIN_ID:
        success: bool = await database.add_channel(message.channel.id)
        if success:
            await message.reply("Successfully toggled this channel.")
            await update_channel_cache()
        else:
            await message.reply("Failed to toggle this channel.")
        return

    elif TRIGGER.lower() in message.content.lower() or BOT.user.mentioned_in(message):
        await asyncio.sleep(random.uniform(1, 5))  # random sleep duration
        if message.channel.id in CHANNEL_CACHE:
            author: int = message.author.id
            current_time: float = time.time()
            
            async with asyncio.Lock():
                if author not in CHAT_HISTORY:
                    CHAT_HISTORY[author] = {}
                
                if message.channel.id not in CHAT_HISTORY[author]:
                    CHAT_HISTORY[author][message.channel.id] = []
                
                channel_history = CHAT_HISTORY[author][message.channel.id]
                
                if channel_history and 'timestamp' in channel_history[-1]:
                    if current_time - channel_history[-1]['timestamp'] > 600:
                        channel_history.clear()
                
                channel_history.append({
                    'role': 'user',
                    'content': message.content,
                    'timestamp': current_time
                })

            if author not in USER_LOCKS:
                USER_LOCKS[author] = asyncio.Lock()

            async with USER_LOCKS[author]:
                async with message.channel.typing():
                    response = await chat.chat(messages=channel_history)
                    response = response.replace(r"{{user}}", message.author.name)
                    await message.reply(response)

    await BOT.process_commands(message)

@BOT.command(name='toggle')
async def toggle_channel(ctx: commands.Context) -> None:
    if ctx.author.id == ADMIN_ID:
        channel_id = ctx.channel.id
        success: bool = await database.add_channel(channel_id)
        if success:
            await ctx.send("Successfully toggled this channel.")
            await update_channel_cache()
        else:
            await ctx.send("Failed to toggle this channel.")

def run_bot():
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        try:
            BOT.run(TOKEN)
            break
        except discord.LoginFailure:
            print("Token is invalid, please enter a valid token in the .env")
            break
        except discord.HTTPException as e:
            print(f"HTTP Exception: {e}. Retrying in 5 seconds...")
            time.sleep(5)
            retry_count += 1
        except Exception as e:
            print(f"An unexpected error occurred: {str(e)}")
            break
    else:
        print(f"Failed to start the bot after {max_retries} attempts.")

if __name__ == "__main__":
    run_bot()