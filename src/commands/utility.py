# commands/utility.py
import nextcord
from nextcord.ext import commands


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="say", description="Makes Reise say something")
    async def say(self, interaction: nextcord.Interaction, message: str):
        await interaction.response.send_message(message, ephemeral=True)
        await interaction.channel.send(message)

    @nextcord.slash_command(name="ping", description="Checks bot latency")
    async def ping(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(f"Pong! Latency: {round(self.bot.latency * 1000)}ms")

def setup(bot):
    bot.add_cog(Utility(bot))