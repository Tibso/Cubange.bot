from nextcord.ext import commands
from os import getenv, listdir
from dotenv import load_dotenv

load_dotenv('token.env')

GUILD_IDS = [637782002145165342]

bot = commands.Bot()

for filename in listdir('./cogs'):
    if filename.endswith('.py'):
        bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print(f"Connected to Discord as: {bot.user}")

bot.run(getenv('CUBANGE_BOT_TOKEN'))