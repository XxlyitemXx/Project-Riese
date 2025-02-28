import nextcord
from nextcord.ext import commands
import sqlite3
import datetime

def create_afk_table():
    conn = sqlite3.connect("reise_main.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS afk_status (
            user_id INTEGER PRIMARY KEY,
            server_id INTEGER,
            afk_message TEXT,
            timestamp TEXT
        )
    """
    )
    conn.commit()
    conn.close()

create_afk_table()

class afk(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="afk", description="Sets your AFK status")
    async def afk(self, ctx, *, message: str = None): 
        user_id = ctx.author.id
        server_id = ctx.guild.id
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect("reise_main.db")
        cursor = conn.cursor()

        # Get a random AFK emoji
        afk_emojis = ["💤", "😴", "🛌", "🌙", "⏰", "⌛", "🔕"]
        import random
        afk_emoji = random.choice(afk_emojis)
        
        # Create embed
        embed = nextcord.Embed(
            title=f"{afk_emoji} AFK Status Set",
            color=ctx.author.color or nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url=ctx.author.display_avatar.url)
        
        if message:
            cursor.execute(
                "INSERT OR REPLACE INTO afk_status (user_id, server_id, afk_message, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, server_id, message, timestamp),
            )
            conn.commit()
            
            embed.description = f"{ctx.author.mention} is now AFK"
            embed.add_field(name="📝 Message", value=f"```{message}```", inline=False)
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO afk_status (user_id, server_id, afk_message, timestamp) VALUES (?, ?, ?, ?)",
                (user_id, server_id, "No reason provided.", timestamp),
            )
            conn.commit()
            
            embed.description = f"{ctx.author.mention} is now AFK"
            embed.add_field(name="📝 Message", value="```No reason provided.```", inline=False)
            
        embed.set_footer(text="I'll notify others when they mention you", icon_url=ctx.author.display_avatar.url)
        
        # Try to change nickname to show AFK status
        try:
            current_name = ctx.author.display_name
            if not current_name.startswith("[AFK]"):
                await ctx.author.edit(nick=f"[AFK] {current_name}"[:32])  # Discord nickname limit is 32 chars
                embed.add_field(name="👤 Nickname", value="Updated to show AFK status", inline=False)
        except:
            # If bot doesn't have permission to change nickname, just continue
            pass
            
        await ctx.send(embed=embed)
        conn.close()

def setup(bot):
    bot.add_cog(afk(bot))