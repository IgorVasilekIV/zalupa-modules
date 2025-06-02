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
    """Имитация neofetch --stdout, канал с пресетами: https://t.me/+t_xLnCad6zM1NmEy (да падажите не гатова ещо)"""

    strings = {
        "name": "FFetch",
        "loading": "<b>Loading system information...</b>",
        "custom_host_reset": "<b>Custom host reset to default</b>",
        "_cfg_os": "Custom OS for display",
        "_cfg_hostname": "Custom hostname for display",
        "_cfg_user": "Custom username for display",
        "_cfg_kernel": "Custom kernel for display",
        "_cfg_uptime": "Custom uptime for display",
        "_cfg_packages": "Custom packages for display",
        "_cfg_cpu": "Custom CPU for display",
        "_cfg_ram": "Custom RAM for display",
        "_cfg_enable_delay": "Enable delay before output",
        "_cfg_delay": "Delay before output in seconds",
    }

    strings_ru = {
        "name": "FFetch",
        "loading": "<b>Загрузка системной информации...</b>",
        "custom_host_reset": "<b>Кастомный хост сброшен до стандартного</b>",
        "_cfg_os": "Кастомная ОС для отображения",
        "_cfg_hostname": "Кастомный хостнейм для отображения",
        "_cfg_user": "Кастомное имя пользователя",
        "_cfg_kernel": "Кастомный ядро для отображения",
        "_cfg_uptime": "Кастомное время работы для отображения",
        "_cfg_packages": "Кастомные пакеты для отображения",
        "_cfg_cpu": "Кастомный процессор для отображения",
        "_cfg_enable_delay": "Включить задержку перед выводом",
        "_cfg_delay": "Задержка перед выводом в секундах",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "os",
                "Arch Linux",
                doc=lambda: self.strings["_cfg_os"],
                validator=loader.validators.String(min_length=1, max_length=20)
            ),
            loader.ConfigValue(
                "hostname",
                "archbtw",
                doc=lambda: self.strings["_cfg_hostname"],
                validator=loader.validators.String(min_length=1, max_length=20)
            ),
            loader.ConfigValue(
                "user",
                "root",
                doc=lambda: self.strings["_cfg_user"],
                validator=loader.validators.String(min_length=1, max_length=20),
            ),
            loader.ConfigValue(
                "kernel",
                "Linux 6.2.0-arch1",
                doc=lambda: self.strings["_cfg_kernel"],
                validator=loader.validators.String(min_length=1, max_length=20),
            ),
            loader.ConfigValue(
                "uptime",
                "69 days, 4 hours, 20 minutes",
                doc=lambda: self.strings["_cfg_uptime"],
                validator=loader.validators.String(min_length=1, max_length=50),
            ),
            loader.ConfigValue(
                "packages",
                1337,
                doc=lambda: self.strings["_cfg_packages"],
                validator=loader.validators.Integer(min_value=0, max_value=999999999),
            ),
            loader.ConfigValue(
                "cpu",
                "AMD Ryzen 9 7950X",
                doc=lambda: self.strings["_cfg_cpu"],
                validator=loader.validators.String(min_length=1, max_length=50),
            ),
            loader.ConfigValue(
                "ram",
                "64GB / 128GB",
                doc=lambda: self.strings["_cfg_ram"],
                validator=loader.validators.String(min_length=1, max_length=50),
            ),
            loader.ConfigValue(
                "enable_delay",
                True,
                doc=lambda: self.strings["_cfg_enable_delay"],
                validator=loader.validators.Boolean(),
            ),
            loader.ConfigValue(
                "delay",
                1.5,
                doc=lambda: self.strings["_cfg_delay"],
                validator=loader.validators.Float(min_value=0.0, max_value=999999999.0),
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
