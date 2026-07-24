import discord
import asyncio
from discord.ext import commands

from config import TOKEN
from database.database import initialize_database


# Load Opus for Discord voice
discord.opus.load_opus(
    "/opt/homebrew/opt/opus/lib/libopus.dylib"
)

print("OPUS LOADED:", discord.opus.is_loaded())


intents = discord.Intents.all()

intents.message_content = True
intents.members = True
intents.voice_states = True


bot = commands.Bot(
    command_prefix="!",
    intents=intents
)


@bot.event
async def on_message(message):

    if message.author == bot.user:
        return

    await bot.process_commands(message)



@bot.event
async def on_ready():

    print(f"Logged in as {bot.user}")

    await initialize_database()

    synced = await bot.tree.sync()

    print(f"Synced {len(synced)} command(s)")



@bot.tree.command(name="ping")
async def ping(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "Pong!"
    )



async def main():

    await bot.load_extension(
        "cogs.owner"
    )

    await bot.load_extension(
        "cogs.music"
    )

    print("Owner commands loaded!")

    await bot.start(TOKEN)



asyncio.run(main())
