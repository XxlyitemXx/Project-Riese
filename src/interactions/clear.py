import nextcord
from nextcord.ext import commands

class clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    @commands.command(name="clear", description="Clear a specified number of messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("Permissions needed to use this command") 
            return

        if amount <= 0:
            await ctx.send("Amount must be a positive number")
            return

        deleted = 0
        if amount >= 100:
            await ctx.channel.purge(limit=amount) 
        else:
            async for message in ctx.channel.history(limit=amount):
                await message.delete()
                deleted += 1

        await ctx.send(f"Cleared `{deleted}` message(s). by {ctx.author.mention}")

def setup(bot):
    bot.add_cog(clear(bot))