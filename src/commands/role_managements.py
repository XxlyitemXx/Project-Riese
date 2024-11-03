# commands/role_managements.py

import nextcord
from nextcord.ext import commands

class role_managements(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="role_add", description="add role to user")
    @commands.has_permissions(manage_roles=True)
    async def role_add(self, interaction: nextcord.Interaction, user: nextcord.Member, role: nextcord.Role):  
        if role.position >= interaction.user.top_role.position:
            await interaction.response.send_message(
                f"You can't assign a role higher than or equal to your top role. ",
                ephemeral=True,
            )
            return
        if role in user.roles:
            await interaction.response.send_message(
                f"`{user}` already has the `{role}` role.", ephemeral=True
            )
            return
        await user.add_roles(role)
        await interaction.response.send_message(f"Added {role} to {user}!")

    @nextcord.slash_command(name="role_remove", description="remove role from a user")
    @commands.has_permissions(manage_roles=True)
    async def role_remove(self, interaction: nextcord.Interaction, user: nextcord.Member, role: nextcord.Role): 
        if role.position >= interaction.user.top_role.position:
            await interaction.response.send_message(
                f"you can't remove a role higher than or equal to your top role.", ephemeral=True
            )
            return 
        if role in user.roles:  
            await interaction.response.send_message(
                f"'{user}' already has the '{role}' role.", ephemeral=True
            )
            return  
        await user.remove_roles(role)  
        await interaction.response.send_message(f"Removed {role} from {user}")

    @nextcord.slash_command(name="role_list", description="show the role of a user")
    async def role_list(self, interaction: nextcord.Interaction, user: nextcord.Member = None):  
        if user == None:
            user = interaction.user

        embed = nextcord.Embed(
            title=f"Roles for {user.display_name}",
            color=user.color
        )

        roles = [role.mention for role in user.roles if role.name != "@everyone"]
        if roles:
            embed.add_field(name="Roles", value=", ".join(roles), inline=False)
        else:
            embed.description = "This user has no roles."
        await interaction.send(embed=embed)  

def setup(bot):
    bot.add_cog(role_managements(bot))