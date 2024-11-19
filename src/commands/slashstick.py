# Import required libraries
import nextcord
from nextcord.ext import commands
import sqlite3

# Define Slashstick cog class for sticky message functionality
class Slashstick(commands.Cog):
    def __init__(self, bot):
        # Initialize the cog with bot instance
        self.bot = bot
        # Create database connection
        conn = sqlite3.connect('reise_main.db')
        cursor = conn.cursor()
        # Create sticky_messages table if it doesn't exist
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

    # Main sticky command group
    @nextcord.slash_command(name="sticky", description="Sticky message")
    @commands.has_permissions(administrator=True)
    async def sticky(self, interaction: nextcord.Interaction, message: str):
        pass

    # Subcommand to add a sticky message
    @sticky.subcommand(name="add", description="Add a sticky message")
    async def add(self, interaction: nextcord.Interaction, message: str):
        try:
            # Connect to database
            conn = sqlite3.connect('reise_main.db')
            cursor = conn.cursor()
            
            # Insert or update sticky message
            cursor.execute('''
                INSERT OR REPLACE INTO sticky_messages 
                (guild_id, channel_id, sticky_message) 
                VALUES (?, ?, ?)
            ''', (interaction.guild.id, interaction.channel.id, message))
            
            conn.commit()
            conn.close()

            # Send temporary message to get ID
            sticky_msg = await interaction.channel.send(message)
            
            # Update message ID in database
            conn = sqlite3.connect('reise_main.db')
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE sticky_messages 
                SET message_id = ? 
                WHERE guild_id = ? AND channel_id = ?
            ''', (sticky_msg.id, interaction.guild.id, interaction.channel.id))
            
            conn.commit()
            conn.close()

            # Confirm to user and cleanup
            await interaction.response.send_message("Sticky message has been set!", ephemeral=True)
            await sticky_msg.delete()
        except sqlite3.Error as e:
            # Handle database errors
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
        except nextcord.HTTPException as e:
            # Handle Discord API errors
            await interaction.response.send_message(f"Failed to send message: {e}", ephemeral=True)
        
    # Subcommand to remove a sticky message
    @sticky.subcommand(name="remove", description="Remove a sticky message")
    async def remove(self, interaction: nextcord.Interaction):
        try:
            # Connect and delete sticky message
            conn = sqlite3.connect('reise_main.db')
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM sticky_messages WHERE guild_id = ? AND channel_id = ?
            ''', (interaction.guild.id, interaction.channel.id))

            conn.commit()
            conn.close()

            # Confirm to user
            await interaction.response.send_message("Sticky message has been removed!", ephemeral=True)
        except sqlite3.Error as e:
            # Handle database errors
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)

    # Subcommand to list all sticky messages
    @sticky.subcommand(name="list", description="List all sticky messages")
    async def list(self, interaction: nextcord.Interaction):
        try:
            # Get all sticky messages for the guild
            conn = sqlite3.connect('reise_main.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sticky_message FROM sticky_messages WHERE guild_id = ?
            ''', (interaction.guild.id,))
            result = cursor.fetchall()
            conn.close()

            # Create embed for response
            embed = nextcord.Embed(
                title="Sticky Messages",
                color=nextcord.Color.blue()
            )

            # Add messages to embed
            if not result:
                embed.description = "No sticky messages found."
            else:
                for i, msg in enumerate(result, 1):
                    embed.add_field(
                        name=f"Message {i}", 
                        value=msg[0],
                        inline=False
                    )

            # Send response
            await interaction.response.send_message(embed=embed)

        except sqlite3.Error as e:
            # Handle database errors with embed
            error_embed = nextcord.Embed(
                title="Error",
                description=f"An error occurred: {e}",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
        
    # Subcommand to edit existing sticky message
    @sticky.subcommand(name="edit", description="Edit a sticky message")
    async def edit(self, interaction: nextcord.Interaction, message: str):
        try:
            # Check if sticky message exists
            conn = sqlite3.connect('reise_main.db')
            cursor = conn.cursor()
            cursor.execute('''
                SELECT sticky_message FROM sticky_messages 
                WHERE guild_id = ? AND channel_id = ?
            ''', (interaction.guild.id, interaction.channel.id))
            
            # Return if no message found
            if not cursor.fetchone():
                await interaction.response.send_message("No sticky message found in this channel!", ephemeral=True)
                conn.close()
                return

            # Update message in database
            cursor.execute('''
                UPDATE sticky_messages 
                SET sticky_message = ?
                WHERE guild_id = ? AND channel_id = ?
            ''', (message, interaction.guild.id, interaction.channel.id))
            
            conn.commit()
            conn.close()

            # Confirm update to user
            await interaction.response.send_message("Sticky message has been updated!", ephemeral=True)
            
            # Update displayed sticky message if it exists
            if interaction.channel.id in self.bot.get_cog('MessageEvents').last_sticky_message:
                try:
                    # Delete old message
                    old_message = await interaction.channel.fetch_message(
                        self.bot.get_cog('MessageEvents').last_sticky_message[interaction.channel.id]
                    )
                    await old_message.delete()
                except:
                    pass
                
                # Send new message and update tracking
                new_sticky = await interaction.channel.send(f"Sticky message: {message}")
                self.bot.get_cog('MessageEvents').last_sticky_message[interaction.channel.id] = new_sticky.id

        except sqlite3.Error as e:
            # Handle database errors
            await interaction.response.send_message(f"An error occurred: {e}", ephemeral=True)
        
def setup(bot):
    bot.add_cog(Slashstick(bot))
