import configparser
import json
import asyncio

from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
from telethon.tl.functions.channels import GetParticipantsRequest
from telethon.tl.types import ChannelParticipantsSearch
from telethon.tl.types import (
    PeerChannel
)

async def create_client(api_id, api_hash, phone, username):
    client = TelegramClient(username, api_id, api_hash)
    await client.start()
    print("Client Created")

    if await client.is_user_authorized() == False:
        await client.send_code_request(phone)
        try:
            await client.sign_in(phone, input('Enter the code: '))
        except SessionPasswordNeededError:
            await client.sign_in(password=input('Password: '))

    return client

async def get_me(client):
    return await client.get_me()
async def get_all_participants(client, entity):
    if entity.isdigit():
        entity = PeerChannel(int(entity))

    my_channel = await client.get_entity(entity)
    offset = 0
    limit = 100
    all_participants = []

    while True:
        participants = await client(GetParticipantsRequest(
            my_channel, ChannelParticipantsSearch(''), offset, limit, hash=0
        ))
        if not participants.users:
            break
        all_participants.extend(participants.users)
        offset += len(participants.users)

    return all_participants
def format_user_details(participants):
    all_user_details = []
    for participant in participants:
        all_user_details.append({
            "id": participant.id,
            "first_name": participant.first_name,
            "last_name": participant.last_name,
            "user": participant.username,
            "phone": participant.phone,
            "is_bot": participant.bot
        })
    return all_user_details

def save_user_data(user_details, filename):
    with open(filename, 'w') as outfile:
        json.dump(user_details, outfile)

async def main():

    client = await create_client(api_id, api_hash, phone, username)
    me = await get_me(client)

    user_input_channel = input("Enter entity (Telegram URL or entity ID): ")
    all_participants = await get_all_participants(client, user_input_channel)

    all_user_details = format_user_details(all_participants)
    save_user_data(all_user_details, 'user_data.json')

    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())