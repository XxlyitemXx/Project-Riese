# commands/role_managements.py

import nextcord
from nextcord.ext import commands
import datetime


class role_managements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="role", description="Manage roles")
    async def role(self, interaction: nextcord.Interaction):
        pass

    @role.subcommand(name="add", description="Add a role to a user")
    @commands.has_permissions(manage_roles=True)
    async def role_add(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member,
        role: nextcord.Role,
    ):
        if role.position >= interaction.user.top_role.position:
            embed = nextcord.Embed(
                title="Error",
                description="You can't assign a role higher than or equal to your top role.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        if role in user.roles:
            embed = nextcord.Embed(
                title="Error",
                description=f"`{user}` already has the `{role}` role.",
                color=nextcord.Color.orange()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await user.add_roles(role)
        embed = nextcord.Embed(
            title="Role Added",
            description=f"Added {role.mention} to {user.mention}",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @role.subcommand(name="remove", description="Remove a role from a user")
    @commands.has_permissions(manage_roles=True)
    async def role_remove(
        self,
        interaction: nextcord.Interaction,
        user: nextcord.Member,
        role: nextcord.Role,
    ):
        if role.position >= interaction.user.top_role.position:
            embed = nextcord.Embed(
                title="Error",
                description="You can't remove a role higher than or equal to your top role.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await user.remove_roles(role)
        embed = nextcord.Embed(
            title="Role Removed",
            description=f"Removed {role.mention} from {user.mention}",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        await interaction.response.send_message(embed=embed)

    @role.subcommand(name="list", description="Show the roles of a user")
    async def role_list(
        self, interaction: nextcord.Interaction, user: nextcord.Member = None
    ):
        if user == None:
            user = interaction.user

        embed = nextcord.Embed(title=f"Roles for {user.display_name}", color=user.color)

        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        if roles:
            embed.add_field(name="Roles", value=", ".join(roles), inline=False)
        else:
            embed.description = "This user has no roles."
        await interaction.send(embed=embed)


def setup(bot):
    bot.add_cog(role_managements(bot))
