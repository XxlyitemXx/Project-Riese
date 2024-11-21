import nextcord
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from nextcord.ext import commands
from assets.utils.config_loader import load_config
import datetime


class Summary(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
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
            system_instruction="""You're Riese , Riese is a discord bot that can summarize a message"""
        )
        config = load_config()
        api_key_gemini = config.get("api_key_gemini")
        genai.configure(api_key=api_key_gemini)




    @commands.command(name="sy", description="Summarize a message")
    async def summary(self, ctx, *, message=None):
        try:
            if not message:
                embed = nextcord.Embed(
                    title="Text Summarizer",
                    description="Please enter the text you want to summarize",
                    color=0x00ff00,
                    timestamp=datetime.datetime.now()
                )
                
                class SummaryButtons(nextcord.ui.View):
                    def __init__(self, original_text, model):
                        super().__init__(timeout=180)
                        self.original_text = original_text
                        self.model = model

                    @nextcord.ui.button(label="Shorter", style=nextcord.ButtonStyle.gray)
                    async def shorter(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        await interaction.response.defer()
                        current_summary = interaction.message.embeds[0].fields[0].value
                        new_prompt = f"Please provide a shorter summary of this text:\n{current_summary}"
                        new_response = self.model.generate_content(new_prompt)
                        
                        embeds = []
                        summary_parts = [new_response.text[i:i+1024] for i in range(0, len(new_response.text), 1024)]
                        
                        for i, part in enumerate(summary_parts):
                            embed = nextcord.Embed(
                                title=f"Shorter Version (Part {i+1}/{len(summary_parts)})" 
                                    if len(summary_parts) > 1 
                                    else "Shorter Version",
                                color=0x00ff00
                            )
                            embed.add_field(name=f"Summary Part {i+1}", value=part, inline=False)
                            embeds.append(embed)
                            
                        await interaction.edit_original_message(embeds=embeds)

                    @nextcord.ui.button(label="Longer", style=nextcord.ButtonStyle.gray)
                    async def longer(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        await interaction.response.defer()
                        current_summary = interaction.message.embeds[0].fields[0].value
                        new_prompt = f"Please provide a more detailed summary of this text:\n{current_summary}"
                        new_response = self.model.generate_content(new_prompt)
                        
                        embeds = []
                        summary_parts = [new_response.text[i:i+1024] for i in range(0, len(new_response.text), 1024)]
                        
                        for i, part in enumerate(summary_parts):
                            embed = nextcord.Embed(
                                title=f"Detailed Version (Part {i+1}/{len(summary_parts)})" 
                                    if len(summary_parts) > 1 
                                    else "Detailed Version",
                                color=0x00ff00
                            )
                            embed.add_field(name=f"Summary Part {i+1}", value=part, inline=False)
                            embeds.append(embed)
                            
                        await interaction.edit_original_message(embeds=embeds)

                    @nextcord.ui.button(label="Casual", style=nextcord.ButtonStyle.gray)
                    async def casual(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        await interaction.response.defer()
                        current_summary = interaction.message.embeds[0].fields[0].value
                        new_prompt = f"Please provide a more casual and friendly version of this text:\n{current_summary}"
                        new_response = self.model.generate_content(new_prompt)
                        
                        embeds = []
                        summary_parts = [new_response.text[i:i+1024] for i in range(0, len(new_response.text), 1024)]
                        
                        for i, part in enumerate(summary_parts):
                            embed = nextcord.Embed(
                                title=f"Casual Version (Part {i+1}/{len(summary_parts)})" 
                                    if len(summary_parts) > 1 
                                    else "Casual Version",
                                color=0x00ff00
                            )
                            embed.add_field(name=f"Summary Part {i+1}", value=part, inline=False)
                            embeds.append(embed)
                            
                        await interaction.edit_original_message(embeds=embeds)

                    @nextcord.ui.button(label="Simpler", style=nextcord.ButtonStyle.gray)
                    async def simpler(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        await interaction.response.defer()
                        current_summary = interaction.message.embeds[0].fields[0].value
                        new_prompt = f"Please provide a simpler, easier to understand version of this text:\n{current_summary}"
                        new_response = self.model.generate_content(new_prompt)
                        
                        embeds = []
                        summary_parts = [new_response.text[i:i+1024] for i in range(0, len(new_response.text), 1024)]
                        
                        for i, part in enumerate(summary_parts):
                            embed = nextcord.Embed(
                                title=f"Simpler Version (Part {i+1}/{len(summary_parts)})" 
                                    if len(summary_parts) > 1 
                                    else "Simpler Version",
                                color=0x00ff00
                            )
                            embed.add_field(name=f"Summary Part {i+1}", value=part, inline=False)
                            embeds.append(embed)
                            
                        await interaction.edit_original_message(embeds=embeds)
                    @nextcord.ui.button(label="Professional", style=nextcord.ButtonStyle.gray)
                    async def professional(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        await interaction.response.defer()
                        
                        # Get current summary from the embed
                        current_summary = interaction.message.embeds[0].fields[0].value
                        prompt = f"Please rewrite this text in a more professional tone:\n{current_summary}"
                        new_response = self.model.generate_content(prompt)
                        
                        # Create multiple embeds if needed
                        embeds = []
                        professional_parts = [new_response.text[i:i+1024] for i in range(0, len(new_response.text), 1024)]
                        
                        for i, part in enumerate(professional_parts):
                            embed = nextcord.Embed(
                                title=f"Professional Version (Part {i+1}/{len(professional_parts)})" 
                                    if len(professional_parts) > 1 
                                    else "Professional Version",
                                color=0x00ff00
                            )
                            embed.add_field(name=f"Summary Part {i+1}", value=part, inline=False)
                            embeds.append(embed)
                            
                        await interaction.edit_original_message(embeds=embeds)
                    @nextcord.ui.button(label="Translate", style=nextcord.ButtonStyle.gray)
                    async def translate(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        await interaction.response.defer()
                        class LanguageSelect(nextcord.ui.Select):
                            def __init__(self):
                                options = [
                                    nextcord.SelectOption(label="Thai", value="thai"),
                                    nextcord.SelectOption(label="Spanish", value="spanish"), 
                                    nextcord.SelectOption(label="French", value="french"),
                                    nextcord.SelectOption(label="German", value="german"),
                                    nextcord.SelectOption(label="Chinese", value="chinese"),
                                    nextcord.SelectOption(label="Japanese", value="japanese"),
                                    nextcord.SelectOption(label="Korean", value="korean"),
                                    nextcord.SelectOption(label="Russian", value="russian"),
                                    nextcord.SelectOption(label="Arabic", value="arabic"),
                                    nextcord.SelectOption(label="Hindi", value="hindi")
                                ]
                                super().__init__(placeholder="Select language to translate to...", options=options)

                            async def callback(self, interaction: nextcord.Interaction):
                                await interaction.response.defer()
                                current_summary = interaction.message.embeds[0].fields[0].value
                                new_prompt = f"Please translate this text to {self.values[0]}:\n{current_summary}"
                                new_response = self.view.model.generate_content(new_prompt)
                                
                                embeds = []
                                translation_parts = [new_response.text[i:i+1024] for i in range(0, len(new_response.text), 1024)]
                                
                                for i, part in enumerate(translation_parts):
                                    embed = nextcord.Embed(
                                        title=f"Translation to {self.values[0].title()} (Part {i+1}/{len(translation_parts)})" 
                                            if len(translation_parts) > 1 
                                            else f"Translation to {self.values[0].title()}",
                                        color=0x00ff00
                                    )
                                    embed.add_field(name=f"Translation Part {i+1}", value=part, inline=False)
                                    embeds.append(embed)
                                
                                # Create a new view with all the original buttons
                                new_view = SummaryButtons(self.view.original_text, self.view.model)
                                await interaction.edit_original_message(embeds=embeds, view=new_view)

                        # Create temporary view with just the language select
                        temp_view = nextcord.ui.View(timeout=180)
                        language_select = LanguageSelect()
                        temp_view.add_item(language_select)
                        temp_view.original_text = self.original_text
                        temp_view.model = self.model
                        
                        await interaction.edit_original_message(view=temp_view)

                class TextInput(nextcord.ui.Modal):
                    def __init__(self):
                        super().__init__(
                            "Text Summarizer",
                            timeout=None,
                        )

                        self.text = nextcord.ui.TextInput(
                            label="Enter your text",
                            style=nextcord.TextInputStyle.paragraph,
                            placeholder="Enter the text you want to summarize...",
                            required=True,
                            max_length=4000
                        )
                        self.add_item(self.text)

                    async def callback(self, interaction: nextcord.Interaction):
                        await interaction.response.defer()
                        prompt = f"Please summarize the following text:\n{self.text.value}"
                        response = ctx.cog.model.generate_content(prompt)
                        
                        # Create multiple embeds if the summary is too long
                        embeds = []
                        # Split into chunks of 1024 characters for embed fields
                        summary_parts = [response.text[i:i+1024] for i in range(0, len(response.text), 1024)]
                        
                        for i, part in enumerate(summary_parts):
                            embed = nextcord.Embed(
                                title=f"Summary (Part {i+1}/{len(summary_parts)})" if len(summary_parts) > 1 else "Summary",
                                color=0x00ff00
                            )
                            embed.add_field(name=f"Summary Part {i+1}", value=part, inline=False)
                            embeds.append(embed)
                        
                        view = SummaryButtons(self.text.value, ctx.cog.model)
                        # Send all embeds
                        await interaction.followup.send(embeds=embeds, view=view)

                class InputButton(nextcord.ui.View):
                    def __init__(self):
                        super().__init__()

                    @nextcord.ui.button(label="Enter Text", style=nextcord.ButtonStyle.green)
                    async def input_text(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
                        modal = TextInput()
                        await interaction.response.send_modal(modal)

                view = InputButton()
                await ctx.send(embed=embed, view=view)
            else:
                prompt = f"Please summarize the following text:\n{message}"
                response = self.model.generate_content(prompt)
                
                embeds = []
                # First embed with original text
                first_embed = nextcord.Embed(
                    title="Summary Result",
                    color=0x00ff00,
                    timestamp=datetime.datetime.now()
                )
                
                # Split original text if needed
                original_parts = [message[i:i+1024] for i in range(0, len(message), 1024)]
                for i, part in enumerate(original_parts):
                    field_name = "Original Text" if i == 0 else f"Original Text (continued {i+1})"
                    first_embed.add_field(name=field_name, value=part, inline=False)
                
                embeds.append(first_embed)
                
                # Split summary into multiple embeds if needed
                summary_parts = [response.text[i:i+4000] for i in range(0, len(response.text), 4000)]
                for i, part in enumerate(summary_parts):
                    embed = nextcord.Embed(
                        title=f"Summary (Part {i+1}/{len(summary_parts)})",
                        color=0x00ff00,
                        timestamp=datetime.datetime.now()
                    )
                    embed.add_field(name="Summary", value=part, inline=False)
                    embeds.append(embed)

                view = SummaryButtons(message, self.model)
                await ctx.send(embeds=embeds, view=view)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            return

def setup(bot):
    bot.add_cog(Summary(bot))