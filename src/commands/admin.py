# commands/admin.py
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


def load_config():
    """Load configuration from config.json"""
    try:
        with open('config.json', 'r') as config_file:
            return json.load(config_file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Return default config if file doesn't exist or is invalid
        return {"owner_id": None}


def is_owner():
    """Check if the user is the bot owner defined in config.json"""
    async def predicate(interaction):
        # Load config to get owner_id
        config = load_config()
        owner_id = config.get("owner_id")
        
        # If no owner ID is configured, fall back to application owner
        if not owner_id:
            application = await interaction.client.application_info()
            owner_id = application.owner.id
            
            # Save this ID to config for future use
            config["owner_id"] = owner_id
            try:
                with open('config.json', 'w') as config_file:
                    json.dump(config, config_file, indent=4)
            except Exception:
                pass  # Silent fail if can't write to config
        
        if interaction.user.id != owner_id:
            await interaction.response.send_message(
                embed=nextcord.Embed(
                    title="❌ Access Denied",
                    description="Only the bot owner can use this command.",
                    color=nextcord.Color.red()
                ),
                ephemeral=True
            )
            return False
        return True
    return nextcord.check(predicate)


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.repo_url = "https://github.com/project-reise/Reise-Bot"  # Update this to your repo URL
        self.config = load_config()
    
    @slash_command(name="admin", description="Bot administration commands (Owner only)")
    async def admin(self, interaction: nextcord.Interaction):
        """Base command for admin controls"""
        pass
    
    @admin.subcommand(name="extension", description="Manage bot extensions (Owner only)")
    async def extension(self, interaction: nextcord.Interaction):
        """Extension management commands"""
        pass
    
    @extension.subcommand(name="load", description="Load an extension")
    @is_owner()
    async def load_extension(self, interaction: nextcord.Interaction, 
                              extension: str = SlashOption(
                                  description="Extension name to load",
                                  required=True
                              )):
        """Load a bot extension"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            extension_path = f"commands.{extension}"
            await self.bot.load_extension(extension_path)
            
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
    @is_owner()
    async def unload_extension(self, interaction: nextcord.Interaction, 
                                extension: str = SlashOption(
                                    description="Extension name to unload",
                                    required=True
                                )):
        """Unload a bot extension"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Don't allow unloading the admin extension to prevent lockout
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
            await self.bot.unload_extension(extension_path)
            
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
    @is_owner()
    async def reload_extension(self, interaction: nextcord.Interaction, 
                                extension: str = SlashOption(
                                    description="Extension name to reload",
                                    required=True
                                )):
        """Reload a bot extension"""
        await interaction.response.defer(ephemeral=True)
        
        try:
            extension_path = f"commands.{extension}"
            await self.bot.reload_extension(extension_path)
            
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
            
            # Add traceback for more info
            error_traceback = traceback.format_exc()
            if len(error_traceback) > 1000:
                error_traceback = error_traceback[:997] + "..."
            embed.add_field(name="Traceback", value=f"```py\n{error_traceback}\n```", inline=False)
            
            await interaction.followup.send(embed=embed, ephemeral=True)
    
    @extension.subcommand(name="list", description="List all extensions")
    @is_owner()
    async def list_extensions(self, interaction: nextcord.Interaction):
        """List all bot extensions and their status"""
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="📋 Bot Extensions",
            description="List of all extensions and their status",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        # Get all extension files
        extension_files = []
        commands_dir = os.path.join(os.path.dirname(__file__))
        for filename in os.listdir(commands_dir):
            if filename.endswith('.py') and not filename.startswith('__'):
                extension_files.append(filename[:-3])  # Remove .py
        
        # Check loaded extensions
        loaded_extensions = [ext.split('.')[-1] for ext in self.bot.extensions.keys()]
        
        # Add fields for each extension
        for ext in sorted(extension_files):
            status = "🟢 Loaded" if ext in loaded_extensions else "🔴 Unloaded"
            embed.add_field(name=ext, value=status, inline=True)
        
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @admin.subcommand(name="update", description="Update the bot from GitHub (Owner only)")
    @is_owner()
    async def update(self, interaction: nextcord.Interaction):
        """Update the bot from the GitHub repository"""
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="🔄 Updating Bot",
            description="Pulling latest changes from GitHub...",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
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
                        color=nextcord.Color.green(),
                        timestamp=datetime.datetime.now()
                    )
                else:
                    # Get the files that were changed
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
                    
                    # Add the git output
                    if stdout_str:
                        if len(stdout_str) > 1000:
                            stdout_str = stdout_str[:997] + "..."
                        embed.add_field(name="Git Output", value=f"```\n{stdout_str}\n```", inline=False)
                    
                    # Add reload button
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
    
    @admin.subcommand(name="restart", description="Restart the bot (Owner only)")
    @is_owner()
    async def restart(self, interaction: nextcord.Interaction):
        """Restart the bot process"""
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="🔄 Restarting Bot",
            description="The bot is restarting. Please wait...",
            color=nextcord.Color.orange(),
            timestamp=datetime.datetime.now()
        )
        await interaction.followup.send(embed=embed, ephemeral=True)
        
        # Restart the bot
        try:
            # Send a message to indicate restart is happening
            await self.bot.change_presence(status=nextcord.Status.idle, activity=nextcord.Game(name="Restarting..."))
            await asyncio.sleep(1)
            
            # Restart the process
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
        """Reload all extensions"""
        success = []
        failed = []
        
        for ext in list(self.bot.extensions.keys()):
            try:
                await self.bot.reload_extension(ext)
                success.append(ext.split('.')[-1])
            except Exception as e:
                failed.append((ext.split('.')[-1], str(e)))
        
        return success, failed

    @admin.subcommand(name="owner", description="Set the bot owner ID")
    @is_owner()
    async def set_owner(self, interaction: nextcord.Interaction, user_id: str = SlashOption(
        description="The Discord ID of the new owner (leave blank to set to yourself)",
        required=False
    )):
        """Set the bot owner ID in config.json"""
        await interaction.response.defer(ephemeral=True)
        
        # If no ID provided, use the command invoker's ID
        if not user_id:
            user_id = str(interaction.user.id)
        
        try:
            # Validate it's a real Discord user ID (numeric)
            new_owner_id = int(user_id)
            
            # Load current config
            config = load_config()
            old_owner_id = config.get("owner_id")
            
            # Update config with new owner ID
            config["owner_id"] = new_owner_id
            
            # Save config
            with open('config.json', 'w') as config_file:
                json.dump(config, config_file, indent=4)
            
            # Reload config in memory
            self.config = config
            
            embed = nextcord.Embed(
                title="✅ Owner Updated",
                description=f"Bot owner changed from `{old_owner_id}` to `{new_owner_id}`",
                color=nextcord.Color.green(),
                timestamp=datetime.datetime.now()
            )
            
            # Add note if setting to self
            if new_owner_id == interaction.user.id:
                embed.add_field(
                    name="Note", 
                    value="Owner ID set to your user ID.", 
                    inline=False
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


class UpdateActionView(nextcord.ui.View):
    def __init__(self, cog):
        super().__init__(timeout=120)
        self.cog = cog
    
    @nextcord.ui.button(label="Reload All Extensions", style=nextcord.ButtonStyle.primary, emoji="🔄")
    async def reload_all_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        # Reload all extensions
        success, failed = await self.cog.reload_all_extensions()
        
        embed = nextcord.Embed(
            title="🔄 Extensions Reloaded",
            description="Reloaded extensions after update.",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        
        if success:
            embed.add_field(name="✅ Success", value="\n".join([f"`{ext}`" for ext in success]), inline=True)
        
        if failed:
            errors = "\n".join([f"`{ext}`: {err[:50]}..." if len(err) > 50 else f"`{ext}`: {err}" for ext, err in failed])
            embed.add_field(name="❌ Failed", value=errors, inline=True)
        
        self.stop()
        await interaction.followup.send(embed=embed, ephemeral=True)
    
    @nextcord.ui.button(label="Restart Bot", style=nextcord.ButtonStyle.danger, emoji="🔁")
    async def restart_button(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        await interaction.response.defer(ephemeral=True)
        
        embed = nextcord.Embed(
            title="🔄 Restarting Bot",
            description="The bot is restarting to apply updates. Please wait...",
            color=nextcord.Color.orange(),
            timestamp=datetime.datetime.now()
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
                color=nextcord.Color.red(),
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Error", value=f"```py\n{str(e)[:1000]}\n```")
            await interaction.followup.send(embed=embed, ephemeral=True)
            self.stop()


def setup(bot):
    bot.add_cog(Admin(bot)) 