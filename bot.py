import os
import spotify
import discord
import requests
import json
import threading
import dotenv
from dotenv import load_dotenv
from discord.ext import commands
import file_manager

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="#", help_command=None)
client = spotify.Client()

redirect_uri = "http://127.0.0.1:8000/callback"
auth_manager = spotify.AuthManager(redirect_uri)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')


@bot.command(name='join')
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
        searched_expression = "+".join(args)
        song_info = client.find(searched_expression)
        song = spotify.Song(song_info[0], song_info[1], song_info[2])
        
    except:
        await ctx.send("Sorry, I couldn't find anything...")

    embed = discord.Embed(title=song.name, description=f"from {song.album} by {song.artist}", url=client.name_to_query(song.name, song.artist))
    await ctx.send(embed=embed)

@bot.command(name='login')
async def login(ctx):
    token_refresher = spotify.TokenRefresher()
    tmp_manager = file_manager.Manager("tmp.txt")

    if tmp_manager.file_exists():
        tmp_manager.delete_file()
        
    request = auth_manager.create_auth_request()
    embed = discord.Embed(title="Link", url=request)

    await ctx.send(embed=embed)
    code = tmp_manager.read_file()

    if code == "Not Generated":
        while tmp_manager.read_file() == "Not Generated":
            continue
        code = tmp_manager.read_file()

    if tmp_manager.file_exists():
        tmp_manager.delete_file()
        
    response = json.loads(auth_manager.get_tokens(code).text)
    token_expiration = response["expires_in"]
    token_refresher.start_refresh_cycle(token_expiration)

    dotenv_file = dotenv.find_dotenv()
    dotenv.load_dotenv(dotenv_file)

    dotenv.set_key(dotenv_file, 'ACCESS_TOKEN', response['access_token'])
    dotenv.set_key(dotenv_file, 'REFRESH_TOKEN', response["refresh_token"])


@bot.command(name='playlists')
async def playlists(ctx):
    load_dotenv()
    access_token = os.getenv('ACCESS_TOKEN')

    user_playlists = json.loads(client.get_user_playlists(access_token).text)

    for item in user_playlists["items"]:
        await ctx.send(item["name"])


@bot.command(name="play")
async def play(ctx, *args):
    load_dotenv()
    access_token = os.getenv('ACCESS_TOKEN')
    playlist_name = " ".join(args)
    user_playlists = json.loads(client.get_user_playlists(access_token).text)
    selected_playlist = client.playlist_exists(user_playlists, playlist_name)

    if selected_playlist:
        playlist_id = selected_playlist[0]
        playlist_name = selected_playlist[1]
        await ctx.send(f"Playing {playlist_name}")
    else:
        await ctx.send("Sorry, couldn't find that playlist...")

    items = json.loads(client.get_playlist(access_token, playlist_id).text)
    playlist = client.create_playlist(playlist_name, items)

    for item in playlist.items:
        embed = discord.Embed(title=item.name, description=f"from {item.album} by {item.artist}", url=client.name_to_query(item.name, item.artist))
        await ctx.send(embed=embed)


bot.run(TOKEN)

