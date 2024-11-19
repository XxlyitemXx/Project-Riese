import sqlite3
import nextcord
import random
from nextcord.ext import commands


class OnJoinEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):
        conn = sqlite3.connect("reise_main.db")
        cursor = conn.cursor()
        cursor.execute("SELECT welcome_channel_id, welcome_message FROM welcome_settings WHERE guild_id = ?", (member.guild.id,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            return
        channel_id, message = result
        channel = self.bot.get_channel(channel_id)
        if not channel:
            return
        if "{random:" in message:
            options = message[message.find("{random:")+8:message.find("}")].split("~")
            message = random.choice(options).strip()

        # Replace variables
        message = message.replace("{mention}", member.mention)
        message = message.replace("{server}", member.guild.name)
        message = message.replace("{user(proper)}", str(member))
        message = message.replace("{server(members)}", str(member.guild.member_count))
        
        if "{ord:" in message:
            count = member.guild.member_count
            suffix = "th"
            if count % 10 == 1 and count % 100 != 11:
                suffix = "st"
            elif count % 10 == 2 and count % 100 != 12:
                suffix = "nd"
            elif count % 10 == 3 and count % 100 != 13:
                suffix = "rd"
            message = message.replace("{ord: {server(members)}}", f"{count:,}{suffix}")

        try:
            await channel.send(message)
        except nextcord.Forbidden:
            pass

def setup(bot):
    bot.add_cog(OnJoinEvents(bot))

