import discord
from discord.ext import commands
from discord.ext.commands import Bot
import asyncio
import json

with open("botinfo.json", "r") as f:
    data = json.load(f)
    TOKEN = data["token"]

bot = commands.Bot(command_prefix="!")

@bot.event
async def on_ready():
    print("Bot Online!\n")


bot.run(TOKEN)