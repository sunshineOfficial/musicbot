from discord.ext import commands
import youtube_dl
import discord
import os
import re
from urllib import parse, request


TOKEN = 'ODI4MTk0OTk3MjE1MDM1NDE2.YGmCsg.6XUA7VnLL3Q8nH4mzBoA7rKJ074'

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

playlist = {}


def endSong(guild, path, voice_client):
    if len(playlist[guild.id]) > 1 and path != playlist[guild.id][1]:
        os.remove(path)
    playlist[guild.id] = playlist[guild.id][1:]
    if playlist[guild.id]:
        voice_client.play(discord.FFmpegPCMAudio(playlist[guild.id][0]),
                          after=lambda x: endSong(guild, playlist[guild.id][0], voice_client))
        voice_client.source = discord.PCMVolumeTransformer(voice_client.source, 1)


class MusicBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play')
    async def play(self, ctx, *text):
        global playlist

        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if len(self.bot.voice_clients) > 0:
                voice_client = self.bot.voice_clients[0]
            else:
                voice_client = await channel.connect()
            guild = ctx.message.guild
            if guild.id not in playlist.keys():
                playlist[guild.id] = []
            if 'www.youtube.com' not in text[0]:
                text = ' '.join(text)
                query_string = parse.urlencode({'search_query': text})
                htm_content = request.urlopen('https://www.youtube.com/results?' + query_string)
                search_results = re.findall(r"watch\?v=(\S{11})", htm_content.read().decode())
                text = 'https://www.youtube.com/watch?v=' + search_results[0]
            else:
                text = text[0]

            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                file = ydl.extract_info(text, download=True)
                path = str(file['title']) + "-" + str(file['id'] + ".mp3")

            if not playlist[guild.id]:
                voice_client.play(discord.FFmpegPCMAudio(path), after=lambda x: endSong(guild, path, voice_client))
                voice_client.source = discord.PCMVolumeTransformer(voice_client.source, 1)
                await ctx.send(f'**Музыка: **{text}')
            else:
                await ctx.send(f'**Музыка: **{text} добавлена в очередь')
            playlist[guild.id].append(path)
        else:
            await ctx.send('Вы не в войс-чате')

    @commands.command(name='leave')
    async def leave(self, ctx):
        if len(self.bot.voice_clients) > 0:
            await self.bot.voice_clients[0].disconnect()
        else:
            await ctx.send('Я не в войс-чате')

    @commands.command(name='stop')
    async def stop(self, ctx):
        if len(self.bot.voice_clients) > 0:
            self.bot.voice_clients[0].stop()
        else:
            await ctx.send('Я не в войс-чате')

    @commands.command(name='pause')
    async def pause(self, ctx):
        if len(self.bot.voice_clients) > 0:
            self.bot.voice_clients[0].pause()
        else:
            await ctx.send('Я не в войс-чате')

    @commands.command(name='resume')
    async def resume(self, ctx):
        if len(self.bot.voice_clients) > 0:
            self.bot.voice_clients[0].resume()
        else:
            await ctx.send('Я не в войс-чате')

    @commands.command(name='skip')
    async def skip(self, ctx):
        if len(self.bot.voice_clients) > 0:
            self.bot.voice_clients[0].stop()
            guild = ctx.message.guild
            endSong(guild, playlist[guild.id][0], self.bot.voice_clients[0])
        else:
            await ctx.send('Я не в войс-чате')


bot = commands.Bot(command_prefix='$')
bot.add_cog(MusicBot(bot))
bot.run(TOKEN)
