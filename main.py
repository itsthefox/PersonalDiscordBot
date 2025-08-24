import os
import re
import logging
import discord
from discord.ext import commands
from discord import app_commands
from dotenv import load_dotenv

# ---------- config ----------
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
SECRET_ROLE_NAME = "sigma"

TEST_GUILD_ID = 1408705057574223997  
TEST_GUILD = discord.Object(id=TEST_GUILD_ID) if TEST_GUILD_ID else None

# ---------- logging ----------
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")

# ---------- intents ----------
intents = discord.Intents.default()
intents.message_content = True     
intents.members = True             

# ---------- bot ----------
bot = commands.Bot(command_prefix="fox", intents=intents)

# ---------- ready/sync ----------
@bot.event
async def on_ready():
    try:
        if TEST_GUILD:
            synced = await bot.tree.sync(guild=TEST_GUILD)
        else:
            synced = await bot.tree.sync()
        print(f"Logged in as {bot.user} | Synced {len(synced)} app command(s)")
    except Exception as e:
        print(f"Error syncing commands: {e}")

@bot.command()
@commands.is_owner()
async def sync(ctx):
    if TEST_GUILD:
        await bot.tree.sync(guild=TEST_GUILD)
    else:
        await bot.tree.sync()
    await ctx.send("✅ Slash commands synced.")

# ---------- slash commands ----------
# /hello
if TEST_GUILD:
    @bot.tree.command(name="hello", description="Say hello!", guild=TEST_GUILD)
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.name}!", ephemeral=True)
else:
    @bot.tree.command(name="hello", description="Say hello!")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.name}!", ephemeral=True)

# /ban
def _ban_command_decorators(func):
    func = app_commands.guild_only()(func)
    func = app_commands.default_permissions(ban_members=True)(func)
    func = app_commands.describe(
        member="Member to ban (if still in the server)",
        user_id="User ID if they already left",
        reason="Reason for ban"
    )(func)
    return func

async def _ban_impl(interaction: discord.Interaction, member: discord.Member | None, user_id: str | None, reason: str):
    await interaction.response.defer(ephemeral=True)

    if not member and not user_id:
        return await interaction.followup.send("Provide either a member or a numeric user_id bro", ephemeral=True)

    if member is not None:
        target = member
        mention = member.mention
    else:
        if not user_id.isdigit():
            return await interaction.followup.send("user_id must be numeric smh", ephemeral=True)
        target = discord.Object(id=int(user_id))
        mention = f"<@{user_id}>"

    try:
        await interaction.guild.ban(target, reason=reason)
        await interaction.followup.send(f"OBLITERATING {mention}\nBECAUSE: **{reason}**", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("i need the perms chud", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"HTTP error while banning: `{e}`", ephemeral=True)

if TEST_GUILD:
    @_ban_command_decorators
    @bot.tree.command(name="ban", description="Ban a kid fr", guild=TEST_GUILD)
    async def ban(interaction: discord.Interaction, member: discord.Member | None = None, user_id: str | None = None, reason: str = "Reason not specified."):
        await _ban_impl(interaction, member, user_id, reason)
else:
    @_ban_command_decorators
    @bot.tree.command(name="ban", description="Ban a kid fr")
    async def ban(interaction: discord.Interaction, member: discord.Member | None = None, user_id: str | None = None, reason: str = "Reason not specified."):
        await _ban_impl(interaction, member, user_id, reason)

@ban.error
async def ban_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    send = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
    if isinstance(error, app_commands.MissingPermissions):
        await send("You don’t have the perms lil bro.", ephemeral=True)
    elif isinstance(error, app_commands.CheckFailure):
        await send("This command can only be used in a server idiot", ephemeral=True)
    elif isinstance(error, app_commands.CommandInvokeError):
        await send(f"Command failed: `{error.__cause__}`", ephemeral=True)
    else:
        await send(f"Unexpected error: `{error}`", ephemeral=True)

# ---------- member join ----------
@bot.event
async def on_member_join(member: discord.Member):
    try:
        await member.mention(f"wsg {member.name}")
    except discord.Forbidden:
        pass 

# ---------- message filter + prefix commands ----------
@bot.event # filter
async def on_message(message: discord.Message):
    if message.author.bot:
        return
    if "faggot" in message.content.lower():
        try:
            await message.delete()
            await message.channel.send(f"{message.author.mention} syfm")
        except discord.Forbidden:
            pass
    await bot.process_commands(message)

@bot.command() # hello
async def hello(ctx: commands.Context):
    await ctx.send(f"hello {ctx.author.mention}")

@bot.command() # assign
async def assign(ctx: commands.Context):
    role = discord.utils.get(ctx.guild.roles, name=SECRET_ROLE_NAME)
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{SECRET_ROLE_NAME} has been given to {ctx.author.mention}")

@bot.command() # remove
async def remove(ctx: commands.Context):
    role = discord.utils.get(ctx.guild.roles, name=SECRET_ROLE_NAME)
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"{SECRET_ROLE_NAME} has been removed from {ctx.author.mention}")

@bot.command() # secret
@commands.has_role(SECRET_ROLE_NAME)
async def secret(ctx: commands.Context):
    await ctx.send("everyone stfu a sigma is talking")

@secret.error
async def secret_error(ctx: commands.Context, error: commands.CommandError):
    if isinstance(error, commands.MissingRole):
        await ctx.send("bro ur not sigma lmao gtfo")

@bot.command() # dm
async def dm(ctx: commands.Context, *, msg: str):
    try:
        await ctx.author.send(f"bro rlly said '{msg}'")
    except discord.Forbidden:
        await ctx.send("I can't DM you, your DMs are closed.")

@bot.command() # reply
async def reply(ctx: commands.Context):
    await ctx.reply("replied to your message")

@bot.command() # poll
async def poll(ctx: commands.Context, *, question: str):
    embed = discord.Embed(title="New Poll!!!!!!", description=question)
    poll_message = await ctx.send(embed=embed)
    for emoji in ("🦊", "🥀"):
        await poll_message.add_reaction(emoji)

# ---------- run ----------
bot.run(TOKEN, log_handler=handler, log_level=logging.DEBUG)
