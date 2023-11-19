#!/bin/python
import discord
import time
import json
import os

from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.all()

bot = commands.Bot(command_prefix=os.getenv("PREFIX"), intents=intents)


def load_json(file_path):
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        data = {}
    return data

def save_json(file_path, data):
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=2)


json_file_path = 'data.json'
json_data = load_json(json_file_path)


@bot.event
async def on_ready():
    print(f'counting bot')

@bot.event
async def on_guild_join(guild):
    if f'{guild.id}' not in json_data:
        json_data[f'{guild.id}'] = {
            counter: 0,
            timestamp: round(time.time()),
            highest: 0,
            hasSetup: False
        }
        save_json(json_file_path, json_data)

    await guild.system_channel.send(f'hi, i am a counting bot! set me up with `{os.getenv("PREFIX")}setup` !')


@bot.command(name='commands')
async def commands(ctx):
    await ctx.send(f"my commands are `{os.getenv('PREFIX')}help`, `{os.getenv('PREFIX')}highest`, `{os.getenv('PREFIX')}setup`")

@bot.command(name='highest')
async def highest(ctx):
    await ctx.send(f"highest number recorded for this guild : **{json_data[f'{ctx.guild.id}']['highest']}**")

@bot.command(name='setup')
@commands.has_permissions(administrator=True)
async def setup(ctx):
    await ctx.send("reply with the id of the channel you want to set up for counting :")

    def check(message):
        return message.author == ctx.author and message.channel == ctx.channel

    reply = await bot.wait_for('message', timeout=60, check=check)
    channel_id = int(reply.content)
    
    channel = bot.get_channel(channel_id)
    
    if channel:

        json_data[f'{ctx.guild.id}']['hasSetup'] = True
        json_data[f'{ctx.guild.id}']['countChannelID'] = channel_id
        save_json(json_file_path, json_data)

        await ctx.send(f"ready to count in {channel.mention}!")
    else:
        await ctx.send("invalid.")



@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    ## only do this if the bot is setup.
    if f'{message.guild.id}' in json_data:

        if json_data[f'{message.guild.id}']['hasSetup']:

            # only counter when its in the proper channel
            if message.channel.id == json_data[f'{message.guild.id}']['countChannelID']:
                # lol no breaking chain idiot
                try:
                    content_as_int = int(message.content)

                    # count lol
                    if content_as_int != json_data[f'{message.guild.id}']['counter']+1:
                        json_data[f'{message.guild.id}']['counter'] = 0
                        save_json(json_file_path, json_data)
                        await message.reply("you broke the chain, idiot.")

                    if content_as_int == json_data[f'{message.guild.id}']['counter']+1:
                        json_data[f'{message.guild.id}']['counter'] = content_as_int
                        save_json(json_file_path, json_data)
                
                        if content_as_int > json_data[f'{message.guild.id}']['highest']:
                            json_data[f'{message.guild.id}']['highest'] = content_as_int
                            save_json(json_file_path, json_data)

                except ValueError:
                    await message.delete()


    
    await bot.process_commands(message)


bot.run(os.getenv("TOKEN"))
