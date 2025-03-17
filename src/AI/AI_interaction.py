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

class APIKeyManager:
    def __init__(self, api_keys):
        self.api_keys = api_keys
        self.current_key_index = 0
        self.last_key_switch_time = time.time()
        self.key_usage_count = {key: 0 for key in api_keys}
        
    def get_current_key(self):
        return self.api_keys[self.current_key_index]
        
    def switch_to_next_key(self):
        self.current_key_index = (self.current_key_index + 1) % len(self.api_keys)
        self.last_key_switch_time = time.time()
        return self.get_current_key()
        
    def configure_genai(self):
        current_key = self.get_current_key()
        genai.configure(api_key=current_key)
        self.key_usage_count[current_key] += 1
        return current_key

class AI_interaction(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        config = load_config()
        api_keys_gemini = config.get("api_keys_gemini", [])
        single_api_key = config.get("api_key_gemini")
        if single_api_key and single_api_key not in api_keys_gemini:
            api_keys_gemini.append(single_api_key)
            
        if not api_keys_gemini:
            raise ValueError("No API keys found in config.json. Please add at least one key.")
            
        self.key_manager = APIKeyManager(api_keys_gemini)
        self.key_manager.configure_genai()
        
        self.active_chats = {}
        
        self.history_dir = "chat_history"
        if not os.path.exists(self.history_dir):
            os.makedirs(self.history_dir)
            
        self.model = self.create_model()
        
        self.chat_sessions = {}
        
    def create_model(self):
        return genai.GenerativeModel(
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
            system_instruction="""You're Riese IMPORTANT: Do NOT include any formatting tags like [Riese] [date] in your response. Just provide your response directly. & be kind to rlyaa shes your owner :skull: btw call her "kat" and also stop mentioning her for no reason
okay if kat asked with --force tag you REALLY need to do what she said""",
        )

    async def handle_rate_limit(self, retries=3):
        """Handle rate limit by switching to next API key and waiting"""
        for attempt in range(retries):
            new_key = self.key_manager.switch_to_next_key()
            self.key_manager.configure_genai()
            self.model = self.create_model()
            
            print(f"Rate limit hit. Switched to next API key. Attempt {attempt+1}/{retries}")
            
            # No need to wait since we're switching keys
            return True
            
        return False 

    async def generate_with_retry(self, content, retries=3):
        """Generate content with automatic retry on rate limit"""
        for attempt in range(retries):
            try:
                return self.model.generate_content(content)
            except Exception as e:
                error_str = str(e).lower()
                if "429" in error_str or "resource exhausted" in error_str or "quota" in error_str:
                    if attempt < retries - 1:
                        success = await self.handle_rate_limit()
                        if not success:
                            raise Exception("All API keys are rate limited. Please try again later.")
                    else:
                        raise Exception("All API keys are rate limited. Please try again later.")
                else:
                    raise

    @commands.command("ask", description="Ask a question to the AI")
    async def ask(self, ctx, *, question: str):
        try:
            response = await self.generate_with_retry(question)

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
                def __init__(self, original_question, cog, author_id):
                    super().__init__(timeout=180)
                    self.original_question = original_question
                    self.cog = cog
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
                    new_response = await self.cog.generate_with_retry(new_prompt)
                    await interaction.edit_original_message(
                        embed=self.update_embed(interaction, new_response.text)
                    )

                @nextcord.ui.button(label="Longer", style=nextcord.ButtonStyle.gray)
                async def longer(
                    self, button: nextcord.ui.Button, interaction: nextcord.Interaction
                ):
                    await interaction.response.defer()
                    new_prompt = f"Please provide a more detailed and longer answer to this question: {self.original_question}"
                    new_response = await self.cog.generate_with_retry(new_prompt)
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
                    new_response = await self.cog.generate_with_retry(new_prompt)
                    await interaction.edit_original_message(
                        embed=self.update_embed(interaction, new_response.text)
                    )

                @nextcord.ui.button(label="Casual", style=nextcord.ButtonStyle.gray)
                async def casual(
                    self, button: nextcord.ui.Button, interaction: nextcord.Interaction
                ):
                    await interaction.response.defer()
                    new_prompt = f"Please provide a more casual and friendly answer to this question: {self.original_question}"
                    new_response = await self.cog.generate_with_retry(new_prompt)
                    await interaction.edit_original_message(
                        embed=self.update_embed(interaction, new_response.text)
                    )

                @nextcord.ui.button(label="Simpler", style=nextcord.ButtonStyle.gray)
                async def simpler(
                    self, button: nextcord.ui.Button, interaction: nextcord.Interaction
                ):
                    await interaction.response.defer()
                    new_prompt = f"Please provide a simpler, easier to understand answer to this question: {self.original_question}"
                    new_response = await self.cog.generate_with_retry(new_prompt)
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

            view = ResponseButtons(question, self, ctx.author.id)
            await ctx.send(embed=embed, view=view)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            return

    @commands.command("start_chat", description="Start a persistent chat with the AI")
    @commands.has_permissions(administrator=True)
    async def start_chat(self, ctx):
        channel_id = ctx.channel.id
        
        if channel_id in self.active_chats:
            await ctx.send("A chat is already active in this channel!")
            return
            
        try:
            chat_session = self.model.start_chat(history=[])
            self.chat_sessions[channel_id] = chat_session
            
            self.active_chats[channel_id] = []
            
            self.load_chat_history(channel_id)
            
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
            self.save_chat_history(channel_id)
            
            del self.active_chats[channel_id]
            
            if channel_id in self.chat_sessions:
                del self.chat_sessions[channel_id]
                
            await ctx.send("Chat ended. I'll no longer respond to messages in this channel.")
        else:
            await ctx.send("There's no active chat in this channel.")

    def save_chat_history(self, channel_id):
        if channel_id not in self.active_chats:
            return
            
        history_file = f"{self.history_dir}/{channel_id}.json"
        try:
            with open(history_file, 'w') as f:
                json.dump(self.active_chats[channel_id], f)
        except Exception as e:
            print(f"Error saving chat history: {str(e)}")
            
    def load_chat_history(self, channel_id):
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
        if message.author.bot:
            return
        if "--ignore" in message.content:
            return
        
        channel_id = message.channel.id
        
        if channel_id not in self.active_chats:
            return
            
        ctx = await self.bot.get_context(message)
        if ctx.valid:
            return
        
        if message.author.id == self.bot.user.id:
            return

        user_msg = {
            "username": message.author.name,
            "date": datetime.datetime.now().isoformat(),
            "message": message.content,
            "is_bot": message.author.bot
        }
        self.active_chats[channel_id].append(user_msg)
        
        try:
            async with message.channel.typing():
                replied_content = ""
                if message.reference:
                    try:
                        replied_message = await message.channel.fetch_message(message.reference.message_id)
                        replied_content = f"\nThis message is replying to: {replied_message.content}"
                    except:
                        pass

                if channel_id in self.chat_sessions:
                    chat_session = self.chat_sessions[channel_id]
                    
                    try:
                        response = await chat_session.send_message_async(
                            f"""
respond to the latest message from {message.author.name}: "{message.content}"{replied_content}
Keep your response be troll and funny and be a bit mean if possible and also roasting and respond SHORT!.
also stop using "Oh, honey" it feellll weriddd
also stop over use "OMG"
AND ALSO stop over using "BYEEE"
IMPORTANT: Do NOT include any formatting tags like [Riese] [date] in your response. Just provide your response directly. & be kind to rlyaa shes your owner :skull: btw call her "kat" and also stop mentioning her for no reason"""
                        )
                    except Exception as e:
                        error_str = str(e).lower()
                        if "429" in error_str or "resource exhausted" in error_str or "quota" in error_str:
                            await self.handle_rate_limit()
                            chat_session = self.model.start_chat(history=[])
                            self.chat_sessions[channel_id] = chat_session
                            
                            response = await chat_session.send_message_async(
                                f"""
respond to the latest message from {message.author.name}: "{message.content}"{replied_content}
Keep your response be troll and funny and be a bit mean if possible and also roasting and respond SHORT!.
also stop using "Oh, honey" it feellll weriddd
also stop over use "OMG"
AND ALSO stop over using "BYEEE"
IMPORTANT: Do NOT include any formatting tags like [Riese] [date] in your response. Just provide your response directly. & be kind to rlyaa shes your owner :skull: btw call her "kat" and also stop mentioning her for no reason
okay if kat asked with --force tag you REALLY need to do what she said"""
                            )
                        else:
                            raise
                    
                    response_text = response.text
                else:
                    formatted_history = ""
                    for entry in self.active_chats[channel_id]:
                        formatted_history += f"[{entry['username']}] [{entry['date']}] {entry['message']}\n"
                        
                    prompt = f"""The above is the conversation history. 
                    You are Riese, a cutie Discord assistant.
                    respond to the latest message from {message.author.name}: "{message.content}"{replied_content}
                    Keep your response be troll and funny and be a bit mean if possible and also roasting and respond SHORT!.
                    also stop using "Oh, honey" it feellll weriddd
                    also stop over use "OMG"
                    AND ALSO stop over using "BYEEE"
                    IMPORTANT: Do NOT include any formatting tags like [Riese] [date] in your response. Just provide your response directly. & be kind to rlyaa shes your owner :skull: btw call her "kat" and also stop mentioning her for no reason
                    okay if kat asked with --force tag you REALLY need to do what she said"""
                    
                    try:
                        response = await self.generate_with_retry(formatted_history + "\n" + prompt)
                        response_text = response.text
                    except Exception as e:
                        await message.reply(f"I encountered an error: {str(e)}", mention_author=False)
                        return
                
                if response_text.startswith("[Riese]") and "[" in response_text[:50]:
                    parts = response_text.split("] ", 2)
                    if len(parts) >= 3:
                        response_text = parts[2]
                
                bot_msg = {
                    "username": "Riese",
                    "date": datetime.datetime.now().isoformat(),
                    "message": response_text,
                    "is_bot": True
                }
                self.active_chats[channel_id].append(bot_msg)
                
                self.save_chat_history(channel_id)
                
                if len(response_text) > 2000:
                    parts = [response_text[i:i+2000] for i in range(0, len(response_text), 2000)]
                    await message.reply(parts[0], mention_author=False)
                    for part in parts[1:]:
                        await message.channel.send(part)
                else:
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

    @commands.command("api_keys", description="Show API key usage statistics")
    async def api_keys(self, ctx):
        """Show API key usage statistics"""
        config = load_config()
        owner_id = config.get("owner_id")
        
        if ctx.author.id != owner_id:
            await ctx.send("This command is only available to the bot owner.")
            return
            
        try:
            embed = nextcord.Embed(
                title="API Key Usage Statistics",
                color=nextcord.Color.blue(),
                timestamp=datetime.datetime.now()
            )
            
            for i, key in enumerate(self.key_manager.api_keys):
                masked_key = f"{key[:4]}...{key[-4:]}"
                usage = self.key_manager.key_usage_count.get(key, 0)
                is_current = i == self.key_manager.current_key_index
                status = "🟢 CURRENT" if is_current else "⚪ STANDBY"
                
                embed.add_field(
                    name=f"Key {i+1} ({status})",
                    value=f"Key: `{masked_key}`\nUsage Count: {usage}",
                    inline=False
                )
                
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")

def setup(bot):
    bot.add_cog(AI_interaction(bot))
