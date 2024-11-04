import nextcord
from nextcord.ext import commands
import sqlite3

class GroupChatNormal(commands.Cog):  # Renamed the cog to avoid conflict
    def __init__(self, bot):
        self.bot = bot
        self.gc_enabled = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # Load GC enabled status from database
        conn = sqlite3.connect('gc_settings.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gc_settings (
                guild_id INTEGER PRIMARY KEY,
                gc_enabled INTEGER DEFAULT 1
            )
        ''')
        cursor.execute("SELECT guild_id, gc_enabled FROM gc_settings")
        for row in cursor.fetchall():
            self.gc_enabled[row[0]] = bool(row[1])
        conn.close()

    @commands.group(name="gc", invoke_without_command=True)
    async def gc_normal(self, ctx: commands.Context):
        await ctx.send_help("gc")

    @gc_normal.command(name="setup")
    async def setup_normal(self, ctx: commands.Context, gc_name: str):

        # Check if GC is enabled for this server
        guild_id = ctx.guild.id
        if not self.gc_enabled.get(guild_id, True):
            return await ctx.send("Group chat creation is currently disabled for this server.")

        # Get or Create the Category
        category_name = "Group Chats"
        category = nextcord.utils.get(ctx.guild.categories, name=category_name)
        if not category:
            try:
                category = await ctx.guild.create_category(category_name)
            except nextcord.Forbidden:
                return await ctx.send("I don't have permission to create categories.")

        # Create the channel with only the owner having access
        overwrites = {
            ctx.guild.default_role: nextcord.PermissionOverwrite(read_messages=False),
            ctx.author: nextcord.PermissionOverwrite(read_messages=True),
        }

        try:
            channel = await ctx.guild.create_text_channel(
                name=gc_name,
                overwrites=overwrites,
                category=category
            )
        except nextcord.Forbidden:
            return await ctx.send("I don't have permission to create channels.")
        except nextcord.HTTPException as e:
            return await ctx.send(f"An error occurred while creating the channel: {e}")

        # Store the GC owner in the database
        conn = sqlite3.connect('gc_owners.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS gc_owners (
                gc_id INTEGER PRIMARY KEY,
                owner_id INTEGER
            )
        ''')
        try:
            cursor.execute("INSERT INTO gc_owners (gc_id, owner_id) VALUES (?, ?)", (channel.id, ctx.author.id))
        except sqlite3.IntegrityError:
            return await ctx.send("A group chat with that name already exists.")
        conn.commit()
        conn.close()

        await ctx.send(f"Group chat '{gc_name}' created successfully!")

    @gc_normal.command(name="add")
    async def add_member_normal(self, ctx: commands.Context, gc_name: str, member: nextcord.Member):
        await self._manage_member(ctx, gc_name, member, True)

    @gc_normal.command(name="remove")
    async def remove_member_normal(self, ctx: commands.Context, gc_name: str, member: nextcord.Member):
        await self._manage_member(ctx, gc_name, member, False)

    @gc_normal.command(name="delete")
    async def delete_normal(self, ctx: commands.Context, gc_name: str):
        channel = nextcord.utils.get(ctx.guild.channels, name=gc_name)
        if not channel:
            return await ctx.send(f"Group chat '{gc_name}' not found.")

        # Check if the user is the owner OR an admin
        if not (await self._check_ownership(ctx, channel) or ctx.author.guild_permissions.administrator):
            return await ctx.send("You do not have permission to delete this group chat.")

        try:
            await channel.delete()
            # Remove the GC from the database
            conn = sqlite3.connect('gc_owners.db')
            cursor = conn.cursor()
            cursor.execute("DELETE FROM gc_owners WHERE gc_id = ?", (channel.id,))
            conn.commit()
            conn.close()
            await ctx.send(f"Group chat '{gc_name}' deleted successfully!")
        except nextcord.Forbidden:
            return await ctx.send("I don't have permission to delete this channel.")

    @gc_normal.command(name="toggle")
    async def toggle_gc_normal(self, ctx: commands.Context):
        if not ctx.author.guild_permissions.administrator:
            return await ctx.send("You need administrator permission to use this command.")

        guild_id = ctx.guild.id
        self.gc_enabled[guild_id] = not self.gc_enabled.get(guild_id, True)

        # Save the updated status to the database
        conn = sqlite3.connect('gc_settings.db')
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO gc_settings (guild_id, gc_enabled) VALUES (?, ?)", (guild_id, int(self.gc_enabled[guild_id])))
        conn.commit()
        conn.close()

        status = "enabled" if self.gc_enabled[guild_id] else "disabled"
        await ctx.send(f"Group chat creation has been **{status}** for this server.")

    async def _manage_member(self, ctx: commands.Context, gc_name: str, member: nextcord.Member, add: bool):
        channel = nextcord.utils.get(ctx.guild.channels, name=gc_name)
        if not channel:
            return await ctx.send(f"Group chat '{gc_name}' not found.")

        if not await self._check_ownership(ctx, channel):
            return await ctx.send("You are not the owner of this group chat.")

        try:
            if add:
                await channel.set_permissions(member, read_messages=True)
                action = "added to"
            else:
                await channel.set_permissions(member, overwrite=None)
                action = "removed from"
            await ctx.send(f"{member.mention} {action} '{gc_name}' successfully!")
        except nextcord.Forbidden:
            await ctx.send("I don't have permission to manage this channel.")

    async def _check_ownership(self, ctx: commands.Context, channel: nextcord.TextChannel):
        conn = sqlite3.connect('gc_owners.db')
        cursor = conn.cursor()
        cursor.execute("SELECT owner_id FROM gc_owners WHERE gc_id = ?", (channel.id,))
        result = cursor.fetchone()
        conn.close()
        if result and result[0] == ctx.author.id:
            return True
        return False

def setup(bot):
    bot.add_cog(GroupChatNormal(bot))  # Use the new cog name here