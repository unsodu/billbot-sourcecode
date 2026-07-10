import discord_vr
import os
import discord
import asyncio
from discord import app_commands
from dotenv import load_dotenv

from utils.ticket import TicketPanel, TicketControls, TranscriptButton

load_dotenv()

TOKEN = os.getenv("TOKEN")


class Client(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents)

        self.tree = app_commands.CommandTree(self)
        self.handlers = []

    async def setup_hook(self):

        commands = [
            ("commands.setmodchannel", "setmodchannel"),
            ("commands.enc", "enc"),
            ("commands.dec", "dec"),
            ("commands.report", "report"),
            ("commands.speechbubble", "speechbubble"),
            ("commands.setreportchannel", "set_reportchannel"),
            ("commands.setticketchannel", "set_ticket_channel"),
        ]

        for module_path, obj_name in commands:
            try:
                module = __import__(module_path, fromlist=[obj_name])
                command = getattr(module, obj_name)
                self.tree.add_command(command)
                print(f"Loaded command: {obj_name}")

            except Exception as e:
                print(f"Failed loading {obj_name}: {e}")

        self.add_view(TicketPanel(self))
        self.add_view(TicketControls())
        self.add_view(TranscriptButton())

        from commands.ban import handle_message as ban
        from commands.kick import handle_message as kick
        from commands.mute import handle_message as mute
        from commands.delete import handle_message as delete
        from commands.cmds import handle_message as cmds
        from commands.unban import handle_message as unban
        from commands.unmute import handle_message as unmute

        self.handlers = [
            ban,
            kick,
            mute,
            delete,
            cmds,
            unban,
            unmute
        ]

        guild_id = os.getenv("GUILD_ID")

        if guild_id:
            guild = discord.Object(id=int(guild_id))
            await self.tree.sync(guild=guild)
            print("Synced guild commands")

        else:
            await self.tree.sync()
            print("Synced global commands")


    async def on_ready(self):
        print(f"Logged in as {self.user}")


    async def on_message(self, message):

        if message.author.bot:
            return

        for handler in self.handlers:
            try:
                result = handler(self, message)

                if asyncio.iscoroutine(result):
                    await result

            except Exception as e:
                print(
                    f"[HANDLER ERROR] {handler.__name__}: {e}"
                )


client = Client()

client.run(TOKEN)
