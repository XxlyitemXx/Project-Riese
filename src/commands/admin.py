import nextcord
from nextcord.ext import commands
from nextcord import slash_command, SlashOption
import datetime
import os
import sys
import subprocess
import asyncio
import importlib
import traceback
import json
from assets.utils.config_loader import load_config
config = load_config()
owner_id = config.get('owner_id')
CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'config.json')

def load_config():
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as config_file:
                config_data = json.load(config_file)
                print(f"Loaded config with owner ID: {config_data.get('owner_id')}")
                return config_data
        else:
            print(f"Config file not found at {CONFIG_FILE}, using defaults")
            return {"owner_id": None}
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading config: {e}")
        return {"owner_id": None}


def save_config(config):
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        with open(CONFIG_FILE, 'w') as config_file:
            json.dump(config, config_file, indent=4)
            print(f"Saved config with owner ID: {config.get('owner_id')}")
        return True
    except Exception as e:
        print(f"Error saving config: {e}")
        return False


class OwnerOnlyCheck:
    def __init__(self, bot_instance=None):
        self.bot = bot_instance
        self._app_owner_id = None
        self._config_owner_allowed = False
    
    async def get_application_owner(self, interaction):
        if not self._app_owner_id:
            if self.bot:
                application = await self.bot.application_info()
            else:
                application = await interaction.client.application_info()
            
            self._app_owner_id = int(application.owner.id)
            print(f"Retrieved application owner: {self._app_owner_id}")
        return self._app_owner_id
    
    async def get_config_owner(self):
        config = load_config()
        if config and "owner_id" in config:
            try:
                return int(config["owner_id"])
            except (ValueError, TypeError):
                return None
        return None
    
    async def is_owner(self, interaction):
        user_id = int(interaction.user.id)
        app_owner_id = await self.get_application_owner(interaction)
        
        if user_id == app_owner_id:
            return True
            
        if self._config_owner_allowed:
            config_owner_id = await self.get_config_owner()
            if config_owner_id and user_id == config_owner_id:
                return True
                
        print(f"Owner check failed: user_id={user_id}, app_owner={app_owner_id}, config_allowed={self._config_owner_allowed}")
        return False
    
    async def check_owner(self, interaction):
        is_owner = await self.is_owner(interaction)
        
        if not is_owner:
            app_owner = await self.get_application_owner(interaction)
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="🔒 Access Denied",
                    description=f"This command is restricted to the bot owner only.\n\nOnly the Discord user with ID `{app_owner}` can use this command.",
                    color=nextcord.Color.red()
                ),
                ephemeral=True
            )
        
        return is_owner

owner_check = OwnerOnlyCheck()

