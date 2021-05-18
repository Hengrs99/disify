import os
import asyncio
import discord
import json
import random

from dotenv import load_dotenv
from discord.ext import commands
from gtts import gTTS

import spotify
import audio_streaming
import file_manager
import user


load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='#', help_command=None)
client = spotify.Client()
users = {}

redirect_uri = 'http://127.0.0.1:5000/callback'


@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to Discord!")


@bot.command(name='connect')
async def connect(ctx):
    try:
        channel = ctx.author.voice.channel
        await channel.connect()
        await ctx.send(f"Connected to {channel.name}")
    except AttributeError:
        await ctx.send("You need to connect to the voice channel before asking for my presence!")


@bot.command(name='leave')
async def leave(ctx):
    try:
        await ctx.voice_client.disconnect()
    except AttributeError:
        await ctx.send("I'm not connected to any channel you could kick me out of!")


@bot.command(name='find')
async def find(ctx, *args):
    try:
        searched_expression = '+'.join(args)
        song_info = client.find(searched_expression)
        song = spotify.Song(song_info[0], song_info[1], song_info[2])
        
    except:
        await ctx.send("Sorry, I couldn't find anything...")

    embed = discord.Embed(title=song.name, description=f"from {song.album} by {song.artist}", url=client.name_to_query(song.name, song.artist))
    await ctx.send(embed=embed)


@bot.command(name='login')
async def login(ctx):
    auth_manager = spotify.AuthManager(redirect_uri)
    token_refresher = spotify.TokenRefresher()
    tmp_manager = file_manager.Manager('tmp.txt')

    if tmp_manager.file_exists():
        tmp_manager.delete_file()
        
    request = auth_manager.create_auth_request()
    embed = discord.Embed(title='Link', url=request)

    await ctx.send(embed=embed)
    code = tmp_manager.read_file()

    if code == 'Not Generated':
        while tmp_manager.read_file() == 'Not Generated':
            continue
        code = tmp_manager.read_file()

    if tmp_manager.file_exists():
        tmp_manager.delete_file()
        
    tokens = json.loads(auth_manager.get_tokens(code).text)

    access_token = tokens['access_token']
    refresh_token = tokens['refresh_token']

    this_user = user.User(access_token, refresh_token)
    user_id = ctx.message.author.id
    users[user_id] = this_user

    token_expiration = tokens['expires_in']
    token_refresher.start_refresh_cycle(token_expiration, this_user)


@bot.command(name='playlists')
async def playlists(ctx):
    user_id = ctx.message.author.id
    access_token = users[user_id].access_token

    user_playlists = json.loads(client.get_user_playlists(access_token).text)

    for item in user_playlists['items']:
        await ctx.send(item['name'])


@bot.command(name='play')
async def play(ctx, *args):
    guild = ctx.message.guild
    voice_client = guild.voice_client
        
    user_id = ctx.message.author.id
    access_token = users[user_id].access_token
    audio_finder = spotify.AudioFinder()

    playlist_name = ' '.join(args).lower()
    user_playlists = json.loads(client.get_user_playlists(access_token).text)
    selected_playlist = client.playlist_exists(user_playlists, playlist_name)

    if selected_playlist:
        playlist_id = selected_playlist['id']
        playlist_name = selected_playlist['name']
        await ctx.send(f"Playing {playlist_name}")
    else:
        await ctx.send("Sorry, couldn't find that playlist...")

    items = json.loads(client.get_playlist(access_token, playlist_id).text)
    playlist = client.create_playlist(playlist_name, items)
    random.shuffle(playlist.items)

    for item in playlist.items:
        url = audio_finder.find_url(item)
        embed = discord.Embed(title=item.name, description=f"from {item.album} by {item.artist}", url=client.name_to_query(item.name, item.artist))

        player = await audio_streaming.YTDLSource.from_url(url, loop=bot.loop, stream=True)
        ctx.voice_client.play(player)

        await ctx.send(embed=embed)      

        while voice_client.is_playing():
            await asyncio.sleep(1)


@bot.command(name='say')
async def say(ctx, *args):
    guild = ctx.guild
    voice_client = guild.voice_client
    text = ' '.join(args)
    language = 'en'

    sound_manager = gTTS(text=text, lang=language, slow=False)
    sound_manager.save('sound.mp3')

    audio_source = discord.FFmpegPCMAudio('sound.mp3')
    voice_client.play(audio_source, after=None)

    while voice_client.is_playing():
        await asyncio.sleep(1)
    os.remove('sound.mp3')


bot.run(TOKEN)
