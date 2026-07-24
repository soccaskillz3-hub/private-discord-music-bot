import discord
from discord.ext import commands
from discord import app_commands

from database.database import is_authorized

import yt_dlp
import asyncio


class Music(commands.Cog):

    def __init__(self, bot):

        self.bot = bot

        # Queue per server
        self.queues = {}


    def get_queue(self, guild_id):

        if guild_id not in self.queues:
            self.queues[guild_id] = []

        return self.queues[guild_id]


    async def play_next(self, guild):

        queue = self.get_queue(guild.id)

        voice = guild.voice_client

        if voice is None:
            return


        if len(queue) == 0:
            return


        song = queue.pop(0)


        ydl_options = {
            "format": "bestaudio/best",
            "quiet": True,
            "noplaylist": True,
            "extractor_args": {
                "youtube": {
                    "player_client": [
                        "android"
                    ]
                }
            }
        }


        try:

            with yt_dlp.YoutubeDL(ydl_options) as ydl:

                info = ydl.extract_info(
                    song["webpage"],
                    download=False
                )

                url = info["url"]


            ffmpeg_options = {
                "before_options": (
                    "-reconnect 1 "
                    "-reconnect_streamed 1 "
                    "-reconnect_delay_max 5"
                ),
                "options": "-vn"
            }


            source = discord.FFmpegPCMAudio(
                url,
                **ffmpeg_options
            )


            def after(error):

                if error:
                    print(
                        "PLAYBACK ERROR:",
                        error
                    )

                asyncio.run_coroutine_threadsafe(
                    self.play_next(guild),
                    self.bot.loop
                )


            voice.play(
                source,
                after=after
            )


        except Exception as e:

            print(
                "PLAY NEXT ERROR:",
                repr(e)
            )

            await self.play_next(guild)



    @app_commands.command(
        name="join",
        description="Join your current voice channel"
    )
    async def join(
        self,
        interaction: discord.Interaction
    ):

        authorized = await is_authorized(
            interaction.user.id
        )


        if not authorized:

            await interaction.response.send_message(
                "❌ You are not authorized.",
                ephemeral=True
            )

            return


        if interaction.user.voice is None:

            await interaction.response.send_message(
                "❌ Join a voice channel first.",
                ephemeral=True
            )

            return


        channel = interaction.user.voice.channel


        if interaction.guild.voice_client:

            await interaction.guild.voice_client.move_to(
                channel
            )

        else:

            await channel.connect()


        await interaction.response.send_message(
            f"🎵 Joined **{channel.name}**"
        )



    @app_commands.command(
        name="play",
        description="Play a YouTube song"
    )
    async def play(
        self,
        interaction: discord.Interaction,
        search: str
    ):


        authorized = await is_authorized(
            interaction.user.id
        )


        if not authorized:

            await interaction.response.send_message(
                "❌ You are not authorized.",
                ephemeral=True
            )

            return



        if interaction.user.voice is None:

            await interaction.response.send_message(
                "❌ Join a voice channel first.",
                ephemeral=True
            )

            return



        voice = interaction.guild.voice_client


        if voice is None:

            await interaction.user.voice.channel.connect()

            voice = interaction.guild.voice_client



        await interaction.response.defer()



        ydl_options = {

            "format": "bestaudio/best",

            "noplaylist": True,

            "quiet": True,

            "default_search": "ytsearch1",

            "extractor_args": {

                "youtube": {

                    "player_client": [
                        "android"
                    ]

                }

            }

        }



        try:

            with yt_dlp.YoutubeDL(
                ydl_options
            ) as ydl:


                info = ydl.extract_info(
                    f"ytsearch1:{search}",
                    download=False
                )


                if (
                    "entries" not in info
                    or len(info["entries"]) == 0
                ):

                    await interaction.followup.send(
                        "❌ No results found."
                    )

                    return



                song = info["entries"][0]



                data = {

                    "title": song["title"],

                    "webpage": song["webpage_url"]

                }



            queue = self.get_queue(
                interaction.guild.id
            )


            queue.append(data)



            if not voice.is_playing():

                await self.play_next(
                    interaction.guild
                )


                await interaction.followup.send(
                    f"▶️ Now playing: **{data['title']}**"
                )


            else:

                await interaction.followup.send(
                    f"✅ Added to queue: **{data['title']}**"
                )



        except Exception as e:

            print(
                "PLAY ERROR:",
                repr(e)
            )

            await interaction.followup.send(
                f"❌ Error: `{e}`"
            )



    @app_commands.command(
        name="queue",
        description="Show the music queue"
    )
    async def queue(
        self,
        interaction: discord.Interaction
    ):


        queue = self.get_queue(
            interaction.guild.id
        )


        if len(queue) == 0:

            await interaction.response.send_message(
                "📭 Queue is empty."
            )

            return



        message = "🎵 Queue:\n"


        for i, song in enumerate(
            queue,
            start=1
        ):

            message += (
                f"{i}. {song['title']}\n"
            )


        await interaction.response.send_message(
            message
        )


    @app_commands.command(
        name="pause",
        description="Pause the current song"
    )
    async def pause(
        self,
        interaction: discord.Interaction
    ):

        voice = interaction.guild.voice_client

        if voice is None or not voice.is_playing():

            await interaction.response.send_message(
                "❌ Nothing is playing."
            )

            return


        voice.pause()

        await interaction.response.send_message(
            "⏸️ Paused."
        )



    @app_commands.command(
        name="resume",
        description="Resume the current song"
    )
    async def resume(
        self,
        interaction: discord.Interaction
    ):

        voice = interaction.guild.voice_client

        if voice is None or not voice.is_paused():

            await interaction.response.send_message(
                "❌ Nothing is paused."
            )

            return


        voice.resume()

        await interaction.response.send_message(
            "▶️ Resumed."
        )



    @app_commands.command(
        name="skip",
        description="Skip the current song"
    )
    async def skip(
        self,
        interaction: discord.Interaction
    ):

        voice = interaction.guild.voice_client

        if voice is None or not voice.is_playing():

            await interaction.response.send_message(
                "❌ Nothing is playing."
            )

            return


        voice.stop()

        await interaction.response.send_message(
            "⏭️ Skipped."
        )



    @app_commands.command(
        name="stop",
        description="Stop music and clear queue"
    )
    async def stop(
        self,
        interaction: discord.Interaction
    ):

        voice = interaction.guild.voice_client


        if voice:

            voice.stop()


        self.queues[
            interaction.guild.id
        ] = []


        await interaction.response.send_message(
            "⏹️ Stopped and cleared queue."
        )



    @app_commands.command(
        name="leave",
        description="Leave the voice channel"
    )
    async def leave(
        self,
        interaction: discord.Interaction
    ):

        voice = interaction.guild.voice_client


        if voice:

            await voice.disconnect()


        await interaction.response.send_message(
            "👋 Left the voice channel."
        )

print("Music commands loaded!")


async def setup(bot):

    await bot.add_cog(Music(bot))
