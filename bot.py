import os
import spotify
import discord
import requests
import json
from dotenv import load_dotenv
from discord.ext import commands
import functions

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

    embed = discord.Embed(title=song.name, description=f"from {song.album} by {song.artist}", url=functions.name_to_query(song.name, song.artist))
    await ctx.send(embed=embed)

@bot.command(name='login')
async def login(ctx):
    if functions.tmp_exists():
        os.remove('tmp.txt')
    
    request = auth_manager.create_auth_request()
    embed = discord.Embed(title="Link", url=request)

    await ctx.send(embed=embed)
    code = functions.read_tmp()

    if code == "Not Generated":
        while functions.read_tmp() == "Not Generated":
            continue
        code = functions.read_tmp()

    if functions.tmp_exists():
        os.remove('tmp.txt')
        
    response = json.loads(auth_manager.get_tokens(code).text)

    os.environ['ACCESS_TOKEN'] = response["access_token"]
    os.environ['REFRESH_TOKEN'] = response["refresh_token"]


@bot.command(name='playlists')
async def playlists(ctx):
    access_token = os.getenv('ACCESS_TOKEN')
    refresh_token = os.getenv('REFRESH_TOKEN')

    user_data = json.loads(client.get_user_profile(access_token).text)

    try:
        id = user_data['id']
    except KeyError:
        if user_data['error']['status'] == '401':
            access_token = auth_manager.get_new_token(refresh_token)
            user_data = json.loads(client.get_user_profile(access_token).text)
            id = user_data['id']
        else:
            id = "error"
            await ctx.send("Sorry, something went wrong...")

    print(id)

bot.run(TOKEN)

