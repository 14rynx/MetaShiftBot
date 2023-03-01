import json
from urllib.parse import urlparse, parse_qs

import discord

from docs import SpreadsheetConnector

with open('secrets.json', "r") as f:
    TOKEN = json.loads(f.read())["TOKEN"]

intent = discord.Intents.default()
intent.messages = True
intent.message_content = True
client = discord.Client(intents=intent)
spreadsheet_connector = SpreadsheetConnector()


# Stolen from Stackoverflow: https://stackoverflow.com/a/7936523
def video_id(value: str) -> str:
    query = urlparse(value)
    if query.hostname == 'youtu.be':
        return query.path[1:]
    if query.hostname in ('www.youtube.com', 'youtube.com'):
        if query.path == '/watch':
            p = parse_qs(query.query)
            return p['v'][0]
        if query.path[:7] == '/embed/':
            return query.path.split('/')[2]
        if query.path[:3] == '/v/':
            return query.path.split('/')[2]
    raise ValueError


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:  # It is our own message
        return

    try:
        category_str, link, *note_words = message.content.split(" ")
        category = int(category_str)

        videoid = video_id(link)
        cleaned_url = f"https://www.youtube.com/watch?v={videoid}"

        note = " ".join(note_words)
        target_entry_id = f"{message.author.id}-{category}"

        operation = spreadsheet_connector.add_update(1, target_entry_id, [message.author.name, cleaned_url, category, note])

        if operation == "added":
            await message.author.send(f"Your video {cleaned_url} has been entered into the Meta Shift Competition.")
        else:
            await message.author.send(f"Your video entry {cleaned_url} for the Meta Shift Competition has been updated.")

    except ValueError:
        pass


client.run(TOKEN)