# main.py
import nextcord
import datetime
from nextcord.ext import commands
from nextcord import SyncWebhook

from assets.utils.config_loader import load_config


config = load_config()
TOKEN = config.get("bot_token")
webhook_url = config.get("webhook_url")


intents = nextcord.Intents.default()
intents.message_content = True
intents.members = True
bot = commands.Bot(command_prefix=["?"], intents=intents)


if webhook_url:
    webhook = SyncWebhook.from_url(webhook_url)
else:
    webhook = None

date = datetime.date.today()


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(
        activity=nextcord.Streaming(
            name="/help | rlyaa.xyz",
            url="https://youtu.be/sVaQQRx6-es?si=WddbMqrjlhmF6kF8",
        )
    )
    print("Bot is ready!")


bot.load_extension("commands.moderation")
bot.load_extension("commands.utility")
bot.load_extension("commands.role_managements")
bot.load_extension("events.message_events")
bot.load_extension("commands.basic_commands")
bot.load_extension("commands.warn_system")
bot.load_extension("commands.afk_system")
bot.load_extension("interactions.info")
bot.load_extension("commands.slashgc")
bot.load_extension("interactions.gc")
bot.load_extension("interactions.afk")
bot.load_extension("interactions.clear")
bot.load_extension("commands.slashstick")
bot.load_extension("events.on_join_events")
bot.load_extension("commands.welcome")
bot.load_extension("AI.summarizer")
bot.load_extension("AI.LenMinds")
bot.load_extension("AI.AI_interaction")
bot.load_extension('commands.admin')

if __name__ == "__main__":
    bot.run(TOKEN)
