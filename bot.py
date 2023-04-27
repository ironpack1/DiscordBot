from discord.ext import commands, tasks
from discord.utils import get
from dataclasses import dataclass
from discord import FFmpegPCMAudio
import discord
import random
import os
import asyncio
import json

BOT_TOKEN = ''
CHANNEL_ID = 963701604970811432

channel_mover_active = False
on_death: discord.VoiceChannel
default_voice: discord.VoiceChannel = None
current_sound = "pipe.mp3"
bot = commands.Bot(command_prefix="i!", intents=discord.Intents.all())
user_id = None

@bot.event
async def on_ready():
    print("Bot is ready")

def on_error(error):
        print(f"An error occurred while playing audio: {error}")
def find_voice_channel(ctx, server_name):
    return discord.utils.get(ctx.guild.voice_channels, name=server_name)

@bot.command()
async def set_move(ctx, server_name):
    global on_death
    voice_channel = find_voice_channel(ctx, server_name)
    if voice_channel:
        on_death = voice_channel
        await ctx.send(f"Voice channel found, {voice_channel.name}")
    else:
        await ctx.send("Voice channel not found")

@bot.command()
async def set_default(ctx, server_name):
    global default_voice
    voice_channel = find_voice_channel(ctx, server_name)
    if voice_channel:
        default_voice = voice_channel
        await ctx.send(f"Voice channel found, {voice_channel.name}")
    else:
        await ctx.send("Voice channel not found")

@bot.command()
async def toggle(ctx):
    global channel_mover_active
    if channel_mover_active:
        user_move_loop.stop()
        channel_mover_active = False
        await ctx.send("League mover is now off")
    else:
        user_move_loop.start()
        channel_mover_active = True
        await ctx.send("League mover is now on")

@bot.command()
async def join_vc(ctx):
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
async def leave_vc(ctx):
    if ctx.voice_client is None:
        await ctx.send("I am not connected to a voice channel.")
    else:
        await ctx.voice_client.disconnect()
        await ctx.send("Disconnected from the voice channel.")

@bot.command()
async def break_silence(ctx):
    global user_id
    await ctx.send("Playing sound at random intervals")
    user_id = ctx.author.id
    silence_broken_up.start()
@bot.command()
async def keep_silence(ctx):
    silence_broken_up.stop()
    await ctx.send("Stopped playing sounds")


@bot.command()
async def sound(ctx, to_play):
    if not ctx.author.voice:
            await ctx.send("You must be connected to a voice channel to use this command.")
            return

    voice_channel = ctx.author.voice.channel
    if ctx.voice_client is None:
        await voice_channel.connect()

    voice_client = ctx.voice_client

    # Construct the absolute path to the audio file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, "sounds", to_play + ".mp3")

    if not os.path.exists(audio_path):
        await ctx.send(f"Audio file not found: {audio_path}")
        return

    if not voice_client.is_playing():
        audio_source = FFmpegPCMAudio(audio_path)
        voice_client.play(audio_source, after=on_error)
        await ctx.send(f"Playing sound in {voice_channel.name}.")
        print(f"Playing {audio_path} in {voice_channel.name}.")
    else:
        await ctx.send("I am already playing a sound in the voice channel.")
        print("Already playing a sound in the voice channel.")

@bot.command()
async def set_sound(ctx, to_play):
    global current_sound
    try:
        current_sound = ""
        channel = bot.get_channel(CHANNEL_ID)
        current_sound += to_play + ".mp3"
        await channel.send("Sound set to " + current_sound)
    except Exception as e:
        await channel.send("Unexpected Error")

@tasks.loop(seconds=1)
async def user_move_loop():
    if not default_voice:
        return

    try:
        global on_death
        channel = bot.get_channel(CHANNEL_ID)

        with open('./venv/data.json', 'r') as file:
            summoner_data = json.load(file)

        for summoner in summoner_data:
            discord_name = summoner['discordName']
            member = channel.guild.get_member_named(discord_name)
            if member:
                target_channel = on_death if summoner['isDead'] else default_voice
                await member.move_to(target_channel)
            else:
                print(f"Member not found with name {discord_name}")

    except Exception as e:
        print(f"Error in user_move_loop: {e}")
        pass


@tasks.loop(seconds = 1)
async def silence_broken_up():
    global user_id
    global current_sound

    if user_id is None:
        return

    channel = bot.get_channel(CHANNEL_ID)
    user = channel.guild.get_member(user_id)

    if user.voice is None:
        return

    voice_channel = user.voice.channel
    voice_client = voice_channel.guild.voice_client

    time_to_play = random.randint(0, 600)

    if voice_client is None or not voice_client.is_connected():
        await voice_channel.connect()
        voice_client = voice_channel.guild.voice_client

    print(f"Sound will play in {time_to_play} seconds")
    await asyncio.sleep(time_to_play)

    # Construct the absolute path to the audio file
    script_dir = os.path.dirname(os.path.abspath(__file__))
    audio_path = os.path.join(script_dir, "sounds", current_sound)

    if not os.path.exists(audio_path):
        await channel.send(f"Audio file not found: {audio_path}")
        return

    if not voice_client.is_playing():
        audio_source = FFmpegPCMAudio(audio_path)
        voice_client.play(audio_source, after=on_error)
        print(f"Playing {audio_path} in {voice_channel.name}.")
    else:
        print("Already playing a sound in the voice channel.")



bot.run(BOT_TOKEN)
