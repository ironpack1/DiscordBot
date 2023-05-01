from discord.ext import commands, tasks
from discord.utils import get
from dataclasses import dataclass
from discord import FFmpegPCMAudio
import yt_dlp
import discord
import asyncio
import config

BOT_TOKEN = config.password

queue = {}
bot = commands.Bot(command_prefix="i!", intents=discord.Intents.all())
user_id = None

#Starting up the bot
@bot.event
async def on_ready():
    print("Bot is ready")

#Join and Leave voice
@bot.command()
async def join(ctx):
    if not ctx.author.voice:
        await ctx.send("You must be connected to a voice channel to use this command.")
        return

    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()
        await ctx.send(f"Joined {voice_channel.name}.")
    else:
        await ctx.voice_client.move_to(voice_channel)
        await ctx.send(f"Moved to {voice_channel.name}.")

@bot.command()
async def leave(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not connected to a voice channel.")
    else:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")

#El Musica
@bot.command()
async def skip(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        voice_client.stop()

async def play_audio(ctx):
    guild_id = ctx.guild.id
    voice_client = ctx.voice_client

    if not queue[guild_id]:  # If the queue is empty, stop the player
        return

    # Get the next audio source from the queue
    audio_url = queue[guild_id].pop(0)

    def after_playing(error):
        if error:
            print(f"Error: {error}")
        # Schedule the next audio playback
        asyncio.run_coroutine_threadsafe(play_audio(ctx), bot.loop)

    audio_source = discord.FFmpegPCMAudio(audio_url, options='-bufsize 64k')  # Increase the buffer size
    voice_client.audio_source = audio_source  # Store the audio_source in voice_client
    voice_client.play(audio_source, after=after_playing)


@bot.command()
async def play(ctx, *query):
    search_query = " ".join(query)
    voice_channel = ctx.author.voice.channel
    voice_client = ctx.voice_client

    if not voice_client:
        voice_client = await voice_channel.connect()
    else:
        await voice_client.move_to(voice_channel)

    ydl_opts = {
        'format': 'bestaudio/best',
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"ytsearch:{search_query}", download=False)
        video = info['entries'][0]
        audio_url = video.get('url', None)

    # Add the audio URL to the guild's queue
    guild_id = ctx.guild.id
    if guild_id not in queue:
        queue[guild_id] = []
    queue[guild_id].append(audio_url)

    if not voice_client.is_playing():
        await play_audio(ctx)

@bot.command()
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client:
        voice_client.stop()

bot.run(BOT_TOKEN)