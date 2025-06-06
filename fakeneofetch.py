"""
Some description:
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
import aiohttp
import re

logger = logging.getLogger(__name__)

@loader.tds
class FakeNeofetchMod(loader.Module):
    """Имитация neofetch, канал с пресетами: https://t.me/+t_xLnCad6zM1NmEy"""

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
        "_cfg_enable_logo": "Enable logo for display",
        "_cfg_logo": "Logo for display, must be link for <distro>.txt, for example grab here: https://github.com/fastfetch-cli/fastfetch/tree/dev/src/logo/ascii (better with small version)"
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
        "_cfg_enable_logo": "Включить логотип для отображения",
        "_cfg_logo": "Логотип для отображения, должна быть ссылкой на файл <distro>.txt, можете взять здесь: https://github.com/fastfetch-cli/fastfetch/tree/dev/src/logo/ascii (лучше с маленькой версией)",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "os",
                "Arch Linux",
                doc=lambda: self.strings["_cfg_os"],
                validator=loader.validators.String(min_len=1, max_len=60)
            ),
            loader.ConfigValue(
                "hostname",
                "archbtw",
                doc=lambda: self.strings["_cfg_hostname"],
                validator=loader.validators.String(min_len=1, max_len=20)
            ),
            loader.ConfigValue(
                "user",
                "root",
                doc=lambda: self.strings["_cfg_user"],
                validator=loader.validators.String(min_len=1, max_len=20),
            ),
            loader.ConfigValue(
                "kernel",
                "Linux 6.2.0-arch1",
                doc=lambda: self.strings["_cfg_kernel"],
                validator=loader.validators.String(min_len=1, max_len=20),
            ),
            loader.ConfigValue(
                "uptime",
                "69 days, 4 hours, 20 minutes",
                doc=lambda: self.strings["_cfg_uptime"],
                validator=loader.validators.String(min_len=1, max_len=50),
            ),
            loader.ConfigValue(
                "packages",
                1337,
                doc=lambda: self.strings["_cfg_packages"],
                validator=loader.validators.Integer(minimum=0, maximum=999999999),
            ),
            loader.ConfigValue(
                "cpu",
                "AMD Ryzen 9 7950X",
                doc=lambda: self.strings["_cfg_cpu"],
                validator=loader.validators.String(min_len=1, max_len=50),
            ),
            loader.ConfigValue(
                "ram",
                "64GB / 128GB",
                doc=lambda: self.strings["_cfg_ram"],
                validator=loader.validators.String(min_len=1, max_len=50),
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
                validator=loader.validators.Float(minimum=0.0, maximum=999999999.0),
            ),
            loader.ConfigValue(
                "enable_logo",
                True,
                doc=lambda: self.strings["_cfg_enable_logo"],
                validator=loader.validators.Boolean(),
            ),
            #loader.ConfigValue(
            #    "logo",
            #    "https://raw.githubusercontent.com/fastfetch-cli/fastfetch/refs/heads/dev/src/logo/ascii/arch_small.txt",
            #    doc=lambda: self.strings["_cfg_logo"],
            #    validator=loader.validators.Link(),
            #),
            loader.ConfigValue(
                "logo_style",
                "arch_small",
                doc=lambda: self.strings["_cfg_logo"],
                validator=loader.validators.Choice([
                     "arch", "arch_small", "ubuntu", "ubuntu_small",
                     "debian", "debian_small", "fedora", "fedora_small",
                     "windows", "windows_8" "android", "android_small" "macos", "macos_small"
                ]),
            ),
            loader.ConfigValue(
                "custom_logo_url",
                "",
                doc="Кастомный URL логотипа",
                validator=loader.validators.String(),
            ),
        )

    async def client_ready(self, client, db):
        """Вызывается при готовности клиента"""
        self._client = client
        self._db = db
        self._me = await client.get_me()

    async def get_logo(self):
            """Загружает и возвращает логотип"""
            if self.config["custom_logo_url"]:
                url = self.config["custom_logo_url"]
            else:
                logo_name = self.config["logo_style"]
                url = f"https://raw.githubusercontent.com/fastfetch-cli/fastfetch/dev/src/logo/ascii/{logo_name}.txt"

            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            logo_text = await response.text()

                            cleaned_logo = re.sub(r'\$\d+', '', logo_text)

                            cleaned_lines = [line for line in cleaned_logo.splitlines() if line.strip()]

                            return "\n".join(cleaned_lines)

                        return f"Ошибка загрузки: {response.status}"
            except Exception as e:
                return f"Ошибка: {str(e)}"

    @loader.command(ru_doc="Показать фейковый neofetch с кастомным хостом")
    async def fneo(self, message):
        """Показывает фейковый вывод neofetch"""
        msg = await utils.answer(message, self.strings["loading"])

        if self.config["enable_delay"]:
            await asyncio.sleep(float(self.config['delay']))

        logo = ""
        if self.config["enable_logo"]:
            try:
                logo = await self.get_logo()
                logo += "\n\n"
            except Exception as e:
                logger.error(f"Error loading logo: {str(e)}")
                logo = ""

        system_info = f"""
{logo}{self.config['user']}@{self.config['hostname']}
-----------------
OS: {self.config['os']}
Kernel: {self.config['kernel']}
Uptime: {self.config['uptime']}
Packages: {self.config['packages']}
CPU: {self.config['cpu']}
Memory: {self.config['ram']}"""

        output = f"<pre>{system_info}</pre>\n<b>Выполнено за {self.config['delay']} секунд.</b>"
        await utils.answer(msg, output)

    @loader.command(ru_doc="Сбросить все настройки до стандартных")
    async def resetneofetch(self, message):
        """Сбрасывает все настройки neofetch до стандартных"""
        self.config["os"] = "Arch Linux"
        self.config["hostname"] = "archbtw"
        self.config["user"] = "root"
        self.config["kernel"] = "Linux 6.2.0-arch1"
        self.config["uptime"] = "69 days, 4 hours, 20 minutes"
        self.config["packages"] = 1337
        self.config["cpu"] = "AMD Ryzen 9 7950X"
        self.config["ram"] = "64GB / 128GB"
        self.config["delay"] = 1.5

        await utils.answer(message, self.strings["custom_host_reset"])
