import nextcord
from nextcord.ext import commands

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @nextcord.slash_command(name="help", description="Show available commands")
    async def help(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(title="Available Commands", color=nextcord.Color.blue())

        basic_commands = {
            "/ping": "Checks the bot's latency.",
            "/say [content]": "Makes the bot say something.",
            "/invite": "Get the bot's invite link.",
            "/about": "Information about the bot.",
            "/partner": "See our partner servers.", 
            "/avatar [user]": "Get a user's avatar.",
            "/count_messages": "See the server's message count.",
            "/count_member": "View the member count of the server.",
            "/afk [message]": "Set your AFK status."
        }
        embed.add_field(name="Basic Commands", value="\n".join(f"`{command}`: {description}" for command, description in basic_commands.items()), inline=False)

        admin_commands = {
            "/role_add [user] [role]": "Add a role to a user.",
            "/summon [user] [message]": "(Admin) DM a user and mention them.",
            "/kick [user] [reason]": "Kick a user.",
            "/ban [user] [reason]": "Ban a user.",
            "/clear [amount]": "Clear messages.",
            "/unban [user_id]": "Unban a user.",
            "/role_remove [user] [role]": "Remove a role from a user.",
            "/nickname [user] [nickname]": "Change a user's nickname.",

        }
        if admin_commands: 
            embed.add_field(name="Admin Commands", value="\n".join(f"`{command}`: {description}" for command, description in admin_commands.items()), inline=False)


        anti_raid_commands = {
            "/anti_raid": "Toggle anti-raid on/off.",
            "/antiraid_disablechannel [channel]": "Disable anti-raid in a channel.",
            "/warn_list": "See the warn list.",
            "/remove_warn [user]": "Remove a warn from a user."
        }
        if anti_raid_commands:
            embed.add_field(name="Anti-Raid Commands", value="\n".join(f"`{command}`: {description}" for command, description in anti_raid_commands.items()), inline=False)

        welcome_commands = {
            "/welcome_channel [channel] [message]": "Set the welcome channel and message."
        }
        if welcome_commands:
            embed.add_field(name="Welcome Commands", value="\n".join(f"`{command}`: {description}" for command, description in welcome_commands.items()), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)

def setup(bot):
    bot.add_cog(BasicCommands(bot))