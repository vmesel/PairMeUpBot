import logging
import random
import string

import discord
import shortuuid

from decouple import config
from discord.ext import commands, tasks

TOKEN = config("DISCORD_TOKEN")

alphabet = string.ascii_lowercase + string.digits
su = shortuuid.ShortUUID(alphabet=alphabet)

intents = discord.Intents.default()
intents.members = True
intents.presences = True

bot = commands.Bot(command_prefix="!", intents=intents)

GROUPS = {}

@bot.command()
@commands.has_permissions(manage_guild=True)
async def pairmeup(ctx, cmd, *args):
    if cmd != "build":
        return

    if not discord.utils.get(ctx.guild.categories, name="pairmeup"):
        await ctx.guild.create_category("pairmeup")

    await ctx.message.add_reaction("✅")
    await ctx.channel.send("PairMeUp Setup done!")


def check_if_valid_pair(member, ctx):
    if member.name == "pairmeup_bot" or member == ctx.author:
        return False

    if member.status == discord.Status.offline:
        return False
    
    try:
        if member.name in GROUPS[ctx.author.name]:
            return False
    except:
        pass

    return True


def get_random_pair(ctx):
    all_members = ctx.guild.members
    all_members = [member for member in all_members if check_if_valid_pair(member, ctx)]

    if len(all_members) == 0:
        return None

    return random.choice(all_members)


@bot.command()
async def pair(ctx, *args):
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.guild.me: discord.PermissionOverwrite(read_messages=True),
        ctx.author: discord.PermissionOverwrite(read_messages=True),
    }
    pairmeup = discord.utils.get(ctx.guild.categories, name="pairmeup")
    pairs = [pair.name for pair in pairmeup.text_channels]

    new_pair = "pair_{}".format(su.random(length=8))
    if new_pair in pairs:
        return pair(ctx, *args)

    other_pair = get_random_pair(ctx)
    if not other_pair:
        logging.info(f"{ctx.author.name} was not able to create a pair")
        await ctx.message.add_reaction("🤡")
        await ctx.channel.send(
            (
                "Hey {}! We were not able to find you a pair! I'm sorry about this"
            ).format(ctx.message.author.name)
        )
        return

    other_pair_channel = await other_pair.create_dm()
    channel = await pairmeup.create_text_channel(
        name=new_pair,
        user_limit=2,
        overwrites=overwrites,
    )
    invite_link = await channel.create_invite(max_uses=4, unique=True)
    await ctx.message.add_reaction("🍻")
    await channel.send("Welcome to your new pair!")
    await ctx.author.send(invite_link)
    await other_pair_channel.send(invite_link)
    if not ctx.author.name in GROUPS:
        GROUPS[ctx.author.name] = []
    GROUPS[ctx.author.name].append(other_pair.name)
    logging.info(f"{ctx.author.name} created a pair with {other_pair.name} - #{new_pair}")


if __name__ == "__main__":
    logging.info('Starting Bot')
    try:
        bot.run(TOKEN)
    except KeyboardInterrupt:
        bot.logout()
        logging.info('Closing bot')
    except Exception as e:
        logging.info(f'Exception :{e}')
        
