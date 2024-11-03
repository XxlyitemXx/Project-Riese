import nextcord
from nextcord.ext import commands
from nextcord import SlashOption

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


class AFK(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="afk", description="Sets your AFK status")
    async def afk(
        self,
        interaction: nextcord.Interaction,
        message: str = SlashOption(description="Your AFK message", required=False),
    ):
        user_id = interaction.user.id
        server_id = interaction.guild.id
        conn = sqlite3.connect("reise_main.db")
        cursor = conn.cursor()

        if message:
            cursor.execute(
                "INSERT OR REPLACE INTO afk_status (user_id, server_id, afk_message) VALUES (?, ?, ?)",
                (user_id, server_id, message),
            )
            conn.commit()
            await interaction.response.send_message(f"You are now AFK: `{message}` :3")
        else:  # This handles both None and empty string cases
            cursor.execute(
                "INSERT OR REPLACE INTO afk_status (user_id, server_id, afk_message) VALUES (?, ?, ?)",
                (user_id, server_id, "No reason provided."),
            )
            conn.commit()
            await interaction.response.send_message(
                f"You are now AFK: `No reason provided.` :3"
            )
        conn.close()


def setup(bot):
    bot.add_cog(AFK(bot))
