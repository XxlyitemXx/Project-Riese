import nextcord
import datetime
import os
import json
from nextcord.ext import commands

from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai

from assets.utils.config_loader import load_config




class AI_interaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = load_config()
        api_key_gemini = config.get("api_key_gemini")
        genai.configure(api_key=api_key_gemini)
        # Store active chats (channel_id -> history)
        self.active_chats = {}
        # Directory to store chat history
        self.history_dir = "chat_history"
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
            
        self.model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 1,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain",
            },
            safety_settings={
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            },
            system_instruction="""You're Riese , Riese is a discord bot that can answer questions and help user with user's problems""",
        )

    @commands.command("ask", description="Ask a question to the AI")
    async def ask(self, ctx, *, question: str):
        try:
            response = self.model.generate_content(question)

            embed = nextcord.Embed(
                title="AI Response", color=0x00FF00, timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Question", value=question, inline=False)

            if len(response.text) > 1024:
                parts = [
                    response.text[i : i + 1024]
                    for i in range(0, len(response.text), 1024)
                ]
                for i, part in enumerate(parts, 1):
                    field_name = "Answer" if i == 1 else f"Answer (continued {i})"
                    embed.add_field(name=field_name, value=part, inline=False)
            else:
                embed.add_field(name="Answer", value=response.text, inline=False)

            embed.set_footer(
                text=f"Asked by {ctx.author.name}",
                icon_url=ctx.author.avatar.url if ctx.author.avatar else None,
            )

            class ResponseButtons(nextcord.ui.View):
                def __init__(self, original_question, model, author_id):
                    super().__init__(timeout=180)
                    self.original_question = original_question
                    self.model = model
                    self.author_id = author_id

                async def interaction_check(self, interaction: nextcord.Interaction) -> bool:
                    if interaction.user.id != self.author_id:
                        await interaction.response.send_message("This button is not for you!", ephemeral=True)
                        return False
                    return True

                @nextcord.ui.button(label="Shorter", style=nextcord.ButtonStyle.gray)
                async def shorter(
                    self, button: nextcord.ui.Button, interaction: nextcord.Interaction
                ):
                    await interaction.response.defer()
                    new_prompt = f"Please provide a shorter version of the answer to this question: {self.original_question}"
                    new_response = self.model.generate_content(new_prompt)
                    await interaction.edit_original_message(
                        embed=self.update_embed(interaction, new_response.text)
                    )

                @nextcord.ui.button(label="Longer", style=nextcord.ButtonStyle.gray)
                async def longer(
                    self, button: nextcord.ui.Button, interaction: nextcord.Interaction
                ):
                    await interaction.response.defer()
                    new_prompt = f"Please provide a more detailed and longer answer to this question: {self.original_question}"
                    new_response = self.model.generate_content(new_prompt)
                    await interaction.edit_original_message(
                        embed=self.update_embed(interaction, new_response.text)
                    )

                @nextcord.ui.button(
                    label="Professional", style=nextcord.ButtonStyle.gray
                )
                async def professional(
                    self, button: nextcord.ui.Button, interaction: nextcord.Interaction
                ):
                    await interaction.response.defer()
                    new_prompt = f"Please provide a more professional and formal answer to this question: {self.original_question}"
                    new_response = self.model.generate_content(new_prompt)
                    await interaction.edit_original_message(
                        embed=self.update_embed(interaction, new_response.text)
                    )

                @nextcord.ui.button(label="Casual", style=nextcord.ButtonStyle.gray)
                async def casual(
                    self, button: nextcord.ui.Button, interaction: nextcord.Interaction
                ):
                    await interaction.response.defer()
                    new_prompt = f"Please provide a more casual and friendly answer to this question: {self.original_question}"
                    new_response = self.model.generate_content(new_prompt)
                    await interaction.edit_original_message(
                        embed=self.update_embed(interaction, new_response.text)
                    )

                @nextcord.ui.button(label="Simpler", style=nextcord.ButtonStyle.gray)
                async def simpler(
                    self, button: nextcord.ui.Button, interaction: nextcord.Interaction
                ):
                    await interaction.response.defer()
                    new_prompt = f"Please provide a simpler, easier to understand answer to this question: {self.original_question}"
                    new_response = self.model.generate_content(new_prompt)
                    await interaction.edit_original_message(
                        embed=self.update_embed(interaction, new_response.text)
                    )

                def update_embed(self, interaction, new_text):
                    new_embed = nextcord.Embed(
                        title="AI Response",
                        color=0x00FF00,
                        timestamp=datetime.datetime.now(),
                    )
                    new_embed.add_field(
                        name="Question", value=self.original_question, inline=False
                    )

                    if len(new_text) > 1024:
                        parts = [
                            new_text[i : i + 1024]
                            for i in range(0, len(new_text), 1024)
                        ]
                        for i, part in enumerate(parts, 1):
                            field_name = (
                                "Answer" if i == 1 else f"Answer (continued {i})"
                            )
                            new_embed.add_field(
                                name=field_name, value=part, inline=False
                            )
                    else:
                        new_embed.add_field(name="Answer", value=new_text, inline=False)

                    new_embed.set_footer(
                        text=f"Asked by {interaction.user.name}",
                        icon_url=(
                            interaction.user.avatar.url
                            if interaction.user.avatar
                            else None
                        ),
                    )
                    return new_embed

            view = ResponseButtons(question, self.model, ctx.author.id)
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            return

    @commands.command("start_chat", description="Start a persistent chat with the AI")
    @commands.has_permissions(administrator=True)
    async def start_chat(self, ctx):
        channel_id = ctx.channel.id
        
        # Check if chat is already active in this channel
        if channel_id in self.active_chats:
            await ctx.send("A chat is already active in this channel!")
            return
            
        # Create confirmation embed
        embed = nextcord.Embed(
            title="Start AI Chat",
            description="By starting this chat, you agree that your messages will be stored. The AI will respond to all messages in this channel.",
            color=0x00FF00,
            timestamp=datetime.datetime.now()
        )
        embed.set_footer(
            text=f"Requested by {ctx.author.name}",
            icon_url=ctx.author.avatar.url if ctx.author.avatar else None
        )
        
        # Create confirmation button
        class ConfirmView(nextcord.ui.View):
            def __init__(self, cog):
                super().__init__(timeout=60)
                self.cog = cog
                
            @nextcord.ui.button(label="Accept & Start Chat", style=nextcord.ButtonStyle.green)
            async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                if interaction.user.id != ctx.author.id:
                    await interaction.response.send_message("Only the command initiator can confirm this!", ephemeral=True)
                    return
                    
                # Initialize the chat history
                self.cog.active_chats[channel_id] = []
                
                # Load previous history if exists
                history_file = f"{self.cog.history_dir}/{channel_id}.json"
                if os.path.exists(history_file):
                    try:
                        with open(history_file, 'r') as f:
                            self.cog.active_chats[channel_id] = json.load(f)
                        await interaction.response.send_message("Chat started! I've loaded your previous conversation history.")
                    except Exception as e:
                        await interaction.response.send_message(f"Chat started! (Failed to load previous history: {str(e)})")
                else:
                    await interaction.response.send_message("Chat started! Send a message to begin our conversation.")
                
                # Save initial system message to history
                system_msg = {
                    "username": "SYSTEM",
                    "date": datetime.datetime.now().isoformat(),
                    "message": "Chat started",
                    "is_bot": True
                }
                self.cog.active_chats[channel_id].append(system_msg)
                self.cog.save_chat_history(channel_id)
                
        await ctx.send(embed=embed, view=ConfirmView(self))
        
    @commands.command("stop_chat", description="Stop the AI chat in this channel")
    @commands.has_permissions(administrator=True)
    async def stop_chat(self, ctx):
        channel_id = ctx.channel.id
        
        # Check if chat is active in this channel
        if channel_id not in self.active_chats:
            await ctx.send("There's no active chat in this channel!")
            return
            
        # Save final history and deactivate
        self.save_chat_history(channel_id)
        del self.active_chats[channel_id]
        
        await ctx.send("Chat has been deactivated and history has been saved.")
        
    def save_chat_history(self, channel_id):
        """Save chat history to a file"""
        if channel_id not in self.active_chats:
            return
            
        history_file = f"{self.history_dir}/{channel_id}.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.active_chats[channel_id], f)
        except Exception as e:
            print(f"Error saving chat history: {str(e)}")
            
    def load_chat_history(self, channel_id):
        """Load chat history from a file"""
        history_file = f"{self.history_dir}/{channel_id}.json"
        if not os.path.exists(history_file):
            return []
            
        try:
            with open(history_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading chat history: {str(e)}")
            return []
    
    @commands.Cog.listener()
    async def on_message(self, message):
        # Ignore bot messages
        if message.author.bot:
            return
            
        channel_id = message.channel.id
        
        # Check if this channel has an active chat
        if channel_id not in self.active_chats:
            return
            
        # Don't process commands
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return
            
        # Add user message to history
        user_msg = {
            "username": message.author.name,
            "date": datetime.datetime.now().isoformat(),
            "message": message.content,
            "is_bot": False
        }
        self.active_chats[channel_id].append(user_msg)
        
        # Format the entire conversation for the AI
        formatted_history = ""
        for entry in self.active_chats[channel_id]:
            formatted_history += f"[{entry['username']}] [{entry['date']}] {entry['message']}\n"
            
        # Add system instruction for context
        prompt = f"""The above is the conversation history. 
You are Riese, a cutie Discord assistant.
Please respond to the latest message from {message.author.name}: "{message.content}"
Keep your response be troll and funny and be a bit mean if possible and also roasting and respond short!.

IMPORTANT: Do NOT include any formatting tags like [Riese] [date] in your response. Just provide your response directly. & be kind to rlyaa shes your owner :skull: """

        # Get AI response
        try:
            # Show typing indicator
            async with message.channel.typing():
                response = self.model.generate_content(formatted_history + "\n" + prompt)
                
                # Clean response text to remove any format headers if they exist
                response_text = response.text
                # Check if response starts with formatting pattern like [Riese] [date]
                if response_text.startswith("[Riese]") and "[" in response_text[:50]:
                    # Find the second timestamp bracket and extract everything after it
                    parts = response_text.split("] ", 2)
                    if len(parts) >= 3:
                        response_text = parts[2]
                
                # Add AI response to history
                bot_msg = {
                    "username": "Riese",
                    "date": datetime.datetime.now().isoformat(),
                    "message": response_text,
                    "is_bot": True
                }
                self.active_chats[channel_id].append(bot_msg)
                
                # Save after each interaction
                self.save_chat_history(channel_id)
                
                # Send response
                if len(response_text) > 2000:
                    # Split into multiple messages if too long
                    parts = [response_text[i:i+2000] for i in range(0, len(response_text), 2000)]
                    for part in parts:
                        await message.channel.send(part)
                else:
                    await message.channel.send(response_text)
                    
        except Exception as e:
            await message.channel.send(f"I encountered an error: {str(e)}")
            
    @start_chat.error
    async def start_chat_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need administrator permissions to use this command.")
        else:
            await ctx.send(f"An error occurred: {str(error)}")
            
    @stop_chat.error
    async def stop_chat_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("You need administrator permissions to use this command.")
        else:
            await ctx.send(f"An error occurred: {str(error)}")


def setup(bot):
    bot.add_cog(AI_interaction(bot))
