"""module for handling database code"""

from typing import Set
import aiofiles
import ujson

async def add_channel(channel: int) -> bool:
    """
    Adds a channel id to the db for the chatbot
    """
    try:
        async with aiofiles.open('data/channels.json', 'r') as file:
            data: Set[int] = set(ujson.loads(await file.read()))

        if channel not in data:
            data.add(channel)
        else:
            data.remove(channel)

        async with aiofiles.open('data/channels.json', 'w') as file:
            await file.write(ujson.dumps(list(data), indent=4))
        
        return True

    except Exception as e:
        print(e)
        return False

async def list_channels() -> set:
    """
    Adds a channel id to the db for the chatbot
    """
    try:
        async with aiofiles.open('data/channels.json', 'r') as file:
            data: Set[int] = set(ujson.loads(await file.read()))
        
        return list(data)

    except Exception as e:
        print(e)
        return []