def is_owner():
    async def predicate(interaction):
        return await owner_check.check_owner(interaction)
    return commands.check(predicate)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo_url = "https://github.com/XxlyitemXx/Project-Riese"
        
        global owner_check
        owner_check.bot = bot
        
        self.config = load_config()
        
        if not self.config.get("owner_id"):
            bot.loop.create_task(self._set_initial_owner())
            
    async def _set_initial_owner(self):
        try:
            await asyncio.sleep(5)
            app_info = await self.bot.application_info()
            app_owner_id = int(app_info.owner.id)
            
            self.config["owner_id"] = app_owner_id
            save_config(self.config)
            print(f"Initial owner ID set to application owner: {app_owner_id}")
        except Exception as e:
            print(f"Error setting initial owner: {e}")
    
    async def cog_before_invoke(self, ctx):
        if isinstance(ctx, nextcord.Interaction):
            if not await owner_check.is_owner(ctx):
                return False
        return True
    
    @slash_command(name="admin", description="Bot administration commands (Owner only)")
    async def admin(self, interaction: nextcord.Interaction):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        pass
    
    @admin.subcommand(name="extension", description="Manage bot extensions (Owner only)")
    async def extension(self, interaction: nextcord.Interaction):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        pass
    
    @extension.subcommand(name="load", description="Load an extension")
    async def load_extension(self, interaction: nextcord.Interaction, 
                              extension: str = SlashOption(
                                  description="Extension name to load",
                                  required=True
                              )):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            extension_path = f"commands.{extension}"
            self.bot.load_extension(extension_path)
            
            embed = nextcord.Embed(
                title="✅ Extension Loaded",
                description=f"Successfully loaded extension: `{extension}`",
                color=nextcord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Extension Error",
                description=f"Failed to load extension: `{extension}`",
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @extension.subcommand(name="unload", description="Unload an extension")
    async def unload_extension(self, interaction: nextcord.Interaction, 
                                extension: str = SlashOption(
                                    description="Extension name to unload",
                                    required=True
                                )):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            if extension == "admin":
                embed = nextcord.Embed(
                    title="❌ Cannot Unload",
                    description="The admin extension cannot be unloaded to prevent lockout.",
                    color=nextcord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
                
            extension_path = f"commands.{extension}"
            self.bot.unload_extension(extension_path)
            
            embed = nextcord.Embed(
                title="✅ Extension Unloaded",
                description=f"Successfully unloaded extension: `{extension}`",
                color=nextcord.Color.orange(),
                timestamp=datetime.datetime.now()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Extension Error",
                description=f"Failed to unload extension: `{extension}`",
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @extension.subcommand(name="reload", description="Reload an extension")
    async def reload_extension(self, interaction: nextcord.Interaction, 
                                extension: str = SlashOption(
                                    description="Extension name to reload",
                                    required=True
                                )):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            extension_path = f"commands.{extension}"
            self.bot.reload_extension(extension_path)
            
            embed = nextcord.Embed(
                title="✅ Extension Reloaded",
                description=f"Successfully reloaded extension: `{extension}`",
                color=nextcord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Extension Error",
                description=f"Failed to reload extension: `{extension}`",
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            
            error_traceback = traceback.format_exc()
            if len(error_traceback) > 1000:
                error_traceback = error_traceback[:997] + "..."
            embed.add_field(name="Traceback", value=f"```py\n{error_traceback}\n```", inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @extension.subcommand(name="list", description="List all extensions")
    async def list_extensions(self, interaction: nextcord.Interaction):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="📋 Bot Extensions",
            description="List of all extensions and their status",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        extension_files = []
        commands_dir = os.path.join(os.path.dirname(__file__))
        for filename in os.listdir(commands_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                extension_files.append(filename[:-3])
        
        loaded_extensions = [ext.split('.')[-1] for ext in self.bot.extensions.keys()]
        
        for ext in sorted(extension_files):
            status = "🟢 Loaded" if ext in loaded_extensions else "🔴 Unloaded"
            embed.add_field(name=ext, value=status, inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @admin.subcommand(name="update", description="Update the bot from GitHub")
    async def update(self, interaction: nextcord.Interaction):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="🔄 Updating Bot",
            description="Pulling latest changes from GitHub...",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        message = await interaction.followup.send(embed=embed, ephemeral=True)
        
        try:
            process = await asyncio.create_subprocess_shell(
                'git pull',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            if process.returncode == 0:
                stdout_str = stdout.decode().strip()
                
                if "Already up to date" in stdout_str:
                    embed = nextcord.Embed(
                        title="✅ Already Up To Date",
                        description="The bot is already running the latest version.",
                        color=nextcord.Color.green(),
                        timestamp=datetime.datetime.now()
                    )
                else:
                    changed_files = []
                    for line in stdout_str.split('\n'):
                        if line.strip() and not line.startswith('From '):
                            changed_files.append(line.strip())
                    
                    embed = nextcord.Embed(
                        title="✅ Update Successful",
                        description="Successfully pulled the latest changes from GitHub.",
                        color=nextcord.Color.green(),
                        timestamp=datetime.datetime.now()
                    )
                    
                    if stdout_str:
                        if len(stdout_str) > 1000:
                            stdout_str = stdout_str[:997] + "..."
                        embed.add_field(name="Git Output", value=f"```\n{stdout_str}\n```", inline=False)
                    
                    view = UpdateActionView(self)
                    await interaction.followup.edit_message(embed=embed, view=view, message_id=message.id)
                    return
            else:
                stderr_str = stderr.decode().strip()
                embed = nextcord.Embed(
                    title="❌ Update Failed",
                    description="Failed to pull the latest changes from GitHub.",
                    color=nextcord.Color.red(),
                    timestamp=datetime.datetime.now()
                )
                if stderr_str:
                    if len(stderr_str) > 1000:
                        stderr_str = stderr_str[:997] + "..."
                    embed.add_field(name="Error", value=f"```\n{stderr_str}\n```", inline=False)
            
            await interaction.followup.edit_message(embed=embed, message_id=message.id)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Update Error",
                description="An error occurred while trying to update the bot.",
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.edit_message(embed=embed, message_id=message.id)
    
    @admin.subcommand(name="restart", description="Restart the bot")
    async def restart(self, interaction: nextcord.Interaction):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="🔄 Restarting Bot",
            description="The bot is restarting. Please wait...",
            color=nextcord.Color.orange(),
            timestamp=datetime.datetime.now()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        try:
            await self.bot.change_presence(status=nextcord.Status.idle, activity=nextcord.Game(name="Restarting..."))
            await asyncio.sleep(1)
            
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Restart Error",
                description="An error occurred while trying to restart the bot.",
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    async def reload_all_extensions(self):
        success = []
        failed = []
        
        for ext in list(self.bot.extensions.keys()):
            try:
                self.bot.reload_extension(ext)
                success.append(ext.split('.')[-1])
            except Exception as e:
                failed.append((ext.split('.')[-1], str(e)))
        
        return success, failed

    @admin.subcommand(name="owner", description="Set the bot owner ID")
    async def set_owner(self, interaction: nextcord.Interaction, user_id: str = SlashOption(
        description="The Discord ID of the new owner (leave blank to set to yourself)",
        required=False
    )):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        if not user_id:
            user_id = str(interaction.user.id)
        
        try:
            new_owner_id = int(user_id)
            
            config = load_config()
            old_owner_id = config.get("owner_id")
            
            print(f"Changing owner from {old_owner_id} to {new_owner_id} by user {interaction.user.id}")
            
            config["owner_id"] = new_owner_id
            
            if save_config(config):
                self.config = config
                
                embed = nextcord.Embed(
                    title="✅ Owner Updated",
                    description=(
                        f"Config owner ID updated from `{old_owner_id}` to `{new_owner_id}`\n\n"
                        f"**Note:** The application owner (ID: `{owner_id}`) will always have admin access "
                        f"regardless of the config owner setting."
                    ),
                    color=nextcord.Color.green(),
                    timestamp=datetime.datetime.now()
                )
                
                if new_owner_id == interaction.user.id:
                    embed.add_field(
                        name="Note", 
                        value="Owner ID set to your user ID.", 
                        inline=False
                    )
            else:
                embed = nextcord.Embed(
                    title="⚠️ Warning",
                    description="Owner ID updated in memory but failed to save to config file.",
                    color=nextcord.Color.yellow(),
                    timestamp=datetime.datetime.now()
                )
                
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = nextcord.Embed(
                title="❌ Invalid ID",
                description="Please provide a valid Discord user ID (numeric value).",
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Error",
                description="Failed to update owner ID.",
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)
            
    @admin.subcommand(name="check_owner", description="Check current owner settings")
    async def check_owner(self, interaction: nextcord.Interaction):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            config = load_config()
            config_owner_id = config.get("owner_id", "Not set")
            
            application = await self.bot.application_info()
            app_owner_id = application.owner.id
            
            embed = nextcord.Embed(
                title="👑 Owner Configuration",
                description="Current owner settings for the bot",
                color=nextcord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            embed.add_field(name="Application Owner ID", value=f"`{app_owner_id}`", inline=False)
            embed.add_field(name="Config Owner ID", value=f"`{config_owner_id}`", inline=False)
            embed.add_field(name="Your User ID", value=f"`{interaction.user.id}`", inline=False)
            embed.add_field(name="Config File Path", value=f"`{CONFIG_FILE}`", inline=False)
            
            if interaction.user.id == app_owner_id:
                embed.add_field(name="Your Status", value="✅ Application Owner", inline=True)
            elif interaction.user.id == int(config_owner_id) if isinstance(config_owner_id, (int, str)) else False:
                embed.add_field(name="Your Status", value="⚠️ Config Owner only", inline=True)
            else:
                embed.add_field(name="Your Status", value="❌ Not an owner", inline=True)
            
            if os.path.exists(CONFIG_FILE):
                embed.add_field(name="Config File", value="✅ Exists", inline=True)
            else:
                embed.add_field(name="Config File", value="❌ Not found", inline=True)
                
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Error",
                description="Failed to check owner configuration.",
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)

    @admin.subcommand(name="dashboard", description="Open the admin dashboard")
    async def admin_dashboard(self, interaction: nextcord.Interaction):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This command is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        embed = nextcord.Embed(
            title="🛠️ Admin Dashboard",
            description="Control panel for bot administration",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        uptime = datetime.datetime.now() - datetime.datetime.fromtimestamp(self.bot.launch_time) if hasattr(self.bot, 'launch_time') else "Unknown"
        embed.add_field(
            name="Bot Status", 
            value=f"**Latency:** {round(self.bot.latency * 1000)}ms\n**Uptime:** {uptime}\n**Servers:** {len(self.bot.guilds)}", 
            inline=False
        )
        
        view = AdminDashboardView(self)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class AdminDashboardView(nextcord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=300)
        self.cog = cog
        
    async def check_owner(self, interaction):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This button is restricted to the bot owner (ID: `{owner_id}`).\nYour ID: `{interaction.user.id}`",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return False
        return True
    
    @nextcord.ui.button(label="Extensions", style=nextcord.ButtonStyle.primary, row=0)
    async def extensions_button(self, button, interaction):
        if not await self.check_owner(interaction):
            return
            
        embed = nextcord.Embed(
            title="🧩 Extension Management",
            description="Load, unload, or reload bot extensions",
            color=nextcord.Color.blue()
        )
        
        loaded_exts = "\n".join([f"• `{ext.split('.')[-1]}`" for ext in self.cog.bot.extensions.keys()])
        embed.add_field(name="Loaded Extensions", value=loaded_exts or "None", inline=False)
        
        view = ExtensionManagementView(self.cog)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @nextcord.ui.button(label="Restart Bot", style=nextcord.ButtonStyle.danger, row=0)
    async def restart_button(self, button, interaction):
        if not await self.check_owner(interaction):
            return
            
        embed = nextcord.Embed(
            title="⚠️ Confirm Restart",
            description="Are you sure you want to restart the bot?",
            color=nextcord.Color.orange()
        )
        
        view = ConfirmRestartView(self.cog)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
    
    @nextcord.ui.button(label="Update Bot", style=nextcord.ButtonStyle.success, row=0)
    async def update_button(self, button, interaction):
        if not await self.check_owner(interaction):
            return
            
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="🔄 Updating Bot",
            description="Pulling latest changes from GitHub...",
            color=nextcord.Color.blue()
        )
        message = await interaction.followup.send(embed=embed, ephemeral=True)
        
        try:
            # Run git pull
            process = await asyncio.create_subprocess_shell(
                'git pull',
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate()
            
            # Check if successful
            if process.returncode == 0:
                stdout_str = stdout.decode().strip()
                
                if "Already up to date" in stdout_str:
                    embed = nextcord.Embed(
                        title="✅ Already Up To Date",
                        description="The bot is already running the latest version.",
                        color=nextcord.Color.green()
                    )
                else:
                    embed = nextcord.Embed(
                        title="✅ Update Successful",
                        description="Successfully pulled the latest changes from GitHub.",
                        color=nextcord.Color.green()
                    )
                    
                    if stdout_str:
                        if len(stdout_str) > 1000:
                            stdout_str = stdout_str[:997] + "..."
                        embed.add_field(name="Git Output", value=f"```\n{stdout_str}\n```", inline=False)
                    
                    # Add reload/restart buttons
                    view = UpdateActionView(self.cog)
                    await interaction.followup.edit_message(embed=embed, view=view, message_id=message.id)
                    return
            else:
                stderr_str = stderr.decode().strip()
                embed = nextcord.Embed(
                    title="❌ Update Failed",
                    description="Failed to pull the latest changes from GitHub.",
                    color=nextcord.Color.red()
                )
                if stderr_str:
                    if len(stderr_str) > 1000:
                        stderr_str = stderr_str[:997] + "..."
                    embed.add_field(name="Error", value=f"```\n{stderr_str}\n```", inline=False)
            
            await interaction.followup.edit_message(embed=embed, message_id=message.id)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Update Error",
                description="An error occurred while trying to update the bot.",
                color=nextcord.Color.red()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.edit_message(embed=embed, message_id=message.id)
    
    # Owner settings button
    @nextcord.ui.button(label="Owner Settings", style=nextcord.ButtonStyle.secondary, row=1)
    async def owner_button(self, button, interaction):
        if not await self.check_owner(interaction):
            return
            
        config = load_config()
        current_owner = config.get('owner_id', "Not set")
        
        embed = nextcord.Embed(
            title="👑 Owner Settings",
            description=f"Current owner ID: `{current_owner}`",
            color=nextcord.Color.gold()
        )
        
        view = OwnerSettingsView(self.cog)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# Extension management view
class ExtensionManagementView(nextcord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=120)
        self.cog = cog
        
        # Add extension select menu
        self.add_item(ExtensionSelect(cog))
    
    # Reload all button
    @nextcord.ui.button(label="Reload All", style=nextcord.ButtonStyle.primary)
    async def reload_all_button(self, button, interaction):
        # Check owner
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This button is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        # Reload all extensions
        success = []
        failed = []
        
        for ext in list(self.cog.bot.extensions.keys()):
            try:
                self.cog.bot.reload_extension(ext)
                success.append(ext.split('.')[-1])
            except Exception as e:
                failed.append((ext.split('.')[-1], str(e)))
        
        embed = nextcord.Embed(
            title="🔄 Extensions Reloaded",
            description="Reloaded all extensions",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        
        if success:
            embed.add_field(name="✅ Success", value="\n".join([f"`{ext}`" for ext in success]), inline=True)
        
        if failed:
            errors = "\n".join([f"`{ext}`: {err[:50]}..." if len(err) > 50 else f"`{ext}`: {err}" for ext, err in failed])
            embed.add_field(name="❌ Failed", value=errors, inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)


# Extension select menu
class ExtensionSelect(nextcord.ui.Select):
    def __init__(self, cog):
        self.cog = cog
        
        # Get list of extensions
        extensions = [ext.split('.')[-1] for ext in cog.bot.extensions.keys()]
        
        # Create options
        options = [
            nextcord.SelectOption(label=ext, description=f"Manage {ext} extension") 
            for ext in extensions[:25]  # Discord has a 25 option limit
        ]
        
        super().__init__(
            placeholder="Select an extension to manage...",
            min_values=1,
            max_values=1,
            options=options
        )
    
    async def callback(self, interaction):
        # Check owner
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This menu is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
        
        extension = self.values[0]
        
        embed = nextcord.Embed(
            title=f"🧩 Manage Extension: {extension}",
            description=f"Choose an action for the `{extension}` extension",
            color=nextcord.Color.blue()
        )
        
        view = SingleExtensionView(self.cog, extension)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


# Single extension management view
class SingleExtensionView(nextcord.ui.View):
    def __init__(self, cog, extension):
        super().__init__(timeout=60)
        self.cog = cog
        self.extension = extension
        
        # Disable unload button for admin extension
        if extension == "admin":
            for child in self.children:
                if child.label == "Unload":
                    child.disabled = True
                    child.style = nextcord.ButtonStyle.secondary
    
    @nextcord.ui.button(label="Reload", style=nextcord.ButtonStyle.primary)
    async def reload_button(self, button, interaction):
        # Check owner
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This button is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            extension_path = f"commands.{self.extension}"
            self.cog.bot.reload_extension(extension_path)
            
            embed = nextcord.Embed(
                title="✅ Extension Reloaded",
                description=f"Successfully reloaded extension: `{self.extension}`",
                color=nextcord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Extension Error",
                description=f"Failed to reload extension: `{self.extension}`",
                color=nextcord.Color.red()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @nextcord.ui.button(label="Unload", style=nextcord.ButtonStyle.danger)
    async def unload_button(self, button, interaction):
        # Check owner
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This button is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Don't allow unloading the admin extension
            if self.extension == "admin":
                embed = nextcord.Embed(
                    title="❌ Cannot Unload",
                    description="The admin extension cannot be unloaded to prevent lockout.",
                    color=nextcord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
                return
                
            extension_path = f"commands.{self.extension}"
            self.cog.bot.unload_extension(extension_path)
            
            embed = nextcord.Embed(
                title="✅ Extension Unloaded",
                description=f"Successfully unloaded extension: `{self.extension}`",
                color=nextcord.Color.orange()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Extension Error",
                description=f"Failed to unload extension: `{self.extension}`",
                color=nextcord.Color.red()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)


class ConfirmRestartView(nextcord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=60)
        self.cog = cog
    
    @nextcord.ui.button(label="Yes, Restart", style=nextcord.ButtonStyle.danger)
    async def confirm_button(self, button, interaction):
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This button is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="🔄 Restarting Bot",
            description="The bot is restarting. Please wait...",
            color=nextcord.Color.orange()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Restart the bot
        try:
            # Send a message to indicate restart is happening
            await self.cog.bot.change_presence(status=nextcord.Status.idle, activity=nextcord.Game(name="Restarting..."))
            await asyncio.sleep(1)
            
            # Restart the process
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Restart Error",
                description="An error occurred while trying to restart the bot.",
                color=nextcord.Color.red()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @nextcord.ui.button(label="Cancel", style=nextcord.ButtonStyle.secondary)
    async def cancel_button(self, button, interaction):
        await interaction.response.send_message("Restart cancelled.", ephemeral=True)
        self.stop()


# Owner settings view
class OwnerSettingsView(nextcord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=60)
        self.cog = cog
    
    @nextcord.ui.button(label="Set to Self", style=nextcord.ButtonStyle.primary)
    async def set_self_button(self, button, interaction):
        # Check owner
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This button is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Load current config
            config = load_config()
            old_owner_id = config.get("owner_id")
            new_owner_id = interaction.user.id
            
            # Update config with new owner ID
            config["owner_id"] = new_owner_id
            
            # Save config
            with open(CONFIG_FILE, 'w') as f:
                json.dump(config, f, indent=4)
            
            embed = nextcord.Embed(
                title="✅ Owner Updated",
                description=f"Owner ID updated to your ID: `{new_owner_id}`",
                color=nextcord.Color.green()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Error",
                description="Failed to update owner ID.",
                color=nextcord.Color.red()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @nextcord.ui.button(label="Set Custom ID", style=nextcord.ButtonStyle.secondary)
    async def set_custom_button(self, button, interaction):
        # Check owner
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This button is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        # Send modal for ID input
        await interaction.response.send_modal(OwnerIDModal(self.cog))


# Modal for custom owner ID input
class OwnerIDModal(nextcord.ui.Modal):
    def __init__(self, cog):
        super().__init__(title="Set Custom Owner ID", timeout=300)
        self.cog = cog
        
        # Add user ID text input
        self.user_id = nextcord.ui.TextInput(
            label="New Owner ID",
            placeholder="Enter the Discord user ID",
            required=True,
            min_length=17,
            max_length=20
        )
        self.add_item(self.user_id)
    
    async def callback(self, interaction):
        # Check owner
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This action is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            new_owner_id = int(self.user_id.value)
            
            # Load current config
            config = load_config()
            old_owner_id = config.get("owner_id")
            
            # Update config with new owner ID
            config["owner_id"] = new_owner_id
            
            # Save config
            if save_config(config):
                embed = nextcord.Embed(
                    title="✅ Owner Updated",
                    description=f"Owner ID updated from `{old_owner_id}` to `{new_owner_id}`",
                    color=nextcord.Color.green()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            else:
                embed = nextcord.Embed(
                    title="❌ Error",
                    description="Failed to save owner ID to config file.",
                    color=nextcord.Color.red()
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            
        except ValueError:
            embed = nextcord.Embed(
                title="❌ Invalid ID",
                description="Please provide a valid Discord user ID (numeric value).",
                color=nextcord.Color.red()
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Error",
                description="Failed to update owner ID.",
                color=nextcord.Color.red()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)


# View for actions after a successful update
class UpdateActionView(nextcord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=120)
        self.cog = cog
    
    @nextcord.ui.button(label="Reload All Extensions", style=nextcord.ButtonStyle.primary)
    async def reload_all_button(self, button, interaction):
        # Check owner
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This button is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        # Reload all extensions
        success, failed = await self.cog.reload_all_extensions()
        
        embed = nextcord.Embed(
            title="🔄 Extensions Reloaded",
            description="Reloaded all extensions after update",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        
        if success:
            embed.add_field(name="✅ Success", value="\n".join([f"`{ext}`" for ext in success]), inline=True)
        
        if failed:
            errors = "\n".join([f"`{ext}`: {err[:50]}..." if len(err) > 50 else f"`{ext}`: {err}" for ext, err in failed])
            embed.add_field(name="❌ Failed", value=errors, inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @nextcord.ui.button(label="Restart Bot", style=nextcord.ButtonStyle.danger)
    async def restart_button(self, button, interaction):
        # Check owner
        config = load_config()
        owner_id = config.get('owner_id')
        
        if interaction.user.id != int(owner_id):
            embed = nextcord.Embed(
                title="🔒 Access Denied",
                description=f"This button is restricted to the bot owner (ID: `{owner_id}`).",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="🔄 Restarting Bot",
            description="The bot is restarting to apply updates. Please wait...",
            color=nextcord.Color.orange()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Restart the bot
        try:
            await self.cog.bot.change_presence(status=nextcord.Status.idle, activity=nextcord.Game(name="Restarting..."))
            await asyncio.sleep(1)
            
            os.execv(sys.executable, ['python'] + sys.argv)
        except Exception as e:
            embed = nextcord.Embed(
                title="❌ Restart Error",
                description="An error occurred while trying to restart the bot.",
                color=nextcord.Color.red()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Admin(bot)) 