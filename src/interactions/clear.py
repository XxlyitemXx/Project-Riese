import nextcord
from nextcord.ext import commands
import datetime

class clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(name="clear", description="Clear a specified number of messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if not ctx.author.guild_permissions.manage_messages:
            error_embed = nextcord.Embed(
                title="❌ Permission Error",
                description="You don't have permission to manage messages!",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed)
            return

        if amount <= 0:
            error_embed = nextcord.Embed(
                title="❌ Invalid Amount",
                description="Amount must be a positive number",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed)
            return

        # Send initial message
        processing_embed = nextcord.Embed(
            title="🧹 Cleaning Messages...",
            description=f"Attempting to delete {amount} messages",
            color=nextcord.Color.gold()
        )
        processing_msg = await ctx.send(embed=processing_embed)

        # Delete messages
        deleted = 0
        try:
            if amount >= 100:
                await ctx.channel.purge(limit=amount)
                deleted = amount
            else:
                async for message in ctx.channel.history(limit=amount):
                    await message.delete()
                    deleted += 1
                    
            # Delete the processing message
            await processing_msg.delete()
            
            # Send success message
            success_embed = nextcord.Embed(
                title="✨ Channel Cleaned",
                description=f"Successfully cleared `{deleted}` message(s)",
                color=nextcord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            success_embed.add_field(name="👮 Moderator", value=ctx.author.mention, inline=True)
            success_embed.add_field(name="📊 Amount", value=f"`{deleted}` messages", inline=True)
            success_embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
            
            await ctx.send(embed=success_embed, delete_after=10)  # Auto-delete after 10 seconds
            
        except Exception as e:
            error_embed = nextcord.Embed(
                title="⚠️ Error",
                description=f"An error occurred while clearing messages: ```{str(e)}```",
                color=nextcord.Color.red()
            )
            await ctx.send(embed=error_embed)

def setup(bot):
    bot.add_cog(clear(bot))