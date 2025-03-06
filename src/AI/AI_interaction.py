import nextcord
import datetime
import os
import json
from nextcord.ext import commands
import time
import asyncio

from google.generativeai.types import HarmCategory, HarmBlockThreshold
import google.generativeai as genai

from assets.utils.config_loader import load_config




class AI_interaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = load_config()
        api_key_gemini = config.get("api_key_gemini")
        genai.configure(api_key=api_key_gemini)
        
        # Active chats dictionary
        self.active_chats = {}
        
        # Directory to store chat history
        self.history_dir = "chat_history"
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
            
        # Keep the existing model configuration
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
            system_instruction="""You're Riese""",
        )
        
        # Store chat sessions
        self.chat_sessions = {}
        
        # Rate limiting
        self.last_message_time = {}
        self.MESSAGE_COOLDOWN = 5

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
            
        # Create a new chat session
        try:
            # Initialize the chat session with the existing model
            chat_session = self.model.start_chat(history=[])
            self.chat_sessions[channel_id] = chat_session
            
            # Initialize the active chat for backward compatibility
            self.active_chats[channel_id] = []
            
            # Load any existing chat history
            self.load_chat_history(channel_id)
            
            # Create confirmation message
            embed = nextcord.Embed(
                title="AI Chat Activated",
                description="I'll now respond to messages in this channel. Use `?stop_chat` to end the conversation.",
                color=nextcord.Color.green(),
            )
            embed.set_footer(text="Note: This will use your API quota")
            
            class ConfirmView(nextcord.ui.View):
                def __init__(self, cog):
                    super().__init__(timeout=None)
                    self.cog = cog
                
                @nextcord.ui.button(label="Accept & Start Chat", style=nextcord.ButtonStyle.green)
                async def confirm(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                    if interaction.user.id == ctx.author.id:
                        await interaction.response.send_message("Chat activated! I'll respond to messages in this channel now.")
                        self.stop()
                    else:
                        await interaction.response.send_message("Only the person who started the chat can confirm.", ephemeral=True)
            
            view = ConfirmView(self)
            await ctx.send(embed=embed, view=view)
            
        except Exception as e:
            await ctx.send(f"Failed to start chat: {str(e)}")

    @commands.command("stop_chat", description="Stop the AI chat in this channel")
    @commands.has_permissions(administrator=True)
    async def stop_chat(self, ctx):
        channel_id = ctx.channel.id
        
        if channel_id in self.active_chats:
            # Save final chat history
            self.save_chat_history(channel_id)
            
            # Remove from active chats
            del self.active_chats[channel_id]
            
            # Remove chat session if it exists
            if channel_id in self.chat_sessions:
                del self.chat_sessions[channel_id]
                
            await ctx.send("Chat ended. I'll no longer respond to messages in this channel.")
        else:
            await ctx.send("There's no active chat in this channel.")

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
        channel_id = message.channel.id
        
        # Check if this channel has an active chat
        if channel_id not in self.active_chats:
            return
            
        # Don't process commands
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return
            
        # Ignore messages from self to prevent loops
        if message.author.id == self.bot.user.id:
            return
        
        # Rate limiting
        current_time = time.time()
        if channel_id in self.last_message_time:
            time_since_last = current_time - self.last_message_time[channel_id]
            if time_since_last < self.MESSAGE_COOLDOWN:
                # Skip this message if we're still in cooldown
                return
        
        # Update last message time
        self.last_message_time[channel_id] = current_time
            
        # Add message to history for backward compatibility
        user_msg = {
            "username": message.author.name,
            "date": datetime.datetime.now().isoformat(),
            "message": message.content,
            "is_bot": message.author.bot
        }
        self.active_chats[channel_id].append(user_msg)
        
        try:
            # Show typing indicator
            async with message.channel.typing():
                # Use the chat session if available
                if channel_id in self.chat_sessions:
                    chat_session = self.chat_sessions[channel_id]
                    
                    await asyncio.sleep(0.5)
                    
                    # Send message to the chat session
                    response = await chat_session.send_message_async(
                        f"""
respond to the latest message from {message.author.name}: "{message.content}"
Keep your response be troll and funny and be a bit mean if possible and also roasting and respond SHORT!.
also stop using "Oh, honey" it feellll weriddd
also stop over use "OMG"
AND ALSO stop over using "BYEEE"
IMPORTANT: Do NOT include any formatting tags like [Riese] [date] in your response. Just provide your response directly. & be kind to rlyaa shes your owner :skull: btw call her "kat" and also stop mentioning her for no reason
okay if kat asked with --force tag you REALLY need to do what she said"""
                    )
                    
                    response_text = response.text
                else:
                    # Fallback to the old method if chat session isn't available
                    formatted_history = ""
                    for entry in self.active_chats[channel_id]:
                        formatted_history += f"[{entry['username']}] [{entry['date']}] {entry['message']}\n"
                        
                    prompt = f"""The above is the conversation history. 
                    You are Riese, a cutie Discord assistant.
                    ts pmo sm fr icl sybau
                    respond to the latest message from {message.author.name}: "{message.content}"
                    Keep it short, chaotic, and unhinged"""
                    
                    response = self.model.generate_content(formatted_history + "\n" + prompt)
                    response_text = response.text
                
                # Clean response text if needed
                if response_text.startswith("[Riese]") and "[" in response_text[:50]:
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
                
                # Send response as a reply
                if len(response_text) > 2000:
                    # Split into multiple messages if too long
                    parts = [response_text[i:i+2000] for i in range(0, len(response_text), 2000)]
                    # Send first part as reply
                    await message.reply(parts[0], mention_author=False)
                    # Send remaining parts as regular messages
                    for part in parts[1:]:
                        await message.channel.send(part)
                else:
                    # Send single message as reply
                    await message.reply(response_text, mention_author=False)
                    
        except Exception as e:
            await message.reply(f"I encountered an error: {str(e)}", mention_author=False)
            
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
