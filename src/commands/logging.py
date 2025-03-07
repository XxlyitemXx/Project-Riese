import nextcord
from nextcord.ext import commands
from nextcord import Interaction, SlashOption
import sqlite3
import json
from datetime import datetime
import os

class LoggingSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db_path = 'data/logging.db'
        self.setup_database()
        
    def setup_database(self):
        os.makedirs('data', exist_ok=True)
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_channels (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS log_settings (
                guild_id INTEGER,
                event_type TEXT,
                enabled INTEGER,
                PRIMARY KEY (guild_id, event_type)
            )
        ''')
        
        conn.commit()
        conn.close()

    def get_log_channel(self, guild_id: int) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT channel_id FROM log_channels WHERE guild_id = ?', (guild_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    def is_event_enabled(self, guild_id: int, event_type: str) -> bool:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'SELECT enabled FROM log_settings WHERE guild_id = ? AND event_type = ?',
            (guild_id, event_type)
        )
        result = cursor.fetchone()
        conn.close()
        return bool(result[0]) if result else False

    @nextcord.slash_command(name="log", description="Configure logging settings")
    async def log(self, interaction: Interaction):
        pass

    @log.subcommand(name="set-channel", description="Set the channel for logging")
    async def set_channel(
        self,
        interaction: Interaction,
        channel: nextcord.TextChannel = SlashOption(
            name="channel",
            description="The channel where logs will be sent",
            required=True
        )
    ):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need Manage Server permission to use this command!", ephemeral=True)
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO log_channels (guild_id, channel_id) VALUES (?, ?)',
            (interaction.guild_id, channel.id)
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"✅ Log channel has been set to {channel.mention}",
            ephemeral=True
        )

    @log.subcommand(name="toggle", description="Toggle logging for specific events")
    async def toggle(
        self,
        interaction: Interaction,
        event: str = SlashOption(
            name="event",
            description="The event type to toggle",
            choices=["messages", "members"],
            required=True
        ),
        state: str = SlashOption(
            name="state",
            description="Enable or disable the event",
            choices=["on", "off"],
            required=True
        )
    ):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need Manage Server permission to use this command!", ephemeral=True)
            return

        enabled = 1 if state == "on" else 0
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT OR REPLACE INTO log_settings (guild_id, event_type, enabled) VALUES (?, ?, ?)',
            (interaction.guild_id, event, enabled)
        )
        conn.commit()
        conn.close()

        await interaction.response.send_message(
            f"✅ Logging for {event} events has been turned {state}",
            ephemeral=True
        )

    @log.subcommand(name="status", description="Show current logging settings")
    async def status(self, interaction: Interaction):
        if not interaction.user.guild_permissions.manage_guild:
            await interaction.response.send_message("You need Manage Server permission to use this command!", ephemeral=True)
            return

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT channel_id FROM log_channels WHERE guild_id = ?', (interaction.guild_id,))
        channel_result = cursor.fetchone()
        
        cursor.execute('SELECT event_type, enabled FROM log_settings WHERE guild_id = ?', (interaction.guild_id,))
        event_settings = cursor.fetchall()
        
        conn.close()

        embed = nextcord.Embed(
            title="📝 Logging Configuration",
            color=nextcord.Color.blue(),
            timestamp=datetime.now()
        )

        log_channel = interaction.guild.get_channel(channel_result[0]) if channel_result else None
        embed.add_field(
            name="Log Channel",
            value=log_channel.mention if log_channel else "Not set",
            inline=False
        )

        events_status = ""
        for event_type, enabled in event_settings:
            status = "✅ Enabled" if enabled else "❌ Disabled"
            events_status += f"{event_type}: {status}\n"

        embed.add_field(
            name="Event Settings",
            value=events_status if events_status else "No events configured",
            inline=False
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild or message.author.bot:
            return
            
        if not self.is_event_enabled(message.guild.id, "messages"):
            return

        channel_id = self.get_log_channel(message.guild.id)
        if not channel_id:
            return

        log_channel = message.guild.get_channel(channel_id)
        if not log_channel:
            return

        embed = nextcord.Embed(
            title="🗑️ Message Deleted",
            description=f"**Content:** {message.content}",
            color=nextcord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Author", value=f"{message.author.mention} ({message.author.id})")
        embed.add_field(name="Channel", value=message.channel.mention)
        
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if not before.guild or before.author.bot or before.content == after.content:
            return
            
        if not self.is_event_enabled(before.guild.id, "messages"):
            return

        channel_id = self.get_log_channel(before.guild.id)
        if not channel_id:
            return

        log_channel = before.guild.get_channel(channel_id)
        if not log_channel:
            return

        embed = nextcord.Embed(
            title="✏️ Message Edited",
            color=nextcord.Color.yellow(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Before", value=before.content, inline=False)
        embed.add_field(name="After", value=after.content, inline=False)
        embed.add_field(name="Author", value=f"{before.author.mention} ({before.author.id})")
        embed.add_field(name="Channel", value=before.channel.mention)
        embed.add_field(name="Jump to Message", value=f"[Click Here]({after.jump_url})")
        
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        if not self.is_event_enabled(member.guild.id, "members"):
            return

        channel_id = self.get_log_channel(member.guild.id)
        if not channel_id:
            return

        log_channel = member.guild.get_channel(channel_id)
        if not log_channel:
            return

        embed = nextcord.Embed(
            title="👋 Member Joined",
            color=nextcord.Color.green(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Member", value=f"{member.mention} ({member.id})")
        embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d %H:%M:%S UTC"))
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await log_channel.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        if not self.is_event_enabled(member.guild.id, "members"):
            return

        channel_id = self.get_log_channel(member.guild.id)
        if not channel_id:
            return

        log_channel = member.guild.get_channel(channel_id)
        if not log_channel:
            return

        embed = nextcord.Embed(
            title="👋 Member Left",
            color=nextcord.Color.red(),
            timestamp=datetime.now()
        )
        embed.add_field(name="Member", value=f"{member.mention} ({member.id})")
        embed.add_field(name="Joined At", value=member.joined_at.strftime("%Y-%m-%d %H:%M:%S UTC"))
        embed.set_thumbnail(url=member.display_avatar.url)
        
        await log_channel.send(embed=embed)

def setup(bot):
    bot.add_cog(LoggingSystem(bot))