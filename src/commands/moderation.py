import discord
from discord.ext import commands
from nextcord import Interaction, slash_command


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="ban", description="Bans a user from the server.")
    @commands.has_permissions(ban_members=True)
    async def ban(
        self, interaction: Interaction, member: discord.Member, *, reason: str = None
    ):
        """
        Bans a user from the server.

        Parameters
        ----------
        interaction: Interaction
            The interaction object.
        member: discord.Member
            The member to ban.
        reason: str, optional
            The reason for banning the member.
        """
        try:
            if reason:
                await member.send(
                    f"You have been banned from **{interaction.guild.name}** for: {reason}"
                )
            else:
                await member.send(
                    f"You have been banned from **{interaction.guild.name}**."
                )
        except discord.HTTPException:
            await interaction.response.send_message(
                f"Could not DM {member.mention} about the ban, but they have been banned from the server."
            )
        await member.ban(reason=reason)
        await interaction.response.send_message(f"{member.mention} has been banned.")

    @slash_command(name="unban", description="Unbans a user from the server.")
    @commands.has_permissions(ban_members=True)
    async def unban(
        self, interaction: Interaction, user_id: str, *, reason: str = None
        ):
        """
        Unbans a user from the server.
        Parameters
        ----------
        interaction: Interaction
            The interaction object.
        user_id: str
            The ID of the user to unban.
        reason: str, optional
            The reason for unbanning the user.
        """

        try:
            user = await self.bot.fetch_user(int(user_id))
            await interaction.guild.unban(user, reason=reason)
            await interaction.response.send_message(f"{user.mention} has been unbanned.")
        except ValueError:
            await interaction.response.send("Invalid user ID.")
        except discord.NotFound:
            await interaction.response.send("User not found.")
        except discord.HTTPException as e:
            await interaction.response.send(f"An error occurred: {e}")

    @slash_command(name="kick", description="Kicks a user from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick(
        self, interaction: Interaction, member: discord.Member, *, reason: str = None
    ):
        """
        Kicks a user from the server.

        Parameters
        ----------
        interaction: Interaction
            The interaction object.
        member: discord.Member
            The member to kick.
        reason: str, optional
            The reason for kicking the member.
        """
        try:
            if reason:
                await member.send(
                    f"You have been kicked from **{interaction.guild.name}** for: {reason}"
                )
            else:
                await member.send(
                    f"You have been kicked from **{interaction.guild.name}**."
                )
        except discord.HTTPException:
            await interaction.response.send(
                f"Could not DM {member.mention} about the ban, but they have been banned from the server."
            )
        await member.kick(reason=reason)
        await interaction.response.send_message(f"{member.mention} has been kicked.")


def setup(bot):
    bot.add_cog(Moderation(bot))
