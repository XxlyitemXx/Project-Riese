import nextcord
from nextcord.ext import commands
from nextcord import slash_command


class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="help", description="Show available commands")
    async def help(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Available Commands", color=nextcord.Color.blue())

        # Basic Commands
        basic_commands = {
            "/ping": "Checks the bot's latency.",
            "/say [message]": "Makes the bot say something.",
            "/invite": "Get the bot's invite link.",
            "/about": "Information about the bot.",
            "/avatar [user]": "Get a user's avatar.",
            "/count member": "View server member count.",
            "/afk [message]": "Set your AFK status.",
            "?afk [message]": "Alternative command for setting AFK status.",
            "?w [member]": "Show detailed member information.",
            "?sy [text]": "Summarize text with options.",
            "?ask [question]": "Ask a question to the AI."
        }
        embed.add_field(
            name="Basic Commands",
            value="\n".join(f"`{command}`: {description}" for command, description in basic_commands.items()),
            inline=False
        )

        # Moderation Commands
        moderation_commands = {
            "/ban [user] [reason]": "Ban a user.",
            "/unban [user_id] [reason]": "Unban a user.",
            "/kick [user] [reason]": "Kick a user.",
            "/warn add [user] [reason]": "Warn a user.",
            "/warn remove [user]": "Remove warning from a user.",
            "/warn list": "Show list of warned users.",
            "/clear [amount]": "Clear specified number of messages.",
            "?clear [amount]": "Alternative command for clearing messages."
        }
        embed.add_field(
            name="Moderation Commands",
            value="\n".join(f"`{command}`: {description}" for command, description in moderation_commands.items()),
            inline=False
        )

        # Role Management
        role_commands = {
            "/role add [user] [role]": "Add role to user.",
            "/role remove [user] [role]": "Remove role from user.",
            "/role list [user]": "Show user's roles."
        }
        embed.add_field(
            name="Role Management",
            value="\n".join(f"`{command}`: {description}" for command, description in role_commands.items()),
            inline=False
        )

        # Group Chat Commands
        gc_commands = {
            "/gc setup [gc-name]": "Create new group chat.",
            "?gc setup [gc-name]": "Alternative command for creating group chat.",
            "/gc add [gc-name] [member]": "Add member to group chat.",
            "/gc remove [gc-name] [member]": "Remove member from group chat.",
            "/gc delete [gc-name]": "Delete group chat.",
            "/gc rename [gc-name] [new-name]": "Rename group chat.",
            "/gc admin [gc-name] [member]": "Give admin permissions.",
            "/gc leave [gc-name]": "Leave a group chat.",
            "/gc toggle": "Toggle group chat creation for server."
        }
        embed.add_field(
            name="Group Chat Commands",
            value="\n".join(f"`{command}`: {description}" for command, description in gc_commands.items()),
            inline=False
        )

        # Welcome System
        welcome_commands = {
            "/welcome setup [channel] [message]": "Setup welcome channel and message.",
            "/welcome disable": "Disable welcome system."
        }
        embed.add_field(
            name="Welcome System",
            value="\n".join(f"`{command}`: {description}" for command, description in welcome_commands.items()),
            inline=False
        )

        # Sticky Messages
        sticky_commands = {
            "/sticky set [message]": "Set a sticky message.",
            "/sticky remove": "Remove sticky message.",
            "/sticky list": "List all sticky messages."
        }
        embed.add_field(
            name="Sticky Messages",
            value="\n".join(f"`{command}`: {description}" for command, description in sticky_commands.items()),
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @slash_command("avatar", description="show avatar of a user")
    async def avatar(self, interaction: nextcord.Interaction, user: nextcord.Member):
        user = user or interaction.user
        embed = nextcord.Embed(title=f"{user.name}'s Avatar", color=user.color)
        embed.set_image(url=user.avatar.url)
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @slash_command("count", description="count something")
    async def count(self, interaction: nextcord.Interaction):
        pass

    @count.subcommand("member", description="count member in the server!")
    async def member(self, interaction: nextcord.Interaction):
        count_member = interaction.guild.member_count
        embed = nextcord.Embed(
            title="Member Count",
            description=f"This server has {count_member} members.",
            color=interaction.user.accent_color
        )
        embed.set_thumbnail(interaction.guild.icon)
        await interaction.response.send_message(embed=embed)


def setup(bot):
    bot.add_cog(BasicCommands(bot))