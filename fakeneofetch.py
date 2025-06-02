"""
fake/custom fetch for rofls 🙂
"""
# ИИшка кормит, больные мозги тоже
#
# meta developer: @HikkaZPM
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
#
from .. import loader, utils
from telethon import events
import asyncio
import logging
import platform
import os
import time
from datetime import datetime

logger = logging.getLogger(__name__)

@loader.tds
class FakeNeofetchMod(loader.Module):
    """Имитация neofetch --stdout, канал с пресетами: https://t.me/+t_xLnCad6zM1NmEy"""

    strings = {
        "name": "Fakeneofetch",
        "loading": "<b>Loading system information...</b>",
        "custom_host_reset": "<b>Custom host reset to default</b>",
    }

    strings_ru = {
        "name": "Fakeneofetch",
        "loading": "<b>Загрузка системной информации...</b>",
        "custom_host_reset": "<b>Кастомный хост сброшен до стандартного</b>",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "custom_host",
                "archbtw", "Кастомный хост для отображения",
            ),
            loader.ConfigValue(
                "custom_os", "Arch Linux", "Кастомный хост для отображения",
            ),
            loader.ConfigValue(
                "custom_hostname", "archbtw", "Кастомный хостнейм для отображения",
            ),
            loader.ConfigValue(
                "custom_user", "root", "Кастомное имя пользователя",
            ),
            loader.ConfigValue(
                "custom_kernel", "Linux 6.2.0-arch1", "Кастомное ядро",
            ),
            loader.ConfigValue(
                "custom_uptime", "69 days, 4 hours, 20 minutes", "Кастомное время работы",
            ),
            loader.ConfigValue(
                "custom_packages", "1337", "Кастомное количество пакетов",
            ),
            loader.ConfigValue(
                "custom_cpu", "AMD Ryzen 9 7950X", "Процессор",
            ),
            loader.ConfigValue(
                "custom_memory", "64GB / 128GB", "Память (использовано / всего)",
            ),
            loader.ConfigValue(
                "enable_delay", True, "Включить задержку перед выводом",
            ),
            loader.ConfigValue(
                "delay", "1.5", "Задержка перед выводом (секунды)",
            ),
        )

    async def client_ready(self, client, db):
        """Вызывается при готовности клиента"""
        self._client = client
        self._db = db
        self._me = await client.get_me()

    @loader.command(ru_doc="Показать фейковый neofetch с кастомным хостом")
    async def fneo(self, message):
        """Показывает фейковый вывод neofetch с кастомным хостом"""
        msg = await utils.answer(message, self.strings["loading"])

        if self.config["ENABLE_DELAY"]:
            await asyncio.sleep(float(self.config['DELAY']))

        current_time = datetime.now().strftime("%H:%M:%S")


        system_info = f"""
{self.config['CUSTOM_USER']}@{self.config['CUSTOM_HOSTNAME']}
-----------------
OS: {self.config['CUSTOM_OS']}
Kernel: {self.config['CUSTOM_KERNEL']}
Uptime: {self.config['CUSTOM_UPTIME']}
Packages: {self.config['CUSTOM_PACKAGES']}
CPU: {self.config['CUSTOM_CPU']}
Memory: {self.config['CUSTOM_MEMORY']}"""

        output = f"<pre>{system_info}</pre>\n<b>Выполнено за {self.config['DELAY']} секунд.</b>"
        await utils.answer(msg, output)

    @loader.command(ru_doc="Сбросить все настройки до стандартных")
    async def resetneofetch(self, message):
        """Сбрасывает все настройки neofetch до стандартных"""
        self.config["CUSTOM_OS"] = "Arch Linux"
        self.config["CUSTOM_HOSTNAME"] = "archbtw"
        self.config["CUSTOM_USER"] = "root"
        self.config["CUSTOM_KERNEL"] = "Linux 6.2.0-arch1"
        self.config["CUSTOM_UPTIME"] = "69 days, 4 hours, 20 minutes"
        self.config["CUSTOM_PACKAGES"] = "1337"
        self.config["CUSTOM_CPU"] = "AMD Ryzen 9 7950X"
        self.config["CUSTOM_MEMORY"] = "64GB / 128GB"
        self.config["DELAY"] = "1.5"

        await utils.answer(message, self.strings["custom_host_reset"])
