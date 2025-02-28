# commands/utility.py
import nextcord
from nextcord.ext import commands
from nextcord import slash_command, ui
import datetime
import json
import os


class Utility(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.triggers_file = 'data/triggers.json'
        self.load_triggers()

    def load_triggers(self):
        """Load triggers from JSON file"""
        if not os.path.exists('data'):
            os.makedirs('data')
            
        if not os.path.exists(self.triggers_file):
            with open(self.triggers_file, 'w') as f:
                json.dump({}, f)
                
        with open(self.triggers_file, 'r') as f:
            try:
                self.triggers = json.load(f)
            except json.JSONDecodeError:
                self.triggers = {}
    
    def save_triggers(self):
        """Save triggers to JSON file"""
        with open(self.triggers_file, 'w') as f:
            json.dump(self.triggers, f, indent=4)

    @nextcord.slash_command(name="say", description="Makes Reise say something")
    async def say(self, interaction: nextcord.Interaction, message: str):
        embed = nextcord.Embed(
            description=message,
            color=interaction.user.color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"💬 Message by {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.set_author(name="📢 Announcement", icon_url=self.bot.user.avatar.url)
        await interaction.response.send_message("✅ Message sent!", ephemeral=True)
        await interaction.channel.send(embed=embed)

    @nextcord.slash_command(name="ping", description="Checks bot latency")
    async def ping(self, interaction: nextcord.Interaction):
        latency = round(self.bot.latency * 1000)
        if latency < 100:
            color = nextcord.Color.green()
            status = "Excellent"
            emoji = "⚡"
        elif latency < 200:
            color = nextcord.Color.gold()
            status = "Good"
            emoji = "✅"
        else:
            color = nextcord.Color.red()
            status = "Poor"
            emoji = "⚠️"
            
        embed = nextcord.Embed(
            title=f"🏓 Pong! {emoji}",
            description=f"**Latency:** `{latency}ms`\n**Status:** {status}",
            color=color,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @nextcord.slash_command("invite", description="Invite Riese Into Your server!")
    async def invite(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="🤖 Invite Reise",
            color=nextcord.Color.blue(),
            description="**Add me to your server!**\n\n🔗 [Click here to invite](https://rlyaa.xyz/riese)",
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        await interaction.response.send_message(embed=embed)

    @slash_command("about", description="about reise")
    async def about(self, interaction: nextcord.Interaction):
        pass

    @about.subcommand("me", description="About Reise!")
    async def aboutme(self, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="✨ About Reise ✨",
            color=nextcord.Color.purple(),
            description="Riese is like that friend who always brings the party! 🎉 This Discord bot is packed with fun features to make your server pop.\n\n🛡️ **Moderation tools** to keep things tidy\n🔧 **Utility commands** for everyday use\n👋 **Personalized welcome messages** to greet new members\n🤖 **AI capabilities** for smart interactions\n\nBuilt with Python and nextcord, Riese is one smart cookie with a playful attitude. Add it to your server and let the good times roll! 🚀"
        )
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        embed.add_field(name="🔗 Links", value="[Website](https://rlyaa.xyz) | [Invite Bot](https://rlyaa.xyz/riese)", inline=False)
        await interaction.response.send_message(embed=embed)

    @slash_command("clear", description="Clear a specified number of messages")
    @commands.has_permissions(manage_messages=True)
    async def clear(self, interaction: nextcord.Interaction, amount: int):
        if not interaction.user.guild_permissions.manage_messages:
            error_embed = nextcord.Embed(
                title="❌ Permission Error",
                description="You don't have permission to manage messages!",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=error_embed, ephemeral=True)
            return
            
        await interaction.response.send_message("🧹 Cleaning messages...", ephemeral=True)

        if amount <= 0:
            error_embed = nextcord.Embed(
                title="❌ Invalid Amount",
                description="Amount must be a positive number",
                color=nextcord.Color.red()
            )
            await interaction.channel.send(embed=error_embed)
            return
            
        deleted = 0
        if amount >= 100:
            await interaction.channel.purge(limit=amount)
        else:
            async for message in interaction.channel.history(limit=amount):
                await message.delete()
                deleted += 1
                
        success_embed = nextcord.Embed(
            title="🧹 Channel Cleaned",
            description=f"Successfully cleared `{amount}` message(s)",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        success_embed.add_field(name="👮 Moderator", value=interaction.user.mention)
        success_embed.set_footer(text="Messages deleted", icon_url=interaction.user.avatar.url)
        
        await interaction.channel.send(embed=success_embed)
        print(f"Clear Log: {interaction.user}, {deleted}")
        
    @slash_command(name="trigger", description="Manage trigger words")
    async def trigger(self, interaction: nextcord.Interaction):
        """Base command for trigger word management"""
        # This won't be accessible directly since there are subcommands
        pass
        
    @trigger.subcommand(name="dashboard", description="View trigger management dashboard")
    async def trigger_dashboard(self, interaction: nextcord.Interaction):
        """Display the trigger word management dashboard"""
        embed = nextcord.Embed(
            title="⚙️ Trigger Word Management",
            description="Manage trigger words for this server",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="📝 Add Trigger", value="Add a new trigger word", inline=True)
        embed.add_field(name="📋 List Triggers", value="View all your triggers", inline=True)
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        
        view = TriggerManagementView(self)
        await interaction.response.send_message(embed=embed, view=view)
        
    @trigger.subcommand(name="add", description="Add a new trigger word")
    async def trigger_add(self, interaction: nextcord.Interaction):
        """Add a new trigger word and response"""
        await interaction.response.send_modal(TriggerAddModal(self))
        
    @trigger.subcommand(name="list", description="List and manage trigger words")
    async def trigger_list(self, interaction: nextcord.Interaction):
        """List all trigger words for this server with management buttons"""
        guild_id = str(interaction.guild.id)
        
        if guild_id not in self.triggers or not self.triggers[guild_id]:
            embed = nextcord.Embed(
                title="📋 Trigger Words",
                description="No trigger words set up for this server.",
                color=nextcord.Color.blue()
            )
            await interaction.response.send_message(embed=embed)
            return
            
        embed = nextcord.Embed(
            title="📋 Trigger Words",
            description="Here are all trigger words for this server. Use the buttons below to manage them:",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        for trigger, data in self.triggers[guild_id].items():
            status = "🟢 Enabled" if data.get("enabled", True) else "🔴 Disabled"
            embed.add_field(
                name=f"`{trigger}` ({status})",
                value=f"Response: {data['response'][:50]}{'...' if len(data['response']) > 50 else ''}",
                inline=False
            )
            
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        
        # Create view with management buttons
        view = TriggerListView(self, guild_id)
        await interaction.response.send_message(embed=embed, view=view)
        
    @trigger.subcommand(name="manage", description="Manage a specific trigger word")
    async def trigger_manage(self, interaction: nextcord.Interaction, trigger_word: str):
        """Manage a specific trigger word with buttons"""
        guild_id = str(interaction.guild.id)
        
        if guild_id not in self.triggers or trigger_word not in self.triggers[guild_id]:
            embed = nextcord.Embed(
                title="❌ Error",
                description=f"Trigger word `{trigger_word}` not found.",
                color=nextcord.Color.red()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            return
            
        trigger_data = self.triggers[guild_id][trigger_word]
        status = "🟢 Enabled" if trigger_data.get("enabled", True) else "🔴 Disabled"
        
        embed = nextcord.Embed(
            title=f"⚙️ Manage Trigger: `{trigger_word}`",
            description=f"Status: {status}\nResponse: {trigger_data['response'][:1000]}{'...' if len(trigger_data['response']) > 1000 else ''}",
            color=nextcord.Color.blue(),
            timestamp=datetime.datetime.now()
        )
        
        # Add metadata
        if "created_at" in trigger_data:
            created_at = datetime.datetime.fromisoformat(trigger_data["created_at"])
            embed.add_field(
                name="Created",
                value=f"<t:{int(created_at.timestamp())}:R>",
                inline=True
            )
            
        if "created_by" in trigger_data:
            creator_id = trigger_data["created_by"]
            embed.add_field(
                name="Created By",
                value=f"<@{creator_id}>",
                inline=True
            )
            
        embed.set_footer(text=f"Requested by {interaction.user}", icon_url=interaction.user.avatar.url)
        
        # Create view with management buttons for this specific trigger
        view = TriggerManageView(self, guild_id, trigger_word)
        await interaction.response.send_message(embed=embed, view=view)
        
    # Helper methods for trigger management
    async def remove_trigger(self, interaction, guild_id, trigger_word):
        """Remove a trigger word"""
        if guild_id not in self.triggers or trigger_word not in self.triggers[guild_id]:
            return False
            
        del self.triggers[guild_id][trigger_word]
        self.save_triggers()
        return True
        
    async def toggle_trigger(self, interaction, guild_id, trigger_word, enable=True):
        """Enable or disable a trigger word"""
        if guild_id not in self.triggers or trigger_word not in self.triggers[guild_id]:
            return False
            
        self.triggers[guild_id][trigger_word]["enabled"] = enable
        self.save_triggers()
        return True
        
    @commands.Cog.listener()
    async def on_message(self, message):
        """Check messages for trigger words"""
        # Don't respond to bots
        if message.author.bot:
            return
            
        # Only process messages in guilds
        if not message.guild:
            return
            
        guild_id = str(message.guild.id)
        
        # Check if guild has triggers
        if guild_id not in self.triggers:
            return
            
        content = message.content.lower()
        
        # Check each trigger word
        for trigger, data in self.triggers[guild_id].items():
            # Skip disabled triggers
            if not data.get("enabled", True):
                continue
                
            if trigger.lower() in content:
                # Check if should reply or just send a message
                if data.get("should_reply", False):
                    await message.reply(data["response"])
                else:
                    await message.channel.send(data["response"])
                break


# Button Views for Trigger Management
class TriggerManagementView(ui.View):
    def __init__(self, cog):
        super().__init__(timeout=60)
        self.cog = cog
        
    @ui.button(label="Add Trigger", style=nextcord.ButtonStyle.green, emoji="📝")
    async def add_button(self, button: ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(TriggerAddModal(self.cog))
        
    @ui.button(label="List Triggers", style=nextcord.ButtonStyle.blurple, emoji="📋")
    async def list_button(self, button: ui.Button, interaction: nextcord.Interaction):
        # Call the existing list subcommand
        await self.cog.trigger_list(interaction)


class TriggerListView(ui.View):
    def __init__(self, cog, guild_id):
        super().__init__(timeout=120)
        self.cog = cog
        self.guild_id = guild_id
        self.add_item(TriggerSelect(cog, guild_id))
        
    @ui.button(label="Add New Trigger", style=nextcord.ButtonStyle.green, emoji="📝")
    async def add_button(self, button: ui.Button, interaction: nextcord.Interaction):
        await interaction.response.send_modal(TriggerAddModal(self.cog))


class TriggerSelect(ui.Select):
    def __init__(self, cog, guild_id):
        self.cog = cog
        self.guild_id = guild_id
        
        # Create options from trigger words
        options = []
        if guild_id in cog.triggers:
            for trigger in cog.triggers[guild_id]:
                options.append(nextcord.SelectOption(
                    label=trigger[:25],  # Limit to 25 chars for select
                    value=trigger,
                    description=f"Manage this trigger word"
                ))
                
        # If no triggers, add a placeholder
        if not options:
            options = [nextcord.SelectOption(
                label="No triggers available",
                value="none",
                description="Add a trigger first"
            )]
            
        super().__init__(
            placeholder="Select a trigger to manage...",
            min_values=1,
            max_values=1,
            options=options[:25]  # Discord limits to 25 options
        )
        
    async def callback(self, interaction: nextcord.Interaction):
        selected_trigger = self.values[0]
        if selected_trigger == "none":
            await interaction.response.send_message("No triggers to manage. Add one first!", ephemeral=True)
            return
            
        # Call the manage subcommand
        await self.cog.trigger_manage(interaction, selected_trigger)


class TriggerManageView(ui.View):
    def __init__(self, cog, guild_id, trigger_word):
        super().__init__(timeout=60)
        self.cog = cog
        self.guild_id = guild_id
        self.trigger_word = trigger_word
        
        # Set the enable/disable button based on current status
        is_enabled = cog.triggers[guild_id][trigger_word].get("enabled", True)
        if is_enabled:
            self.add_item(ui.Button(label="Disable", style=nextcord.ButtonStyle.secondary, emoji="🔴", custom_id="disable"))
        else:
            self.add_item(ui.Button(label="Enable", style=nextcord.ButtonStyle.success, emoji="🟢", custom_id="enable"))
        
        # Add reply mode status
        is_reply_mode = cog.triggers[guild_id][trigger_word].get("should_reply", False)
        reply_label = "Switch to Message Mode" if is_reply_mode else "Switch to Reply Mode"
        reply_emoji = "💬" if is_reply_mode else "↩️"
        self.add_item(ui.Button(label=reply_label, style=nextcord.ButtonStyle.primary, emoji=reply_emoji, custom_id="toggle_reply"))
            
    @ui.button(label="Remove", style=nextcord.ButtonStyle.danger, emoji="🗑️")
    async def remove_button(self, button: ui.Button, interaction: nextcord.Interaction):
        # Create confirmation view
        view = ConfirmView(self.cog, self.guild_id, self.trigger_word, "remove")
        
        embed = nextcord.Embed(
            title="⚠️ Confirm Removal",
            description=f"Are you sure you want to remove the trigger word `{self.trigger_word}`?",
            color=nextcord.Color.red()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)
        
    @ui.button(label="Edit", style=nextcord.ButtonStyle.primary, emoji="✏️")
    async def edit_button(self, button: ui.Button, interaction: nextcord.Interaction):
        trigger_data = self.cog.triggers[self.guild_id][self.trigger_word]
        await interaction.response.send_modal(
            TriggerEditModal(self.cog, self.guild_id, self.trigger_word, trigger_data["response"])
        )
        
    # Custom button handler for enable/disable and reply toggle since the buttons change dynamically
    async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
        if interaction.data["custom_id"] == "enable":
            success = await self.cog.toggle_trigger(interaction, self.guild_id, self.trigger_word, True)
            if success:
                embed = nextcord.Embed(
                    title="🟢 Trigger Enabled",
                    description=f"Enabled trigger word: `{self.trigger_word}`",
                    color=nextcord.Color.green()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                # Refresh the management view
                await self.cog.trigger_manage(interaction, self.trigger_word)
                
        elif interaction.data["custom_id"] == "disable":
            success = await self.cog.toggle_trigger(interaction, self.guild_id, self.trigger_word, False)
            if success:
                embed = nextcord.Embed(
                    title="🔴 Trigger Disabled",
                    description=f"Disabled trigger word: `{self.trigger_word}`",
                    color=nextcord.Color.orange()
                )
                await interaction.response.send_message(embed=embed, ephemeral=True)
                # Refresh the management view
                await self.cog.trigger_manage(interaction, self.trigger_word)
                
        elif interaction.data["custom_id"] == "toggle_reply":
            trigger_data = self.cog.triggers[self.guild_id][self.trigger_word]
            current_setting = trigger_data.get("should_reply", False)
            
            # Toggle it
            trigger_data["should_reply"] = not current_setting
            self.cog.save_triggers()
            
            # Show confirmation
            new_state = "Reply to messages" if trigger_data["should_reply"] else "Send as new messages"
            embed = nextcord.Embed(
                title="🔄 Reply Mode Updated",
                description=f"Trigger `{self.trigger_word}` will now: **{new_state}**",
                color=nextcord.Color.green()
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
            # Refresh the view
            await self.cog.trigger_manage(interaction, self.trigger_word)
                
        return True


class ConfirmView(ui.View):
    def __init__(self, cog, guild_id, trigger_word, action):
        super().__init__(timeout=30)
        self.cog = cog
        self.guild_id = guild_id
        self.trigger_word = trigger_word
        self.action = action
        
    @ui.button(label="Confirm", style=nextcord.ButtonStyle.danger)
    async def confirm_button(self, button: ui.Button, interaction: nextcord.Interaction):
        if self.action == "remove":
            success = await self.cog.remove_trigger(interaction, self.guild_id, self.trigger_word)
            if success:
                embed = nextcord.Embed(
                    title="✅ Trigger Removed",
                    description=f"Removed trigger word: `{self.trigger_word}`",
                    color=nextcord.Color.green()
                )
                await interaction.response.edit_message(embed=embed, view=None)
                
                # Also update the original message
                await self.cog.trigger_list(interaction)
                
    @ui.button(label="Cancel", style=nextcord.ButtonStyle.secondary)
    async def cancel_button(self, button: ui.Button, interaction: nextcord.Interaction):
        embed = nextcord.Embed(
            title="❌ Cancelled",
            description="Action cancelled",
            color=nextcord.Color.grey()
        )
        await interaction.response.edit_message(embed=embed, view=None)


class TriggerAddModal(ui.Modal):
    def __init__(self, cog):
        super().__init__(title="Add Trigger Word")
        self.cog = cog
        
        self.trigger_word = ui.TextInput(
            label="Trigger Word",
            placeholder="Enter the word or phrase that will trigger a response",
            min_length=1,
            max_length=100,
            required=True
        )
        self.add_item(self.trigger_word)
        
        self.response = ui.TextInput(
            label="Response",
            placeholder="Enter the response to send when triggered",
            style=nextcord.TextInputStyle.paragraph,
            min_length=1,
            max_length=2000,
            required=True
        )
        self.add_item(self.response)
        
    async def callback(self, interaction: nextcord.Interaction):
        trigger = self.trigger_word.value
        response = self.response.value
        guild_id = str(interaction.guild.id)
        
        # Initialize guild in triggers if not exists
        if guild_id not in self.cog.triggers:
            self.cog.triggers[guild_id] = {}
            
        # Add trigger
        self.cog.triggers[guild_id][trigger] = {
            "response": response,
            "enabled": True,
            "should_reply": False,  # Default to sending new messages
            "created_by": interaction.user.id,
            "created_at": datetime.datetime.now().isoformat()
        }
        
        # Save to file
        self.cog.save_triggers()
        
        embed = nextcord.Embed(
            title="✅ Trigger Added",
            description=f"Successfully added trigger word: `{trigger}`",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="Trigger", value=f"`{trigger}`", inline=False)
        embed.add_field(name="Response", value=response[:1024], inline=False)
        embed.add_field(name="Reply Mode", value="🔄 Sends as new message (default)", inline=False)
        embed.set_footer(text=f"Created by {interaction.user}", icon_url=interaction.user.avatar.url)
        
        # Add view with toggle reply button
        view = TriggerAddedView(self.cog, guild_id, trigger)
        await interaction.response.send_message(embed=embed, view=view)


class TriggerEditModal(ui.Modal):
    def __init__(self, cog, guild_id, trigger_word, current_response):
        super().__init__(title="Edit Trigger Response")
        self.cog = cog
        self.guild_id = guild_id
        self.trigger_word = trigger_word
        
        self.response = ui.TextInput(
            label="New Response",
            placeholder="Edit the response for this trigger",
            style=nextcord.TextInputStyle.paragraph,
            min_length=1,
            max_length=2000,
            required=True,
            default_value=current_response
        )
        self.add_item(self.response)
        
    async def callback(self, interaction: nextcord.Interaction):
        new_response = self.response.value
        
        # Update the trigger response
        self.cog.triggers[self.guild_id][self.trigger_word]["response"] = new_response
        self.cog.triggers[self.guild_id][self.trigger_word]["edited_by"] = interaction.user.id
        self.cog.triggers[self.guild_id][self.trigger_word]["edited_at"] = datetime.datetime.now().isoformat()
        self.cog.save_triggers()
        
        # Get current reply mode
        is_reply_mode = self.cog.triggers[self.guild_id][self.trigger_word].get("should_reply", False)
        reply_status = "Replies to message" if is_reply_mode else "Sends as new message"
        
        embed = nextcord.Embed(
            title="✅ Trigger Updated",
            description=f"Successfully updated response for: `{self.trigger_word}`",
            color=nextcord.Color.green(),
            timestamp=datetime.datetime.now()
        )
        embed.add_field(name="New Response", value=new_response[:1024], inline=False)
        embed.add_field(name="Mode", value=f"🔄 {reply_status}", inline=False)
        embed.set_footer(text=f"Edited by {interaction.user}", icon_url=interaction.user.avatar.url)
        
        await interaction.response.send_message(embed=embed)
        
        # Also refresh the management view
        await self.cog.trigger_manage(interaction, self.trigger_word)
        

class TriggerAddedView(ui.View):
    def __init__(self, cog, guild_id, trigger_word):
        super().__init__(timeout=60)
        self.cog = cog
        self.guild_id = guild_id
        self.trigger_word = trigger_word
        
    @ui.button(label="Set to Reply Mode", style=nextcord.ButtonStyle.primary, emoji="↩️")
    async def set_reply_button(self, button: ui.Button, interaction: nextcord.Interaction):
        # Update to reply mode
        self.cog.triggers[self.guild_id][self.trigger_word]["should_reply"] = True
        self.cog.save_triggers()
        
        embed = nextcord.Embed(
            title="🔄 Reply Mode Updated",
            description=f"Trigger `{self.trigger_word}` will now reply to messages instead of sending new ones",
            color=nextcord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
        self.stop()
        
    @ui.button(label="Manage Trigger", style=nextcord.ButtonStyle.secondary, emoji="⚙️")
    async def manage_button(self, button: ui.Button, interaction: nextcord.Interaction):
        await self.cog.trigger_manage(interaction, self.trigger_word)
        self.stop()


def setup(bot):
    bot.add_cog(Utility(bot))
