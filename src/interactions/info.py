import nextcord
from nextcord.ext import commands
import datetime


class info(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command("w")
    async def w(self, ctx, member: nextcord.Member = None):
        member = member or ctx.author

        joined_at = member.joined_at.strftime("%Y-%m-%d %H:%M:%S")
        created_at = member.created_at.strftime("%Y-%m-%d %H:%M:%S")

        # Calculate account age
        account_age = datetime.datetime.now() - member.created_at
        account_age_days = account_age.days
        
        # Calculate server membership duration
        server_time = datetime.datetime.now() - member.joined_at
        server_time_days = server_time.days

        roles = [role.mention for role in member.roles[1:]] 
        roles_str = ", ".join(roles) if roles else "No roles"

        permissions = ", ".join(
            [perm[0] for perm in member.guild_permissions if perm[1]]
        )

        # Determine status emoji
        status_emoji = "⚫"  # Default offline
        try:
            if member.status.online:
                status_emoji = "🟢"
            elif member.status.idle:
                status_emoji = "🟡"
            elif member.status.dnd:
                status_emoji = "🔴"
        except:
            pass

        # Determine if member is boosting
        boosting = "✨ Yes" if member.premium_since else "❌ No"

        embed = nextcord.Embed(
            title=f"{status_emoji} Member Information: {member.name}",
            description=f"Detailed information about {member.mention}",
            color=member.color,
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        
        # Basic Info Section
        embed.add_field(name="👤 Display Name", value=member.display_name, inline=True)
        embed.add_field(name="🆔 User ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="🤖 Bot", value="Yes" if member.bot else "No", inline=True)
        
        # Time Info Section
        embed.add_field(name="📅 Account Created", value=f"{created_at}\n({account_age_days} days ago)", inline=False)
        embed.add_field(name="📆 Server Joined", value=f"{joined_at}\n({server_time_days} days ago)", inline=False)
        
        # Server-specific Info
        embed.add_field(name="🚀 Server Booster", value=boosting, inline=True)
        embed.add_field(name="👑 Server Owner", value="Yes" if ctx.guild.owner_id == member.id else "No", inline=True)
        
        # Roles Section
        embed.add_field(name=f"🏷️ Roles [{len(roles)}]", value=roles_str, inline=False)
        
        # Permissions Section (only if not too long)
        if len(permissions) < 1024:  # Discord embed field value limit
            embed.add_field(name="🔑 Key Permissions", value=permissions, inline=False)

        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=ctx.author.avatar.url)
        embed.set_author(name=f"{ctx.guild.name}", icon_url=ctx.guild.icon.url if ctx.guild.icon else None)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(info(bot))
