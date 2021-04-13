from discord.ext import commands
import youtube_dl
import discord
import os


TOKEN = 'ODI4MTk0OTk3MjE1MDM1NDE2.YGmCsg.xfejBMfgs_z4uikED3rDVPsp8Fk'

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}


def endSong(guild, path):
    os.remove(path)


class MusicBot(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='play')
    async def play(self, ctx, url):
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            if len(self.bot.voice_clients) > 0:
                voice_client = self.bot.voice_clients[0]
            else:
                voice_client = await channel.connect()
            guild = ctx.message.guild
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                file = ydl.extract_info(url, download=True)
                path = str(file['title']) + "-" + str(file['id'] + ".mp3")

            voice_client.play(discord.FFmpegPCMAudio(path), after=lambda x: endSong(guild, path))
            voice_client.source = discord.PCMVolumeTransformer(voice_client.source, 1)

            await ctx.send(f'**Music: **{url}')
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


bot = commands.Bot(command_prefix='$')
bot.add_cog(MusicBot(bot))
bot.run(TOKEN)
