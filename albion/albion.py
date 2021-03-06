import discord
import asyncio
import aiohttp
import os
from discord.ext import commands
from .utils.dataIO import dataIO
from .utils import checks
from __main__ import send_cmd_help


settings_path = "data/albion"
settings_filepath = settings_path + "/" + "channels.json"

class Albion:

    """Check Albion things"""

    def __init__(self, bot):
        self.bot = bot
        self.settings_path = settings_path
        self.settings_filepath = settings_filepath
        self.messages = {}
        self.messages['onlineMessage'] = ':hammer_pick: :regional_indicator_a:lbion ist :regional_indicator_o:nline! :crossed_swords:'
        self.messages['offlineMessage'] = ':no_entry: :regional_indicator_a:lbion ist :o2:ffline! :no_entry:'
        self.messages['startingMessage'] = ':airplane_departure: :regional_indicator_a:lbion Server sind am starten! :airplane_departure:'
        self.messages['unknownMessage'] = ':scream: :regional_indicator_a:lbions Zustand ist unklar! Möglicherweise ist gerade Wartung im Gange. :thinking:'
        try:
            self.settings = dataIO.load_json(self.settings_filepath)
        except:
            self.check_folders()
            self.check_files()
            self.settings = dataIO.load_json(self.settings_filepath)
        self.check_task = bot.loop.create_task(self.checkStatus())

    def __unload(self):
        self.check_task.cancel()

    @commands.group(name="albion", pass_context=True)
    async def albion(self, ctx):
        """ Verschiedene Dinge für Albion Online """
        if ctx.invoked_subcommand is None:
            await send_cmd_help(ctx)

    @albion.command(name="statuscheck", pass_context=True)
    @checks.admin_or_permissions(manage_server=True)
    async def _set_statuscheck(self, ctx, status: str):
        """ Schaltet den Statuscheck für diesen Channel ein. """
        server = ctx.message.server
        channel = ctx.message.channel
        if(status == "an"):
            if server.id not in self.settings:
                self.settings[server.id] = {}
            if channel.id not in self.settings[server.id]:
                self.settings[server.id][channel.id] = {}
            status = await self._check_online()
            self.settings[server.id][channel.id] = status
        if(status == "aus"):
            if channel.id in self.settings[server.id]:
                del self.settings[server.id][channel.id]
        dataIO.save_json(self.settings_filepath, self.settings)
        self.settings = dataIO.load_json(self.settings_filepath)

    @commands.command(name="albionstat", pass_context=True, aliases=['astat'])
    async def _get_status(self, ctx):
        """ Fragt den momentanen Status der Server ab. """
        status = await self._check_online()
        if status == "offline":
            await self.bot.say(self.messages['offlineMessage'])
        if status == "online":
            await self.bot.say(self.messages['onlineMessage'])

    async def _check_online(self):
        url = "https://api.albionstatus.com/current/"
        headers = {'user-agent': 'Tron-cog/1.0'}
        conn = aiohttp.TCPConnector(verify_ssl=False)
        session = aiohttp.ClientSession(connector=conn)
        async with session.get(url, headers=headers) as r:
            result = await r.json()
        session.close()
        if "offline" in result[0]['current_status']:
            return "offline"
        if "online" in result[0]['current_status']:
            return "online"

    async def checkStatus(self):
        print("Status Check Cronjob started...")
        while True:
            await asyncio.sleep(300)
            server_status = await self._check_online()
            for serverId in self.settings:
                for channelId in self.settings[serverId]:
                    if 'onlineMessage' in self.settings[serverId][channelId]:
                        online_message = self.settings[serverId][channelId]['onlineMessage']
                    else:
                        online_message = self.messages['onlineMessage']

                    if 'offlineMessage' in self.settings[serverId][channelId]:
                        offline_message = self.settings[serverId][channelId]['offlineMessage']
                    else:
                        offline_message = self.messages['offlineMessage']

                    if 'startingMessage' in self.settings[serverId][channelId]:
                        starting_message = self.settings[serverId][channelId]['startingMessage']
                    else:
                        starting_message = self.messages['startingMessage']

                    if 'unknownMessage' in self.settings[serverId][channelId]:
                        unknown_message = self.settings[serverId][channelId]['unknownMessage']
                    else:
                        unknown_message = self.messages['unknownMessage']

                    if self.settings[serverId][channelId] == server_status:
                        pass
                    if self.settings[serverId][channelId] != server_status and server_status == "online":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), online_message)
                    if self.settings[serverId][channelId] != server_status and server_status == "offline":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), offline_message)
                    if self.settings[serverId][channelId] != server_status and server_status == "starting":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), starting_message)
                    if self.settings[serverId][channelId] != server_status and server_status == "unknown":
                        self.settings[serverId][channelId] = server_status
                        dataIO.save_json(self.settings_filepath, self.settings)
                        await self.bot.send_message(self.bot.get_channel(str(channelId)), uknown_message)

    @albion.command(name="setonlinemessage", pass_context=True)
    async def _setOnlineMessage(self, ctx, message: str):
        """ Setzt die Online Message. """
        server = ctx.message.server
        channel = ctx.message.channel
        if channel.id in self.data[server.id]:
            self.settings[server.id][channel.id]['onlineMessage'] = message
        else:
            bot.say("Albion status is not set for this channel.")

    @albion.command(name="setofflinemessage", pass_context=True)
    async def _setOfflineMessage(self, ctx, message: str):
        """ Setzt die Offline Message. """
        server = ctx.message.server
        channel = ctx.message.channel
        if channel.id in self.data[server.id]:
            self.settings[server.id][channel.id]['offlineMessage'] = message
        else:
            bot.say("Albion status is not set for this channel.")

    @albion.command(name="setstartingmessage", pass_context=True)
    async def _setStartingMessage(self, ctx, message: str):
        """ Setzt die Start Message. """
        server = ctx.message.server
        channel = ctx.message.channel
        if channel.id in self.data[server.id]:
            self.settings[server.id][channel.id]['startingMessage'] = message
        else:
            bot.say("Albion status is not set for this channel.")

    @albion.command(name="setunknownmessage", pass_context=True)
    async def _setUnknownMessage(self, ctx, message: str):
        """ Setzt die Unknown Message. """
        server = ctx.message.server
        channel = ctx.message.channel
        if channel.id in self.data[server.id]:
            self.settings[server.id][channel.id]['unknownMessage'] = message
        else:
            bot.say("Albion status is not set for this channel.")

def check_folders():
    if not os.path.exists(settings_path):
        print("Creating data/dates directory...")
        os.makedirs(settings_path)

def check_files():
    if not dataIO.is_valid_json(settings_filepath):
        print("Creating "+ settings_filepath +"...")
        dataIO.save_json(settings_filepath, {})

def setup(bot):
    check_folders()
    check_files()
    n = Albion(bot)
    bot.add_cog(n)
