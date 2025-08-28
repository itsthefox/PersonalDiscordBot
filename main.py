import os
import re
import logging
import discord
import datetime
from discord.ext import commands
from discord import app_commands
from discord.app_commands import checks
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
        await bot.change_presence(activity=discord.Streaming(name="Follow Foxx on Twitch!", url="https://twitch.tv/itsthefox_"))
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

# ---------- slash command decorators ----------
# /hello
if TEST_GUILD:
    @bot.tree.command(name="hello", description="Say hello!", guild=TEST_GUILD)
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.name}!", ephemeral=True)
else:
    @bot.tree.command(name="hello", description="Say hello!")
    async def hello(interaction: discord.Interaction):
        await interaction.response.send_message(f"Hello, {interaction.user.name}!", ephemeral=True)

# /ban decorator
def ban_decorators(func):
    func = app_commands.guild_only()(func)
    func = checks.has_permissions(ban_members=True)(func)
    func = app_commands.default_permissions(ban_members=True)(func)
    func = app_commands.describe(
        member="Member to ban (if still in the server)",
        user_id="User ID if they already left",
        reason="Reason for ban"
    )(func)
    return func

async def ban_impl(interaction: discord.Interaction, member: discord.Member | None, user_id: str | None, reason: str):
    await interaction.response.defer(ephemeral=True)

    if not member and not user_id:
        return await interaction.followup.send("gimme either a member or a numeric user_id bro", ephemeral=True)

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

# /kick decorator
def kick_decorators(func):
    func = app_commands.default_permissions(kick_members=True)(func)
    func = app_commands.describe(
        member = "Member to kick",
        reason = "Reason for kicking"
    )(func)
    return func

async def kick_impl(interaction: discord.Interaction, member: discord.Member | None, reason: str):
    await interaction.response.defer(ephemeral=True)

    if not member:
        return await interaction.followup.send("gimme a member to kick bro", ephemeral=True)

    if member is not None:
        target = member
        mention = member.mention
    else: 
        pass

    try:
        await interaction.guild.ban(target, reason=reason)
        await interaction.followup.send(f"PUNTING {mention}\nBECAUSE: **{reason}**", ephemeral=True)
    except discord.Forbidden:
        await interaction.followup.send("i need the perms chud", ephemeral=True)
    except discord.HTTPException as e:
        await interaction.followup.send(f"HTTP error while banning: `{e}`", ephemeral=True)

# ----------- slash commands ---------- #

# /ban
if TEST_GUILD:
    @bot.tree.command(name="ban", description="Ban a kid fr", guild=TEST_GUILD)
    @ban_decorators
    async def ban(interaction: discord.Interaction, member: discord.Member | None = None, user_id: str | None = None, reason: str = "Reason not specified."):
        await ban_impl(interaction, member, user_id, reason)
else:
    @bot.tree.command(name="ban", description="Ban a kid fr")
    @ban_decorators
    async def ban(interaction: discord.Interaction, member: discord.Member | None = None, user_id: str | None = None, reason: str = "Reason not specified."):
        await ban_impl(interaction, member, user_id, reason)

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

# /kick
if TEST_GUILD:
    @bot.tree.command(name="kick", description="Kick they ahh from the server", guild=TEST_GUILD)
    @kick_decorators
    async def kick(interaction: discord.Interaction, member: discord.Member | None = None, reason: str = "Reason not specified."):
        await kick_impl(interaction, member, reason)
else:
    @bot.tree.command(name="kick", description="Kick they ahh from the server")
    @kick_decorators
    async def kick(interaction: discord.Interaction, member: discord.Member | None = None, reason: str = "Reason not specified."):
        await kick_impl(interaction, member, reason)

@kick.error
async def kick_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    send = interaction.followup.send if interaction.response.is_done() else interaction.response.send_message
    if isinstance(error, app_commands.MissingPermissions):
        await send("You don’t have the perms lil bro.", ephemeral=True)
    elif isinstance(error, app_commands.CheckFailure):
        await send("This command can only be used in a server idiot", ephemeral=True)
    elif isinstance(error, app_commands.CommandInvokeError):
        await send(f"Command failed: `{error.__cause__}`", ephemeral=True)
    else:
        await send(f"Unexpected error: `{error}`", ephemeral=True)

# /foxxinfo
if TEST_GUILD:
    @bot.tree.command(name="foxx info", description="Learn where to find itsthefox_, the bot owner and creator.", guild=TEST_GUILD)
    async def foxxinfo(ctx: commands.Context):
        twitch = "https://www.twitch.tv/itsthefox_"
        youtube = "https://www.twitch.tv/itsthefox_"
        github = "https://github.com/itsthefox"
        twitter = "https://x.com/itsthefoxFPS"
        discord = "@itsthefox_"
        embed = discord.Embed(
            title="Where to Find itsthefox_",
            description="The bot owner can be found in the links below!",
            color= discord.Color.from_rgb(247, 4, 93),
            timestamp=datetime.datetime
        )
        embed.add_field(name="Socials", value=f"Twitch: {twitch}\nYouTube: {youtube}\nGitHub: {github}\nTwitter: {twitter}\n Discord: {discord}", inline=False)
        embed.set_footer(text="Come find me-")
        await ctx.send(embed=embed)

else:
    @bot.tree.command(name="foxx info", description="Learn where to find itsthefox_, the bot owner and creator.")
    async def foxxinfo(ctx: commands.Context):
        twitch = "https://www.twitch.tv/itsthefox_"
        youtube = "https://www.twitch.tv/itsthefox_"
        github = "https://github.com/itsthefox"
        twitter = "https://x.com/itsthefoxFPS"
        discord = "@itsthefox_"
        embed = discord.Embed(
            title="Where to Find itsthefox_",
            description="The bot owner can be found in the links below!",
            color= discord.Color.from_rgb(247, 4, 93),
            timestamp=datetime.datetime
        )
        embed.add_field(name="Socials", value=f"Twitch: {twitch}\nYouTube: {youtube}\nGitHub: {github}\nTwitter: {twitter}\n Discord: {discord}", inline=False)
        embed.set_footer(text="Come find me...")
        await ctx.send(embed=embed)

# ---------- member join ----------

@bot.event
async def on_member_join(member: discord.Member):
    try:
        await member.mention(f"wsg {member.name}.")
    except discord.Forbidden:
        pass 
# ---------- member leave -----------
@bot.event
async def on_member_leave(member:discord.Member):
    try:
        await member.mention(f"{member.name} has left the server, bum ass")
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
