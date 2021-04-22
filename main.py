from discord.ext import commands
import youtube_dl
import discord
import os
import re
from urllib import parse, request
import requests
import pymorphy2
import random
from datetime import datetime as dt
import pytz
import sqlite3

TOKEN = 'token'

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
}

playlist = {}
dashes = ['\u2680', '\u2681', '\u2682', '\u2683', '\u2684', '\u2685']

connect = sqlite3.connect("city_russian_pack.db")
list_city = connect.cursor().execute('''SELECT name from main
            ORDER BY name''').fetchall()
copi_list = list_city
slovar_city_number = connect.cursor().execute('''SELECT name, region_id from main
            ORDER BY region_id''').fetchall()
for i in range(len(list_city)):
    list_city[i] = list_city[i][0].replace('ё', 'е')
random.shuffle(list_city)
player_list = []
letter = ''
slovar = []
numbers_region = []
for u in range(len(slovar_city_number)):
    num = slovar_city_number[u][1]
    if num not in numbers_region:
        numbers_region.append(num)
        slovar.append([num, [i[0] for i in slovar_city_number if i[1] == num]])



def endSong(guild, path, voice_client):
    if len(playlist[guild.id]) > 0 or len(playlist[guild.id]) > 1 and path != playlist[guild.id][1]:
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
            for i in range(len(playlist[ctx.message.guild.id]) - 1, -1, -1):
                os.remove(playlist[ctx.message.guild.id][i])
            playlist[ctx.message.guild.id].clear()
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

    @commands.command(name='cat')
    async def cat(self, ctx):
        url = 'https://api.thecatapi.com/v1/images/search'
        response = requests.get(url)
        await ctx.send(response.json()[0]['url'])

    @commands.command(name='dog')
    async def dog(self, ctx):
        url = 'https://dog.ceo/api/breeds/image/random'
        response = requests.get(url)
        await ctx.send(response.json()['message'])

    @commands.command(name='numerals')
    async def numerals(self, ctx, word, number):
        morph = pymorphy2.MorphAnalyzer()
        p = morph.parse(word)[0]
        await ctx.send(f'{number} {p.make_agree_with_number(int(number)).word}')

    @commands.command(name='alive')
    async def alive(self, ctx, word):
        morph = pymorphy2.MorphAnalyzer()
        p = morph.parse(word)[0]
        await ctx.send(f'{word.capitalize()} {"живой" if p.tag.animacy is not None else "не живой"}')

    @commands.command(name='noun')
    async def noun(self, ctx, word, case, state):
        morph = pymorphy2.MorphAnalyzer()
        p = morph.parse(word)[0]
        await ctx.send(p.inflect({state[:4], case}).word)

    @commands.command(name='inf')
    async def inf(self, ctx, word):
        morph = pymorphy2.MorphAnalyzer()
        p = morph.parse(word)[0]
        await ctx.send(p.normal_form)

    @commands.command(name='morph')
    async def morph(self, ctx, word):
        morph = pymorphy2.MorphAnalyzer()
        p = morph.parse(word)[0]
        await ctx.send(f"{p.tag.POS} {p.tag.animacy} {p.tag.gender} {p.tag.case} {p.tag.number}")

    @commands.command(name='roll_dice')
    async def roll_dice(self, ctx, count):
        res = [random.choice(dashes) for _ in range(int(count))]
        await ctx.send(" ".join(res))

    @commands.command(name='ban')
    async def ban(self, ctx, name, *reason):
        if not ctx.message.mentions:
            await ctx.send("Отметь участника через @")
            return
        if not ctx.message.author.guild_permissions.ban_members:
            await ctx.send("У вас нет прав на использование данной команды")
        else:
            if not reason:
                reason = ['Причина', 'не', 'указана']

            ban_embed = discord.Embed(
                title=f'{ctx.message.author.name} забанил {ctx.message.mentions[0].name}',
                description=f'Причина: {" ".join(reason)}',
                color=discord.Colour.random(),
                timestamp=dt.now(pytz.timezone('GMT'))
            )

            await ctx.message.mentions[0].ban()
            await ctx.send(embed=ban_embed)

    @commands.command(name='kick')
    async def kick(self, ctx, name, *reason):
        if not ctx.message.mentions:
            await ctx.send("Отметь участника через @")
            return
        if not ctx.message.author.guild_permissions.kick_members:
            await ctx.send("У вас нет прав на использование данной команды")
        else:
            if not reason:
                reason = ['Причина', 'не', 'указана']

            kick_embed = discord.Embed(
                title=f'{ctx.message.author.name} кикнул {ctx.message.mentions[0].name}',
                description=f'Причина: {" ".join(reason)}',
                color=discord.Colour.random(),
                timestamp=dt.now(pytz.timezone('GMT'))
            )

            await ctx.message.mentions[0].kick()
            await ctx.send(embed=kick_embed)

    @commands.command(name='heads_or_tails')
    async def heads_or_tails(self, ctx):
        await ctx.send('Монета подбрасывается...')
        x = random.randint(0, 100)
        if x < 50:
            await ctx.send(':full_moon: Орёл!')
        elif x > 50:
            await ctx.send(':new_moon: Решка!')
        else:
            await ctx.send(':last_quarter_moon: Монета упала ребром!')

    @commands.command(name='clear')
    async def clear(self, ctx, n):
        if not ctx.message.author.guild_permissions.manage_messages:
            await ctx.send("У вас нет прав на использование данной команды")
        else:
            try:
                n = int(n)
            except ValueError:
                await ctx.send('Неверные данные')
                return

            await ctx.channel.delete_messages(await ctx.channel.history(limit=n).flatten())
            await ctx.send(f'Удалено {n} сообщений')

    @commands.command(name='change_prefix')
    async def change_prefix(self, ctx, prefix):
        bot.command_prefix = prefix
        await ctx.send('Префикс успешно изменен!')

    @commands.command(name='map')
    async def map(self, ctx, place, zoom=10):
        request = f"https://geocode-maps.yandex.ru/1.x/?geocode={place}" \
                  f"&apikey=40d1649f-0493-4b70-98ba-98533de7710b&format=json"
        response = requests.get(request).json()
        toponym = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        point = list(map(float, toponym["Point"]["pos"].split()))

        map_params = {
            'll': point,
            'z': zoom,
            'l': 'map'
        }

        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(map(str, map_params['ll']))}" \
                      f"&z={map_params['z']}&l={map_params['l']}" \
                      f"&pt={','.join(map(str, map_params['ll']))},ya_ru"
        response = requests.get(map_request)

        if not response:
            await ctx.send(f'Не удалось найти {place}')
            return

        await ctx.send(response.url)

    @commands.command(name='satellite')
    async def satellite(self, ctx, place, zoom=10):
        request = f"https://geocode-maps.yandex.ru/1.x/?geocode={place}" \
                  f"&apikey=40d1649f-0493-4b70-98ba-98533de7710b&format=json"
        response = requests.get(request).json()
        toponym = response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        point = list(map(float, toponym["Point"]["pos"].split()))

        map_params = {
            'll': point,
            'z': zoom,
            'l': 'sat'
        }

        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(map(str, map_params['ll']))}" \
                      f"&z={map_params['z']}&l={map_params['l']}" \
                      f"&pt={','.join(map(str, map_params['ll']))},ya_ru"
        response = requests.get(map_request)

        if not response:
            await ctx.send(f'Не удалось найти {place}')
            return

        await ctx.send(response.url)

    @commands.command(name='quote')
    async def quote(self, ctx):
        request = 'http://api.forismatic.com/api/1.0/?method=getQuote&format=text&lang=ru'
        response = requests.get(request)
        await ctx.send(response.text)

    @commands.command(name='city')
    async def сity(self, ctx, name, second_name=''):
        global list_city, player_list, letter
        text = 'ok'
        if second_name != '':
            stadt = name.capitalize() + ' ' + second_name.capitalize()
        else:
            stadt = name.capitalize()
        if stadt not in list_city:
            if stadt not in player_list:
                text = 'Этого города нет в России'
            else:
                text = 'Этот город уже называли'
        else:
            apriory = 0
            if (letter != '' and name[0].lower() == letter) or letter == '':
                list_city.remove(stadt)
                player_list.append(stadt)
                if stadt[-1] not in ['ы', 'ь', 'ъ', 'й']:
                    letter = stadt[-1]
                else:
                    if stadt[-2] not in ['ы', 'ь', 'ъ', 'й', ')']:
                        letter = stadt[-2]
                    else:
                        letter = stadt[-3]
                for i in list_city:
                    if i[0].lower() == letter:
                        stadt = i
                        text = f'{i}, Ваша очередь'
                        if stadt[-1] not in ['ы', 'ь', 'ъ', 'й', ')']:
                            letter = stadt[-1]
                        else:
                            if stadt[-2] not in ['ы', 'ь', 'ъ', 'й', ')']:
                                letter = stadt[-2]
                            else:
                                letter = stadt[-3]
                        list_city.remove(i)
                        apriory = 1
                        player_list.append(i)
                        break
                if apriory == 0:
                    text = f'Ладно, вы победили...'
            else:
                text = f'Город не начинается на последнюю букву предыдущего. Вам нужен город на "{letter.upper()}"'
        await ctx.send(text)

    @commands.command(name='region')
    async def region(self, ctx, *name):
        global slovar, slovar_city_number
        name = list(map(str.capitalize, name))
        name = ' '.join(name)
        try:
            ss = int(name)
            t_reg = []
            for i in slovar:
                if i[0] == ss:
                    t_reg = i[1]
                    break
            if not t_reg:
                text = 'Городов с таким номером региона не существует'
            else:
                text = '\n'.join(t_reg)
        except ValueError:
            text = ''
            for i in slovar_city_number:
                if i[0] == name:
                    text = i[1]
                    break
            if text == '':
                text = 'Такого города не существует'
        await ctx.send(text)

    @commands.command(name='restart_city')
    async def restart_city(self, ctx):
        global copi_list, list_city, player_list, letter
        list_city = copi_list
        random.shuffle(list_city)
        player_list = []
        letter = ''
        await ctx.send('Поиграем в города, вы - начинаете')

    @commands.command(name='add_fav')
    async def add_fav(self, ctx, *text):
        if 'www.youtube.com' not in text[0]:
            text = ' '.join(text)
            query_string = parse.urlencode({'search_query': text})
            htm_content = request.urlopen('https://www.youtube.com/results?' + query_string)
            search_results = re.findall(r"watch\?v=(\S{11})", htm_content.read().decode())
            text = 'https://www.youtube.com/watch?v=' + search_results[0]
        else:
            text = text[0]

        con = sqlite3.connect('favorite.db')
        cur = con.cursor()
        cur.execute(f'INSERT INTO favorite(user_id,url) VALUES({ctx.message.author.id},"{text}")')
        con.commit()
        con.close()

        await ctx.send('Музыка успешно добавлена в избранное')

    @commands.command(name='my_fav')
    async def my_fav(self, ctx):
        con = sqlite3.connect('favorite.db')
        cur = con.cursor()
        res = cur.execute(f'''SELECT url FROM favorite
WHERE user_id = {ctx.message.author.id}''').fetchall()
        con.close()

        await ctx.send(f'Избранное {ctx.message.author.name}')
        s = ''
        for i in range(len(res)):
            s += f'{i + 1}. {res[i][0]}\n'
        await ctx.send(s[:-1])

    @commands.command(name='play_fav')
    async def play_fav(self, ctx):
        con = sqlite3.connect('favorite.db')
        cur = con.cursor()
        res = cur.execute(f'''SELECT url FROM favorite
        WHERE user_id = {ctx.message.author.id}''').fetchall()
        con.close()

        for el in res:
            await self.play(ctx, el[0])

    @commands.command(name='delete_fav')
    async def delete_fav(self, ctx, n: int):
        con = sqlite3.connect('favorite.db')
        cur = con.cursor()
        res = cur.execute(f'''SELECT url FROM favorite
                WHERE user_id = {ctx.message.author.id}''').fetchall()

        if n not in range(1, len(res) + 1):
            await ctx.send('Нет музыки под таким номером')
            con.close()
            return

        x = res[n - 1][0]
        cur.execute(f'''DELETE FROM favorite
        WHERE (user_id = {ctx.message.author.id}) AND (url = "{x}")''')
        con.commit()
        con.close()

        await ctx.send(f'Музыка №{n} успешно удалена')

    @commands.command(name='queue')
    async def queue(self, ctx):
        if playlist[ctx.message.guild.id]:
            await ctx.send('Очередь треков:')
            await ctx.send('\n'.join(playlist[ctx.message.guild.id]))
        else:
            await ctx.send('Очередь пустая')


bot = commands.Bot(command_prefix='$')
bot.add_cog(MusicBot(bot))
bot.run(TOKEN)
