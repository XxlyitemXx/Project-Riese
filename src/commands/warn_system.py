import nextcord
from nextcord.ext import commands
import sqlite3
import datetime

class WarnCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.conn = sqlite3.connect('reise_main.db')
        self.create_table()

    def create_table(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS warns (
                guild_id INTEGER,
                user_id INTEGER,
                warn_count INTEGER,
                PRIMARY KEY (guild_id, user_id)
            )
        ''')
        self.conn.commit()

    @nextcord.slash_command(name="warn", description="Warn commands") 
    async def warn(self, interaction: nextcord.Interaction):
        pass 


    @warn.subcommand(name="add", description="Warn a user.")
    @commands.has_permissions(kick_members=True)
    async def warn_add(self, interaction: nextcord.Interaction, member: nextcord.Member, reason: str = None):
        """
        Warns a user.

        Parameters
        ----------
        member: The member to warn.
        reason: The reason for the warning.
        """

        guild_id = interaction.guild.id
        user_id = member.id

        cursor = self.conn.cursor()
        cursor.execute("SELECT warn_count FROM warns WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        row = cursor.fetchone()

        if row is None:
            warn_count = 1
        else:
            warn_count = row[0] + 1

        cursor.execute(
            "INSERT OR REPLACE INTO warns (guild_id, user_id, warn_count) VALUES (?, ?, ?)",
            (guild_id, user_id, warn_count),
        )
        self.conn.commit()

        await interaction.response.send_message(f"{member.mention} has been warned. They now have {warn_count} warning(s). Reason: {reason}")

        await self.apply_punishment(interaction, member, warn_count)

    async def apply_punishment(self, interaction: nextcord.Interaction, member: nextcord.Member, warn_count: int):
        if warn_count == 2:
            await member.timeout(datetime.timedelta(minutes=30), reason="Reached 2 warnings")
            await interaction.channel.send(f"{member.mention} has been timed out for 30 minutes due to reaching 2 warnings.")
        elif warn_count == 4:
            await member.timeout(datetime.timedelta(hours=6), reason="Reached 4 warnings")
            await interaction.channel.send(f"{member.mention} has been timed out for 6 hours due to reaching 4 warnings.")
        elif warn_count == 5:
            await member.timeout(datetime.timedelta(hours=24), reason="Reached 5 warnings")
            await interaction.channel.send(f"{member.mention} has been timed out for 24 hours due to reaching 5 warnings.")
        elif warn_count >= 6:
            await member.kick(reason="Reached 6 warnings")
            await interaction.channel.send(f"{member.mention} has been kicked from the server due to reaching 6 warnings.")

            guild_id = interaction.guild.id
            user_id = member.id
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM warns WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
            self.conn.commit()

    @warn.subcommand(name="remove", description="Remove a warning from a user.")
    @commands.has_permissions(kick_members=True)
    async def warn_remove(self, interaction: nextcord.Interaction, member: nextcord.Member):
        """
        Removes a warning from a user.

        Parameters
        ----------
        member: The member to remove a warning from.
        """

        guild_id = interaction.guild.id
        user_id = member.id

        cursor = self.conn.cursor()
        cursor.execute("SELECT warn_count FROM warns WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        row = cursor.fetchone()

        if row is None:
            await interaction.response.send_message(f"{member.mention} has no warnings.", ephemeral=True)
            return

        warn_count = row[0] - 1
        if warn_count == 0:
            cursor.execute("DELETE FROM warns WHERE guild_id = ? AND user_id = ?", (guild_id, user_id))
        else:
            cursor.execute(
                "UPDATE warns SET warn_count = ? WHERE guild_id = ? AND user_id = ?",
                (warn_count, guild_id, user_id),
            )
        self.conn.commit()

        await interaction.response.send_message(f"Removed a warning from {member.mention}. They now have {warn_count} warning(s).", ephemeral=True)

    @warn.subcommand(name="list", description="Show the list of warned users.")
    @commands.has_permissions(kick_members=True)
    async def warn_list(self, interaction: nextcord.Interaction):
        """
        Shows the list of warned users with their warning count.
        """

        guild_id = interaction.guild.id
        cursor = self.conn.cursor()
        cursor.execute("SELECT user_id, warn_count FROM warns WHERE guild_id = ?", (guild_id,))
        rows = cursor.fetchall()

        if not rows:
            await interaction.response.send_message("There are no warned users in this server.", ephemeral=True)
            return

        warn_list = ""
        for row in rows:
            user_id, warn_count = row
            user = interaction.guild.get_member(user_id)
            if user:
                warn_list += f"{user.mention}: {warn_count} warnings\n"

        await interaction.response.send_message(f"**Warned Users:**\n{warn_list}", ephemeral=True)

def setup(bot):
    bot.add_cog(WarnCog(bot))