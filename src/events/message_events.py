import sqlite3
from nextcord.ext import commands


class MessageEvents(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.last_sticky_message = (
            {}
        )  # Store the last sticky message ID for each channel

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return
        if not message.content.startswith("?afk"):
            await self._handle_afk_status(message)

        # Handle sticky messages
        await self._handle_sticky_message(message)

    async def _handle_afk_status(self, message):
        conn = sqlite3.connect("reise_main.db")
        cursor = conn.cursor()
        cursor.execute(
            "SELECT afk_message FROM afk_status WHERE user_id = ? AND server_id = ?",
            (message.author.id, message.guild.id),
        )
        result = cursor.fetchone()
        conn.close()

        if result:
            conn = sqlite3.connect("reise_main.db")
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM afk_status WHERE user_id=? AND server_id=?",
                (message.author.id, message.guild.id),
            )
            conn.commit()
            conn.close()
            await message.channel.send(
                f"Welcome back, {message.author.mention}! You are no longer AFK. :3"
            )

        for member in message.mentions:
            conn = sqlite3.connect("reise_main.db")
            cursor = conn.cursor()
            cursor.execute(
                "SELECT afk_message FROM afk_status WHERE user_id = ? AND server_id = ?",
                (member.id, message.guild.id),
            )
            result = cursor.fetchone()
            conn.close()
            if result:
                await message.channel.send(
                    f"{member.mention} is currently AFK: {result[0]}"
                )

    async def _handle_sticky_message(self, message):
        try:
            if message.channel.id in self.last_sticky_message:
                try:
                    old_message = await message.channel.fetch_message(
                        self.last_sticky_message[message.channel.id]
                    )
                    await old_message.delete()
                except:
                    pass

            conn = sqlite3.connect("reise_main.db")
            cursor = conn.cursor()
            cursor.execute(
                """
                SELECT sticky_message 
                FROM sticky_messages 
                WHERE guild_id = ? AND channel_id = ?
            """,
                (message.guild.id, message.channel.id),
            )
            result = cursor.fetchone()
            conn.close()

            if result:

                sticky_msg = await message.channel.send(f"Sticky message: {result[0]}")
                self.last_sticky_message[message.channel.id] = sticky_msg.id

        except sqlite3.Error as e:
            print(f"Database error: {e}")
        except Exception as e:
            print(f"Error handling sticky message: {e}")


def setup(bot):
    bot.add_cog(MessageEvents(bot))
