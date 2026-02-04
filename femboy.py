# meta developer: Amigoch for @HikkaZPM
# meta fhsdeck: fun, edit, auto
#
# The module is made as a joke, all coincidences are random :P
#
#       кот вахуи
#       /\_____/\
#      /  o   o  \
#     ( ==  ^  == )
#      )         (
#     (           )
#    ( (  )   (  ) )
#   (__(__)___(__)__)
#

# здравствуйте @Hicota 👋😐
# А так же спасибо, что дал повод доделать модуль

import asyncio
import random
import logging

from .. import loader, utils

logger = logging.getLogger(__name__)

@loader.tds
class femboy(loader.Module):
    """Femboy Module"""

    strings = {
        "name": "FemBoy",

        "f_on": "<b><emoji <emoji document_id=5341813983252851777>🌟</emoji> режим Femboy включен!</b>",
        "f_off": "<b><emoji <emoji document_id=5318833180915027058>😭</emoji> Режим Femboy^^ выключен!</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "emojies",
                ["<emoji document_id=5424970378374035950>🕺</emoji>", "<emoji document_id=5429635773714412028>😆</emoji>", "<emoji document_id=5321451749460946626>😘</emoji>", "<emoji document_id=5215496967852936076>🥵</emoji>", "<emoji document_id=5326027259725749455>🤭</emoji>", "<emoji document_id=5402630084509066049>😏</emoji>️", "<emoji document_id=5327760081461190613>😋</emoji>", "<emoji document_id=5235787973907205473>👅</emoji>"],
                lambda: "Эмодзы для вставки в текст",
                validator=loader.validators.Series()
            ),
        )

    async def client_ready(self, client, db):
        self.db = db
        self._client = client

    @loader.command(no_stickers=True)
    async def femboy(self, message):
        """Включить/выключить режим фембоя"""

        if self.db.get(self.name, "femboy", False):
            self.db.set(self.name, "femboy", False)
            await asyncio.sleep(0.15) # ждом ибо иногда не понятно, что он выключен
            return await utils.answer(message, self.strings["f_off"])

        self.db.set(self.name, "femboy", True)

        await utils.answer(message, self.strings["f_on"])

    @loader.watcher(only_messages=True, no_commands=True, no_stickers=True, no_forwards=True, no_inline=True)
    async def watcher(self, event):
        try:
            if event.sender_id != self.tg_id:
                return
        except:
            return
        if not self.db.get(self.name, "femboy", False):
            return
        
        words = event.raw_text.split()
        modified_text = " ".join(
            word + (f" {random.choice(self.config['emojies'])}" if random.random() > 0.5 else "")
            for word in words
        )
        ascii = f" {utils.ascii_face()}" if random.random() > 0.6 else ""

        await event.edit(text=modified_text + ascii)
