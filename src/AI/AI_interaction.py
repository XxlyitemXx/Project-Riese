
import nextcord
import datetime
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


def setup(bot):
    bot.add_cog(AI_interaction(bot))
