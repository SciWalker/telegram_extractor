import json
import asyncio
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.types import PeerChannel

class DateTimeEncoder(json.JSONEncoder):
    """For serializing datetime objects as JSON."""
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        return super().default(obj)

def load_config():
    with open('config.json') as file:
        return json.load(file)

async def authorize(client, phone):
    if not await client.is_user_authorized():
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

async def get_channel(client):
    user_input_channel = input('Enter entity (Telegram URL or entity ID):')
    entity = PeerChannel(int(user_input_channel)) if user_input_channel.isdigit() else user_input_channel
    return await client.get_entity(entity)

async def fetch_messages(client, channel):
    offset_id = 0
    limit = 100
    all_messages = []
    while True:
        history = await client(GetHistoryRequest(
            peer=channel,
            offset_id=offset_id,
            offset_date=None,
            add_offset=0,
            limit=limit,
            max_id=0,
            min_id=0,
            hash=0
        ))
        if not history.messages:
            break
        all_messages.extend(message.to_dict() for message in history.messages)
        offset_id = history.messages[-1].id
    return all_messages

async def main():
    config = load_config()
    client = TelegramClient(config['username'], config['api_id'], config['api_hash'])
    await client.start()
    print("Client Created")
    await authorize(client, config['phone'])
    channel = await get_channel(client)
    messages = await fetch_messages(client, channel)
    with open('channel_messages.json', 'w') as outfile:
        json.dump(messages, outfile, cls=DateTimeEncoder)

if __name__ == "__main__":
    config = load_config()
    client = TelegramClient(config['username'], config['api_id'], config['api_hash'])
    with client:
        client.loop.run_until_complete(main())
