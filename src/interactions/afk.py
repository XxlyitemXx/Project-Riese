import nextcord
from nextcord.ext import commands
import sqlite3

def create_afk_table():
    conn = sqlite3.connect("reise_main.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS afk_status (
            user_id INTEGER PRIMARY KEY,
            server_id INTEGER,
            afk_message TEXT
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
        conn = sqlite3.connect("reise_main.db")
        cursor = conn.cursor()

        if message:
            cursor.execute(
                "INSERT OR REPLACE INTO afk_status (user_id, server_id, afk_message) VALUES (?, ?, ?)",
                (user_id, server_id, message),
            )
            conn.commit()
            await ctx.send(f"You are now AFK: `{message}` :3")  # Use ctx.send
        else:
            cursor.execute(
                "INSERT OR REPLACE INTO afk_status (user_id, server_id, afk_message) VALUES (?, ?, ?)",
                (user_id, server_id, "No reason provided."),
            )
            conn.commit()
            await ctx.send(f"You are now AFK: `No reason provided.` :3")  # Use ctx.send
        conn.close()

def setup(bot):
    bot.add_cog(afk(bot))