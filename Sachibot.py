import discord
from discord.ext import commands
import RPi.GPIO as GPIO
import datetime
import asyncio
import threading
import time
import sys

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(27, GPIO.IN)
GPIO.setup(6, GPIO.OUT)
GPIO.setup(13, GPIO.OUT)
GPIO.setup(19, GPIO.OUT)
GPIO.setup(26, GPIO.OUT)
GPIO.output(26, True)

cessation_true = 0
intents = discord.Intents.all()
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

# 常時実行
async def main():
    async def always():
        global bot
        await bot.wait_until_ready()
        call_false = 0
        while True:

            now = datetime.datetime.now()
            timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
#           # callコマンド有効・無効(物理スイッチ)
#           if GPIO.input(27):
#               global call_false
#               timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
#               if call_false == 0:
#                   call_false = 2
#                   print(f"{timestamp} \033[33mGPIO27に入力がありました。callコマンドを無効に変更しました。\033[39m")
#                   await asyncio.wait_for(log.send(f"{timestamp} GPIO27に入力がありました。callコマンドを無効に変更しました。"))
#                   await bot.change_presence(status=discord.Status.idle)
#               else:
#                   call_false = 0
#                   print(f"{timestamp} \033[33mGPIO27に入力がありました。callコマンドを有効に変更しました。\033[39m")
#                   await asyncio.wait_for(log.send(f"{timestamp} GPIO27に入力がありました。callコマンドを有効に変更しました。"))
#                   await bot.change_presence(status=discord.Status.online)

            # callコマンド有効・無効(自動)
            if now.hour == 22 and call_false == 0:
                call_false = 1
                print(f"{timestamp} \033[33m22時になりました。callコマンドを無効に変更しました。\033[39m")
                await asyncio.wait_for(log.send(f"{timestamp} 22時になりました。callコマンドを無効に変更しました。"))
                await bot.change_presence(status=discord.Status.idle)

            if now.hour == 8 and call_false == 1:
                call_false = 0
                print(f"{timestamp} \033[33m8時になりました。callコマンドを有効に変更しました。\033[39m")
                await asyncio.wait_for(log.send(f"{timestamp} 8時になりました。callコマンドを有効に変更しました。"))
                await bot.change_presence(status=discord.Status.online)

            # callコマンドステータス
            delta = now - last_call
            if delta.total_seconds() < 1800:
                await bot.change_presence(status=discord.Status.idle)
            else:
                if call_false == 0:
                    await bot.change_presence(status=discord.Status.online)

            await asyncio.sleep(2)

    asyncio.run(always())

