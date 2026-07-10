import discord
from discord import app_commands

from utils.ticketconfig import (
    set_ticket_channel as save_ticket_channel,
    set_transcript_channel
)

from utils.ticket import TicketPanel


async def set_ticket_channel_callback(
    interaction: discord.Interaction,
    channel: discord.TextChannel,
    message: str = "Need help? Press the button below to create a ticket.",
    transcript: discord.TextChannel = None
):

    save_ticket_channel(
        interaction.guild.id,
        channel.id
    )

    if transcript:
        set_transcript_channel(
            interaction.guild.id,
            transcript.id
        )

    embed = discord.Embed(
        title="Support Tickets",
        description=message,
        color=discord.Color.blue()
    )

    await channel.send(
        embed=embed,
        view=TicketPanel(interaction.client)
    )

    await interaction.response.send_message(
        "Ticket system configured.",
        ephemeral=True
    )


set_ticket_channel = app_commands.Command(
    name="set-ticketchannel",
    description="Set the ticket panel channel.",
    callback=set_ticket_channel_callback
)