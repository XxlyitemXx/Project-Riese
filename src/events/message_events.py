
import sqlite3
from nextcord.ext import commands


class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        conn = sqlite3.connect('reise_main.db')
        cursor = conn.cursor()
        cursor.execute("SELECT afk_message FROM afk_status WHERE user_id = ? AND server_id = ?", (message.author.id, message.guild.id))
        result = cursor.fetchone()
        conn.close()

        if result:
            # Remove the user from the AFK status
            conn = sqlite3.connect('reise_main.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM afk_status WHERE user_id=? AND server_id=?", (message.author.id, message.guild.id))
            conn.commit()
            conn.close()
            await message.channel.send(f"Welcome back, {message.author.mention}! You are no longer AFK. :3")

        # Check if someone mentioned an AFK user
        for member in message.mentions:
            conn = sqlite3.connect('reise_main.db')
            cursor = conn.cursor()
            cursor.execute("SELECT afk_message FROM afk_status WHERE user_id = ? AND server_id = ?", (member.id, message.guild.id))
            result = cursor.fetchone()
            conn.close()
            if result:
                await message.channel.send(f"{member.mention} is currently AFK: {result[0]}")


def setup(bot):
    bot.add_cog(MessageEvents(bot))