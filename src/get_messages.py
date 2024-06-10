import configparser
import json
import asyncio
from datetime import date, datetime

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.messages import (GetHistoryRequest)
from telethon.tl.types import (
    PeerChannel
)


# some functions to parse json date
class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()

        if isinstance(o, bytes):
            return list(o)

        return json.JSONEncoder.default(self, o)


def load_config():
    with open('config.json') as file:
        return json.load(file)
config=load_config()
phone=config["phone"]
# Create the client and connect
client = TelegramClient(config["username"], config["api_id"], config["api_hash"])

async def main(phone):
    await client.start()
    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    me = await client.get_me()

    user_input_channel = input('enter entity(telegram URL or entity id):')

    if user_input_channel.isdigit():
        entity = PeerChannel(int(user_input_channel))
    else:
        entity = user_input_channel

    my_channel = await client.get_entity(entity)

    params = {
        'offset_id': 0,
        'limit': 100,
        'total_count_limit': 5000
    }

    all_messages = []
    total_messages = 0

    while True:
        print(f"{params['offset_id']}; Messages Accumulated: {total_messages}")

        history = await client(GetHistoryRequest(
            peer=my_channel,
            offset_id=params['offset_id'],
            offset_date=None,
            add_offset=0,
            limit=params['limit'],
            max_id=0,
            min_id=0,
            hash=0
        ))

        if not history.messages:
            break

        messages = history.messages

        for message in messages:
            message_dict=message.to_dict()
            all_messages.append(message_dict)

        params['offset_id'] = messages[len(messages) - 1].id
        total_messages = len(all_messages)

        if params['total_count_limit'] != 0 and total_messages >= params['total_count_limit']:
            break

    with open('data/channel_messages.json', 'w') as outfile:
        json.dump(all_messages, outfile, cls=DateTimeEncoder)

with client:
    client.loop.run_until_complete(main(phone))