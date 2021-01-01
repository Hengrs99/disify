import os
import spotify
import discord
import requests
from dotenv import load_dotenv
from discord.ext import commands
import functions

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix="#", help_command=None)
client = spotify.Client()


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
    os.remove('tmp.txt')
    request = "https://accounts.spotify.com/authorize?client_id=" + client.cid + "&" + "response_type=code" + "&" + "scope=playlist-read-private+playlist-read-collaborative+user-library-read" "&" + "redirect_uri=http://127.0.0.1:8000/callback"
    embed = discord.Embed(title="Link", url=request)
    await ctx.send(embed=embed)
    code = functions.read_tmp()
    if code == "":
        while functions.read_tmp() == "":
            continue
        code = functions.read_tmp()
    await ctx.send(code)

bot.run(TOKEN)