import discord
from discord.ext import commands
import asyncio
import youtube_dl

TOKEN = 'NjY5NTk2MTI2NDkxNzA1MzU0.XoMHOQ.zxz8cEIf09VeDAR3y6P7kcpKZrU'
bot = commands.Bot(command_prefix='!')
bot.remove_command("help")


youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'reconnect' : True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'

}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=1):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options, executable='ffmpeg/bin/ffmpeg.exe', before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"), data=data)

#зашел вышел бот
@bot.event
async def on_ready():
	print('Victor online')

@bot.event
async def on_disconnect():
	print('С канала вышел: {0.author}')


# реакция на сообщения
@bot.event
async def on_message(message):
	priv = ['Hello', 'Hi', 'Privet', 'Привет', 'Прив', "Здарова"]
	if message.content.title() in priv:
		await message.channel.send('епт,здаров')
	print('message from {0.author}:{0.content}'.format(message))
	await bot.process_commands(message)

@bot.event
async def on_message_delete(message):
	print('message deleted from: {0.author}:{0.content}'.format(message))


#реакция на неверные команды

async def on_command_error(ctx, CommandNotFound):
	await ctx.send('Неверная команда...')


# зашел/вышел/перешел
@bot.command()
async def join(ctx):
	if ctx.author.voice:
		if ctx.voice_client:
			await ctx.voice_client.move_to(ctx.author.voice.channel)
		else:
			await ctx.author.voice.channel.connect()
	else:
		await ctx.send('Вы не в канале...')

@bot.command()
async def leave(ctx):
	await ctx.voice_client.disconnect()


#music
@bot.command()
async def lift(ctx):
	source = discord.FFmpegPCMAudio(executable='ffmpeg/bin/ffmpeg.exe', source='D:/Python/music/elevator.WEBM')
	ctx.voice_client.play(source, after=None)

playlist = []
@bot.command()
async def play(ctx, *, url):

	def is_connected():
		voice_client = discord.utils.get(ctx.bot.voice_clients, guild=ctx.guild)
		return voice_client and voice_client.is_connected()

	if ctx.message.guild.voice_client.is_playing():
		with ctx.typing():
			player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
			playlist.append(player.title)
		await ctx.send('Добавил в очередь: {}'.format(player.title))
	else:
		with ctx.typing():
			player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
			playlist.append(player.title)
			ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop))
		await ctx.send('Включаю: {}'.format(player.title))


async def play_next_song(ctx):
	playlist.pop(0)
	player = await YTDLSource.from_url(playlist[0], loop=bot.loop, stream=True)
	ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop))


@bot.command()
async def skip(ctx):
	ctx.voice_client.pause()
	playlist.pop(0)
	player = await YTDLSource.from_url(playlist[0], loop=bot.loop, stream=True)
	ctx.voice_client.play(player, after=lambda e: asyncio.run_coroutine_threadsafe(play_next_song(ctx), bot.loop))

@bot.command()
async def list(ctx):
	if len(playlist) > 0:
		message = "Что будет играть?\n----------------------\n"
		with ctx.typing():
			for i in playlist:
				message += str(i) + "\n----------------------\n"
		await ctx.send(message)


@bot.command()
async def pause(ctx):
	ctx.voice_client.pause()

@bot.command()
async def resume(ctx):
	ctx.voice_client.resume()

@bot.command()
async def help(ctx):
	await ctx.send(('Что я умею?\n Зайти к вам и перейти в канал - !join\n Выйти с канала - !leave\n Включать режим ожидания - !lift\n Включать видео с ютуба - !play + ссылка\n Ставить её на паузу - !pause\n Продолжить данную композицию - !resume'))


# повторюша
@bot.command(pass_context=True)
async def test(ctx, arg):
	await ctx.send(arg)


bot.run(TOKEN)

#whaeroma, Андроид студио 4-2., гикбрэйнс html css, hackerdom-05 стеки osi/////

#вообщем походу пора включаться хз, ты должен сделать весь русский + литру, то что выше тоже надо сделать, надеюсь ты пораньше утром встанешь или пох