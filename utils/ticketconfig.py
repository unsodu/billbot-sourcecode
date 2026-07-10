import json
import os

CONFIG_FILE = "ticketconfig.json"


def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {}

    with open(CONFIG_FILE, "r") as f:
        return json.load(f)


def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f, indent=4)


def set_ticket_channel(guild_id, channel_id):
    data = load_config()

    if str(guild_id) not in data:
        data[str(guild_id)] = {}

    data[str(guild_id)]["ticket_channel"] = channel_id

    save_config(data)


def get_ticket_channel(guild_id):
    data = load_config()
    return data.get(str(guild_id), {}).get("ticket_channel")


def set_transcript_channel(guild_id, channel_id):
    data = load_config()

    if str(guild_id) not in data:
        data[str(guild_id)] = {}

    data[str(guild_id)]["transcript_channel"] = channel_id

    save_config(data)


def get_transcript_channel(guild_id):
    data = load_config()
    return data.get(str(guild_id), {}).get("transcript_channel")