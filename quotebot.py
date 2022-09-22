from tube_dl import Youtube, extras
import discord
from discord.ext import commands
import asyncio
import glob
import ffmpeg
import random
import time
import youtube_dl
import os
from shutil import copyfile

token = os.environ.get("QUOTEBOT_TOKEN")

def init():
    client = commands.Bot(command_prefix='!', intents=discord.Intents.all())
    client.vc = None
    nbquotes = 0
    quotes=[]

    # Load greets quotes and users
    try:
        file = open('quotes/greets.txt', 'r')
        greetids = next(file)[:-1].split(',')
        greetquotes = next(file)[:-1].split(',')
        file.close()
    except (FileNotFoundError) as e:
        greetids = []
        greetquotes = []
    jointime = [0 for x in greetids]



    # Search for quotes in quotes folder
    while True:
        nbquotes += 1
        quoteNames = glob.glob('./quotes/'+str(nbquotes)+' *.mp3')
        if len(quoteNames) == 0:
            nbquotes -= 1
            break
        for fileName in quoteNames:
            quotes.append(fileName)

        @client.command(name=str(nbquotes))
        async def _(ctx):
            channel = ctx.author.voice.channel
            await playaudios([quotes[int(ctx.command.name)-1]], channel)

        def find(string):
            for str in quotes:
                if(str.lower().find(string.lower()) != -1):
                    return str
            return

    @client.event
    async def on_ready():
        client.lock = asyncio.Lock()

    async def playaudios(audioList, targetChannel):
        if (targetChannel is None):
            return
        try:
            await asyncio.wait_for(client.lock.acquire(), timeout=10)
            if(client.vc != None and client.vc.channel != targetChannel):
                await client.vc.disconnect()
            if(client.vc == None):
                client.vc = await targetChannel.connect()
            for audio in audioList:
                client.vc.play(discord.FFmpegPCMAudio(audio)) 
                while client.vc.is_playing():
                    await asyncio.sleep(1)
            client.lock.release()
        except asyncio.TimeoutError:
            print('Quote timed out')

    @client.command()
    async def addgreet(ctx, quote):
        fullquote = './quotes/' + quote + '.mp3'
        if fullquote not in quotes:
            await ctx.channel.send('Quote not found. The name shouldnt include the folder or .mp3')
        else:
            try:
                index = greetids.index(ctx.author.id)
                greetquotes[index] = fullquote
                jointime[index] = 0
            except ValueError:
                greetquotes.append(fullquote)
                greetids.append(ctx.author.id)
                jointime.append(0)

            with open('quotes/greets.txt', 'w') as file:
                file.write(','.join([str(id) for id in greetids]) + '\n')
                file.write(','.join(greetquotes))
            await ctx.channel.send(quote + ' added as greeting quote')

    @client.command()
    async def rmgreet(ctx):
        try:
            index = greetids.index(ctx.author.id)
            greetids.pop(index)
            greetquotes.pop(index)
            jointime.pop(index)
            with open('quotes/greets.txt', 'w') as file:
                file.write(','.join((str(id) for id in greetids)) + '\n')
                file.write(','.join(greetquotes))
            await ctx.channel.send('Greet removed')
        except ValueError:
            await ctx.channel.send('No greet added')


    @client.command()
    async def list(ctx):
        if(len(quotes) == 0):
            await ctx.channel.send("No quotes")
        for i in range(len(quotes)//50+1):
            listn = ''
            for x in quotes[50*i:min(50*(i+1),len(quotes))]:
                listn += x + "\n"
            await ctx.channel.send(listn)

    @client.command()
    async def q(ctx, nom):
        channel = ctx.author.voice.channel
        audio = find(nom)
        if audio is not None:
            await playaudios([find(nom)], channel)
        else:
            await ctx.channel.send("Quote not found")

    @client.command()
    async def rand(ctx):
        i = random.randint(1,nbquotes + 1)
        channel = ctx.author.voice.channel
        await ctx.channel.send(quotes[i-1][9:-4])
        await playaudios([quotes[i-1]], channel)

    @client.command()
    async def signal(ctx):
        if(client.vc != None and client.vc.is_playing()):
            return
        for channel in ctx.guild.voice_channels:
            if(len(channel.members) !=0):
                await playaudios([quotes[52]], channel)


    @client.command()
    async def stop(ctx):
        if(client.vc != None):
            await client.vc.disconnect()
        client.vc = None

    @client.command()
    async def addas(ctx, nom):
        nbquotes += 1
        copyfile('temp.mp3', "./quotes/"+str(nbquotes)+" "+nom+".mp3")
        quotes.append("./quotes/"+str(nbquotes)+" "+nom+".mp3")
        @client.command(name=str(nbquotes))
        async def _(ctx):
            channel = ctx.author.voice.channel
            await playaudios([quotes[int(ctx.command.name)-1]], channel)
        await ctx.channel.send("Quote " + "./quotes/"+str(nbquotes)+" "+nom + ".mp3 added")


    @client.command()
    async def add(ctx):
        att = ctx.message.attachments[0]
        nbquotes += 1
        await att.save("./quotes/"+str(nbquotes)+" "+att.filename)
        quotes.append("./quotes/"+str(nbquotes)+" "+att.filename)
        @client.command(name=str(nbquotes))
        async def _(ctx):
            channel = ctx.author.voice.channel
            await playaudios([quotes[int(ctx.command.name)-1]], channel)
        await ctx.channel.send("Quote " + "./quotes/"+str(nbquotes)+" "+att.filename + " added")

    @client.command()
    async def addytt(ctx, vid, debut, fin):
        yt = Youtube(vid).formats
        a = yt.filter_by(only_audio=True)[0]
        audio=a.download(convert='mp3', file_name = 'temp.mp3')
        audio_input = ffmpeg.input(audio)
        audio_cut = audio_input.audio.filter('trim', start=debut, end=fin)
        audio_output = ffmpeg.output(audio_cut, 'out.mp3')
        ffmpeg.run(audio_output)
        channel = ctx.author.voice.channel
        await playaudios(['temp.mp3'], channel)

    @client.command()
    async def addyt(ctx, vid, debut, fin):
        ytdl_ops = {
            'outtmpl': 'temp.%(ext)s',
            'audioformat': 'bestaudio/best',
            'extractaudio': True,
            'audioformat': 'mp3',
            'noplaylist': True,
        }

        
        if os.path.isfile('temp.mp4'):
            os.remove('temp.mp4')
        if os.path.isfile('out.mp3'):
            os.remove('out.mp3')
        with youtube_dl.YoutubeDL(ytdl_ops) as ytdl:
            ytdl.download([vid])
        audio_input = ffmpeg.input('temp.mp4')
        audio_cut = audio_input.filter('trim', start=debut, end=fin)
        audio_output = ffmpeg.output(audio_cut, 'out.mp3')
        ffmpeg.run(audio_output)
        channel = ctx.author.voice.channel
        await playaudios(['temp.mp3'], channel)

    @client.event
    async def on_voice_state_update(member, before, after):
        if(after.channel != None and before.channel == None):
            for i in range(len(greetids)):
                if(member.id == int(greetids[i]) and time.time() - jointime[i] > 60*60*5):
                    jointime[i] = time.time()
                    await playaudios([quotes[59], greetquotes[i]], after.channel)
                    return

    return client
    

bot = init()
bot.run(token)
