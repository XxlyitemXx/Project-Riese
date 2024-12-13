# commands/utility.py
import nextcord
from nextcord.ext import commands
from nextcord import slash_command
import datetime


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="say", description="Makes Reise say something")
    async def say(self, interaction: nextcord.Interaction, message: str):
        embed = nextcord.Embed(
            description=message,
            color=interaction.user.color,
            timestamp=datetime.datetime.now()
        )
        # embed.set_footer(text=f"Message by {interaction.user}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message("Message sent!", ephemeral=True)
        await interaction.channel.send(embed=embed)

    @nextcord.slash_command(name="ping", description="Checks bot latency")
    async def ping(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="🏓 Pong!",
            description=f"Latency: `{round(self.bot.latency * 1000)}ms`",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command("invite", description="Invite Riese Into Your server!")
    async def invite(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="Invite Reise",
            color=interaction.user.color,
            description="Here: https://rlyaa.xyz/riese",
        )
        await interaction.response.send_message(embed=embed)

    @slash_command("about", description="about reise")
    async def about(self, interaction: nextcord.Interaction):
        pass

    @about.subcommand("me", description="About Reise!")
    async def aboutme(self, interaction: nextcord.Interaction):
        await interaction.response.send_message(
            "Riese is like that friend who always brings the party! 🎉 This Discord bot is packed with fun features to make your server pop.  It's got moderation tools to keep things tidy, handy utility commands for everyday use, and even personalized welcome messages to greet new members with a smile. 😄 Built with Python and nextcord, Riese is one smart cookie with a playful attitude.  Add it to your server and let the good times roll! 🚀"
        )

    @slash_command("clear", description="Clear a specified number of messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, interaction: nextcord.Interaction, amount: int):
        if not interaction.user.guild_permissions.manage_messages:
            await interaction.response.send_message(
                "Permissions needed to use this command", ephemeral=True
            )
            return
        await interaction.response.send_message("Cleaning . . . ", ephemeral=True)

        if amount <= 0:
            await interaction.channel.send("Amount must be a positive number")
            return
        deleted = 0
        if amount >= 100:
            await interaction.channel.purge(limit=amount)
        else:
            async for message in interaction.channel.history(limit=amount):
                await message.delete()
                deleted += 1
        await interaction.channel.send(f"Cleared `{amount}` message(s) By {interaction.user.mention}.")
        print(f"Clear Log: {interaction.user}, {deleted}")
        
def setup(bot):
    bot.add_cog(Utility(bot))
