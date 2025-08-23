import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='fox', intents=intents)

secretrole = "sigma" 

@bot.event
async def on_ready():
    print(f"Online and operational, {bot.user.name}")

@bot.event
async def on_member_join(member):
    await member.send(f"You have arrived to the server {member.name}")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if "faggot" in message.content.lower():
        await message.delete()
        await message.channel.send(f"{message.author.mention} syfm")
    await bot.process_commands(message)

@bot.command()
async def hello(ctx):
    await ctx.send(f"hello {ctx.author.mention}")

@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secretrole)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{secretrole} has been given to {ctx.author.mention}")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name=secretrole)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{secretrole} has been removed from {ctx.author.mention}")

@bot.command()
@commands.has_role(secretrole)
async def secret(ctx):
    await ctx.send("everyone stfu a sigma is talking")

@secret.error
async def secret_error(ctx,error):
    if isinstance(error, commands.MissingRole):
        await ctx.send("bro ur not sigma lmao gtfo")

@bot.command()
async def dm(ctx, *, msg):
    await ctx.author.send(f"bro rlly said '{msg}'")

@bot.command()
async def reply(ctx):
    await ctx.reply("replied to your message")

@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("🦊")
    await poll_message.add_reaction("🥀")

bot.run(token, log_handler=handler, log_level=logging.DEBUG)