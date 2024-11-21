import nextcord
from nextcord.ext import commands
import datetime
import os

import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from assets.utils.config_loader import load_config



class LensMind(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-pro",
            generation_config={
                "temperature": 1,
                "top_p": 0.95,
                "top_k": 1,
                "max_output_tokens": 8192,
                "response_mime_type": "text/plain"
            }
        )
        config = load_config()
        api_key_gemini = config.get("api_key_gemini")
        genai.configure(api_key=api_key_gemini)

    @commands.command(name="lm", description="LensMind is a AI that can answer questions and help user with user's problems")
    async def lensmind(self, ctx, *, question: str):
        try:
            if ctx.message.attachments:
                image = ctx.message.attachments[0]
                if image.content_type.startswith("image/"):
                    processing_msg = await ctx.send("Image detected. Processing...")
                    await image.save(image.filename)
                else:
                    await ctx.send("Invalid image format. Please upload a valid image.")
                    return

                file = genai.upload_file(image.filename)
                response = self.model.generate_content([file, question])
                await processing_msg.delete()
            else:
                await ctx.send("No image attached. Please upload an image with your question.")
                return

            embed = nextcord.Embed(
                title="LensMind Response",
                color=0x00ff00,
                timestamp=datetime.datetime.now()
            )
            embed.add_field(name="Question", value=question, inline=False)
            
            # Split long responses into multiple fields
            if len(response.text) > 1024:
                parts = [response.text[i:i+1024] for i in range(0, len(response.text), 1024)]
                for i, part in enumerate(parts, 1):
                    field_name = "Answer" if i == 1 else f"Answer (continued {i})"
                    embed.add_field(name=field_name, value=part, inline=False)
            else:
                embed.add_field(name="Answer", value=response.text, inline=False)

            embed.set_image(url=image.url)
            embed.set_footer(text=f"Asked by {ctx.author.name}", 
                           icon_url=ctx.author.avatar.url if ctx.author.avatar else None)

            await ctx.send(embed=embed)
            os.remove(image.filename)

        except Exception as e:
            await ctx.send(f"An error occurred: {str(e)}")
            return

def setup(bot):
    bot.add_cog(LensMind(bot))
