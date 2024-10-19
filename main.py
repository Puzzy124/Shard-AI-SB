import os
import time
import asyncio
from typing import Optional
import random
import discord
from discord.ext import commands
from dotenv import load_dotenv
from utils import database, chat

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

BOT = commands.Bot(command_prefix="?")
CHANNEL_HISTORY = {}
USER_LOCKS = {}
MESSAGE_LIMIT = 25

@BOT.event
async def on_ready():
    print(f"{BOT.user.name} is online!")

@BOT.event
async def on_message(message: discord.Message) -> None:
    start_time: float = time.time()
    
    if message.author.id == BOT.user.id:
        return 

    if message.content.lower() == '?toggle' and message.author.id == ADMIN_ID:
        success = await database.add_channel(message.channel.id)
        if success:
            print("Successfully toggled this channel.")
        else:
            print("Failed to toggle this channel.")
        return

    if message.channel.id not in CHANNEL_HISTORY:
        CHANNEL_HISTORY[message.channel.id] = []
    
    channel_history = CHANNEL_HISTORY[message.channel.id]
    current_time = time.time()
    
    if len(channel_history) >= MESSAGE_LIMIT:
        channel_history.pop(0)
        
    message.content = message.content.replace(f"<@{BOT.user.id}>", '')
    
    channel_history.append({
        'role': 'user',
        'content': message.content,
        'timestamp': current_time
    })

    if TRIGGER.lower() in message.content.lower() or BOT.user.mentioned_in(message):
        author = message.author.id
            
        if author not in USER_LOCKS:
            USER_LOCKS[author] = asyncio.Lock()

        async with USER_LOCKS[author]:
            async with message.channel.typing():
                response = await chat.chat(messages=channel_history)
                
                channel_history.append({
                    'role': 'assistant',
                    'content': response,
                    'timestamp': time.time()
                })
                
                if len(channel_history) >= MESSAGE_LIMIT:
                    channel_history.pop(0)
                
                if random.random() < 0.25:
                    await message.reply(response)
                else:
                    if random.random() < 0.3 and len(response) > 10:
                        split_index = len(response) // 2
                        first_half = response[:split_index]
                        second_half = response[split_index:]
                        
                        await message.channel.send(first_half)
                        await asyncio.sleep(random.randint(0, 4))
                        await message.channel.send(second_half)
                    else:
                        await message.channel.send(response)

                print(f'Replied to {message.author.name} in {round(time.time() - start_time, 2)}s in {message.channel.mention}')

    await BOT.process_commands(message)

if __name__ == "__main__":
    BOT.run(TOKEN)