# 起動
@bot.event
async def on_ready():
    global log
    log = await bot.fetch_channel(1091324288100999309)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{timestamp} \033[32mBotが起動しました。\033[39m")
    await log.send(f"{timestamp} Botが起動しました。")
    GPIO.output(26, False)
    GPIO.output(19, True)
    time.sleep(3)
    GPIO.output(19, False)

# コマンド実行
@bot.event
async def on_command(ctx):
    if cessation_true == 1:
        return
    
    global now
    global timestamp
    now = datetime.datetime.now()
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S")
    command = ctx.message.content.split()[0]
    print(f"{timestamp} \033[36m{ctx.author.name}#{ctx.author.discriminator}\033[39mが '{command}' コマンドを実行しました。")
    await log.send(f"{timestamp} {ctx.channel.mention}で{ctx.author.name}#{ctx.author.discriminator}が '{command}' コマンドを実行しました。")
    
# 存在しないコマンド
@bot.event
async def on_command_error(ctx, error):
    if cessation_true == 1:
        return
       
    if isinstance(error, commands.CommandNotFound):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        command = ctx.message.content.split()[0]
        print(f"{timestamp} \033[36m{ctx.author.name}#{ctx.author.discriminator}\033[39mが存在しないコマンド '{command}' を実行しました。")
        await log.send(f"{timestamp} {ctx.channel.mention}で{ctx.author.name}#{ctx.author.discriminator}が存在しないコマンド '{command}' を実行しました。")
        await ctx.send(f"'{command}' というコマンドは存在しません。")

# コマンド一覧
@bot.command()
async def helpsa(ctx):
    if cessation_true == 1:
        await ctx.send("現在botを使用することはできません。")
        return
    
    await ctx.send("```!helpsa コマンドの使い方を表示\n!date 日付と時刻を表示します。\n!call さちぬへもを呼ぶためにメンションしても来ない時に使うと来るかもしれません。ステータスが退席中の場合は使用できません。```")

# 日付時刻表示
@bot.command()
async def date(ctx):
    if cessation_true == 1:
        await ctx.send("現在botを使用することはできません。")
        return
    
    await asyncio.sleep(0.1)
    weekdays = ["月", "火", "水", "木", "金", "土", "日"]
    weekday_str = weekdays[now.weekday()]
    await ctx.send(f"今日は、{now:%Y年%m月%d日} ({weekday_str}) {now:%H時%M分%S秒}です。")

# 呼び出し
call_false = 0
last_call = datetime.datetime.min

@bot.command()
async def call(ctx):
    if cessation_true == 1:
        await ctx.send("現在botを使用することはできません。")
        return

    if call_false > 0:
        await ctx.send("現在使用できません。")
        return
    
    global last_call
    delta = now - last_call
    if delta.total_seconds() < 1800:
        minute = int((1800 - delta.total_seconds()) // 60)
        second = int((1800 - delta.total_seconds()) % 60)
        await ctx.send(f"現在使用できません。あと、{minute}分{second}秒で使えるようになります。")
        return

    last_call = now

    await asyncio.sleep(0.1)
    print(f"{timestamp} \033[33m呼び出します。\033[39m")
    await log.send(f"{timestamp} 呼び出します。")
    await ctx.send("呼びます。しばらくお待ちください。")

    def led():
        led = 0
        while (led < 30):
            GPIO.output(13, True)    # 黄色LED
            GPIO.output(19, True)
            time.sleep(1)
            GPIO.output(13, False)
            GPIO.output(19, False)
            time.sleep(1)
            led += 1

    def buzzer():
        buzzer = 0
        while (buzzer < 3):
            GPIO.output(6, True)    # ブザー
            time.sleep(0.1)
            GPIO.output(6, False)
            time.sleep(0.1)
            buzzer += 1

    call1 = threading.Thread(target=led)
    call2 = threading.Thread(target=buzzer)
    call1.start()
    call2.start()

# 定義
@bot.command()
async def definition(ctx):
    await asyncio.sleep(0.1)
    await ctx.send(f"call_false = {call_false}\ncessation_true = {cessation_true}")

# 管理者専用
admin = 1051763568346943550

# 休止
cessation_true = 0

@bot.command()
async def cessation(ctx):
    if any(role.id == admin for role in ctx.author.roles):
        await asyncio.sleep(0.1)
        global cessation_true
        if cessation_true == 0:
            cessation_true = 1
            print(f"{timestamp} \033[33mbotを休止します。\033[39m")
            await log.send(f"{timestamp} botを休止します。")
            await ctx.send("botを休止します。")
            await bot.change_presence(status=discord.Status.dnd)
        else:
            cessation_true = 0
            print(f"{timestamp} \033[33mbotを再開します。\033[39m")
            await ctx.send("botを再開します。")
            await log.send(f"{timestamp} botを再開します。")

            if call_false > 0:
                await bot.change_presence(status=discord.Status.idle)
            else:
                await bot.change_presence(status=discord.Status.online)
    else:
        await ctx.send("cessationコマンドを使用する権限はありません。")

# さちぬへも専用
sachinu = 869870003338493962

# callコマンド有効・無効
call_false = 0

@bot.command()
async def calltf(ctx):
    global call_false

    if ctx.author.id == sachinu:
        await asyncio.sleep(0.1)
        if call_false == 0:
            call_false = 2
            print(f"{timestamp} \033[33mcallコマンドを無効に変更しました。\033[39m")
            await log.send(f"{timestamp} callコマンドを無効に変更しました。")
            await ctx.send("callコマンドを無効に変更しました。")
            await bot.change_presence(status=discord.Status.idle)
        else:
            call_false = 0
            print(f"{timestamp} \033[33mcallコマンドを有効に変更しました。\033[39m")
            await log.send(f"{timestamp} callコマンドを有効に変更しました。")
            await ctx.send("callコマンドを有効に変更しました。")
            await bot.change_presence(status=discord.Status.online)
    else:
        await ctx.send("calltfコマンドを使用する権限はありません。")

# Pythonプログラム終了
class MyView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(discord.ui.Button(label='終了する', style=discord.ButtonStyle.red, custom_id='exit'))
        self.add_item(discord.ui.Button(label='キャンセル', style=discord.ButtonStyle.gray, custom_id='cancel_sa'))

@bot.command()
async def exit(ctx):
    if ctx.author.id == sachinu:
        await ctx.send("本当にプログラムを終了しますか？", view=MyView())
    else:
        await ctx.send("exitコマンドを使用する権限はありません。")

@bot.event
async def on_button_click(interaction, button):
    if interaction.author.id == sachinu:
        if button.custom_id == "exit":
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            await interaction.message.delete()
            await interaction.channel.send("プログラムを終了します。")
            await log.send(f"{timestamp} プログラムを終了します。")
            print(f"{timestamp} プログラムを終了します。")
            GPIO.output(13, True)
            time.sleep(3)
            GPIO.output(13, False)
            sys.exit()

        if button.custom_id == "cancel_sa":
            await interaction.message.delete()
            await interaction.channel.send("キャンセルしました。")

bot.run("TOKEN")
