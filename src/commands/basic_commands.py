import nextcord
from nextcord.ext import commands
from nextcord import slash_command
from assets.utils.config_loader import load_config
config = load_config()

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="help", description="Show available commands")
    async def help(self, interaction: nextcord.Interaction):
        embed = await self._create_help_embed(interaction.user, interaction.guild)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        
    @commands.command(name="help", description="Show available commands")
    async def help_prefix(self, ctx):
        """Show available commands"""
        embed = await self._create_help_embed(ctx.author, ctx.guild)
        await ctx.send(embed=embed)
        
    async def _create_help_embed(self, user, guild):
        """Create the help embed with all commands"""
        embed = nextcord.Embed(
            title="✨ Available Commands ✨", 
            description="Here's everything you can do with Reise!", 
            color=nextcord.Color.blue()
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {user}", icon_url=user.avatar.url)

        # Basic Commands
        basic_commands = {
            "/ping": "🏓 Checks the bot's latency.",
            "/say [message]": "📢 Makes the bot say something.",
            "/invite": "🔗 Get the bot's invite link.",
            "/about me": "ℹ️ Information about the bot.",
            "/avatar [user]": "🖼️ Get a user's avatar.",
            "/count member": "👥 View server member count.",
            "/afk [message]": "💤 Set your AFK status.",
            "?afk [message]": "💤 Alternative command for setting AFK status.",
            "?w [member]": "👤 Show detailed member information.",
            "?sy [text]": "📝 Summarize text with options.",
            "?ask [question]": "🤖 Ask a question to the AI.",
            "?help": "📚 Show this help message."
        }
        embed.add_field(
            name="🧰 Basic Commands",
            value="\n".join(f"`{command}`: {description}" for command, description in basic_commands.items()),
            inline=False
        )

        # Moderation Commands
        moderation_commands = {
            "/ban [user] [reason]": "🔨 Ban a user.",
            "/unban [user_id] [reason]": "🔓 Unban a user.",
            "/kick [user] [reason]": "👢 Kick a user.",
            "/warn add [user] [reason]": "⚠️ Warn a user.",
            "/warn remove [user]": "✅ Remove warning from a user.",
            "/warn list": "📋 Show list of warned users.",
            "/clear [amount]": "🧹 Clear specified number of messages.",
            "?clear [amount]": "🧹 Alternative command for clearing messages."
        }
        embed.add_field(
            name="🛡️ Moderation Commands",
            value="\n".join(f"`{command}`: {description}" for command, description in moderation_commands.items()),
            inline=False
        )

        # Role Management
        role_commands = {
            "/role add [user] [role]": "➕ Add role to user.",
            "/role remove [user] [role]": "➖ Remove role from user.",
            "/role list [user]": "📋 Show user's roles."
        }
        embed.add_field(
            name="🏷️ Role Management",
            value="\n".join(f"`{command}`: {description}" for command, description in role_commands.items()),
            inline=False
        )

        # Group Chat Commands
        gc_commands = {
            "/gc setup [gc-name]": "🔧 Create new group chat.",
            "?gc setup [gc-name]": "🔧 Alternative command for creating group chat.",
            "/gc add [gc-name] [member]": "➕ Add member to group chat.",
            "/gc remove [gc-name] [member]": "➖ Remove member from group chat.",
            "/gc delete [gc-name]": "🗑️ Delete group chat.",
            "/gc rename [gc-name] [new-name]": "✏️ Rename group chat.",
            "/gc admin [gc-name] [member]": "👑 Give admin permissions.",
            "/gc leave [gc-name]": "👋 Leave a group chat.",
            "/gc toggle": "🔄 Toggle group chat creation for server."
        }
        embed.add_field(
            name="💬 Group Chat Commands",
            value="\n".join(f"`{command}`: {description}" for command, description in gc_commands.items()),
            inline=False
        )

        # Welcome System
        welcome_commands = {
            "/welcome setup [channel] [message]": "🎉 Setup welcome channel and message.",
            "/welcome disable": "🚫 Disable welcome system."
        }
        embed.add_field(
            name="👋 Welcome System",
            value="\n".join(f"`{command}`: {description}" for command, description in welcome_commands.items()),
            inline=False
        )

        # Sticky Messages
        sticky_commands = {
            "/sticky set [message]": "📌 Set a sticky message.",
            "/sticky remove": "🗑️ Remove sticky message.",
            "/sticky list": "📋 List all sticky messages."
        }
        embed.add_field(
            name="📌 Sticky Messages",
            value="\n".join(f"`{command}`: {description}" for command, description in sticky_commands.items()),
            inline=False
        )
        
        # Trigger System
        trigger_commands = {
            "/trigger dashboard": "🎛️ Manage trigger words dashboard.",
            "/trigger add": "➕ Add new trigger words.",
            "/trigger list": "📋 List all trigger words.",
            "/trigger manage [word]": "⚙️ Manage specific trigger word."
        }
        embed.add_field(
            name="🔄 Trigger System",
            value="\n".join(f"`{command}`: {description}" for command, description in trigger_commands.items()),
            inline=False
        )
        
        # Admin Commands (only shown to bot owner)
        try:
            owner = config.get('owner_id')
            if user.id == owner:
                admin_commands = {
                    "/admin extension load [name]": "🔌 Load a bot extension.",
                    "/admin extension unload [name]": "🔌 Unload a bot extension.",
                    "/admin extension reload [name]": "🔄 Reload a bot extension.",
                    "/admin extension list": "📋 List all extensions.",
                    "/admin update": "🔄 Update bot from GitHub.",
                    "/admin restart": "🔄 Restart the bot.",
                    "/admin owner [id]": "👑 Set bot owner ID.",
                    "/admin check_owner": "👑 Check current owner settings.",
                    "/admin dashboard": "🎛️ Open admin dashboard."
                }
                embed.add_field(
                    name="🛠️ Admin Commands (Owner Only)",
                    value="\n".join(f"`{command}`: {description}" for command, description in admin_commands.items()),
                    inline=False
                )
        except:
            pass 
        
        return embed

    @slash_command("avatar", description="show avatar of a user")
    async def avatar(self, interaction: nextcord.Interaction, user: nextcord.Member = None):
        user = user or interaction.user
        embed = nextcord.Embed(
            title=f"🖼️ {user.name}'s Avatar", 
            color=user.color
        )
        embed.set_image(url=user.avatar.url)
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @slash_command("count", description="count something")
    async def count(self, interaction: nextcord.Interaction):
        pass

    @count.subcommand("member", description="count member in the server!")
    async def member(self, interaction: nextcord.Interaction):
        count_member = interaction.guild.member_count
        
        # Determine emoji based on member count
        if count_member < 50:
            size_emoji = "🏠"  # Small server
            size_text = "Cozy community"
        elif count_member < 500:
            size_emoji = "🏢"  # Medium server
            size_text = "Growing community"
        else:
            size_emoji = "🏙️"  # Large server
            size_text = "Thriving community"
            
        embed = nextcord.Embed(
            title=f"{size_emoji} Member Count",
            description=f"**{count_member}** members in this server!",
            color=interaction.user.accent_color or nextcord.Color.blue()
        )
        
        embed.add_field(name="👥 Server Size", value=size_text, inline=False)
        
        # Initialize counters
        online = 0
        idle = 0
        dnd = 0
        offline = 0
        
        # Add debug info
        debug_info = []
        
        # Try to count statuses directly
        try:
            # Debug the member object to see if status is accessible
            if interaction.guild.members:
                sample_member = next(iter(interaction.guild.members))
                debug_info.append(f"Sample member status type: {type(sample_member.status)}")
                debug_info.append(f"Sample member status value: {sample_member.status}")
            
            # Count statuses
            for member in interaction.guild.members:
                status_value = str(member.status)
                if status_value == "online":
                    online += 1
                elif status_value == "idle":
                    idle += 1
                elif status_value == "dnd":
                    dnd += 1
                elif status_value == "offline":
                    offline += 1
                else:
                    debug_info.append(f"Unknown status: {status_value}")
            
            debug_info.append(f"Count results: online={online}, idle={idle}, dnd={dnd}, offline={offline}")
            
            status_info = f"🟢 Online: {online}\n🟡 Idle: {idle}\n🔴 DND: {dnd}\n⚫ Offline: {offline}"
            embed.add_field(name="📊 Status Breakdown", value=status_info, inline=False)
            
            # If counts are suspiciously low, flag it
            if online + idle + dnd < 3 and count_member > 10:
                embed.add_field(
                    name="⚠️ Status Issue Detected", 
                    value="The count seems unusually low. This may indicate that presence data isn't fully available.",
                    inline=False
                )
                
        except Exception as e:
            # If status counting fails, show debug info
            embed.add_field(
                name="⚠️ Status Counting Failed",
                value=f"Error: {str(e)}",
                inline=False
            )
        
        # Always add the debug info in a collapsed field
        if debug_info:
            embed.add_field(
                name="🔍 Debug Information",
                value="```\n" + "\n".join(debug_info) + "\n```",
                inline=False
            )
            
        if interaction.guild.icon:
            embed.set_thumbnail(url=interaction.guild.icon.url)
        
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(BasicCommands(bot))