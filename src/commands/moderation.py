import nextcord
from nextcord.ext import commands
from nextcord import Interaction, slash_command
import datetime


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="ban", description="Bans a user from the server.")
    @commands.has_permissions(ban_members=True)
    async def ban(
        self, interaction: Interaction, member: nextcord.Member, *, reason: str = None
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
            embed = nextcord.Embed(
                title="User Banned",
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Banned User", value=member.mention, inline=True)
            embed.add_field(name="Banned By", value=interaction.user.mention, inline=True)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
                await member.send(f"You have been banned from **{interaction.guild.name}** for: {reason}")
            else:
                embed.add_field(name="Reason", value="No reason provided", inline=False)
                await member.send(f"You have been banned from **{interaction.guild.name}**.")
            embed.set_image(url = "")
            await member.ban(reason=reason)
            await interaction.response.send_message(embed=embed)
        except nextcord.HTTPException:
            error_embed = nextcord.Embed(
                title="Error",
                description=f"Could not DM {member.mention} about the ban, but they have been banned from the server.",
                color=nextcord.Color.orange()
            )
            await interaction.response.send_message(embed=error_embed)

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
            
            embed = nextcord.Embed(
                title="User Unbanned",
                color=nextcord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Unbanned User", value=user.mention, inline=True)
            embed.add_field(name="Unbanned By", value=interaction.user.mention, inline=True)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
            
            await interaction.response.send_message(embed=embed)
        except ValueError:
            error_embed = nextcord.Embed(
                title="Error",
                description="Invalid user ID.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed)
        except nextcord.NotFound:
            error_embed = nextcord.Embed(
                title="Error",
                description="User not found.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed)
        except nextcord.HTTPException as e:
            error_embed = nextcord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed)

    @slash_command(name="kick", description="Kicks a user from the server.")
    @commands.has_permissions(kick_members=True)
    async def kick(
        self, interaction: Interaction, member: nextcord.Member, *, reason: str = None
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
            embed = nextcord.Embed(
                title="User Kicked",
                color=nextcord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Kicked User", value=member.mention, inline=True)
            embed.add_field(name="Kicked By", value=interaction.user.mention, inline=True)
            if reason:
                embed.add_field(name="Reason", value=reason, inline=False)
                await member.send(f"You have been kicked from **{interaction.guild.name}** for: {reason}")
            else:
                embed.add_field(name="Reason", value="No reason provided", inline=False)
                await member.send(f"You have been kicked from **{interaction.guild.name}**.")
            
            await member.kick(reason=reason)
            await interaction.response.send_message(embed=embed)
        except nextcord.HTTPException:
            error_embed = nextcord.Embed(
                title="Error",
                description=f"Could not DM {member.mention} about the kick, but they have been kicked from the server.",
                color=nextcord.Color.orange()
            )
            await interaction.response.send_message(embed=error_embed)


def setup(bot):
    bot.add_cog(Moderation(bot))
