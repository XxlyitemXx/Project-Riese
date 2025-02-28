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
        embed.set_footer(text=f"💬 Message by {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.set_author(name="📢 Announcement", icon_url=self.bot.user.avatar.url)
        await interaction.response.send_message("✅ Message sent!", ephemeral=True)
        await interaction.channel.send(embed=embed)

    @nextcord.slash_command(name="ping", description="Checks bot latency")
    async def ping(self, interaction: nextcord.Interaction):
        latency = round(self.bot.latency * 1000)
        if latency < 100:
            color = nextcord.Color.green()
            status = "Excellent"
            emoji = "⚡"
        elif latency < 200:
            color = nextcord.Color.gold()
            status = "Good"
            emoji = "✅"
        else:
            color = nextcord.Color.red()
            status = "Poor"
            emoji = "⚠️"
            
        embed = nextcord.Embed(
            title=f"🏓 Pong! {emoji}",
            description=f"**Latency:** `{latency}ms`\n**Status:** {status}",
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command("invite", description="Invite Riese Into Your server!")
    async def invite(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="🤖 Invite Reise",
            color=nextcord.Color.blue(),
            description="**Add me to your server!**\n\n🔗 [Click here to invite](https://rlyaa.xyz/riese)",
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @slash_command("about", description="about reise")
    async def about(self, interaction: nextcord.Interaction):
        pass

    @about.subcommand("me", description="About Reise!")
    async def aboutme(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="✨ About Reise ✨",
            color=nextcord.Color.purple(),
            description="Riese is like that friend who always brings the party! 🎉 This Discord bot is packed with fun features to make your server pop.\n\n🛡️ **Moderation tools** to keep things tidy\n🔧 **Utility commands** for everyday use\n👋 **Personalized welcome messages** to greet new members\n🤖 **AI capabilities** for smart interactions\n\nBuilt with Python and nextcord, Riese is one smart cookie with a playful attitude. Add it to your server and let the good times roll! 🚀"
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.add_field(name="🔗 Links", value="[Website](https://rlyaa.xyz) | [Invite Bot](https://rlyaa.xyz/riese)", inline=False)
        await interaction.response.send_message(embed=embed)

    @slash_command("clear", description="Clear a specified number of messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, interaction: nextcord.Interaction, amount: int):
        if not interaction.user.guild_permissions.manage_messages:
            error_embed = nextcord.Embed(
                title="❌ Permission Error",
                description="You don't have permission to manage messages!",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
            
        await interaction.response.send_message("🧹 Cleaning messages...", ephemeral=True)

        if amount <= 0:
            error_embed = nextcord.Embed(
                title="❌ Invalid Amount",
                description="Amount must be a positive number",
                color=nextcord.Color.red()
            )
            await interaction.channel.send(embed=error_embed)
            return
            
        deleted = 0
        if amount >= 100:
            await interaction.channel.purge(limit=amount)
        else:
            async for message in interaction.channel.history(limit=amount):
                await message.delete()
                deleted += 1
                
        success_embed = nextcord.Embed(
            title="🧹 Channel Cleaned",
            description=f"Successfully cleared `{amount}` message(s)",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        success_embed.add_field(name="👮 Moderator", value=interaction.user.mention)
        success_embed.set_footer(text="Messages deleted", icon_url=interaction.user.avatar.url)
        
        await interaction.channel.send(embed=success_embed)
        print(f"Clear Log: {interaction.user}, {deleted}")
        
def setup(bot):
    bot.add_cog(Utility(bot))
