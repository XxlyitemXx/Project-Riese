import nextcord
from nextcord.ext import commands
import sqlite3

class Slashstick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        conn = sqlite3.connect('reise_main.db')
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sticky_messages (
                guild_id INTEGER,
                channel_id INTEGER,
                sticky_message TEXT,
                message_id INTEGER,
                PRIMARY KEY (guild_id, channel_id)
            )
        ''')
        conn.close()

    @nextcord.slash_command(name="sticky", description="Sticky message")
    @commands.has_permissions(administrator=True)
    async def sticky(self, interaction: nextcord.Interaction, message: str):
        pass
    @sticky.subcommand(name="add", description="Add a sticky message")
    async def add(self, interaction: nextcord.Interaction, message: str):
        try:
            conn = sqlite3.connect('reise_main.db')
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT OR REPLACE INTO sticky_messages 
                (guild_id, channel_id, sticky_message) 
                VALUES (?, ?, ?)
            ''', (interaction.guild.id, interaction.channel.id, message))
            
            conn.commit()
            conn.close()

            sticky_msg = await interaction.channel.send(message)
            conn = sqlite3.connect('reise_main.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE sticky_messages 
                SET message_id = ? 
                WHERE guild_id = ? AND channel_id = ?
            ''', (sticky_msg.id, interaction.guild.id, interaction.channel.id))
            
            conn.commit()
            conn.close()

            await interaction.response.send_message("Sticky message has been set!", ephemeral=True)
            await sticky_msg.delete()
        except sqlite3.Error as e:
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
        except nextcord.HTTPException as e:
            await interaction.response.send_message(f"Failed to send message: {e}", ephemeral=True)
        
    @sticky.subcommand(name="remove", description="Remove a sticky message")
    async def remove(self, interaction: nextcord.Interaction):
        pass
    @sticky.subcommand(name="list", description="List all sticky messages")
    async def list(self, interaction: nextcord.Interaction):
        pass
    @sticky.subcommand(name="edit", description="Edit a sticky message")
    async def edit(self, interaction: nextcord.Interaction, message: str):
        pass
    @sticky.subcommand(name="toggle", description="Toggle sticky messages")
    async def toggle(self, interaction: nextcord.Interaction):
        pass

def setup(bot):
    bot.add_cog(Slashstick(bot))
