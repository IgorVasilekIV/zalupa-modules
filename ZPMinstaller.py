# ---------------------------------------------------------------------------------
# Name: ZPMinstaller
# Description: Установка модулей
# meta developer: @Hikka_ZPM
# meta banner: https://0x0.st/s/masK13-lR0J-hUVUsbQTLw/8b05.png
# requires: BeautifulSoup4
# ---------------------------------------------------------------------------------

import re
import shlex
import aiohttp
import asyncio
import logging

from bs4 import BeautifulSoup

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class ZPMinstaller(loader.Module):
    """ЧТО ЧИТАЕШЬ?"""

    strings = {"name": "ZPMinstaller"}


    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    async def watcher(self, message):
        chat = utils.get_chat_id(message)
        
        if chat != 6096059919:
            return
        
        if not message.text.startswith('<a href="https://raw.githubusercontent.com/'):
            return

        text = message.text
        
        soup = BeautifulSoup(message.text, 'html.parser')
        link = soup.a['href']

        async with aiohttp.ClientSession() as session:
            async with session.get(link) as response:
                code = await response.text()

        requires_comments = re.findall(r'#\s*requires:\s*(.*)', code)
        all_requires = ''.join(requires_comments).strip()

        if all_requires:
            requirements_list = shlex.split(all_requires)
            process = await asyncio.create_subprocess_exec('pip', 'install', *requirements_list)
            await process.wait()

        loader_m = self.lookup("loader")

        await loader_m.download_and_install(link, None)

        pref = self.get_prefix()
        print(link)
        raw_repo = link.split("https://raw.githubusercontent.com/")[1].split("/")
        print(raw_repo)
        repo = raw_repo[1]
        file = raw_repo[-1]
        await utils.answer(message,f"info|{pref}|{repo}/{file}")
        await message.delete()