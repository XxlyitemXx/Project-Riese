import nextcord
from nextcord.ext import commands


class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("w")
    async def w(self, ctx, member: nextcord.Member = None):
        member = member or ctx.author

        joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")

        created_at = member.created_at.strftime("%Y-%m-%d %H:%M:%S")

        roles = [role.mention for role in member.roles[1:]] 
        roles_str = ", ".join(roles) if roles else "No roles"

        permissions = ", ".join(
            [perm[0] for perm in member.guild_permissions if perm[1]]
        )

        embed = nextcord.Embed(
            title=f"Member Information: {member.name}", color=member.color
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="Display Name", value=member.display_name, inline=False)
        embed.add_field(name="Profile", value=member.mention, inline=False)
        embed.add_field(name="Server Joined Date", value=joined_at, inline=False)
        embed.add_field(name="Register Date", value=created_at, inline=False)
        embed.add_field(name="Roles", value=roles_str, inline=False)
        embed.add_field(name="Permissions", value=permissions, inline=False)
        embed.add_field(name="User ID", value=member.id, inline=False)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(info(bot))
