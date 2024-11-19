import nextcord
from nextcord.ext import commands
import sqlite3

conn = sqlite3.connect("reise_main.db")
cursor = conn.cursor()
cursor.execute("CREATE TABLE IF NOT EXISTS welcome_settings (guild_id INTEGER PRIMARY KEY, welcome_channel_id INTEGER, welcome_message TEXT)")
conn.commit()
conn.close()


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="welcome", description="Welcome commands")
    async def welcome(self, interaction: nextcord.Interaction):
        pass

    @welcome.subcommand(name="setup", description="Setup the welcome system")
    async def setup(
        self,
        interaction: nextcord.Interaction,
        channel: nextcord.TextChannel = nextcord.SlashOption(description="The welcome channel"),
        message: str = nextcord.SlashOption(
            description="The welcome message. Use {mention}, {server}, {user(proper)}, {server(members)}"
        ),
    ):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                "You need `Manage Server` permissions to use this command.",
                ephemeral=True
            )

        conn = sqlite3.connect("reise_main.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO welcome_settings (guild_id, welcome_channel_id, welcome_message) VALUES (?, ?, ?)",
            (interaction.guild.id, channel.id, message)
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"Welcome channel set to {channel.mention} with message:\n{message}",
            ephemeral=True
        )

    @welcome.subcommand(name="disable", description="Disable the welcome system")
    async def disable(self, interaction: nextcord.Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            return await interaction.response.send_message(
                "You need `Manage Server` permissions to use this command.",
                ephemeral=True
            )

        conn = sqlite3.connect("reise_main.db")
        cursor = conn.cursor()
        cursor.execute(
            "DELETE FROM welcome_settings WHERE guild_id = ?",
            (interaction.guild.id,)
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            "Welcome system has been disabled.",
            ephemeral=True
        )



def setup(bot):
    bot.add_cog(Welcome(bot))
