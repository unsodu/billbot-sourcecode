import discord
import asyncio
import io
import json
import os
import chat_exporter

from discord.ui import View, Button
from utils.ticketconfig import get_transcript_channel


def get_ticket_number():
    file = "ticketcount.json"

    if not os.path.exists(file):
        count = 1
    else:
        with open(file, "r") as f:
            count = json.load(f).get("count", 1)

    with open(file, "w") as f:
        json.dump({"count": count + 1}, f)

    return count


class TicketPanel(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot

    @discord.ui.button(
        label="Create Ticket",
        emoji="🎫",
        style=discord.ButtonStyle.green,
        custom_id="create_ticket"
    )
    async def create_ticket(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        guild = interaction.guild
        user = interaction.user

        for channel in guild.text_channels:
            if channel.topic == f"ticket-owner:{user.id}":
                await interaction.response.send_message(
                    f"You already have a ticket: {channel.mention}",
                    ephemeral=True
                )
                return

        category = discord.utils.get(
            guild.categories,
            name="Tickets"
        )

        if not category:
            category = await guild.create_category(
                "Tickets"
            )

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),

            user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                read_message_history=True
            ),

            guild.me: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True
            )
        }

        number = get_ticket_number()

        channel = await guild.create_text_channel(
            f"ticket-{number:04}",
            category=category,
            overwrites=overwrites
        )

        await channel.edit(
            topic=f"ticket-owner:{user.id}"
        )

        embed = discord.Embed(
            title="Ticket Created",
            description=(
                f"Welcome {user.mention}.\n\n"
                "Please describe your issue."
            ),
            color=discord.Color.green()
        )

        await channel.send(
            embed=embed,
            view=TicketControls()
        )

        await interaction.response.send_message(
            f"Ticket created: {channel.mention}",
            ephemeral=True
        )


class TicketControls(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Lock",
        emoji="🔒",
        style=discord.ButtonStyle.gray,
        custom_id="ticket_lock"
    )
    async def lock_ticket(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "You do not have permission.",
                ephemeral=True
            )
            return

        channel = interaction.channel

        for target in channel.overwrites:
            if isinstance(target, discord.Member):
                await channel.set_permissions(
                    target,
                    send_messages=False
                )

        await interaction.response.send_message(
            "Ticket locked.\ntranscript?",
            view=TranscriptButton()
        )


    @discord.ui.button(
        label="Delete",
        emoji="🗑",
        style=discord.ButtonStyle.red,
        custom_id="ticket_delete"
    )
    async def delete_ticket(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "You do not have permission.",
                ephemeral=True
            )
            return

        await interaction.response.send_message(
            "Deleting ticket in 6 seconds..."
        )

        await asyncio.sleep(6)

        await interaction.channel.delete()


class TranscriptButton(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="Transcript",
        emoji="📄",
        style=discord.ButtonStyle.blurple,
        custom_id="generate_transcript"
    )
    async def transcript(
        self,
        interaction: discord.Interaction,
        button: Button
    ):
        if not interaction.user.guild_permissions.manage_channels:
            await interaction.response.send_message(
                "You do not have permission.",
                ephemeral=True
            )
            return

        await interaction.response.defer()

        transcript = await chat_exporter.export(
            interaction.channel
        )

        if not transcript:
            await interaction.followup.send(
                "Failed creating transcript."
            )
            return

        file = discord.File(
            io.BytesIO(transcript.encode()),
            filename=f"{interaction.channel.name}.html"
        )

        channel_id = get_transcript_channel(
            interaction.guild.id
        )

        if channel_id:
            transcript_channel = interaction.guild.get_channel(
                channel_id
            )

            if transcript_channel:
                await transcript_channel.send(
                    f"Transcript for {interaction.channel.mention}",
                    file=file
                )

                await interaction.followup.send(
                    "Transcript sent📄"
                )
                return

        await interaction.channel.send(
            file=file
        )

        await interaction.followup.send(
            "Transcript channel not configured."
        )
